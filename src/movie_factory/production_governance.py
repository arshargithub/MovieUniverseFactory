"""397: canonical effort/proof/retirement events; no dispatch or artistic oracle.

Only the trusted Controller writes these events. Derived state is never accepted
from a model packet. Cached replay is disposable and checked against its ledger.
"""
from copy import deepcopy
import json
from . import production_knowledge as pk
from . import review_control as rc

VERSION = 1
DEFAULTS = {'review_after': 10, 'stop_after': 20, 'context_bytes': 24576}


def need(ok, message):
    if not ok:
        from .production_workflow import Blocked
        raise Blocked('GOV397_' + message)


def install(con):
    con.executescript('''
      CREATE TABLE IF NOT EXISTS governance_events397 (
        seq INTEGER PRIMARY KEY, event_id TEXT UNIQUE NOT NULL,
        kind TEXT NOT NULL, payload TEXT NOT NULL, digest TEXT NOT NULL);
      CREATE TRIGGER IF NOT EXISTS governance397_no_update BEFORE UPDATE ON governance_events397
        BEGIN SELECT RAISE(ABORT,'immutable governance'); END;
      CREATE TRIGGER IF NOT EXISTS governance397_no_delete BEFORE DELETE ON governance_events397
        BEGIN SELECT RAISE(ABORT,'immutable governance'); END;
      CREATE TABLE IF NOT EXISTS governance_cache397 (
        slot INTEGER PRIMARY KEY CHECK(slot=1), seq INTEGER, state TEXT, digest TEXT);
      CREATE TABLE IF NOT EXISTS governance_requests397 (
        event_id TEXT PRIMARY KEY, digest TEXT NOT NULL);
      CREATE TRIGGER IF NOT EXISTS governance_requests397_no_update BEFORE UPDATE ON governance_requests397
        BEGIN SELECT RAISE(ABORT,'immutable governance request'); END;
      CREATE TRIGGER IF NOT EXISTS governance_requests397_no_delete BEFORE DELETE ON governance_requests397
        BEGIN SELECT RAISE(ABORT,'immutable governance request'); END;
    ''')


def empty():
    return dict(version=VERSION, sequence=0, nodes={}, tasks={}, cycles={}, proofs={},
                retirements={}, exceptions={}, reviews={}, effects={}, regressions={})


def replay(history, base=None):
    s = deepcopy(base) if base is not None else empty()
    for e in history:
        need(e['seq'] == s['sequence'] + 1, 'EVENT_SEQUENCE')
        need(pk.digest({'kind': e['kind'], 'data': e['data']}) == e['digest'], 'EVENT_CORRUPT')
        d, k = e['data'], e['kind']
        if k == 'node':
            need(d['id'] not in s['nodes'], 'NODE_EXISTS')
            s['nodes'][d['id']] = d
        elif k == 'migration':
            need(d['task'] not in s['tasks'], 'TASK_ALREADY_MIGRATED')
            s['tasks'][d['task']] = d
        elif k == 'cycle':
            need(d['id'] not in s['cycles'], 'DUPLICATE_CYCLE')
            s['cycles'][d['id']] = dict(d, completed=False, reserved_sequence=e['seq'])
        elif k == 'cycle_result':
            need(d['id'] in s['cycles'], 'UNRESERVED_CYCLE_RESULT')
            s['cycles'][d['id']].update(completed=True, result=d['status'])
        elif k == 'proof':
            need(d['id'] not in s['proofs'], 'DUPLICATE_PROOF')
            s['proofs'][d['id']] = dict(d, valid=True, qualified_sequence=e['seq'])
        elif k == 'invalidate':
            need(d['proof'] in s['proofs'], 'UNKNOWN_PROOF')
            s['proofs'][d['proof']]['valid'] = False
        elif k == 'regression':
            s['regressions'][d['task']+':'+d['feature']]=d['cycle']
            s.setdefault('regression_sequence',{})[d['task']+':'+d['feature']]=e['seq']
        elif k == 'retire':
            s['retirements'][d['node']] = d
        elif k == 'exception':
            need(d['id'] not in s['exceptions'], 'EXCEPTION_REUSED')
            s['exceptions'][d['id']] = d
        elif k == 'scope_review':
            s['reviews'][d['task']] = d
        elif k == 'rebind':
            s['tasks'][d['task']]['node'] = d['node']
        elif k == 'node_limit':
            s['nodes'][d['node']]['limit'] = d['limit']
        elif k == 'task_allocation':
            s['tasks'][d['task']]['remaining_allocation'] = d['allocation']
        elif k == 'milestone':
            s['nodes'][d['node']]['completion_proofs'] = d['proofs']
        elif k == 'effect':
            # A per-finding record cannot count the same experiment several times.
            key = d['experiment'] + ':' + d['feature'] + ':' + d['requirement']
            prior = s['effects'].get(key)
            need(prior is None or prior == d, 'CONFLICTING_EFFECT')
            s['effects'][key] = d
        else:
            need(False, 'UNKNOWN_EVENT')
        s['sequence'] = e['seq']
    return s


def history(con, after=0):
    return [dict(seq=r[0], kind=r[1], data=json.loads(r[2]), digest=r[3]) for r in con.execute(
        'SELECT seq,kind,payload,digest FROM governance_events397 WHERE seq>? ORDER BY seq', (after,))]


def snapshot(con, *, full=False):
    if full:
        return replay(history(con))
    row = con.execute('SELECT seq,state,digest FROM governance_cache397 WHERE slot=1').fetchone()
    if row:
        s = json.loads(row[1])
        need(s['sequence'] == row[0] and pk.digest(s) == row[2], 'CACHE_CORRUPT_FULL_REPLAY_REQUIRED')
        end = con.execute('SELECT COALESCE(MAX(seq),0) FROM governance_events397').fetchone()[0]
        need(row[0] <= end, 'CACHE_AHEAD_OF_LEDGER')
    else:
        s = empty()
    return replay(history(con, s['sequence']), s)


def append(con, ident, kind, data):
    need(isinstance(ident, str) and ident.strip(), 'EVENT_ID')
    digest = pk.digest({'kind': kind, 'data': data})
    old = con.execute('SELECT digest FROM governance_events397 WHERE event_id=?', (ident,)).fetchone()
    if old:
        need(old[0] == digest, 'EVENT_ID_CONFLICT')
        return snapshot(con)
    s = snapshot(con)
    cur = con.execute('INSERT INTO governance_events397(event_id,kind,payload,digest) VALUES(?,?,?,?)',
                      (ident, kind, json.dumps(data, sort_keys=True), digest))
    s = replay([dict(seq=cur.lastrowid, kind=kind, data=data, digest=digest)], s)
    con.execute('INSERT OR REPLACE INTO governance_cache397 VALUES(1,?,?,?)',
                (s['sequence'], json.dumps(s, sort_keys=True), pk.digest(s)))
    return s


def descendants(s, node):
    result = {node}
    while True:
        nxt = result | {k for k, v in s['nodes'].items() if v.get('parent') in result}
        if nxt == result:
            return result
        result = nxt


def ancestors(s, node):
    out = []
    while node is not None:
        need(node in s['nodes'] and node not in out, 'NODE_LINEAGE')
        out.append(node)
        node = s['nodes'][node].get('parent')
    return out


def integer(value, minimum=0):
    return type(value) is int and value >= minimum


def define_node(root, con, ident, data):
    rc.binding(root, data['authority'])
    s = snapshot(con)
    need(isinstance(data.get('id'), str) and data['id'], 'NODE_ID')
    need(data.get('kind') in {'release', 'milestone', 'capability', 'family'}, 'NODE_KIND')
    need(data.get('limit') is None or integer(data['limit']), 'NODE_LIMIT')
    need(data.get('limit') is not None or data['kind'] == 'release', 'FINITE_CHILD_ALLOCATION')
    need(isinstance(data.get('purpose'), str) and data['purpose'].strip(), 'NODE_PURPOSE')
    if 'weight' in data:
        import math
        need(type(data['weight']) in {int, float} and math.isfinite(data['weight']) and data['weight'] >= 0, 'NODE_WEIGHT')
    if data.get('parent') is not None:
        need(data['parent'] in s['nodes'], 'MISSING_PARENT')
        parent = s['nodes'][data['parent']]
        need(parent['kind'] == {'milestone':'release','capability':'milestone','family':'capability'}.get(data['kind']), 'NODE_HIERARCHY')
        need(parent['limit'] is not None, 'PARENT_ENVELOPE_UNSET')
        assigned = sum(n['limit'] for n in s['nodes'].values() if n.get('parent') == data['parent'])
        need(assigned + data['limit'] <= parent['limit'], 'PARENT_OVERALLOCATED')
        if data['kind'] == 'milestone' and 'weight' in parent:
            assigned_weight = sum(n.get('weight',0) for n in s['nodes'].values() if n.get('parent') == data['parent'])
            need(assigned_weight + data.get('weight',0) <= parent['weight'], 'PARENT_WEIGHT_OVERALLOCATED')
    else:
        need(data['kind'] == 'release', 'ROOT_KIND')
    return append(con, ident, 'node', data)


def migrate(root, con, state, ident, data):
    rc.binding(root, data['authority'])
    need(not con.execute('SELECT 1 FROM heavy_job').fetchone(), 'ACTIVE_JOB')
    need(data.get('state_digest') == pk.digest(state), 'MIGRATION_STALE')
    need(data.get('task') == state['task'], 'MIGRATION_TASK')
    need(data.get('baseline_slots') == state['cycle'], 'BASELINE_COUNTER')
    need(data.get('original_limit') == state['max_corrections'], 'BASELINE_LIMIT')
    need(isinstance(data.get('features'), list) and data['features'] and
         len(set(data['features'])) == len(data['features']), 'FEATURE_IDENTITY')
    need(set(data.get('historical_age', {})) == set(data['features']) and
         all(integer(n) for n in data['historical_age'].values()), 'HISTORY_COVERAGE')
    need(isinstance(data.get('history_evidence'), dict) and data['history_evidence'], 'HISTORY_EVIDENCE')
    for b in data['history_evidence'].values(): rc.binding(root, b)
    need(isinstance(data.get('unknowns'), list), 'UNKNOWN_CAPTURE')
    profile=data.get('profile',{})
    need(set(profile)==set(DEFAULTS) and all(integer(v,1) for v in profile.values()) and
         profile['review_after']<profile['stop_after'], 'INVALID_PROFILE')
    if profile!=DEFAULTS:
        rc.binding(root,data['profile_authority'])
        approved=pk.read_json(root,data['profile_authority']['path'])
        need(approved.get('decision')=='approve_governance_profile' and
             approved.get('task')==state['task'] and approved.get('profile')==profile,'UNAPPROVED_PROFILE')
        rc.binding(root,approved['human_source'])
    s = snapshot(con)
    node = data.get('node')
    need(node in s['nodes'], 'MIGRATION_NODE')
    capability=next(n for n in ancestors(s,node) if s['nodes'][n]['kind']=='capability')
    siblings=[t for t in s['tasks'].values() if capability in ancestors(s,t['node'])]
    need(not siblings or set(data['features'])==set(siblings[0]['features']), 'CAPABILITY_FEATURE_IDENTITY_CHANGED')
    need(integer(data.get('remaining_allocation')), 'FINITE_TASK_ALLOCATION')
    need(data['remaining_allocation'] <= max(0, state['max_corrections'] - state['cycle']),
         'MIGRATION_CANNOT_GRANT_CYCLES')
    assigned=sum(t['remaining_allocation'] for t in s['tasks'].values() if t['node']==node)
    need(assigned+data['remaining_allocation']<=s['nodes'][node]['limit'],'TASK_ALLOCATION_OVER_FAMILY')
    need(data.get('lane','production') in {'production','engineering','workflow_admin'},'TASK_LANE')
    data = dict(data, lane=data.get('lane','production'),baseline_cycle=state['cycle'], baseline_stage=state['stage'])
    return append(con, ident, 'migration', data)


def task_progress(s, task):
    need(task in s['tasks'], 'MIGRATION_REQUIRED')
    t = s['tasks'][task]
    cycles = [v for v in s['cycles'].values() if v['task'] == task]
    capability=next(n for n in ancestors(s,t['node']) if s['nodes'][n]['kind']=='capability')
    peers={k:v for k,v in s['tasks'].items() if capability in ancestors(s,v['node'])}
    lineage_cycles=[v for v in s['cycles'].values() if v['task'] in peers]
    ages = {f:max(x['historical_age'].get(f,0) for x in peers.values()) for f in t['features']}
    proof_stamps={}
    for f in t['features']:
        cutoff=max(s.get('regression_sequence',{}).get(k+':'+f,-1) for k in peers)
        valid = [v for v in s['proofs'].values() if v['task'] in peers and
                 v['feature'] == f and v['valid'] and
                 v['qualified_sequence']>cutoff]
        if valid:
            # IDs carry task-local cycle counters; ledger order supplies global time.
            latest=max(valid,key=lambda v:v['qualified_sequence']);proof_stamps[f]=latest['id']
            ages[f] = sum(c['completed'] and f in c['features'] and c['reserved_sequence']>
                          latest['qualified_sequence'] for c in lineage_cycles)
        else:
            proof_stamps[f]='historical-baseline'
            ages[f] += sum(c['completed'] and f in c['features'] for c in lineage_cycles)
    effects = [e for e in s['effects'].values() if e['task'] in peers and e['result'] != 'effective']
    failures = {f: len({e['experiment'] for e in effects if e['feature'] == f}) for f in t['features']}
    r = s['reviews'].get(task)
    if r:
        failures = {f: max(0, n - r['effect_counts'].get(f, 0)) for f, n in failures.items()}
    line = ancestors(s, t['node'])
    used = {}
    for n in line:
        below = descendants(s, n)
        used[n] = sum(1 for c in s['cycles'].values() if c['node'] in below)
    due=[f for f,n in ages.items() if n>=t['profile']['review_after'] and
         (not r or r.get('proof_stamps',{}).get(f)!=proof_stamps[f] or
          r.get('reviewed_ages',{}).get(f,-1)<(n//t['profile']['review_after'])*t['profile']['review_after'])]
    decision=('STOP_AND_REALLOCATE' if any(n in s['retirements'] for n in line) or any(
        n>=t['profile']['stop_after'] for n in ages.values()) else
        'REASSESS' if due or any(n>=2 for n in failures.values()) else
        'ALLOCATION_EXHAUSTED' if len(cycles)>=t['remaining_allocation'] else 'CONTINUE_WITHIN_AUTHORITY')
    return dict(task=task, decision=decision,spent=len(cycles), historical_slots=t['baseline_slots'],
                remaining=max(0, t['remaining_allocation'] - len(cycles)), feature_age=ages,
                ineffective_interventions=failures, lineage=line, ancestor_spent=used,
                retirement=[n for n in line if n in s['retirements']],
                warnings=[f for f, n in ages.items() if n >= t['profile']['review_after']],
                blocked_features=[f for f, n in ages.items() if n >= t['profile']['stop_after']],
                proof_stamps=proof_stamps,investment_review_required=due,
                scope_review_required=any(n >= 2 for n in failures.values()))


def guard(con, state, *, operation='construction', allow_existing=False, recipe_digest=None, root=None):
    s = snapshot(con)
    if state['task'] not in s['tasks']:
        need(state.get('mode') != 'local_native', 'MIGRATION_REQUIRED')
        return None  # Explicit offline/frozen historical compatibility; no native authority.
    p = task_progress(s, state['task'])
    if root is not None:
        t=s['tasks'][state['task']]
        rc.binding(root,t['authority'])
        for b in t['history_evidence'].values():rc.binding(root,b)
        for n in p['lineage']:rc.binding(root,s['nodes'][n]['authority'])
    key = state['task'] + ':' + str(state['cycle'])
    if operation == 'review' and key in s['cycles']:
        return p  # Finish existing evidence at the ceiling; never reserve new work.
    exceptions = [x for x in s['exceptions'].values() if x['task'] == state['task'] and
                  x['node'] in p['lineage'] and p['spent'] - x['start_spent'] -
                  int(key in s['cycles'] and not s['cycles'][key]['completed']) < x['limit'] and
                  operation in x['operations'] and (recipe_digest is None or recipe_digest in x['recipes'])]
    exception = exceptions[-1] if exceptions else None
    need(not p['retirement'] or exception, 'RETIRED_FOR_PRODUCTION')
    need(not p['blocked_features'] or exception, 'NO_PROGRESS_STOP_RECOMMEND_REALLOCATION')
    if operation == 'construction':
        need(not p['investment_review_required'] or exception, 'INVESTMENT_REVIEW_REQUIRED')
        if state.get('brief', {}).get('production_contract397'):
            contract = state['brief']['production_contract397']
            need(contract['family'] == s['tasks'][state['task']]['node'] and
                 contract['capability'] in p['lineage'], 'BRIEF_LINEAGE_CHANGED')
            need({f for v in contract['feature_map'].values() for f in v} == set(s['tasks'][state['task']]['features']),
                 'FEATURE_SCOPE_CHANGED')
        need(not p['scope_review_required'], 'SCOPE_REASSESSMENT_REQUIRED')
        if not (allow_existing and key in s['cycles']):
            need(p['remaining'] > 0, 'TASK_ALLOCATION_EXHAUSTED')
            for n, used in p['ancestor_spent'].items():
                limit = s['nodes'][n]['limit']
                need(limit is not None and used < limit, 'ANCESTOR_ALLOCATION_EXHAUSTED')
    return p


def authorize_exception(root, con, state, ident, data):
    rc.binding(root, data['authority']); approval = pk.read_json(root, data['authority']['path'])
    need(approval.get('decision') == 'approve_governance_exception' and approval.get('task') == state['task']
         and approval.get('assignment') == data['assignment'], 'EXCEPTION_EXACT_APPROVAL')
    rc.binding(root, approval['human_source'])
    a = data['assignment']; s = snapshot(con); p = task_progress(s, state['task'])
    need(a.get('node') in p['lineage'] and integer(a.get('limit'), 1), 'EXCEPTION_SCOPE')
    need(a['limit'] <= p['remaining'] and a.get('acknowledges_retirement') is True, 'EXCEPTION_NO_NEW_ALLOWANCE')
    need(a.get('operations') and set(a['operations']) <= {'construction', 'native_transport',
         'apply_existing_graft', 'key_pose_render', 'motion_preview', 'review'}, 'EXCEPTION_OPERATIONS')
    need(a.get('recipes') and all(isinstance(v, str) and len(v) == 64 for v in a['recipes']), 'EXCEPTION_RECIPE_SCOPE')
    need(a.get('new_variants') is False and a.get('renew_automatically') is False, 'EXCEPTION_NOT_BROAD_RESTART')
    return append(con, ident, 'exception', dict(id=ident, task=state['task'], start_spent=p['spent'],
                  authority=data['authority'], **a))


def rebind(root, con, state, ident, data):
    rc.binding(root, data['authority']); s = snapshot(con); old = s['tasks'][state['task']]['node']
    need(data.get('task') == state['task'] and data.get('node') in s['nodes'], 'REBIND_SCOPE')
    old_cap = next(n for n in ancestors(s, old) if s['nodes'][n]['kind'] == 'capability')
    need(old_cap in ancestors(s, data['node']), 'REBIND_CANNOT_CHANGE_CAPABILITY')
    return append(con, ident, 'rebind', data)


def amend_limit(root, con, ident, data):
    rc.binding(root, data['authority']); approval = pk.read_json(root, data['authority']['path'])
    s = snapshot(con); n = s['nodes'].get(data.get('node'))
    need(n is not None and integer(data.get('limit')), 'LIMIT_SCOPE')
    need(approval.get('decision') == 'approve_governance_allocation' and approval.get('node') == data['node']
         and approval.get('old_limit') == n['limit'] and approval.get('new_limit') == data['limit'], 'LIMIT_EXACT_APPROVAL')
    rc.binding(root, approval['human_source'])
    assigned = sum(x['limit'] for x in s['nodes'].values() if x.get('parent') == data['node'])
    need(data['limit'] >= assigned, 'LIMIT_BELOW_CHILD_RESERVATIONS')
    spent = sum(c['node'] in descendants(s,data['node']) for c in s['cycles'].values())
    need(data['limit'] >= spent, 'LIMIT_CANNOT_REFUND_SPENT_CYCLES')
    if n.get('parent'):
        siblings = sum(x['limit'] for x in s['nodes'].values() if x.get('parent') == n['parent'] and x['id'] != data['node'])
        need(s['nodes'][n['parent']]['limit'] is not None and siblings + data['limit'] <= s['nodes'][n['parent']]['limit'], 'PARENT_OVERALLOCATED')
    return append(con, ident, 'node_limit', data)


def amend_task_allocation(root, con, state, ident, data):
    """Reconcile a separate legitimate cycle grant; never clears failure history."""
    rc.binding(root,data['authority']); approval=pk.read_json(root,data['authority']['path'])
    s=snapshot(con); t=s['tasks'][state['task']]; p=task_progress(s,state['task'])
    need(data.get('task')==state['task'] and integer(data.get('allocation')), 'TASK_ALLOCATION_SCOPE')
    need(approval.get('decision')=='approve_task_allocation' and approval.get('task')==state['task']
         and approval.get('old_allocation')==t['remaining_allocation']
         and approval.get('new_allocation')==data['allocation'], 'TASK_ALLOCATION_EXACT_APPROVAL')
    rc.binding(root,approval['human_source'])
    need(data['allocation']>=p['spent'], 'TASK_ALLOCATION_NO_REFUND')
    need(data['allocation']-p['spent']<=max(0,state['max_corrections']-state['cycle']), 'TASK_ALLOCATION_NO_NEW_ALLOWANCE')
    siblings=sum(x['remaining_allocation'] for k,x in s['tasks'].items() if k!=state['task'] and x['node']==t['node'])
    need(siblings+data['allocation']<=s['nodes'][t['node']]['limit'], 'TASK_ALLOCATION_OVER_FAMILY')
    return append(con,ident,'task_allocation',data)


def milestone(root, con, ident, data):
    s = snapshot(con); n = s['nodes'].get(data.get('node'))
    need(n is not None and n['kind'] == 'milestone', 'MILESTONE_SCOPE')
    need(data.get('proofs') and all(p in s['proofs'] and s['proofs'][p]['valid'] for p in data['proofs']), 'MILESTONE_PROOFS')
    features = {s['proofs'][p]['feature'] for p in data['proofs']}
    need(set(n.get('required_features', [])) and set(n['required_features']) <= features, 'MILESTONE_FEATURE_COVERAGE')
    need(all(n['id'] in ancestors(s, s['tasks'][s['proofs'][p]['task']]['node']) for p in data['proofs']), 'MILESTONE_PROOF_LINEAGE')
    rc.binding(root, data['authority'])
    return append(con, ident, 'milestone', data)


def release_progress(s):
    def retained(ident):
        p=s['proofs'][ident];t=s['tasks'][p['task']]
        cap=next(n for n in ancestors(s,t['node']) if s['nodes'][n]['kind']=='capability')
        peers=[k for k,v in s['tasks'].items() if cap in ancestors(s,v['node'])]
        cutoff=max(s.get('regression_sequence',{}).get(k+':'+p['feature'],-1) for k in peers)
        return p['valid'] and p['qualified_sequence']>cutoff
    earned = 0.0
    roots = [n for n in s['nodes'].values() if n['kind']=='release']
    total = sum(n['weight'] for n in roots) if roots and all('weight' in n for n in roots) else None
    for n in s['nodes'].values():
        if n['kind'] != 'milestone': continue
        weight = n.get('weight', 0.0)
        proofs = n.get('completion_proofs', [])
        if proofs and all(retained(p) for p in proofs): earned += weight
    return dict(earned=earned, total_weight=total, fraction=earned/total if total else None,
                note='Qualified milestone scope only; not cycle consumption or the Director394scenario.')


def economics(s, *, baseline_cycles=None, total_envelope=None):
    """Canonical prospective investment plus explicitly conditional394 scenario.

    Unknown historical whole-projectC remains unknown; original task baselines
    are reported separately and never summed as a complete project census.
    """
    need(baseline_cycles is None or integer(baseline_cycles,1),'ECONOMIC_BASELINE')
    need(total_envelope is None or integer(total_envelope,1),'ECONOMIC_ENVELOPE')
    counts={lane:0 for lane in ('production','engineering','workflow_admin')}
    for cycle in s['cycles'].values():counts[s['tasks'][cycle['task']].get('lane','production')]+=1
    total=sum(counts.values())
    milestones={}
    for ident,node in s['nodes'].items():
        if node['kind']!='milestone':continue
        used=sum(c['node'] in descendants(s,ident) for c in s['cycles'].values())
        milestones[ident]=dict(spent=used,envelope=node['limit'],burn=used/node['limit'] if node['limit'] else None)
    scenario=dict(label='Director394illustration only;not measured readiness',scope=12,earned=1.5,
        fraction=.125,remaining=10.5,remaining_to_completed=7,baseline_cycles=baseline_cycles,
        same_productivity_remaining=7*baseline_cycles if baseline_cycles is not None else None,
        same_productivity_total=8*baseline_cycles if baseline_cycles is not None else None,
        total_envelope=total_envelope,required_improvement=None)
    if baseline_cycles is not None and total_envelope is not None:
        need(total_envelope>baseline_cycles,'ECONOMIC_ENVELOPE_NOT_ABOVE_SUNK')
        scenario['required_improvement']=7*baseline_cycles/(total_envelope-baseline_cycles)
    return dict(prospective_reserved_cycles=total,by_lane=counts,
        admin_share=counts['workflow_admin']/total if total else None,milestones=milestones,
        historical_baselines={k:t['baseline_slots'] for k,t in s['tasks'].items()},
        qualified_release=release_progress(s),scenario=scenario,
        limits='No uniform whole-project census or forecast; no finished-footage credit forR&D/admin.')


def reserve(con, state, root=None):
    p = guard(con, state, allow_existing=True,root=root)
    if p is None: return
    s = snapshot(con); t = s['tasks'][state['task']]
    key = state['task'] + ':' + str(state['cycle'])
    if key in s['cycles']: return
    need(state['cycle'] <= state['max_corrections'], 'ORIGINAL_ALLOWANCE_EXHAUSTED')
    append(con, 'cycle:' + key, 'cycle', dict(id=key, task=state['task'], node=t['node'],
        cycle=state['cycle'], features=t['features'], profile=t['profile'],
        lane=t.get('lane','production'),phase=state.get('planning_step') or state['stage']))


def finish_cycle(con, state, status, ident):
    s = snapshot(con); key = state['task'] + ':' + str(state['cycle'])
    if key not in s['cycles'] or s['cycles'][key]['completed']: return
    need(status in {'PASS', 'FAIL', 'UNKNOWN', 'TECHNICAL_FAILURE'}, 'CYCLE_RESULT')
    append(con, ident, 'cycle_result', dict(id=key, status=status))


def capture_outcomes(con,state,observations,ident):
    s=snapshot(con)
    if state['task'] not in s['tasks']:return
    mapping=state.get('brief',{}).get('production_contract397',{}).get('feature_map',{})
    failed={f for o in observations if o['status']=='FAIL' for f in mapping.get(o['requirement'],[])}
    for f in failed:
        append(con,ident+':'+f,'regression',dict(task=state['task'],feature=f,cycle=state['cycle']))


def scope_review(root, con, state, ident, data):
    from .production_contracts import scope_contract
    s = snapshot(con); p = task_progress(s, state['task'])
    need(data.get('task') == state['task'], 'SCOPE_TASK')
    need(data.get('decision') in {'split', 'keep', 'merge', 'change_method', 'retire'}, 'SCOPE_DECISION')
    scope_contract(root, data['diagnostic'])
    need(data.get('effect_counts') == {f: n + (s['reviews'].get(state['task'], {}).get('effect_counts', {}).get(f, 0))
                                     for f, n in p['ineffective_interventions'].items()}, 'SCOPE_COUNTS_NOT_CANONICAL')
    need(data.get('next_operation') == data['diagnostic']['first_operation'], 'SCOPE_NO_EXECUTABLE_CHANGE')
    need(isinstance(data.get('next_operation_binding'),dict) and
         data['next_operation_binding'].get('id') == data['next_operation'], 'SCOPE_OPERATION_BINDING')
    result=append(con, ident, 'scope_review', dict(data,reviewed_ages=p['feature_age'],proof_stamps=p['proof_stamps']))
    if data['decision']=='retire':
        t=s['tasks'][state['task']]
        result=append(con,ident+':retire','retire',dict(node=t['node'],reason=data['diagnostic']['failure_next'],authority=t['authority']))
    return result


def validate_plan(con, state, brief, root=None):
    s=snapshot(con)
    if state['task'] not in s['tasks']: return
    d=brief.get('production_contract397');need(d is not None,'STAGE_CONTRACT_REQUIRED')
    t=s['tasks'][state['task']]
    need(d['family']==t['node'] and d['capability'] in ancestors(s,t['node']), 'BRIEF_LINEAGE_CHANGED')
    need({f for fs in d['feature_map'].values() for f in fs}==set(t['features']), 'FEATURE_SCOPE_CHANGED')
    review=s['reviews'].get(state['task'])
    if review:
        need(review['next_operation_binding']==d['operations'][0], 'SCOPE_DECISION_NOT_APPLIED')
        need(review['diagnostic']==d['scope'], 'SCOPE_DIAGNOSIS_NOT_APPLIED')
    for p in d.get('input_proofs',[]):
        need(p.get('id') in s['proofs'], 'UNKNOWN_INPUT_PROOF')
        proof=s['proofs'][p['id']]
        need(proof['valid'] and proof['conditions']==p.get('conditions') and
             proof['conditions'].get('proof_kind')==p.get('kind'), 'INPUT_PROOF_STALE_OR_UNQUALIFIED')
        need(root is not None,'INPUT_PROOF_ROOT_REQUIRED')
        for b in proof['evidence'].values():rc.binding(root,b)


def capture_effect(con, state, ident, data):
    s = snapshot(con)
    if state['task'] not in s['tasks']: return
    contract = state.get('brief', {}).get('production_contract397', {})
    feature_map = contract.get('feature_map', {})
    for f in feature_map.get(data['key'], []):
        need(f in s['tasks'][state['task']]['features'], 'UNKNOWN_FEATURE')
        # Evaluation already verified against exact same-plan outcomes by retro.
        e = data['evaluation']
        row = con.execute('SELECT record FROM retrospective_events WHERE task=? AND event_id=?',
                          (state['task'], e['outcome_event'])).fetchone()
        need(row is not None, 'EFFECT_OUTCOME_REQUIRED')
        experiment = json.loads(row[0])['data']['attempt']
        append(con, ident + ':' + f, 'effect', dict(task=state['task'], feature=f,
               experiment=experiment, requirement=data['key'], result=e['result'], evidence=e['evidence']))


def retire(root, con, ident, data):
    rc.binding(root, data['authority'])
    s = snapshot(con)
    need(data.get('node') in s['nodes'] and isinstance(data.get('reason'), str) and data['reason'], 'RETIREMENT_SCOPE')
    return append(con, ident, 'retire', data)


def record_proof(root, con, state, ident, proof):
    """Only called after typed criterion/native review; not an arbitrary PASS API."""
    s = snapshot(con)
    need(state['task'] in s['tasks'], 'MIGRATION_REQUIRED')
    need(proof['feature'] in s['tasks'][state['task']]['features'], 'UNKNOWN_FEATURE')
    need(proof['task'] == state['task'] and proof['cycle'] == state['cycle'], 'PROOF_VERSION')
    need(proof.get('validated_contract') == pk.digest(state['brief']['production_contract397']), 'PROOF_CONTRACT')
    need(proof.get('evidence') and proof.get('conditions'), 'PROOF_EVIDENCE')
    for b in proof['evidence'].values(): rc.binding(root, b)
    return append(con, ident, 'proof', proof)
