"""Read-only, source-scoped production economics. Unknown is not zero.

Enrolled governance cycles and observed operating cycles remain disjoint from
routed operations, native jobs and Director inputs. This module grants nothing.
"""
from collections import Counter
import json
import math
from . import production_governance as g
from . import review_control as rc
from .experiment_ledger import effective_events


def retained_features(s):
    result=set()
    for task,t in s['tasks'].items():
        cap=next(n for n in g.ancestors(s,t['node']) if s['nodes'][n]['kind']=='capability')
        result.update((cap,f) for f,p in g.task_progress(s,task)['proof_stamps'].items()
                      if p!='historical-baseline')
    return result


def rolling(history, *, window=10):
    g.need(g.integer(window,1) and window<=1000,'SCORECARD_WINDOW_BOUND')
    s=g.replay(history);cycles=sorted(s['cycles'].values(),key=lambda c:c['reserved_sequence'])
    if not cycles:return dict(charged_cycles=0,completed_results=0,pending=0,
                              retained_feature_delta=None,retained_production_yield=None,
                              reason='No prospective enrolled cycles; historical baselines are separate.')
    chosen=cycles[-window:];first=chosen[0]['reserved_sequence']
    before=g.replay([e for e in history if e['seq']<first])
    a,b=retained_features(before),retained_features(s)
    pa,pb=g.release_progress(before),g.release_progress(s)
    comparable=(pa['total_weight'] is not None and pa['total_weight']==pb['total_weight'] and
                {k:n.get('weight') for k,n in before['nodes'].items() if n['kind']=='milestone'}==
                {k:n.get('weight') for k,n in s['nodes'].items() if n['kind']=='milestone'})
    delta=pb['earned']-pa['earned'] if comparable else None
    return dict(charged_cycles=len(chosen),cycle_ids=[c['id'] for c in chosen],
                completed_results=sum(c['completed'] for c in chosen),pending=sum(not c['completed'] for c in chosen),
                retained_feature_gains=[list(x) for x in sorted(b-a)],retained_feature_losses=[list(x) for x in sorted(a-b)],
                retained_feature_delta=len(b-a)-len(a-b),qualified_milestone_weight_delta=delta,
                retained_production_yield=delta/len(chosen) if delta is not None else None,
                reason='Ledger-sequence window; no footage credit for failed experiments or proof counts. Unconfigured/reweighted milestone scope gives null yield.')


def operating_observations(events, enrolled, *, root=None):
    cycles={};conflicts=[];unverified=[];escapes=set();handovers=set();outputs=set();attributed=set()
    observations=[];coverage=[]
    for e in effective_events(events):
        if e.get('event_type')!='proxy_observed':continue
        name=e.get('name')
        if name not in {'plan_execute_review_cycle','director_escape','director_handover','usable_output','measurement_coverage'}:continue
        if root is not None:
            try:
                b=e.get('evidence_binding')
                if not isinstance(b,dict) or b.get('path')!=e.get('evidence_ref'):raise ValueError('unbound observation')
                rc.binding(root,b)
            except (ValueError,OSError,KeyError):
                unverified.append(e['event_id']);continue
        if name=='measurement_coverage':
            if root is not None: coverage.append(e)
            continue
        if name=='plan_execute_review_cycle':
            ident=e.get('work_cycle_id');lane=e.get('lane');status=e.get('cycle_status')
            if not ident or lane not in {'production','engineering','workflow_admin'} or status not in {'reserved','completed','failed'} or type(e.get('count')) is not int or e['count']!=1 or not e.get('evidence_ref'):
                conflicts.append(e['event_id']);continue
            if ident in enrolled:
                attributed.add(ident);continue  # One cycle, not another admin charge.
            prior=cycles.get(ident)
            if prior and (prior['lane']!=lane or (prior['status']!='reserved' and status!=prior['status'])):
                conflicts.append(ident);continue
            cycles[ident]=dict(lane=lane,status=status,experiment=e['experiment_id'])
        elif name in {'director_escape','director_handover','usable_output'}:
            ident=e.get('item_id')
            if type(e.get('count')) is not int or e['count']!=1 or not ident or not e.get('evidence_ref'):
                conflicts.append(e['event_id']);continue
            {'director_escape':escapes,'director_handover':handovers,'usable_output':outputs}[name].add(ident)
            observations.append((name,ident,e.get('work_cycle_id')))
    by_lane={lane:sum(c['lane']==lane for c in cycles.values()) for lane in ('production','engineering','workflow_admin')}
    rates=None
    if coverage:
        e=coverage[-1]
        try:
            p=rc.path(root,e['evidence_binding']['path'])
            g.need(p.suffix=='.json' and p.stat().st_size<=1024*1024,'COVERAGE_BOUND')
            d=json.loads(p.read_text());ids=d.get('cycle_ids',[])
            g.need(type(d.get('schema')) is int and d['schema']==1 and d.get('purpose')=='measurement_coverage', 'COVERAGE_SCHEMA')
            g.need(ids and len(ids)==len(set(ids)) and set(ids)<=enrolled|set(cycles),'COVERAGE_CYCLE_SCOPE')
            required={'director_escape','director_handover','usable_output'}
            g.need(required<=set(d.get('complete_fields',[])),'COVERAGE_INCOMPLETE')
            counts={k:len({ident for name,ident,cycle in observations if name==k and cycle in ids}) for k in required}
            cost=d.get('provider_cost_usd');seconds=d.get('net_seconds')
            for value in (cost,seconds):g.need(value is None or type(value) in {int,float} and math.isfinite(value) and value>=0,'COVERAGE_RESOURCE_VALUE')
            g.need(seconds is None or d.get('net_time_excludes_director_idle') is True,'COVERAGE_NET_IDLE')
            outputs_count=counts['usable_output']
            rates=dict(cycle_ids=ids,coverage_binding=e['evidence_binding'],observation_counts=counts,
                escape_rate=counts['director_escape']/len(ids),handover_rate=counts['director_handover']/len(ids),
                reported_provider_cost_usd=cost,net_seconds=seconds,
                cost_per_usable_output=cost/outputs_count if cost is not None and outputs_count else None,
                net_seconds_per_usable_output=seconds/outputs_count if seconds is not None and outputs_count else None,
                limits='Rates apply only to this source-bound declared-complete capture scope, not all production. Coverage and classifications still need truthful human/agent audit.')
        except (ValueError,OSError,KeyError,TypeError):
            conflicts.append(e['event_id'])
    return dict(observed_additional_cycles=len(cycles),by_lane=by_lane,
                completed_cycles=sum(c['status']=='completed' for c in cycles.values()),
                failed_cycles=sum(c['status']=='failed' for c in cycles.values()),
                pending_cycles=sum(c['status']=='reserved' for c in cycles.values()),
                duplicate_enrolled_cycles_not_recharged=sorted(attributed),
                known_director_escapes=len(escapes),known_director_handovers=len(handovers),
                known_usable_output_observations=len(outputs),
                escape_rate=rates['escape_rate'] if rates else None,
                handover_rate=rates['handover_rate'] if rates else None,
                cost_per_usable_output=rates['cost_per_usable_output'] if rates else None,
                scoped_rates=rates,
                coverage='Source-scoped observations only; missing observations/usage/census are unknown, not proof of zero events or cost.',
                conflicts=conflicts,unverified_observations=unverified,
                provenance='Bound source hashes checked' if root is not None else 'Declared synthetic/test observations; no source verification')


def build(con, *, operating_events=(), window=10, root=None):
    history=g.history(con);s=g.snapshot(con)
    econ=g.economics(s);ops=operating_observations(operating_events,set(s['cycles']),root=root)
    counts=Counter()
    # Read actual routed requests, not assumptions about conversation turns.
    for (raw,) in con.execute('SELECT decision FROM routing'):
        route=json.loads(raw)
        if not route['id'].startswith('legacy-simulation:'):counts[route['route']]+=1
    observed_total=econ['prospective_reserved_cycles']+ops['observed_additional_cycles']
    observed_admin=econ['by_lane']['workflow_admin']+ops['by_lane']['workflow_admin']
    configuration=dict(release_weights_configured=econ['qualified_release']['total_weight'] is not None,
        historical_project_cycle_baseline_configured=False,
        original_task_baselines=econ['historical_baselines'],
        allocation_state='FINITE_REMAINING' if any(g.task_progress(s,t)['remaining']>0 for t in s['tasks']) else 'NO_NEW_TASK_ALLOWANCE',
        forecasts_available=False)
    return dict(schema=1,economics=econ,configuration=configuration,
                rolling=rolling(history,window=window),operating=ops,
                observed_combined_cycles=observed_total,
                observed_admin_share=observed_admin/observed_total if observed_total and not ops['conflicts'] and not ops['unverified_observations'] else None,
                routed_operation_inventory=dict(sorted(counts.items())),
                coverage='Enrolled canonical cycles plus explicitly identified operating-cycle observations. Routed operations are not cycles. Not a uniform historical/all-work census.',
                outcome='Trailer plus episodes1and2; artistic/readiness gates remain separate.',
                authority_granted=False)
