import copy,json
from pathlib import Path
from movie_factory import production_workflow as w,production_knowledge as p,expert_planning as ep
from movie_factory.task_router import DATABASE
r=Path.cwd();o=r/'results/sikh374';c=w.Controller(r,DATABASE);task='sikh335-supporting-appearance';s=c.state(task);assert s['cycle']==127
def bind(q):return dict(path=q,sha256=p.file_hash(r/q))
def write(n,v):(o/n).write_text(json.dumps(v,indent=2)+'\n')
report=dict(status='FAIL',observation='127 proxy rejects vertex6445 at11.483465mm versus original11.483696mm: virtually unchanged cage point, falsely penalized by nearby8.67mm stroke maximum.125/126/127 proxy guards are not evidence of actual cloth intersection. Reassess method: reuse padsolve370 actual final horse/cloth surface vertex/triangle-centroid signed2mm clearance test. No cage threshold or nearest-point proxy substitutes for the required interface.',run=bind('results/sikh374/appearance-c127-sculpt-run.json'),actual=bind('.runtime/factory-native/sikh374-appearance-c127-sculpt/horse-sculpt374-failure.json'),remaining='No rendered repair yet. Last128 cycle within374 allowance; no extension/reset.')
write('METHOD_REASSESSMENT127.json',report)
c.retrospective(task,'outcome',dict(attempt='sikh374-form127',role='diagnostic',origin='proxy-method-reassessment',observations=[dict(requirement='interfaces',status='FAIL',observation=report['observation'])],evidence={'actual':bind('results/sikh374/METHOD_REASSESSMENT127.json')}),'sikh374-form127-method-fail')
new=['src/movie_factory/adapters/blender/nihang_sculpt374.py','src/movie_factory/adapters/blender/nihang_patch.py','tests/test_horse_sculpt374.py','results/sikh374/METHOD_REASSESSMENT127.json','.runtime/context-hygiene/runs/sikh374-final-surface-tests02/stdout.log']
t=p.read_json(r,'results/sikh374/task127.json');t['id']='sikh374-horseform128'
for q in new:t['inputs'][q]=p.file_hash(r/q)
write('task128.json',t);packet=p.task_packet(r,t);assert packet['dispatch_ready'],packet['blockers'];write('packet128.json',packet)
b=copy.deepcopy(s['brief']);src=copy.deepcopy(s['direction']['context_sources'])
for x in src:
 if x['id']=='controls':x['binding']=bind('results/sikh374/task128.json')
for x in src:b['source_bindings'][x['id']]=x['binding']
for q in new:b['source_bindings'][q]=bind(q)
b['source_bindings']['results/sikh374/task128.json']=bind('results/sikh374/task128.json');b.update(knowledge_task='results/sikh374/task128.json',knowledge_digest=packet['packet_digest'])
b['work_unit']['edit_kinds'].append('mounted_horseform374_contact')
rid='director_form_motion';b['requirements'].append(dict(id=rid,criterion='Director313 judges temporal coherence of corrected chest/shoulder form on exact full-speed accepted rear under new geometry; neither source invariance nor static images confers AV acceptance.',modes=['direct_motion'],director_av=True))
e=b['expert_plan'];e['realizations'][rid]=copy.deepcopy(e['realizations']['evidence']);e['realizations'][rid].update(lenses=['camera_editorial','production_reuse'],derivation=b['requirements'][-1]['criterion'])
for lens in ['camera_editorial','production_reuse']:e['beats'][0]['lenses'][lens]['requirements'].append(rid)
e['challenge']['intent_coverage']['torso']['requirements'].append(rid);e['challenge']['plan_digest']=ep.plan_digest(b);write('revised128-brief.json',b)
cfg=p.read_json(r,'results/sikh374/appearance-c127.json');cfg.update(cause=report['observation'],method='Actual Basis-local connected upper chest/sternum/shoulder sculpt; source cloth-owned domain protected including two-ring topology, relative correctives/nap synchronized, exact actions/weights/back frozen. Reuse padsolve370 actual final-surface signed2mm contact sampling, critical5poses before save and all92frames in bounded readonly batches. No arbitrary global cage-distance proxy.',sources=cfg['sources']+new,retrospective_evidence=['results/sikh374/appearance-c128.json','results/sikh374/appearance-c128-challenge.json','results/sikh374/REQUEST.md','results/sikh374/METHOD_REASSESSMENT127.json'])
steps=cfg['steps'];early=[x for x in steps if not x['id'].startswith('move')];contact_ids=[]
for i,start in enumerate(range(276,368,16)):
 key=f'contact{i:02d}';contact_ids.append(key);early.append(dict(id=key,depends_on=['inspect','front','side','reverse','intended'],recipe=dict(operation='nihang_patch',frame=367,width=432,height=768,samples=8,edits=[dict(kind='mounted_horseform374_contact',target='horse',frames=list(range(start,min(start+16,368))))])))
for x in steps:
 if x['id'].startswith('move'):x['depends_on']+=contact_ids;early.append(x)
cfg['steps']=early;write('appearance-c128.json',cfg)
ch=p.read_json(r,'results/sikh374/appearance-c127-challenge.json');ch['checks']['interfaces']['observation']='Repeated false positives require method replacement, not weaker artistic judgment. Actual final-surface gap test is reused from accepted padsolve370;5critical poses before source save, all92 integer frames in6readonly batches before moving proof. Corrected appearance judged separately.';ch['checks']['authority']['observation']='128 is final fifth124..128 cycle. No new allowance or resources; preserve actual failed history. Only completed proof or consequential blocker may hand over.';ch['strongest_counterexample']='Source-contact topology exclusion may erase the sculpt or leave a visible boundary; actual matched5x3 and intended-light views must prove positive anatomy before extended render. Final-surface vertex/centroid sampling is not continuous collision or Director temporal judgment.';write('appearance-c128-challenge.json',ch)
c.revise(task,b,bind('results/sikh374/REQUEST.md'),'127 proxy falsepositive;128 reuses accepted actual final-surface contact method and requires Director AV on exact changed-form clip. Final authorized cycle.','sikh374-replan128',grounding=dict(context_sources=src,reason='Reviewed actual127 failed proxy and existing padsolve370 final-surface implementation plus40tests. Preserve all history; no guard PASS inferred, new source/looks remain prospective.',evidence={'reassessment':bind('results/sikh374/METHOD_REASSESSMENT127.json'),'tests':bind('.runtime/context-hygiene/runs/sikh374-final-surface-tests02/stdout.log')}));print(c.state(task)['cycle'])
q=Path('scripts/sikh374_plan125.py').read_text().replace('revised125-brief.json','revised128-brief.json').replace('scripts/sikh374_plan125.py','scripts/sikh374_plan128.py');Path('scripts/sikh374_plan128.py').write_text(q)
