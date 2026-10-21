"""Offline staged workflow controller. No model, shell, render or network dispatch.

Enforces transitions through this API, not arbitrary chat/filesystem operations.
Tickets separate stage submissions; they are not an OS sandbox. Semantic review
claims remain fallible. A live adapter must restrict controller/database access.
"""
from __future__ import annotations

import argparse
from contextlib import closing, contextmanager
from datetime import datetime, timezone
import json
import math
from pathlib import Path
import secrets
import sqlite3

from . import production_knowledge as pk
from . import review_control as rc


class Blocked(ValueError):
    pass


ROUTES = {'production', 'show', 'research', 'plan', 'operations'}
ROLES = {'faithful_motion', 'directional_design', 'accepted_quality',
         'exact_asset', 'negative_control', 'source_evidence'}
STAGES = {'BRIEFING': 'planner', 'EXECUTING': 'builder', 'REVIEWING': 'reviewer',
          'EVIDENCE_NEEDED': 'reviewer'}
READY = {'READY_FOR_DIRECTOR', 'READY_FOR_DIRECTOR_AV', 'COMPLETE'}


def require(value, message):
    if not value:
        raise Blocked(message)


def nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def rows(items):
    try:
        return rc.unique(items)
    except (ValueError, TypeError, KeyError) as e:
        raise Blocked('INVALID_ROWS') from e


def bindings(root, items):
    require(isinstance(items, dict) and items, 'MISSING_BINDINGS')
    for item in items.values():
        rc.binding(root, item)


def validate_brief(root, brief, route):
    require(brief.get('schema') == 1 and brief.get('route') == route, 'BRIEF_ROUTE')
    for field in ('intent', 'audience_result', 'strategy', 'early_proof', 'scope', 'exclusions'):
        require(nonempty(brief.get(field)), 'MISSING_BRIEF:' + field)
    require(brief.get('open_decisions') == [], 'DIRECTOR_DECISION_REQUIRED')
    require(brief.get('offline_only') is True, 'LIVE_DRIVER_NOT_QUALIFIED')
    require(brief.get('protected'), 'PROTECTED_SCOPE_REQUIRED')
    bindings(root, brief['source_bindings'])
    task = pk.read_json(root, brief['knowledge_task'])
    require(brief['knowledge_task'] in {b['path'] for b in brief['source_bindings'].values()},
            'UNBOUND_KNOWLEDGE_TASK')
    fresh = pk.task_packet(root, task)
    require(fresh['dispatch_ready'] and fresh['packet_digest'] == brief['knowledge_digest'],
            'STALE_OR_BLOCKED_KNOWLEDGE')
    reqs = rows(brief['requirements'])
    mapping = brief['knowledge_mapping']
    require(set(mapping) == {r['id'] for r in fresh['obligations']}, 'KNOWLEDGE_COVERAGE')
    for item in mapping.values():
        require(nonempty(item.get('reason')) and item.get('requirements') and
                set(item['requirements']) <= set(reqs), 'KNOWLEDGE_APPLICATION')
    for r in reqs.values():
        require(nonempty(r.get('criterion')) and r.get('modes') and
                set(r['modes']) <= rc.MODES, 'INVALID_REQUIREMENT')
        require(type(r.get('director_av')) is bool, 'UNDECLARED_REVIEW_OWNER')
        if r['director_av']:
            require(set(r['modes']) <= {'direct_motion', 'direct_audio'}, 'VISIBLE_FAILURE_NOT_HUMAN_AV')
        else:
            require(all(brief['capabilities'].get(m) is True for m in r['modes']),
                    'UNAVAILABLE_AGENT_REVIEW')
    require(any(not r['director_av'] for r in reqs.values()), 'NO_AGENT_CHECKS')
    references = rows(brief['references'])
    for ref in references.values():
        require(ref.get('role') in ROLES, 'REFERENCE_ROLE')
        rc.binding(root, ref['binding'])
        for field in ('authority', 'scope', 'fidelity', 'allowed_variation', 'not_authority'):
            require(nonempty(ref.get(field)), 'REFERENCE_CONTRACT:' + field)
        aspects = rows(ref['aspects'])
        for aspect in aspects.values():
            require(nonempty(aspect.get('instruction')) and aspect.get('requirements') and
                    set(aspect['requirements']) <= set(reqs), 'REFERENCE_ASPECT_COVERAGE')
            require(len({reqs[k]['director_av'] for k in aspect['requirements']}) == 1,
                    'REFERENCE_ASPECT_MIXED_OWNERS_SPLIT')
        if ref['role'] == 'faithful_motion':
            interval = ref.get('time_range_seconds')
            require(isinstance(interval, list) and len(interval) == 2 and
                    all(type(x) in {int, float} and math.isfinite(x) for x in interval) and
                    0 <= interval[0] < interval[1], 'MOTION_REFERENCE_RANGE')
    require(set(brief['reference_plan']) == set(references), 'PLANNING_REFERENCE_COVERAGE')
    for rid, application in brief['reference_plan'].items():
        require(application.get('reference_digest') == pk.digest(references[rid]) and
                nonempty(application.get('application')), 'PLANNING_REFERENCE_ROLE_LOST')
    # Engine changes invalidate old agreements even if the input media is identical.
    return pk.digest({'brief': brief, 'controller': pk.file_hash(Path(__file__)),
                      'review': pk.file_hash(Path(rc.__file__))})


def review_result(root, brief, candidate, review, fingerprint):
    require(review.get('fingerprint') == fingerprint, 'STALE_REVIEW')
    require(review.get('candidate_digest') == pk.digest(candidate), 'WRONG_CANDIDATE')
    checks = rows(review['checks'])
    reqs = rows(brief['requirements'])
    require(set(checks) == set(reqs), 'CHECK_COVERAGE')
    evidence = review.get('evidence', {})
    bindings(root, {k: e['binding'] for k, e in evidence.items()})
    for e in evidence.values():
        require(e.get('mode') in rc.MODES and brief['capabilities'].get(e['mode']) is True,
                'UNAVAILABLE_EVIDENCE_MODE')
        require(e.get('candidate_digest') == pk.digest(candidate) and
                nonempty(e.get('scope')), 'UNBOUND_EVIDENCE')
    failures, pending, missing = [], [], []
    for rid, req in reqs.items():
        check = checks[rid]
        require(check.get('status') in {'PASS', 'FAIL', 'NOT_RUN'}, 'INVALID_VERDICT')
        require(nonempty(check.get('observation')) and nonempty(check.get('comparison')),
                'MISSING_OBSERVATION')
        ev = check.get('evidence', [])
        require(isinstance(ev, list) and set(ev) <= set(evidence), 'UNKNOWN_EVIDENCE')
        if req['director_av']:
            require(check['status'] != 'PASS', 'DIRECTOR_AV_CANNOT_BE_SELF_PASSED')
            (failures if check['status'] == 'FAIL' else pending).append(rid)
        else:
            if check['status'] == 'NOT_RUN':
                missing.append(rid)
                continue
            require(ev, 'MISSING_AGENT_EVIDENCE')
            require(set(req['modes']) <= {evidence[k]['mode'] for k in ev}, 'WRONG_EVIDENCE_MODE')
            if check['status'] == 'FAIL':
                failures.append(rid)
    refs = rows(brief['references'])
    uses = review['reference_checks']
    require(set(uses) == set(refs), 'REVIEW_REFERENCE_COVERAGE')
    for rid, ref in refs.items():
        if ref['role'] == 'negative_control' and ref['binding']['sha256'] in {
                b['sha256'] for b in candidate['artifacts'].values()}:
            failures.append('KNOWN_REJECTED_ARTIFACT:' + rid)
        use = uses[rid]
        require(use.get('reference_digest') == pk.digest(ref), 'REFERENCE_ROLE_CHANGED')
        require(nonempty(use.get('observation')) and nonempty(use.get('comparison')),
                'REFERENCE_COMPARISON_REQUIRED')
        require(use.get('evidence') and set(use['evidence']) <= set(evidence), 'REFERENCE_EVIDENCE')
        aspects = rows(use['aspects'])
        require(set(aspects) == set(rows(ref['aspects'])), 'REFERENCE_ASPECT_REVIEW')
        for aspect in aspects.values():
            require(aspect.get('status') in {'PASS', 'FAIL', 'NOT_RUN'} and
                    nonempty(aspect.get('observation')), 'REFERENCE_ASPECT_VERDICT')
            linked = rows(ref['aspects'])[aspect['id']]['requirements']
            if all(reqs[k]['director_av'] for k in linked):
                require(aspect['status'] != 'PASS', 'REFERENCE_AV_CANNOT_BE_SELF_PASSED')
                (pending if aspect['status'] == 'NOT_RUN' else failures).append('reference:' + rid + ':' + aspect['id'])
                continue
            if aspect['status'] == 'NOT_RUN':
                missing.append('reference:' + rid + ':' + aspect['id'])
            elif aspect['status'] == 'FAIL':
                failures.append('reference:' + rid + ':' + aspect['id'])
            else:
                needed = {m for k in linked for m in reqs[k]['modes']}
                require(needed <= {evidence[k]['mode'] for k in use['evidence']}, 'REFERENCE_WRONG_EVIDENCE_MODE')
    for field in ('audience_read', 'strongest_counterexample', 'adjacent_review'):
        require(nonempty(review.get(field)), 'MISSING_REVIEW:' + field)
    require(isinstance(review.get('open_visible_defects'), list), 'DEFECT_INVENTORY_REQUIRED')
    failures += ['visible:' + d for d in review['open_visible_defects']]
    return {'failures': sorted(set(failures)), 'missing_evidence': sorted(set(missing)), 'pending_director_av': pending,
            'production_approved': False, 'director_approved': False}


class Controller:
    """Single SQLite transaction per transition; append-only event snapshots."""

    def __init__(self, root, database):
        self.root = Path(root).resolve()
        self.database = rc.path(self.root, str(database))
        self.database.parent.mkdir(parents=True, exist_ok=True)
        with closing(self.connect()) as con:
            con.executescript('''
                CREATE TABLE IF NOT EXISTS events (
                    seq INTEGER PRIMARY KEY, task TEXT NOT NULL, event_id TEXT UNIQUE NOT NULL,
                    request_hash TEXT NOT NULL, utc TEXT NOT NULL, action TEXT NOT NULL,
                    state TEXT NOT NULL, state_hash TEXT NOT NULL);
                CREATE TRIGGER IF NOT EXISTS events_no_update BEFORE UPDATE ON events
                    BEGIN SELECT RAISE(ABORT, 'immutable event'); END;
                CREATE TRIGGER IF NOT EXISTS events_no_delete BEFORE DELETE ON events
                    BEGIN SELECT RAISE(ABORT, 'immutable event'); END;
                CREATE TABLE IF NOT EXISTS heavy_job (
                    slot INTEGER PRIMARY KEY CHECK(slot=1), task TEXT, job_id TEXT UNIQUE);
                CREATE TABLE IF NOT EXISTS jobs (
                    job_id TEXT PRIMARY KEY, task TEXT, status TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS deliverables (
                    deliverable_id TEXT PRIMARY KEY, task TEXT UNIQUE NOT NULL);
            ''')

    def connect(self):
        con = sqlite3.connect(self.database, timeout=10)
        con.row_factory = sqlite3.Row
        return con

    @contextmanager
    def transaction(self):
        con = self.connect()
        try:
            con.execute('BEGIN IMMEDIATE')
            yield con
            con.commit()
        except BaseException:
            con.rollback()
            raise
        finally:
            con.close()

    def _state(self, con, task):
        row = con.execute('SELECT * FROM events WHERE task=? ORDER BY seq DESC LIMIT 1', (task,)).fetchone()
        require(row is not None, 'UNKNOWN_TASK')
        state = json.loads(row['state'])
        require(pk.digest(state) == row['state_hash'], 'CORRUPT_STATE')
        return state

    def state(self, task):
        with closing(self.connect()) as con:
            state = self._state(con, task)
        return {k: v for k, v in state.items() if k != 'ticket'}

    def events(self, task):
        with closing(self.connect()) as con:
            return [{'seq': r['seq'], 'utc': r['utc'], 'action': r['action'],
                     'stage': json.loads(r['state'])['stage'],
                     'cycle': json.loads(r['state'])['cycle'],
                     'findings': json.loads(r['state']).get('findings', {})}
                    for r in con.execute('SELECT * FROM events WHERE task=? ORDER BY seq', (task,))]

    def _change(self, task, event_id, action, payload, fn):
        require(nonempty(task) and nonempty(event_id), 'IDENTITY_REQUIRED')
        digest = pk.digest({'task': task, 'action': action, 'payload': payload})
        with self.transaction() as con:
            prior = con.execute('SELECT * FROM events WHERE event_id=?', (event_id,)).fetchone()
            if prior:
                require(prior['request_hash'] == digest, 'EVENT_ID_CONFLICT')
                old = json.loads(prior['state'])
                if action == 'deliver':
                    current = self._state(con, task)
                    require(current['stage'] in READY and current.get('fingerprint') == old.get('fingerprint')
                            and current.get('candidate') == old.get('candidate')
                            and current.get('result') == old.get('result'), 'STALE_RECEIPT')
                    self._fresh(current)
                    if current['stage'] == 'COMPLETE':
                        bindings(self.root, current['result']['artifacts'])
                    else:
                        findings = review_result(self.root, current['brief'], current['candidate'], current['review'], current['fingerprint'])
                        require(not findings['failures'] and not findings['missing_evidence'], 'REVIEW_FAILED')
                return self._public(old)
            state = fn(con)
            con.execute('INSERT INTO events(task,event_id,request_hash,utc,action,state,state_hash) VALUES(?,?,?,?,?,?,?)',
                        (task, event_id, digest, datetime.now(timezone.utc).isoformat(), action,
                         json.dumps(state, sort_keys=True), pk.digest(state)))
            return self._public(state)

    @staticmethod
    def _public(state):
        return {k: v for k, v in state.items() if k != 'ticket'}

    @staticmethod
    def _stage(state, stage):
        state['stage'] = stage
        state['ticket'] = secrets.token_hex(24) if stage in STAGES else None
        return state

    def create(self, task, route, authority, event_id, max_corrections=2, direction=None):
        require(route in ROUTES and type(max_corrections) is int and 0 <= max_corrections <= 20,
                'INVALID_ROUTE_OR_LIMIT')
        rc.binding(self.root, authority)
        if route == 'production':
            require(isinstance(direction, dict) and nonempty(direction.get('intent'))
                    and nonempty(direction.get('deliverable_id'))
                    and direction.get('references') and direction.get('protected'), 'DIRECTOR_CONTEXT_REQUIRED')
            rows(direction['references'])
            for ref in direction['references']:
                rc.binding(self.root, ref['binding'])
        def apply(con):
            require(not con.execute('SELECT 1 FROM events WHERE task=?', (task,)).fetchone(), 'TASK_EXISTS')
            if route == 'production':
                require(not con.execute('SELECT 1 FROM deliverables WHERE deliverable_id=?',
                                        (direction['deliverable_id'],)).fetchone(), 'DELIVERABLE_ALREADY_TRACKED')
                con.execute('INSERT INTO deliverables VALUES(?,?)', (direction['deliverable_id'], task))
            return self._stage({'task': task, 'route': route, 'cycle': 0,
                                'max_corrections': max_corrections, 'authority': authority,
                                'direction': direction,
                                'offline_only': True, 'production_approved': False},
                               'BRIEFING' if route == 'production' else 'LIGHTWEIGHT')
        return self._change(task, event_id, 'create', [route, authority, max_corrections, direction], apply)

    def _fresh(self, state):
        rc.binding(self.root, state['authority'])
        if state.get('revision_authority'):
            rc.binding(self.root, state['revision_authority'])
        if state.get('direction'):
            for ref in state['direction']['references']:
                rc.binding(self.root, ref['binding'])
        if 'brief' in state:
            require(validate_brief(self.root, state['brief'], state['route']) == state['fingerprint'],
                    'STALE_BRIEF')
        if state.get('candidate'):
            bindings(self.root, state['candidate']['artifacts'])

    def packet(self, task):
        """Trusted adapter only: stage-scoped ticket, not included in progress log."""
        with closing(self.connect()) as con:
            state = self._state(con, task)
        self._fresh(state)
        require(state['stage'] in STAGES, 'NO_STAGE_DISPATCH')
        packet = {'task': task, 'stage': state['stage'], 'actor': STAGES[state['stage']],
                  'ticket': state['ticket'], 'cycle': state['cycle'],
                  'max_corrections': state['max_corrections'], 'offline_only': True,
                  'direction': state['direction'], 'authority': state['authority']}
        if 'brief' in state:
            packet.update(brief=state['brief'], fingerprint=state['fingerprint'])
        if STAGES.get(state['stage']) == 'reviewer':
            packet['candidate'] = state['candidate']
            # Builder's narrative/application claims are deliberately not supplied.
        elif state.get('findings'):
            packet['feedback'] = state['findings']
        return packet

    def submit(self, task, actor, ticket, result, event_id):
        def apply(con):
            state = self._state(con, task)
            require(STAGES.get(state['stage']) == actor and state['ticket'] == ticket,
                    'WRONG_STAGE_OR_TICKET')
            require(not con.execute('SELECT 1 FROM heavy_job WHERE task=?', (task,)).fetchone(), 'JOB_STILL_ACTIVE')
            self._fresh(state)
            if actor == 'planner':
                require(result.get('references') == state['direction']['references'] and
                        result.get('protected') == state['direction']['protected'], 'PLANNER_CHANGED_DIRECTOR_AUTHORITY')
                state['fingerprint'] = validate_brief(self.root, result, state['route'])
                state['brief'] = result
                return self._stage(state, 'EXECUTING')
            if actor == 'builder':
                require(result['fingerprint'] == state['fingerprint'], 'BUILDER_STALE_BRIEF')
                references = rows(state['brief']['references'])
                uses = result['reference_uses']
                require(set(uses) == set(references), 'EXECUTION_REFERENCE_COVERAGE')
                for rid, ref in references.items():
                    require(uses[rid].get('reference_digest') == pk.digest(ref) and
                            nonempty(uses[rid].get('application')), 'EXECUTION_REFERENCE_ROLE_LOST')
                candidate = result['candidate']
                require(nonempty(candidate.get('version')), 'CANDIDATE_VERSION')
                bindings(self.root, candidate['artifacts'])
                state['candidate'] = candidate
                state['builder_record'] = result
                state['evidence_cycles'] = 0
                return self._stage(state, 'REVIEWING')
            findings = review_result(self.root, state['brief'], state['candidate'], result, state['fingerprint'])
            state['review'] = result
            state['findings'] = findings
            if findings['failures']:
                if state['cycle'] >= state['max_corrections']:
                    return self._stage(state, 'REPLAN_REQUIRED')
                state['cycle'] += 1
                return self._stage(state, 'EXECUTING')
            if findings['missing_evidence']:
                state['evidence_cycles'] = state.get('evidence_cycles', 0) + 1
                return self._stage(state, 'EVIDENCE_NEEDED' if state['evidence_cycles'] <= 2 else 'BLOCKED')
            return self._stage(state, 'READY_FOR_DIRECTOR_AV' if findings['pending_director_av'] else 'READY_FOR_DIRECTOR')
        return self._change(task, event_id, 'submit:' + actor, [ticket, result], apply)

    def revise(self, task, brief, decision, reason, event_id):
        """Controller-owned Director direction update. Never resets the retry cap."""
        rc.binding(self.root, decision)
        require(nonempty(reason), 'REVISION_REASON')
        def apply(con):
            state = self._state(con, task)
            require(state['route'] == 'production', 'WRONG_ROUTE')
            require(not con.execute('SELECT 1 FROM heavy_job WHERE task=?', (task,)).fetchone(), 'JOB_STILL_ACTIVE')
            fingerprint = validate_brief(self.root, brief, state['route'])
            state.update(brief=brief, fingerprint=fingerprint, revision_reason=reason, revision_authority=decision)
            state['direction'].update(intent=brief['intent'], references=brief['references'], protected=brief['protected'])
            for key in ('candidate', 'review', 'builder_record'):
                state.pop(key, None)
            # Exhaustion cannot be bypassed by modifying intent/references.
            return self._stage(state, 'REPLAN_REQUIRED' if state['stage'] == 'REPLAN_REQUIRED' else 'EXECUTING')
        return self._change(task, event_id, 'revise', [brief, decision, reason], apply)

    def complete_lightweight(self, task, result, event_id):
        def apply(con):
            state = self._state(con, task)
            require(state['stage'] == 'LIGHTWEIGHT', 'WRONG_ROUTE')
            self._fresh(state)
            require(result.get('offline_only') is True and nonempty(result.get('verification')),
                    'LIGHTWEIGHT_VERIFICATION')
            bindings(self.root, result['artifacts'])
            state['result'] = result
            return self._stage(state, 'COMPLETE')
        return self._change(task, event_id, 'complete_lightweight', result, apply)

    def deliver(self, task, event_id):
        def apply(con):
            state = self._state(con, task)
            require(state['stage'] in READY, 'NOT_READY')
            self._fresh(state)
            if state['stage'] == 'COMPLETE':
                bindings(self.root, state['result']['artifacts'])
            else:
                findings = review_result(self.root, state['brief'], state['candidate'], state['review'], state['fingerprint'])
                require(not findings['failures'] and not findings['missing_evidence'], 'REVIEW_FAILED')
            state['receipt'] = {'stage': state['stage'], 'offline_replay_only': True,
                                'production_approved': False, 'director_approved': False,
                                'artifacts': state.get('candidate', state.get('result'))['artifacts']}
            return state
        return self._change(task, event_id, 'deliver', {}, apply)

    def job(self, task, job_id, action, event_id):
        """Reservation only, no process launch. Crashed jobs require explicit release."""
        require(action in {'acquire', 'release'}, 'INVALID_JOB_ACTION')
        def apply(con):
            state = self._state(con, task)
            if action == 'acquire':
                self._fresh(state)
                require(state['stage'] == 'EXECUTING', 'JOB_OUTSIDE_EXECUTION')
                require(not con.execute('SELECT 1 FROM heavy_job').fetchone(), 'HEAVY_JOB_BUSY')
                require(not con.execute('SELECT 1 FROM jobs WHERE job_id=?', (job_id,)).fetchone(), 'DUPLICATE_JOB')
                con.execute('INSERT INTO jobs VALUES(?,?,?)', (job_id, task, 'ACTIVE'))
                con.execute('INSERT INTO heavy_job VALUES(1,?,?)', (task, job_id))
            else:
                require(con.execute('SELECT 1 FROM heavy_job WHERE task=? AND job_id=?', (task, job_id)).fetchone(), 'WRONG_JOB_OWNER')
                con.execute('DELETE FROM heavy_job WHERE task=? AND job_id=?', (task, job_id))
                con.execute('UPDATE jobs SET status=? WHERE job_id=?', ('RELEASED', job_id))
            state['last_job'] = {'id': job_id, 'action': action}
            return state
        return self._change(task, event_id, 'job:' + action, job_id, apply)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path.cwd())
    parser.add_argument('--database', default='.runtime/workflow323.sqlite3')
    parser.add_argument('command', choices=['status', 'events'])
    parser.add_argument('--task', required=True)
    args = parser.parse_args(argv)
    try:
        controller = Controller(args.root, args.database)
        value = controller.state(args.task) if args.command == 'status' else controller.events(args.task)
        print(json.dumps(value, indent=2))
        return 0
    except (Blocked, rc.Blocked, pk.KnowledgeError, OSError, ValueError, KeyError, TypeError) as e:
        print(json.dumps({'blocked': True, 'error': str(e)}))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
