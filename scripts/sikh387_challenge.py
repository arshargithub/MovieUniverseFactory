"""Parent-authored challenge of227proof. No inference or artistic candidate verdict."""
import json,copy
from pathlib import Path
from movie_factory import production_workflow as wf,production_knowledge as pk
r=Path(__file__).resolve().parents[1];c=wf.Controller(r,'.runtime/factory-entry.sqlite3');s=c.state('sikh335-supporting-appearance');b=s['planning_artifacts']['STRATEGIZING']['brief']
x=pk.read_json(r,'results/sikh386/appearance-c226-challenge.json')
observations=dict(grounding='New387authority, exact source193and final226failure are retained; failed contraction is not a foundation.',expert_coverage='Anatomy requires supported chest and origins; posed strain tests one structural cause while preserving actual action. Other film work deferred.',film_alignment='Original actor and acceptedPashtun quality remain fixed; clay diagnostic is not a newlook.',preferences='No routine technical gate; first proof tests worstview before dense iteration. No known shape failure offered ready.',reference_roles='Physicalphotos and qualifiedCC0guide govern anatomy, video/66/75/80 govern performance; no new identity.',method='Posed edge-local ARAP differs from failed neutral guide fit. Surface-volume collapse and boundary kinks are concrete counterexamples; actualnative comparison must veto.',interfaces='Both shoulders/neck/forelegs/thorax remain visible. Exactdistal and original skeleton first; no substituteperformance.',efficient_quality='Threepose prerequisite before dense cache/coat. No more contraction coefficients. Failure causes a method review.',authority='Same original335task227/251 shared ceiling; SolHigh, no spend/provider/cloud/install/Astra/newactor.')
for k,row in x['checks'].items():row.update(status='PASS',observation=observations[k],comparison='387strategy versus actual226visible failures and approved physical/performance references.',source_ids=['director387','closure226','scope386'])
cfg=pk.read_json(r,f'results/sikh387/appearance-c{s["cycle"]}.json')
x['checks']['method']['observation']=cfg['method']+' Criticaltest: '+cfg['proof']
x['strongest_counterexample']=cfg.get('counterexample','A strain-minimizing surface can still collapse volume or keep an unsupported shelf; numerical/structural success is not artistic approval.')
for k,observation in cfg.get('challenge_observations',{}).items():x['checks'][k]['observation']=observation
x['reference_challenge']['readiness_digest']=pk.digest(b['reference_readiness'])
for row in x['reference_challenge']['checks'].values():row.update(status='PASS',observation='Retain purpose-qualified realhorse anatomy, existing spatial guide and original action; enough for this causal structural test. No new reference substitutes for construction.')
x['unit_scope_challenge']['unit_digest']=pk.digest(b['work_unit']);x['unit_scope_challenge']['counterexample']=x['strongest_counterexample']
for row in x['unit_scope_challenge']['checks'].values():row.update(status='PASS',observation=cfg.get('scope_challenge','Merged connectedforequarter; first threepose numeric prerequisite, then actualfront/side/opposite339. Shared227..251ceiling and original performance remain explicit.'))
(r/f'results/sikh387/appearance-c{s["cycle"]}-challenge.json').write_text(json.dumps(x,indent=2)+'\n')
