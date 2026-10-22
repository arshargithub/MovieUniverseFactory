"""Explicit challenge of the replacement pattern, not inheritance of a visual pass."""
import json
from pathlib import Path
r=Path(__file__).resolve().parents[1];p=r/'results/sikh335/look01'
v=json.loads((p/'challenge-verdict-c8.json').read_text())
updates={
 'grounding':('C8 actual images reject the prior patch construction; separate339 authority extends the same task to12. Fresh knowledge packet and STRATEGY_C9 reconcile the unchanged quality floor.','No repeated approval was counted twice; all eight failed attempts remain.'),
 'expert_coverage':('Pattern construction, garment support, sleeve elbow/cuff ownership and barycentric pose transfer are now explicit. Face/headwear are still independent mandatory dependencies.','A low-poly shell is not automatically tailored cloth. The complete actor must eventually pass.'),
 'method':('Reviewed new connected front/back and sleeve topology, support pins, measured body depth, original collision donor,40-frame settle and normal-offset pose transfer. Six offline tests pass, including connectedness and barycentric reconstruction.','This changes representation rather than embossing a rectangular patch. Native body fit and simulation are still hypotheses, not qualified capabilities.'),
 'interfaces':('Actual elbow/cuff donors are transformed into shirt space; fixed waist and shoulder support remain. Existing207 pose action is copied to the new surface-bound topology. Outer layers retarget to the new exterior.','Straight portions of the sleeve and pinned shoulder boundaries may still intersect or look rigid; stance/crest/reverse images are vetoes. No animated-cloth claim.'),
 'efficient_quality':('One complete replacement garment on leader and near actor, with serial revealing images before further construction or propagation.','No final sequence rerender or cosmetic detailing of a rejected torso.'),
 'authority':('Separate explicit four-correction approval raises8 to12. This is correction9, no spend or external service.','No automatic extension beyond12 and no resetting motion allowance.')}
for key,(observation,comparison) in updates.items():
    v['checks'][key]['observation']=observation;v['checks'][key]['comparison']=comparison
v['strongest_counterexample']='The new shell can be connected yet still badly tailored: shoulder/cuff pinning can cause rigid ridges, initial sleeve-body collision can explode, nearest binding can distort inside an elbow. Reject on these actual results; do not claim success because a solver completed. Face and crown still block whole-character delivery.'
dest=p/'challenge-verdict-c9.json';assert not dest.exists();dest.write_text(json.dumps(v,indent=2)+'\n')
