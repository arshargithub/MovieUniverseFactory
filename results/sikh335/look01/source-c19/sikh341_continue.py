"""Final approved correction: neutral form repair, then conditionally its bend."""
import json
from pathlib import Path
from movie_factory import production_workflow as wf,production_knowledge as pk
from movie_factory import planning_pipeline as pp,expert_planning as ep
from movie_factory.task_router import DATABASE
r=Path(__file__).resolve().parents[1];out=r/'results/sikh335/look01'
c=wf.Controller(r,DATABASE);task='sikh335-supporting-appearance';s=c.state(task)
reason='C18 actually performed neutral native drape but front fails molded torso and ragged collar; fresh-open inactive-scene matrices also failed. Preserve all evidence. C19 repairs neutral rest ease/boundaries and evaluates source-scene state explicitly. All three neutral views must PASS before the planned single bend; no further tuning allowance.'
if s['cycle']==18:
 d=s['direction'];c.reground(task,d['context_sources'],d['knowledge_task'],d['knowledge_digest'],reason,'sikh341-c19-reground')
assert c.state(task)['cycle']==19 and c.state(task)['max_corrections']==19
def write(name,value):
 p=out/name
 if p.exists():assert json.loads(p.read_text())==value
 else:p.write_text(json.dumps(value,indent=2)+'\n')
 return {'path':str(p.relative_to(r)),'sha256':pk.file_hash(p)}
art={x:pk.read_json(r,f'results/sikh335/look01/{x.lower()}-c18.json')['artifact'] for x in pp.STEPS[:3]}
b=art['STRATEGIZING']['brief']
for ref in b['source_bindings'].values():
 actual=pk.file_hash(r/ref['path'])
 if actual!=ref['sha256']:
  assert ref['path'].startswith(('src/movie_factory/adapters/blender/nihang_','scripts/sikh341_','tests/test_nihang341_'))
  ref['sha256']=actual
for path in ('results/sikh335/look01/rejection-c18.json','scripts/sikh341_continue.py','scripts/sikh341_save_review.py'):
 b['source_bindings'][path]={'path':path,'sha256':pk.file_hash(r/path)}
steps=[]
for name in ('save','neutral_front','neutral_back','neutral_side','bend','bend_front','bend_back','bend_side'):
 if name in ('save','bend'):
  recipe=dict(operation='nihang_patch',frame=283,width=640,height=640,samples=16,
    edits=[dict(kind='neutral_garment_proof',target='mounted leader',phase='neutral' if name=='save' else 'bend')])
 else:
  view=name.replace('bend_','neutral_')
  recipe=dict(operation='nihang_frames',frame=283,frames=[283],width=640,height=640,samples=16,view=view)
 ref=write(name+'-recipe-c19.json',recipe);b['source_bindings'][ref['path']]=ref
 dependencies=[] if name=='save' else (['save','neutral_front','neutral_back','neutral_side'] if name=='bend' else (['bend'] if name.startswith('bend_') else ['save']))
 steps.append(dict(id=name,kind='proof',depends_on=dependencies,requirements=['preservation','form','interfaces','evidence'],
  acceptance='Actual saved neutral front/back/side must have credible garment form before bend. Bend then tests shoulder/armpit/elbow/cuff; no whole-character or motion approval.',native_recipe=ref))
art['GROUNDING']['reconciliation']+=' '+reason
b['expert_plan']['realizations']['form']['method']+=' C19 bridges front torso sculpture with bounded designed rest ease and smooths cut edges before settling; initial clearance and solve displacement remain separate guards.'
b['expert_plan']['realizations']['preservation']['method']+=' Fresh snapshot explicitly evaluates owning production scene before reading its preserved objects; inactive identities cannot serve as state.'
b['expert_plan']['realizations']['interfaces']['method']+=' Bend step depends on reviewed neutral save AND all three actual neutral image runs, preventing an unreviewed neutral result from reaching bending.'
b['expert_plan']['challenge']['scope_tradeoff']='Final authorized correction19. Neutral form repair and planned bend are sequential proof steps, not two extra corrections; if either fails stop without further tuning.'
b['expert_plan']['challenge']['plan_digest']=ep.plan_digest(b)
art['STRATEGIZING']['steps']=steps
art['STRATEGIZING']['resource_scope']='Final correction19/max19. Neutral repair must pass images before one controlled bend; any new construction failure stops. No spend or motion task change.'
for stage in pp.STEPS[:3]:
 if pp.STEPS.index(stage)<pp.STEPS.index(c.state(task)['planning_step']):continue
 p=c.packet(task);response=dict(input_digest=p['planning_input_digest'],outcome='complete',artifact=art[stage])
 c.submit(task,p['actor'],p['ticket'],response,'sikh341-c19-'+stage);write(stage.lower()+'-c19.json',response)
p=c.packet(task);p.pop('ticket',None);write('challenge-input-c19.json',p)
write('source-manifest-c19.json',{str(p.relative_to(r)):pk.file_hash(p) for p in sorted((r/'src/movie_factory/adapters/blender').glob('*.py'))})
print(c.state(task)['planning_step'])
