from copy import deepcopy
from test_production_workflow import setup,direction,bind

def test_new_knowledge_task_path_reconciles_in_one_revision(setup):
 root,c,b,packet=setup
 c.create('t','production',bind(root,'authority.md'),'create',5,direction(b))
 old=c.state('t');(root/'next-task.json').write_text('{"unit":"next"}')
 packet['packet_digest']='knowledge-v2'
 sources=deepcopy(old['direction']['context_sources'])
 for src in sources:
  if src['binding']['path']=='task.json':src['binding']=bind(root,'next-task.json')
 newer=deepcopy(b);newer['knowledge_task']='next-task.json';newer['knowledge_digest']='knowledge-v2'
 newer['source_bindings']['next-task']=bind(root,'next-task.json')
 state=c.revise('t',newer,bind(root,'authority.md'),'Next Director unit with freshly reviewed packet','next',grounding=dict(context_sources=sources,reason='Reviewed next unit packet',evidence={'proof':bind(root,'evidence.jpg')}))
 assert state['cycle']==1 and state['max_corrections']==5
 assert state['direction']['knowledge_task']=='next-task.json'
 assert state['authority']==old['authority']
 assert state['direction']['context_sources']==sources
