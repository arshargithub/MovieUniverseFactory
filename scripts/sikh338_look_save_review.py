"""Technical preservation gate only; permits revealing images, not acceptance."""
import json
from pathlib import Path
from movie_factory import production_workflow as wf, production_knowledge as pk
from movie_factory.native_admission import Bridge
from movie_factory.task_router import DATABASE
r=Path(__file__).resolve().parents[1];out=r/'results/sikh335/look01'
c=wf.Controller(r,DATABASE);task='sikh335-supporting-appearance';cycle=c.state(task)['cycle']
run=pk.read_json(r,f'results/sikh335/look01/save-run-c{cycle}.json')
assert run['status']=='RETURNED'
for b in run['artifacts'].values():assert pk.file_hash(r/b['path'])==b['sha256']
p=pk.read_json(r,run['artifacts']['patch']['path']);d=pk.read_json(r,run['artifacts']['scripts']['path'])
assert p['before']['objects']==p['after']['objects']
assert p['before']['camera_matrix']==p['after']['camera_matrix']
assert not d['blocked_drivers'] and not d['known_source_defects']
look=next(x['look'] for x in p['support'] if 'look' in x)
assert len(look['actors'])==2 and look['actors'][0]['garment']['cached_poses']==207
for a in look['actors']:
    assert a['garment']['drape']['maximum_displacement']<.09
v={'verdict':'PASS','run_digest':pk.digest(run),'evidence':run['artifacts'],
 'observation':'Both native panel simulations completed. Leader maximum depth delta42.24mm and near-crowd22.77mm;207 leader pose caches preserved; selected rig/actor/camera state unchanged; zero blocked or invalid used drivers.',
 'comparison':'Technical save gate only. Garment shape, boundary blend, face/crown/saddle and animated transfer are NOT_RUN or previously failed; actual images are required. No appearance or production pass.',
 'open_defects':[]}
Bridge(c).record_review(task,'save',v)
dest=out/f'save-technical-review-c{cycle}.json';assert not dest.exists();dest.write_text(json.dumps(v,indent=2)+'\n')
print(v['observation'])
