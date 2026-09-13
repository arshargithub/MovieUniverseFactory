"""Bounded local batch driver. Run only after preflight and full-cycle inspection."""
import concurrent.futures,json,os,shutil,sqlite3,subprocess,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
PYTHON=ROOT/'.venv/bin/python'
OUT=ROOT/'runs/demonstrator-01'
AUTH=json.loads((ROOT/'results/demonstrator-01/rough-cut/authorization.json').read_text())

def native_seconds():
 c=sqlite3.connect(ROOT/'.runtime/experiment-ops.sqlite3');rows=[json.loads(r[0]) for r in c.execute('select payload from events')];starts={};total=0
 for e in rows:
  if not (e.get('job_id','').startswith('demo01-cut') and e.get('job_kind')=='native'):continue
  if e['event_type']=='job_started':starts[e['job_id']]=e
  elif e['event_type']=='job_completed' and e['job_id'] in starts:
   total+=max(0,e['monotonic_seconds']-starts.pop(e['job_id'])['monotonic_seconds'])
 total+=sum(max(0,time.monotonic()-e['monotonic_seconds']) for e in starts.values())
 return total

def run_block(row):
 shot,start,end=row
 if time.monotonic()-AUTH['monotonic_start']>AUTH['engineering_limit_seconds']:raise RuntimeError('Active envelope exhausted')
 if native_seconds()+2*900>AUTH['native_limit_seconds']:raise RuntimeError('Native budget reserve insufficient')
 if shutil.disk_usage(ROOT).free<5.15*1024**3:raise RuntimeError('Storage reserve insufficient')
 name=f'cut-frames-{shot}-{start:04d}-{end:04d}-serial';folder=OUT/name
 if folder.exists():raise RuntimeError(f'Existing output must be reconciled: {name}')
 job={'mode':'demo_cut_render','output_dir':str(folder),'profile':{'shot':shot,'start':start,'end':end}}
 code='from movie_factory.adapters.blender.runner import run_blender;import sys;r=run_blender('+repr(job)+',blender_bin="/Applications/Blender.app/Contents/MacOS/Blender",timeout=900);print(r);sys.exit(0 if r.get("ok") else 1)'
 command=[str(PYTHON),'-m','movie_factory.experiment_ops','job','--experiment','DEMONSTRATOR-01','--episode','stage-a','--phase','rough-cut-render','--kind','native','--id',f'demo01-cut-{shot}-{start}-{end}-serial','--',str(PYTHON),'-c',code]
 result=subprocess.run(command,cwd=ROOT,capture_output=True,text=True)
 (ROOT/'results/demonstrator-01/rough-cut'/f'{name}.log').write_text(result.stdout+result.stderr)
 print(json.dumps({'shot':shot,'start':start,'end':end,'returncode':result.returncode,'free_gib':round(shutil.disk_usage(ROOT).free/1024**3,3)}),flush=True)
 if result.returncode:raise RuntimeError(f'Native block failed: {name}')
 return folder

if __name__=='__main__':
 # The two extreme frames have already been rendered from this scene and are reused.
 blocks=[]
 for shot,start,end in [('shot1',0,143),('shot2',144,312),('shot3',312,432),('shot4',432,575)]:
  for a in range(start,end,48):blocks.append((shot,a,min(a+48,end)))
 # One native worker after measured swap growth; submit only after successful completion.
 with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
  for i in range(0,len(blocks),1):
   futures=[pool.submit(run_block,b) for b in blocks[i:i+1]]
   for future in futures:future.result()
