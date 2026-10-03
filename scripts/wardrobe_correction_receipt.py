"""Compact exchange171 operating receipt; no invented usage or lifetime cost."""
from datetime import datetime
import hashlib
import json
from pathlib import Path
import sqlite3

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'.runtime/art-direction/series01-facebuilder-trial-01'
OUT=BASE/'wardrobe171-operating'

def main():
 con=sqlite3.connect(f'file:{ROOT/".runtime/experiment-ops.sqlite3"}?mode=ro',uri=True)
 events=[json.loads(p) for (p,) in con.execute('SELECT payload FROM events ORDER BY seq') if json.loads(p)['event_id'].startswith('wardrobe171-')];con.close()
 starts={e['job_id']:e for e in events if e['event_type']=='job_started'};ends={e['job_id']:e for e in events if e['event_type']=='job_completed'}
 assert starts.keys()==ends.keys(),'Every dispatched job must be reconciled'
 jobs=[{'id':n,'kind':s['job_kind'],'outcome':ends[n]['outcome'],'seconds':ends[n]['monotonic_seconds']-s['monotonic_seconds']} for n,s in starts.items()]
 start=next(e for e in events if e['event_id']=='wardrobe171-work-start');end=next(e for e in events if e['event_id']=='wardrobe171-work-end')
 seconds=(datetime.fromisoformat(end['utc'])-datetime.fromisoformat(start['utc'])).total_seconds()
 review=json.loads((OUT/'visual-review.json').read_text());assert review['known_structural_blockers']==[]
 manifest=[]
 for folder in ('wardrobe171-seal01','wardrobe171-verify01'):
  for path in sorted((BASE/folder).iterdir()):
   if not path.is_file():continue
   h=hashlib.sha256()
   with path.open('rb') as stream:
    for block in iter(lambda:stream.read(8*1024*1024),b''):h.update(block)
   manifest.append({'path':str(path.relative_to(ROOT)),'bytes':path.stat().st_size,'sha256':h.hexdigest()})
 retained=sum(p.stat().st_size for folder in BASE.glob('wardrobe171-*') if folder.is_dir() for p in folder.rglob('*') if p.is_file())
 card={'scope':'Exchange171 five wardrobe/skin corrections on protected accepted foundation','status':'INTERNAL_SCOPED_STATIC_CORRECTION_REVIEW_READY_DIRECTOR_APPEARANCE_PENDING','captured_activity_start':start['utc'],'captured_activity_end':end['utc'],'captured_activity_seconds':seconds,'prior_partial_body_and_wardrobe_seconds':34965.503284,'cumulative_partial_captured_seconds':34965.503284+seconds,'lifetime_net_seconds':None,
 'time_limits':'Current assistant activity excludes initial intake before capture, Director waiting and final receipt/design-commit overhead. Prior capture gaps remain. Native job time is not added to activity.',
 'engineering_model':None,'reasoning_effort':None,'engineering_tokens':None,'engineering_dollar_cost':None,'paid_provider_calls_in_this_scope':0,'asset_purchases_in_this_scope':0,'spend_provenance':'Observed local-only scope, not free subscription engineering',
 'native_job_count':sum(j['kind']=='native' for j in jobs),'native_job_sum_seconds':sum(j['seconds'] for j in jobs if j['kind']=='native'),'jobs':jobs,'job_outcome_definition':'Process exit only; failed visual previews retained separately, not promoted','retained_scope_bytes_before_receipt':retained,'selected_storage_forecast_bytes':350_000_000,'technical_selected_outputs':1,'director_accepted_outputs_in_this_scope':0,
 'limits':['Static neutral/full/partial prescribed poses only; not cloth physics or continuous riding','Coarse boots and loose hand hold remain named moving-shot dependencies','Body/groom/horse upstream release rights unresolved','Git text commits do not back up native media off-device'],
 'next_move':'Director reviews integrated corrected appearance; after direction selection, make complete inexpensive coordinated riding passage inside trailer timing.'}
 OUT.mkdir(exist_ok=True)
 for name,data in [('scope-events.json',events),('artifact-manifest.json',manifest),('CARD.json',card)]:
  (OUT/name).write_text(json.dumps(data,indent=2)+'\n')
 print(json.dumps({k:card[k] for k in ('captured_activity_seconds','native_job_count','retained_scope_bytes_before_receipt')}))

if __name__=='__main__':main()
