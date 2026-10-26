"""Append-only retrospective obligations. Declared evidence is not artistic truth.

Policy evaluation is pure; callers append events in the same transaction as the
outcome. No provider, native process, automatic budget or knowledge promotion.
"""
from __future__ import annotations

import json
from pathlib import Path
from . import production_knowledge as pk
from . import review_control as rc

VERSION = 1


def need(ok, message):
    if not ok:
        from .production_workflow import Blocked
        raise Blocked('RETRO_' + message)


def engine():
    return pk.file_hash(Path(__file__))


def install(con):
    con.executescript('''
        CREATE TABLE IF NOT EXISTS retrospective_events (
          seq INTEGER PRIMARY KEY, task TEXT NOT NULL, event_id TEXT NOT NULL,
          record TEXT NOT NULL, digest TEXT NOT NULL, UNIQUE(task,event_id));
        CREATE TRIGGER IF NOT EXISTS retro_no_update BEFORE UPDATE ON retrospective_events
          BEGIN SELECT RAISE(ABORT, 'immutable retrospective'); END;
        CREATE TRIGGER IF NOT EXISTS retro_no_delete BEFORE DELETE ON retrospective_events
          BEGIN SELECT RAISE(ABORT, 'immutable retrospective'); END;
    ''')


def events(con, task):
    out = []
    for row in con.execute('SELECT event_id,record,digest FROM retrospective_events WHERE task=? ORDER BY seq', (task,)):
        record = json.loads(row[1])
        need(pk.digest(record) == row[2], 'CORRUPT_EVENT')
        out.append(dict(id=row[0], **record))
    return out


def append(con, task, ident, kind, data):
    record = dict(kind=kind, data=data)
    previous = con.execute('SELECT digest FROM retrospective_events WHERE task=? AND event_id=?', (task,ident)).fetchone()
    if previous:
        need(previous[0] == pk.digest(record), 'EVENT_CONFLICT')
        return
    con.execute('INSERT INTO retrospective_events(task,event_id,record,digest) VALUES(?,?,?,?)',
                (task,ident,json.dumps(record,sort_keys=True),pk.digest(record)))


def project(history):
    """Pure replay. Stable requirement keys defeat issue-label-only resets."""
    state = dict(version=None, engine=None, gates={}, warnings={}, streaks={},
                 requirements={}, outcomes=[], proofs={}, responses={}, proof_uses=[], proof_bindings={}, sequence=len(history))
    superseded = {e['data']['supersedes'] for e in history if e['kind']=='outcome' and e['data'].get('supersedes')}

    def hold(key, reason, event):
        old = state['gates'].get(key)
        triggers = list(old['triggers']) if old else []
        if event not in triggers: triggers.append(event)
        state['gates'][key] = dict(status='OPEN', reason=reason, triggers=triggers)
        state['responses'].pop(key, None)

    for event in history:
        kind, data, eid = event['kind'], event['data'], event['id']
        if kind == 'initialize':
            state.update(version=data['version'],engine=data['engine'])
        elif kind == 'plan':
            reqs = data['requirements']
            if state['requirements'] and reqs != state['requirements']:
                hold('__requirements__', 'requirement_identity_or_criterion_changed', eid)
            state['requirements'] = reqs
            old_uses={(u.get('task'),u['id']) for u in state['proof_uses']}
            new_uses={(u.get('task'),u['id']) for u in data.get('proof_uses',[])}
            if old_uses-new_uses:
                hold('__dependencies__','proof_dependency_removed_requires_reconciliation',eid)
            state['proof_uses']=data.get('proof_uses',[])
            state['proof_bindings']=data.get('proof_bindings',{})
        elif kind == 'outcome' and eid not in superseded:
            state['outcomes'].append(dict(event=eid, **data))
            for obs in data['observations']:
                key = obs['requirement']
                # An expected negative control is retained, never counted as a
                # failed creative iteration. Contradicted assumptions use flags.
                if (data['role'] == 'negative_control' and
                        not any(obs.get(f) for f in ('falsified','foundation','regressed','dependency_changed','reference_gap'))): continue
                if obs.get('reference_gap'):
                    hold(key, 'reference_inputs_inadequate', eid)
                elif obs.get('falsified') or obs.get('foundation') or obs.get('regressed'):
                    hold(key, 'strategy_falsifier_or_regression', eid)
                elif obs.get('dependency_changed'):
                    hold(key, 'targeted_revalidation', eid)
                elif obs['status'] == 'UNKNOWN':
                    hold(key, 'evidence_reconciliation', eid)
                elif obs['status'] == 'FAIL':
                    if state['gates'].get(key,{}).get('status') == 'TESTING':
                        hold(key, 'intervention_failed', eid)
                    # Native and whole-task reviews of the same attempt count
                    # once for a requirement, not once per rendering/view.
                    attempts = state['streaks'].setdefault(key, [])
                    if data['attempt'] not in attempts: attempts.append(data['attempt'])
                    if len(attempts) >= 2: state['warnings'][key] = len(attempts)
                    if len(attempts) >= 3: hold(key, 'repeated_unresolved_requirement', eid)
                elif obs['status'] == 'PASS':
                    state['streaks'].pop(key,None)
                    state['warnings'].pop(key,None)
                    # A PASS does not silently close an open or TESTING finding.
            if data.get('exhausted'): hold('__allowance__', 'allowance_exhausted', eid)
        elif kind == 'response':
            state['responses'][data['key']] = dict(data, event=eid)
        elif kind == 'admit':
            key = data['key']
            if key not in state['gates'] or pk.digest(state['gates'][key]) != data['gate_digest']:
                hold(key,'corrected_history_invalidates_admission',eid)
                continue
            state['gates'][key].update(status='TESTING',plan=data['plan'],admitted_event=eid)
            state['streaks'].pop(key,None)
            state['warnings'].pop(key,None)
        elif kind == 'evaluate':
            key = data['key']
            if state['gates'].get(key,{}).get('status') != 'TESTING': continue
            if data['result'] == 'effective':
                state['gates'][key].update(status='CLOSED', evaluation=eid)
            else: hold(key, 'intervention_' + data['result'], eid)
        elif kind == 'proof':
            state['proofs'][data['id']] = data
        elif kind == 'dependency':
            hold(data['key'], 'targeted_revalidation', eid)
        elif kind == 'closure':
            state['closure'] = data
    return state


def snapshot(con, task):
    return project(events(con,task))


def fresh(con, state):
    if state['route'] != 'production': return None
    value = snapshot(con,state['task'])
    need(value['version'] == VERSION, 'REVIEWED_MIGRATION_REQUIRED')
    need(value['engine'] == engine(), 'POLICY_CHANGED_RECONCILE')
    return value


def validate_evidence(root, con, state):
    value = fresh(con,state)
    if value is None: return
    for key,gate in value['gates'].items():
        if gate['status']!='TESTING': continue
        reply=value['responses'].get(key)
        need(reply, 'MISSING_RESPONSE')
        for b in reply['evidence'].values(): rc.binding(root,b)
        admission=next(e['data'] for e in events(con,state['task']) if e['id']==gate['admitted_event'])
        for b in admission['challenge']['evidence'].values(): rc.binding(root,b)


def guard(con, state, *, delivery=False):
    value = fresh(con,state)
    if value is None: return
    opened = [k for k,v in value['gates'].items() if v['status']=='OPEN']
    need(not opened, 'REQUIRED:' + ','.join(opened))
    testing = [v for v in value['gates'].values() if v['status']=='TESTING']
    if delivery: need(not testing, 'EFFECT_NOT_EVALUATED')
    for gate in testing:
        need(gate['plan'] == pk.digest(state.get('brief')), 'TEST_PLAN_CHANGED')


def plan(con, state, ident, brief, root=None):
    fresh(con,state)
    proof_bindings={}
    for use in brief.get('retrospective_proof_uses',[]):
        owner=use.get('task',state['task'])
        found=snapshot(con,owner)['proofs'].get(use.get('id'))
        need(found,'UNKNOWN_PROOF')
        proof_bindings[owner+':'+use['id']]=pk.digest(found)
    append(con,state['task'],ident,'plan',dict(requirements={r['id']:r['criterion'] for r in brief['requirements']},
        proof_uses=brief.get('retrospective_proof_uses',[]),proof_bindings=proof_bindings))
    if root is not None:
        from .resource_manifest import validate
        for use in brief.get('retrospective_proof_uses',[]):
            owner = use.get('task',state['task'])
            other = snapshot(con,owner)
            found = other['proofs'].get(use.get('id'))
            need(found, 'UNKNOWN_PROOF')
            rc.binding(root,found['manifest'])
            result = validate(root,pk.read_json(root,found['manifest']['path']),use['conditions'])
            key = '__proof__:'+owner+':'+use['id']
            if not result['reuse_admissible']:
                # Stable event identity merges repeats of an unchanged use.
                append(con,state['task'], 'proof-use:'+pk.digest([key,use,result]), 'dependency',
                       dict(key=key,use=use,manifest=found['manifest'],blockers=result['blockers']))


def outcome(con, state, ident, data):
    fresh(con,state)
    need(data.get('role') in {'production','diagnostic','negative_control','technical'}, 'OUTCOME_ROLE')
    need(isinstance(data.get('attempt'),str) and data['attempt'], 'ATTEMPT_REQUIRED')
    need(isinstance(data.get('observations'),list) and data['observations'], 'OBSERVATIONS_REQUIRED')
    current=snapshot(con,state['task'])
    reqs=set(current['requirements']) | set(current['gates'])
    for item in data['observations']:
        need(item.get('requirement') in reqs or str(item.get('requirement','')).startswith('__'), 'UNKNOWN_REQUIREMENT')
        need(item.get('status') in {'PASS','FAIL','UNKNOWN','NOT_TESTED'}, 'STATUS')
        need(isinstance(item.get('observation'),str) and item['observation'].strip(), 'OBSERVATION')
        for flag in ('falsified','foundation','regressed','dependency_changed','reference_gap'):
            need(flag not in item or type(item[flag]) is bool, 'FLAG')
    if data.get('supersedes'):
        prior = [e for e in events(con,state['task']) if e['id']==data['supersedes'] and e['kind']=='outcome']
        need(len(prior)==1 and prior[0]['data']['attempt']==data['attempt'], 'CORRECTION_IDENTITY')
        need(not any(e['data'].get('supersedes')==data['supersedes'] for e in events(con,state['task'])), 'CORRECTION_CHAIN')
    combined = {}
    order = {'NOT_TESTED':0,'PASS':1,'UNKNOWN':2,'FAIL':3}
    for item in data['observations']:
        key = item['requirement']
        if key not in combined: combined[key] = dict(item)
        else:
            previous = combined[key]
            if order[item['status']] > order[previous['status']]: previous['status']=item['status']
            previous['observation'] += '\n' + item['observation']
            for flag in ('falsified','foundation','regressed','dependency_changed','reference_gap'):
                previous[flag] = previous.get(flag,False) or item.get(flag,False)
    append(con,state['task'],ident,'outcome',dict(data,plan=pk.digest(state.get('brief')),observations=list(combined.values())))


def auto_outcome(con, state, ident, observations, *, origin, evidence=None, extra=None):
    data = dict(attempt=str(state['cycle'])+':'+str(state.get('fingerprint',state.get('planning_step'))),
                role='technical' if origin=='worker' else 'production', origin=origin,
                observations=observations,evidence=evidence or {},
                method=state.get('planning_artifacts',{}).get('STRATEGIZING',{}).get('method_choice'),
                plan=pk.digest(state.get('brief')),
                exhausted=state['stage']=='REPLAN_REQUIRED')
    if extra:
        # Extra semantic judgments supplement rather than replace base checks.
        need(isinstance(extra,list), 'SUPPLEMENT_LIST')
        data['observations'] += extra
    outcome(con,state,ident,data)


def response(root, con, state, ident, key, data):
    from . import reference_readiness as rr
    rr.assessment(root, state.get('brief', {}).get('reference_readiness'), data)
    value = fresh(con,state)
    gate = value['gates'].get(key)
    need(gate and gate['status']=='OPEN', 'NO_OPEN_FINDING')
    if gate['reason']=='reference_inputs_inadequate':
        need(data.get('target_stage')=='GROUNDING' and data.get('reference_assessment',{}).get('diagnosis')=='reference_gap', 'REFERENCE_GAP_REQUIRES_GROUNDING')
    for field in ('cause','uncertainty','change_or_retain_rationale','preserve','test','expected','failure_response'):
        need(isinstance(data.get(field),str) and data[field].strip(), 'RESPONSE_'+field.upper())
    need(data.get('target_stage') in {'GROUNDING','DERIVING','STRATEGIZING'}, 'REPAIR_STAGE')
    need(data.get('plan') == pk.digest(state.get('brief')), 'RESPONSE_PLAN')
    need(data.get('gate_digest') == pk.digest(gate), 'STALE_FINDING')
    need(data.get('evidence'), 'EVIDENCE_REQUIRED')
    for b in data['evidence'].values(): rc.binding(root,b)
    append(con,state['task'],ident,'response',dict(key=key,**data))


def admit(root, con, state, ident, key, data):
    value = fresh(con,state)
    gate, reply = value['gates'].get(key), value['responses'].get(key)
    need(gate and gate['status']=='OPEN' and reply, 'RESPONSE_REQUIRED')
    need(reply['gate_digest']==pk.digest(gate) and reply['plan']==pk.digest(state.get('brief')), 'STALE_RESPONSE')
    need(data.get('response_event')==reply['event'], 'WRONG_RESPONSE')
    from . import reference_readiness as rr
    rr.assessment(root, state.get('brief', {}).get('reference_readiness'), reply)
    for b in reply['evidence'].values(): rc.binding(root,b)
    checks = data.get('checks',{})
    need(set(checks)=={'causal_test','actual_method','preservation','authority'}, 'CHALLENGE_COVERAGE')
    for check in checks.values():
        need(check.get('status')=='PASS' and bool(check.get('observation')), 'CHALLENGE_FAILED')
    need(bool(data.get('counterexample')) and data.get('evidence'), 'CHALLENGE_EVIDENCE')
    for b in data['evidence'].values(): rc.binding(root,b)
    append(con,state['task'],ident,'admit',dict(key=key,plan=reply['plan'],gate_digest=pk.digest(gate),challenge=data))


def evaluate(root, con, state, ident, key, data):
    value = fresh(con,state)
    validate_evidence(root,con,state)
    gate = value['gates'].get(key)
    need(gate and gate['status']=='TESTING', 'TEST_NOT_ADMITTED')
    need(data.get('result') in {'effective','ineffective','inconclusive'}, 'EFFECT_RESULT')
    need(data.get('observation') and data.get('evidence'), 'EFFECT_EVIDENCE')
    for b in data['evidence'].values(): rc.binding(root,b)
    history = events(con,state['task'])
    since = next(i for i,e in enumerate(history) if e['id']==gate['admitted_event'])
    later = [e for e in history[since+1:] if e['kind']=='outcome']
    need(data.get('outcome_event') in {e['id'] for e in later}, 'NO_POST_TEST_OUTCOME')
    observed = next(e['data'] for e in later if e['id']==data['outcome_event'])
    if data['result']=='effective':
        need(not any(e['data'].get('supersedes')==data['outcome_event'] for e in history), 'OUTCOME_SUPERSEDED')
        need(observed['role'] in {'production','diagnostic'} and observed['plan']==gate['plan'], 'WRONG_EFFECT_SCOPE')
        for b in observed.get('evidence',{}).values(): rc.binding(root,b)
        need(any(o['requirement']==key and o['status']=='PASS' for o in observed['observations']), 'NO_MATCHING_PASS')
    append(con,state['task'],ident,'evaluate',dict(key=key,**data))


def proof(root, con, state, ident, data):
    """Reference an existing resource manifest; never create another asset registry."""
    from .resource_manifest import validate
    fresh(con,state)
    need(data.get('id') and data.get('manifest') and data.get('conditions'), 'PROOF_CONTRACT')
    rc.binding(root,data['manifest'])
    record = pk.read_json(root,data['manifest']['path'])
    result = validate(root,record,data['conditions'])
    need(result['reuse_admissible'], 'PROOF_NOT_QUALIFIED')
    need(data.get('requirements') and set(data['requirements']) <= set(snapshot(con,state['task'])['requirements']), 'PROOF_SCOPE')
    append(con,state['task'],ident,'proof',data)


def check_proofs(root, con, state):
    from .resource_manifest import validate
    value = fresh(con,state)
    if value is None: return
    for use in state.get('brief',{}).get('retrospective_proof_uses',[]):
        owner = use.get('task',state['task'])
        other = snapshot(con,owner)
        found = other['proofs'].get(use.get('id'))
        need(found, 'UNKNOWN_PROOF')
        need(value['proof_bindings'].get(owner+':'+use['id'])==pk.digest(found), 'PROOF_VERSION_CHANGED')
        need(other['version']==VERSION and other['engine']==engine(), 'DEPENDENT_POLICY_RECONCILE')
        need(not any(other['gates'].get(r,{}).get('status') in {'OPEN','TESTING'}
                     for r in found['requirements']+['__requirements__','__migration__','__dependencies__']), 'DEPENDENT_PROOF_HELD')
        rc.binding(root,found['manifest'])
        result = validate(root,pk.read_json(root,found['manifest']['path']),use['conditions'])
        if not result['reuse_admissible']:
            key='__proof__:'+owner+':'+use['id']
            gate=value['gates'].get(key,{})
            diagnostic=(use.get('purpose')=='diagnostic' and gate.get('status')=='TESTING'
                        and gate.get('plan')==pk.digest(state.get('brief')))
            # A scoped adaptation test can explore new conditions, not bypass
            # stale input, licensing, open failures or missing artifacts.
            need(diagnostic and all(x.startswith(('UNTESTED_CONDITION:','UNSPECIFIED_CONDITION:')) for x in result['blockers']),
                 'PROOF_REVALIDATION_REQUIRED')


def packet(con, state):
    value = fresh(con,state)
    if value is None: return {}
    # Complete event history remains on disk. No automatic full-history prompt.
    gates={k:(dict(status='CLOSED',evaluation=g['evaluation']) if g['status']=='CLOSED' else g)
           for k,g in value['gates'].items()}
    result=dict(policy=VERSION,sequence=value['sequence'],gates=gates,warnings=value['warnings'],
                responses={k:v for k,v in value['responses'].items() if gates[k]['status']!='CLOSED'},
                proofs=value['proofs'],history_api='retrospective.events(connection, task)',
                instruction='Inspect source-bound outcomes for each open finding; respond, challenge, then test. Admission is not effectiveness. No new authority.')
    if state.get('brief',{}).get('reference_readiness') is not None:
        from . import reference_readiness as rr
        result['reference_contract']=rr.contract()
        result['reference_readiness']=state['brief']['reference_readiness']
    # Lossless deduplication: active findings often share the same intervention.
    # Keep every event/key/gate identity, but carry its common payload once.
    if len(json.dumps(result))>60000:
        pool={};indexed={}
        for key,row in result['responses'].items():
            identity={k:v for k,v in row.items() if k in {'event','key','gate_digest'}}
            body={k:v for k,v in row.items() if k not in identity}
            digest=pk.digest(body);pool[digest]=body
            indexed[key]=dict(identity,payload_ref=digest)
        result.update(response_encoding='shared_payloads_v1',response_payloads=pool,responses=indexed)
        result['instruction']+=' Responses use lossless shared payloads: merge response_payloads[payload_ref] with each indexed event/key/gate_digest; full original records remain in events.'
    need(len(json.dumps(result))<=60000,'PACKET_TOO_LARGE_RECONCILE_SCOPE')
    return result


def expand_packet_responses(value):
    """Read-only lossless decoder for audit/tools; no authority or state change."""
    if value.get('response_encoding')!='shared_payloads_v1':return value['responses']
    pool=value['response_payloads'];out={}
    for key,row in value['responses'].items():
        body=pool[row['payload_ref']]
        need(pk.digest(body)==row['payload_ref'],'RESPONSE_PAYLOAD_CHANGED')
        out[key]=dict(body,**{k:v for k,v in row.items() if k!='payload_ref'})
    return out
