"""Authoritative, credential-free 3D-04 evidence export."""
from __future__ import annotations

import io
import json
import shutil
import subprocess
import tarfile
from pathlib import Path

from .packages import atomic_json,file_digest,manifest_for,safe_relative


def _read(path:Path)->dict: return json.loads(path.read_text())


def _extract_commit(repo:Path,commit:str,destination:Path)->None:
    paths=["src","tests","config","schemas","feasibility","docs","prior-art",
           "MOVIE_FACTORY_3D_FEASIBILITY_SPEC.md","README.md","SETUP_README.md","requirements.lock",
           "pyproject.toml",".python-version",".env.example","AGENTS.md"]
    if subprocess.run(["git","cat-file","-e",f"{commit}:results/3d04"],cwd=repo,
                      stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode==0:
        paths.append("results/3d04")
    archive=subprocess.run(["git","archive",commit,*paths],cwd=repo,check=True,capture_output=True)
    destination.mkdir(parents=True)
    with tarfile.open(fileobj=io.BytesIO(archive.stdout),mode="r:") as bundle:
        bundle.extractall(destination,filter="data")


def _verify_manifest(root:Path,manifest_path:Path)->int:
    manifest=_read(manifest_path)
    for item in manifest["artifacts"]:
        artifact=safe_relative(root,root/item["path"])
        if not artifact.is_file() or artifact.stat().st_size!=item["bytes"] or file_digest(artifact)!=item["sha256"]:
            raise ValueError("Evidence manifest mismatch: "+item["path"])
    return len(manifest["artifacts"])


def _reproducibility_text(summary:dict,control:dict)->str:
    accepted=Path(summary["run_path"]); controls=Path(control["run_path"])
    return f"""# Reproducing the 3D-04 GREEN evidence

This bundle is credential-free. `execution-source/` is the exact source revision used for the accepted scored run. `control-source/` is the revision used to build and measure the Blender scene-level failure controls. `source/` contains the final evidence and export tooling.

The accepted run is in `{accepted.as_posix()}` and the separate failure-control addendum is in `{controls.as_posix()}`. The accepted run was not modified by the control campaign. Open `{(accepted/'review/index.html').as_posix()}` for the complete synchronized playback. The original broken player remains at `{(accepted/'review/index-original-broken.html').as_posix()}` and its provenance is `{(accepted/'review/player-repair.json').as_posix()}`; all reviewed PNGs retain their pre-repair hashes.

Verify every bundle file from the bundle root:

```sh
cd source
python3 -m venv .venv
.venv/bin/pip install --require-hashes -r requirements.lock
cd ..
source/.venv/bin/python - <<'PY'
import hashlib, json, pathlib
root = pathlib.Path('.')
manifest = json.loads((root / 'inventory.json').read_text())
for item in manifest['artifacts']:
    path = root / item['path']
    assert path.stat().st_size == item['bytes']
    assert hashlib.sha256(path.read_bytes()).hexdigest() == item['sha256']
print(len(manifest['artifacts']), 'artifacts verified')
PY
```

To recreate the paths expected by the frozen configuration and opt-in native tests:

```sh
mkdir -p source/.runtime/assets/3d-03/staged-v1
cp -R assets/admitted-staging/. source/.runtime/assets/3d-03/staged-v1/
mkdir -p source/runs/3d031/character-v2-20260911T012644Z-2d7d8605/initial/build
cp baseline/scene.blend baseline/snapshot.json source/runs/3d031/character-v2-20260911T012644Z-2d7d8605/initial/build/
```

Run the offline suite from `source/` with `.venv/bin/pytest -q`. Run the native Blender control regression with `MF_NATIVE_TEST=1 .venv/bin/pytest tests/native/test_character_assets.py -q -m blender -k performance_scene_controls`. Re-running the full authoritative control command additionally requires copying the accepted run into `source/{accepted.parent.as_posix()}/` so its complete manifest can be verified; then use `mf3d run-performance-controls-04 --accepted-run {accepted.as_posix()} --output runs/3d04-controls`.

The qualified boundary remains one admitted rig, one in-place treadmill run, one structured pelvis-and-chest edit, and frames 40–70. Contact preservation is relative to the treadmill baseline; it does not establish a stationary world-space planted foot during forward locomotion. Provider cost was $0.00. Total production economics remain incomplete because human review time was not recorded.
"""


def export_performance_04(repo:Path,destination:Path)->dict:
    repo=repo.resolve(); destination=destination.resolve()
    if destination.exists(): raise FileExistsError(destination)
    safe_relative(repo,destination)
    compact=repo/"results/3d04"; summary=_read(compact/"summary.json")
    control=_read(compact/"control-addendum.json")
    if summary.get("decision")!="GREEN" or summary.get("director_status")!="ACCEPTED" or not control.get("passed"):
        raise ValueError("3D-04 evidence and Blender control addendum must be accepted")
    compact_count=_verify_manifest(compact,compact/"manifest.json")
    accepted=safe_relative(repo,repo/summary["run_path"]); controls=safe_relative(repo,repo/control["run_path"])
    accepted_count=_verify_manifest(accepted,accepted/"artifact-manifest.json")
    control_count=_verify_manifest(controls,controls/"artifact-manifest.json")
    for required in (accepted/"build/scene.blend",accepted/"replay/build/scene.blend",accepted/"review/index.html",
                     accepted/"review/index-original-broken.html",accepted/"review/player-repair.json",
                     controls/"result.json",controls/"no_op/build/scene.blend",
                     controls/"edit_every_cycle/build/scene.blend",controls/"boundary_leakage/build/scene.blend",
                     controls/"support_foot_slide/build/scene.blend"):
        if not required.is_file(): raise ValueError("Required 3D-04 evidence is missing: "+str(required))
    shutil.copytree(compact,destination/"results/3d04")
    shutil.copytree(accepted,destination/summary["run_path"])
    shutil.copytree(controls,destination/control["run_path"])
    campaign=_read(compact/"frozen-campaign.json"); baseline=safe_relative(repo,repo/campaign["baseline"]["relative_path"])
    (destination/"baseline").mkdir(parents=True)
    shutil.copy2(baseline,destination/"baseline/scene.blend")
    shutil.copy2(baseline.with_name("snapshot.json"),destination/"baseline/snapshot.json")
    shutil.copytree(repo/".runtime/assets/3d-03/staged-v1",destination/"assets/admitted-staging")
    execution_commit=summary["execution_source_commit"]; control_commit=control["source_commit"]
    final_commit=subprocess.run(["git","rev-parse","HEAD"],cwd=repo,text=True,capture_output=True,check=True).stdout.strip()
    final_tree=subprocess.run(["git","rev-parse","HEAD^{tree}"],cwd=repo,text=True,capture_output=True,check=True).stdout.strip()
    tag_commit=subprocess.run(["git","rev-parse","3d-04-v1-green-evidence-v2^{}"],cwd=repo,text=True,capture_output=True,check=True).stdout.strip()
    if final_commit!=tag_commit: raise ValueError("Final source must equal the complete 3D-04 evidence tag")
    _extract_commit(repo,execution_commit,destination/"execution-source")
    _extract_commit(repo,control_commit,destination/"control-source")
    _extract_commit(repo,final_commit,destination/"source")
    atomic_json(destination/"bundle-source-binding.json",{
        "schema_version":"1.0","experiment_id":"3D-04","execution_commit":execution_commit,
        "execution_tree":summary["execution_source_tree"],"control_commit":control_commit,
        "control_tree":control["source_tree"],"evidence_and_export_commit":final_commit,
        "evidence_and_export_tree":final_tree,"evidence_tag":"3d-04-v1-green-evidence-v2"})
    atomic_json(destination/"excluded-inventory.json",{
        "schema_version":"1.0","excluded":[".env and credential values",".git history",".venv dependencies",
        "development native-test scratch runs","superseded 3D-04 scored attempt"],
        "note":"Recreate the project-local environment from requirements.lock. No provider call is required."})
    (destination/"REPRODUCIBILITY.md").write_text(_reproducibility_text(summary,control))
    files=[path for path in destination.rglob("*") if path.is_file() and path.name!="inventory.json"]
    inventory={"schema_version":"1.0","experiment_id":"3D-04","artifacts":manifest_for(destination,files)}
    atomic_json(destination/"inventory.json",inventory)
    return {"output":str(destination),"artifacts":len(inventory["artifacts"]),
            "bytes":sum(item["bytes"] for item in inventory["artifacts"]),
            "compact_artifacts":compact_count,"accepted_run_artifacts":accepted_count,
            "control_run_artifacts":control_count,"execution_commit":execution_commit,
            "control_commit":control_commit,"final_commit":final_commit}
