"""Read-only campaign inventory plus auditable local report artifacts."""
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

from movie_factory.production_workflow import Controller
from movie_factory.task_router import DATABASE
from movie_factory.experiment_ledger import Ledger

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'results/sikh348'
def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()
def binding(p):
    return dict(path=str(p.relative_to(ROOT)), sha256=digest(p))
def write(name, value):
    (OUT/name).write_text(json.dumps(value, indent=2)+'\n')

def main():
    authority = binding(OUT/'REQUEST.md')
    controller = Controller(ROOT,DATABASE)
    route = controller.route_request('sikh348-retrospective',dict(
        text='Audit the Nihang leader, horse and rearing campaign and save causal findings.',
        operations=['research','plan','document'],authority=authority,
        rationale='Existing files and evidence only; no production mutation, native process, media admission or correction extension.'))
    write('route.json',route)
    ledger=Ledger(ROOT/'.runtime/experiment-ops.sqlite3')
    if not any(e['event_id']=='sikh348-work-start' for e in ledger.events()):
        ledger.append(dict(event_id='sikh348-work-start',experiment_id='SIKH335',episode_id='first',
            utc=datetime.now(timezone.utc).isoformat(),event_type='work_started',phase='design',
            activity_id='sikh348-retrospective',note='Causal audit; initial source recovery before this timestamp is unmeasured.'))
    rows=[]
    for folder,cap in [('look01',52),('motion01',12)]:
        base=ROOT/'results/sikh335'/folder
        for cycle in range(cap+1):
            paths=sorted(base.glob(f'*-c{cycle}.json'))
            runs=[];reviews=[];reasons=[]
            for p in paths:
                d=json.loads(p.read_text())
                if '-run-' in p.name:
                    runs.append(dict(source=binding(p),id=d.get('id'),step=d.get('step'),status=d.get('status'),error=d.get('error'),parent=d.get('parent'),artifacts=d.get('artifacts',{})))
                if 'review' in p.name:
                    reviews.append(dict(source=binding(p),verdict=d.get('verdict',d.get('status')),observation=d.get('observation')))
                if 'rejection' in p.name:
                    reasons.append(dict(source=binding(p),reason=d.get('reason',d.get('observation')),status=d.get('status')))
            rows.append(dict(branch=folder,cycle=cycle,artifact_count=len(paths),runs=runs,reviews=reviews,rejections=reasons,
                has_returned_save=any(x['step']=='save' and x['status']=='RETURNED' for x in runs),
                sources=[binding(p) for p in paths]))
    write('cycle-inventory.json',dict(scope='Mechanical inventory of c0 initial plus numbered corrections; absence of a run is not proof no attempt occurred. RETURNED is technical, not artistic.',rows=rows))
    states={t:{k:controller.state(t)[k] for k in ('cycle','max_corrections','stage')} for t in
        ('sikh335-supporting-appearance','sikh335-continuous-performance')}
    write('state-at-audit.json',states)
    source_paths = ['results/sikh348/REQUEST.md','results/sikh321/disposition.json',
        'docs/knowledge/NIHANG_REARING_REVIEW_FAILURE_321.md',
        'results/sikh335/STRATEGY.md','results/sikh335/CONTROL_FINDINGS.md',
        'results/sikh335/REASSESSMENT_339.md','results/sikh335/REASSESSMENT_340.md',
        'results/sikh335/REASSESSMENT_341.md','results/sikh335/REASSESSMENT_342.md',
        'results/sikh335/REASSESSMENT_343.md','results/sikh335/LEARNINGS_344.md',
        'results/sikh335/REASSESSMENT_347.md','results/sikh335/motion01/landing-review-c12.md']
    write('task.json',dict(id='sikh348-causal-retrospective',operation='motion',
        entities=['nihang_leader','nihang_horse','nihang_crowd'],phase='planning',
        query='Retrospective on construction, deformation, rearing reference, knowledge application and admission failures.',
        intent='Identify cross-cycle causes and a discriminating next proof; no native changes or artistic qualification.',
        inputs={p:digest(ROOT/p) for p in source_paths},open_decisions=[],max_context_characters=60000,
        execution_prerequisites=['Audit only. Existing correction caps remain exhausted. No production work authorized.']))
    print(json.dumps(dict(states=states,rows=len(rows),appearance_returned_save_cycles=[x['cycle'] for x in rows if x['branch']=='look01' and x['has_returned_save']],
        motion_returned_save_cycles=[x['cycle'] for x in rows if x['branch']=='motion01' and x['has_returned_save']])))

if __name__=='__main__':
    main()
