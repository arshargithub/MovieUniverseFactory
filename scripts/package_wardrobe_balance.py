"""Package the reviewed static exchange172 result, retaining unknown usage."""
import base64
from datetime import datetime
import hashlib
from io import BytesIO
import json
from pathlib import Path
import sqlite3
from PIL import Image,ImageChops
from package_wardrobe_fit_review import check_review

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'.runtime/art-direction/series01-facebuilder-trial-01'
OUT=BASE/'wardrobe172-operating'
GALLERY=Path('/Users/adisharma/.codex/visualizations/2026/09/09/01a0878c-e7a2-75e0-873c-c31d97f879a1/pashtun-wardrobe-balance.html')
CRITERIA={'fitted_sleeves','folded_shawl','shoulder_clearance','proportion_check','protected_foundation','posed_interfaces','adjacent_regressions'}
ROWS=[('standing-front','Front'),('upper-front','Front close-up'),('upper-left','Left ¾'),('upper-right','Right ¾'),('upper-rear','Rear close-up'),('standing-side','Standing side'),('standing-rear','Back'),('mounted-side','Riding side'),('mounted-opposite-side','Other riding side'),('mounted-upper-left','Riding left ¾'),('mounted-upper-right','Riding right ¾'),('mounted-upper-rear','Riding rear ¾'),('mounted-partial','Partial lean')]

def main():
    selected=BASE/'wardrobe172-seal01';fresh=BASE/'wardrobe172-verify01'
    review=json.loads((OUT/'visual-review.json').read_text());check_review(review,selected,'wardrobe172-seal01',CRITERIA)
    verified=json.loads((fresh/'result.json').read_text())
    assert all(verified[k] for k in ('reopened','protected_signatures_exact','body_basis_exact','source_unchanged'))
    assert all(v is not None and v<2e-5 for v in verified['surface_errors'].values())
    compared=[]
    for name,_ in ROWS:
        previous=BASE/'wardrobe172-preview13'/(name+'.png')
        if previous.is_file():
            assert ImageChops.difference(Image.open(previous).convert('RGB'),Image.open(selected/(name+'.png')).convert('RGB')).getbbox() is None
            compared.append(name)
    reopened={}
    for path in fresh.glob('reopened-*.png'):
        delta=ImageChops.difference(Image.open(path).convert('RGB'),Image.open(selected/path.name.removeprefix('reopened-')).convert('RGB'))
        maximum=max(v[1] for v in delta.getextrema());assert maximum<=4
        reopened[path.name]=maximum
    assert len(compared)==4 and len(reopened)==2
    frames=[(selected/(name+'.png'),short,'Corrected static wardrobe · '+short+' · appearance pending') for name,short in ROWS]
    refs=ROOT/'.runtime/art-direction/series01-pashtun-baseline-v01'
    frames += [(refs/'frontal-v02-individualized.png','Illustrated front','Approved illustrated identity and costume vocabulary'),(refs/'portrait-v07-individualized.png','Illustrated portrait','Approved illustrated identity and folded shawl vocabulary')]
    data=[]
    for path,short,label in frames:
        im=Image.open(path).convert('RGB');im.thumbnail((920,760));stream=BytesIO();im.save(stream,'JPEG',quality=84,optimize=True)
        data.append({'short':short,'label':label,'image':'data:image/jpeg;base64,'+base64.b64encode(stream.getvalue()).decode()})
    html=GALLERY.read_text();assert '/* REVIEW_DATA */[]' in html
    html=html.replace('/* REVIEW_DATA */[]',json.dumps(data));assert len(html.encode())<1_000_000
    GALLERY.write_text(html)
    (OUT/'pixel-comparison.json').write_text(json.dumps({'selected_vs_inspected_preview_exact':compared,'fresh_open_max_channel_differences':reopened,'other_selected_frames':'Individually visually reviewed; not preview-identical claim'},indent=2)+'\n')
    print(json.dumps({'views':len(data),'gallery_bytes':len(html.encode()),'preview_exact':len(compared),'reopened':reopened}))

def receipt():
    con=sqlite3.connect(f'file:{ROOT/".runtime/experiment-ops.sqlite3"}?mode=ro',uri=True)
    events=[json.loads(p) for (p,) in con.execute('SELECT payload FROM events ORDER BY seq') if json.loads(p)['event_id'].startswith('wardrobe172-')];con.close()
    starts={e['job_id']:e for e in events if e['event_type']=='job_started'};ends={e['job_id']:e for e in events if e['event_type']=='job_completed'};assert starts.keys()==ends.keys()
    start=next(e for e in events if e['event_id']=='wardrobe172-work-start');end=next(e for e in events if e['event_id']=='wardrobe172-work-end')
    seconds=(datetime.fromisoformat(end['utc'])-datetime.fromisoformat(start['utc'])).total_seconds()
    retained=sum(p.stat().st_size for folder in BASE.glob('wardrobe172-*') if folder.is_dir() for p in folder.rglob('*') if p.is_file())
    manifest=[]
    for folder in ('wardrobe172-seal01','wardrobe172-verify01'):
        for path in sorted((BASE/folder).iterdir()):
            if not path.is_file():continue
            h=hashlib.sha256()
            with path.open('rb') as stream:
                for block in iter(lambda:stream.read(8*1024*1024),b''):h.update(block)
            manifest.append({'path':str(path.relative_to(ROOT)),'bytes':path.stat().st_size,'sha256':h.hexdigest()})
    card={'scope':'Exchange172 fitted sleeves, folded scarf/shoulder clearance and measurement-led head proportion check','status':'SCOPED_STATIC_REVIEW_READY_DIRECTOR_APPEARANCE_PENDING','captured_activity_seconds':seconds,'capture_limits':'Initial context reading before capture and final receipt/commit overhead excluded; prior gaps remain','prior_partial_body_wardrobe_seconds':38416.321559,'cumulative_partial_captured_seconds':38416.321559+seconds,'lifetime_net_seconds':None,'engineering_tokens':None,'engineering_dollar_cost':None,'engineering_model':None,'reasoning_effort':None,'paid_provider_calls':0,'asset_purchases':0,'native_job_count':sum(s['job_kind']=='native' for s in starts.values()),'all_jobs_reconciled':True,'retained_directories_bytes_before_receipt':retained,'gallery_bytes':GALLERY.stat().st_size,'technical_selected_outputs':1,'director_accepted_outputs':0,'head_scale_changed':False,'limits':['Approximate landmarks, not medical anthropometry or universal aesthetic proof','Static prescribed poses, not riding/cloth dynamics/general rig qualification','Existing loose grasp/boots/horse look remain moving-shot dependencies','Upstream release rights unresolved; local Git is not off-device media backup']}
    for name,value in [('CARD.json',card),('scope-events.json',events),('artifact-manifest.json',manifest)]:
        (OUT/name).write_text(json.dumps(value,indent=2)+'\n')
    print(json.dumps(card))

if __name__=='__main__':
    import sys
    if sys.argv[1:]==['receipt']:receipt()
    elif sys.argv[1:]==[]:main()
    else:raise ValueError('Only fixed packaging or receipt modes')
