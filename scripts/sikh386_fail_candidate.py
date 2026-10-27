"""Submit explicitly authored failed image review/effect; no automated art verdict."""
import json,sys
from pathlib import Path
from movie_factory import production_workflow as wf,production_knowledge as pk
from movie_factory.native_admission import Bridge
r=Path(__file__).resolve().parents[1];c=wf.Controller(r,'.runtime/factory-entry.sqlite3');task='sikh335-supporting-appearance';s=c.state(task);cy=s['cycle'];f=sys.argv[1];x=pk.read_json(r,f);assert x['cycle']==cy
bind=lambda p:dict(path=p,sha256=pk.file_hash(r/p));ev={f:bind(f)}
for step in x['steps']:
 run=pk.read_json(r,f'results/sikh386/appearance-c{cy}-{step}-run.json');v=dict(verdict='FAIL',run_digest=pk.digest(run),observation=x['observation'],comparison=x['comparison'],open_defects=x['defects'],evidence=run['artifacts'],cycle_disposition=dict(category='art_rejected',observation=x['observation']))
 Bridge(c).record_review(task,step,v);p=f'results/sikh386/appearance-c{cy}-{step}-review.json';(r/p).write_text(json.dumps(v,indent=2)+'\n');ev[p]=bind(p)
packet=c.retrospective_packet(task);pending=packet['pending_effects386'];keys=set(v['key'] for v in pending.values());oid=f'sikh386-c{cy}-actual-rejection'
c.retrospective(task,'outcome',dict(attempt=oid,role='production',origin='actual_candidate_internal_rejection',observations=[dict(requirement=k,status='UNKNOWN' if k=='director_form_motion' else 'FAIL',observation=x['observation']+' Known visible failure; temporal judgment not attempted.') for k in keys],evidence=ev),oid)
for aid,v in pending.items():
 c.retrospective(task,'evaluate',dict(key=v['key'],evaluation=dict(admission_event=aid,result='inconclusive' if v['key']=='director_form_motion' else 'ineffective',outcome_event=oid,observation=x['conclusion'],evidence=ev)),aid+'-actual-effect')
close=dict(x,cycle=cy,max=s['max_corrections'],disposition='art_rejected',art_candidates=1,not_run=x['not_run'])
(r/f'results/sikh386/CYCLE{cy}_CLOSEOUT.json').write_text(json.dumps(close,indent=2)+'\n');print('Rejected',cy,'; shared remaining',s['max_corrections']-cy)
