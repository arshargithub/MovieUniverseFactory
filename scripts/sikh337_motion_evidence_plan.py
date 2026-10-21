"""Complete missing timing evidence without discarding verified existing frames."""
import json
from pathlib import Path
from movie_factory import production_workflow as wf,production_knowledge as pk,planning_pipeline as pp,expert_planning as ep
from movie_factory.task_router import DATABASE
root=Path(__file__).resolve().parents[1];out=root/'results/sikh335/motion01'
c=wf.Controller(root,DATABASE);task='sikh335-continuous-performance'
state=c.state(task)
if state['cycle']==7:
    d=state['direction'];c.reground(task,d['context_sources'],d['knowledge_task'],d['knowledge_digest'],
      'Reviewed native camera-manifest admission change and independent appearance failure. Complete missing342–441 timing evidence on exact candidate5; retain verified252–341 historical images. No manual-only execution step; judgment belongs in review stage. No appearance or motion artistic pass.',
      'sikh337-motion-evidence-reground')
assert c.state(task)['cycle']==8
def read(name):return pk.read_json(root,'results/sikh335/motion01/'+name)
def bind(path):return {'path':path,'sha256':pk.file_hash(root/path)}
def save(name,data):
    p=out/name
    if p.exists():assert json.loads(p.read_text())==data
    else:p.write_text(json.dumps(data,indent=2)+'\n')
art={'GROUNDING':read('grounding-c3.json')['artifact'],'DERIVING':read('deriving-c5.json')['artifact'],
     'STRATEGIZING':read('strategizing-c6.json')['artifact']}
brief=art['STRATEGIZING']['brief']
for path in list(brief['source_bindings']):
    if path.startswith('src/movie_factory/adapters/blender/'):
        brief['source_bindings'][path]=bind(path)
for path in ['src/movie_factory/native_admission.py','scripts/sikh337_motion_evidence_plan.py',
             'results/sikh335/REASSESSMENT_337.md']:
    brief['source_bindings'][path]=bind(path)
for i in range(6):
    path=f'results/sikh335/motion01/clip{i:02d}-run-c6.json';run=pk.read_json(root,path)
    assert run['status']=='RETURNED'
    brief['source_bindings'][path]=bind(path)
    for name,b in run['artifacts'].items():
        if name.startswith('frame_'):
            assert pk.file_hash(root/b['path'])==b['sha256'];brief['source_bindings'][b['path']]=b
art['GROUNDING']['reconciliation']+=' Existing c6 chunks00–05 are immutable historical PNG evidence from unchanged candidate5, not current-handler qualification. Their hashes are verified. Appearance remains rejected and is not waived; remaining motion evidence proceeds independently.'
brief['strategy']='Preserve candidate5 exactly, extract342–441 with original216x384/2-sample profile, combine with hash-verified historical252–341 at24fps. No manual-only execution step. Review the complete timed evidence separately; no appearance or AV approval inferred.'
steps=[s for s in art['STRATEGIZING']['steps'] if s['id']=='preserve' or s['id'] in [f'clip{i:02d}' for i in range(6,13)]]
for step in steps:step['acceptance']='Exact unchanged native extraction and declared PNG hashes/profile only. No appearance, motion or Director AV acceptance.'
for step in steps:
    if step['id']!='preserve':step['requirements']=[r['id'] for r in brief['requirements']]
art['STRATEGIZING']['steps']=steps
brief['expert_plan']['challenge'].update(
 omission_probe='Old partial evidence alone is insufficient; all190 frames must be present and mapped. Full-speed AV remains Director-owned. Appearance defects veto integrated delivery.',
 scope_tradeoff='No redundant render of verified first90 frames; historical receipts are not relabeled current-handler passes. This completes timing evidence only.')
brief['expert_plan']['challenge']['plan_digest']=ep.plan_digest(brief)
art['STRATEGIZING']['method_choice'].update(chosen=brief['strategy'],evidence_status='hypothesis',
 discriminating_test='Exact190-frame24fps clip plus actual motion/reference review; final artistic verdict separate from extraction.')
art['STRATEGIZING']['resource_scope']='Motion correction8/max10; one unchanged save and seven serial remaining render chunks. No spend, changed animation, appearance allowance or final delivery.'
for stage in pp.STEPS[:3]:
    if pp.STEPS.index(stage)<pp.STEPS.index(c.state(task)['planning_step']):continue
    p=c.packet(task);response={'input_digest':p['planning_input_digest'],'outcome':'complete','artifact':art[stage]}
    c.submit(task,p['actor'],p['ticket'],response,'sikh337-motion-c8-'+stage);save(stage.lower()+'-c8.json',response)
p=c.packet(task);p.pop('ticket',None);save('challenge-input-c8.json',p)
print(c.state(task)['planning_step'])
