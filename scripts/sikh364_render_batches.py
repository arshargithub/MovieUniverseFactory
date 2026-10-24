"""Serial fixed admitted42 batch transport; no direct Blender or art review."""
import json,subprocess,sys,time
from pathlib import Path
from movie_factory import production_workflow as wf
from movie_factory.native_admission import Bridge
from movie_factory.task_router import DATABASE
r=Path(__file__).resolve().parents[1];py=str(r/'.venv/bin/python');c=wf.Controller(r,DATABASE);task='sikh335-continuous-performance';s=c.state(task)
assert s['cycle']==42 and s['stage']=='EXECUTING'
steps=s['planning_artifacts']['STRATEGIZING']['steps'];batch=[x['id'] for x in steps if x['id'].startswith('frames')]
assert batch==['frames'+str(i).zfill(2) for i in range(1,17)]
for step in batch:
 s=c.state(task);assert s['cycle']==42 and s['stage']=='EXECUTING';c._fresh(s)
 old=Bridge(c).runs(s).get(step)
 if old:
  if old['status']!='RETURNED':raise RuntimeError('UNRESOLVED_OR_FAILED_BATCH:'+step)
  # Explicit receipt reuse only; actual qualified output will be reviewed later.
  wf.bindings(r,old['artifacts']);print('RETAIN EXISTING',step,flush=True);continue
 print('BEGIN',step,flush=True);start=time.monotonic()
 args=[py,'-m','movie_factory.experiment_ops','job','--experiment','sikh335','--episode','leader363','--phase','rendering','--id','sikh364-m42-'+step,'--kind','native','--',py,'scripts/sikh363_plan.py','motion',step]
 result=subprocess.run(args,cwd=r,check=False)
 print('END',step,'exit',result.returncode,'seconds',round(time.monotonic()-start,2),flush=True)
 if result.returncode:sys.exit(result.returncode)
print('ALL16 ADMITTED BATCHES RETURNED; IMAGE/ENCODED/AV REVIEW NOT IMPLIED',flush=True)
