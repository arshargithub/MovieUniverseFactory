"""Final permitted planning repair: continuous evidence of unchanged candidate5."""
import json
from pathlib import Path
from movie_factory import production_workflow as wf,production_knowledge as pk,expert_planning as ep
from movie_factory.native_admission import Bridge
from movie_factory.task_router import DATABASE
root=Path(__file__).resolve().parents[1];out=root/'results/sikh335/motion01'
c=wf.Controller(root,DATABASE);task='sikh335-continuous-performance'
def bind(p):return {'path':p,'sha256':pk.file_hash(root/p)}
run=pk.read_json(root,'results/sikh335/motion01/render-run-c5.json')
v={'verdict':'FAIL','run_digest':pk.digest(run),'evidence':run['artifacts'],
   'observation':'All13 actual phase images inspected. Rider counterbalance improves crest/landing posture; hoof arrival, support and actual-contactFX remain stable. Neck segment ratios0.999920–1.000096 do not establish structural stretching. Complete timed motion is still absent, and supporting appearance remains visibly schematic.',
   'comparison':'Phase images can reject bad poses but cannot qualify the reference rhythm or transitions. Original task explicitly requires continuous evidence; this missing execution step is a planning omission, not Director approval or artistic success.',
   'open_defects':['Continuous timing evidence missing','Supporting appearance and crowd performance remain unqualified','Director full-speed AV NOT_RUN']}
if c.state(task)['cycle']==5:
    Bridge(c).record_review(task,'render',v)
    (out/'render-review-c5.json').write_text(json.dumps(v,indent=2)+'\n')
    art=json.loads(json.dumps(c.state(task)['planning_artifacts']))
    c.replan(task,'STRATEGIZING','Repair missing continuous evidence step before any motion claim. Preserve candidate5 exactly; no further pose edit. Same cumulative cycle6/max6, not a fresh task or artistic retry reset.','sikh336-continuous-evidence-replan')
else:
    assert c.state(task)['cycle']==6 and c.state(task)['planning_step']=='STRATEGIZING'
    art={'STRATEGIZING':pk.read_json(root,'results/sikh335/motion01/strategizing-c5.json')['artifact']}
brief=art['STRATEGIZING']['brief'];source=pk.read_json(root,'results/sikh335/motion01/save-run-c5.json')['artifacts']['native']
brief['source_bindings'][source['path']]=source
brief['source_bindings']['results/sikh335/motion01/render-review-c5.json']=bind('results/sikh335/motion01/render-review-c5.json')
brief['strategy']+=' Preserve candidate5 and render every source frame252–441 at24fps in serial bounded chunks; retain all source-frame/hash mappings. This is evidence completion, not another pose candidate.'
steps=[]
save={'operation':'nihang_save','frame':327,'width':216,'height':384,'samples':2}
(out/'preserve-c6-recipe.json').write_text(json.dumps(save,indent=2)+'\n')
binding=bind('results/sikh335/motion01/preserve-c6-recipe.json');brief['source_bindings'][binding['path']]=binding
steps.append({'id':'preserve','kind':'proof','depends_on':[],'requirements':['preservation'],
              'acceptance':'Selected native state/dependencies match candidate5 exactly; no animation/appearance pass.', 'native_recipe':binding})
for index,start in enumerate(range(252,442,15)):
    frames=sorted(set(range(start,min(start+15,442)))|{327})
    recipe={'operation':'nihang_frames','frame':327,'width':216,'height':384,'samples':2,'frames':frames}
    name=f'clip{index:02d}';path=f'results/sikh335/motion01/{name}-c6-recipe.json'
    (root/path).write_text(json.dumps(recipe,indent=2)+'\n');binding=bind(path);brief['source_bindings'][path]=binding
    steps.append({'id':name,'kind':'proof','depends_on':['preserve'],'requirements':['preservation','evidence'],
                  'acceptance':'Every declared frame has verified PNG/hash/profile and unchanged native dependencies. Technical extraction only; no artistic pass.', 'native_recipe':binding})
steps.append({'id':'continuous_review','kind':'proof','depends_on':[s['id'] for s in steps if s['id'].startswith('clip')],
              'requirements':[r['id'] for r in brief['requirements']],
              'acceptance':'Inspect complete timed-frame coverage against original motion/reference and larger phase controls; bind contact trajectories and interfaces. Known appearance/performance defects FAIL, direct AV stays NOT_RUN. This is a manual review step, not automatic artifact acceptance.'})
art['STRATEGIZING']['steps']=steps
art['STRATEGIZING']['method_choice'].update(chosen=brief['strategy'],discriminating_test='Complete190 frames plus verified24fps encoding. Inspect timed contact, pose trajectories and transitions; direct AV remains Director313, no known-look waiver.')
art['STRATEGIZING']['resource_scope']='Cycle6/max6: final approved planning correction adds missing continuous evidence, not a fourth changed pose. Candidate5 preserved;13 serial bounded render chunks216x384 samples2; no new spend, provider or appearance allowance.'
brief['expert_plan']['challenge'].update(plan_digest=ep.plan_digest(brief),omission_probe='A sequence of phase stills is not a motion deliverable. Complete frames must exist before admitting timed review; low-resolution footage cannot approve material/face quality.')
p=c.packet(task);result={'input_digest':p['planning_input_digest'],'outcome':'complete','artifact':art['STRATEGIZING']}
c.submit(task,p['actor'],p['ticket'],result,'sikh336-continuous-STRATEGIZING')
(out/'strategizing-c6.json').write_text(json.dumps(result,indent=2)+'\n')
p=c.packet(task);p.pop('ticket',None)
(out/'continuous-challenge-input-c6.json').write_text(json.dumps(p,indent=2)+'\n')
print(c.state(task)['planning_step'])
