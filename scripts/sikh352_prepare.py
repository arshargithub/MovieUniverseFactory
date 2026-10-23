"""Bootstrap exact request records; no native construction or allowance reset."""
import json
from pathlib import Path
from movie_factory import production_knowledge as pk
r=Path(__file__).resolve().parents[1];o=r/'results/sikh352'
def write(n,v):
 p=o/n;assert not p.exists();p.write_text(json.dumps(v,indent=2)+'\n')
def bind(p):return dict(path=p,sha256=pk.file_hash(r/p))
write('allowance.json',dict(task='sikh335-supporting-appearance',decision='approve_additional_corrections',additional_corrections=4,
 prior_cycle=57,prior_max_corrections=57,question='Renew correction authority for coordinated shoulder-elbow-wrist/contact proof before garment transfer.',director_reply='go ahead. 4 more cycles approved'))
write('amendment-request.json',dict(text='Director352 approves four additional corrections to existing exhausted appearance task.',operations=['code','document'],amendment_task='sikh335-supporting-appearance',authority=bind('results/sikh352/allowance.json'),rationale='Exact administrative extension; full production continuation separately routed.'))
write('request.json',dict(text='Continue coordinated arm/contact anatomy proof and dependent garment transfer within four additional appearance corrections.',operations=['native_inspect','asset','edit','render','code','test','document'],continuation=True,authority=bind('results/sikh352/REQUEST.md'),rationale='Existing appearance task, original intent preserved; no separate motion correction or new external authority.'))
