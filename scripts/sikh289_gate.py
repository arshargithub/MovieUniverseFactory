"""Record reviewed evidence and retain the broader production block explicitly."""
import hashlib,json
from pathlib import Path
import numpy as np
from PIL import Image
from movie_factory import production_knowledge as pk
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'.runtime/art-direction/series01-sikh289'
RESULT=ROOT/'results/sikh289'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ev(p):return {'path':str(p.relative_to(ROOT)),'sha256':sha(p)}
def main():
    manual=json.loads((RESULT/'staging-observations.json').read_text())
    packet=json.loads((RESULT/'camera_patch-1/packet.json').read_text())
    contact=json.loads((BASE/'reopen-02/contact-trace.json').read_text())
    gaps={field:max(abs(r[field]) for r in contact) for field in ('front_center_x','front_ground_gap','rear_ground_gap')}
    gaps['greeting_support_boot_max']=max(r['support_boot_bottom'] for r in contact if r['supported_greeting_interval'])
    if max(gaps.values())>.006:raise ValueError(gaps)
    differences=[]
    for f in (1,169,199,271):
        a=np.array(Image.open(BASE/f'camera_patch-01/frames/frame-{f:04d}.png')).astype(int)
        b=np.array(Image.open(BASE/f'reopen-02/frame-{f:04d}.png')).astype(int)
        differences.append({'frame':f,'maximum_channel_difference':int(abs(a-b).max()),'mean_channel_difference':float(abs(a-b).mean())})
    receipts=[]
    for p in sorted(RESULT.glob('*/receipt.json')):
        r=json.loads(p.read_text());receipts.append({'job':p.parent.name,**r})
    metrics={'native_receipt_count':len(receipts),'successful_exit_count':sum(r['returncode']==0 for r in receipts),
        'failed_or_cancelled_exit_count':sum(r['returncode']!=0 for r in receipts),'native_process_seconds':sum(r['process_seconds'] for r in receipts),
        'source':'same-process monotonic elapsed in per-job receipts; includes setup/save/render, not only render waiting',
        'exact_net_work_seconds':None,'director_wait_seconds':None,'render_wait_seconds':None,'engineering_tokens':None,
        'reason':'Early context/capture gap and unmatched work interval across download reply; process overlap not added to agent effort.',
        'contact_trace_maxima_m':gaps,'sampled_reopen_pixels':differences,'external_provider_calls_this_pass':0,
        'aws_launches_this_pass':0,'new_media_remote_backed_up':False}
    (RESULT/'metrics.json').write_text(json.dumps(metrics,indent=2)+'\n')
    evidence=[ev(RESULT/'REVIEW.md'),ev(RESULT/'staging-observations.json'),ev(RESULT/'metrics.json'),ev(BASE/'camera_patch-01/sikh-staging-26s.mp4')]
    scoped={'scope':'Director-authorized action/geography study with actual motorcycle and declared character proxies; not final production admission',
        'director_acceptance':'PENDING','manual_findings':manual,'evidence':evidence,'technical_metrics':metrics}
    (RESULT/'staging-review.json').write_text(json.dumps(scoped,indent=2)+'\n')
    process={'authority','strategy','versioning','economics','cache_safety','current_state','au_reference','sikh_scope'}
    stage={'anticipation','au_staging'}
    checks=[]
    for rule in packet['obligations']:
        if rule['id'] in process:
            status='PASS';observation='Scoped authority, protected sources, capture limits and local-only disposition are documented. This is not final production admission.'
        elif rule['id'] in stage:
            status='PASS';observation='Seven-beat brief and chronological staging observations are recorded; camera, contact and transition defects were corrected internally.'
        else:
            status='NOT_RUN';observation='Final actor/cloth/illustrated look/performance/release qualification is not provided by the explicitly authorized proxy staging study. Preserve this blocker for production integration.'
        checks.append({'id':rule['id'],'kind':rule['check_kind'],'status':status,'action_taken':'Applied strategy289 and retained distinct staging versus production gates.','observation':observation,'evidence':evidence})
    review={'packet_digest':packet['packet_digest'],'scope':'Broader production admission, deliberately not claimed by this staging deliverable',
        'checks':checks,'hypotheses':[{'prediction':'A mechanically valid scene might still have unreadable staging or FX artifacts.',
        'observation':'Chronology exposed missed shoulder framing and dust bounds; failed variants retained.',
        'response':'Corrected framing and volume field, reviewed final chronology and scoped the remaining production requirements.', 'result':'resolved'}],
        'adjacent_regressions':'Compared final chronology and fresh reopen contacts. Final character/anatomy/cloth and sound remain unqualified, not hidden polish.',
        'stopping_reason':'Authorized staging deliverable only; no final production handoff or admission. Separate proxy authorization does not waive remaining production gates.'}
    (RESULT/'production-review.json').write_text(json.dumps(review,indent=2)+'\n')
    gate=pk.check_review(ROOT,packet,review);(RESULT/'production-gate.json').write_text(json.dumps(gate,indent=2)+'\n')
    print(json.dumps({'staging':manual['disposition'],'production_gate':gate,'metrics':metrics},indent=2))
    # This is intentionally a blocking production gate, not a fabricated PASS.
    return 0 if gate['ready_for_review'] else 2
if __name__=='__main__':raise SystemExit(main())
