"""Exact Director387 amendment, with two reviewed closure-source changes only."""
import copy,json
from pathlib import Path
from movie_factory import production_workflow as wf,production_knowledge as pk,production_allowance as pa
r=Path(__file__).resolve().parents[1];o=r/'results/sikh387';c=wf.Controller(r,'.runtime/factory-entry.sqlite3');task='sikh335-supporting-appearance'
bind=lambda p:dict(path=p,sha256=pk.file_hash(r/p))
s=c.state(task);assert (s['cycle'],s['max_corrections'])==(226,226)
sources=copy.deepcopy(s['direction']['context_sources']);b=pk.read_json(r,'results/sikh386/revised226-brief.json')
reviewed={'docs/knowledge/MICRO_APPEARANCE_WORKFLOW_386.md','scripts/sikh386_bind_source_review.py'}
# Explicit selection: full386guide already read; source excerpt retains failed-effect rule,
# while new closure covers final structural diagnosis. Superseded envelope strategy is historical.
for row in sources:
    if row['id']=='effects386':row['lines']=[65,82]
    if row['id']=='strategy386':row['lines']=[3,12]
for k,v in b['source_bindings'].items():
    if pk.file_hash(r/v['path'])!=v['sha256']:
        assert v['path'] in reviewed,v['path'];b['source_bindings'][k]=bind(v['path'])
for row in sources:
    if row['binding']['path'] in reviewed:row['binding']=bind(row['binding']['path'])
for ident,path,lines,category,statement in [
 ('director387','results/sikh387/REQUEST.md',[1,11],'direction','Director387 grants25 shared additional corrections to same structural compatibility/reconstruction task; original horse, accepted performance, no new resources.'),
 ('closure226','results/sikh386/CONTINUATION226.md',[33,39],'learnings','Previous50slots failed; no more blind masks/rigidity sweeps. Distinguish approved performance from agent-owned implementation freezes; source ownership and coupled articulation proof first.')]:
    sources.append(dict(id=ident,binding=bind(path),lines=lines,category=category,status='adopted',required=True,statement=statement,scope='387structural proof with same original task, history and artistic floor'))
for p in ['results/sikh387/REQUEST.md','results/sikh387/APPROVED_ALLOWANCE.json','scripts/sikh387_allowance.py','results/sikh386/CONTINUATION226.md','results/sikh386/EXHAUSTION226.md','results/sikh386/REVIEW_TRANSPORT_FIX226.md']:
    b['source_bindings'][p]=bind(p)
t=copy.deepcopy(pk.read_json(r,s['direction']['knowledge_task']));t.update(id='sikh387-native227',intent='Structural compatibility/reconstruction proof for original horse chest and shoulder articulation preserving Director-approved rearing performance.',inputs={v['path']:v['sha256'] for v in b['source_bindings'].values()})
(o/'task227.json').write_text(json.dumps(t,indent=2)+'\n');packet=pk.task_packet(r,t);assert packet['dispatch_ready'],packet['blockers'];(o/'packet227.json').write_text(json.dumps(packet,indent=2)+'\n')
for row in sources:
    if row['id']=='controls':row['binding']=bind('results/sikh387/task227.json')
grounding=dict(context_sources=sources,knowledge_task='results/sikh387/task227.json',knowledge_digest=packet['packet_digest'],reason='Read exact386guide final outcome appendix and repaired pure bind-review builder; only these two changed prior sources are reconciled. Reviewed packet selections shorten historical386envelope strategy and effect excerpt to accommodate actual closure findings within48KB; full mandatory guide was read and authority is retained. Preserve all original source classifications and historical failures; new387 grant supersedes exhausted quantity, not quality.',evidence={p:bind(p) for p in ['results/sikh387/REQUEST.md','results/sikh386/CONTINUATION226.md','results/sikh386/REVIEW_TRANSPORT_FIX226.md']})
pa.extend(c,task,'sikh387-allowance',bind('results/sikh387/APPROVED_ALLOWANCE.json'),'sikh387-twenty-five',grounding=grounding)
after=c.state(task);assert (after['cycle'],after['max_corrections'])==(227,251)
(o/'START_STATE.json').write_text(json.dumps({k:after[k] for k in ['task','cycle','max_corrections','stage','planning_step']},indent=2)+'\n')
print('Same task extended:227/251; fresh grounding required')
