"""Bind the actual failed outcome; never reuse prior pass declarations."""
import json
from pathlib import Path
from movie_factory import production_knowledge as pk
r=Path(__file__).resolve().parents[1];out=r/'results/sikh335/look01'
p=pk.read_json(r,'.runtime/knowledge-pilot213/sikh340-current.json')
paths=['results/sikh335/look01/exhaustion-c17.json','results/sikh335/REASSESSMENT_340.md']
evidence=[{'path':x,'sha256':pk.file_hash(r/x)} for x in paths]
checks=[]
for ob in p['obligations']:
    checks.append({'id':ob['id'],'kind':ob['check_kind'],
       'status':'FAIL' if ob['id'] in ('construction_interfaces','strategy','visual_gate','look','anticipation') else 'NOT_RUN',
       'action_taken':'Preserved exact five-attempt evidence and stopped native work at17/max17. No inherited artistic PASS.',
       'observation':'No complete saved candidate. Leader numerical solve is not appearance; near-crowd solve fails. Native neutral proof was not performed. Complete obligation remains unqualified.',
       'evidence':evidence})
review={'packet_digest':p['packet_digest'],'checks':checks,
 'hypotheses':[{'prediction':'Separating initial pattern defects may yield a stable complete garment.',
 'observation':'Leader settles after repairs; near crowd still exceeds guard. Geometric plots remain insufficient for artistic qualification.',
 'response':'Stop posed construction route. Actual native neutral-body proof is prerequisite to future bending.',
 'result':'unresolved'}],
 'adjacent_regressions':'No complete save or render. Face/crown/tack and performance remain open; original masters untouched.',
 'stopping_reason':'Appearance17/max17 exhausted. Authority blocker, not completion. No known-failure media review queue.'}
(out/'knowledge-review340.json').write_text(json.dumps(review,indent=2)+'\n')
print('Recorded failed outcome for evidence gate')
