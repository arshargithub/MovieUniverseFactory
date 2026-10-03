"""Compact scoped receipt; engineering usage stays unknown, not estimated."""
import hashlib
import json
from pathlib import Path
import sqlite3
from datetime import datetime

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'.runtime/art-direction/series01-facebuilder-trial-01'
OUT=BASE/'wardrobe169-operating'

def main():
    con=sqlite3.connect(f'file:{ROOT / ".runtime/experiment-ops.sqlite3"}?mode=ro',uri=True)
    events=[json.loads(p) for _,p in con.execute('SELECT id,payload FROM events ORDER BY seq')
            if json.loads(p)['event_id'].startswith(('wardrobe169-','body169-'))]
    con.close()
    starts={e['job_id']:e for e in events if e['event_type']=='job_started'}
    ends={e['job_id']:e for e in events if e['event_type']=='job_completed'}
    jobs=[]
    for name,start in starts.items():
        end=ends.get(name)
        jobs.append({'id':name,'kind':start['job_kind'],'outcome':end.get('outcome') if end else None,
                     'seconds':end['monotonic_seconds']-start['monotonic_seconds'] if end else None})
    assert all(j['outcome'] is not None for j in jobs), 'Reconcile running jobs before handoff'
    work_start=next(e for e in events if e['event_id']=='body169-work-start')
    work_end=next((e for e in events if e['event_id']=='wardrobe169-work-end'),None)
    seconds=(datetime.fromisoformat(work_end['utc'])-datetime.fromisoformat(work_start['utc'])).total_seconds() if work_end else None
    manifest=[]
    for folder in ('wardrobe169-seal01','wardrobe169-verify01'):
        for path in sorted((BASE/folder).iterdir()):
            if path.is_file():
                h=hashlib.sha256()
                with path.open('rb') as stream:
                    for block in iter(lambda:stream.read(8*1024*1024),b''):h.update(block)
                manifest.append({'path':str(path.relative_to(ROOT)),'bytes':path.stat().st_size,'sha256':h.hexdigest()})
    scoped_dirs=[p for p in BASE.glob('wardrobe169-*') if p.is_dir()]
    storage=sum(p.stat().st_size for folder in scoped_dirs for p in folder.rglob('*') if p.is_file())
    card={'scope':'Exchange169 wardrobe and existing horse/tack private static fit',
          'status':'INTERNAL_STATIC_REVIEW_READY_DIRECTOR_APPEARANCE_PENDING',
          'captured_activity_start':work_start['utc'],'captured_activity_end':work_end['utc'] if work_end else None,
          'captured_activity_seconds':seconds,'captured_prior_body_seconds':19454.46836,
          'cumulative_partial_captured_seconds':seconds+19454.46836 if seconds is not None else None,
          'lifetime_net_seconds':None,'time_limits':'Activity boundary capture, not token-generation time; historical body gaps remain. Receipt and local commit overhead after work_end is excluded.',
          'engineering_model':None,'reasoning_effort':None,'engineering_tokens':None,'engineering_dollar_cost':None,
          'paid_provider_calls_in_this_scope':0,'asset_purchases_in_this_scope':0,
          'spend_provenance':'Observed execution of this scoped local workflow; not the historical experiment provider ledger or subscription cost.',
          'native_job_count':sum(j['kind']=='native' for j in jobs),
          'native_job_sum_seconds':sum(j['seconds'] for j in jobs if j['kind']=='native'),
          'jobs':jobs,'retained_scope_bytes_before_receipt':storage,
          'director_accepted_outputs_in_this_scope':0,'technical_selected_outputs':1,
          'limits':['No gallop/motion/cloth simulation or dynamic grasp qualification','Provisional materials, scarf folds, boots and loose finger hold','Body/groom/horse release rights unresolved','No remote push or off-device media backup'],
          'next_move':'Select coarse costume direction, then complete an inexpensive coordinated riding passage in trailer timing before fine garment polish.'}
    OUT.mkdir(exist_ok=True)
    for name,data in [('scope-events.json',events),('artifact-manifest.json',manifest),('CARD.json',card)]:
        (OUT/name).write_text(json.dumps(data,indent=2)+'\n')
    print(json.dumps({k:card[k] for k in ('captured_activity_seconds','native_job_count','retained_scope_bytes_before_receipt')}))

if __name__=='__main__':main()
