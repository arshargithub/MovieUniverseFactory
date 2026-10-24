"""Reviewed source/handler revision after all101 diagnostics, original limits."""
import json
from pathlib import Path
from copy import deepcopy
from movie_factory import production_workflow as wf,production_knowledge as pk
from movie_factory.task_router import DATABASE
r=Path(__file__).resolve().parents[1];o=r/'results/sikh363';c=wf.Controller(r,DATABASE)
def bind(p):return dict(path=p,sha256=pk.file_hash(r/p))
for label,task,old in [('appearance','sikh335-supporting-appearance',101),('motion','sikh335-continuous-performance',28)]:
 s=c.state(task);assert s['cycle']==old
 kt=pk.read_json(r,s['direction']['knowledge_task']);kt['id']='sikh363-'+label+'-causal';kt['inputs']['results/sikh363/CAUSAL_AUDIT.md']=pk.file_hash(o/'CAUSAL_AUDIT.md')
 path=f'results/sikh363/{label}-task-causal.json';(r/path).write_text(json.dumps(kt,indent=2)+'\n');packet=pk.task_packet(r,kt);assert packet['dispatch_ready'],packet['blockers'];(o/(label+'-packet-causal.json')).write_text(json.dumps(packet,indent=2)+'\n')
 sources=deepcopy(s['direction']['context_sources']);next(x for x in sources if x['id']=='controls')['binding']=bind(path)
 # Current full363 authority/strategy supersede old implementation details.
 # Keep their original statement/status/scope and applicable exact excerpts.
 for row in sources:
  if row['id']=='direction':row['lines']=[3,22]
  if row['id']=='cast_findings':row['lines']=[6,19]
 sources.append(dict(id='audit363',binding=bind('results/sikh363/CAUSAL_AUDIT.md'),lines=[1,31],category='learnings',status='adopted',required=True,statement='Actual front chest failure, invalid side framing and open rein-hand claw confirmed; length metrics did not pass anatomy. Compare corrective effect and actual grip before integration.',scope='Original363 correction; diagnosis is not repair/acceptance.'))
 s=c.reground(task,sources,path,packet['packet_digest'],'Actual101 diagnostic evidence now supports a targeted MCP closure and corrective comparison. Fixed native outcome ownership no longer confuses component availability with art or human AV. All101 native steps returned and reviewed before engine/handler changes; preserve original failed evidence and limits.','sikh363-'+label+'-causal-reground')
 print(label,s['cycle'],s['max_corrections'])
