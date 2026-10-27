"""Record an explicitly authored intervention; never evaluates visual results."""
import json,sys
from pathlib import Path
from movie_factory import production_workflow as wf,production_knowledge as pk,retrospective as rt
r=Path(__file__).resolve().parents[1];task='sikh335-supporting-appearance';c=wf.Controller(r,'.runtime/factory-entry.sqlite3');s=c.state(task);cy=s['cycle'];f=sys.argv[1];v=pk.read_json(r,f);assert v['cycle']==cy
bind=lambda p:dict(path=p,sha256=pk.file_hash(r/p))
ev={p:bind(p) for p in [f]+v['evidence_paths']};packet=c.retrospective_packet(task);assert not packet['pending_effects386'],packet['pending_effects386']
common=dict(reference_assessment=dict(readiness_digest=pk.digest(s['brief']['reference_readiness']),diagnosis=v['diagnosis'],disposition='retain',reason=v['reference_reason'],aspects=list(s['brief']['reference_readiness']['decisions']),evidence=list(ev.values())),cause=v['cause'],uncertainty=v['uncertainty'],change_or_retain_rationale=v['rationale'],preserve=v['preserve'],test=v['test'],expected=v['expected'],failure_response=v['failure_response'],target_stage='STRATEGIZING',plan=pk.digest(s['brief']),evidence=ev,scope_assessment=dict(decision=v['scope_decision'],unit_digest=pk.digest(s['brief']['work_unit']),reason=v['scope_reason']),causal_assessment=dict(category=v['category'],method_family=v['method_family'],changed_prediction=v['prediction'],previous_result=v['previous_result']))
for key in v['keys']:
 gate=rt.expand_packet_gates(c.retrospective_packet(task))[key]
 if gate['status']=='TESTING':
  oid=f'sikh386-c{cy}-{key}-prior-plan-unknown';c.retrospective(task,'outcome',dict(attempt=oid,role='diagnostic',origin='changed_test_plan',observations=[dict(requirement=key,status='UNKNOWN',observation='Previous plan outcome does not qualify current experiment; retain original findings.')],evidence=ev),oid)
  gate=rt.expand_packet_gates(c.retrospective_packet(task))[key]
 assert gate['status']=='OPEN',(key,gate['status'])
 event=f'sikh386-c{cy}-{key}-intervention'
 c.retrospective(task,'response',dict(key=key,response=dict(common,gate_digest=pk.digest(gate))),event)
 challenge=dict(response_event=event,counterexample=v['counterexample'],evidence=ev,checks={k:dict(status='PASS',observation=t) for k,t in dict(causal_test=v['test'],actual_method=v['method'],preservation=v['preserve'],authority=f'Original task and current{cy}/226, no new resources or model/spend.').items()})
 c.retrospective(task,'admit',dict(key=key,challenge=challenge),event+'-admit')
c.packet(task);print('Explicit intervention admitted for',cy)
