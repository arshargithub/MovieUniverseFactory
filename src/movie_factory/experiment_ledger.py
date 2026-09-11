"""Small append-only operational ledger; independent of qualification/provider budgets."""
from __future__ import annotations

import json
import math
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from .telemetry import canonical_json, sanitize

EVENT_TYPES = {
    'start', 'reopen', 'close', 'work_started', 'work_ended', 'phase_changed',
    'wait_started', 'wait_ended', 'job_started', 'job_completed',
    'model_setting_observed', 'usage_observed', 'proxy_observed', 'human_review', 'allowance_observed',
}
EXCLUDED_WAITS = {'director_response', 'next_prompt', 'user_pause'}
WAIT_REASONS = EXCLUDED_WAITS | {'provider_limit', 'machine_failure', 'infrastructure'}


def timestamp(value: str) -> float:
    dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
    if dt.utcoffset() is None or dt.utcoffset().total_seconds() != 0:
        raise ValueError('timestamps must explicitly use UTC')
    return dt.timestamp()


def validate_event(event: dict) -> None:
    for field in ('event_id', 'experiment_id', 'episode_id', 'utc', 'event_type', 'phase'):
        if not isinstance(event.get(field), str) or not event[field]:
            raise ValueError(f'missing {field}')
    timestamp(event['utc'])
    kind = event['event_type']
    if kind not in EVENT_TYPES:
        raise ValueError('unsupported event type')
    if kind.startswith('wait_') and not event.get('wait_id'):
        raise ValueError('wait_id required')
    if kind == 'wait_started' and event.get('reason') not in WAIT_REASONS:
        raise ValueError('explicit wait reason required')
    if kind.startswith('job_') and not event.get('job_id'):
        raise ValueError('job_id required')
    if kind.startswith('work_') and not event.get('activity_id'):
        raise ValueError('activity_id required')
    if kind == 'reopen' and not event.get('prior_episode_id'):
        raise ValueError('reopen requires a prior episode')
    if kind == 'close' and event.get('disposition') not in {'GREEN', 'YELLOW', 'RED', 'ABANDONED'}:
        raise ValueError('close requires a disposition')
    for field in ('monotonic_seconds', 'duration_seconds'):
        if event.get(field) is not None and (type(event[field]) not in (int, float)
                or not math.isfinite(event[field]) or event[field] < 0):
            raise ValueError(f'invalid {field}')


class Ledger:
    """SQLite transactions recover interrupted writes; event IDs make retries idempotent.

    Corrections append a full replacement with supersedes=<old event_id>. No UPDATE
    or DELETE operation is exposed. Exported JSON retains all historical events.
    """
    def __init__(self, path: Path):
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        self.path = path
        with sqlite3.connect(path) as db:
            db.execute('CREATE TABLE IF NOT EXISTS events '
                       '(seq INTEGER PRIMARY KEY, id TEXT UNIQUE NOT NULL, payload TEXT NOT NULL)')

    def events(self) -> list[dict]:
        with sqlite3.connect(self.path) as db:
            return [json.loads(row[0]) for row in db.execute('SELECT payload FROM events ORDER BY seq')]

    def append(self, event: dict) -> bool:
        record = sanitize({'schema_version': '1.0', 'task_id': None, 'turn_id': None,
                           'run_id': None, 'reason': None, 'evidence_ref': None, **event})
        validate_event(record)
        payload = canonical_json(record)
        with sqlite3.connect(self.path) as db:
            db.execute('BEGIN IMMEDIATE')
            existing = db.execute('SELECT payload FROM events WHERE id=?', (record['event_id'],)).fetchone()
            if existing:
                if existing[0] != payload:
                    raise ValueError('event ID reused with different content; append a correction')
                return False
            if record.get('supersedes'):
                prior = db.execute('SELECT payload FROM events WHERE id=?', (record['supersedes'],)).fetchone()
                if prior is None:
                    raise ValueError('correction target missing')
                old = json.loads(prior[0])
                if any(record[k] != old[k] for k in ('experiment_id', 'episode_id', 'event_type')):
                    raise ValueError('correction cannot change episode or event type')
                if any(e.get('supersedes') == record['supersedes'] for e in self.events()):
                    raise ValueError('supersede the latest correction, not an older event')
            db.execute('INSERT INTO events(id,payload) VALUES (?,?)', (record['event_id'], payload))
        return True


def effective_events(events: list[dict]) -> list[dict]:
    result = []
    positions = {}
    for event in events:
        if event.get('supersedes'):
            pos = positions.pop(event['supersedes'])
            result[pos] = event
        else:
            pos = len(result)
            result.append(event)
        positions[event['event_id']] = pos
    return result


def union(intervals):
    result = []
    for low, high in sorted(intervals):
        if high <= low:
            continue
        if result and low <= result[-1][1]:
            result[-1] = (result[-1][0], max(high, result[-1][1]))
        else:
            result.append((low, high))
    return result


def seconds(intervals):
    return sum(high-low for low, high in union(intervals))


def subtract(intervals, covered):
    remainder = union(intervals)
    for low, high in union(covered):
        next_intervals = []
        for a, b in remainder:
            if b <= low or a >= high:
                next_intervals.append((a, b))
            else:
                if a < low:
                    next_intervals.append((a, low))
                if b > high:
                    next_intervals.append((high, b))
        remainder = next_intervals
    return remainder


def episode_report(events: list[dict], *, as_of: str | None = None) -> dict:
    """Exact net elapsed is withheld on gaps, missing boundaries or clock jumps."""
    problems = []
    starts = [e for e in events if e['event_type'] in {'start', 'reopen'}]
    closes = [e for e in events if e['event_type'] == 'close']
    if len(starts) != 1 or len(closes) != 1:
        problems.append('missing_or_duplicate_lifecycle_boundary')
    start = timestamp(starts[0]['utc']) if starts else min(timestamp(e['utc']) for e in events)
    end = timestamp(closes[-1]['utc']) if closes else timestamp(as_of or events[-1]['utc'])
    if end < start:
        problems.append('clock_discontinuity')
    times = [timestamp(e['utc']) for e in events]
    if times != sorted(times):
        problems.append('clock_discontinuity_or_out_of_order_capture')
    if any(t < start or t > end for t in times):
        problems.append('event_outside_episode')
    groups = {'work': [], 'wait': [], 'job': []}
    active = {}
    job_durations = []
    for e in events:
        kind = e['event_type']
        group = kind.split('_')[0]
        if group not in groups:
            continue
        key = (group, e[{'work': 'activity_id', 'wait': 'wait_id', 'job': 'job_id'}[group]])
        if kind.endswith('started'):
            if key in active:
                problems.append('duplicate_interval_start')
            active[key] = e
        else:
            first = active.pop(key, None)
            if first is None:
                problems.append('missing_interval_start')
                continue
            a, b = timestamp(first['utc']), timestamp(e['utc'])
            if b < a:
                problems.append('clock_discontinuity')
                continue
            groups[group].append((a, b, first))
            if group == 'job':
                mono = None
                if first.get('clock_id') and first.get('clock_id') == e.get('clock_id'):
                    if first.get('monotonic_seconds') is not None and e.get('monotonic_seconds') is not None:
                        mono = e['monotonic_seconds'] - first['monotonic_seconds']
                        if mono < 0 or abs(mono-(b-a)) > 1:
                            problems.append('clock_discontinuity')
                if mono is None:
                    problems.append('missing_job_monotonic_clock')
                job_durations.append({'job_id': e['job_id'], 'utc_seconds': b-a,
                                      'monotonic_seconds': mono, 'outcome': e.get('outcome'),
                                      'job_kind': first.get('job_kind', 'native')})
    for (group, _), first in active.items():
        problems.append('missing_interval_end')
        # A potentially live/crashed job blocks wait exclusion through the horizon.
        groups[group].append((timestamp(first['utc']), end, first))
    working = [(a, b) for group in ('work', 'job') for a, b, _ in groups[group]]
    human_waits = [(a, b) for a, b, e in groups['wait'] if e['reason'] in EXCLUDED_WAITS]
    excluded = subtract(human_waits, working)
    all_intervals = [(a, b) for group in groups.values() for a, b, _ in group]
    gaps = subtract([(start, end)], all_intervals)
    if gaps:
        problems.append('unexplained_gap')
    phases = [e for e in events if e['event_type'] in {'start', 'reopen', 'phase_changed'}]
    phase_totals = {}
    for i, e in enumerate(phases):
        b = timestamp(phases[i+1]['utc']) if i+1 < len(phases) else end
        duration = seconds(subtract([(timestamp(e['utc']), b)], excluded))
        phase_totals[e['phase']] = phase_totals.get(e['phase'], 0) + duration
    complete = not problems
    calendar = max(0, end-start)
    native_jobs = [j for j in job_durations if j['job_kind'] == 'native']
    human_reviews = [e.get('duration_seconds') for e in events if e['event_type'] == 'human_review']
    proxies = {}
    for e in events:
        if e['event_type'] == 'proxy_observed':
            name, count = e.get('name'), e.get('count')
            if name and type(count) is int and count >= 0:
                proxies[name] = proxies.get(name, 0) + count
    return {
        'episode_id': events[0]['episode_id'], 'lifecycle': 'CLOSED' if closes else 'OPEN',
        'disposition': closes[-1].get('disposition') if closes else None,
        'calendar_elapsed_seconds': calendar if starts and closes and end >= start else None,
        'excluded_input_wait_seconds': seconds(excluded) if complete else None,
        'observed_excluded_input_wait_seconds': seconds(excluded),
        'net_elapsed_seconds': calendar-seconds(excluded) if complete else None,
        'coverage_fraction': (calendar-seconds(gaps))/calendar if calendar else None,
        'unknown_gap_seconds': seconds(gaps), 'uncertainties': sorted(set(problems)),
        'jobs': job_durations,
        'native_jobs': native_jobs,
        'native_job_wall_sum_seconds': sum(j['monotonic_seconds'] for j in native_jobs)
            if all(j['monotonic_seconds'] is not None for j in native_jobs)
            and not any(k[0] == 'job' and e.get('job_kind', 'native') == 'native' for k, e in active.items()) else None,
        'native_job_wall_union_seconds': seconds([(a, b) for a, b, e in groups['job']
                                                  if e.get('job_kind', 'native') == 'native']) if complete else None,
        'assistant_active_union_seconds': seconds([(a, b) for a, b, e in groups['work']
                                                    if e.get('actor') == 'assistant']),
        'assistant_time_scope': 'Recorded activity intervals only; not token generation time',
        'human_review_seconds': sum(human_reviews) if human_reviews and None not in human_reviews else None,
        'phase_net_seconds': phase_totals if complete else None,
        'operational_proxies': proxies,
    }


def summarize(events: list[dict], experiment_id: str, *, as_of=None) -> dict:
    selected = [e for e in effective_events(events) if e['experiment_id'] == experiment_id]
    episodes = {}
    for e in selected:
        episodes.setdefault(e['episode_id'], []).append(e)
    reports = [episode_report(group, as_of=as_of) for group in episodes.values()]
    for group, report in zip(episodes.values(), reports):
        reopening = next((e for e in group if e['event_type'] == 'reopen'), None)
        if reopening:
            prior = episodes.get(reopening['prior_episode_id'], [])
            closed = [e for e in prior if e['event_type'] == 'close']
            if not closed or timestamp(closed[-1]['utc']) > timestamp(reopening['utc']):
                report['uncertainties'].append('invalid_reopen_link')
                report['net_elapsed_seconds'] = None
    return {'schema_version': '1.0', 'experiment_id': experiment_id, 'episodes': reports,
            'closed_episode_count': sum(r['lifecycle'] == 'CLOSED' for r in reports),
            'net_episode_sum_seconds': sum(r['net_elapsed_seconds'] for r in reports)
                if reports and all(r['net_elapsed_seconds'] is not None for r in reports) else None,
            'note': 'Episode totals exclude inter-episode gaps. Job sums are process-seconds, not CPU time.'}
