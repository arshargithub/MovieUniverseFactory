"""Bind completed scoped media and manual observations; never admit production."""
import json,sys
from pathlib import Path
import numpy as np
from PIL import Image
from movie_factory import production_knowledge as pk
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'.runtime/art-direction/series01-sikh320'
def main():
    v=int(sys.argv[1]);assert 1<=v<=20
    dest=ROOT/'results/sikh320';delivery=BASE/f'delivery-{v:02d}'
    verify=json.loads((BASE/f'verify-{v:02d}/interfaces.json').read_text())
    audit=json.loads((BASE/f'audit-{v:02d}/protection.json').read_text())
    media=json.loads((delivery/'verification.json').read_text())
    assert verify['status']==audit['status']=='PASS'
    assert media['decode']=='PASS' and len(media['frames'])==190
    assert not media['direct_motion'] and not media['direct_audio']
    comparison=[]
    for f in (276,298,321,344,381,417):
        original=BASE/f'motion-{v:02d}/frames/frame-{f:04d}.png'
        repeat=BASE/f'reopen-{v:02d}/frames/frame-{f:04d}.png'
        a=np.asarray(Image.open(original).convert('RGB'),dtype=np.int16)
        b=np.asarray(Image.open(repeat).convert('RGB'),dtype=np.int16)
        delta=np.abs(a-b)
        comparison.append({'frame':f,'maximum_channel_difference_255':int(delta.max()),'channels_over_one':int((delta>1).sum()),'source_sha':pk.file_hash(original),'repeat_sha':pk.file_hash(repeat)})
    replay={'status':'PASS' if all(x['maximum_channel_difference_255']<=1 for x in comparison) else 'FAIL','threshold_maximum_channel_255':1,'controls':comparison,'scope':'Six independently reopened same-frame controls; not motion or production acceptance.'}
    (dest/'replay.json').write_text(json.dumps(replay,indent=2))
    def bound(p):return {'path':str(p.relative_to(ROOT)),'sha256':pk.file_hash(p)}
    evidence=[dest/'STRATEGY.md',dest/'REVIEW.md',dest/'CARRY_FORWARD.md',dest/'knowledge-reconciliation.json',dest/'replay.json',BASE/f'build-{v:02d}/sequence.blend',BASE/f'verify-{v:02d}/interfaces.json',BASE/f'audit-{v:02d}/protection.json',delivery/'verification.json']
    evidence+=sorted((delivery/'chronology').glob('*.jpg'))+sorted((delivery/'encoded-review').glob('*.jpg'))
    queue={'status':'AWAITING_DIRECTOR_AV','authority':'docs/knowledge/review_control/README.md#current-authority--exchange313','scope':{'core_frames':[276,417],'rendered_frames':[252,441],'fps':24,'seconds':190/24,'context_frames_each_side':24},'candidate':bound(delivery/'nihang-crowd-review.mp4'),'protected_pashtun':bound(ROOT/'.runtime/art-direction/series01-finish248/delivery01/pashtun-20s.mp4'),'evidence':[bound(p) for p in evidence],'pending_director_judgments':['Coordinated leader and horse performance at full speed, especially gather-to-lift and forceful landing','Individual crowd clearance while continuing to watch rider','Supporting wardrobe and accessories belong in the accepted Pashtun film language','Sound/contact timing and continuity across both handles'],'limitations':{'direct_motion':False,'direct_audio':False,'strict_replay':replay['status'],'full_sequence_reintegration':'NOT_RUN','principal_sikh':'protected unfinished proxy','production_pass':False,'s3_upload':False}}
    (dest/'DIRECTOR_AV_QUEUE.json').write_text(json.dumps(queue,indent=2))
    task=json.loads((dest/f'delivery-{v}/task.json').read_text());task['id']=f'sikh320-final-review-{v}'
    # Only these explicitly reviewed320 source amendments are rebound. Do not
    # sweep/rehash other inherited inputs to bypass a stale packet.
    reconciliation=json.loads((dest/'knowledge-reconciliation.json').read_text())
    assert reconciliation['status']=='REVIEWED_RECONCILIATION'
    for name in ('docs/knowledge/CURRENT_PRODUCTION_STATE.md','docs/knowledge/SUPPORTING_SHOT_REVIEW_320.md'):
        assert pk.file_hash(ROOT/name)==reconciliation['reviewed_files'][name]
        task['inputs'][name]=pk.file_hash(ROOT/name)
    for p in [*evidence,Path(__file__).resolve()]:task['inputs'][str(p.relative_to(ROOT))]=pk.file_hash(p)
    packet=pk.task_packet(ROOT,task);assert packet['dispatch_ready'],packet['blockers']
    checks=[]
    evidenced_process={'authority','strategy','versioning','cache_safety','current_state'}
    for obligation in packet['obligations']:
        rid=obligation['id'];status='PASS' if rid in evidenced_process else 'NOT_RUN'
        if rid=='render_profile' and replay['status']=='FAIL':status='FAIL'
        checks.append({'id':rid,'kind':obligation['check_kind'],'status':status,'observation':'Applied scoped local strategy and preserved authority/master boundaries; exact evidence and human-pending judgments are bound in the manual queue. Frame/source/technical findings are in REVIEW.md; no direct playback/listening or generalized artistic acceptance.','action_taken':'Kept prior rejection and strict exceptions separate. Prepared only the Director-authorized isolated AV review, not a successful strict deliver receipt.','evidence':[bound(dest/'REVIEW.md'),bound(dest/'DIRECTOR_AV_QUEUE.json')]})
    review={'packet_digest':packet['packet_digest'],'checks':checks,'hypotheses':[{'prediction':'Independent outward body motion can violate respectful rider attention or overtwist necks.','observation':'Fixed headings failed the outer-actor control; coupled orientation/support now meets the recorded range and target checks. Full-speed human interpretation remains pending.','response':'Changed upstream body/feet solution, rebound heads/necks/clothes, inspected frame evidence and queued Director AV separately.','result':'resolved'}],'adjacent_regressions':'708 protected objects unchanged; all-frame cuff/prop/gaze checks and six-control reopen evidence remain distinct from motion acceptance.','stopping_reason':'Only the scoped manual Director AV stage under313; no production pass or new release authority.'}
    for name,value in [('final-task',task),('final-packet',packet),('knowledge-review',review),('knowledge-gate',pk.check_review(ROOT,packet,review))]:(dest/(name+'.json')).write_text(json.dumps(value,indent=2))
    (dest/'final-packet.md').write_text(pk.packet_markdown(packet))
    print(json.dumps({'queue':str(dest/'DIRECTOR_AV_QUEUE.json'),'replay':replay['status'],'strict_gate':pk.check_review(ROOT,packet,review)['ready_for_review']}))
if __name__=='__main__':main()
