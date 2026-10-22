"""Fresh scoped packet; no blanket refresh of historical corpus pins."""
import json
from pathlib import Path
from movie_factory import production_knowledge as pk
r=Path(__file__).resolve().parents[1]
old=json.loads((r/'.runtime/knowledge-pilot213/sikh342-current.json').read_text())
t=old['task']
for path,h in t['inputs'].items():assert pk.file_hash(r/path)==h
t['id']='sikh335-continuation343'
t['intent']='Continue existing five-cycle isolated Nihang correction: coherent whole supporting actor proof and explicit scene-owned landing repair; accepted Pashtun floor unchanged.'
t['execution_authority']={'source':'results/sikh335/allowance343.json','scope':'Five shared corrections on existing tasks; no new spend or egress.'}
for path in ['results/sikh335/allowance343.json','results/sikh335/REASSESSMENT_342.md']:
 t['inputs'][path]=pk.file_hash(r/path)
p=r/'results/sikh335/task343.json';assert not p.exists();p.write_text(json.dumps(t,indent=2)+'\n')
