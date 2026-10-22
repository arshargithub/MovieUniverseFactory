"""Fresh scoped packet; no blanket refresh of historical corpus pins."""
import json
from pathlib import Path
from movie_factory import production_knowledge as pk
r=Path(__file__).resolve().parents[1]
old=json.loads((r/'.runtime/knowledge-pilot213/sikh345-current.json').read_text())
t=old['task']
for path,h in t['inputs'].items():assert pk.file_hash(r/path)==h
t['id']='sikh335-continuation346'
t['intent']='Continue existing five-cycle isolated Nihang correction: mounted leader anatomical contact and continuous cloth proof; accepted Pashtun floor unchanged.'
t['execution_authority']={'source':'results/sikh335/allowance346.json','scope':'Five shared corrections on existing tasks; no new spend or egress.'}
for path in ['results/sikh335/allowance346.json','results/sikh335/REASSESSMENT_345.md']:
 t['inputs'][path]=pk.file_hash(r/path)
p=r/'results/sikh335/task346.json';assert not p.exists();p.write_text(json.dumps(t,indent=2)+'\n')
