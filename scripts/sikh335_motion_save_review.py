"""Measured technical save gate; authorizes diagnostic rendering, not art approval."""
import json,math
from pathlib import Path
from movie_factory import production_workflow as wf,production_knowledge as pk
from movie_factory.native_admission import Bridge
from movie_factory.task_router import DATABASE
root=Path(__file__).resolve().parents[1];out=root/'results/sikh335/motion01'
c=wf.Controller(root,DATABASE);task='sikh335-continuous-performance';cycle=c.state(task)['cycle']
run=json.loads((out/f'save-run-c{cycle}.json').read_text())
patch=pk.read_json(root,run['artifacts']['patch']['path'])
rows=patch['support'][1]['motion']['frames']
assert [r['frame'] for r in rows]==list(range(252,442))
error=max(math.dist(s['support_target'],s['visible_hoof']) for r in rows for s in r['hind_support'])
retract=max(s['flight_wrist_adjustment'] for r in rows for s in r['hind_support'])
diag=pk.read_json(root,run['artifacts']['scripts']['path'])
assert error<.001 and retract<.02 and not diag['blocked_drivers'] and not diag['known_source_defects']
verdict={'verdict':'PASS','run_digest':pk.digest(run),'evidence':run['artifacts'],
    'observation':f'190 authored frames; maximum visible hind endpoint error{error:.8f}m, airborne wrist retraction{retract:.8f}m; zero invalid used drivers.',
    'comparison':'Technical persistence/support gate only. Phase silhouettes, actual rider/rein/spear fit, anatomy, appearance and full-speed motion are NOT_RUN; no integrated pass.',
    'open_defects':[]}
Bridge(c).record_review(task,'save',verdict)
(out/f'save-review-c{cycle}.json').write_text(json.dumps(verdict,indent=2)+'\n')
print(verdict['observation'])
