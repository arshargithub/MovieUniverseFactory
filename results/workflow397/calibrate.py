"""Read-only historical shadow calibration; never grants native authority."""
import json,sqlite3,time
from pathlib import Path
from movie_factory import retrospective as rt,production_knowledge as pk
root=Path.cwd(); report={}
with sqlite3.connect('file:.runtime/factory-entry.sqlite3?mode=ro',uri=True) as source:
 for task in ['sikh335-supporting-appearance','sikh335-continuous-performance']:
  h=rt.events(source,task);t=time.perf_counter();full=rt.project(h);full_ms=(time.perf_counter()-t)*1000
  # Exercise tail replay over every event in deterministic chunks, including supersession fallback.
  acc=None;all_seen=[];t=time.perf_counter()
  for i in range(0,len(h),25):
   tail=h[i:i+25];all_seen+=tail
   acc=rt.project(all_seen) if any(e['kind']=='outcome' and e['data'].get('supersedes') for e in tail) else rt.project(tail,acc)
  incremental_ms=(time.perf_counter()-t)*1000
  assert acc==full
  c=sqlite3.connect(':memory:');rt.install(c)
  c.executemany('INSERT INTO retrospective_events(task,event_id,record,digest) VALUES(?,?,?,?)',[(task,e['id'],json.dumps({k:e[k] for k in ['kind','data']}),pk.digest({k:e[k] for k in ['kind','data']})) for e in h])
  last=c.execute('SELECT max(seq) FROM retrospective_events').fetchone()[0]
  c.execute('INSERT INTO retrospective_cache397 VALUES(?,?,?,?,?)',(task,last,rt.engine(),json.dumps(full),pk.digest(full)))
  t=time.perf_counter();cached=rt.snapshot(c,task);cached_ms=(time.perf_counter()-t)*1000;assert cached==full
  report[task]=dict(events=len(h),full_digest=pk.digest(full),incremental_equal=True,cached_equal=True,full_ms=full_ms,chunked_total_ms=incremental_ms,cached_ms=cached_ms,scope='Local Python replay only; not end-to-end or token savings.')
Path('results/workflow397/HISTORICAL_CALIBRATION.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
