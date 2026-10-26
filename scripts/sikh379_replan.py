"""Continue the same admitted chest unit with an explicitly reviewed target."""
import argparse,copy,json
from pathlib import Path
from movie_factory import production_workflow as w,production_knowledge as p,expert_planning as ep
from movie_factory.task_router import DATABASE
a=argparse.ArgumentParser();a.add_argument('--cycle',type=int,required=True);a.add_argument('--reason',required=True);args=a.parse_args()
r=Path(__file__).resolve().parents[1];o=r/'results/sikh379';c=w.Controller(r,DATABASE);task='sikh335-supporting-appearance';s=c.state(task);cy=args.cycle
assert cy==s['cycle']+1 and cy<=146
def bind(q):return dict(path=q,sha256=p.file_hash(r/q))
def write(name,v):
 q=o/name;text=json.dumps(v,indent=2)+'\n'
 if q.exists():assert q.read_text()==text, name
 else:q.write_text(text)
 return bind(str(q.relative_to(r)))
prior=s['cycle'];b=copy.deepcopy(s['brief']);src=copy.deepcopy(s['direction']['context_sources']);cfg=p.read_json(r,f'results/sikh379/appearance-c{prior}.json')
new=[f'.runtime/art-direction/sikh379-targets/c{cy}.npz',f'.runtime/art-direction/sikh379-targets/c{cy}.json',f'results/sikh379/REJECT{prior}.md','scripts/sikh379_replan.py','src/movie_factory/horse_shape379.py','scripts/sikh379_targets.py','tests/test_horse_shape379.py','src/movie_factory/adapters/blender/nihang_chest379.py']
if cy>=140:new+=['src/movie_factory/retrospective.py','tests/test_retro_packet379.py','results/sikh379/PACKET_REPAIR_STRATEGY.md','results/sikh379/PACKET_DEDUP_CONTROL.json']
if cy>=143:new+=['results/sikh379/CAGE_REASSESSMENT142.md','results/sikh379/REST_REASSESSMENT141.md']
for q in new:b['source_bindings'][q]=bind(q)
t=p.read_json(r,f'results/sikh379/task{prior}.json');t['id']=f'sikh379-native{cy}';t['inputs'].update({q:p.file_hash(r/q) for q in new});write(f'task{cy}.json',t);packet=p.task_packet(r,t);assert packet['dispatch_ready'],packet['blockers'];write(f'packet{cy}.json',packet)
b.update(knowledge_task=f'results/sikh379/task{cy}.json',knowledge_digest=packet['packet_digest'])
for row in src:
 if row['id']=='controls':row['binding']=bind(f'results/sikh379/task{cy}.json')
 b['source_bindings'][row['id']]=row['binding']
b['source_bindings'][f'results/sikh379/task{cy}.json']=bind(f'results/sikh379/task{cy}.json')
b['expert_plan']['realizations']['form']['derivation']=args.reason+' Qualified gross physical references retained; actual posed form must pass. Fixed accepted action and all negative controls stay binding.'
b['expert_plan']['challenge']['plan_digest']=ep.plan_digest(b);write(f'revised{cy}-brief.json',b)
cage=p.read_json(r,f'.runtime/art-direction/sikh379-targets/c{cy}.json')['config'].get('body_cage',False)
cfg.update(brief_path=f'results/sikh379/revised{cy}-brief.json',cause=args.reason,method=('379 body-supported pectoral cage fitted to original dorsal thorax, local ARAP connection to moving limb interfaces; raw shape is hypothesis and real photos govern anatomy.' if cage else '379 local shape-preserving ARAP from qualified positive contours; target parameters in bound data report.')+' No primary skeleton/action change or general-rig claim.',reconciliation='Same original task137..146, retained references/failures/limits; changed data and snapshotclock reviewed, no new authority.',sources=list(dict.fromkeys(cfg['sources']+new)),retrospective_evidence=['results/sikh379/REQUEST.md','results/sikh379/STRATEGY.md','results/sikh379/REFERENCE_QUALIFICATION.md',f'results/sikh379/REJECT{prior}.md',f'.runtime/art-direction/sikh379-targets/c{cy}.json'])
cfg['steps'][0]['recipe']['edits'][0]['data']=bind(f'.runtime/art-direction/sikh379-targets/c{cy}.npz')
for step in cfg['steps'][1:]:step['recipe'].update(frame=367,frames=[367,339,333,342,283])
if cy>=140:
 byid={step['id']:step for step in cfg['steps']}
 cfg['steps']=[byid[k] for k in ['repair','front','worst','side']]
 byid['front']['depends_on']=['repair'];byid['worst']['depends_on']=['repair','front'];byid['side']['depends_on']=['repair','front','worst']
write(f'appearance-c{cy}.json',cfg)
ch=p.read_json(r,f'results/sikh379/appearance-c{prior}-challenge.json');ch['checks']['method']['observation']=args.reason+' Fixed data-only implementation/invariant checks plus actual worst-angle falsifier; no anatomy claim from ARAP.';ch['checks']['interfaces']['observation']='Primary snapshot367 matches savedsource367 to compare actual selected state; independent phase frames333339342 and standing controls remain required. Source action invariants/coat/contact still separately required.';write(f'appearance-c{cy}-challenge.json',ch)
c.revise(task,b,bind('results/sikh379/REQUEST.md'),args.reason,f'sikh379-replan{cy}',grounding=dict(context_sources=src,reason='Source-bound failure and target parameter update; reference/authority scope retained, controls task refreshed.',evidence={q:bind(q) for q in new}))
print('Same task cycle',c.state(task)['cycle'])
