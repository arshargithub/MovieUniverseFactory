"""Technical finish receipt, explicitly not the earlier waist review wording."""
import json
from pathlib import Path
from movie_factory import production_workflow as wf,production_knowledge as pk
from movie_factory.native_admission import Bridge
from movie_factory.task_router import DATABASE
r=Path(__file__).resolve().parents[1];c=wf.Controller(r,DATABASE);t='sikh335-supporting-appearance';cy=c.state(t)['cycle']
run=pk.read_json(r,f'results/sikh353/save-run-c{cy}.json');assert run['status']=='RETURNED'
for item in run['artifacts'].values():assert pk.file_hash(r/item['path'])==item['sha256']
patch=pk.read_json(r,run['artifacts']['patch']['path']);assert patch['before']['objects']==patch['after']['objects']
report=patch['support'][0]['finish353'];assert report['changed'] and report['source_preserved']
diag=pk.read_json(r,run['artifacts']['scripts']['path']);assert not diag['blocked_drivers'] and not diag['known_source_defects']
v=dict(verdict='PASS',run_digest=pk.digest(run),evidence=run['artifacts'],observation='Owned finish edits saved/reopened, source and protected root/horse pose state retained. Actual material/crown/beard/eye inventory returned. Technical persistence only.',comparison='64 source remains preserved; this does not pass facial shape, garment interfaces, horse appearance or AV.',open_defects=[])
Bridge(c).record_review(t,'save',v);(r/f'results/sikh353/save-technical-c{cy}.json').write_text(json.dumps(v,indent=2)+'\n')
print({k:report[k] for k in ('crowns','beard_curves','horse_vertices','horse_modifiers','eyes')})
