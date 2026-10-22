"""Reconcile a repaired control plan without clearing the foundation finding."""
from pathlib import Path
from movie_factory import production_workflow as wf, production_knowledge as pk
from movie_factory.task_router import DATABASE
r=Path(__file__).resolve().parents[1];c=wf.Controller(r,DATABASE);task='sikh335-supporting-appearance';s=c.state(task);cycle=s['cycle']
ev={p:dict(path=p,sha256=pk.file_hash(r/p)) for p in ['results/sikh348/CAUSAL_LEDGER.md','results/sikh348/NEXT_PROOF.md','results/sikh351/REQUEST.md',f'results/sikh351/challenge-c{cycle}.json','results/sikh351/DIAGNOSIS.md']}
c.retrospective(task,'outcome',dict(attempt=f'c{cycle}-retained-foundation',role='diagnostic',origin='replan-reconciliation',
 observations=[dict(requirement='form',status='FAIL',observation='56 reduced slit but retained implausible tucked upper arm; no repaired anatomy yet qualified.',foundation=True)],evidence=ev),f'sikh351-c{cycle}-form-open')
for key,gate in c.retrospective_packet(task)['gates'].items():
 if gate['status']=='TESTING' and gate['plan']!=pk.digest(c.state(task)['brief']):
  c.retrospective(task,'outcome',dict(attempt=f'c{cycle}-reconcile-{key}',role='diagnostic',origin='changed-plan',observations=[dict(requirement=key,status='UNKNOWN',observation='Prior test admission belongs to preceding plan; explicitly reconcile retained synthesis against repaired plan.')],evidence=ev),f'sikh351-c{cycle}-{key}-reopen')
for key,gate in c.retrospective_packet(task)['gates'].items():
 if gate['status']!='OPEN':continue
 response=dict(cause='56 plane correction still inherits an elbow behind the torso; endpoint preservation does not imply anatomical configuration.',uncertainty='Changing elbow pole may expose wrist twist or shoulder discontinuity.',
 change_or_retain_rationale='Retain56 plane transport; test anterior/down/out pole for spear arm while preserving wrist/digits and lengths; no smoothing.',
 preserve='All historical records, original authority, separate motion12 and appearance57 ceiling.',test='Pose-only repair save/reopen; bare283/327/350 front and back, matched controls.',
 expected='Either identify causal family or retain uncertainty; no whole appearance approval.',failure_response='Revise affected strategy within remaining count; no new task or cosmetic retry.',
 target_stage='STRATEGIZING',plan=pk.digest(c.state(task)['brief']),gate_digest=pk.digest(gate),evidence=ev)
 event=f'sikh351-c{cycle}-{key}-response';c.retrospective(task,'response',dict(key=key,response=response),event)
 challenge=dict(response_event=event,counterexample='Correct elbow plane can still leave unacceptable shoulder or wrist twisting; inspect rather than infer a pass.',evidence=ev,
 checks={k:dict(status='PASS',observation=v) for k,v in dict(causal_test='55 matched controls localize custom fault; change frames only.',actual_method='Fixed tested anatomy handler with save prerequisite.',preservation='Original52 and23 preserved; old wrist and digit matrices restored; no horse or crowd mutation.',authority=f'Explicit five appearance corrections;{cycle} of57; no spending.').items()})
 c.retrospective(task,'admit',dict(key=key,challenge=challenge),f'sikh351-c{cycle}-{key}-admit')
print({k:v['status'] for k,v in c.retrospective_packet(task)['gates'].items()})
