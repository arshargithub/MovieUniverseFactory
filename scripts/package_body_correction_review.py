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
CURRENT = BASE / 'body158-fit27'
GALLERY = Path('/Users/adisharma/.codex/visualizations/2026/09/09/01a0878c-e7a2-75e0-873c-c31d97f879a1/pashtun-body-foundation-review.html')


def main():
    result=json.loads((CURRENT/'result.json').read_text())
    assert result['saved_verification']['reopened']
    rows=[
        ('interface','Neck and shoulders · continuous surface'),
        ('three-quarter','Facing right ¾ · corrected foundation'),
        ('other-three-quarter','Facing left ¾ · corrected foundation'),
        ('back','Back · corrected foundation'),
        ('side','Side · corrected foundation'),
        ('front','Front · corrected foundation'),
        ('seated-three-quarter','Seated reach ¾ · not final riding performance'),
        ('seated-side','Seated reach side · localized elbow correction'),
    ]
    paths=[CURRENT/(name+'.png') for name,_ in rows]+[BASE/'body157-fit16/interface.png',BASE/'body157-fit16/seated-side.png']
    labels=[label for _,label in rows]+['Previous rejected neck interface','Previous seated elbow']
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
    buttons=['Neck and shoulders','Facing right ¾','Facing left ¾','Back','Side','Front','Seated ¾','Seated side','Previous neck','Previous elbow']
    for i,label in enumerate(buttons[:9]):
        text=re.sub(r'(<button[^>]*data-i="'+str(i)+r'">).*?(</button>)',lambda m:m[1]+label+m[2],text)
    if 'data-i="9"' not in text:
        text=text.replace('  </div>\n  <figure>', '    <button class="btn" type="button" data-i="9">Previous elbow</button>\n  </div>\n  <figure>',1)
    text=text.replace('body157-fit16','body158-fit27').replace("version:'body157'","version:'body158'").replace("version==='body157'","version==='body158'")
    text=text.replace('REVISED_FOUNDATION_NOT_ANIMATION_READY','CORRECTED_INTERFACE_DIRECTOR_REVIEW_PENDING').replace('1 / 9','1 / 10')
    assert len(text.encode())<1_000_000 and 'data-i="9"' in text
    GALLERY.write_text(text)
    events=[e for e in Ledger(ROOT/'.runtime/experiment-ops.sqlite3').events() if e['event_id'].startswith('body158-')]
    starts={e['job_id']:e for e in events if e['event_type']=='job_started'}
    jobs=[{'id':e['job_id'],'returncode':e['returncode'],'seconds':e['monotonic_seconds']-starts[e['job_id']]['monotonic_seconds']} for e in events if e['event_type']=='job_completed']
    start=next(e for e in events if e['event_id']=='body158-work-start')
    end=next(e for e in events if e['event_id']=='body158-work-end')
    seconds=(datetime.fromisoformat(end['utc'].replace('Z','+00:00'))-datetime.fromisoformat(start['utc'].replace('Z','+00:00'))).total_seconds()
    files=[p for d in BASE.glob('body158-fit*') if d.is_dir() for p in d.rglob('*') if p.is_file()]
    card=BASE/'body158-operating';card.mkdir(exist_ok=True)
    manifest={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [CURRENT/'adult-body-fit.blend',CURRENT/'result.json',BASE/'natural152-seal-16/natural-hair.blend',*paths]}
    summary={'scope':'Neck integration and seated elbow correction, exchange158','disposition':'YELLOW_DIRECTOR_REVIEW_PENDING','captured_active_seconds':seconds,'prior_captured_seconds':2809.146363,'cumulative_captured_seconds':2809.146363+seconds,'capture':'PARTIAL','capture_exclusions':['Initial context recovery','Final receipt/commit overhead'],'jobs':jobs,'native_time_inside_activity':True,'retained_evidence_bytes':sum(p.stat().st_size for p in files),'paid_provider_calls':0,'asset_purchases_usd':0,'engineering_tokens':None,'engineering_cost_usd':None,'full_suite_run':False,'remaining':['Director appearance acceptance','Dressed riding fit','Full facial/motion qualification','Rights and backup']}
    for name,value in [('pass-summary.json',summary),('events.json',events),('checksums.json',manifest)]:
        (card/name).write_text(json.dumps(value,indent=2)+'\n')
    print(json.dumps({'gallery_bytes':len(text.encode()),'captured_minutes':seconds/60,'cumulative_minutes':(2809.146363+seconds)/60,'artifact_mb':summary['retained_evidence_bytes']/1e6,'jobs':len(jobs)}))


if __name__=='__main__':main()
