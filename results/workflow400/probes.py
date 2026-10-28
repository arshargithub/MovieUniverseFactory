"""Independent400 counterexamples. Isolated temporary DB/files; no production writes."""
from pathlib import Path
from tempfile import TemporaryDirectory
import sqlite3,json,copy,sys
from movie_factory import production_governance as g, production_contracts as pc, production_knowledge as pk
sys.path.insert(0,str(Path.cwd()/'tests'))
from test_production_workflow import make_brief

def bind(root,name):return dict(path=name,sha256=pk.file_hash(root/name))
def state(task='t',cycle=0):return dict(task=task,mode='offline',route='production',cycle=cycle,max_corrections=100,stage='EXECUTING')
def setup(root):
    c=sqlite3.connect(':memory:');g.install(c);c.execute('CREATE TABLE heavy_job(slot INTEGER)')
    for name in ['authority.md','reference.mov','task.json','candidate.bin','evidence.jpg']:(root/name).write_text('Synthetic audit fixture')
    a=bind(root,'authority.md')
    for ident,kind,parent in [('r','release',None),('m','milestone','r'),('c','capability','m'),('f','family','c')]:
        g.define_node(root,c,ident,dict(id=ident,kind=kind,parent=parent,limit=100,purpose='Isolated audit',authority=a))
    migrate(root,c,'t',100,a)
    return c,a

def migrate(root,c,task,allocation,a):
    s=state(task)
    g.migrate(root,c,s,'migrate-'+task,dict(task=task,state_digest=pk.digest(s),authority=a,baseline_slots=0,original_limit=100,features=['chest'],historical_age={'chest':0},history_evidence={'source':a},unknowns=[],profile=g.DEFAULTS,node='f',remaining_allocation=allocation))

def scope(a):return dict(question='Can a supported target survive the chosen test?',first_operation='proof',success_next='Use proven form',failure_next='Reject source',smaller_proof='One worst-view target',coupling_counterexample='Both foreleg roots must be visible',discriminator='Matched whole region',decision='keep',prerequisites=[],changes=[dict(domain='form',control='one target')],invariants=[dict(owner='director',condition='Preserve accepted motion')],evidence={'source':a})

def contract(root,a):
    b=make_brief(root)
    criteria=[dict(id=r['id'],critical=True,kind='judgment',anchor=r['criterion'],assessor='Director' if r['director_av'] else 'agent',coordinate_space='world',profile='matched',invalidation='Candidate change',references=['rear'],cells=['front'],human_av=r['director_av'],threshold=None,comparator=None) for r in b['requirements']]
    b['production_contract397']=dict(version=1,family='f',capability='c',criteria=criteria,feature_map={r['id']:['chest'] for r in b['requirements']},scope=scope(a),operations=[dict(id='proof',**{'class':'control'},requires=[],produces=['transport'],prerequisite_steps=[],recipe=None)])
    return b

out=[]
def note(id,expected,observed,**details):out.append(dict(id=id,expected=expected,observed=observed,conforms=expected==observed,details=details))
with TemporaryDirectory(prefix='mf-audit400-') as td:
    root=Path(td);c,a=setup(root)
    d=scope(a)
    data=dict(task='t',decision='split',diagnostic=d,effect_counts={'chest':0},next_operation='proof',next_operation_binding=dict(id='proof',**{'class':'control'},requires=[],produces=['transport'],prerequisite_steps=[],recipe=None))
    try:
        g.scope_review(root,c,state(),'contradictory-scope',data)
        b=contract(root,a);g.validate_plan(c,state(),b,root)
        observed='ADMITTED'
    except ValueError as e:observed='BLOCKED'
    note('scope_outer_split_inner_keep','BLOCKED',observed,meaning='Outer review says split, but diagnostic/next plan remains keep with no child graph')
with TemporaryDirectory(prefix='mf-audit400-') as td:
    root=Path(td);c,a=setup(root);b=contract(root,a);d=b['production_contract397']['scope'];d.update(decision='split',children=[dict(id='target',question='Is target good?',acceptance='Qualified target',depends_on=[]),dict(id='binding',question='Does target survive?',acceptance='Qualified pose',depends_on=['target'])],current_child='binding')
    try:pc.validate(root,b);observed='ADMITTED'
    except ValueError:observed='BLOCKED'
    note('split_child_without_target_or_execution_mapping','BLOCKED',observed,meaning='Current child depends on unqualified target; actual first operation produces transport only, no child mapping')
with TemporaryDirectory(prefix='mf-audit400-') as td:
    root=Path(td);c,a=setup(root);b=contract(root,a);criterion=b['production_contract397']['criteria'][0]
    criterion.update(kind='measurement',metric_key='crossings',threshold=0,comparator='eq',calibration='missing-calibration.json',negative_control='missing-negative.json')
    try:pc.validate(root,b);observed='ADMITTED'
    except ValueError:observed='BLOCKED'
    note('unbound_nonexistent_numeric_calibration','BLOCKED',observed,meaning='Only nonempty strings are required, no bound calibration/control provenance')
with TemporaryDirectory(prefix='mf-audit400-') as td:
    root=Path(td);c,a=setup(root)
    # Replace this independent fixture to allocate one cycle per canonical peer task.
    c.close();c=sqlite3.connect(':memory:');g.install(c);c.execute('CREATE TABLE heavy_job(slot INTEGER)')
    for ident,kind,parent in [('r','release',None),('m','milestone','r'),('c','capability','m'),('f','family','c')]:g.define_node(root,c,ident,dict(id=ident,kind=kind,parent=parent,limit=100,purpose='Audit charged pending cycles',authority=a))
    for i in range(21):
        t='peer'+str(i);migrate(root,c,t,1,a);g.reserve(c,state(t))
    p=g.task_progress(g.snapshot(c),'peer20')
    note('charged_pending_capability_stagnation','BLOCKED' if 21>=20 else 'ADMITTED','BLOCKED' if p['decision']=='STOP_AND_REALLOCATE' else 'ADMITTED',reserved=len(g.snapshot(c)['cycles']),completed=sum(x['completed'] for x in g.snapshot(c)['cycles'].values()),feature_age=p['feature_age'],decision=p['decision'],meaning='Twenty-one charged attempts can remain pending without any proof; watchdog ages only completed results')
print(json.dumps(out,indent=2))
Path('results/workflow400/COUNTEREXAMPLES.json').write_text(json.dumps(out,indent=2)+'\n')
# Positive and adversarial measurement controls on the actual typed reviewer.
with TemporaryDirectory(prefix='mf-audit400-') as td:
    root=Path(td);c,a=setup(root);b=contract(root,a);d=b['production_contract397'];criterion=d['criteria'][0]
    b['requirements'][0]['modes']=['technical']
    criterion.update(kind='measurement',metric_key='crossings',threshold=0,comparator='eq',calibration='unbound-calibration',negative_control='unbound-control')
    candidate={'version':'audit-measure','artifacts':{'native':bind(root,'candidate.bin')}}
    raw=dict(coordinate_space='world',profile='matched',candidate_digest=pk.digest(candidate),cell='front',crossings=3)
    (root/'measurement.json').write_text(json.dumps(raw));e=dict(binding=bind(root,'measurement.json'),candidate_digest=pk.digest(candidate),mode='technical')
    result={'contract_checks397':[dict(id='appearance',status='PASS',observation='Intentionally false scalar pass',cells=[dict(id='front',status='PASS',evidence=['measured'])])],'evidence':{'measured':e}}
    try:pc.review(root,b,candidate,result,subset=['appearance']);observed='ADMITTED'
    except ValueError:observed='BLOCKED'
    note('actual_bound_scalar_overrules_false_pass','BLOCKED',observed,raw_value=3,threshold=0)
    raw['crossings']=0;(root/'measurement.json').write_text(json.dumps(raw));result['evidence']['measured']['binding']=bind(root,'measurement.json')
    try:
        bad,missing,_=pc.review(root,b,candidate,result,subset=['appearance']);observed='ADMITTED' if not bad and not missing else 'BLOCKED'
    except ValueError:observed='BLOCKED'
    note('valid_bound_scalar_positive_control','ADMITTED',observed,raw_value=0,threshold=0)
Path('results/workflow400/COUNTEREXAMPLES.json').write_text(json.dumps(out,indent=2)+'\n')
print('All controls:',json.dumps(out[-2:],indent=2))
