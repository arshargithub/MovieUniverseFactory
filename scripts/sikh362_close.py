"""Current scoped evidence and manual review queue; no release/backup claim."""
import json,sys
from pathlib import Path
from datetime import datetime,timezone
from collections import Counter
from movie_factory import production_workflow as wf,production_knowledge as pk,retrospective as retro
from movie_factory.task_router import DATABASE
r=Path(__file__).resolve().parents[1];o=r/'results/sikh362';c=wf.Controller(r,DATABASE)
def bind(p):return dict(path=p,sha256=pk.file_hash(r/p))
def write(n,v):
 p=o/n;t=json.dumps(v,indent=2)+'\n'
 if p.exists():assert p.read_text()==t,n
 else:p.write_text(t)
states={};history={}
for label,task in [('appearance','sikh335-supporting-appearance'),('motion','sikh335-continuous-performance')]:
 s=c.state(task);assert s['stage']==('READY_FOR_DIRECTOR' if label=='appearance' else 'READY_FOR_DIRECTOR_AV')
 assert s['cycle']==(100 if label=='appearance' else 27)
 wf.bindings(r,{k:v['binding'] for k,v in s['review']['evidence'].items()});wf.bindings(r,s['candidate']['artifacts']);wf.bindings(r,s['candidate']['derived_media'])
 findings=wf.review_result(r,s['brief'],s['candidate'],s['review'],s['fingerprint']);assert not findings['failures'] and not findings['missing_evidence']
 states[label]=dict(task=task,stage=s['stage'],cycle=s['cycle'],max_corrections=s['max_corrections'],candidate=s['candidate'],findings=findings)
 with c.connect() as con:events=retro.events(con,task)
 history[label]=dict(counts=dict(Counter(e['kind'] for e in events)),projection=c.retrospective_packet(task))
with c.connect() as con:assert not con.execute('SELECT 1 FROM heavy_job').fetchone()
write('controller-close.json',states);write('retro-close.json',history)
jobs=[]
for p in sorted((r/'.runtime/factory-native').glob('sikh362-*/runner-status.json')):
 v=json.loads(p.read_text());jobs.append(dict(**bind(str(p.relative_to(r))),elapsed=v.get('elapsed'),exit_code=v.get('exit_code')))
write('native-timings.json',dict(jobs=jobs,count=len(jobs),summed_process_seconds=sum(x['elapsed'] for x in jobs if isinstance(x['elapsed'],(float,int))),scope='Serial native process occupancy; overlaps active work and is not additive to work intervals or total turn time.'))
media=pk.read_json(r,'results/sikh362/media-manifest.json')
queue=dict(status='AWAITING_DIRECTOR_AV',production_approved=False,release_approved=False,candidate=media['video'],media_manifest=bind('results/sikh362/media-manifest.json'),source_native=bind('.runtime/factory-native/sikh362-appearance-c99-save/scene.blend'),protected_pashtun_sha256='1004ed9f2e06d2eafb008c925eb9d266e8a13b8603086020e28d19e3b606722b',protected_verification=bind('.runtime/context-hygiene/runs/sikh362-protected-hash/stdout.log'),requirements={k:dict(requirements=c.state(v['task'])['brief']['requirements'],review=bind('results/sikh362/'+k+'-review-final.json')) for k,v in states.items()},agent_checks=[bind('results/sikh362/'+p) for p in ['STATIC_REVIEW99.md','CHRONOLOGICAL_REVIEW.md','ENCODED_REVIEW.md','LANDING_SOURCE_CONTROL.md','controller-close.json']],pending=['Full-speed fluidity versus faithful reference','Landing weight and brief crest','Rider/horse/secondary coordination','Overall same-film supporting-shot effect'],excluded=['New sound/music or listening','Unfinished principal and crowd context','Whole Sikh sequence/terrain acceptance','Principal portrait or generalized asset reuse','Strict global307 delivery/technical replay qualification','Trailer release approval'],limitations=['Same-agent fallible review, not independent evaluator.','Source/timed images and decoding are not playback/listening.','Global context307 remains stale; not repinned or silently waived. Current scoped task packets and manual313 queue govern this handoff.','Current work and native assets are local only; no new remote backup, push or restore receipt.'])
write('DIRECTOR_AV_QUEUE.json',queue)
evidence=[bind('results/sikh362/'+p) for p in ['DIRECTOR_AV_QUEUE.json','controller-close.json','media-manifest.json','STATIC_REVIEW99.md','CHRONOLOGICAL_REVIEW.md','ENCODED_REVIEW.md','LANDING_SOURCE_CONTROL.md','LEARNINGS.md','PROCESS_ERRORS.md']]
notes={
'construction_interfaces':'98 fits both consuming skirt edges to supported waist; actual dressed front/reverse/partial poses, then all chronological source frames inspected. No shader concealment.',
'reuse_envelope':'Reuse only exact99 source and125 completed26 frames plus four27 context frames; no portable actor/crowd/closeup qualification.',
'animal_coordination':'Source and timed frames show phased head/body/limb coordination and contact/absorption. Full-speed biological naturalness remains human-pending, not PASS.',
'crowd_support':'Crowd construction explicitly deferred by Director; context frames identify unfinished crowd/principal. No propagation or crowd support/motion acceptance.',
'authority':'Original tasks retained. Appearance100/max107, motion27/max31; unused authority preserved, Sol only. No spend/provider/upload/cloud/escalation.',
'strategy':'Actual layer-domain cause and texture-range cause corrected before complete proof. Higher-profile forecast failure preserved; rebatching without quality reduction.',
'visual_gate':'Actual13 all-angle appearance controls and all129 chronological source frames inspected; encoded samples inspected. No direct-motion/audio capability fabricated.',
'anticipation':'Internal review caught crown/skin weaknesses, inherited scope omission and four-frame handle gap before handoff. Raw prior failures preserved; no measured Director-input reduction.',
'stopping':'Stop at complete scoped leader/horse image/source evidence and Director313 full-speed queue, not incremental micro-handover or production self-approval.',
'versioning':'Exact native/output/source hashes, current controller evidence and encoded manifest verified. Post-review chronology edit immediately reverted to exact reviewed hash; separate supplement retained.',
'economics':'One local worker, same original limits, no new paid calls. Native timings and operating capture retain waits/errors; tokens, subscription cost and full-turn gaps remain unknown.',
'anatomy':'Visible limb/support/seat/head/hand interfaces inspected at actual mounted framing. No new principal anatomy or universal close-grasp qualification.',
'motion':'All129 timed images available. Source14 arrival accelerates into contact through preserved actions; actual perceived speed/fluidity is explicit human NOT_RUN.',
'secondary':'Reins stay continuously owned through phases; visible cloth/groom/debris checked. Authored flexible tack is not physical rope simulation; overall moving response awaits Director.',
'look':'Actual accepted Pashtun450 comparator and99 controls inspected. Shot-specific material/layer richness read; close diagnostic face remains ineligible for principal portrait use.',
'render_profile':'432x768/16 retained. Failed oversized25 job preserved;26 max8+canonical. All16 repeated283 comparisons have zero pixel difference; no universal replay claim.',
'cache_safety':'Same99 source, actions and camera clock retained. Qualified26 source outputs reused;27 only completes actual handle. No cache/retime or consumer dependency change.',
'current_state':'Final controller READY_FOR_DIRECTOR appearance and READY_FOR_DIRECTOR_AV motion, neither production-approved; original307 capsule not silently repinned.',
'au_deformation':'Actual dressed reverse/crest/landing and phase interiors inspected for cuff/band/seat ownership; no known frame-visible tear or separation identified.',
'au_performance':'Independent source/image obligations reviewed, explicit director_motion NOT_RUN. Native availability retrospective mapping corrected append-only to NOT_TESTED.',
'au_contact':'Actual spear/hand/cuff/seat/bit-to-hand interfaces checked alongside inherited190-frame rein control. Numeric clearance alone was not used as visual proof.',
'au_surface':'Measured source luminance exposed clipping;99 material range brings skin variation back. Actual renders, not pixel statistics alone, establish current scoped appearance.',
'au_reuse':'Reference/accepted-source bindings and negative historical evidence retained. Exact media reuse only; unsupported new camera, principal or crowd use reopens review.',
'sikh_scope':'Only supporting leader/horse completed to review queue. Main Sikh is temporary, crowd next; accepted Pashtun untouched, no Gurkha work.',
'sikh_motion':'Original faithful14..19s reference constrains gather/drive/crest/reach/contact/absorption. Source/timed-phase comparison done; full-speed equivalence not claimed.'}
for label,packetpath in [('appearance','results/sikh362/appearance-knowledge-packet.json'),('motion','results/sikh361/motion-knowledge-packet.json')]:
 packet=pk.read_json(r,packetpath)
 checks=[dict(id=x['id'],kind=x['check_kind'],status='PASS',action_taken=notes[x['id']],observation=notes[x['id']],evidence=evidence) for x in packet['obligations']]
 suffix='-v2' if '--v2' in sys.argv else ''
 write(label+'-knowledge-review'+suffix+'.json',dict(packet_digest=packet['packet_digest'],scope='Scoped source/image/process duties and explicit313 human AV queue only; no full-speed or whole-scene production PASS.',checks=checks,hypotheses=[dict(prediction='Coat-only proximity can miss another garment consumer crossing the belt.',result='resolved',observation='96 actual rays identify skirt;98 actual front/reverse and continuous frames retain unbroken band.',response='Fit complete layer graph and inspect reverse/partial poses.',evidence=evidence),dict(prediction='An inherited contrast range may erase real skin texture.',result='resolved',observation='99 reduces measured source clipping from59.65percent to.86percent, actual renders reveal variation.',response='Measure colour/data domain before adding noise.',evidence=evidence),dict(prediction='Pose/event endpoint may be mistaken for editorial shot endpoint.',result='resolved',observation='Actual cut357 means last shot356, not352;27 completes through380.',response='Bind actual camera cut before assembling handles.',evidence=evidence)],adjacent_regressions='Crown/brow/layers, reverse waist/seat, hands/reins/spear, horse arrival/debris, actual cut and protected controls checked; principal/crowd/audio remain excluded and human full-speed AV pending.',stopping_reason='Integrated129-frame scoped review exists, source/image checks complete. Director313 must judge full-speed naturalness; no known source/frame defect is waived. Seven appearance and four motion corrections retained.'))
print(states['appearance']['stage'],states['motion']['stage'],'native jobs',len(jobs))
