import json
from copy import deepcopy
import pytest
from movie_factory import production_allowance as pa, production_workflow as wf
from test_production_workflow import setup, direction, bind


def blocked(setup):
    root,c,b,_=setup
    c.create('t','production',bind(root,'authority.md'),'create',2,direction(b))
    for n in range(3):c.replan('t','GROUNDING','Existing method correction',f'replan{n}')
    decision={'task':'t','decision':'approve_additional_corrections','additional_corrections':4,
        'prior_cycle':2,'prior_max_corrections':2,'question':'May I extend this task by four?','director_reply':'Approve four additional corrections'}
    return root,c,decision


def route(root,c,data):
    (root/'decision.json').write_text(json.dumps(data))
    b=bind(root,'decision.json')
    c.route_request('extension',{'text':'Approved extension','operations':['code'],'authority':b,
        'amendment_task':'t','rationale':'Administrative amendment; full production replanning required'})
    return b


def test_extension_retains_history_and_consumes_first_new_cycle(setup):
    root,c,data=blocked(setup);before=c.state('t');events=c.events('t');binding=route(root,c,data)
    after=pa.extend(c,'t','extension',binding,'approved-extension')
    assert after['cycle']==3 and after['max_corrections']==6
    assert after['stage']=='BRIEFING' and after['planning_step']=='GROUNDING'
    assert after['direction']==before['direction'] and after['authority']==before['authority']
    assert c.events('t')[:len(events)]==events
    assert after['planning_artifacts']=={} and len(after['allowance_history'])==1
    assert pa.extend(c,'t','extension',binding,'approved-extension')==after
    with pytest.raises(wf.Blocked):pa.extend(c,'t','extension',binding,'duplicate-event')


@pytest.mark.parametrize('change',[{'additional_corrections':True},{'additional_corrections':0},{'additional_corrections':-1},
    {'additional_corrections':21},{'prior_cycle':0},{'prior_max_corrections':3},{'task':'other'},
    {'decision':'agent_recommendation'},{'director_reply':''}])
def test_invalid_or_stale_authority_cannot_extend(setup,change):
    root,c,data=blocked(setup);data.update(change);binding=route(root,c,data)
    with pytest.raises(wf.Blocked):pa.extend(c,'t','extension',binding,'invalid')
    assert c.state('t')['cycle']==2 and c.state('t')['max_corrections']==2


def test_changed_decision_bytes_and_missing_route_block(setup):
    root,c,data=blocked(setup);binding=route(root,c,data)
    (root/'decision.json').write_text('{}')
    with pytest.raises(ValueError):pa.extend(c,'t','extension',binding,'stale')


def test_four_more_means_four_not_unlimited_or_replayable(setup):
    root,c,data=blocked(setup);binding=route(root,c,data)
    pa.extend(c,'t','extension',binding,'approved')
    for n in range(3):
        state=c.replan('t','GROUNDING','Still correcting',f'new{n}')
        assert state['cycle']==4+n
    assert c.replan('t','GROUNDING','Fourth correction failed','limit')['stage']=='REPLAN_REQUIRED'
    with pytest.raises(wf.Blocked):pa.extend(c,'t','extension',binding,'reuse-approval')
    assert c.state('t')['cycle']==6 and c.state('t')['max_corrections']==6


def test_exhausted_source_reconciliation_is_atomic_and_preserves_intent(setup):
    root,c,data=blocked(setup);before=c.state('t');binding=route(root,c,data)
    setup[3]['packet_digest']='knowledge-v2'
    with pytest.raises(wf.Blocked,match='STALE_GROUNDING_KNOWLEDGE'):
        pa.extend(c,'t','extension',binding,'stale')
    grounding=dict(context_sources=deepcopy(before['direction']['context_sources']),
        knowledge_task=before['direction']['knowledge_task'],knowledge_digest='knowledge-v2',
        reason='Reviewed source revision; original intent and references unchanged',
        evidence={'review':bind(root,'evidence.jpg')})
    result=pa.extend(c,'t','extension',binding,'reconciled',grounding=grounding)
    assert result['cycle']==3 and result['max_corrections']==6
    assert result['direction']['intent']==before['direction']['intent']
    assert result['direction']['references']==before['direction']['references']
    assert result['allowance_history'][-1]['prior_direction']==before['direction']
    assert result['planning_artifacts']=={} and result['planning_step']=='GROUNDING'


@pytest.mark.parametrize('change',['drop','promote','stale','no_evidence'])
def test_allowance_reconciliation_cannot_erase_or_promote_sources(setup,change):
    root,c,data=blocked(setup);before=c.state('t');binding=route(root,c,data)
    g=dict(context_sources=deepcopy(before['direction']['context_sources']),
        knowledge_task=before['direction']['knowledge_task'],knowledge_digest='knowledge-v1',
        reason='Reviewed reconciliation',evidence={'review':bind(root,'evidence.jpg')})
    if change=='drop': g['context_sources']=[]
    elif change=='promote': g['context_sources'][0]['status']='provisional'
    elif change=='stale': g['knowledge_digest']='stale'
    else: g['evidence']={}
    with pytest.raises((wf.Blocked,ValueError)):
        pa.extend(c,'t','extension',binding,'bad-reconciliation',grounding=g)
    assert c.state('t')==before
