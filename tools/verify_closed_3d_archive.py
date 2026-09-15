#!/usr/bin/env python3
"""Verify the closed-3D content-addressed archive without restoring it to disk."""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path


def aws_json(profile: str, region: str, *args: str) -> dict:
    command = [
        "/usr/local/bin/aws",
        *args,
        "--profile",
        profile,
        "--region",
        region,
        "--output",
        "json",
    ]
    completed = subprocess.run(command, check=True, capture_output=True, text=True)
    return json.loads(completed.stdout)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--bucket", required=True)
    parser.add_argument("--prefix", required=True)
    parser.add_argument("--profile", required=True)
    parser.add_argument("--region", required=True)
    args = parser.parse_args()

    manifest = json.loads(args.manifest.read_text())
    expected = {
        f"{args.prefix.rstrip('/')}/objects/{item['sha256'][:2]}/{item['sha256']}": item
        for item in manifest["objects"]
    }
    listing = aws_json(
        args.profile,
        args.region,
        "s3api",
        "list-objects-v2",
        "--bucket",
        args.bucket,
        "--prefix",
        f"{args.prefix.rstrip('/')}/objects/",
    )
    remote = {item["Key"]: item for item in listing.get("Contents", [])}
    missing = sorted(set(expected) - set(remote))
    unexpected = sorted(set(remote) - set(expected))
    size_mismatches = sorted(
        key
        for key in set(expected) & set(remote)
        if expected[key]["bytes"] != remote[key]["Size"]
    )
    if missing or unexpected or size_mismatches:
        raise SystemExit(
            f"archive mismatch: missing={len(missing)} unexpected={len(unexpected)} "
            f"size_mismatches={len(size_mismatches)}"
        )

    objects_by_size = sorted(manifest["objects"], key=lambda item: item["bytes"])
    sample_indexes = sorted(
        {0, len(objects_by_size) // 4, len(objects_by_size) // 2,
         3 * len(objects_by_size) // 4, len(objects_by_size) - 1}
    )
    checksum_samples = []
    for index in sample_indexes:
        item = objects_by_size[index]
        key = f"{args.prefix.rstrip('/')}/objects/{item['sha256'][:2]}/{item['sha256']}"
        head = aws_json(
            args.profile,
            args.region,
            "s3api",
            "head-object",
            "--bucket",
            args.bucket,
            "--key",
            key,
            "--checksum-mode",
            "ENABLED",
        )
        expected_b64 = base64.b64encode(bytes.fromhex(item["sha256"])).decode("ascii")
        checksum_type = head.get("ChecksumType")
        stored_checksum = head.get("ChecksumSHA256")
        comparable = checksum_type == "FULL_OBJECT"
        checksum_matches = stored_checksum == expected_b64 if comparable else None
        if comparable and not checksum_matches:
            raise SystemExit(f"remote checksum mismatch for {key}")
        if not stored_checksum:
            raise SystemExit(f"remote checksum absent for {key}")
        checksum_samples.append(
            {
                "sha256": item["sha256"],
                "bytes": item["bytes"],
                "checksum_type": checksum_type,
                "ordinary_sha256_comparable": comparable,
                "checksum_matches": checksum_matches,
            }
        )

    restore_item = min(
        objects_by_size,
        key=lambda item: abs(item["bytes"] - 128 * 1024 * 1024),
    )
    restore_key = (
        f"s3://{args.bucket}/{args.prefix.rstrip('/')}/objects/"
        f"{restore_item['sha256'][:2]}/{restore_item['sha256']}"
    )
    process = subprocess.Popen(
        [
            "/usr/local/bin/aws",
            "s3",
            "cp",
            restore_key,
            "-",
            "--profile",
            args.profile,
            "--region",
            args.region,
            "--only-show-errors",
        ],
        stdout=subprocess.PIPE,
    )
    restored_digest = hashlib.sha256()
    restored_bytes = 0
    assert process.stdout is not None
    for chunk in iter(lambda: process.stdout.read(1024 * 1024), b""):
        restored_digest.update(chunk)
        restored_bytes += len(chunk)
    return_code = process.wait()
    restored_sha256 = restored_digest.hexdigest()
    if (
        return_code != 0
        or restored_bytes != restore_item["bytes"]
        or restored_sha256 != restore_item["sha256"]
    ):
        raise SystemExit("streamed restore verification failed")

    manifest_key = (
        f"{args.prefix.rstrip('/')}/manifests/"
        "closed-3d-01-through-06a-manifest.json"
    )
    manifest_head = aws_json(
        args.profile,
        args.region,
        "s3api",
        "head-object",
        "--bucket",
        args.bucket,
        "--key",
        manifest_key,
        "--checksum-mode",
        "ENABLED",
    )
    manifest_sha256 = sha256_file(args.manifest)
    manifest_expected_b64 = base64.b64encode(
        bytes.fromhex(manifest_sha256)
    ).decode("ascii")
    manifest_checksum_type = manifest_head.get("ChecksumType")
    manifest_stream_verified = False
    if manifest_checksum_type == "FULL_OBJECT":
        if manifest_head.get("ChecksumSHA256") != manifest_expected_b64:
            raise SystemExit("remote manifest checksum mismatch")
    else:
        manifest_uri = f"s3://{args.bucket}/{manifest_key}"
        manifest_process = subprocess.Popen(
            [
                "/usr/local/bin/aws",
                "s3",
                "cp",
                manifest_uri,
                "-",
                "--profile",
                args.profile,
                "--region",
                args.region,
                "--only-show-errors",
            ],
            stdout=subprocess.PIPE,
        )
        remote_manifest_digest = hashlib.sha256()
        remote_manifest_bytes = 0
        assert manifest_process.stdout is not None
        for chunk in iter(lambda: manifest_process.stdout.read(1024 * 1024), b""):
            remote_manifest_digest.update(chunk)
            remote_manifest_bytes += len(chunk)
        if (
            manifest_process.wait() != 0
            or remote_manifest_bytes != args.manifest.stat().st_size
            or remote_manifest_digest.hexdigest() != manifest_sha256
        ):
            raise SystemExit("streamed manifest verification failed")
        manifest_stream_verified = True

    receipt = {
        "schema_version": 1,
        "verified_at": datetime.now(timezone.utc).isoformat(),
        "bucket": args.bucket,
        "prefix": args.prefix.rstrip("/") + "/",
        "manifest": {
            "local_path": str(args.manifest),
            "sha256": manifest_sha256,
            "bytes": args.manifest.stat().st_size,
            "remote_version_id": manifest_head.get("VersionId"),
            "remote_checksum_type": manifest_checksum_type,
            "remote_checksum_matches": True,
            "streamed_restore_verified": manifest_stream_verified,
        },
        "inventory": {
            "path_count": manifest["path_count"],
            "object_count": len(remote),
            "object_bytes": sum(item["Size"] for item in remote.values()),
            "exact_key_and_size_match": True,
            "missing": 0,
            "unexpected": 0,
            "size_mismatches": 0,
        },
        "checksum_samples": checksum_samples,
        "streamed_restore": {
            "sha256": restore_item["sha256"],
            "bytes": restored_bytes,
            "matches": True,
        },
        "local_deletion_authorized": False,
    }
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.receipt.with_suffix(args.receipt.suffix + ".tmp")
    temporary.write_text(json.dumps(receipt, indent=2) + "\n")
    temporary.replace(args.receipt)
    print(json.dumps(receipt["inventory"], indent=2))
    print(json.dumps(receipt["streamed_restore"], indent=2))


if __name__ == "__main__":
    main()
