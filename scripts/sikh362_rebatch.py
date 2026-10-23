"""Record interrupted25 and replan original task26, not a retry/reset."""
import json
from pathlib import Path
from movie_factory import production_workflow as wf,production_knowledge as pk
from movie_factory.task_router import DATABASE
r=Path(__file__).resolve().parents[1];c=wf.Controller(r,DATABASE);task='sikh335-continuous-performance'
runpath='results/sikh362/motion-c25-frames01-run.json';run=pk.read_json(r,runpath);assert run['status']=='FAILED'
ev={'run':dict(path=runpath,sha256=pk.file_hash(r/runpath))}
c.retrospective(task,'outcome',dict(attempt='362-motion25-render',role='diagnostic',origin='operator-stopped-resource-forecast',observations=[dict(requirement='evidence',status='FAIL',observation='Measured38.5/40.5sec first frames predicts16-frame batch beyond600sec cap. Verified task-owned PID644 terminated withSIGTERM; bridge recordsFAILED, no completed run or AV claim. Preserve partial images/logs, do not use them as finished media.',foundation=False)],evidence=ev),'sikh362-motion25-resource-outcome')
state=c.replan(task,'STRATEGIZING','Retain image quality, source/native and all original authority; reduce chunks from15+canonical to8+canonical based on measured render cost. No lowered visual gate or lost history.','sikh362-motion25-rebatch')
assert state['cycle']==26 and state['max_corrections']==31
cfg=pk.read_json(r,'results/sikh362/motion-c25.json');cfg['cause']+='25 interrupted before anticipated worker timeout; batch forecast was wrong for higher-detail profile. No artistic candidate failed.'
save=cfg['steps'][0];steps=[save]
frames=list(range(252,377))
for i,start in enumerate(range(0,len(frames),8),1):
    chosen=frames[start:start+8]
    if 283 not in chosen:chosen=chosen+[283]
    steps.append(dict(id=f'frames{i:02d}',depends_on=['save'],recipe=dict(operation='nihang_frames',frame=283,frames=chosen,view='production',width=432,height=768,samples=16)))
cfg['steps']=steps
cfg['method']+=' Batch at most8 consecutive frames plus canonical283 (at most9 total); no automatic completion of an oversized job.'
p=r/'results/sikh362/motion-c26.json';p.write_text(json.dumps(cfg,indent=2)+'\n');print(state['cycle'],len(steps)-1)
