"""Retrospective, main-agent-authored frozen-evidence closeout. No Blender/LLM calls.

This records the real late-admission failure; it cannot qualify prospective330
execution or silently reset the two corrections used by pose02 and pose03.
"""
import json, argparse
from pathlib import Path
from movie_factory import production_knowledge as pk
from movie_factory import production_workflow as wf
from movie_factory import planning_pipeline as pp
from movie_factory import expert_planning as ep

ROOT = Path(__file__).resolve().parents[1]
BASE = '.runtime/art-direction/series01-sikh331/pose-03'
REQS = [
 ('P1', 'preparation', 'Gather through neck/poll, chest, pelvis and supported limbs, not detached foot gestures.', ['story_performance','animation_physics','anatomy_contact'], 'motion'),
 ('P2', 'crest', 'Articulated active balance with compact unequal forelimbs, plausible hind support and coupled rider.', ['story_performance','camera_editorial','animation_physics','anatomy_contact'], 'motion'),
 ('P3', 'landing', 'Reach, contact, whole-body absorption and coherent seat/rein/stirrup/earth response.', ['animation_physics','anatomy_contact','effects_environment'], 'motion'),
 ('P4', 'appearance', 'Leader, horse and tack belong beside accepted Pashtun: no shell clothing, cap crown or polished statue coat.', ['story_performance','anatomy_contact','production_reuse'], 'film'),
 ('P5', 'crowd', 'Purposeful supported clearance with differentiated body orientation, continuous rider attention and credible near actors.', ['story_performance','camera_editorial','animation_physics','anatomy_contact','production_reuse'], 'direction'),
 ('P6', 'continuity', 'Contiguous252–441 with one-second handles, coherent exchange and technical/source integrity.', ['camera_editorial','effects_environment','production_reuse'], 'direction'),
 ('P7', 'admission', 'Original stages precede native dispatch; shared correction bounds and exact recipe/protected-source evidence survive.', ['production_reuse'], 'direction'),
 ('AV', 'continuity', 'Director alone judges full-speed feel, impact/neigh sound, emotional effect and acceptance.', ['story_performance','sound_music'], 'direction'),
]
OBS = {
 'P1': ('FAIL', '298 still presents a long relatively straight neck; pelvis/chest do not gather as a compact whole.', 'Reference15.9s has conspicuous neck curl and coordinated preparation.'),
 'P2': ('FAIL', '327 forefeet point down and head flex improves, but support remains extended and forelimb folding abrupt.', 'Reference17.3s has a compact articulated balance; a better hoof orientation does not qualify that silhouette.'),
 'P3': ('NOT_RUN', '350/353 lower the body/head; transition interiors and rebuilt dependent contact caches are incomplete.', 'Sampled compression cannot qualify momentum, contact and distributed recovery.'),
 'P4': ('FAIL', '298/327/353 retain a smooth torso shell, cap crown, regular beard, tube lower garments and polished coat.', 'Accepted Pashtun establishes rich layered forms at readable framing; dark lighting is not a quality waiver.'),
 'P5': ('NOT_RUN', 'No representative near-warrior proof or propagation completed.', 'The one-actor prerequisite failed; inherited rejected crowd is not a new pass.'),
 'P6': ('NOT_RUN', 'Six phase renders only; no continuous clip, reverse controls or fresh-open comparison.', 'The agreed deliverable is the entire contiguous passage, not selected images.'),
 'P7': ('FAIL', 'Native construction preceded actual stage submission; first two recipe snapshots and some transitive bindings are missing.', 'Written strategy is not an enforced staged workflow; later replay cannot repair chronology.'),
 'AV': ('NOT_RUN', 'No direct playback/listening claim or Director queue.', 'Visible failures cannot be delegated to the Director AV exception.'),
}

def binding(path):
    return {'path': path, 'sha256': pk.file_hash(ROOT / path)}

def write(path, obj):
    path.write_text(json.dumps(obj, indent=2) + '\n')

def run(relative):
    OUT=ROOT/relative
    if not OUT.resolve().is_relative_to(ROOT/'results/sikh331'):
        raise ValueError('Use results/sikh331 output')
    OUT.mkdir(parents=True, exist_ok=False)
    task = json.loads((ROOT/'results/sikh331/pose-03/task.json').read_text())
    paths = ['results/sikh331/PROOF_AUDIT.md', 'results/workflow330/NIHANG_PROSPECTIVE_BRIEF.md', BASE+'/sequence.blend', BASE+'/pose-evidence.json', BASE+'/worker.log', BASE+'/receipt.json']
    paths += [BASE+f'/frames/frame-{f:04d}.png' for f in (298,314,327,344,350,353)]
    task.update(id='sikh331-frozen-closeout', phase='planning', intent='Retrospective failure adjudication, not new construction authority', inputs={p:binding(p)['sha256'] for p in paths})
    write(OUT/'task.json', task)
    knowledge = pk.task_packet(ROOT, task)
    assert knowledge['dispatch_ready'], knowledge['blockers']
    write(OUT/'knowledge.json', knowledge)
    (OUT/'knowledge.md').write_text(pk.packet_markdown(knowledge))
    source_specs = [
      ('direction','direction','results/workflow330/NIHANG_PROSPECTIVE_BRIEF.md',1,36,'adopted','Preserve the original whole-pose and same-film goal; no reduced target.'),
      ('learnings','learnings','docs/knowledge/PLANNING_PIPELINE_330.md',1,40,'adopted','Written phases and complete schemas do not make native execution enforced.'),
      ('film','film_language','docs/planning/SERIES_01_ART_DIRECTION_C.md',1,13,'adopted','Use rich illustrated forms and weighty larger-than-life action, not primitive proxies.'),
      ('preferences','director_preferences','docs/planning/PLANNING_SUBSTAGES_329.md',8,42,'historical','330 adopted serial phases; no routine technical approval or isolated specialist org chart.'),
      ('references','references','docs/knowledge/NIHANG_REARING_REVIEW_FAILURE_321.md',7,30,'adopted','Reference action governs complete shape and phase relationships, not just total duration.'),
      ('controls','controls','docs/knowledge/NIHANG_REARING_REVIEW_FAILURE_321.md',32,57,'adopted','Rejected320 is a failure control; look and judgment failures are already documented.'),
      ('constraints','constraints','results/sikh331/PROOF_AUDIT.md',1,34,'adopted','This record is retrospective; two corrective variants consumed. No new allowance or AV judgment.'),
      ('task','constraints',relative+'/task.json',1,17,'adopted','Frozen native/evidence bytes only, fresh domain obligations, no rendering.'),
    ]
    sources=[dict(id=i,category=c,binding=binding(p),lines=[a,z],status=s,required=True,statement=why,scope='Retrospective frozen-evidence closeout; original authority retained') for i,c,p,a,z,s,why in source_specs]
    requirements=[dict(id=r,criterion=text,modes=['direct_motion','direct_audio'] if r=='AV' else ['technical'] if r=='P7' else ['image'],director_av=r=='AV') for r,b,text,l,ref in REQS]
    refs=[]
    for rid,path,role,ids,scope in [
      ('motion','.runtime/art-direction/series01-sikh256/references/reference-b.mov','faithful_motion',['P1','P2','P3'],'Faithful gather/rear/land shape and phase relationships; edited monocular14–19s; not mocap.'),
      ('film','.runtime/art-direction/series01-sikh321/comparisons/appearance.jpg','accepted_quality',['P4'],'Only the accepted Pashtun panel sets the film floor; adjacent320 panel is rejected.'),
      ('direction','results/workflow330/NIHANG_PROSPECTIVE_BRIEF.md','directional_design',['P5','P6','P7'],'Frozen original production intent and boundaries.'),
    ]:
        ref=dict(id=rid,binding=binding(path),role=role,authority='Director authority preserved in330/321',scope=scope,fidelity=scope,allowed_variation='Unseen anatomy inferred; no literal identity or pixel matching',not_authority='No new asset rights, release, acceptance or paid calls',aspects=[dict(id='required',instruction=scope,requirements=ids)])
        if rid=='motion': ref['time_range_seconds']=[14,19]
        if rid=='direction': ref['aspects'].append(dict(id='director_av',instruction='Full-speed audiovisual judgment remains Director-owned',requirements=['AV']))
        refs.append(ref)
    methods={r:dict(beats=[beat],lenses=lenses,derivation=text,origin='reference' if ref=='motion' else 'director',priority='quality_floor',reference_ids=[ref],method='Compare exact frozen candidate evidence with original intent and reference; do not repair during review.',interfaces=['horse/rider/seat/reins/cloth' if beat!='admission' else 'native launcher/controller/source/correction counter'],early_proof=OBS[r][1],failure_condition=OBS[r][2],reopen_when='New authorized representation or candidate invalidates this frozen verdict') for r,beat,text,lenses,ref in REQS}
    intents={beat:text for r,beat,text,l,ref in REQS if r!='AV'}
    beats=[]
    for beat,intent in intents.items():
        lens_rows={}
        for lens in ep.LENSES:
            ids=[r for r,m in methods.items() if beat in m['beats'] and lens in m['lenses']]
            lens_rows[lens]=dict(applies=bool(ids),requirements=ids,why='; '.join(next(t for r,b,t,l,f in REQS if r==rid) for rid in ids) if ids else 'No separate obligation for this lens in this beat; coupled checks are assigned in the relevant other beats.')
        beats.append(dict(id=beat,audience_read=intent,framing='Actual inherited shot framing; phase images only where available',lenses=lens_rows))
    # Per-domain obligation routing, retaining broad scope/protection requirements.
    groups={'animal_coordination':['P1','P2','P3'],'anatomy':['P1','P2','P3','P4'],'crowd_support':['P5'],'look':['P4'],'construction_interfaces':['P3','P4','P5'],'motion':['P1','P2','P3'],'secondary':['P3','P6'],'render_profile':['P6'],'cache_safety':['P6','P7'],'vehicle_response':['P6'],'drainage_use':['P6']}
    km={o['id']:dict(requirements=groups.get(o['id'],['P7']),reason=o['action']+' Scope: do not reconstruct excluded scenery/vehicle; report relevant unperformed checks as NOT_RUN.') for o in knowledge['obligations']}
    brief=dict(schema=1,route='production',intent='Adjudicate331 against frozen330 goal without promoting failed diagnostics.',audience_result='No weak supporting-cast clip reaches Director review.',strategy='Freeze and reject known visible failures; distinguish prospective construction failure from retrospective controller replay.',early_proof='Exact phase and appearance comparisons veto incomplete integration.',scope='Retrospective review of pose03 and process chronology',exclusions='No authoring, rendering, model calls, crowd propagation or new correction allowance',open_decisions=[],offline_only=False,frozen_evidence_only=True,protected=['Pashtun253 unchanged','Rejected320 retained','Original330 direction unchanged'],source_bindings={s['id']:s['binding'] for s in sources},knowledge_task='results/sikh331/frozen-review/task.json',knowledge_digest=knowledge['packet_digest'],knowledge_mapping=km,requirements=requirements,capabilities={m:m not in {'direct_motion','direct_audio'} for m in wf.rc.MODES},references=refs,reference_plan={r['id']:dict(reference_digest=pk.digest(r),application=r['scope']) for r in refs})
    brief['expert_plan']=dict(version=1,beat_intents=intents,beats=beats,realizations=methods,challenge=dict(intent_coverage={b:dict(reason=t,requirements=[r for r,m in methods.items() if b in m['beats']]) for b,t in intents.items()},cross_discipline_conflicts='Improved landing pose invalidates contacts and cloth; visible support can conflict with required silhouette.',omission_probe='Late controller use is itself a failure; include original intent beyond checklist.',scope_tradeoff='Do not render crowd/full sequence after failed representative proof.',open_issues=[]))
    brief['expert_plan']['challenge']['plan_digest']=ep.plan_digest(brief)
    brief['knowledge_task']=relative+'/task.json'
    direction={k:brief[k] for k in ('intent','protected','references','knowledge_task','knowledge_digest')}
    direction.update(deliverable_id='sikh331-production-proof',beat_intents=intents,context_sources=sources)
    ids=[r['id'] for r in requirements]
    grounding=dict(uses={s['id']:dict(disposition='apply',reason=s['statement'],implication=s['statement']) for s in sources},knowledge_uses={o['id']:o['action'] for o in knowledge['obligations']},reconciliation='331 native diagnostics preceded actual stage submission; this is late closeout, never backdated qualification. AU and321 failures retained; current307 freshness failure not repinned.',unresolved=[])
    deriving=dict(requirements=requirements,beats=beats,derivations={r:{k:m[k] for k in pp.DERIVATION_FIELDS} for r,m in methods.items()},context_mapping={s['id']:dict(requirements=ids,reason=s['statement']) for s in sources},knowledge_mapping=km)
    strategizing=dict(brief=brief,method_choice=dict(chosen=brief['strategy'],alternatives='Do not label this a prospective run or use AV-pending to conceal visible failures.',evidence_status='observed',discriminating_test=brief['early_proof']),steps=[dict(id='frozen-proof',depends_on=[],requirements=ids,kind='proof',acceptance='Record supported FAIL and NOT_RUN; no new construction.')],resource_scope=brief['exclusions'],replan_triggers='Any claim of production readiness or prospective enforcement contradicts actual chronology.')
    challenge=dict(outcome='admit',checks={f:dict(status='PASS',source_ids=['constraints','direction'],observation='Admit only retrospective frozen review with zero remaining corrections.',comparison='This does not admit native authoring or reverse the observed production failure.') for f in pp.FACETS},issues=[],strongest_counterexample='A formal receipt after construction could masquerade as successful prospective enforcement; preserve explicit late chronology.')
    controller=wf.Controller(ROOT,relative+'/controller.sqlite3')
    # Zero remaining: initial pose01 + actual corrective pose02 and pose03.
    controller.create('sikh331','production',binding('results/sikh331/PROOF_AUDIT.md'),'331-closeout-create',max_corrections=0,direction=direction,mode='frozen_evidence')
    for step,artifact in zip(pp.STEPS,[grounding,deriving,strategizing,challenge]):
        packet=controller.packet('sikh331')
        result=dict(artifact,input_digest=packet['planning_input_digest']) if step=='CHALLENGING' else dict(outcome='complete',artifact=artifact,input_digest=packet['planning_input_digest'])
        write(OUT/(step.lower()+'.json'),result)
        controller.submit('sikh331',packet['actor'],packet['ticket'],result,'331-closeout-'+step)
    packet=controller.packet('sikh331');state=controller.state('sikh331')
    candidate=dict(version='331-pose03-rejected',artifacts={str(i):binding(p) for i,p in enumerate(paths)})
    result=dict(fingerprint=state['fingerprint'],candidate=candidate,reference_uses={r['id']:dict(reference_digest=pk.digest(r),application='Earlier construction used this authority but did not meet it. See331 audit; no retroactive success.') for r in refs},requirement_uses={r:dict(plan_digest=ep.plan_digest(brief),application=OBS[r][1]) for r in methods})
    controller.submit('sikh331',packet['actor'],packet['ticket'],result,'331-closeout-candidate')
    evidence={str(f):dict(binding=binding(BASE+f'/frames/frame-{f:04d}.png'),mode='image',candidate_digest=pk.digest(candidate),scope='Actual original camera, sampled frame; no temporal certification') for f in (298,314,327,344,350,353)}
    evidence['audit']=dict(binding=binding('results/sikh331/PROOF_AUDIT.md'),mode='technical',candidate_digest=pk.digest(candidate),scope='Chronology/source/known-warning record; not native validity pass')
    ev_images=['298','314','327','344','350','353']
    review=dict(fingerprint=state['fingerprint'],candidate_digest=pk.digest(candidate),evidence=evidence,checks=[dict(id=r,status=s,observation=o,comparison=c,evidence=['audit'] if r=='P7' else ev_images if s!='NOT_RUN' else []) for r,(s,o,c) in OBS.items()],reference_checks={r['id']:dict(reference_digest=pk.digest(r),observation='Known visible failures and missing integration evidence retained.',comparison=r['scope'],evidence=ev_images+['audit'],aspects=[dict(id=a['id'],status='NOT_RUN' if a['id']=='director_av' else 'FAIL',observation='No complete qualified result for this original requirement.') for a in r['aspects']]) for r in refs},audience_read='Not commanding same-film supporting cast yet.',strongest_counterexample='Improved hoof orientation and lower head coexist with the same failed broad forms.',adjacent_review='Changed spine/root invalidates old dependent contact caches; not fully requalified.',open_visible_defects=['ungathered-preparation','extended-support-shape','shell-costume','sculptural-horse'],intent_checks={b:dict(scope='supported_evidence_only',status=OBS[next(r for r,m in methods.items() if b in m['beats'])][0],observation=OBS[next(r for r,m in methods.items() if b in m['beats'])][1],comparison=t,evidence=ev_images+['audit']) for b,t in intents.items()},planning_gaps=[])
    write(OUT/'review.json',review)
    packet=controller.packet('sikh331')
    final=controller.submit('sikh331',packet['actor'],packet['ticket'],review,'331-closeout-review')
    assert final['stage']=='REPLAN_REQUIRED'
    write(OUT/'report.json',dict(stage=final['stage'],remaining_corrections=0,prior_native_attempts=3,prior_corrections=2,chronology='RETROSPECTIVE_NOT_PROSPECTIVE',native_authoring_enforced=False,independent_reviewer=False,production_ready=False,findings=final['findings']))
    print(json.dumps({'stage':final['stage'],'failures':len(final['findings']['failures']),'remaining_corrections':0,'prospective_qualification':False}))

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',default='results/sikh331/frozen-review02')
    run(p.parse_args().output)
