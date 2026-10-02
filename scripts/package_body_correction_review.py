"""Mechanically refresh the existing compact body-review gallery and evidence card."""
import base64
from datetime import datetime
import hashlib
from io import BytesIO
import json
from pathlib import Path
import re

from PIL import Image
from movie_factory.experiment_ledger import Ledger

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / '.runtime/art-direction/series01-facebuilder-trial-01'
CURRENT = BASE / 'body160-fit39'
REFERENCE = BASE / 'body159-fit33'
PREFIX = 'body160-'
GALLERY = Path('/Users/adisharma/.codex/visualizations/2026/09/09/01a0878c-e7a2-75e0-873c-c31d97f879a1/pashtun-body-foundation-review.html')


def main():
    result=json.loads((CURRENT/'result.json').read_text())
    assert result['saved_verification']['reopened']
    rows=[
        ('neck-front','New front · continuous torso and adapted collarbones'),
        ('accepted-neck-front','Accepted bust · matched front and lighting'),
        ('interface','New right-facing ¾ · neck and shoulders'),
        ('accepted-interface','Accepted bust · matched right-facing ¾'),
        ('neck-other-side','New left-facing ¾'),
        ('neck-back','Posterior neck · hair hidden for anatomy inspection'),
        ('front','Whole-body front · foundation only'),
        ('back','Whole-body back · foundation only'),
        ('seated-interface','Seated shoulder connection · close ¾'),
        ('seated-neck-front','Seated neck and collarbones · close front'),
        ('seated-three-quarter','Seated reach ¾ · not final riding performance'),
        ('seated-side','Seated reach side · coarse rig'),
    ]
    # Reuse valid full-bust references from33 under identical camera/light.
    # The current run's control-source frames have a neck-only display mask.
    paths=[(REFERENCE if name.startswith('accepted-') else CURRENT)/(name+'.png') for name,_ in rows]+[REFERENCE/'interface.png',REFERENCE/'seated-interface.png']
    labels=[label for _,label in rows]+['Rejected fit33 · chest strip and shoulder contour','Rejected fit33 · seated shoulder connection']
    pictures=[]
    for path in paths:
        im=Image.open(path).convert('RGB');im.thumbnail((480,640))
        buf=BytesIO();im.save(buf,format='JPEG',quality=87)
        pictures.append('data:image/jpeg;base64,'+base64.b64encode(buf.getvalue()).decode())
    text=GALLERY.read_text()
    text=re.sub(r'const pictures=.*?;\n',lambda _: 'const pictures='+json.dumps(pictures)+';\n',text)
    text=re.sub(r'const labels=.*?;\n',lambda _: 'const labels='+json.dumps(labels)+';\n',text)
    text=re.sub(r'<img src="[^"]*"',lambda _: '<img src="'+pictures[0]+'"',text,count=1)
    text=re.sub(r'<figcaption[^>]*>.*?</figcaption>', '<figcaption aria-live="polite">'+labels[0]+'</figcaption>',text,count=1)
    buttons=['New front','Accepted front','New ¾','Accepted ¾','Other ¾','Neck back','Full front','Full back','Seated close ¾','Seated close front','Seated full ¾','Seated side','Rejected neutral','Rejected seated']
    controls='\n'.join(f'    <button class="btn" type="button" data-i="{i}">{label}</button>' for i,label in enumerate(buttons))
    text=re.sub(r'(<div class="viz-controls"[^>]*>).*?(</div>)',lambda m:m[1]+'\n'+controls+'\n  '+m[2],text,count=1,flags=re.S)
    text=text.replace('body159-fit33','body160-fit39').replace("version:'body159'","version:'body160'").replace("version==='body159'","version==='body160'")
    text=re.sub(r'(body-count">)\d+ / \d+',lambda m:m[1]+'1 / '+str(len(paths)),text)
    assert len(text.encode())<1_000_000 and 'data-i="13"' in text
    GALLERY.write_text(text)
    events=[e for e in Ledger(ROOT/'.runtime/experiment-ops.sqlite3').events() if e['event_id'].startswith(PREFIX)]
    starts={e['job_id']:e for e in events if e['event_type']=='job_started'}
    jobs=[{'id':e['job_id'],'returncode':e['returncode'],'seconds':e['monotonic_seconds']-starts[e['job_id']]['monotonic_seconds']} for e in events if e['event_type']=='job_completed']
    start=next(e for e in events if e['event_id']==PREFIX+'work-start')
    end=next(e for e in events if e['event_id']==PREFIX+'work-end')
    seconds=(datetime.fromisoformat(end['utc'].replace('Z','+00:00'))-datetime.fromisoformat(start['utc'].replace('Z','+00:00'))).total_seconds()
    files=[p for d in BASE.glob(PREFIX+'fit*') if d.is_dir() for p in d.rglob('*') if p.is_file()]
    card=BASE/'body160-operating';card.mkdir(exist_ok=True)
    manifest={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [CURRENT/'adult-body-fit.blend',CURRENT/'result.json',BASE/'natural152-seal-16/natural-hair.blend',*paths]}
    prior=json.loads((BASE/'body159-operating/pass-summary.json').read_text())['cumulative_captured_seconds']
    summary={'scope':'Replace broad bust graft with continuous donor shoulders and anatomical relief, exchange160','disposition':'YELLOW_DIRECTOR_REVIEW_PENDING','captured_active_seconds':seconds,'prior_captured_seconds':prior,'cumulative_captured_seconds':prior+seconds,'capture':'PARTIAL','capture_exclusions':['Initial context recovery','Final receipt/commit/push overhead'],'jobs':jobs,'native_time_inside_activity':True,'retained_evidence_bytes':sum(p.stat().st_size for p in files),'paid_provider_calls':0,'asset_purchases_usd':0,'engineering_tokens':None,'engineering_cost_usd':None,'full_suite_run':False,'remaining':['Director appearance acceptance','Dressed riding fit','Full facial/motion qualification','Rights and backup']}
    for name,value in [('pass-summary.json',summary),('events.json',events),('checksums.json',manifest)]:
        (card/name).write_text(json.dumps(value,indent=2)+'\n')
    print(json.dumps({'gallery_bytes':len(text.encode()),'captured_minutes':seconds/60,'cumulative_minutes':(prior+seconds)/60,'artifact_mb':summary['retained_evidence_bytes']/1e6,'jobs':len(jobs)}))


if __name__=='__main__':main()
