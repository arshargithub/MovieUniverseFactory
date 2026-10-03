"""Compact exchange170 receipt; no inferred engineering usage or lifetime time."""
from datetime import datetime
import hashlib
import json
from pathlib import Path
import sqlite3

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'.runtime/art-direction/series01-facebuilder-trial-01'
OUT=BASE/'wardrobe170-operating'


def main():
    con=sqlite3.connect(f'file:{ROOT/".runtime/experiment-ops.sqlite3"}?mode=ro',uri=True)
    events=[json.loads(p) for _,p in con.execute('SELECT id,payload FROM events ORDER BY seq') if json.loads(p)['event_id'].startswith('wardrobe170-')]
    con.close()
    starts={e['job_id']:e for e in events if e['event_type']=='job_started'}
    ends={e['job_id']:e for e in events if e['event_type']=='job_completed'}
    assert starts.keys()==ends.keys(), 'Reconcile every dispatched job before handoff'
    jobs=[{'id':name,'kind':start['job_kind'],'outcome':ends[name]['outcome'],'seconds':ends[name]['monotonic_seconds']-start['monotonic_seconds']} for name,start in starts.items()]
    start=next(e for e in events if e['event_id']=='wardrobe170-work-start')
    end=next(e for e in events if e['event_id']=='wardrobe170-work-end')
    seconds=(datetime.fromisoformat(end['utc'])-datetime.fromisoformat(start['utc'])).total_seconds()
    manifest=[]
    for folder in ('wardrobe170-seal02','wardrobe170-verify02'):
        for path in sorted((BASE/folder).iterdir()):
            if not path.is_file():continue
            h=hashlib.sha256()
            with path.open('rb') as stream:
                for block in iter(lambda:stream.read(8*1024*1024),b''):h.update(block)
            manifest.append({'path':str(path.relative_to(ROOT)),'bytes':path.stat().st_size,'sha256':h.hexdigest()})
    retained=sum(p.stat().st_size for folder in BASE.glob('wardrobe170-*') if folder.is_dir() for p in folder.rglob('*') if p.is_file())
    card={'scope':'Exchange170 tailored costume, open scarf and static single-tail refinement',
          'status':'INTERNAL_STATIC_DIRECTION_REVIEW_READY_DIRECTOR_APPEARANCE_PENDING',
          'captured_activity_start':start['utc'],'captured_activity_end':end['utc'],'captured_activity_seconds':seconds,
          'prior_partial_body_and_wardrobe_seconds':31155.672652,'cumulative_partial_captured_seconds':31155.672652+seconds,'lifetime_net_seconds':None,
          'time_limits':'Current assistant activity window excludes Director wait and final receipt/commit overhead; historical capture gaps remain. Native job time is not added to activity.',
          'engineering_model':None,'reasoning_effort':None,'engineering_tokens':None,'engineering_dollar_cost':None,
          'paid_provider_calls_in_this_scope':0,'asset_purchases_in_this_scope':0,'spend_provenance':'Observed scoped local execution only, not free subscription engineering.',
          'native_job_count':sum(j['kind']=='native' for j in jobs),'native_job_sum_seconds':sum(j['seconds'] for j in jobs if j['kind']=='native'),
          'job_outcome_definition':'Wrapper exit outcome only; failed visual previews and seal01 are retained and not promoted.',
          'jobs':jobs,'retained_scope_bytes_before_receipt':retained,'initial_storage_forecast_bytes':350_000_000,
          'technical_selected_outputs':1,'director_accepted_outputs_in_this_scope':0,
          'limits':['Static pose and prescribed partial lean only; no gait, cloth physics or continuous grasp','Coarse footwear/hem/hand hold remain shot-screen dependencies','Body/groom/horse release rights unresolved','Git text durability is not off-device native-media backup'],
          'next_move':'Review whole tailored costume direction, then complete an inexpensive coordinated riding passage in trailer timing before detail polish.'}
    OUT.mkdir(exist_ok=True)
    for name,data in [('scope-events.json',events),('artifact-manifest.json',manifest),('CARD.json',card)]:
        (OUT/name).write_text(json.dumps(data,indent=2)+'\n')
    print(json.dumps({k:card[k] for k in ('captured_activity_seconds','native_job_count','retained_scope_bytes_before_receipt')}))


if __name__=='__main__':main()
