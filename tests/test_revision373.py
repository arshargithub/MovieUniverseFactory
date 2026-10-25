from copy import deepcopy
import pytest
from test_production_workflow import setup,direction,bind
from movie_factory import production_workflow as wf

def test_atomic_direction_packet_revision_preserves_counter_and_source_authority(setup):
 root,c,b,packet=setup
 c.create('t','production',bind(root,'authority.md'),'create',5,direction(b))
 before=c.state('t');history=c.events('t');sources=deepcopy(before['direction']['context_sources'])
 g=dict(context_sources=sources,reason='New reviewed source packet with Director revision',evidence={'proof':bind(root,'evidence.jpg')})
 after=c.revise('t',b,bind(root,'authority.md'),'Director next unit','revise',grounding=g)
 assert after['cycle']==1 and after['max_corrections']==5
 assert after['direction']['context_sources']==sources
 assert c.events('t')[:len(history)]==history

@pytest.mark.parametrize('fault',['drop','promote','evidence'])
def test_atomic_revision_cannot_drop_promote_or_use_unreviewed_sources(setup,fault):
 root,c,b,packet=setup
 c.create('t','production',bind(root,'authority.md'),'create',5,direction(b));before=c.state('t')
 g=dict(context_sources=deepcopy(before['direction']['context_sources']),reason='Reviewed',evidence={'proof':bind(root,'evidence.jpg')})
 if fault=='drop':g['context_sources']=[]
 elif fault=='promote':g['context_sources'][0]['status']='provisional'
 else:g['evidence']={}
 with pytest.raises(wf.Blocked):c.revise('t',b,bind(root,'authority.md'),'Next unit','bad',grounding=g)
 assert c.state('t')==before
