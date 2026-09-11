"""Local commands: python -m movie_factory.experiment_ops --help."""
from __future__ import annotations

import argparse
import json
import subprocess
import time
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

from .engineering_usage import import_rollout, reconcile
from .experiment_ledger import EVENT_TYPES, Ledger, effective_events, summarize, timestamp
from .packages import atomic_json
from .telemetry import utc_now


def build_report(events, experiment_id, *, usage=None, api_costs=None, as_of=None):
    result = summarize(events, experiment_id, as_of=as_of)
    effective = [e for e in effective_events(events) if e['experiment_id'] == experiment_id]
    usage_events = [e['usage'] for e in effective if e['event_type'] == 'usage_observed' and 'usage' in e]
    # One reconciler receives every imported record; duplicate imports cannot inflate usage.
    envelope = usage or {}
    records = envelope.get('records', []) + usage_events
    times = sorted((e['utc'] for e in effective), key=timestamp)
    tasks = sorted({e['task_id'] for e in effective if e.get('task_id')})
    windows = []
    for episode in result['episodes']:
        group = [e for e in effective if e['episode_id'] == episode['episode_id']]
        starts = [e['utc'] for e in group if e['event_type'] in {'start', 'reopen'}]
        ends = [e['utc'] for e in group if e['event_type'] == 'close']
        if starts:
            windows.append((starts[0], ends[-1] if ends else as_of or group[-1]['utc']))
    result['engineering_usage'] = reconcile(records, task_ids=tasks, start=times[0], end=as_of or times[-1], windows=windows) if times else {
        'status': 'UNKNOWN', 'observed_tokens': None, 'exact_attributable_tokens': None}
    if 'account_allowance' in result['engineering_usage']:
        result['engineering_usage']['account_allowance']['observations'] = [
            e for e in effective if e['event_type'] == 'allowance_observed']
    result['model_setting_observations'] = [e for e in effective if e['event_type'] == 'model_setting_observed']
    result['factory_api'] = api_costs if api_costs is not None else {
        'provider_calls': None, 'known_api_cost_usd': None, 'status': 'UNKNOWN',
        'reason': 'No provider ledger evidence supplied; absence is not zero.'}
    closed = [e for e in effective if e['event_type'] == 'close']
    result['outcome_denominators'] = {
        'closed_experiments': int(bool(result['episodes']) and all(e['lifecycle'] == 'CLOSED' for e in result['episodes'])),
        'closed_episodes': len(closed),
        'technically_successful_outputs': sum(e['technical_outputs'] for e in closed)
            if closed and all(type(e.get('technical_outputs')) is int for e in closed) else None,
        'director_accepted_outputs': sum(e['director_outputs'] for e in closed)
            if closed and all(type(e.get('director_outputs')) is int for e in closed) else None,
    }
    tokens = result['engineering_usage'].get('exact_attributable_tokens')
    net = result['net_episode_sum_seconds']
    result['consumption_per_outcome'] = {
        name: {'net_seconds': net/count if count and net is not None else None,
               'engineering_tokens': tokens['total_tokens']/count if count and tokens and tokens['total_tokens'] is not None else None}
        for name, count in result['outcome_denominators'].items()}
    result['cost_scope'] = 'Development investment; repeatable runtime cost remains in the campaign provider records.'
    return result


def markdown(report):
    def value(item):
        return 'UNKNOWN' if item is None else str(item)
    lines = [f"# {report['experiment_id']} operating report", '',
             'Lifecycle closure and qualification colour are independent.', '',
             '| Episode | Lifecycle / disposition | Calendar s | Excluded input s | Net s | Coverage |',
             '|---|---|---:|---:|---:|---:|']
    for e in report['episodes']:
        lines.append(f"| {e['episode_id']} | {e['lifecycle']} / {value(e['disposition'])} | "
                     f"{value(e['calendar_elapsed_seconds'])} | {value(e['excluded_input_wait_seconds'])} | "
                     f"{value(e['net_elapsed_seconds'])} | {value(e['coverage_fraction'])} |")
        if e['uncertainties']:
            lines += ['', f"{e['episode_id']} uncertainty: {', '.join(e['uncertainties'])}.", '']
    u = report['engineering_usage']
    lines += ['', f"Engineering usage: **{u['status']}**. Exact attributable tokens: "
              f"{value(u.get('exact_attributable_tokens'))}.",
              f"Observed token categories (may be partial): {value(u.get('observed_tokens'))}.",
              'Cached and reasoning tokens are subsets, not additions to the total.', '',
              f"Factory API evidence: {report['factory_api']}.",
              'Subscription charges are shared fixed overhead; engineering dollar allocation and API-equivalent cost are UNKNOWN.', '',
              f"Outcome denominators: {report['outcome_denominators']}.",
              f"Consumption per outcome: {report['consumption_per_outcome']}.", '',
              'See JSON for job sums/unions, phases, work intervals and coverage. Job sums are process-seconds, not CPU core-seconds.',
              'Account quota is a separate capacity measure; percentages are not per-experiment tokens.', '']
    return '\n'.join(lines)


def demo_events():
    """120 calendar, 35 excluded, 85 net minutes; entirely synthetic."""
    origin = datetime(2026, 1, 1, tzinfo=timezone.utc)
    specs = [
        (0, 'start', {}), (0, 'work_started', {'activity_id': 'engineering', 'actor': 'assistant'}),
        (20, 'work_ended', {'activity_id': 'engineering'}),
        (20, 'wait_started', {'wait_id': 'review', 'reason': 'director_response'}),
        (20, 'job_started', {'job_id': 'render1', 'clock_id': 'fixture', 'monotonic_seconds': 1200}),
        (25, 'job_started', {'job_id': 'render2', 'clock_id': 'fixture', 'monotonic_seconds': 1500}),
        (30, 'job_completed', {'job_id': 'render1', 'clock_id': 'fixture', 'monotonic_seconds': 1800}),
        (30, 'job_completed', {'job_id': 'render2', 'clock_id': 'fixture', 'monotonic_seconds': 1800}),
        (50, 'wait_ended', {'wait_id': 'review'}), (50, 'human_review', {'duration_seconds': 120}),
        (50, 'work_started', {'activity_id': 'repair', 'actor': 'assistant'}),
        (70, 'work_ended', {'activity_id': 'repair'}),
        (70, 'wait_started', {'wait_id': 'prompt', 'reason': 'next_prompt'}),
        (85, 'wait_ended', {'wait_id': 'prompt'}),
        (85, 'work_started', {'activity_id': 'packaging', 'actor': 'assistant'}),
        (85, 'phase_changed', {}), (120, 'work_ended', {'activity_id': 'packaging'}),
        (120, 'close', {'disposition': 'YELLOW', 'technical_outputs': 1, 'director_outputs': 1}),
    ]
    return [{'event_id': f'demo-{i}', 'experiment_id': 'SIMULATED-OPS', 'episode_id': 'demo-1',
             'task_id': 'synthetic-task', 'utc': (origin+timedelta(minutes=minute)).isoformat(),
             'event_type': kind, 'phase': 'packaging' if minute >= 85 else 'engineering',
             'evidence_ref': 'synthetic acceptance fixture; not historical usage', **extra}
            for i, (minute, kind, extra) in enumerate(specs)]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ledger', type=Path, default=Path('.runtime/experiment-ops.sqlite3'))
    commands = parser.add_subparsers(dest='command', required=True)
    emit = commands.add_parser('emit')
    emit.add_argument('--experiment', required=True); emit.add_argument('--episode', required=True)
    emit.add_argument('--type', choices=sorted(EVENT_TYPES), required=True)
    emit.add_argument('--id', required=True, help='Stable event ID for safe retries')
    emit.add_argument('--phase', required=True); emit.add_argument('--utc')
    emit.add_argument('--fields', type=json.loads, default={}, help='Additional structured JSON; no secrets')
    ingest = commands.add_parser('append'); ingest.add_argument('event', type=Path)
    report = commands.add_parser('report'); report.add_argument('--experiment', required=True)
    report.add_argument('--output', type=Path, required=True); report.add_argument('--usage', type=Path)
    report.add_argument('--api-costs', type=Path); report.add_argument('--as-of')
    export = commands.add_parser('export'); export.add_argument('--output', type=Path, required=True)
    imp = commands.add_parser('import-usage')
    for arg in ('task', 'start', 'end', 'version'):
        imp.add_argument('--'+arg, required=True)
    imp.add_argument('--path', type=Path, required=True); imp.add_argument('--output', type=Path, required=True)
    demo = commands.add_parser('demo'); demo.add_argument('--output', type=Path, required=True)
    job = commands.add_parser('job')
    for arg in ('experiment', 'episode', 'phase', 'id'):
        job.add_argument('--'+arg, required=True)
    job.add_argument('--kind', choices=['local', 'native'], default='local')
    job.add_argument('args', nargs=argparse.REMAINDER)
    args = parser.parse_args(argv)
    if args.command == 'import-usage':
        result = import_rollout(args.path, task_id=args.task, start=args.start, end=args.end,
                                installed_version=args.version)
        atomic_json(args.output, result)
        print(result['status']); return 0
    if args.command == 'demo':
        events = demo_events()
        result = build_report(events, 'SIMULATED-OPS')
        args.output.mkdir(parents=True, exist_ok=True)
        atomic_json(args.output/'events.json', events)
    else:
        ledger = Ledger(args.ledger)
        if args.command == 'emit':
            prior = next((e for e in ledger.events() if e['event_id'] == args.id), None)
            ledger.append({'event_id': args.id, 'experiment_id': args.experiment,
                           'episode_id': args.episode, 'event_type': args.type,
                           'utc': args.utc or (prior['utc'] if prior else utc_now()), 'phase': args.phase, **args.fields})
            return 0
        if args.command == 'append':
            ledger.append(json.loads(args.event.read_text())); return 0
        if args.command == 'export':
            atomic_json(args.output, ledger.events()); return 0
        if args.command == 'job':
            command = args.args[1:] if args.args[:1] == ['--'] else args.args
            if not command:
                parser.error('job requires a command after --')
            if any(e.get('job_id') == args.id for e in ledger.events()):
                parser.error('job ID already used; inspect it before rerunning with a new ID')
            context = {'experiment_id': args.experiment, 'episode_id': args.episode,
                       'phase': args.phase, 'job_id': args.id, 'job_kind': args.kind, 'clock_id': str(uuid.uuid4())}
            ledger.append({**context, 'event_id': args.id+'-start', 'event_type': 'job_started',
                           'utc': utc_now(), 'monotonic_seconds': time.monotonic()})
            try:
                code = subprocess.run(command, check=False).returncode
            except OSError:
                code = 127
            ledger.append({**context, 'event_id': args.id+'-end', 'event_type': 'job_completed',
                           'utc': utc_now(), 'monotonic_seconds': time.monotonic(),
                           'outcome': 'PASSED' if code == 0 else 'FAILED', 'returncode': code})
            return code
        result = build_report(ledger.events(), args.experiment,
                              usage=json.loads(args.usage.read_text()) if args.usage else None,
                              api_costs=json.loads(args.api_costs.read_text()) if args.api_costs else None,
                              as_of=args.as_of)
    args.output.mkdir(parents=True, exist_ok=True)
    atomic_json(args.output/'summary.json', result)
    (args.output/'REPORT.md').write_text(markdown(result))
    print(args.output/'REPORT.md')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
