"""Bounded closeout accounting; categories and worker elapsed are not art success."""
import collections,json,re
from pathlib import Path
r=Path(__file__).resolve().parents[1];o=r/'results/sikh386';rows=[]
for n in range(177,227):
 x=json.loads((o/f'CYCLE{n}_CLOSEOUT.json').read_text());assert x['cycle']==n;rows.append(x)
counts=collections.Counter(x.get('disposition',x.get('category','unclassified')) for x in rows);jobs=[];missing=[]
for d in sorted((r/'.runtime/factory-native').glob('sikh386-appearance-c*')):
 m=re.match(r'sikh386-appearance-c(\d+)-',d.name)
 if not m or not 177<=int(m[1])<=226 or not (d/'job.json').exists():continue
 j=json.loads((d/'job.json').read_text());p=d/'runner-status.json'
 if not p.exists():missing.append(str(d.relative_to(r)));continue
 s=json.loads(p.read_text());jobs.append(dict(id=d.name,cycle=int(m[1]),operation=j.get('recipe',{}).get('operation',j.get('mode')),elapsed_seconds=s.get('elapsed'),exit_code=s.get('exit_code'),ok=s.get('ok')))
actual=sum(x.get('art_candidates',x.get('artistic_candidates',0)) for x in rows);elapsed=sum(x['elapsed_seconds'] for x in jobs if x['elapsed_seconds'] is not None);render=sum(x['elapsed_seconds'] for x in jobs if x['elapsed_seconds'] is not None and x['operation'] in ['nihang_render','nihang_frames'])
x=dict(shared_slots=50,range=[177,226],artistic_candidates_closeout_classification=actual,other_slots=50-actual,dispositions=dict(counts),native_jobs_with_runner_receipt=len(jobs),native_jobs_missing_runner_receipt=missing,recorded_runner_elapsed_sum_seconds=elapsed,render_operation_runner_sum_seconds=render,runner_failures=sum(x['ok'] is False or x['exit_code'] not in [0,None] for x in jobs),limits=['Candidate classification is recorded per correction, not rendered image count or artistic success rate.','Runner elapsed includes process/load/inspection/save/render and excludes planning/code/client work; it is not pure kernel render time, CPU core-seconds or full campaign net work.','Do not add overlapping operating-ledger work/job intervals; Director idle is reconciled separately.','No token/model-usage efficiency is inferred.'],jobs=jobs)
(o/'CLOSEOUT_METRICS226.json').write_text(json.dumps(x,indent=2)+'\n');print(json.dumps({k:v for k,v in x.items() if k!='jobs'},indent=2))
