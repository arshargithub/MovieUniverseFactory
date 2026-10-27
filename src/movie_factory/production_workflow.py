"""Staged workflow controller. No model, shell, render or network dispatch.

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
from . import retrospective as retro


class Blocked(ValueError):
    pass


ROUTES = {'production', 'show', 'research', 'plan', 'operations', 'engineering'}
ROLES = {'faithful_motion', 'directional_design', 'accepted_quality',
         'exact_asset', 'negative_control', 'source_evidence'}
STAGES = {'BRIEFING': 'planner', 'EXECUTING': 'builder', 'REVIEWING': 'reviewer',
          'EVIDENCE_NEEDED': 'reviewer'}
READY = {'READY_FOR_DIRECTOR', 'READY_FOR_DIRECTOR_AV', 'COMPLETE'}


def stage_actor(state):
    if state['stage'] == 'BRIEFING' and state.get('planning_step') == 'CHALLENGING':
        return 'reviewer'
    return STAGES.get(state['stage'])


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


def validate_brief(root, brief, route, mode='offline'):
    from . import expert_planning as ep
    require(brief.get('schema') == 1 and brief.get('route') == route, 'BRIEF_ROUTE')
    for field in ('intent', 'audience_result', 'strategy', 'early_proof', 'scope', 'exclusions'):
        require(nonempty(brief.get(field)), 'MISSING_BRIEF:' + field)
    require(brief.get('open_decisions') == [], 'DIRECTOR_DECISION_REQUIRED')
    require(mode in {'offline', 'frozen_evidence', 'local_native'}, 'LIVE_DRIVER_NOT_QUALIFIED')
    require(brief.get('offline_only') is (mode == 'offline'), 'WORKFLOW_MODE_MISMATCH')
    if mode == 'frozen_evidence':
        require(brief.get('frozen_evidence_only') is True, 'FROZEN_EVIDENCE_REQUIRED')
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
    from . import reference_readiness as rr
    rr.brief(root, brief, required=mode == 'local_native')
    if mode == 'local_native' and brief.get('work_unit'):
        require(brief['work_unit'].get('version') == 2, 'NATIVE_UNIT_SCOPE_CONTRACT386_REQUIRED')
    ep.validate(brief)
    # Engine changes invalidate old agreements even if the input media is identical.
    return pk.digest({'brief': brief, 'controller': pk.file_hash(Path(__file__)),
                      'expert_planning': pk.file_hash(Path(ep.__file__)),
                      'review': pk.file_hash(Path(rc.__file__))})


def review_result(root, brief, candidate, review, fingerprint):
    from . import expert_planning as ep
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
    intent_failures, intent_missing, gaps = ep.review_intent(brief, review, evidence)
    failures += intent_failures + ['planning:' + g for g in gaps]
    missing += intent_missing
    from . import reference_readiness as rr
    ref_fail, ref_missing = rr.review(brief, review, evidence)
    failures += ref_fail
    missing += ref_missing
    return {'failures': sorted(set(failures)), 'missing_evidence': sorted(set(missing)), 'pending_director_av': pending,
            'planning_gaps': gaps,
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
                CREATE TABLE IF NOT EXISTS routing (
                    id TEXT PRIMARY KEY, utc TEXT NOT NULL, decision TEXT NOT NULL);
                CREATE TRIGGER IF NOT EXISTS routing_no_update BEFORE UPDATE ON routing
                    BEGIN SELECT RAISE(ABORT, 'immutable routing'); END;
                CREATE TRIGGER IF NOT EXISTS routing_no_delete BEFORE DELETE ON routing
                    BEGIN SELECT RAISE(ABORT, 'immutable routing'); END;
            ''')
            retro.install(con)

    def route_request(self, request_id, request, continuation=None):
        from . import task_router as tr
        require(nonempty(request_id), 'REQUEST_ID_REQUIRED')
        rc.binding(self.root, request['authority'])
        with self.transaction() as con:
            parent = None
            if continuation:
                state = self._state(con, continuation)
                require(state.get('routing'), 'LEGACY_ROUTE_REQUIRES_MIGRATION')
                self._fresh(state)
                parent = state['routing']
                require(request.get('continuation') is True, 'CONTINUATION_DECLARATION_REQUIRED')
            decision = tr.decide(request, parent)
            decision.update(id=request_id, continuation_task=continuation)
            old = con.execute('SELECT decision FROM routing WHERE id=?', (request_id,)).fetchone()
            if old:
                require(json.loads(old[0]) == decision, 'REQUEST_ID_CONFLICT')
            else:
                con.execute('INSERT INTO routing VALUES(?,?,?)',
                            (request_id, datetime.now(timezone.utc).isoformat(), json.dumps(decision, sort_keys=True)))
        return decision

    def routing(self, request_id):
        from . import task_router as tr
        with closing(self.connect()) as con:
            row = con.execute('SELECT decision FROM routing WHERE id=?', (request_id,)).fetchone()
        require(row is not None, 'ROUTE_FIRST_REQUIRED')
        value = json.loads(row[0])
        tr.validate(self.root, value)
        return value

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
                     'planning_step': json.loads(r['state']).get('planning_step'),
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
                    retro.guard(con, current, delivery=True)
                    retro.check_proofs(self.root, con, current)
                    if current['stage'] == 'COMPLETE':
                        bindings(self.root, current['result']['artifacts'])
                    else:
                        findings = review_result(self.root, current['brief'], current['candidate'], current['review'], current['fingerprint'])
                        require(not findings['failures'] and not findings['missing_evidence'], 'REVIEW_FAILED')
                return self._public(old)
            previous = con.execute('SELECT state FROM events WHERE task=? ORDER BY seq DESC LIMIT 1', (task,)).fetchone()
            previous = json.loads(previous[0]) if previous else None
            state = fn(con)
            if (state['route']=='production' and state['stage']=='REPLAN_REQUIRED'
                    and (not previous or previous['stage']!='REPLAN_REQUIRED')):
                retro.auto_outcome(con,state,'exhaustion:'+event_id,
                    [dict(requirement='__allowance__',status='NOT_TESTED',observation='Correction allowance exhausted; synthesis required before continuation.')],
                    origin='exhaustion',evidence={'authority':state['authority']})
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

    def create(self, task, route, authority, event_id, max_corrections=2, direction=None, mode='offline', admission=None):
        from . import task_router as tr
        require(route in ROUTES and type(max_corrections) is int and 0 <= max_corrections <= 20,
                'INVALID_ROUTE_OR_LIMIT')
        require(mode in {'offline', 'frozen_evidence', 'local_native'} and (mode == 'offline' or route == 'production'),
                'LIVE_DRIVER_NOT_QUALIFIED')
        rc.binding(self.root, authority)
        if admission is None:
            require(mode != 'local_native', 'ROUTE_FIRST_REQUIRED')
            # Historical offline fixtures remain reproducible, but now enter
            # routing first. This is not a prospectively classified live request.
            op = {'production': 'render', 'show': 'display', 'research': 'research',
                  'plan': 'plan', 'operations': 'backup', 'engineering': 'code'}[route]
            admission = 'legacy-simulation:' + event_id
            self.route_request(admission, {'text': (direction or {}).get('intent', 'Legacy ' + route),
                'operations': [op], 'authority': authority,
                'rationale': 'Offline/frozen compatibility record; not native authorization.'})
        routed = self.routing(admission)
        require(routed['route'] == route, 'REQUEST_ROUTE_MISMATCH')
        require(routed['request']['authority'] == authority, 'REQUEST_AUTHORITY_MISMATCH')
        require(routed.get('continuation_task') is None, 'CONTINUE_EXISTING_TASK_NO_NEW_LIMIT')
        if mode == 'local_native':
            require(self.database == self.root / tr.DATABASE, 'NATIVE_CANONICAL_CONTROLLER_REQUIRED')
        if route == 'production':
            from . import planning_pipeline as pp
            require(isinstance(direction, dict) and nonempty(direction.get('intent'))
                    and nonempty(direction.get('deliverable_id'))
                    and direction.get('references') and direction.get('protected'), 'DIRECTOR_CONTEXT_REQUIRED')
            require(isinstance(direction.get('beat_intents'), dict) and direction['beat_intents']
                    and all(nonempty(k) and nonempty(v) for k, v in direction['beat_intents'].items()),
                    'DIRECTOR_BEAT_SCOPE_REQUIRED')
            rows(direction['references'])
            for ref in direction['references']:
                rc.binding(self.root, ref['binding'])
            pp.sources(self.root, direction)
            pp.source_context(self.root, direction)
        def apply(con):
            require(not con.execute('SELECT 1 FROM events WHERE task=?', (task,)).fetchone(), 'TASK_EXISTS')
            if route == 'production':
                require(not con.execute('SELECT 1 FROM deliverables WHERE deliverable_id=?',
                                        (direction['deliverable_id'],)).fetchone(), 'DELIVERABLE_ALREADY_TRACKED')
                con.execute('INSERT INTO deliverables VALUES(?,?)', (direction['deliverable_id'], task))
                retro.append(con,task,'initialize','initialize',dict(version=retro.VERSION,engine=retro.engine()))
            return self._stage({'task': task, 'route': route, 'cycle': 0,
                                'max_corrections': max_corrections, 'authority': authority,
                                'direction': direction,
                                'routing': routed,
                                'planning_step': 'GROUNDING' if route == 'production' else None,
                                'planning_artifacts': {}, 'planning_version': 1,
                                'planning_engine': pp.engine_digest() if route == 'production' else None,
                                'mode': mode, 'offline_only': mode == 'offline',
                                'frozen_evidence_only': mode == 'frozen_evidence', 'production_approved': False},
                               'BRIEFING' if route == 'production' else 'LIGHTWEIGHT')
        return self._change(task, event_id, 'create', [route, authority, max_corrections, direction, mode, admission], apply)

    def _fresh(self, state):
        with closing(self.connect()) as con:
            retro.fresh(con,state)
            retro.validate_evidence(self.root,con,state)
        if state.get('routing'):
            require(self.routing(state['routing']['id']) == state['routing'], 'ROUTE_CHANGED')
        rc.binding(self.root, state['authority'])
        if state.get('revision_authority'):
            rc.binding(self.root, state['revision_authority'])
        if state.get('direction'):
            from . import planning_pipeline as pp
            require(state.get('planning_version') == 1, 'LEGACY_PLANNING_REQUIRES_MIGRATION')
            require(state.get('planning_engine') == pp.engine_digest(), 'PLANNING_ENGINE_CHANGED_REVIEWED_MIGRATION_REQUIRED')
            pp.sources(self.root, state['direction'])
            for ref in state['direction']['references']:
                rc.binding(self.root, ref['binding'])
        if 'brief' in state:
            require(validate_brief(self.root, state['brief'], state['route'], state.get('mode', 'offline')) == state['fingerprint'],
                    'STALE_BRIEF')
        if state.get('candidate'):
            bindings(self.root, state['candidate']['artifacts'])

    def packet(self, task):
        """Trusted adapter only: stage-scoped ticket, not included in progress log."""
        from . import expert_planning as ep
        with closing(self.connect()) as con:
            state = self._state(con, task)
        self._fresh(state)
        with closing(self.connect()) as con:
            if state['stage']=='EXECUTING':
                retro.guard(con,state)
                retro.check_proofs(self.root,con,state)
            retrospective = retro.packet(con,state)
        require(state['stage'] in STAGES, 'NO_STAGE_DISPATCH')
        packet = {'task': task, 'stage': state['stage'], 'actor': stage_actor(state),
                  'ticket': state['ticket'], 'cycle': state['cycle'],
                  'max_corrections': state['max_corrections'], 'offline_only': state['offline_only'],
                  'frozen_evidence_only': state.get('frozen_evidence_only', False),
                  'direction': state['direction'], 'authority': state['authority']}
        packet['retrospective'] = retrospective
        from . import reference_readiness as rr
        packet['reference_contract'] = rr.contract()
        from . import planning_pipeline as pp
        if state.get('direction'):
            packet['source_context'] = pp.source_context(self.root, state['direction'])
            _, fresh = pp.sources(self.root, state['direction'])
            packet['grounding_knowledge'] = {'packet_digest': fresh['packet_digest'],
                                            'obligations': fresh['obligations']}
        if state.get('revision_authority'):
            packet['direction_revision'] = {'reason': state['revision_reason'],
                'source_context': pp.source_context(self.root, {'context_sources': [
                    {'id': 'revision', 'binding': state['revision_authority'],
                     **({'lines': state['revision_authority']['lines']} if 'lines' in state['revision_authority'] else {})}]})}
        if state['stage'] == 'BRIEFING':
            packet.update(pp.packet(state))
            packet['expert_instruction'] = pp.GOALS[state['planning_step']]
            packet['expert_contract'] = ep.contract()
            return packet
        if 'brief' in state:
            packet.update(brief=state['brief'], fingerprint=state['fingerprint'])
        if packet['actor'] == 'planner':
            packet['expert_instruction'] = ep.PLANNER_INSTRUCTION
            packet['expert_contract'] = ep.contract()
        elif packet['actor'] == 'reviewer':
            packet['expert_instruction'] = ep.REVIEWER_INSTRUCTION
        if STAGES.get(state['stage']) == 'reviewer':
            packet['candidate'] = state['candidate']
            # Builder's narrative/application claims are deliberately not supplied.
        elif state.get('findings'):
            packet['feedback'] = state['findings']
        return packet

    def submit(self, task, actor, ticket, result, event_id):
        def apply(con):
            state = self._state(con, task)
            require(stage_actor(state) == actor and state['ticket'] == ticket,
                    'WRONG_STAGE_OR_TICKET')
            require(not con.execute('SELECT 1 FROM heavy_job WHERE task=?', (task,)).fetchone(), 'JOB_STILL_ACTIVE')
            self._fresh(state)
            if state['stage'] == 'BRIEFING':
                return self._planning_submit(state, result, con, event_id)
            if actor == 'builder':
                retro.guard(con,state)
                retro.check_proofs(self.root,con,state)
                from . import expert_planning as ep
                ep.validate_execution(state['brief'], result)
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
                if state.get('mode') == 'local_native':
                    from .native_admission import validate_candidate
                    validate_candidate(self, state, result)
                state['candidate'] = candidate
                state['builder_record'] = result
                state['evidence_cycles'] = 0
                return self._stage(state, 'REVIEWING')
            findings = review_result(self.root, state['brief'], state['candidate'], result, state['fingerprint'])
            state['review'] = result
            state['findings'] = findings
            observations = [dict(requirement=r['id'],status=('NOT_TESTED' if r['status']=='NOT_RUN' else r['status']),
                                 observation=r['observation']) for r in result['checks']]
            # A general visible/reference/intent veto cannot be hidden by PASS
            # rows. Preserve an aggregate issue in addition to specific checks.
            if findings['failures']:
                observations.append(dict(requirement='__whole_result__',status='FAIL',observation='; '.join(findings['failures'])))
            def capture():
                retro.auto_outcome(con,state,'review:'+event_id,observations,origin='final_review',
                                   evidence={k:v['binding'] for k,v in result['evidence'].items()},extra=result.get('retrospective_observations'))
            if findings['planning_gaps']:
                capture()
                return self._planning_repair(state, 'DERIVING', findings['planning_gaps'])
            if findings['failures']:
                if state['cycle'] >= state['max_corrections']:
                    self._stage(state, 'REPLAN_REQUIRED'); capture(); return state
                capture()
                state['cycle'] += 1
                return self._stage(state, 'EXECUTING')
            if findings['missing_evidence']:
                capture()
                state['evidence_cycles'] = state.get('evidence_cycles', 0) + 1
                return self._stage(state, 'EVIDENCE_NEEDED' if state['evidence_cycles'] <= 2 else 'BLOCKED')
            capture()
            retro.append(con,task,'closure:'+event_id,'closure',dict(
                result='AWAITING_DIRECTOR_AV' if findings['pending_director_av'] else 'AWAITING_DIRECTOR',
                candidate=state['candidate'],scope=state['brief']['scope'],
                pending=findings['pending_director_av'],production_approved=False))
            return self._stage(state, 'READY_FOR_DIRECTOR_AV' if findings['pending_director_av'] else 'READY_FOR_DIRECTOR')
        return self._change(task, event_id, 'submit:' + actor, [ticket, result], apply)

    def _planning_repair(self, state, target, feedback):
        from . import planning_pipeline as pp
        state['planning_feedback'] = feedback
        if state['cycle'] >= state['max_corrections']:
            return self._stage(state, 'REPLAN_REQUIRED')
        state['cycle'] += 1
        pp.invalidate(state, target)
        return self._stage(state, 'BRIEFING')

    def _planning_submit(self, state, result, con, event_id):
        from . import planning_pipeline as pp
        require(result.get('input_digest') == pp.input_digest(state), 'STALE_PLANNING_INPUT')
        step, direction = state['planning_step'], state['direction']
        if result.get('outcome') == 'needs_director':
            pp.director_decision(result)
            state['decision'] = result['decision']
            return self._stage(state, 'DIRECTOR_DECISION')
        artifacts = state['planning_artifacts']
        if step == 'CHALLENGING':
            target = pp.challenge(direction, result, root=self.root,
                                  readiness=artifacts.get('GROUNDING', {}).get('reference_readiness'),
                                  work_unit=artifacts['STRATEGIZING']['brief'].get('work_unit'))
            if target:
                retro.auto_outcome(con,state,'challenge:'+event_id,
                    [dict(requirement='__planning__',status='FAIL',observation=str(result['issues']))],origin='planning_challenge',
                    extra=result.get('retrospective_observations'))
                return self._planning_repair(state, target, result['issues'])
            brief = artifacts['STRATEGIZING']['brief']
            state['fingerprint'] = validate_brief(self.root, brief, state['route'], state.get('mode', 'offline'))
            state['brief'] = brief
            state['planning_admission'] = result
            retro.plan(con,state,'plan:'+event_id,brief,self.root)
            return self._stage(state, 'EXECUTING')
        require(result.get('outcome') == 'complete' and isinstance(result.get('artifact'), dict), 'PLANNING_ARTIFACT_REQUIRED')
        data = result['artifact']
        if step == 'GROUNDING': pp.grounding(self.root, direction, data,
                                            reference_required=state.get('mode') == 'local_native')
        elif step == 'DERIVING': pp.derivation(self.root, direction, artifacts['GROUNDING'], data)
        elif step == 'STRATEGIZING':
            if data.get('brief', {}).get('expert_plan', {}).get('challenge', {}).get('plan_digest') == '__PARENT_COMPUTES__':
                from . import expert_planning as ep
                data = json.loads(json.dumps(data))
                data['brief'] = ep.seal_planner_response(data['brief'])
            pp.strategy(direction, artifacts['DERIVING'], data)
            validate_brief(self.root, data['brief'], state['route'], state.get('mode', 'offline'))
        else: require(False, 'UNKNOWN_PLANNING_STEP')
        artifacts[step] = data
        state['planning_step'] = pp.STEPS[pp.STEPS.index(step) + 1]
        return self._stage(state, 'BRIEFING')

    def replan(self, task, target, reason, event_id):
        """Agent-owned in-scope method correction; no new authority or counter reset."""
        from . import planning_pipeline as pp
        require(target in pp.STEPS[:3] and nonempty(reason), 'REPLAN_TARGET_REASON')
        def apply(con):
            state = self._state(con, task)
            require(state['route'] == 'production' and state['stage'] not in {'DIRECTOR_DECISION', 'REPLAN_REQUIRED'}, 'REPLAN_NOT_AVAILABLE')
            require(not con.execute('SELECT 1 FROM heavy_job WHERE task=?', (task,)).fetchone(), 'JOB_STILL_ACTIVE')
            self._fresh(state)
            require(all(s in state['planning_artifacts'] for s in pp.STEPS[:pp.STEPS.index(target)]), 'MISSING_UPSTREAM_PLAN')
            return self._planning_repair(state, target, [reason])
        return self._change(task, event_id, 'replan', [target, reason], apply)

    def recover_native_control(self, task, admission, direction, reason, event_id):
        """Bounded technical recovery, never an artistic review/correction reset.

        Only failed source-preserving controls qualify. A fresh continuation
        authority is required and all planning stages are invalidated. Three
        recoveries total per task, independent of event/admission/plan names.
        Closed runs and original authority remain in the append-only history.
        """
        from . import planning_pipeline as pp
        require(nonempty(reason), 'RECOVERY_REASON')
        routed = self.routing(admission)
        require(routed.get('continuation_task') == task, 'RECOVERY_CONTINUATION_REQUIRED')
        rc.binding(self.root, routed['request']['authority'])
        pp.sources(self.root, direction)
        pp.source_context(self.root, direction)
        def apply(con):
            state = self._state(con, task)
            retro.fresh(con,state)
            require(state['mode'] == 'local_native' and state['stage'] in {'EXECUTING', 'REPLAN_REQUIRED'},
                    'RECOVERY_NATIVE_STATE')
            require(not con.execute('SELECT 1 FROM heavy_job').fetchone(), 'JOB_STILL_ACTIVE')
            require(not state.get('candidate') and not state.get('review'), 'RECOVERY_NOT_ARTISTIC_RETRY')
            require(state.get('technical_recoveries', 0) < 3, 'TECHNICAL_RECOVERY_LIMIT')
            for key in ('intent', 'deliverable_id', 'references', 'protected', 'beat_intents'):
                require(direction[key] == state['direction'][key], 'RECOVERY_SCOPE_CHANGED:' + key)
            runs = [json.loads(r[0]) for r in con.execute(
                'SELECT record FROM native_runs WHERE task=? AND cycle=? AND fingerprint=?',
                (task, state['cycle'], state.get('fingerprint')))]
            require(runs and any(r['status'] == 'FAILED' for r in runs)
                    and all(r['status'] in {'FAILED', 'RETURNED'} for r in runs), 'RECOVERY_NO_CLOSED_FAILURE')
            for run in runs:
                verdict = con.execute('SELECT record FROM native_reviews WHERE run=?', (run['id'],)).fetchone()
                require(not verdict or json.loads(verdict[0])['verdict'] == 'PASS', 'RECOVERY_NOT_ARTISTIC_RETRY')
            for step in state['planning_artifacts']['STRATEGIZING']['steps']:
                recipe = step.get('native_recipe')
                require(recipe is not None, 'RECOVERY_ONLY_FIXED_CONTROLS')
                rc.binding(self.root, recipe)
                require(pk.read_json(self.root, recipe['path'])['operation'] in {'nihang_save', 'nihang_render'},
                        'RECOVERY_ONLY_FIXED_CONTROLS')
            old_sources = {s['id']: s for s in state['direction']['context_sources']}
            new_sources = {s['id']: s for s in direction['context_sources']}
            require(set(old_sources) <= set(new_sources), 'RECOVERY_SOURCE_OMISSION')
            for sid, source in old_sources.items():
                require(source['status'] == new_sources[sid]['status']
                        and source['required'] == new_sources[sid]['required'], 'RECOVERY_SOURCE_AUTHORITY_CHANGED')
            state['technical_recoveries'] = state.get('technical_recoveries', 0) + 1
            state.setdefault('recovery_history', []).append({'admission': admission, 'reason': reason,
                'failed_runs': [r['id'] for r in runs if r['status'] == 'FAILED'],
                'prior_fingerprint': state.get('fingerprint'), 'prior_engine': state['planning_engine']})
            state['revision_authority'] = routed['request']['authority']
            state['revision_reason'] = reason
            state['direction'] = direction
            state['planning_engine'] = pp.engine_digest()
            pp.invalidate(state, 'GROUNDING')
            return self._stage(state, 'BRIEFING')
        return self._change(task, event_id, 'recover_native_control', [admission, direction, reason], apply)

    def reconcile_recovery_planner(self, task, admission, reason, event_id):
        """Repair planner implementation before any recovered plan/worker exists."""
        from . import planning_pipeline as pp
        routed = self.routing(admission)
        rc.binding(self.root, routed['request']['authority'])
        require(nonempty(reason), 'RECOVERY_REASON')
        def apply(con):
            state = self._state(con, task)
            retro.fresh(con,state)
            require(state['stage'] == 'BRIEFING' and state['planning_step'] == 'GROUNDING'
                    and not state['planning_artifacts'] and state.get('recovery_history'), 'RECOVERY_PLAN_ALREADY_STARTED')
            require(state['recovery_history'][-1]['admission'] == admission
                    and routed.get('continuation_task') == task, 'RECOVERY_CONTINUATION_REQUIRED')
            require(not con.execute('SELECT 1 FROM heavy_job').fetchone(), 'JOB_STILL_ACTIVE')
            state['revision_reason'] = reason
            state['planning_engine'] = pp.engine_digest()
            return self._stage(state, 'BRIEFING')
        return self._change(task, event_id, 'reconcile_recovery_planner', [admission, reason], apply)

    def revise(self, task, brief, decision, reason, event_id, *, grounding=None):
        """Controller-owned Director direction update. Never resets the retry cap."""
        rc.binding(self.root, decision)
        require(nonempty(reason), 'REVISION_REASON')
        def apply(con):
            state = self._state(con, task)
            retro.fresh(con,state)
            require(state['route'] == 'production', 'WRONG_ROUTE')
            require(not con.execute('SELECT 1 FROM heavy_job WHERE task=?', (task,)).fetchone(), 'JOB_STILL_ACTIVE')
            validate_brief(self.root, brief, state['route'], state.get('mode', 'offline'))
            # Direction and its reviewed knowledge packet may change together.
            # Serial reground+revise used two correction slots and could not
            # bind a new knowledge-task path during revision. Keep this atomic,
            # preserving every required source role/status and prior history.
            if grounding is not None:
                require(nonempty(grounding.get('reason')) and grounding.get('evidence'), 'REVISION_GROUNDING_RECORD')
                for item in grounding['evidence'].values(): rc.binding(self.root,item)
                updated=rows(grounding['context_sources'])
                for old in state['direction']['context_sources']:
                    require(not old['required'] or old['id'] in updated, 'REQUIRED_SOURCE_DROPPED')
                    if old['id'] in updated:
                        require(all(updated[old['id']].get(k)==old[k] for k in
                            ('category','status','required','statement','scope')), 'REGROUND_AUTHORITY_CHANGED')
                state['direction']['context_sources']=grounding['context_sources']
            state.update(revision_reason=reason, revision_authority=decision)
            state['direction'].update(intent=brief['intent'], references=brief['references'], protected=brief['protected'],
                                      beat_intents=brief['expert_plan']['beat_intents'],
                                      knowledge_task=brief['knowledge_task'], knowledge_digest=brief['knowledge_digest'])
            if brief.get('reference_readiness') is not None:
                state['direction']['reference_scope'] = brief['reference_readiness']['scope']
            # Explicit reviewed rebase only. Metadata/status cannot be silently
            # rewritten; source hashes must be bound in the revised brief.
            for source in state['direction']['context_sources']:
                matches = list({pk.digest(b): b for b in brief['source_bindings'].values()
                                if b['path'] == source['binding']['path']}.values())
                require(len(matches) == 1, 'REVISION_SOURCE_COVERAGE')
                source['binding'] = matches[0]
            from . import planning_pipeline as pp
            pp.sources(self.root, state['direction'])
            pp.source_context(self.root, state['direction'])
            state['planning_engine'] = pp.engine_digest()
            state.pop('decision', None)
            return self._planning_repair(state, 'GROUNDING', [reason])
        return self._change(task, event_id, 'revise', [brief, decision, reason, grounding], apply)

    def reground(self, task, context_sources, knowledge_task, knowledge_digest, reason, event_id):
        """Trusted source reconciliation, not a model response or new creative authority.

        May add reviewed sources/rebase bytes; cannot drop required sources or
        promote their status. Original intent, reference roles and limits survive.
        """
        from . import planning_pipeline as pp
        require(nonempty(reason), 'REGROUND_REASON')
        def apply(con):
            state = self._state(con, task)
            retro.fresh(con,state)
            require(state['route'] == 'production' and state['stage'] not in {'DIRECTOR_DECISION', 'REPLAN_REQUIRED'}, 'REGROUND_NOT_AVAILABLE')
            require(not con.execute('SELECT 1 FROM heavy_job WHERE task=?', (task,)).fetchone(), 'JOB_STILL_ACTIVE')
            rc.binding(self.root, state['authority'])
            updated = rows(context_sources)
            for old in state['direction']['context_sources']:
                require(not old['required'] or old['id'] in updated, 'REQUIRED_SOURCE_DROPPED')
                if old['id'] in updated:
                    require(all(updated[old['id']].get(k) == old[k] for k in ('category', 'status', 'required', 'statement', 'scope')), 'REGROUND_AUTHORITY_CHANGED')
            state['direction'].update(context_sources=context_sources, knowledge_task=knowledge_task, knowledge_digest=knowledge_digest)
            pp.sources(self.root, state['direction']); pp.source_context(self.root, state['direction'])
            state['planning_engine'] = pp.engine_digest()
            return self._planning_repair(state, 'GROUNDING', [reason])
        return self._change(task, event_id, 'reground', [context_sources, knowledge_task, knowledge_digest, reason], apply)

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
            retro.guard(con,state,delivery=True)
            retro.check_proofs(self.root,con,state)
            if state['stage'] == 'COMPLETE':
                bindings(self.root, state['result']['artifacts'])
            else:
                findings = review_result(self.root, state['brief'], state['candidate'], state['review'], state['fingerprint'])
                require(not findings['failures'] and not findings['missing_evidence'], 'REVIEW_FAILED')
            state['receipt'] = {'stage': state['stage'], 'offline_replay_only': state['offline_only'],
                                'frozen_evidence_only': state.get('frozen_evidence_only', False),
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
                retro.guard(con,state)
                retro.check_proofs(self.root,con,state)
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

    def retrospective_packet(self, task):
        """Read-only even if the task is exhausted; never authorizes a worker."""
        with closing(self.connect()) as con:
            state = self._state(con,task)
            return retro.packet(con,state)

    def migrate_retrospective(self, task, decision, reconciliation, event_id):
        """Explicit reviewed policy migration; never updates native/planning pins."""
        rc.binding(self.root,decision)
        require(reconciliation.get('evidence') and reconciliation.get('coverage') and
                reconciliation.get('unknowns'), 'RETRO_MIGRATION_RECORD_REQUIRED')
        bindings(self.root,reconciliation['evidence'])
        def apply(con):
            state=self._state(con,task)
            require(state['route']=='production','RETRO_PRODUCTION_ONLY')
            require(not con.execute('SELECT 1 FROM heavy_job').fetchone(),'JOB_STILL_ACTIVE')
            require(reconciliation.get('state_digest')==pk.digest(self._public(state)), 'RETRO_MIGRATION_STALE')
            previous=retro.snapshot(con,task)
            require(previous['version'] != retro.VERSION or previous['engine'] != retro.engine(), 'RETRO_ALREADY_INITIALIZED')
            retro.append(con,task,'policy:'+event_id,'initialize',dict(version=retro.VERSION,engine=retro.engine(),
                         decision=decision,reconciliation=reconciliation))
            if state.get('brief'):
                retro.plan(con,state,'migration-plan:'+event_id,state['brief'],self.root)
            retro.auto_outcome(con,state,'migration-evidence:'+event_id,
                [dict(requirement='__migration__',status='UNKNOWN',observation='Reconcile retained history and unknowns before native continuation.')],
                origin='migration',evidence=reconciliation['evidence'])
            return state
        return self._change(task,event_id,'migrate_retrospective',[decision,reconciliation],apply)

    def retrospective(self, task, action, data, event_id):
        """Source-bound internal analysis API. No stage or correction reset."""
        require(action in {'outcome','response','admit','evaluate','proof','supersede_scope'}, 'RETRO_ACTION')
        def apply(con):
            state = self._state(con,task)
            require(state['route']=='production','RETRO_PRODUCTION_ONLY')
            retro.fresh(con,state)
            if action=='outcome':
                require(data.get('evidence'), 'RETRO_EVIDENCE_REQUIRED')
                bindings(self.root,data['evidence'])
                retro.outcome(con,state,event_id,data)
            elif action=='response': retro.response(self.root,con,state,event_id,data['key'],data['response'])
            elif action=='admit':
                self._fresh(state)
                require(not con.execute('SELECT 1 FROM heavy_job WHERE task=?',(task,)).fetchone(),'JOB_STILL_ACTIVE')
                retro.admit(self.root,con,state,event_id,data['key'],data['challenge'])
            elif action=='evaluate': retro.evaluate(self.root,con,state,event_id,data['key'],data['evaluation'])
            elif action=='supersede_scope': retro.supersede_scope(self.root,con,state,event_id,data)
            else: retro.proof(self.root,con,state,event_id,data)
            if state['stage'] in STAGES:
                self._stage(state,state['stage'])
            return state
        return self._change(task,event_id,'retrospective:'+action,data,apply)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path.cwd())
    parser.add_argument('--database', default='.runtime/workflow323.sqlite3')
    parser.add_argument('command', choices=['status', 'events', 'retrospective'])
    parser.add_argument('--task', required=True)
    args = parser.parse_args(argv)
    try:
        controller = Controller(args.root, args.database)
        value = (controller.state(args.task) if args.command == 'status' else
                 controller.retrospective_packet(args.task) if args.command == 'retrospective' else controller.events(args.task))
        print(json.dumps(value, indent=2))
        return 0
    except (Blocked, rc.Blocked, pk.KnowledgeError, OSError, ValueError, KeyError, TypeError) as e:
        print(json.dumps({'blocked': True, 'error': str(e)}))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
