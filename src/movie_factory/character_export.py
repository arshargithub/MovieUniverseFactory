"""Authoritative, credential-free 3D-03.1 evidence bundle."""
from __future__ import annotations

import io
import json
import shutil
import subprocess
import tarfile
from pathlib import Path

from .packages import atomic_json,file_digest,manifest_for,safe_relative


def _read(path:Path): return json.loads(path.read_text())


def _extract_commit(repo:Path,commit:str,destination:Path)->None:
    paths=["src","tests","config","schemas","feasibility","docs","prior-art",
           "MOVIE_FACTORY_3D_FEASIBILITY_SPEC.md","README.md","SETUP_README.md","requirements.lock",
           "pyproject.toml",".python-version",".env.example","AGENTS.md"]
    has_results=subprocess.run(["git","cat-file","-e",f"{commit}:results/3d031"],cwd=repo,
                               stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL).returncode==0
    if has_results: paths.append("results/3d031")
    archive=subprocess.run(["git","archive",commit,*paths],cwd=repo,check=True,capture_output=True)
    destination.mkdir(parents=True)
    with tarfile.open(fileobj=io.BytesIO(archive.stdout),mode="r:") as bundle:
        bundle.extractall(destination,filter="data")


def export_character_031(repo:Path,destination:Path)->dict:
    destination=destination.resolve()
    if destination.exists(): raise FileExistsError(destination)
    safe_relative(repo,destination)
    summary=_read(repo/"results/3d031/summary.json")
    if summary.get("decision")!="GREEN" or summary.get("director_status")!="ACCEPTED":
        raise ValueError("3D-03.1 evidence is not accepted GREEN")
    compact=repo/"results/3d031"; compact_manifest=_read(compact/"manifest.json")
    for artifact in compact_manifest["artifacts"]:
        path=safe_relative(compact,compact/artifact["path"])
        if not path.is_file() or path.stat().st_size!=artifact["bytes"] or file_digest(path)!=artifact["sha256"]:
            raise ValueError("Compact evidence manifest mismatch: "+artifact["path"])
    qualification=safe_relative(repo,repo/"runs/3d031"/summary["qualification_run"])
    temporal=safe_relative(repo,repo/"runs/3d031-motion"/summary["temporal_run"])
    replay=safe_relative(repo,repo/summary["replay_run"])
    diagnostic=safe_relative(repo,repo/"runs/3d031-diagnostic/parent-evaluation-v4")
    for required in (qualification/"initial/build/scene.blend",qualification/"revision/build/scene.blend",
                     temporal/"review.html",temporal/"worker/temporal-metrics.json",replay/"replay-result.json",
                     diagnostic/"diagnostic.json"):
        if not required.is_file(): raise ValueError("Required 3D-03.1 evidence is missing: "+str(required))
    shutil.copytree(compact,destination/"results/3d031")
    shutil.copytree(qualification,destination/"runs/3d031"/qualification.name)
    shutil.copytree(temporal,destination/"runs/3d031-motion"/temporal.name)
    shutil.copytree(replay,destination/summary["replay_run"])
    shutil.copytree(diagnostic,destination/"runs/3d031-diagnostic"/diagnostic.name)
    shutil.copytree(repo/".runtime/assets/3d-03/staged-v1",destination/"assets/admitted-staging")
    shutil.copytree(repo/".runtime/assets/3d-03/source",destination/"assets/original-archive")
    execution_commit=summary["source_commit"]
    final_commit=subprocess.run(["git","rev-parse","HEAD"],cwd=repo,text=True,capture_output=True,check=True).stdout.strip()
    final_tree=subprocess.run(["git","rev-parse","HEAD^{tree}"],cwd=repo,text=True,capture_output=True,check=True).stdout.strip()
    _extract_commit(repo,execution_commit,destination/"execution-source")
    _extract_commit(repo,final_commit,destination/"source")
    atomic_json(destination/"bundle-source-binding.json",{
        "schema_version":"1.0","experiment_id":"3D-03.1","execution_commit":execution_commit,
        "execution_tree":summary["source_tree"],"evidence_and_export_commit":final_commit,
        "evidence_and_export_tree":final_tree,"evidence_tag":"3d-03-1-v1-green-evidence"})
    atomic_json(destination/"excluded-inventory.json",{
        "schema_version":"1.0","excluded":[".env and credential values",".git history",".venv dependencies",
        "superseded implementation attempts except the authoritative diagnostic","local caches"],
        "note":"Recreate the project-local environment from requirements.lock. No provider call is required."})
    (destination/"REPRODUCIBILITY.md").write_text(
        "# Reproducing the 3D-03.1 GREEN bundle\n\n"
        "`execution-source/` is the exact source revision that produced the accepted qualification. "
        "`source/` contains the final regression, validation, and export tooling. Native baseline and revised scenes, "
        "all 63 temporal frames, contact sheets, playback HTML, the offline replay, and the causal diagnostic are included.\n\n"
        "Create `source/.venv` using `source/SETUP_README.md`; install nothing globally and do not add credentials. "
        "From `source/`, run `.venv/bin/pytest -q`. For native regressions, run "
        "`MF_NATIVE_TEST=1 .venv/bin/pytest tests/native/test_character_assets.py -q -m blender`.\n\n"
        "Review the accepted playback under `runs/3d031-motion/` and the closure report at "
        "`results/3d031/REPORT.md`. Use `mf3d replay-character` with the included qualification run to repeat the "
        "structured revision without provider calls. A fresh visual qualification requires its own Director review.\n")
    files=[path for path in destination.rglob("*") if path.is_file() and path.name!="inventory.json"]
    inventory={"schema_version":"1.0","experiment_id":"3D-03.1","artifacts":manifest_for(destination,files)}
    atomic_json(destination/"inventory.json",inventory)
    return {"output":str(destination),"artifacts":len(inventory["artifacts"]),
            "bytes":sum(item["bytes"] for item in inventory["artifacts"]),"execution_commit":execution_commit,
            "final_commit":final_commit}
