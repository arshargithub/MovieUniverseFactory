"""Review the final authorized trial against its retained failure evidence."""
import json
from pathlib import Path
r=Path(__file__).resolve().parents[1];p=r/'results/sikh335/look01'
v=json.loads((p/'challenge-verdict-c7.json').read_text())
v['checks']['grounding']['observation']='C7 failed while sampling rectangular panel support, before simulation. C6 displacement failure and all earlier image rejections remain. Exact338 final correction authority is unchanged.'
v['checks']['method']['observation']='Reviewed measured-domain sampling: require support at each of35 row heights on both sides, choose90percent of minimum contiguous half-width, require width above6cm. Then settle regular panels with pinned boundaries. Four unit regressions pass but they do not validate native support or simulation.'
v['checks']['method']['comparison']='This repairs the specific unsupported panel boundary assumption without disabling support or displacement guards. It cannot by itself fix face, crown or saddle defects; images remain decisive.'
v['checks']['authority']['observation']='Same task correction8/max8, the last appearance correction approved338. No new provider, spending, installation or master change; no automatic retry follows failure.'
v['strongest_counterexample']='The measured panel may be too narrow or still fail cloth convergence. A converged small patch may not visibly improve the whole garment and cannot clear the independent face/crown/saddle failures. Exhaustion must remain failure, not an incremental artistic handoff.'
dest=p/'challenge-verdict-c8.json';assert not dest.exists();dest.write_text(json.dumps(v,indent=2)+'\n')
