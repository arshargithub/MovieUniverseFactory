import pytest
from movie_factory.budget import BudgetLedger,BudgetExceeded,BudgetError

def make(p,**kw):
 return BudgetLedger(p,100,scope_limits={'feasibility':10,'contingency':15},stage_limits={'api':(100,60)},request_limit=kw.get('request_limit',60),request_ceiling_usd=5,work_item_attempt_limit=3)

def test_global_limits_survive_other_runs_and_restart(tmp_path):
 p=tmp_path/'ledger';b=make(p,request_limit=1)
 b.reserve(run_id='one',stage='api',scope='feasibility',purpose='x',amount_usd=1)
 with pytest.raises(BudgetExceeded):make(p,request_limit=1).reserve(run_id='two',stage='api',scope='feasibility',purpose='y',amount_usd=1)

def test_retry_and_overrun_stop(tmp_path):
 b=make(tmp_path/'ledger');a=b.reserve(run_id='a',stage='api',scope='feasibility',purpose='work',amount_usd=1)
 with pytest.raises(BudgetError):b.reserve(run_id='b',stage='api',scope='feasibility',purpose='work',amount_usd=1)
 for _ in range(2):b.reserve(run_id='b',stage='api',scope='contingency',purpose='work',amount_usd=1)
 with pytest.raises(BudgetExceeded):b.reserve(run_id='c',stage='api',scope='contingency',purpose='work',amount_usd=1)
 b.settle(a,cost_usd=1.1)
 with pytest.raises(BudgetExceeded):b.reserve(run_id='a',stage='api',scope='feasibility',purpose='other',amount_usd=.1)

def test_request_ceiling(tmp_path):
 with pytest.raises(BudgetExceeded):make(tmp_path/'ledger').reserve(run_id='a',stage='api',scope='feasibility',purpose='x',amount_usd=5.01)

def test_additional_campaign_ceiling_counts_prior_and_pending(tmp_path):
 p=tmp_path/'bounded'
 original=BudgetLedger(p,100)
 r=original.reserve(run_id='old',stage='development',scope='development',amount_usd=2)
 original.settle(r,cost_usd=2)
 bounded=BudgetLedger(p,100,additional_campaign_ceiling_usd=3)
 assert bounded.summary()['effective_campaign_limit_usd']==3
 assert bounded.summary()['campaign_limit_usd']==100
 bounded.reserve(run_id='new',stage='development',scope='development',amount_usd=1)
 with pytest.raises(BudgetExceeded):
  BudgetLedger(p,100,additional_campaign_ceiling_usd=3).reserve(run_id='new',stage='development',scope='development',amount_usd=.01)
