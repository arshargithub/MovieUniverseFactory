"""Retain335 failed preflight and re-admit the corrected driver-name validator."""
import json,sys
from pathlib import Path
from movie_factory import production_workflow as wf, production_knowledge as pk, expert_planning as ep, planning_pipeline as pp
from movie_factory.task_router import DATABASE
root=Path(__file__).resolve().parents[1]; out=root/'results/sikh335/support01'
artistic=len(sys.argv)>1 and sys.argv[1]=='forefeet'
if artistic: out=root/'results/sikh335/support02'
c=wf.Controller(root,DATABASE); task='sikh335-supported-representation'; state=c.state(task)
art=json.loads(json.dumps(state['planning_artifacts'])); brief=art['STRATEGIZING']['brief']
for b in brief['source_bindings'].values(): b['sha256']=pk.file_hash(root/b['path'])
if artistic:
    for step in art['STRATEGIZING']['steps']:
        path='results/sikh335/support02/'+('save' if step['id']=='save' else 'render')+'-recipe.json'
        b={'path':path,'sha256':pk.file_hash(root/path)}
        brief['source_bindings'][path]=b;step['native_recipe']=b
    path='results/sikh335/support01/IMAGE_REVIEW.md'
    brief['source_bindings'][path]={'path':path,'sha256':pk.file_hash(root/path)}
brief['expert_plan']['challenge']['plan_digest']=ep.plan_digest(brief)
reason='Native preflight rejected legitimate DEF-thigh hyphen because the path whitelist omitted hyphens. No target or pose was mutated. Correct only that validated-name syntax; preserve failed run and shared correction counter.'
if artistic:
    reason='Actual crest image fails foreleg shape: hooves curl upward above carpi. Correct fixed-length sagittal joint directions and downward hoof orientation; retain supported hindquarters and closed331 failures. First335 artistic correction; controller retains the prior technical repair count too.'
authority={'path':'results/sikh335/REQUEST.md','sha256':pk.file_hash(root/'results/sikh335/REQUEST.md')}
event='sikh335-support-forefeet' if artistic else 'sikh335-support-validator-repair'
c.revise(task,brief,authority,reason,event)
for step in pp.STEPS[:3]:
    p=c.packet(task); r={'input_digest':p['planning_input_digest'],'outcome':'complete','artifact':art[step]}
    c.submit(task,p['actor'],p['ticket'],r,event+'-'+step)
p=c.packet(task);p.pop('ticket',None)
(out/'repair-challenge-input.json').write_text(json.dumps(p,indent=2)+'\n')
print(c.state(task)['planning_step'])
