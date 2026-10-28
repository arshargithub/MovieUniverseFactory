"""400counterexamples + legitimate controls. All fixtures synthetic/offline."""
import copy,json,sqlite3
import pytest
from movie_factory import production_contracts as pc, production_governance as g
from movie_factory import production_knowledge as pk, production_workflow as wf
from test_production_workflow import setup,start,submit,build,review,bind
from governance_fixtures397 import attach,checks
from test_governance397 import ledger,state,fail_cycles


def children():
 return [dict(id='target',question='Is target convincing?',acceptance='Matched target form',depends_on=[],proof_kind='target_form',criteria=['appearance'],operation_ids=['proof','build']),
         dict(id='binding',question='Does form survive?',acceptance='Matched raised pose',depends_on=['target'],proof_kind='pose_form',criteria=['appearance'],operation_ids=['deform'])]


def split(b):
 d=b['production_contract397'];d['scope'].update(decision='split',children=children(),current_child='target')
 d['operations'][-1]['produces']=['target_form']
 return d


def metric(root,c):
 c.update(kind='measurement',metric_key='crossings',comparator='eq',threshold=0)
 for name,value in [('calibration',0),('negative_control',3)]:
  candidate=dict(version=name,artifacts={'source':bind(root,'evidence.jpg')})
  measurement=dict(candidate_digest=pk.digest(candidate),cell=c['cells'][0],coordinate_space=c['coordinate_space'],profile=c['profile'],crossings=value)
  (root/(name+'-measurement.json')).write_text(json.dumps(measurement))
  record=dict(schema=1,purpose=name,conditions=pc.metric_conditions(c),applicability='Synthetic bounded fixture, not real anatomy calibration',control=dict(cell=c['cells'][0],candidate=candidate,measurement=bind(root,name+'-measurement.json')))
  (root/(name+'.json')).write_text(json.dumps(record));c[name]=bind(root,name+'.json')


def test_public_scope_decision_must_match_diagnostic(setup):
 root,c,b,_=setup;start(setup);attach(root,c,b);d=b['production_contract397']
 value=dict(task='t',decision='split',diagnostic=d['scope'],effect_counts={'appearance':0,'temporal':0},next_operation='proof',next_operation_binding=d['operations'][0])
 with pytest.raises(wf.Blocked,match='DECISION_CONTRADICTION'):c.governance('t','scope_review',value,'bad-split')
 assert c.governance_status('t')['spent']==0
 value['decision']='keep';c.governance('t','scope_review',value,'good-keep')


@pytest.mark.parametrize('fault',['missing_child_fields','wrong_operations','wrong_kind','missing_target','wrong_child_digest'])
def test_split_negative_contracts(setup,fault):
 root,c,b,_=setup;start(setup);attach(root,c,b);d=split(b)
 if fault=='missing_child_fields':d['scope']['children'][0].pop('operation_ids')
 if fault=='wrong_operations':d['scope']['children'][0]['operation_ids']=['imaginary']
 if fault=='wrong_kind':d['operations'][-1]['produces']=['transport']
 if fault in {'missing_target','wrong_child_digest'}:
  d['scope']['current_child']='binding';d['scope']['first_operation']='deform';d['operations']=[dict(id='deform',**{'class':'fit'},requires=['target_form'],produces=['pose_form'],prerequisite_steps=[],recipe=None)]
  d['input_proofs']=[dict(id='fabricated',child='target',kind='target_form',conditions={'child':'target','child_digest':'wrong' if fault=='wrong_child_digest' else pk.digest(children()[0])})] if fault=='wrong_child_digest' else [dict(kind='target_form')]
 with pytest.raises((wf.Blocked,KeyError)):pc.validate(root,b)


def test_controller_admits_eligible_split_and_blocks_fictitious_predecessor(setup):
 root,c,b,_=setup;start(setup);attach(root,c,b);d=split(b)
 c.replan('t','STRATEGIZING','Bound target-first micro-proof','split-replan');submit(c,'t',b,'split-admit')
 assert c.state('t')['stage']=='EXECUTING'
 # A syntactically consistent child claim must still exist canonically.
 bad=copy.deepcopy(b);bd=bad['production_contract397'];bd['scope']['current_child']='binding';bd['scope']['first_operation']='deform'
 bd['operations']=[dict(id='deform',**{'class':'fit'},requires=['target_form'],produces=['pose_form'],prerequisite_steps=[],recipe=None)]
 bd['input_proofs']=[dict(id='nonexistent',kind='target_form',child='target',conditions=dict(child='target',child_digest=pk.digest(children()[0]),child_criteria_digest=pc.child_criteria_digest(bd,children()[0]),child_reference_digest=pc.child_reference_digest(bd,children()[0],{r['id']:r for r in bad['references']}),proof_kind='target_form'),artifact=bind(root,'candidate.bin'),consumer_steps=['deform'])]
 pc.validate(root,bad)
 with c.connect() as con:
  with pytest.raises(wf.Blocked,match='UNKNOWN_INPUT_PROOF'):g.validate_plan(con,c.state('t'),bad,root)


@pytest.mark.parametrize('fault',['string','missing','stale','space','threshold','negative_pass','positive_fail','source_drift','nonfinite'])
def test_numeric_provenance_blocks_invalid_calibration(setup,fault):
 root,c,b,_=setup;start(setup);attach(root,c,b);crit=b['production_contract397']['criteria'][0];metric(root,crit)
 if fault=='string':crit['calibration']='nonexistent.json'
 elif fault=='missing':crit['calibration']['path']='missing.json'
 elif fault=='stale':(root/'calibration.json').write_text('{}')
 elif fault in {'space','threshold'}:
  p=root/'calibration.json';v=json.loads(p.read_text());v['conditions']['coordinate_space' if fault=='space' else 'threshold']='wrong';p.write_text(json.dumps(v));crit['calibration']=bind(root,'calibration.json')
 else:
  name='negative_control' if fault=='negative_pass' else 'calibration'
  p=root/(name+'-measurement.json');v=json.loads(p.read_text());v['crossings']=0 if fault=='negative_pass' else float('nan') if fault=='nonfinite' else 2;p.write_text(json.dumps(v))
  q=root/(name+'.json');d=json.loads(q.read_text());d['control']['measurement']=bind(root,p.name);q.write_text(json.dumps(d));crit[name]=bind(root,q.name)
  if fault=='source_drift':(root/'evidence.jpg').write_text('Changed control source')
 with pytest.raises((ValueError,OSError)):pc.validate(root,b)


def test_controller_numeric_provenance_and_actual_measurement(setup):
 root,c,b,_=setup;b['requirements'][0]['modes']=['technical']
 import expert_fixtures as ef
 ef.attach(b);start(setup);attach(root,c,b)
 crit=b['production_contract397']['criteria'][0];metric(root,crit)
 c.replan('t','STRATEGIZING','Technical metric with bound controls','metric-replan')
 submit(c,'t',b,'metric-admit');assert c.state('t')['stage']=='EXECUTING'
 build(root,c);candidate=c.state('t')['candidate']
 (root/'actual.json').write_text(json.dumps(dict(candidate_digest=pk.digest(candidate),coordinate_space=crit['coordinate_space'],profile=crit['profile'],cell='front',crossings=3)))
 result=checks(b,review(root,c));result['evidence']['frame'].update(binding=bind(root,'actual.json'),mode='technical')
 with pytest.raises(wf.Blocked,match='VERDICT_CONTRADICTION'):submit(c,'t',result,'false-metric-pass')
 actual=json.loads((root/'actual.json').read_text());actual['crossings']=0;(root/'actual.json').write_text(json.dumps(actual));result['evidence']['frame']['binding']=bind(root,'actual.json')
 admitted=submit(c,'t',result,'real-metric-pass');assert admitted['stage']=='READY_FOR_DIRECTOR_AV'
 assert not admitted['production_approved']


def test_charged_pending_watchdog_counts_peers_and_allows_existing(ledger):
 root,con,a=ledger
 # All pending cycles are counted; no invented visual FAIL/completion.
 for i in range(10):g.reserve(con,state(cycle=i))
 p=g.task_progress(g.snapshot(con),'t');assert p['feature_age']['chest']==10 and p['completed_result_age']['chest']==0
 assert len(p['unresolved_cycles'])==10
 with pytest.raises(wf.Blocked,match='INVESTMENT_REVIEW'):g.reserve(con,state(cycle=10))
 # The already reserved tenth attempt can finish its fixed work and review.
 g.guard(con,state(cycle=9),allow_existing=True)
 g.append(con,'audit-review10','scope_review',dict(task='t',effect_counts={'chest':0},reviewed_ages=p['feature_age'],proof_stamps=p['proof_stamps']))
 for i in range(10,20):g.reserve(con,state(cycle=i))
 with pytest.raises(wf.Blocked,match='NO_PROGRESS_STOP'):g.reserve(con,state(cycle=20))
 g.guard(con,state(cycle=19),allow_existing=True)
 assert g.guard(con,state(cycle=19),operation='review')['feature_age']['chest']==20
 assert g.snapshot(con)==g.snapshot(con,full=True)


def test_new_peer_shares_investment_review_not_a_new_runway(ledger):
 root,con,a=ledger
 for i in range(10):g.reserve(con,state(cycle=i))
 p=g.task_progress(g.snapshot(con),'t')
 g.append(con,'cap-review','scope_review',dict(task='t',effect_counts={'chest':0},reviewed_ages=p['feature_age'],proof_stamps=p['proof_stamps']))
 # No new allocation: same-capability status query must retain age and review.
 g.migrate(root,con,state('peer'),'peer',dict(task='peer',state_digest=pk.digest(state('peer')),authority=a,baseline_slots=0,original_limit=100,features=['chest'],historical_age={'chest':0},history_evidence={'s':a},unknowns=[],profile=g.DEFAULTS,node='f',remaining_allocation=0))
 p=g.task_progress(g.snapshot(con),'peer');assert p['feature_age']['chest']==10
 assert p['investment_review_required']==[] and p['remaining']==0


def test_bridge_records_child_form_proof_from_actual_reviewed_output(setup,monkeypatch):
 from test_native_handler333 import prepare,run
 from test_task_router332 import step_review
 from movie_factory import native_admission as na
 root,c,bridge,calls=prepare(setup,monkeypatch)
 b=copy.deepcopy(c.state('t')['brief']);d=split(b)
 c.replan('t','STRATEGIZING','Split target proof before child binding','split-native-replan')
 # Preserve actual native recipe bindings in each planning step.
 import planning_fixtures as pf
 while c.state('t')['stage']=='BRIEFING':
  packet=c.packet('t');response=pf.result(packet,b)
  if packet['planning_step']=='STRATEGIZING':
   for step,name in zip(response['artifact']['steps'],['save.json','render.json']):step['native_recipe']=bind(root,name)
  c.submit('t',packet['actor'],packet['ticket'],response,'native-split-'+packet['planning_step'])
 saved=run(root,bridge);step_review(bridge,saved)
 rendered=run(root,bridge,'build',saved['artifacts']['native'])
 candidate=dict(version=rendered['id'],artifacts=rendered['artifacts'])
 sub=dict(criteria=['appearance'],feature='appearance',proof_kind='target_form',conditions={'profile':'fixture'},
  contract_checks397=[dict(id='appearance',status='PASS',observation='Synthetic matched frame',cells=[dict(id='front',status='PASS',evidence=['frame'])])],
  evidence={'frame':dict(binding=rendered['artifacts']['frame'],candidate_digest=pk.digest(candidate),mode='image')})
 verdict=dict(verdict='PASS',observation='Synthetic target inspected',comparison='Synthetic expected target',open_defects=[],evidence=rendered['artifacts'],run_digest=pk.digest(rendered),proof_kinds397=['target_form'],subproofs397=[sub])
 bad=copy.deepcopy(verdict);bad['subproofs397'][0]['criteria']=['temporal']
 with pytest.raises((ValueError,KeyError)):bridge.record_review('t','build',bad)
 bridge.record_review('t','build',verdict)
 with c.connect() as con:
  proof=g.snapshot(con)['proofs'][rendered['id']+':0']
 assert proof['conditions']['child']=='target'
 assert proof['conditions']['child_digest']==pk.digest(children()[0])
 # Use that exact canonical child proof as the next child's input (validation
 # only; new native work is not dispatched or given extra fixture allowance).
 next_b=copy.deepcopy(b);nd=next_b['production_contract397'];nd['scope']['current_child']='binding';nd['scope']['first_operation']='deform'
 nd['operations']=[dict(id='deform',**{'class':'fit'},requires=['target_form'],produces=['pose_form'],prerequisite_steps=[],recipe=None)]
 nd['input_proofs']=[dict(id=proof['id'],kind='target_form',child='target',conditions=proof['conditions'],artifact=proof['evidence']['source_native'],consumer_steps=['deform'])]
 pc.validate(root,next_b)
 wrong_reference=copy.deepcopy(next_b);wrong_reference['references'][0]['fidelity']='Different motion authority'
 with pytest.raises(wf.Blocked,match='CHILD_PREREQUISITE_UNQUALIFIED'):pc.validate(root,wrong_reference)
 with c.connect() as con:g.validate_plan(con,c.state('t'),next_b,root)
 pc.native_operation(root,{'brief':next_b},'deform',{'edits':[]},{},{},parent=proof['evidence']['source_native'])
 with pytest.raises(wf.Blocked,match='NATIVE_SOURCE_MISMATCH'):
  pc.native_operation(root,{'brief':next_b},'deform',{'edits':[]},{},{},parent=bind(root,'parent.blend'))
 # Stale consumed evidence fails without a silent requalification.
 (root/proof['evidence']['frame']['path']).write_bytes(b'changed')
 with c.connect() as con:
  with pytest.raises(ValueError):g.validate_plan(con,c.state('t'),next_b,root)
 assert len(calls)==2


def test_scope_plan_must_apply_the_public_review_operation(setup):
 root,c,b,_=setup;start(setup);attach(root,c,b);d=b['production_contract397'];a=bind(root,'authority.md')
 review_data=dict(task='t',decision='keep',diagnostic=d['scope'],effect_counts={'appearance':0,'temporal':0},next_operation='proof',next_operation_binding=d['operations'][0])
 c.governance('t','scope_review',review_data,'review-keep')
 bad=copy.deepcopy(b);bad['production_contract397']['operations'][0]['class']='target'
 with c.connect() as con:
  with pytest.raises(wf.Blocked,match='DECISION_NOT_APPLIED'):g.validate_plan(con,c.state('t'),bad,root)


def test_original400_pending_peer_counterexample_stops_at_shared_twenty(ledger):
 root,_,a=ledger;con=sqlite3.connect(':memory:');g.install(con);con.execute('CREATE TABLE heavy_job(slot INTEGER)')
 for ident,kind,parent in [('r','release',None),('m','milestone','r'),('c','capability','m'),('f','family','c')]:
  g.define_node(root,con,ident,dict(id=ident,kind=kind,parent=parent,limit=100,purpose='Synthetic pending-peer control',authority=a))
 for i in range(21):
  task='peer'+str(i);st=state(task)
  g.migrate(root,con,st,'migrate'+task,dict(task=task,state_digest=pk.digest(st),authority=a,baseline_slots=0,original_limit=100,features=['chest'],historical_age={'chest':0},history_evidence={'source':a},unknowns=[],profile=g.DEFAULTS,node='f',remaining_allocation=1))
  if i==10:
   with pytest.raises(wf.Blocked,match='INVESTMENT_REVIEW'):g.reserve(con,st)
   diagnostic=dict(question='Does the reserved proof resolve form?',first_operation='proof',success_next='Advance qualified source',failure_next='Reject source',smaller_proof='Single target',coupling_counterexample='Connected region required',discriminator='Matched source frame',decision='keep',prerequisites=[],changes=[dict(domain='form',control='one target')],invariants=[dict(owner='director',condition='Preserve quality')],evidence={'source':a})
   g.scope_review(root,con,state('peer9'),'review-shared-investment',dict(task='peer9',decision='keep',diagnostic=diagnostic,effect_counts={'chest':0},next_operation='proof',next_operation_binding={'id':'proof'}))
  if i==20:
   with pytest.raises(wf.Blocked,match='NO_PROGRESS_STOP'):g.reserve(con,st)
  else:g.reserve(con,st)
 p=g.task_progress(g.snapshot(con),'peer20')
 assert p['feature_age']['chest']==20 and p['completed_result_age']['chest']==0
 assert len(g.snapshot(con)['cycles'])==20 and len(p['unresolved_cycles'])==20
 assert p['decision']=='STOP_AND_REALLOCATE'
 assert g.snapshot(con)==g.snapshot(con,full=True)
