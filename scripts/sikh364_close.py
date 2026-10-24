"""Close source/image evidence into the explicit313 manual AV queue, not release."""
import json
from pathlib import Path
from collections import Counter
from movie_factory import production_workflow as wf, production_knowledge as pk, retrospective as retro
from movie_factory.task_router import DATABASE

r=Path(__file__).resolve().parents[1];o=r/'results/sikh363';c=wf.Controller(r,DATABASE)
def bind(p): return dict(path=p,sha256=pk.file_hash(r/p))
def write(n,v):
    p=o/n;t=json.dumps(v,indent=2)+'\n'
    if p.exists(): assert p.read_text()==t,n
    else: p.write_text(t)
states={};history={}
for label,task in [('appearance','sikh335-supporting-appearance'),('motion','sikh335-continuous-performance')]:
    s=c.state(task);c._fresh(s)
    assert s['stage']==('READY_FOR_DIRECTOR' if label=='appearance' else 'READY_FOR_DIRECTOR_AV')
    assert s['cycle']==(123 if label=='appearance' else 42)
    wf.bindings(r,{k:v['binding'] for k,v in s['review']['evidence'].items()})
    wf.bindings(r,s['candidate']['artifacts']);wf.bindings(r,s['candidate']['derived_media'])
    findings=wf.review_result(r,s['brief'],s['candidate'],s['review'],s['fingerprint'])
    assert not findings['failures'] and not findings['missing_evidence']
    states[label]=dict(task=task,stage=s['stage'],cycle=s['cycle'],max_corrections=s['max_corrections'],candidate=s['candidate'],findings=findings,production_approved=s['production_approved'])
    with c.connect() as con: events=retro.events(con,task)
    history[label]=dict(counts=dict(Counter(e['kind'] for e in events)),projection=c.retrospective_packet(task))
with c.connect() as con: assert not con.execute('SELECT 1 FROM heavy_job').fetchone()
write('controller-close364.json',states);write('retro-close364.json',history)
jobs=[]
for p in sorted((r/'.runtime/factory-native').glob('sikh363-*/runner-status.json')):
    v=json.loads(p.read_text());jobs.append(dict(**bind(str(p.relative_to(r))),elapsed=v.get('elapsed'),exit_code=v.get('exit_code')))
write('native-timings364.json',dict(jobs=jobs,count=len(jobs),summed_process_seconds=sum(x['elapsed'] for x in jobs if isinstance(x['elapsed'],(int,float))),scope='Serial native process occupancy, overlapping active work. Not additive to work intervals or wallclock; failed/control jobs retained.'))
media=pk.read_json(r,'results/sikh363/media-manifest.json')
queue=dict(status='AWAITING_DIRECTOR_AV',production_approved=False,release_approved=False,candidate=media['video'],media_manifest=bind('results/sikh363/media-manifest.json'),source_native=bind('.runtime/factory-native/sikh363-motion-c42-save/scene.blend'),reverse_native=bind('.runtime/factory-native/sikh363-appearance-c123-save/scene.blend'),cloth=bind('results/sikh363/CLOTH121_PROOF.json'),protected_pashtun_sha256='1004ed9f2e06d2eafb008c925eb9d266e8a13b8603086020e28d19e3b606722b',protected_verification=bind('.runtime/context-hygiene/runs/sikh363-protected-hash/stdout.log'),requirements={k:dict(requirements=c.state(v['task'])['brief']['requirements'],review=bind('results/sikh363/'+k+'-review-final.json')) for k,v in states.items()},agent_checks=[bind('results/sikh363/'+p) for p in ['STATIC_REVIEW364.md','CHRONOLOGICAL_REVIEW364.md','ENCODED_REVIEW364.md','CLOCK_AND_SUPPORT364.md','controller-close364.json']],pending=['Full-speed fluidity, weight and readable preparation versus faithful reference','Brief crest and accelerating heavy landing feel','Slam-to-hoist permission and leader eyeline','Rider/horse/flag coordinated motion and overall same-film effect'],excluded=['New sound/music/listening','Unfinished principal and crowd context','Terrain and full Sikh sequence acceptance','Principal portrait or generalized horse/cloth/hand reuse','Strict global307 delivery/replay qualification','Trailer release approval'],limitations=['Same-agent fallible source/image review, not independent evaluator or direct playback.','Global context307 remains stale; not repinned or waived. Fresh scoped task packets/manual313 queue govern this handoff.','Current native assets/local commits have no new remote push, backup or restore receipt.'])
write('DIRECTOR_AV_QUEUE364.json',queue)
evidence=[bind('results/sikh363/'+p) for p in ['DIRECTOR_AV_QUEUE364.json','controller-close364.json','media-manifest.json','STATIC_REVIEW364.md','CHRONOLOGICAL_REVIEW364.md','ENCODED_REVIEW364.md','CLOCK_AND_SUPPORT364.md','CLOTH121_PROOF.json','LEARNINGS364_SUPPLEMENT.md','PROCESS_ERRORS.md']]
notes={
'construction_interfaces':'Fixed actual Basis/finger geometry and shared clock before final cloth. All consumer domains, attachments and current raised-arm reverse checked.',
'reuse_envelope':'Exact final41 pole/action/wind/121 cache and current whole-mounted camera only. New action/wind requires resimulation; no general actor or close portrait qualification.',
'animal_coordination':'Complete106 source/timed frames show preparation, body/head/limb phases and visible support/contact/absorption. Perceived real-time naturalness remains Director AV pending.',
'crowd_support':'Director explicitly defers crowd; requested context retained and identified as unfinished. No crowd propagation or clearing-motion pass.',
'authority':'Director364 ten more each applied to SAME tasks. Appearance123/max127 and motion42/max51; unused allowances retained. Sol policy360; no new spend/provider/cloud/upload/Astra.',
'strategy':'Causal controls separate interpolation mismatch from collision geometry conditioning. Preserve failed controls; conditioning actual collider faces solves original constraints instead of relaxing guard.',
'visual_gate':'All106 actual source frames, revealing reverse283/314/333, hand/chest/flag and17 decoded samples inspected. No agent direct-motion or listening claim.',
'anticipation':'Final reverse checks raised sleeve/shoulder rather than front-only fit; pin/collider subframes and face occlusion tested. Clock omission documented as planning/application failure, not retrieval success.',
'stopping':'Complete isolated unit with actual context and explicit313 full-speed queue. No incremental method checkpoint or production self-approval;4 appearance/9 motion remain.',
'versioning':'Exact final native/cache/action/source/encoded bindings verified,16 canonical314 pixel-equal. No double retime or silent cache transfer; old failed41 rigid-flag review retained.',
'economics':'One heavy local worker, bounded16 render batches; failed/control native times retained and overlap active work. Usage/cost unknown, no measured model savings or paid calls.',
'anatomy':'Actual right fist/thumb, chest Basis and corresponding shape layers, forelegs/hooves and current314 segment control inspected. Single-frame lengths are not all-frame contact proof.',
'motion':'Horse prep through300 preserved, airborne43 to21frames, source/timed arrival327/328 and absorption333; all106 frames present. Full-speed fluidity/weight remains NOT_RUN.',
'secondary':'Real Blender CLOTH solved189frames on exact final pole action. Three original bindings, both collision modes, source cache and pole digest preserved. New action/wind reopens simulation.',
'look':'Accepted Pashtun450 compared with actual intended leader/horse views; supporting material/cloth/head/coat richness assessed, not pixel match or principal portrait use.',
'render_profile':'432x768/16 retained;7 targets+canonical per batch, last1+canonical. All16 repeated314 images zero changed channels. H264106frame24fps silent encode decoded.',
'cache_safety':'Final41 clock precedes121 simulation;42/123 no-edit derivatives retain exact cache. No final source/handler changes during render/review; new clock or wind invalidates cache.',
'current_state':'Appearance READY_FOR_DIRECTOR and motion READY_FOR_DIRECTOR_AV, neither production-approved. Fresh scoped packets separate from unchanged stale global307.',
'au_deformation':'Actual reverse/partial/crest/arrival, neck/crown/arm/cuff/band/seat and chest junction checked; no known current source/frame layer failure identified.',
'au_performance':'Each correction/history retained, native availability explicitly separate from art. Same-agent technical/image checks complete; direct_motion row remains NOT_RUN.',
'au_contact':'Right fist/rein endpoint/control and actual images checked; real three cloth ties and pole vertex/edge penetration guards. Grasp error never misreported as hoof constraint.',
'au_surface':'Actual coat/cloth/skin/head/material views compared at intended framing; no statistic-only or rejected predecessor PASS. Supporting actor is not a new principal portrait.',
'au_reuse':'Exact source/reference bindings, failures and action/cache conditions retained. Upcoming crowd task must explicitly bind363+364 lessons, not assume global indexing or general cloth qualification.',
'sikh_scope':'Leader/horse isolated proof with one-second actual context. Crowd/principal/terrain/audio and full sequence remain unfinished; accepted Pashtun untouched.',
'sikh_motion':'Reference14..19s governs full gather/drive/briefcrest/reachingcontact/absorption and spear signal. Source/timed comparison complete; full-speed equivalence requires Director.'}
for label in states:
    packet=pk.read_json(r,f'results/sikh363/{label}-packet364.json')
    checks=[dict(id=x['id'],kind=x['check_kind'],status='PASS',action_taken=notes[x['id']],observation=notes[x['id']],evidence=evidence) for x in packet['obligations']]
    write(label+'-knowledge-review364.json',dict(packet_digest=packet['packet_digest'],scope='Scoped source/image/process duties and explicit313 human AV queue only; no full-speed, full-scene or production PASS.',checks=checks,hypotheses=[dict(prediction='Pins and collider agreeing at integer frames may still disagree during solver substeps.',result='resolved',observation='119 actual subframe mismatch reaches0.732m; shared world-vertex goals reduce it to3.96um but another failure remains.',response='Bind representation, interpolant and substep domain before simulation; preserve non-sole-cause finding.',evidence=evidence),dict(prediction='Long narrow collision faces can fail even when nominal cylinder surface and settings are correct.',result='resolved',observation='121 same exact cylinder with32 height rings solves189 frames, maxstrain1.23924 and original3pins/both collision modes.118-120 causal failures retained.',response='Inspect normals/conditioning and test same surface, not more stiffness or guard relaxation.',evidence=evidence),dict(prediction='Faster global playback can erase readable preparation and break contact/cache consumers.',result='resolved',observation='41 preserves prep through300 and shares inverse clock;121 is solved afterward on exact pole.106frame clip includes actual cuts and one-second handles.',response='Retime event phases/owners once, rebuild dependent cache and review complete intended passage.',evidence=evidence)],adjacent_regressions='Raised sleeve/shoulder, neck/crown/band/seat, fist/rein, chest/foreleg junction, pole/flag/face, arrival debris and cut handles checked. Unfinished context excluded; full-speed AV pending.',stopping_reason='Complete isolated106frame clip and source/image evidence are ready for explicit Director313 judgment. No known source/frame defect waived;4 appearance/9 motion corrections retained.'))
print('Current source/evidence fresh; both scoped controllers ready, manual Director AV pending; native jobs',len(jobs))
