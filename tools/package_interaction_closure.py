"""Package a verified 3D-05 scored run without inventing Director acceptance.

Run from the repository with its .venv. Produces a pending-review bundle unless
both the scored result and explicit Director record establish acceptance.
"""
import argparse,ctypes,io,json,os,shutil,subprocess,sys,tarfile
from pathlib import Path
from movie_factory.packages import atomic_json,file_digest,manifest_for,safe_relative
from movie_factory.interaction import validate_director_review


def read(path):return json.loads(path.read_text())


def verify(root,manifest):
    items=read(manifest)['artifacts']
    for item in items:
        p=safe_relative(root,root/item['path'])
        if not p.is_file() or p.stat().st_size!=item['bytes'] or file_digest(p)!=item['sha256']:
            raise ValueError('Evidence hash mismatch: '+item['path'])
    return len(items)


def storage_copy(source,destination):
    if sys.platform == 'darwin':
        clone=ctypes.CDLL('/usr/lib/libSystem.B.dylib',use_errno=True).clonefile
        clone.argtypes=[ctypes.c_char_p,ctypes.c_char_p,ctypes.c_int];clone.restype=ctypes.c_int
        if clone(os.fsencode(source),os.fsencode(destination),0)==0:return destination
    return shutil.copy2(source,destination)


def copy_evidence(source,destination):
    # Old per-run manifests inventory harmless worker-generated thumbnails.
    # Preserve those bytes too, but fail closed on any unexpected runtime file.
    for p in source.rglob('*'):
        if p.is_file() and '.worker_runtime' in p.parts:
            tail=Path(*p.parts[p.parts.index('.worker_runtime')+1:])
            if tail.parent.as_posix()!='home/.thumbnails/large' or p.suffix!='.png':
                raise ValueError('Unexpected runtime payload: '+str(p))
    shutil.copytree(source,destination,copy_function=storage_copy,ignore=shutil.ignore_patterns('__pycache__','*.pyc','.env','.env.local','.venv'))


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--run',required=True);parser.add_argument('--output',required=True);args=parser.parse_args()
    repo=Path.cwd().resolve();run=safe_relative(repo,Path(args.run));out=safe_relative(repo,Path(args.output))
    if out.exists():raise FileExistsError(out)
    result=read(run/'result.json');director=read(run/'director-review.json');campaign=read(run/'frozen-campaign.json')
    if not result.get('scored') or not result.get('machine_passed'):raise ValueError('A scored machine-passing run is required')
    accepted=result.get('decision')=='GREEN' and director.get('status')=='ACCEPTED' and director.get('review_seconds',0)>0
    if result.get('decision')=='GREEN' and not accepted:raise ValueError('Inconsistent GREEN/Director evidence')
    if accepted and not validate_director_review(director,read(run/'blind-key.json'),campaign)['passed']:
        raise ValueError('Director scores do not satisfy the frozen gate')
    count=verify(run,run/'artifact-manifest.json')
    for name in ('deterministic-validation.json','checkpoint-validation.json','control-sensitivity.json'):
        if not read(run/name).get('passed'):raise ValueError('Qualification failure: '+name)
    for name in ('build/scene.blend','replay/build/scene.blend','review/index.html'):
        if not (run/name).is_file():raise ValueError('Missing required '+name)
    for role in ('baseline','candidate'):
        for view in campaign['director_gate']['views']:
            if len(list((run/'evidence/frames'/role/view).glob('frame-*.png')))!=96:raise ValueError('Incomplete playback')
    binding=read(run/'source-binding.json')
    if binding['status']!='EXACT_PRE_RUN':raise ValueError('Missing exact execution source binding')
    status=subprocess.check_output(['git','status','--porcelain'],text=True)
    if status:raise ValueError('Commit final evidence/tooling before packaging')
    head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
    out.mkdir(parents=True)
    for label,commit in (('source',head),('execution-source',binding['implementation_commit'])):
        raw=subprocess.check_output(['git','archive',commit])
        with tarfile.open(fileobj=io.BytesIO(raw),mode='r:') as archive:archive.extractall(out/label,filter='data')
    subprocess.run(['git','bundle','create',str(out/'source-history.bundle'),'--all'],check=True)
    relative=run.relative_to(repo);copy_evidence(run,out/relative)
    compact=repo/'results/3d05/closure-v1'
    if compact.is_dir():copy_evidence(compact,out/'results/3d05/closure-v1')
    for development in sorted((repo/'runs/3d05-development').glob('closure-*')):
        if development.is_dir():copy_evidence(development,out/development.relative_to(repo))
    baseline=safe_relative(repo,repo/campaign['baseline']['character_relative_path']);(out/'baseline').mkdir()
    for name in ('scene.blend','snapshot.json'):shutil.copy2(baseline.with_name(name),out/'baseline'/name)
    copy_evidence(repo/'.runtime/assets/3d-02/staged-v1',out/'assets/3d-02/staged-v1')
    copy_evidence(repo/'.runtime/assets/3d-03/staged-v1',out/'assets/3d-03/staged-v1')
    history=repo/'exports/3d05-development-backup-20260911T181445Z';target=out/'historical-development';target.mkdir()
    for name in ('INVENTORY.json','PARTS.json','REPRODUCIBILITY.md','LOCAL-VERIFICATION.json'):
        shutil.copy2(history/name,target/name)
    for part in read(history/'PARTS.json')['parts']:
        p=history/part['name']
        if file_digest(p)!=part['sha256'] or p.stat().st_size!=part['bytes']:raise ValueError('Historical archive changed')
        storage_copy(p,target/p.name)
    state={'schema_version':'1.0','experiment_id':'3D-05','status':'GREEN' if accepted else 'YELLOW_AWAITING_DIRECTOR','run_path':str(relative),'execution_source':binding,'evidence_and_export_commit':head,'historical_archive_scope':'Prior attempts through accepted coordinated preview; later closure probes included under runs/3d05-development/','run_artifacts_verified':count,'provider_calls':0,'historical_human_review_seconds':None}
    atomic_json(out/'bundle-source-binding.json',state)
    (out/'REPRODUCIBILITY.md').write_text(f'''# 3D-05 {'accepted' if accepted else 'pending Director review'} evidence

Status: **{state['status']}**. Missing Director acceptance is not GREEN. The original scored YELLOW result and rejected attempts remain historical facts.

The portable report is `results/3d05/closure-v1/REPORT.md`. Review `{relative}/review/video.html` or the three `*-AB.mp4` files for synchronized video playback. The original frame player is `{relative}/review/index.html`. Its source images are unchanged; any player repair has a separate provenance record. Keep `blind-key.json` private from the Director until scoring.

Verify every entry in `inventory.json` by path, bytes and SHA-256 before replay. The historical archive's numbered parts reconstruct a gzip tar; follow its included guide and inventory. It includes native scenes and original images from rejected attempts. No credentials are included. Harmless worker-generated thumbnails referenced by original run manifests are retained; unexpected runtime files are rejected.

Reproduce exact source history and asset layout:

```sh
git clone source-history.bundle reproduced
cd reproduced
python3.12 -m venv .venv
.venv/bin/pip install --require-hashes -r requirements.lock
.venv/bin/pip install --no-deps --no-build-isolation -e .
mkdir -p .runtime/assets/3d-02 .runtime/assets/3d-03
cp -R ../assets/3d-02/staged-v1 .runtime/assets/3d-02/
cp -R ../assets/3d-03/staged-v1 .runtime/assets/3d-03/
mkdir -p {baseline.parent.relative_to(repo)}
cp ../baseline/scene.blend ../baseline/snapshot.json {baseline.parent.relative_to(repo)}/
.venv/bin/python -m pytest -q
.venv/bin/mf3d run-interaction-05 --configuration feasibility/3d/3d-05/closure --output runs/3d05-reproduction --no-render
```

Install the Blender build recorded in the frozen campaign at the configured executable path, or set `BLENDER_BIN` to it. All outer Python dependencies belong in `.venv`; the trusted worker uses Blender's bundled Python. The full command omitting `--no-render` recreates all frames, native failure controls and persistence/replay evidence; `--scored` additionally enforces clean source and frozen toolchain. Running it does not invent a new Director judgment.

`execution-source/` is the exact dispatch revision; `source/` is the final evidence/tooling revision. `source-history.bundle` preserves their Git identities. Input paths, character/native hashes and sword hashes are in the frozen campaign. Native-test staging is explicit above so missing staged assets cannot silently masquerade as a passed native suite. Native tests additionally require their documented opt-in environment setting.

Qualification is limited to scripted kinematic pickup by one stationary admitted rig with a modified sword, closed conservative section proxies, authored digit closure and one bounded timing revision. It does not establish arbitrary asset support, physical grasp, release/drop or moving pickup. Provider cost is $0; total economics remain incomplete because historical engineering/review time was not measured. Fresh Director duration is recorded only when supplied.
''')
    files=[p for p in out.rglob('*') if p.is_file() and p!=out/'inventory.json']
    atomic_json(out/'inventory.json',{'schema_version':'1.0','artifacts':manifest_for(out,files)})
    verified=verify(out,out/'inventory.json');print(json.dumps({'output':str(out),'status':state['status'],'artifacts_verified':verified},indent=2))

if __name__=='__main__':main()
