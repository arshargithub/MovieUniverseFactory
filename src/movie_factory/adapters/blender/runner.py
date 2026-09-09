"""Bounded subprocess execution of the trusted Blender adapter.

The environment allowlist is credential hygiene, not an OS security sandbox.
The controller must validate paths, packages and operation schemas before dispatch.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import time


def run_blender(job: dict, *, blender_bin: str, timeout: float = 300) -> dict:
    """Run one immutable input job, retaining diagnostics even on failure."""
    output = Path(job["output_dir"])
    if not output.is_absolute():
        raise ValueError("output_dir must be an absolute path")
    if output.exists() and output.is_symlink():
        raise ValueError("output_dir may not be a symbolic link")
    output.mkdir(parents=True, exist_ok=True, mode=0o700)
    output = output.resolve(strict=True)
    if shutil.disk_usage(output).free < 5_000_000_000:
        raise RuntimeError("Refusing Blender worker: less than 5 GB free on output volume")
    binary = Path(blender_bin).expanduser().resolve(strict=True)
    if not binary.is_file() or not os.access(binary, os.X_OK):
        raise ValueError("Blender executable is not an executable file")
    if timeout <= 0:
        raise ValueError("timeout must be positive")
    runtime = output / ".worker_runtime"
    for name in ("home", "temp", "config", "scripts", "datafiles", "cache"):
        (runtime / name).mkdir(parents=True, exist_ok=True, mode=0o700)
    env = {
        "PATH": "/usr/bin:/bin:/usr/sbin:/sbin",
        "HOME": str(runtime / "home"),
        "TMPDIR": str(runtime / "temp"),
        "XDG_CACHE_HOME": str(runtime / "cache"),
        "BLENDER_USER_CONFIG": str(runtime / "config"),
        "BLENDER_USER_SCRIPTS": str(runtime / "scripts"),
        "BLENDER_USER_DATAFILES": str(runtime / "datafiles"),
        "LANG": "en_US.UTF-8",
        "LC_ALL": "en_US.UTF-8",
    }
    effective_job = {**job, "output_dir": str(output)}
    job_path = output / "job.json"
    job_path.write_text(json.dumps(effective_job, sort_keys=True, indent=2, allow_nan=False) + "\n")
    job_path.chmod(0o600)
    command = [str(binary), "--background", "--factory-startup", "--disable-autoexec",
               "--python-exit-code", "7", "--python", str(Path(__file__).with_name("worker.py")),
               "--", "--job", str(job_path)]
    status_path = output / "worker-status.json"
    if status_path.exists():
        raise ValueError("Worker output already has a status; use a fresh attempt directory")
    started = time.monotonic()
    timed_out = False
    with (output / "stdout.log").open("wb") as stdout, (output / "stderr.log").open("wb") as stderr:
        process = subprocess.Popen(command, env=env, cwd=runtime, stdout=stdout, stderr=stderr,
                                   start_new_session=True)
        try:
            process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            timed_out = True
            os.killpg(process.pid, signal.SIGTERM)
            try:
                process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait()
    elapsed = time.monotonic() - started
    if status_path.is_file():
        try:
            result = json.loads(status_path.read_text())
        except (ValueError, OSError):
            result = {"ok": False, "error": "Worker produced invalid status JSON"}
    else:
        result = {"ok": False, "error": "Worker did not produce status"}
    if timed_out:
        result.update(ok=False, error="Worker exceeded timeout", timed_out=True)
    elif process.returncode:
        result.update(ok=False, error=result.get("error") or "Blender process failed")
    # Caller must still reopen the native file and independently validate artifacts.
    result.update(elapsed=elapsed, exit_code=process.returncode, command=command,
                  environment_names=sorted(env), isolation_mode="trusted_structured_operations",
                  os_sandbox=False)
    (output / "runner-status.json").write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
    return result
