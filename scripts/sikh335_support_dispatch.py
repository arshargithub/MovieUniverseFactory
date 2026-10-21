"""Dispatch admitted335 support proof; never use the legacy raw launcher."""
import json,sys
from pathlib import Path
from movie_factory import production_workflow as wf, production_knowledge as pk
from movie_factory.native_admission import Bridge,BLENDER_BIN
from movie_factory.task_router import DATABASE
root=Path(__file__).resolve().parents[1]; folder=sys.argv[2] if len(sys.argv)>2 else 'support01'
assert folder in {'support01','support02'}
out=root/'results/sikh335'/folder
c=wf.Controller(root,DATABASE); task='sikh335-supported-representation'; bridge=Bridge(c)
def bind(p): return {'path':p,'sha256':pk.file_hash(root/p)}
step=sys.argv[1]
cycle=c.state(task)['cycle']
if step=='save':
    p=c.packet(task); v=json.loads((out/'challenge-verdict.json').read_text());v['input_digest']=p['planning_input_digest']
    c.submit(task,p['actor'],p['ticket'],v,'sikh335-support-challenge-'+str(cycle))
    parent=bind('.runtime/art-direction/series01-sikh320/build-10/sequence.blend')
else:
    parent=json.loads((out/('save-run-c'+str(cycle)+'.json')).read_text())['artifacts']['native']
run=bridge.dispatch(task,step,'sikh335-'+folder+'-c'+str(cycle)+'-'+step,parent=parent,blender_bin=BLENDER_BIN,
    timeout=600,recipe=bind('results/sikh335/'+folder+'/'+('save' if step=='save' else 'render')+'-recipe.json'))
(out/(step+'-run-c'+str(cycle)+'.json')).write_text(json.dumps(run,indent=2)+'\n')
print(json.dumps({'id':run['id'],'status':run['status'],'error':run.get('error'),'artifacts':run.get('artifacts')},indent=2))
