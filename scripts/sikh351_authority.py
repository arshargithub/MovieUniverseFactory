"""Apply the exact Director351 extension to the retained appearance task."""
import json
from copy import deepcopy
from pathlib import Path
from movie_factory import production_workflow as wf, production_knowledge as pk
from movie_factory.production_allowance import extend
from movie_factory.task_router import DATABASE

r = Path(__file__).resolve().parents[1]
c = wf.Controller(r, DATABASE)
task = 'sikh335-supporting-appearance'
def bind(path):
    return dict(path=path, sha256=pk.file_hash(r / path))

s = c.state(task)
reconciliation = dict(
    state_digest=pk.digest(s),
    coverage='Retained appearance cycles0–52, original335 authority,348 causal audit including23 cloth proof,35 representation regression and52 bare deformation. Motion12 is separate and not extended.',
    unknowns='Shoulder/elbow causal diagnosis remains unproven. No whole actor, crowd, horse performance or full-speed AV acceptance. No migration of motion task.',
    evidence={p: bind(p) for p in ['results/sikh348/RETROSPECTIVE.md', 'results/sikh348/CAUSAL_LEDGER.md', 'results/sikh348/NEXT_PROOF.md', 'results/sikh335/REASSESSMENT_347.md', 'results/sikh351/REQUEST.md']})
# Migration already succeeded before the extension found the old knowledge pin.
assert c.retrospective_packet(task)['gates']['__migration__']['status']=='OPEN'
kt=pk.read_json(r,'results/sikh335/task.json')
for path,value in kt['inputs'].items():
    if path!='docs/knowledge/PLANNING_PIPELINE_330.md': assert pk.file_hash(r/path)==value
kt.update(id='sikh351-deformation-transfer',intent='Bare deformation and preserved23 garment transfer on existing leader; whole appearance remains unaccepted.')
for path in ['docs/knowledge/PLANNING_PIPELINE_330.md','results/sikh351/REQUEST.md',
             'results/sikh351/GROUNDING_RECONCILIATION.md','results/sikh348/CAUSAL_LEDGER.md',
             'results/sikh348/NEXT_PROOF.md','results/sikh335/REASSESSMENT_347.md']:
    kt['inputs'][path]=pk.file_hash(r/path)
kt['execution_authority']={'source':'results/sikh351/REQUEST.md','scope':'Five additional appearance corrections only; no new spending or motion extension.'}
(r/'results/sikh351/task.json').write_text(json.dumps(kt,indent=2)+'\n')
packet=pk.task_packet(r,kt)
assert packet['dispatch_ready'],packet['blockers']
(r/'results/sikh351/knowledge-packet.json').write_text(json.dumps(packet,indent=2)+'\n')
sources=deepcopy(s['direction']['context_sources'])
next(x for x in sources if x['id']=='controls')['binding']=bind('results/sikh351/task.json')
# Retain mandatory sources with explicit task-relevant excerpts; full texts are
# read separately, and original source hashes/status/meaning remain protected.
next(x for x in sources if x['id']=='learnings')['lines']=[1,40]
next(x for x in sources if x['id']=='references')['lines']=[1,40]
for sid,path in [('audit348','results/sikh348/NEXT_PROOF.md'),('reconciliation351','results/sikh351/GROUNDING_RECONCILIATION.md')]:
    sources.append(dict(id=sid,binding=bind(path),category='learnings',status='adopted',required=True,
        statement='Apply the reviewed causal proof before dependent clothing work.',scope='Local appearance correction; no whole actor acceptance.'))
grounding=dict(context_sources=sources,knowledge_task='results/sikh351/task.json',
    knowledge_digest=packet['packet_digest'],reason='Reviewed330 retrospective addition and348 causal findings; original direction unchanged.',
    evidence={'review':bind('results/sikh351/GROUNDING_RECONCILIATION.md')})
updated = extend(c, task, 'sikh351-allowance', bind('results/sikh351/allowance.json'), 'sikh351-five-approved',grounding=grounding)
receipt = dict(task=task, stage=updated['stage'], cycle=updated['cycle'], maximum=updated['max_corrections'],
               motion_cycle=c.state('sikh335-continuous-performance')['cycle'],
               motion_maximum=c.state('sikh335-continuous-performance')['max_corrections'],
               migration=reconciliation, retrospective=c.retrospective_packet(task))
(r/'results/sikh351/authority-receipt.json').write_text(json.dumps(receipt, indent=2)+'\n')
print(json.dumps({k: v for k, v in receipt.items() if k not in {'migration','retrospective'}}))
