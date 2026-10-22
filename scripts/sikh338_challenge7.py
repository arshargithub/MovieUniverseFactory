"""Source-reviewed challenge of the panel-based drape correction."""
import json
from pathlib import Path
r=Path(__file__).resolve().parents[1];p=r/'results/sikh335/look01'
v=json.loads((p/'challenge-verdict-c5.json').read_text())
v['checks']['grounding']['observation']='Exact338 authority retained. Correction6 actually ran and rejected displacement; the worker did not save a candidate. Original c3 image failures remain.'
v['checks']['method']['observation']='Reviewed current native method: two35x35 regular quad panels sample the existing torso, settle against a contracted collision proxy with pinned boundaries, then transfer only central depth back to unchanged garment topology. This is the specific panel implementation of the supported-drape strategy, replacing full donor topology simulation. Four nonnative regression controls pass.'
v['checks']['method']['comparison']='Uniform panels remove irregular mixed-length donor edges from cloth simulation, but collision convergence and useful visible folds remain unproven. No force-clamping of excessive results; the guard still fails.'
v['checks']['interfaces']['observation']='Actual code preserves x/z and shoulder/cuff/waist boundaries, interpolates panel depth to central torso and applies it to every cached pose. Existing layer refit and revealing stance/crest controls remain.'
v['checks']['authority']['observation']='Same task correction7/max8 after retained native failures5/6. No new spending or provider. Original and candidate5 parents remain protected.'
v['strongest_counterexample']='Supported panels may settle too smoothly, create depth creases at their blend boundary, or fail collision. These and still-open face/crown/saddle issues block artistic admission. No useful look is assumed from the change of mesh used for simulation.'
dest=p/'challenge-verdict-c7.json';assert not dest.exists();dest.write_text(json.dumps(v,indent=2)+'\n')
