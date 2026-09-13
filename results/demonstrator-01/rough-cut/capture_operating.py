"""Compact prospective accounting for this authorized pass only."""
from pathlib import Path
import datetime,json,sqlite3,time,shutil
ROOT=Path(__file__).resolve().parents[3];R=ROOT/'results/demonstrator-01/rough-cut';a=json.loads((R/'authorization.json').read_text())
c=sqlite3.connect(ROOT/'.runtime/experiment-ops.sqlite3');allrows=[json.loads(row[0]) for row in c.execute('select payload from events order by seq')]
rows=[e for e in allrows if e.get('event_id','').startswith('demo01-cut') or e.get('activity_id')=='demo01-cut'];starts={};jobs=[]
for e in rows:
 if e['event_type']=='job_started':starts[e['job_id']]=e
 elif e['event_type']=='job_completed':
  start=starts.pop(e['job_id'],None);seconds=None
  if start and start.get('clock_id')==e.get('clock_id'):seconds=e['monotonic_seconds']-start['monotonic_seconds']
  jobs.append({'id':e['job_id'],'kind':e.get('job_kind'),'outcome':e.get('outcome'),'seconds':seconds,'start_utc':start.get('utc') if start else None,'end_utc':e['utc']})
native=sum(j['seconds'] for j in jobs if j['kind']=='native' and j['seconds'] is not None)
summary={'captured_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'authorization_to_capture_monotonic_seconds':time.monotonic()-a['monotonic_start'],'native_completed_process_seconds':native,'native_compute_limit_seconds':a['native_limit_seconds'],'engineering_envelope_seconds':a['engineering_limit_seconds'],'pure_active_engineering_seconds':None,'subscription_token_usage':None,'director_review_seconds':None,'open_jobs':list(starts),'native_completed_jobs':sum(j['kind']=='native' for j in jobs),'failed_native_jobs':[j['id'] for j in jobs if j['kind']=='native' and j['outcome']!='PASSED'],'jobs':jobs,'storage_free_gib':shutil.disk_usage(ROOT).free/1024**3,'timing_definition':'Native same-process monotonic durations are process-seconds, not CPU core time. Authorization-to-capture includes overlapping rendering and supervision and conservatively bounds active engineering; do not add them together.'}
(R/'operating-events.json').write_text(json.dumps(rows,indent=2)+'\n');(R/'operating-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps({k:v for k,v in summary.items() if k!='jobs'}))
