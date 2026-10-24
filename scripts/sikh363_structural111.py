"""Explicit current-source reconciliation for two independent asset proofs."""
import json
from pathlib import Path
from copy import deepcopy
from movie_factory import production_workflow as wf,production_knowledge as pk,planning_pipeline as pp
from movie_factory.task_router import DATABASE
r=Path(__file__).resolve().parents[1];c=wf.Controller(r,DATABASE);task='sikh335-supporting-appearance';s=c.state(task);assert s['cycle']==110
def bind(p):return dict(path=p,sha256=pk.file_hash(r/p))
kt=pk.read_json(r,'results/sikh363/appearance-task-structural.json');packet=pk.task_packet(r,kt);assert packet['dispatch_ready'],packet['blockers'];path='results/sikh363/appearance-task-structural.json'
sources=deepcopy(s['direction']['context_sources']);next(x for x in sources if x['id']=='controls')['binding']=bind(path)
sources.append(dict(id='structural111',binding=bind('results/sikh363/APPEARANCE111_REVIEW.md'),lines=[1,31],category='learnings',status='adopted',required=True,statement='Actual40 frontal/chronology failures remain open; independent lower-pectoral correction and actual tied-CLOTH/cache capability proof precede final41 rebake and art review.',scope='Same363 original leader/horse correction, no production or identity approval from trial.'))
d={**s['direction'],'context_sources':sources,'knowledge_task':path,'knowledge_digest':packet['packet_digest']};context=pp.source_context(r,d);print('Verified source excerpt bytes',sum(len(x['text'].encode()) for x in context['documents'].values()))
s=c.reground(task,sources,path,packet['packet_digest'],'All110 returned steps reviewed; actual40 frontal reveals unresolved pectoral shape. Reviewed chest/flag typed handler integration and independent parent transport; source40 pole is only technical CLOTH trial, not accepted choreography. Final cache must be regenerated after41 cue correction. Preserve current files, original scopes/caps and all failed evidence.','sikh363-a111-structural-reground')
print('appearance',s['cycle'],s['max_corrections'],'packet',len(packet['obligations']))
