"""Bounded image-to-video preview adapter. No automatic POST retries.

Contract/pricing verified 2026-09-18 against docs.dev.runwayml.com and
runwayml/sdk-python types. Fixed gen4.5 / 5s / 720:1280 / default MP4.
Reservations remain unknown until independently reconciled; success is not
creative acceptance or evidence of a per-task invoice.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import re
import uuid
from urllib.parse import urlparse

import httpx

from ..budget import BudgetLedger
from ..settings import load_settings, SettingsError, _read_dotenv
from ..telemetry import utc_now


class RunwayError(RuntimeError):
    pass


def load_runway_key(root):
    """Honor only the verified SSD migration link, not arbitrary secret links."""
    path = Path(root) / ".env"
    if path.is_symlink():
        target = path.resolve(strict=True)
        expected = Path.home() / ".config/movie-factory/.env"
        if target != expected or path.lstat().st_uid != os.getuid():
            raise SettingsError("Unapproved credential symlink")
        # Existing parser checks regular-file ownership, size, 0600 and names.
        values = _read_dotenv(target)
        local = Path(root) / ".env.local"
        values.update(_read_dotenv(local))
        return os.environ.get("RUNWAY_API_KEY", os.environ.get("runway_api_key",
            values.get("RUNWAY_API_KEY", "")))
    return load_settings(root)["RUNWAY_API_KEY"]


def save_json(path, value):
    path = Path(path)
    temp = path.with_name(path.name + ".tmp-" + uuid.uuid4().hex)
    fd = os.open(temp, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "w") as f:
        json.dump(value, f, indent=2)
        f.write("\n")
        f.flush()
        os.fsync(f.fileno())
    os.replace(temp, path)


class RunwayProvider:
    def __init__(self, root: Path, output: Path, *, client=None):
        self.output = Path(output)
        self.output.mkdir(parents=True, exist_ok=True)
        self.ledger = BudgetLedger(self.output / "budget.jsonl", campaign_limit=5,
            scope_limits={"scored": 3, "contingency": 2},
            stage_limits={"preview": (5, 6)}, request_limit=6,
            request_ceiling_usd=.6, work_item_attempt_limit=2)
        if client is None:
            key = load_runway_key(root)
            if not key:
                raise RunwayError("RUNWAY_API_KEY is missing")
            client = httpx.Client(base_url="https://api.dev.runwayml.com",
                headers={"Authorization": "Bearer " + key,
                         "X-Runway-Version": "2024-11-06"},
                timeout=60, follow_redirects=False)
        self.client = client

    def _request(self, method, path, payload=None):
        try:
            r = self.client.request(method, path, json=payload)
            if r.status_code >= 300:
                raise RunwayError(f"Runway HTTP {r.status_code}; no automatic retry")
            data = r.json()
            if not isinstance(data, dict):
                raise ValueError
            return data
        except RunwayError:
            raise
        except Exception:
            # Never echo response bodies, headers, credentials or signed URLs.
            raise RunwayError("Runway transport/response error; reconcile before retry") from None

    def account(self):
        data = self._request("GET", "/v1/organization")
        allowed = {k: data[k] for k in ("creditBalance", "tier", "usage", "limits") if k in data}
        allowed["observed_utc"] = utc_now()
        save_json(self.output / ("account-" + uuid.uuid4().hex + ".json"), allowed)
        return allowed

    def submit(self, name, image, prompt, *, attempt=1):
        if not re.fullmatch(r"[a-z][a-z0-9-]{0,50}", name) or attempt not in (1, 2):
            raise RunwayError("Invalid work item")
        if not isinstance(prompt, str) or not 1 <= len(prompt.encode("utf-16-le")) // 2 <= 1000:
            raise RunwayError("Prompt must be 1-1000 UTF-16 units")
        raw = Path(image).read_bytes()
        if not raw.startswith(b"\x89PNG\r\n\x1a\n") or len(raw) > 3_500_000:
            raise RunwayError("Input must be a PNG below 3.5 MB")
        path = self.output / f"{name}-{attempt}.json"
        # Exclusive file creation claims this work item before reserving/dispatch.
        try:
            fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        except FileExistsError:
            raise RunwayError("Work item already exists; poll/reconcile, never redispatch") from None
        with os.fdopen(fd, "w") as f:
            f.write('{"status":"CLAIMED"}\n')
            f.flush()
            os.fsync(f.fileno())
        reservation = self.ledger.reserve(run_id="motion-preview", stage="preview",
            scope="scored" if attempt == 1 else "contingency", amount_usd=.6,
            purpose=name, model="gen4.5", prompt_hash=hashlib.sha256(prompt.encode()).hexdigest())
        record = {"name": name, "attempt": attempt, "reservation_id": reservation,
            "submitted_utc": utc_now(), "status": "DISPATCH_UNCERTAIN", "model": "gen4.5",
            "duration": 5, "ratio": "720:1280", "seed": 303, "prompt": prompt,
            "input_sha256": hashlib.sha256(raw).hexdigest(), "estimated_credits": 60,
            "estimated_usd": .6, "actual_cost_usd": None}
        save_json(path, record)
        data = self._request("POST", "/v1/image_to_video", {
            "model": "gen4.5", "duration": 5, "ratio": "720:1280", "seed": 303,
            "promptText": prompt, "promptImage": "data:image/png;base64," + base64.b64encode(raw).decode()})
        try:
            task_id = str(uuid.UUID(data["id"]))
        except (KeyError, ValueError, TypeError):
            raise RunwayError("Missing task ID; reservation retained, do not resubmit") from None
        record.update(task_id=task_id, status="PENDING")
        save_json(path, record)
        return {"name": name, "task_id": task_id, "status": "PENDING"}

    def poll(self, name, attempt=1):
        if not re.fullmatch(r"[a-z][a-z0-9-]{0,50}", name) or attempt not in (1, 2):
            raise RunwayError("Invalid work item")
        path = self.output / f"{name}-{attempt}.json"
        record = json.loads(path.read_text())
        task_id = str(uuid.UUID(record["task_id"]))
        data = self._request("GET", "/v1/tasks/" + task_id)
        record.update(status=data.get("status", "UNKNOWN"), checked_utc=utc_now())
        if record["status"] == "SUCCEEDED":
            # Signed URLs retained privately for artifact retrieval, never printed.
            record["output"] = data.get("output", [])
        elif record["status"] in {"FAILED", "CANCELED"}:
            record["failure_code"] = data.get("failureCode")
        save_json(path, record)
        return {"name": name, "task_id": task_id, "status": record["status"]}

    def download(self, name, attempt=1):
        """Retain generated project assets; never send the API key to the CDN."""
        if not re.fullmatch(r"[a-z][a-z0-9-]{0,50}", name) or attempt not in (1, 2):
            raise RunwayError("Invalid work item")
        path = self.output / f"{name}-{attempt}.json"
        record = json.loads(path.read_text())
        if record.get("status") != "SUCCEEDED" or len(record.get("output", [])) != 1:
            raise RunwayError("Expected one successful video output")
        url = record["output"][0]
        parsed = urlparse(url)
        host = parsed.hostname or ""
        if parsed.scheme != "https" or parsed.username or parsed.password or not any(
            host == domain or host.endswith("." + domain)
            for domain in ("runwayml.com", "runwayml.cloud", "cloudfront.net", "runwaycdn.com")):
            raise RunwayError("Output host requires review before download")
        destination = self.output / f"{name}-{attempt}.mp4"
        if destination.exists():
            raise RunwayError("Output already exists; verify rather than overwrite")
        partial = destination.with_suffix(".mp4.partial")
        digest = hashlib.sha256()
        size = 0
        try:
            with httpx.stream("GET", url, timeout=60, follow_redirects=False) as r:
                r.raise_for_status()
                with partial.open("xb") as f:
                    for chunk in r.iter_bytes():
                        size += len(chunk)
                        if size > 50_000_000: raise RunwayError("Video exceeds 50 MB limit")
                        digest.update(chunk)
                        f.write(chunk)
                    f.flush()
                    os.fsync(f.fileno())
            partial.rename(destination)
        except Exception:
            raise RunwayError("Download incomplete; partial retained, no generation retried") from None
        record.update(local_file=destination.name, output_sha256=digest.hexdigest(), output_bytes=size)
        save_json(path, record)
        return {"name": name, "local_file": str(destination), "bytes": size, "sha256": digest.hexdigest()}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("command", choices=["account", "submit", "poll", "download", "budget"])
    p.add_argument("--root", type=Path, default=Path.cwd())
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--name")
    p.add_argument("--image", type=Path)
    p.add_argument("--prompt-file", type=Path)
    p.add_argument("--attempt", type=int, default=1)
    a = p.parse_args()
    try:
        provider = RunwayProvider(a.root, a.output)
        if a.command == "account": result = provider.account()
        elif a.command == "budget": result = provider.ledger.summary()
        elif a.command == "poll": result = provider.poll(a.name, a.attempt)
        elif a.command == "download": result = provider.download(a.name, a.attempt)
        else: result = provider.submit(a.name, a.image, a.prompt_file.read_text(), attempt=a.attempt)
        print(json.dumps(result))
    except Exception as e:
        # Do not print arbitrary exception bodies or traceback locals.
        print(json.dumps({"error": str(e) if isinstance(e, (RunwayError, SettingsError)) else type(e).__name__}))
        raise SystemExit(1) from None


if __name__ == "__main__":
    main()
