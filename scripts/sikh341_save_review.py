"""Review actual saved proof provenance/safety before revealing images, not art."""
import json,sys
from pathlib import Path
from movie_factory import production_workflow as wf,production_knowledge as pk
from movie_factory.native_admission import Bridge
from movie_factory.task_router import DATABASE
r=Path(__file__).resolve().parents[1];out=r/'results/sikh335/look01'
c=wf.Controller(r,DATABASE);task='sikh335-supporting-appearance';cycle=c.state(task)['cycle']
assert cycle in (18,19)
step=sys.argv[1] if len(sys.argv)>1 else 'save';assert step in ('save','bend')
run=pk.read_json(r,f'results/sikh335/look01/{step}-run-c{cycle}.json');assert run['status']=='RETURNED'
for b in run['artifacts'].values():assert pk.file_hash(r/b['path'])==b['sha256']
p=pk.read_json(r,run['artifacts']['patch']['path']);d=pk.read_json(r,run['artifacts']['scripts']['path'])
assert p['before']['objects']==p['after']['objects']
assert not d['blocked_drivers'] and not d['known_source_defects']
assert p['after']['camera']=='MF neutral camera'
n=p['support'][0]['neutral']
if n['phase']=='neutral':
 assert n['donor_pose']=='actual native unposed rest mesh' and n['settle_frames']==40
 assert 3000<n['garment_vertices']<12000 and n['maximum_displacement']<.09 and n['maximum_initial_fit']<.045
 observation=f"Actual neutral body/garment saved: {n['garment_vertices']} cloth vertices;40-frame settle maximum{n['maximum_displacement']:.6f}m. Source actor/rig state unchanged. No used invalid/unsafe drivers. Neutral studio is an explicit new diagnostic scene."
else:
 assert n['phase']=='bend' and n['angle_degrees']==-75
 assert all(x['unchanged_shoulder'] for x in n['objects'].values())
 observation='Actual reviewed neutral derivative bent at one elbow by75 degrees with unchanged shoulder/other arm. Used driver diagnostics remain clear. Static deformation needs image review.'
v={'verdict':'PASS','run_digest':pk.digest(run),'evidence':run['artifacts'],
 'observation':observation,
 'comparison':'Technical save prerequisite only; actual front/back/side images and form/contact review are still NOT_RUN. This is not a garment visual or whole-character PASS.',
 'open_defects':[]}
Bridge(c).record_review(task,step,v)
dest=out/f'{step}-technical-review-c{cycle}.json';assert not dest.exists();dest.write_text(json.dumps(v,indent=2)+'\n')
print(observation)
