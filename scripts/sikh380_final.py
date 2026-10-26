"""Final146 same-task rest-form correction plus gated integration, no reset."""
import json,copy
from pathlib import Path
from movie_factory import production_workflow as w,production_knowledge as p,expert_planning as ep
from movie_factory.task_router import DATABASE
r=Path(__file__).resolve().parents[1];o=r/'results/sikh380';c=w.Controller(r,DATABASE);task='sikh335-supporting-appearance';s=c.state(task);assert s['cycle']==145 and s['max_corrections']==146

def bind(q):return dict(path=q,sha256=p.file_hash(r/q))
def write(n,v):
 q=o/n;t=json.dumps(v,indent=2)+'\n'
 if q.exists():assert q.read_text()==t
 else:q.write_text(t)
b=copy.deepcopy(s['brief']);src=copy.deepcopy(s['direction']['context_sources']);cfg=p.read_json(r,'results/sikh380/appearance-c145.json');new=['scripts/sikh380_final.py','results/sikh380/REJECT145.md','results/sikh380/appearance-c145-front-review.json','src/movie_factory/adapters/blender/nihang_chest380.py','src/movie_factory/adapters/blender/nihang_patch.py','tests/test_chest380.py','.runtime/factory-native/sikh374-appearance-c124-inspect/horse-form374.npz']
for q in new:b['source_bindings'][q]=bind(q)
t=p.read_json(r,'results/sikh380/task145.json');t['id']='sikh380-native146';t['inputs'].update({q:p.file_hash(r/q) for q in new});write('task146.json',t);packet=p.task_packet(r,t);assert packet['dispatch_ready'],packet['blockers'];write('packet146.json',packet);b.update(knowledge_task='results/sikh380/task146.json',knowledge_digest=packet['packet_digest'])
for row in src:
 if row['id']=='controls':row['binding']=bind('results/sikh380/task146.json')
 b['source_bindings'][row['id']]=row['binding']
b['source_bindings']['results/sikh380/task146.json']=bind('results/sikh380/task146.json');b['work_unit']['edit_kinds'].append('mounted_horse_chest380_coat');b['work_unit']['appearance_proof']['poses']=[283,333,339,342,346,367]
cause='145 actual front rejects full-rest inflated lobes despite improved central participation. Retain live bilateral skin ownership but restore only half of historical sculpt displacement, reducing protrusion while preserving paired muscle form. One final explicit sculpt, no ARAP or action change.'
b['expert_plan']['realizations']['form']['derivation']=cause;b['expert_plan']['challenge']['plan_digest']=ep.plan_digest(b);write('revised146-brief.json',b)
cfg.update(brief_path='results/sikh380/revised146-brief.json',cause=cause,method='380 restrained rest sculpture:50percent raw/Basis delta, full bilateral pectoral/proximal-humeral ownership. Live rig preserved. After body proof, rebind existing coat roots/weights; verify contacts and continuous sampled sequence.',sources=list(dict.fromkeys(cfg['sources']+new)),retrospective_evidence=cfg['retrospective_evidence']+['results/sikh380/REJECT145.md','results/sikh380/appearance-c145-front-review.json'])
cfg['steps'][0]['recipe']['edits']=[dict(kind='mounted_horse_chest380',target='horse',restoration=.5)]
frames=[367,339,333,342,346,283]
for v in cfg['steps'][1:]:v['recipe']['frames']=frames
patch=lambda edits:dict(operation='nihang_patch',frame=367,width=432,height=768,samples=8,edits=edits)
cfg['steps'] += [dict(id='coat',depends_on=['repair','front','worst','side'],recipe=patch([dict(kind='mounted_horse_chest380_coat',target='horse')])),dict(id='contact',depends_on=['coat'],recipe=patch([dict(kind='mounted_horseform374_contact',target='horse',frames=[283,310,320,333,339,342,346,359,367])]))]
for key,view in [('coatfront','horse_form_front374'),('coatreverse','horse_form_reverse374'),('coatside','horse_form_side374')]:cfg['steps'].append(dict(id=key,depends_on=['contact'],recipe=dict(operation='nihang_frames',frame=367,frames=frames,view=view,width=640,height=640,samples=8)))
for i,lo in enumerate(range(276,367,15)):
 fs=[367]+list(range(lo,min(lo+15,367)))
 cfg['steps'].append(dict(id=f'motion{i}',depends_on=['contact','coatfront','coatreverse','coatside'],recipe=dict(operation='nihang_frames',frame=367,frames=fs,view='production',width=432,height=768,samples=8)))
write('appearance-c146.json',cfg)
ch=p.read_json(r,'results/sikh380/appearance-c145-challenge.json');ch['checks']['method']['observation']=cause+' Failed145 recorded before changing bound code. Actual whole matrix veto, no art admission from tests.';ch['checks']['interfaces']['observation']='Add actual346 to matrix, all six front/reverse/side; only then coat root+weight rebind, sampled final-surface saddle contact, all276..367 frames. No new accepted bone action.';ch['strongest_counterexample']='Half restoration may still retain paired pouches or recreate the flattened slab. If any actual pose/view fails, stop146 rather than admit incremental improvement. Coat can amplify mismatch and is checked separately.';write('appearance-c146-challenge.json',ch)
c.revise(task,b,bind('results/sikh380/SWITCH.md'),cause,'sikh380-replan146',grounding=dict(context_sources=src,reason='Actual145 failure and reviewed rest sculpt/coat implementation changes, same authority, no extra cycles.',evidence={q:bind(q) for q in new}));print(c.state(task)['cycle'])
