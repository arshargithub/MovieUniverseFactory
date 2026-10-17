"""Evidence structure and numeric checks; manual visual findings remain explicit."""
import hashlib,json
from pathlib import Path
import numpy as np
from PIL import Image
from movie_factory import production_knowledge as pk
from movie_factory.sikh291_motion import FRONT_FIXED,REAR_FIXED,PARKED
ROOT=Path(__file__).resolve().parents[1]
RESULT=ROOT/'results/sikh291'
BASE=ROOT/'.runtime/art-direction/series01-sikh291'
MOVIE=BASE/'movie-03'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ev(p):return {'path':str(p.relative_to(ROOT)),'sha256':sha(p)}
def main():
    manual=json.loads((RESULT/'staging-observations.json').read_text())
    packet=json.loads((RESULT/'reopen-1/packet.json').read_text())
    trace=json.loads((BASE/'reopen-01/contact-trace.json').read_text())
    maxima={k:max(abs(r[k]) for r in trace) for k in ('front_center_x','front_ground_gap','rear_ground_gap')}
    maxima['greeting_support_boot_max']=max(r['support_boot_bottom'] for r in trace if r['supported_greeting_interval'])
    if max(maxima.values())>.006:raise ValueError(maxima)
    assert all(abs(r['spear_tip_z']-3.19)<1e-5 for r in trace if 15.5<=r['source_t']<=17.0)
    assert all(abs(r['spear_actual_ground_gap'])<1e-5 for r in trace if 15.5<=r['source_t']<=17.0)
    assert min(r['right_hand_to_bar'] for r in trace if 10<=r['source_t']<=12.3)>.15
    assert json.loads((BASE/'reopen-01/reopen.json').read_text())['lamp_common_steering_owner']
    rows=json.loads((MOVIE/'bike-adaptation.json').read_text())['parts']
    owners={int(r['part'][-3:]):r['owner'] for r in rows}
    assert all(owners[i]=='BIKE steering owner' for i in FRONT_FIXED)
    assert all(owners[i]=='BIKE travel owner' for i in REAR_FIXED)
    assert all(owners[i].startswith('removed') for i in PARKED|{92,93,733,734})
    assert len(rows)==755
    diffs=[]
    for f in (1,41,179,213,315,445,505):
        a=np.array(Image.open(MOVIE/f'frames/frame-{f:04d}.png')).astype(int)
        b=np.array(Image.open(BASE/f'reopen-01/frame-{f:04d}.png')).astype(int)
        diffs.append({'frame':f,'maximum_channel_difference':int(abs(a-b).max()),'mean_channel_difference':float(abs(a-b).mean())})
    receipts=[{'job':p.parent.name,**json.loads(p.read_text())} for p in sorted(RESULT.glob('*/receipt.json'))]
    metrics={'native_receipt_count':len(receipts),'successful_exit_count':sum(r['returncode']==0 for r in receipts),
        'failed_or_cancelled_exit_count':sum(r['returncode']!=0 for r in receipts),
        'native_process_seconds':sum(r['process_seconds'] for r in receipts),
        'native_time_definition':'Monotonic worker elapsed includes setup/save/render, not only render wait; jobs sequential.',
        'net_work_seconds':None,'director_wait_seconds':None,'render_wait_seconds':None,'engineering_tokens':None,
        'reason':'No precise cognitive-effort allocation or token telemetry; partial initial ledger capture. Do not add worker time to activity span.',
        'contact_trace_maxima_m':maxima,'component_ownership_checks':'PASS: fixed fork/shocks, removed parked stands and old saddle springs',
        'sampled_reopen_pixels':diffs,'external_provider_calls':0,'aws_launches':0,'new_media_remote_backed_up':False}
    (RESULT/'metrics.json').write_text(json.dumps(metrics,indent=2)+'\n')
    evidence=[ev(RESULT/n) for n in ('REVIEW.md','staging-observations.json','metrics.json')]+[ev(MOVIE/'sikh-staging-22s.mp4')]
    (RESULT/'staging-review.json').write_text(json.dumps({'scope':'Authorized corrected proxy staging only','director_acceptance':'PENDING','findings':manual,'evidence':evidence,'technical':metrics},indent=2)+'\n')
    process={'authority','strategy','versioning','economics','cache_safety','current_state','au_reference','sikh_scope','anticipation','au_staging'}
    checks=[{'id':r['id'],'kind':r['check_kind'],'status':'PASS' if r['id'] in process else 'NOT_RUN',
        'action_taken':'Applied291 strategy and scoped review; retain broader production requirements.',
        'observation':'Manual source/authority/beat review recorded; not artistic acceptance.' if r['id'] in process else 'Final actor, cloth, anatomy, style, motion and release qualification remains outside this explicitly authorized staging study.',
        'evidence':evidence} for r in packet['obligations']]
    review={'packet_digest':packet['packet_digest'],'scope':'Broader production admission, NOT claimed', 'checks':checks,
        'hypotheses':[{'prediction':'Radial wheel classification can rotate stationary fittings; fitting a light or sling by silhouette can still fail adjacent views.',
            'observation':'Quarter-turn controls and rear view exposed wrong part ownership, tall saddle springs, lens obstruction and neck-crossing sling. Original and failed candidates retained.',
            'response':'Explicit part ownership, aligned lamp assembly, shortened seat supports, shoulder-routed sling, full chronological review and fresh reopen.','result':'resolved'}],
        'adjacent_regressions':'Review records full sequence, side support, uncover-to-greeting and spear strike. No general motion or final cloth certification.',
        'stopping_reason':'Completed authorized provisional staging correction; production admission remains blocked, not silently waived.'}
    (RESULT/'production-review.json').write_text(json.dumps(review,indent=2)+'\n')
    gate=pk.check_review(ROOT,packet,review)
    (RESULT/'production-gate.json').write_text(json.dumps(gate,indent=2)+'\n')
    print(json.dumps({'staging':manual['disposition'],'production_gate':gate,'metrics':metrics},indent=2))
    return 0 if gate['ready_for_review'] else 2
if __name__=='__main__':raise SystemExit(main())
