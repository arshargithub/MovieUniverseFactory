"""Verify actual files, retaining failed post-render admission as failed."""
import json,hashlib
from PIL import Image
from pathlib import Path
from movie_factory import production_knowledge as pk
root=Path(__file__).resolve().parents[1];path=root/'.runtime/factory-native/sikh337-c8-clip06'
run=pk.read_json(root,'results/sikh335/motion01/clip06-run-c8.json')
assert run['status']=='FAILED' and run['error']=='Blocked: STALE_BINDING'
worker=json.loads((path/'worker-status.json').read_text());assert worker['ok'] is True
original=pk.read_json(root,'results/sikh335/motion01/save-run-c5.json')
for key in ('snapshot','dependencies'):
    assert pk.file_hash(path/(key+'.json'))==original['artifacts'][key]['sha256']
frames=json.loads((path/'frames.json').read_text())
assert {r['frame'] for r in frames}==set(range(342,357))|{327}
artifacts={}
for row in frames:
    p=path/row['file'];assert pk.file_hash(p)==row['sha256']
    artifacts[f"frame_{row['frame']}"]={'path':str(p.relative_to(root)),'sha256':row['sha256']}
previous=pk.read_json(root,'results/sikh335/motion01/clip00-run-c6.json')
def pixels(p):
    with Image.open(p) as image:return hashlib.sha256(image.convert('RGBA').tobytes()).hexdigest()
control=pixels(root/artifacts['frame_327']['path'])
assert control==pixels(root/previous['artifacts']['frame_327']['path'])
report={'status':'HISTORICAL_WORKER_OUTPUT_NOT_NATIVE_ADMITTED','artifacts':artifacts,
 'original_failed_run':'results/sikh335/motion01/clip06-run-c8.json',
 'worker_seconds':worker['timings']['worker_total_seconds'],'control_rgba_sha256':control,
 'checks':['worker reported successful extraction','selected snapshot/dependencies match candidate5','all16 requested PNG file hashes verified','327 decoded RGBA pixels exactly match earlier control; PNG Date/File/RenderTime metadata differs'],
 'limits':'Native receipt remains FAILED; this source audit does not promote it or establish motion/appearance approval.'}
dest=root/'results/sikh335/motion01/clip06-historical-source.json'
assert not dest.exists();dest.write_text(json.dumps(report,indent=2)+'\n')
print('Verified16 actual images as explicitly unadmitted historical source evidence.')
