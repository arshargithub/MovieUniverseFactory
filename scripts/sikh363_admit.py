"""Transport an authored challenge and its scoped internal retro test response."""
import json,sys
from pathlib import Path
from movie_factory import production_workflow as wf,production_knowledge as pk
from movie_factory.task_router import DATABASE
r=Path(__file__).resolve().parents[1];c=wf.Controller(r,DATABASE);label=sys.argv[1];task='sikh335-'+('supporting-appearance' if label=='appearance' else 'continuous-performance');s=c.state(task);tag=f'{label}-c{s["cycle"]}'
def bind(p):return dict(path=p,sha256=pk.file_hash(r/p))
cfg=pk.read_json(r,f'results/sikh363/{tag}.json');path=f'results/sikh363/{tag}-challenge.json';v=pk.read_json(r,path)
meta=r/f'results/sikh363/{tag}-retro.json'
if meta.exists():cfg={**cfg,**json.loads(meta.read_text())}
if s['stage']=='BRIEFING':
 p=c.packet(task);v['input_digest']=p['planning_input_digest'];c.submit(task,p['actor'],p['ticket'],v,'sikh363-'+tag+'-admission');s=c.state(task)
assert s['stage']=='EXECUTING'
ev={p:bind(p) for p in ['results/sikh363/REQUEST.md',f'results/sikh363/{tag}.json',path]+cfg.get('retro_evidence',[])}
for key,g in c.retrospective_packet(task)['gates'].items():
 if g['status']=='TESTING' and g['plan']!=pk.digest(s['brief']):
  c.retrospective(task,'outcome',dict(attempt='363-'+tag+'-'+key,role='diagnostic',origin='revised-source-proof',observations=[dict(requirement=key,status='UNKNOWN',observation='Changed method/conditions require current-plan proof; prior failures and useful evidence retained.')],evidence=ev),'sikh363-'+tag+'-'+key+'-reopen')
for key,g in c.retrospective_packet(task)['gates'].items():
 if g['status']!='OPEN':continue
 response=dict(cause=cfg['retro_cause'],uncertainty=v['strongest_counterexample'],change_or_retain_rationale=cfg['method'],preserve='Original tasks, history, limits, accepted masters and current scope; source/frame/AV distinct.',test=cfg['proof'],expected=cfg['retro_expected'],failure_response=cfg['failure'],target_stage='GROUNDING',plan=pk.digest(s['brief']),gate_digest=pk.digest(g),evidence=ev)
 event='sikh363-'+tag+'-'+key+'-response';c.retrospective(task,'response',dict(key=key,response=response),event)
 ch=dict(response_event=event,counterexample=v['strongest_counterexample'],evidence=ev,checks={k:dict(status='PASS',observation=t) for k,t in dict(causal_test=response['test'],actual_method=response['change_or_retain_rationale'],preservation=response['preserve'],authority='Current original task cycle/cap preserved; no new external or model authority.').items()});c.retrospective(task,'admit',dict(key=key,challenge=ch),event+'-admit')
print(s['task'],s['cycle'],s['max_corrections'],'admitted test, not art approval')
