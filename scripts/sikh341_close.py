"""Retain actual neutral proof, reject it and stop at the approved ceiling."""
import json
from pathlib import Path
from movie_factory import production_workflow as wf,production_knowledge as pk
from movie_factory.task_router import DATABASE
from movie_factory.experiment_ledger import Ledger
r=Path(__file__).resolve().parents[1];out=r/'results/sikh335/look01'
c=wf.Controller(r,DATABASE);task='sikh335-supporting-appearance';s=c.state(task)
assert s['cycle']==19 and s['max_corrections']==19
runs=[]
for cycle,steps in ((18,('save','neutral_front')),(19,('save','neutral_front','neutral_back','neutral_side'))):
 for step in steps:
  p=out/f'{step}-run-c{cycle}.json';run=json.loads(p.read_text());base=r/'.runtime/factory-native'/run['id']
  row=dict(cycle=cycle,step=step,run=run['id'],status=run['status'],error=run.get('error'),evidence={})
  for name in ('scene.blend','frame.png','snapshot.json','dependencies.json','patch-evidence.json','neutral-proof.npz','stdout.log','stderr.log'):
   f=base/name
   if f.is_file():row['evidence'][name]={'path':str(f.relative_to(r)),'sha256':pk.file_hash(f),'bytes':f.stat().st_size}
  if step!='save':
   saved=r/'.runtime/factory-native'/f'sikh341-look-c{cycle}-save'
   a=json.loads((saved/'snapshot.json').read_text());b=json.loads((base/'snapshot.json').read_text())
   da=json.loads((saved/'dependencies.json').read_text())['bindings'];db=json.loads((base/'dependencies.json').read_text())['bindings']
   row['selected_state_identical']=a==b
   row['dependencies_removed_on_reopen']=sorted(set(da)-set(db))
   row['dependencies_added_on_reopen']=sorted(set(db)-set(da))
  runs.append(row)
if s['stage']!='REPLAN_REQUIRED':
 d=s['direction'];c.reground(task,d['context_sources'],d['knowledge_task'],d['knowledge_digest'],
  'Both341 corrections used. Actual neutral body/garment now exists and torso drape improved, but neckline remains visibly serrated/intersecting. Reopen source matrices repaired19; orphan appended donor library disappears from dependency inventory. Three neutral views inspected. Bend deliberately NOT_RUN; no visual or production pass. Stop further construction at19.',
  'sikh341-c19-exhausted')
s=c.state(task);motion=c.state('sikh335-continuous-performance')
events=Ledger(r/'.runtime/experiment-ops.sqlite3').events();jobs=[]
for e in events:
 if e['event_id'].startswith('sikh341-') and e['event_id'].endswith('-start') and e['event_type']=='job_started':
  end=next((f for f in events if f['event_id']==e['event_id'][:-6]+'-end'),None)
  if end:jobs.append({'job':e['event_id'][:-6],'process_wall_seconds':end['monotonic_seconds']-e['monotonic_seconds']})
report={'task':task,'state':{k:s[k] for k in ('stage','cycle','max_corrections')},
 'motion_state':{k:motion[k] for k in ('stage','cycle','max_corrections')},'runs':runs,'jobs':jobs,
 'new_saved_candidates':2,'new_rendered_diagnostic_images':4,'native_process_wall_seconds':sum(x['process_wall_seconds'] for x in jobs),
 'visual_verdict':'FAIL','bend':'NOT_RUN','direct_motion':'NOT_RUN','director_acceptance':'NOT_REQUESTED',
 'observations':{'neutral18_front':'Molded pectoral/abdominal read and jagged collar. Rejected.',
  'neutral19_front':'Fabric bridges chest with hanging folds; molded pectoral read substantially reduced. Neckline still saw-toothed and unacceptable.',
  'neutral19_back':'Continuous shoulder/armpit region and restrained back folds; no detached rectangular shoulder panels. Waist and cuffs still unfinished.',
  'neutral19_side':'Continuous sleeve/shoulder; chest projects as draped fabric rather than bare anatomy. Front neckline irregularity is visible again.',
  'technical':'19 selected snapshots match exactly in all three fresh processes; all fail strict dependency inventory because an appended unused donor library is dropped. Original failure receipts retained.'},
 'scope':'Actual neutral garment method proof only. No Nihang face, crown, saddle, crowd, faithful performance or integrated sequence completion.',
 'new_provider_calls':0,'new_external_spend':0,'remote_push':False,'new_remote_backup':False}
(out/'exhaustion-c19.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:report[k] for k in ('state','motion_state','native_process_wall_seconds','new_saved_candidates','new_rendered_diagnostic_images')}))
