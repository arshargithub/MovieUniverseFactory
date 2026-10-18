"""Read-only official encoder access preflight; never serialize credentials/URLs.

No inference, GPU allocation, weight download, token creation or retry occurs.
Browser approval is distinct from authenticated API access.
"""
import os
import stat
import hashlib
import json
from urllib.parse import urljoin, urlparse
from pathlib import Path

import httpx

from ..settings import _read_dotenv, SettingsError

REPOSITORY = "facebook/dinov3-vitl16-pretrain-lvd1689m"


def download_encoder(root, output):
    """Stage only approved official encoder data locally; credentials stay local.

    Metadata revision pins filenames. TLS redirects lose Authorization and are
    limited to HF download hosts. No Python/pickle files or remote code.
    """
    token = load_token(root)
    if not token:
        raise ValueError("HF credential missing")
    out = Path(output)
    out.mkdir(parents=True, exist_ok=True)
    with httpx.Client(timeout=120, follow_redirects=False, trust_env=False) as client:
        response = client.get(f"https://huggingface.co/api/models/{REPOSITORY}",
                              headers={"Authorization": "Bearer " + token})
        if response.status_code != 200:
            raise ValueError("Official encoder metadata unavailable")
        meta = response.json()
        revision = meta["sha"]
        if len(revision) != 40 or any(c not in "0123456789abcdef" for c in revision):
            raise ValueError("Invalid revision")
        names = {row["rfilename"] for row in meta["siblings"]}
        selected = {"config.json", "model.safetensors"}
        if not selected <= names:
            raise ValueError("Unexpected encoder layout")
        selected |= names & {"LICENSE", "LICENSE.md", "README.md", "preprocessor_config.json"}
        record = {"repository": REPOSITORY, "revision": revision, "files": {}}
        for name in sorted(selected):
            target = out / name
            if target.exists():
                raise ValueError("Preserve existing encoder staging; do not overwrite")
            url = f"https://huggingface.co/{REPOSITORY}/resolve/{revision}/{name}"
            for index in range(6):
                headers = {"Authorization": "Bearer " + token} if index == 0 else {}
                with client.stream("GET", url, headers=headers) as stream:
                    if stream.is_redirect:
                        url = urljoin(url, stream.headers["location"])
                        parsed = urlparse(url)
                        if parsed.scheme != "https" or not any(parsed.hostname == h or parsed.hostname.endswith("." + h) for h in ("huggingface.co", "hf.co")):
                            raise ValueError("Unapproved model download redirect")
                        continue
                    if stream.status_code != 200:
                        raise ValueError("Encoder download unsuccessful")
                    digest = hashlib.sha256()
                    size = 0
                    with target.open("xb") as handle:
                        for chunk in stream.iter_bytes(1024 * 1024):
                            size += len(chunk)
                            if size > 2_000_000_000:
                                raise ValueError("Encoder size ceiling exceeded")
                            digest.update(chunk)
                            handle.write(chunk)
                    record["files"][name] = {"sha256": digest.hexdigest(), "bytes": size}
                    break
            else:
                raise ValueError("Too many redirects")
        (out / "manifest.json").write_text(json.dumps(record, indent=2))
    return record


def load_token(root):
    token = os.environ.get("HF_TOKEN", "").strip()
    if token:
        return token
    path = Path(root) / ".env"
    expected = Path.home() / ".config/movie-factory/.env"
    if path.is_symlink():
        if path.lstat().st_uid != os.getuid() or path.resolve(strict=True) != expected:
            raise SettingsError("Unapproved credential link")
        path = path.resolve(strict=True)
    token = _read_dotenv(path).get("HF_TOKEN", "").strip()
    if token:
        return token
    # Standard explicit Hugging Face login cache only, no credential discovery.
    cache = Path.home() / ".cache/huggingface/token"
    if cache.exists() or cache.is_symlink():
        info = cache.lstat()
        if not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid() or info.st_mode & 0o077 or info.st_size > 4096:
            raise SettingsError("HF token cache requires an owned private regular file")
        return cache.read_text().strip()
    return ""


def check(root, *, client=None):
    try:
        token = load_token(root)
    except (SettingsError, OSError):
        return {"repository": REPOSITORY, "state": "CREDENTIAL_CONFIGURATION_BLOCKED", "gpu_launched": False}
    result = {"repository": REPOSITORY, "credential_present": bool(token),
              "gpu_launched": False, "weights_downloaded": False}
    if not token:
        return dict(result, state="CREDENTIAL_MISSING")
    owned = client is None
    if owned:
        client = httpx.Client(timeout=30, follow_redirects=False, trust_env=False)
    try:
        # Small gated configuration GET proves access without large weight egress.
        response = client.get(f"https://huggingface.co/{REPOSITORY}/resolve/main/config.json",
                              headers={"Authorization": "Bearer " + token})
        result["http_status"] = response.status_code
        # Never return headers, redirected signed URLs, response bodies or errors.
        result["state"] = "ACCESS_CONFIRMED" if response.status_code == 200 else (
            "REDIRECT_REQUIRES_VERIFICATION" if response.is_redirect else "ACCESS_DENIED_OR_UNAVAILABLE")
        return result
    except httpx.HTTPError:
        return dict(result, state="NETWORK_ERROR")
    finally:
        if owned:
            client.close()
