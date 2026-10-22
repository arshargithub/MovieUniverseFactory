"""Admitted serial native operations for separately authorized corrections9–12."""
import json,sys
from pathlib import Path
from movie_factory import production_workflow as wf,production_knowledge as pk
from movie_factory.native_admission import Bridge,BLENDER_BIN
from movie_factory.task_router import DATABASE
r=Path(__file__).resolve().parents[1];out=r/'results/sikh335/look01';task='sikh335-supporting-appearance'
c=wf.Controller(r,DATABASE);s=c.state(task);cycle=s['cycle'];step=sys.argv[1]
assert 9<=cycle<=12 and s['max_corrections']==12
assert step in {'admit','save','render','leader_front','leader_reverse','crowd_front'}
if step=='admit':
    p=c.packet(task);v=pk.read_json(r,f'results/sikh335/look01/challenge-verdict-c{cycle}.json')
    v['input_digest']=p['planning_input_digest'];c.submit(task,p['actor'],p['ticket'],v,f'sikh339-c{cycle}-challenge')
    print(c.state(task)['stage'])
else:
    path='results/sikh335/motion01/save-run-c5.json' if step=='save' else f'results/sikh335/look01/save-run-c{cycle}.json'
    parent=pk.read_json(r,path)['artifacts']['native']
    recipe=next(x['native_recipe'] for x in s['planning_artifacts']['STRATEGIZING']['steps'] if x['id']==step)
    dest=out/f'{step}-run-c{cycle}.json';assert not dest.exists()
    run=Bridge(c).dispatch(task,step,f'sikh339-look-c{cycle}-{step}',parent=parent,blender_bin=BLENDER_BIN,timeout=600,recipe=recipe)
    dest.write_text(json.dumps(run,indent=2)+'\n')
    print(json.dumps({'id':run['id'],'status':run['status'],'error':run.get('error')}))
    if run['status']!='RETURNED':raise SystemExit(2)
