import copy,json
import pytest
from movie_factory import production_governance as g, production_scorecard401 as sc
from movie_factory import production_workflow as wf
from test_governance397 import ledger,state
from test_production_workflow import setup,start,bind
from governance_fixtures397 import attach


def test_empty_unknown_is_not_zero_percent_or_forecast(ledger):
 _,con,_=ledger
 p=sc.rolling(g.history(con))
 assert p['retained_production_yield'] is None and p['charged_cycles']==0
 assert g.economics(g.snapshot(con))['qualified_release']['fraction'] is None


def test_rolling_retained_features_can_go_backwards(ledger):
 _,con,_=ledger;g.reserve(con,state(cycle=0))
 g.append(con,'positive','proof',dict(id='p',task='t',cycle=0,feature='chest',conditions={},evidence={}))
 g.finish_cycle(con,state(cycle=0),'PASS','end0')
 p=sc.rolling(g.history(con));assert p['retained_feature_delta']==1
 assert p['retained_production_yield'] is None  # Feature is not finished footage.
 g.reserve(con,state(cycle=1));g.append(con,'regression','regression',dict(task='t',feature='chest',cycle=1))
 p=sc.rolling(g.history(con),window=1)
 assert p['retained_feature_delta']==-1 and p['pending']==1
 assert p['retained_feature_losses']==[['c','chest']]


def test_weighted_yield_and_regression(ledger):
 import sqlite3
 from movie_factory import production_knowledge as pk
 root,_,a=ledger;con=sqlite3.connect(':memory:');g.install(con);con.execute('CREATE TABLE heavy_job(slot INTEGER)')
 for ident,kind,parent in [('r','release',None),('m','milestone','r'),('c','capability','m'),('f','family','c')]:
  extra=dict(weight=1) if kind in {'release','milestone'} else {}
  if kind=='milestone':extra['required_features']=['chest']
  g.define_node(root,con,ident,dict(id=ident,kind=kind,parent=parent,limit=10,purpose='Synthetic bounded weighted scope',authority=a,**extra))
 st=state();g.migrate(root,con,st,'t',dict(task='t',state_digest=pk.digest(st),authority=a,baseline_slots=0,original_limit=100,features=['chest'],historical_age={'chest':0},history_evidence={'source':a},unknowns=[],profile=g.DEFAULTS,node='f',remaining_allocation=10))
 g.reserve(con,state(cycle=0));g.append(con,'p','proof',dict(id='p',task='t',cycle=0,feature='chest',conditions={},evidence={}))
 g.milestone(root,con,'qualified',dict(node='m',proofs=['p'],authority=a))
 history=g.history(con);original=copy.deepcopy(history);assert g.replay(history)==g.replay(history);assert history==original
 p=sc.rolling(history);assert p['qualified_milestone_weight_delta']==1 and p['retained_production_yield']==1
 g.reserve(con,state(cycle=1));g.append(con,'bad','regression',dict(task='t',feature='chest',cycle=1))
 p=sc.rolling(g.history(con),window=1);assert p['qualified_milestone_weight_delta']==-1 and p['retained_production_yield']==-1


def event(ident='admin:1',status='reserved',lane='workflow_admin',**extra):
 return dict(event_id='e'+status,event_type='proxy_observed',experiment_id='engineering',name='plan_execute_review_cycle',count=1,work_cycle_id=ident,cycle_status=status,lane=lane,evidence_ref='explicit-synthetic.json',**extra)


def test_operating_cycles_not_turns_or_duplicate_production_cycles():
 events=[event(),event(status='completed'),event('native:1',lane='production')]
 p=sc.operating_observations(events,{'native:1'})
 assert p['observed_additional_cycles']==1 and p['completed_cycles']==1
 assert p['duplicate_enrolled_cycles_not_recharged']==['native:1']
 assert p['escape_rate'] is None and p['cost_per_usable_output'] is None


def test_conflicting_observed_cycle_is_visible_not_free_extra_count():
 p=sc.operating_observations([event(),event(lane='engineering')],set())
 assert p['conflicts']==['admin:1']
 assert p['observed_additional_cycles']==1


def test_source_backed_director_observations_deduplicate_and_do_not_imply_coverage():
 base=dict(event_id='e',event_type='proxy_observed',experiment_id='x',name='director_escape',count=1,item_id='defect-1',evidence_ref='human-source.md')
 p=sc.operating_observations([base,dict(base,event_id='duplicate')],set())
 assert p['known_director_escapes']==1 and p['escape_rate'] is None


def test_controller_scorecard_includes_nonproduction_observations_without_allowance(setup):
 from movie_factory.experiment_ledger import Ledger
 from pathlib import Path
 root,c,b,_=setup;start(setup);attach(root,c,b)
 ledger=Ledger(root/'.runtime/experiment-ops.sqlite3');ledger.append(dict(event('package:1'),episode_id='one',phase='design',utc='2026-10-28T00:00:00Z',evidence_ref='authority.md',evidence_binding=bind(root,'authority.md')))
 before=c.state('t');p=c.production_scorecard()
 assert p['observed_combined_cycles']==1 and p['observed_admin_share']==1
 assert p['authority_granted'] is False
 assert c.state('t')==before and c.governance_status('t')['spent']==0
 assert p['routed_operation_inventory']=={} # Only synthetic legacy registration.


@pytest.mark.parametrize('window',[0,-1,True,1.5,1001])
def test_window_must_be_bounded(ledger,window):
 with pytest.raises(ValueError):sc.rolling(g.history(ledger[1]),window=window)


def test_missing_or_stale_operating_provenance_is_visible(setup):
 root,c,b,_=setup
 e=event()
 p=sc.operating_observations([e],set(),root=root)
 assert p['observed_additional_cycles']==0 and p['unverified_observations']==[e['event_id']]
 e.update(evidence_ref='authority.md',evidence_binding=bind(root,'authority.md'))
 assert sc.operating_observations([e],set(),root=root)['observed_additional_cycles']==1
 (root/'authority.md').write_text('changed')
 assert sc.operating_observations([e],set(),root=root)['unverified_observations']


def test_legacy_governance_review_cache_recovers_sequence_from_events(ledger):
 from movie_factory import production_knowledge as pk
 _,con,_=ledger
 g.append(con,'old-review','scope_review',dict(task='t',effect_counts={'chest':0},reviewed_ages={'chest':0},proof_stamps={'chest':'historical-baseline'}))
 truth=g.snapshot(con,full=True);legacy=copy.deepcopy(truth);legacy['reviews']['t'].pop('recorded_sequence')
 con.execute('UPDATE governance_cache397 SET state=?,digest=?',(json.dumps(legacy),pk.digest(legacy)))
 count=con.execute('SELECT count(*) FROM governance_events397').fetchone()[0]
 assert g.snapshot(con)==truth
 assert con.execute('SELECT count(*) FROM governance_events397').fetchone()[0]==count


def test_rates_require_bound_complete_scope_and_known_cost(tmp_path):
 from movie_factory.production_knowledge import file_hash
 source=tmp_path/'source.md';source.write_text('Synthetic complete capture evidence')
 binding=dict(path=source.name,sha256=file_hash(source))
 rows=[]
 for name,ident in [('director_escape','defect'),('usable_output','output'),('director_handover','review')]:
  rows.append(dict(event_id=name,event_type='proxy_observed',experiment_id='x',name=name,count=1,item_id=ident,work_cycle_id='native:1',evidence_ref=source.name,evidence_binding=binding))
 record=dict(schema=1,purpose='measurement_coverage',cycle_ids=['native:1','native:2'],complete_fields=['director_escape','director_handover','usable_output'],provider_cost_usd=2.5,net_seconds=80,net_time_excludes_director_idle=True)
 path=tmp_path/'coverage.json';path.write_text(json.dumps(record));cover=dict(event_id='coverage',event_type='proxy_observed',name='measurement_coverage',evidence_ref=path.name,evidence_binding=dict(path=path.name,sha256=file_hash(path)))
 assert sc.operating_observations(rows,{'native:1','native:2'},root=tmp_path)['escape_rate'] is None
 p=sc.operating_observations(rows+[cover],{'native:1','native:2'},root=tmp_path)
 assert p['escape_rate']==.5 and p['handover_rate']==.5 and p['cost_per_usable_output']==2.5
 assert p['scoped_rates']['net_seconds_per_usable_output']==80
 record['cycle_ids'].append('unreserved');path.write_text(json.dumps(record));cover['evidence_binding']['sha256']=file_hash(path)
 p=sc.operating_observations(rows+[cover],{'native:1','native:2'},root=tmp_path)
 assert p['scoped_rates'] is None and p['conflicts']==['coverage']


@pytest.mark.parametrize('count',[True,1.0,'1',0,-1])
def test_observation_unit_count_is_strict_integer(count):
 row=event();row['count']=count
 p=sc.operating_observations([row],set())
 assert p['observed_additional_cycles']==0 and p['conflicts']
