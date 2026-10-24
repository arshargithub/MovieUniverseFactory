"""Apply explicit additional allowance plus reviewed grounding, retaining limits."""
import json,copy
from pathlib import Path
from movie_factory import production_workflow as wf,production_knowledge as pk,production_allowance as pa,planning_pipeline as pp
from movie_factory.task_router import DATABASE
r=Path(__file__).resolve().parents[1];o=r/'results/sikh368';c=wf.Controller(r,DATABASE);s=c.state('sikh335-continuous-performance');src=copy.deepcopy(s['direction']['context_sources'])
def bind(p):return dict(path=p,sha256=pk.file_hash(r/p))
for x in src:
 if x['id']=='lessons357':x['lines']=[11,14]
 if x['id']=='controls':x['binding']=bind('results/sikh368/motion-task.json')
for sid,path,statement,category,status in [('director368','results/sikh368/REQUEST.md','Single bracing hoof, deeper head/neck load and rapid head/neck/chest-led firstlift. Prep only; approve5 additional cycles.','direction','adopted'),('strategy368','results/sikh368/STRATEGY.md','Reference30fps interpretation, expert pose requirements and bounded single-brace proof strategy; old49 not accepted.','constraints','hypothesis')]:
 src.append(dict(id=sid,binding=bind(path),category=category,status=status,required=True,statement=statement,scope='Current prep-only correction; original task/history/authority retained.'))
packet=pk.read_json(r,'results/sikh368/motion-packet.json');g=dict(context_sources=src,knowledge_task='results/sikh368/motion-task.json',knowledge_digest=packet['packet_digest'],reason='Explicit368 authority/reference addendum and fresh currentpacket. Reviewed357 excerpt narrows to11..14 retaining tack/retro/engine/allowance lessons; grooming/material construction out of prep scope. Full unchanged source read and bound. Core catalog reviewed separately;307 not repinned.',evidence={p:bind(p) for p in ['results/sikh368/REQUEST.md','results/sikh368/STRATEGY.md','results/sikh368/CONTEXT_RECONCILIATION.md','results/sikh367/LEARNINGS367.md']})
test={**s['direction'],**{k:g[k] for k in ['context_sources','knowledge_task','knowledge_digest']}};pp.sources(r,test);text=pp.source_context(r,test);print('source_context_bytes',len(json.dumps(text).encode()))
s=pa.extend(c,s['task'],'sikh368-motion-amendment',bind('results/sikh368/extension.json'),'sikh368-add-five',grounding=g);(o/'grounding-amendment.json').write_text(json.dumps(g,indent=2)+'\n');print('Amended',s['cycle'],s['max_corrections'])
