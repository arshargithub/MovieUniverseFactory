"""Bootstrap latest explicit authority; no native work."""
import json
from pathlib import Path
from movie_factory import production_knowledge as pk
r=Path(__file__).resolve().parents[1];o=r/'results/sikh354';task='sikh335-supporting-appearance'
def bind(p):return dict(path=p,sha256=pk.file_hash(r/p))
def write(n,v):
 p=o/n;assert not p.exists();p.write_text(json.dumps(v,indent=2)+'\n')
write('allowance.json',dict(task=task,decision='approve_additional_corrections',additional_corrections=5,prior_cycle=67,prior_max_corrections=67,question='Continue whole leader appearance reconstruction, preserving motion16 and deferring crowd.',director_reply='Go ahead for 5 more cycles. Also, curious if retro has been triggered since we implemented it',aggregate_authority=bind('results/sikh354/REQUEST.md')))
write('amendment.json',dict(text='Director354 five more appearance corrections68–72 on original task.',operations=['code','document'],amendment_task=task,authority=bind('results/sikh354/allowance.json'),rationale='Exact allowance extension, no reset or new spend.'))
write('request.json',dict(text='Continue leader and horse whole appearance; report actual retrospective triggers since350.',operations=['status','explain','native_inspect','asset','edit','render','code','test','document'],continuation=True,authority=bind('results/sikh354/REQUEST.md'),rationale='Mixed production and read-only retrospective audit; original task/cumulative limits retained, motion16 preserved, no crowd.'))
