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
CURRENT = BASE / 'body161-fit47'
PROOF = BASE / 'body161-verify48'
REFERENCE = CURRENT
PREFIX = 'body161-'
GALLERY = Path('/Users/adisharma/.codex/visualizations/2026/09/09/01a0878c-e7a2-75e0-873c-c31d97f879a1/pashtun-body-foundation-review.html')


def check_review_gate(review, candidate, evidence_root):
    """Packaging cannot turn a known-failing internal preview into a handoff.

    PASS is recorded visual inspection, not an automated aesthetic judgment.
    Source/reopen checks are an independent prerequisite in main().
    """
    required={'neck_clavicles','chest_shoulders','arms_elbows','knees','abdomen','whole_result'}
    rows=review.get('criteria',[])
    if review.get('candidate')!=candidate or {r.get('id') for r in rows}!=required or len(rows)!=len(required):
        raise ValueError('Visual review does not cover this integrated candidate')
    if any(r.get('status')!='PASS' or not r.get('images') or not r.get('observation') for r in rows):
        raise ValueError('Known visual failures or unreviewed regions must stay internal')
    root=Path(evidence_root).resolve()
    for row in rows:
        for name in row['images']:
            path=root/name
            if Path(name).is_absolute() or path.is_symlink() or not path.is_file() or root not in path.resolve().parents:
                raise ValueError('Visual evidence must be present inside this candidate')
    return True


def main():
    review=json.loads((BASE/'body161-operating/visual-review.json').read_text())
    check_review_gate(review,CURRENT.name,CURRENT)
    result=json.loads((PROOF/'result.json').read_text())
    assert result['saved_verification']['reopened']
    assert result['saved_verification']['evaluated_surfaces_match_reconstruction']
    assert review['technical_gate']=='PASS' and review['fresh_open_visual_replay']=='PASS'
    rows=[
        ('neck-front','New front · retained accepted throat and collarbones'),
        ('accepted-neck-front','Accepted bust · matched front and lighting'),
        ('interface','New right-facing ¾ · neck and shoulders'),
        ('accepted-interface','Accepted bust · matched right-facing ¾'),
        ('neck-other-side','New left-facing ¾'),
        ('neck-back','Posterior neck · hair hidden for anatomy inspection'),
        ('front','Whole-body front · foundation only'),
        ('back','Whole-body back · foundation only'),
        ('seated-interface','Seated shoulder connection · close ¾'),
        ('seated-neck-front','Seated neck and collarbones · close front'),
        ('seated-elbow','Seated elbow · left arm, isolated skin support'),
        ('seated-other-elbow','Seated elbow · right arm, isolated skin support'),
        ('seated-knees','Seated knees · local bend correction'),
        ('seated-other-knees','Seated knees · opposite side'),
        ('seated-abdomen','Seated lower abdomen · symmetrical hip support'),
        ('seated-front','Seated reach front · static foundation only'),
        ('seated-three-quarter','Seated reach ¾ · not final riding performance'),
        ('seated-side','Seated reach side · coarse rig'),
        ('three-quarter','Neutral full ¾ · adult body foundation'),
        ('other-three-quarter','Neutral opposite ¾ · adult body foundation'),
        ('side','Neutral side · adult body foundation'),
    ]
    # References are the full accepted bust: temporarily unmask the control
    # during native rendering, using the exact same camera/light as candidate.
    paths=[(REFERENCE if name.startswith('accepted-') else CURRENT)/(name+'.png') for name,_ in rows]
    labels=[label for _,label in rows]
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
    buttons=['New front','Accepted front','New ¾','Accepted ¾','Other ¾','Neck back','Full front','Full back','Seated close ¾','Seated close front','Left elbow','Right elbow','Knees','Other knees','Abdomen','Seated front','Seated ¾','Seated side','Full ¾','Other full ¾','Full side']
    controls='\n'.join(f'    <button class="btn" type="button" data-i="{i}">{label}</button>' for i,label in enumerate(buttons))
    text=re.sub(r'(<div class="viz-controls"[^>]*>).*?(</div>)',lambda m:m[1]+'\n'+controls+'\n  '+m[2],text,count=1,flags=re.S)
    text=re.sub(r"candidate:'body\d+-fit\d+'", "candidate:'"+CURRENT.name+"'",text)
    text=re.sub(r"version:'body\d+'", "version:'body161'",text)
    text=re.sub(r"version==='body\d+'", "version==='body161'",text)
    text=text.replace("acceptance:'CORRECTED_INTERFACE_DIRECTOR_REVIEW_PENDING'","acceptance:'INTERNAL_VISUAL_GATE_PASS_DIRECTOR_REVIEW_PENDING'")
    text=re.sub(r'(body-count">)\d+ / \d+',lambda m:m[1]+'1 / '+str(len(paths)),text)
    assert len(text.encode())<1_000_000 and 'data-i="20"' in text
    GALLERY.write_text(text)
    events=[e for e in Ledger(ROOT/'.runtime/experiment-ops.sqlite3').events() if e['event_id'].startswith(PREFIX)]
    starts={e['job_id']:e for e in events if e['event_type']=='job_started'}
    jobs=[{'id':e['job_id'],'kind':e.get('job_kind'),'returncode':e['returncode'],'seconds':e['monotonic_seconds']-starts[e['job_id']]['monotonic_seconds'],
           'utc_seconds':(datetime.fromisoformat(e['utc'])-datetime.fromisoformat(starts[e['job_id']]['utc'])).total_seconds()} for e in events if e['event_type']=='job_completed']
    anomalies=[{'job':j['id'],'utc_minus_monotonic_seconds':j['utc_seconds']-j['seconds']} for j in jobs if abs(j['utc_seconds']-j['seconds'])>1.]
    start=next(e for e in events if e['event_id']==PREFIX+'work-start')
    end=next(e for e in events if e['event_id']==PREFIX+'work-end')
    seconds=(datetime.fromisoformat(end['utc'].replace('Z','+00:00'))-datetime.fromisoformat(start['utc'].replace('Z','+00:00'))).total_seconds()
    files=[p for pattern in ('fit*','verify*') for d in BASE.glob(PREFIX+pattern) if d.is_dir() for p in d.rglob('*') if p.is_file()]
    card=BASE/'body161-operating';card.mkdir(exist_ok=True)
    manifest={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [CURRENT/'adult-body-fit.blend',PROOF/'result.json',PROOF/'pixel-comparison.json',*PROOF.glob('*.png'),BASE/'natural152-seal-16/natural-hair.blend',BASE/'body161-job47.json',BASE/'body161-job48.json',card/'visual-review.json',ROOT/'src/movie_factory/adapters/blender/body_studio_fit.py',*paths]}
    prior=json.loads((BASE/'body160-operating/pass-summary.json').read_text())['cumulative_captured_seconds']
    summary={'scope':'Retain accepted throat/clavicles and correct neutral/seated shoulder, elbow, knee and abdominal structure, exchange161','disposition':'INTERNAL_VISUAL_GATE_PASS_DIRECTOR_REVIEW_PENDING','captured_active_seconds':seconds,'prior_captured_seconds':prior,'cumulative_captured_seconds':prior+seconds,'capture':'PARTIAL','capture_exclusions':['Initial context recovery','Final receipt/commit overhead'],'jobs':jobs,'native_time_inside_activity':True,'retained_evidence_bytes':sum(p.stat().st_size for p in files),'paid_provider_calls':0,'asset_purchases_usd':0,'engineering_tokens':None,'engineering_cost_usd':None,'full_suite_run':False,'visual_gate':'visual-review.json','remaining':['Director appearance acceptance','Dressed riding fit','Full facial/motion qualification','Textured body integration','Rights and backup']}
    summary.update(captured_utc_work_span_seconds=seconds,clock_anomalies=anomalies,
                   duration_basis='Cumulative capture is historical partial spans plus this UTC work window, not exact active effort. Unknown clock/suspend gaps are not fabricated Director waits or subtracted.',
                   exact_active_seconds=None if anomalies else seconds)
    if anomalies:summary['captured_active_seconds']=None
    for name,value in [('pass-summary.json',summary),('events.json',events),('checksums.json',manifest)]:
        (card/name).write_text(json.dumps(value,indent=2)+'\n')
    print(json.dumps({'gallery_bytes':len(text.encode()),'utc_work_span_minutes':seconds/60,'exact_active_seconds':summary['exact_active_seconds'],'cumulative_capture_minutes':(prior+seconds)/60,'artifact_mb':summary['retained_evidence_bytes']/1e6,'jobs':len(jobs)}))


if __name__=='__main__':main()
