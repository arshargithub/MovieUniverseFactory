"""Same-task source-informed form correction; preserve original allowance/history."""
import json,copy,sys
from pathlib import Path
from movie_factory import production_workflow as wf,production_knowledge as pk,planning_pipeline as pp,expert_planning as ep
from movie_factory.task_router import DATABASE
r=Path(__file__).resolve().parents[1];o=r/'results/sikh374';c=wf.Controller(r,DATABASE);task='sikh335-supporting-appearance';s=c.state(task)
def bind(p):return dict(path=p,sha256=pk.file_hash(r/p))
def write(n,v):(o/n).write_text(json.dumps(v,indent=2)+'\n')
assert s['cycle']==124
images={}
for v in ['front','side','reverse']:
 folder=r/f'.runtime/factory-native/sikh374-appearance-c124-{v}'
 for row in json.load(open(folder/'frames.json')):images[f'{v}:{row["frame"]}']=bind(str((folder/row['file']).relative_to(r)))
record=dict(status='FAIL',observation='Actual source matrix confirms broad planar anterior torso and weak sternum/pectoral continuity; old raw mesh retains rejected lower bulge. All non-Basis correctives0 in testedposes: choose bounded positive base-form correction, not motion/skinweight patch.',images=images,diagnosis=bind('results/sikh374/DIAGNOSIS124.json'),remaining='Readonly diagnosis only; no artistic pass.')
write('SOURCE_FORM124_REVIEW.json',record)
c.retrospective(task,'outcome',dict(attempt='sikh374-source124',role='diagnostic',origin='actual-matched-source-form',observations=[dict(requirement='form',status='FAIL',observation=record['observation'])],evidence={'actual':bind('results/sikh374/SOURCE_FORM124_REVIEW.json')}),'sikh374-form124-failure')
parent='.runtime/factory-native/sikh374-appearance-c124-inspect/scene.blend';changed=['src/movie_factory/adapters/blender/nihang_patch.py'];new=['src/movie_factory/adapters/blender/nihang_sculpt374.py','tests/test_horse_sculpt374.py','results/sikh374/SOURCE_FORM124_REVIEW.json','results/sikh374/GROUNDING_RECONCILIATION.md','results/sikh374/DIAGNOSIS124.json','.runtime/context-hygiene/runs/sikh374-sculpt-tests/stdout.log',parent]
t=pk.read_json(r,'results/sikh374/task124.json');t.update(id='sikh374-horseform125')
for p in changed+new:t['inputs'][p]=pk.file_hash(r/p)
write('task125.json',t);packet=pk.task_packet(r,t);assert packet['dispatch_ready'],packet['blockers'];write('packet125.json',packet)
src=copy.deepcopy(s['direction']['context_sources'])
for x in src:
 if x['id']=='controls':x['binding']=bind('results/sikh374/task125.json')
b=copy.deepcopy(s['brief']);b.update(knowledge_task='results/sikh374/task125.json',knowledge_digest=packet['packet_digest'])
for p in changed+new:b['source_bindings'][p]=bind(p)
for x in src:b['source_bindings'][x['id']]=x['binding']
b['source_bindings']['results/sikh374/task125.json']=bind('results/sikh374/task125.json');b['work_unit']['edit_kinds']=['mounted_horseform374_inspect','mounted_horseform374_sculpt'];b['work_unit']['negative_controls'].append(dict(id='actual124',binding=bind('results/sikh374/SOURCE_FORM124_REVIEW.json'),expected='FAIL',failure=record['observation']));b['work_unit']['calibration']['actual124']=dict(verdict='FAIL',observation='Actual matched5x3 source controls show flattening; they remain the same-camera negative comparator for new form, not a positive anatomical donor.')
e=b['expert_plan'];e['challenge']['plan_digest']=ep.plan_digest(b);write('revised125-brief.json',b)
base=dict(operation='nihang_patch',frame=367,width=432,height=768,samples=8)
steps=[dict(id='sculpt',depends_on=[],recipe={**base,'edits':[dict(kind='mounted_horseform374_sculpt',target='horse',strength=1.2)]}),dict(id='inspect',depends_on=['sculpt'],recipe={**base,'edits':[dict(kind='mounted_horseform374_inspect',target='horse')]})]
for v in ['front','side','reverse']:steps.append(dict(id=v,depends_on=['inspect'],recipe=dict(operation='nihang_frames',frame=367,frames=[283,333,339,346,367],view='horse_form_'+v+'374',width=640,height=640,samples=8)))
steps.append(dict(id='intended',depends_on=['inspect','front','side','reverse'],recipe=dict(operation='nihang_frames',frame=367,frames=[283,333,339,346,367],view='horse_phase367',width=576,height=576,samples=8)))
for i,start in enumerate(range(276,368,12)):
 fs=list(range(start,min(start+12,368)));fs=sorted(set(fs+[367]));steps.append(dict(id=f'move{i:02d}',depends_on=['inspect','front','side','reverse','intended'],recipe=dict(operation='nihang_frames',frame=367,frames=fs,view='horse_phase367',width=432,height=432,samples=8)))
cfg=pk.read_json(r,'results/sikh374/appearance-c124.json');cfg.update(parent=parent,method='Actual Basis-local broad upper pectoral/central sternum/shoulder strokes, max7.5cm hard cap (predicted~4cm), no smoothing/bone/weight changes. Same delta to all key blocks; synchronize raw cage, transfer local nap, revalidate changed-region/cache separation all92acceptedframes.',proof='Sculpt guard then actual new5x3 matched views before intended-light and wholemoving proof; reject pendant pairs, flat plane, groove shelf, limb-root collapse or affected tack clearance.',cause=record['observation'],expected='Continuous rounded connected upper chest with readable sternum/shoulder transition, no hanging breast/flat plate; fixed accepted motion and unaffected seat/back.',steps=steps,sources=changed+new,retrospective_evidence=['results/sikh374/appearance-c125.json','results/sikh374/appearance-c125-challenge.json','results/sikh374/REQUEST.md','results/sikh374/STRATEGY.md','results/sikh374/SOURCE_FORM124_REVIEW.json'])
write('appearance-c125.json',cfg)
challenge=pk.read_json(r,'results/sikh374/appearance-c124-challenge.json')
for k,row in challenge['checks'].items():row['observation']+=' Current125 uses actual124 source-layer diagnosis and reviewed38-test typed positive-form handler; prospective renders may still fail.'
challenge['strongest_counterexample']='Upper chest strokes may recreate paired breasts or look like an added muscle pad; neutral matched5x3 and original-light whole view must disprove this before92-frame render. Synchronizing raw cage must preserve actual Basis and relative correctives.'
write('appearance-c125-challenge.json',challenge)
c.revise(task,b,bind('results/sikh374/REQUEST.md'),'124 diagnosis rejects flat source;125 tests bounded positive connected torsoform under same five-cycle allowance, no new motion.', 'sikh374-form125-replan',grounding=dict(context_sources=src,reason='Reviewed typed sculpt handler/38tests and actual negative source matrix; sources and task updated atomically, original authority/count retained.',evidence={'diagnosis':bind('results/sikh374/SOURCE_FORM124_REVIEW.json'),'tests':bind('.runtime/context-hygiene/runs/sikh374-sculpt-tests/stdout.log')}));print('cycle',c.state(task)['cycle'])
