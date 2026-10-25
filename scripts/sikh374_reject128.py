import json
from pathlib import Path
from movie_factory import production_workflow as w,production_knowledge as p
from movie_factory.native_admission import Bridge
from movie_factory.task_router import DATABASE
r=Path.cwd();o=r/'results/sikh374';c=w.Controller(r,DATABASE);task='sikh335-supporting-appearance';s=c.state(task);assert s['cycle']==128
b=lambda q:dict(path=q,sha256=p.file_hash(r/q))
images={}
for v in ['front','side','reverse']:
 folder=r/f'.runtime/factory-native/sikh374-appearance-c128-{v}'
 for row in json.load(open(folder/'frames.json')):images[str(row['frame'])+':horse_form_'+v+'374']=b(str((folder/row['file']).relative_to(r)))
reason='FAIL:339 opposite-oblique and side expose a broad triangular skin web/shelf between neck and foreleg during descent. Upper rest-chest volume improved, but the positive connected posed anatomy remains false. Do not pass on relative improvement or numerical contact.'
checks={k:dict(status='FAIL',observation=reason+' This shared native step cannot qualify '+k+'; not a claim that protected data changed or that Director AV occurred.') for k in [x['id'] for x in s['brief']['requirements']]}
run=p.read_json(r,'results/sikh374/appearance-c128-reverse-run.json');verdict=dict(run_digest=p.digest(run),verdict='FAIL',observation=reason,comparison='Actual128 complete opposite-flank poses against positive reference-connected horse anatomy,124 source and365 flattened-form negative. Static/technical success cannot qualify moving appearance.',open_defects=['neck_chest_foreleg_skin_web339'],evidence=run['artifacts'],requirement_outcomes=checks)
Bridge(c).record_review(task,'reverse',verdict);(o/'appearance-c128-reverse-review.json').write_text(json.dumps(verdict,indent=2)+'\n')
report=dict(outcome='REJECTED_INTERNAL_NOT_READY',reason=reason,images=images,source_preservation=b('results/sikh374/SOURCE_COMPARISON128.json'),critical_contact=b('.runtime/factory-native/sikh374-appearance-c128-sculpt/horse-contact374.json'),candidate_native=b('.runtime/factory-native/sikh374-appearance-c128-inspect/scene.blend'),protected_accepted_motion=b('.runtime/factory-native/sikh373-motion-c80-contact/scene.blend'),knowledge_packet=b('results/sikh374/packet128.json'),known_defects=['neck_chest_foreleg_skin_web339','positive anatomical form not established through descent'],not_run=['intended-light controls','all92frame cache audit','new whole moving proof','Director AV queue','strict delivery'],not_run_reason='Stop expensive downstream proof on actual early appearance FAIL; do not fabricate completion or mark native plans as passed.',allowance=dict(first=124,last=128,max=128,remaining=0),causal_limits='Inactive shape keys do not eliminate a skin-weight/deformation cause. Breast/neck/shoulder ownership and posed response must be diagnosed next; no definitive bone-level cause established by these image controls.')
(o/'INTERNAL_REJECTION128.json').write_text(json.dumps(report,indent=2)+'\n')
c.replan(task,'DERIVING',reason+' Five124..128 exhausted; no new native correction without Director allowance. Re-derive phase-conditioned deformation instead of another rest-volume patch.','sikh374-rejected-form128-replan')
retro=c.retrospective_packet(task);(o/'RETRO_STATE128.json').write_text(json.dumps(retro,indent=2)+'\n')
print({k:c.state(task)[k] for k in ['stage','cycle','max_corrections']});print('retro',[(k,v['status']) for k,v in retro['gates'].items()])
