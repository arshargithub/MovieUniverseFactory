"""Run one admitted trusted outer-Python numeric proof; never launches Blender.

Per-step exact data inputs replace the old filename-inferred source metadata.
"""
import json,subprocess,time
from pathlib import Path
from movie_factory import production_workflow as w,production_knowledge as p
from movie_factory.review_control import binding


def verify_inputs(root,step,brief):
 script=step.get('numeric_script');inputs=step.get('numeric_inputs')
 if not isinstance(script,dict) or not isinstance(inputs,list) or not inputs:raise ValueError('NUMERIC386_EXPLICIT_INPUTS_REQUIRED')
 for item in [script]+inputs:
  if item not in brief['source_bindings'].values():raise ValueError('NUMERIC386_UNBOUND_INPUT')
  binding(root,item)
 if not script['path'].startswith('scripts/anatomy386_') or not script['path'].endswith('.py'):raise ValueError('NUMERIC386_UNTRUSTED_SCRIPT')
 if any(not item['path'].endswith('.npz') for item in inputs):raise ValueError('NUMERIC386_INERT_ARRAY_INPUTS_ONLY')
 return script,inputs


def main():
 r=Path(__file__).resolve().parents[1];c=w.Controller(r,'.runtime/factory-entry.sqlite3');task='sikh335-supporting-appearance';s=c.state(task);cy=s['cycle'];assert s['stage']=='EXECUTING'
 step=next(x for x in s['planning_artifacts']['STRATEGIZING']['steps'] if x['id']=='numeric_graft');script,inputs=verify_inputs(r,step,s['brief']);out=r/f'results/sikh390/numeric{cy}-run.json';assert not out.exists()
 job=f'sikh390-c{cy}-numeric-proof';c.job(task,job,'acquire',job+'-acquire');start=time.time();code=None
 try:
  env={'PATH':'/usr/bin:/bin:/usr/sbin:/sbin','LANG':'en_US.UTF-8','TMPDIR':'/private/tmp','PYTHONNOUSERSITE':'1','OMP_NUM_THREADS':'2','OPENBLAS_NUM_THREADS':'2','VECLIB_MAXIMUM_THREADS':'2'}
  with (r/f'results/sikh390/numeric{cy}.log').open('w') as log:code=subprocess.run([str(r/'.venv/bin/python'),str(r/script['path'])],cwd=r,env=env,stdout=log,stderr=subprocess.STDOUT).returncode
  verify_inputs(r,step,s['brief'])
 finally:
  out.write_text(json.dumps(dict(script=script,actual_declared_data_inputs=inputs,started=start,ended=time.time(),returncode=code,scope='Bound outerPython numeric proof only; no native mutation or artisticapproval.'),indent=2)+'\n');c.job(task,job,'release',job+'-release')
 print('Numeric returncode',code)
 if code is not None and code!=0:raise SystemExit(code)

if __name__=='__main__':main()
