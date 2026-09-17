#!/usr/bin/env python3
"""Verify an active content-addressed S3 snapshot and stream-test restoration."""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path


AWS = "/usr/local/bin/aws"


def aws_json(profile: str, region: str, *args: str) -> dict:
    command = [AWS, *args, "--profile", profile, "--region", region, "--output", "json"]
    result = subprocess.run(command, check=True, capture_output=True, text=True)
    return json.loads(result.stdout)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def stream_sha256(uri: str, profile: str, region: str) -> tuple[int, str]:
    process = subprocess.Popen(
        [AWS, "s3", "cp", uri, "-", "--profile", profile, "--region", region, "--only-show-errors"],
        stdout=subprocess.PIPE,
    )
    digest = hashlib.sha256()
    byte_count = 0
    assert process.stdout is not None
    for chunk in iter(lambda: process.stdout.read(1024 * 1024), b""):
        digest.update(chunk)
        byte_count += len(chunk)
    if process.wait() != 0:
        raise RuntimeError(f"S3 stream failed: {uri}")
    return byte_count, digest.hexdigest()


def bucket_controls(profile: str, region: str, bucket: str) -> dict:
    public = aws_json(profile, region, "s3api", "get-public-access-block", "--bucket", bucket)
    versioning = aws_json(profile, region, "s3api", "get-bucket-versioning", "--bucket", bucket)
    encryption = aws_json(profile, region, "s3api", "get-bucket-encryption", "--bucket", bucket)
    ownership = aws_json(profile, region, "s3api", "get-bucket-ownership-controls", "--bucket", bucket)
    block = public.get("PublicAccessBlockConfiguration", {})
    if not all(block.get(name) is True for name in (
        "BlockPublicAcls", "IgnorePublicAcls", "BlockPublicPolicy", "RestrictPublicBuckets"
    )):
        raise RuntimeError("S3 Block Public Access is incomplete")
    if versioning.get("Status") != "Enabled":
        raise RuntimeError("S3 bucket versioning is not enabled")
    algorithms = {
        rule.get("ApplyServerSideEncryptionByDefault", {}).get("SSEAlgorithm")
        for rule in encryption.get("ServerSideEncryptionConfiguration", {}).get("Rules", [])
    }
    if not algorithms.intersection({"AES256", "aws:kms", "aws:kms:dsse"}):
        raise RuntimeError("S3 default server-side encryption is absent")
    rules = ownership.get("OwnershipControls", {}).get("Rules", [])
    if not any(rule.get("ObjectOwnership") == "BucketOwnerEnforced" for rule in rules):
        raise RuntimeError("S3 bucket-owner-enforced ownership is absent")
    return {
        "block_public_access": True,
        "versioning": "Enabled",
        "server_side_encryption": sorted(algorithm for algorithm in algorithms if algorithm),
        "object_ownership": "BucketOwnerEnforced",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--bucket", required=True)
    parser.add_argument("--object-prefix", required=True)
    parser.add_argument("--manifest-key", required=True)
    parser.add_argument("--profile", required=True)
    parser.add_argument("--region", required=True)
    args = parser.parse_args()

    manifest = json.loads(args.manifest.read_text())
    controls = bucket_controls(args.profile, args.region, args.bucket)
    object_prefix = args.object_prefix.rstrip("/")
    expected = {
        f"{object_prefix}/{item['sha256'][:2]}/{item['sha256']}": item
        for item in manifest["objects"]
    }
    listing = aws_json(
        args.profile, args.region, "s3api", "list-objects-v2",
        "--bucket", args.bucket, "--prefix", object_prefix + "/",
    )
    remote = {item["Key"]: item for item in listing.get("Contents", [])}
    missing = sorted(set(expected) - set(remote))
    size_mismatches = sorted(
        key for key in set(expected) & set(remote) if expected[key]["bytes"] != remote[key]["Size"]
    )
    if missing or size_mismatches:
        raise SystemExit(f"backup mismatch: missing={len(missing)} size_mismatches={len(size_mismatches)}")

    objects_by_size = sorted(manifest["objects"], key=lambda item: item["bytes"])
    indexes = sorted({0, len(objects_by_size) // 4, len(objects_by_size) // 2,
                      3 * len(objects_by_size) // 4, len(objects_by_size) - 1})
    checksum_samples = []
    for index in indexes:
        item = objects_by_size[index]
        key = f"{object_prefix}/{item['sha256'][:2]}/{item['sha256']}"
        head = aws_json(
            args.profile, args.region, "s3api", "head-object", "--bucket", args.bucket,
            "--key", key, "--checksum-mode", "ENABLED",
        )
        stored = head.get("ChecksumSHA256")
        checksum_type = head.get("ChecksumType")
        comparable = checksum_type == "FULL_OBJECT"
        matches = stored == base64.b64encode(bytes.fromhex(item["sha256"])).decode("ascii") if comparable else None
        if not stored or (comparable and not matches):
            raise SystemExit(f"remote checksum verification failed for {key}")
        checksum_samples.append({
            "sha256": item["sha256"], "bytes": item["bytes"],
            "checksum_type": checksum_type, "ordinary_sha256_comparable": comparable,
            "checksum_matches": matches,
        })

    restore_item = min(objects_by_size, key=lambda item: abs(item["bytes"] - 128 * 1024 * 1024))
    restore_key = f"{object_prefix}/{restore_item['sha256'][:2]}/{restore_item['sha256']}"
    restored_bytes, restored_sha256 = stream_sha256(
        f"s3://{args.bucket}/{restore_key}", args.profile, args.region
    )
    if restored_bytes != restore_item["bytes"] or restored_sha256 != restore_item["sha256"]:
        raise SystemExit("representative streamed restore verification failed")

    manifest_head = aws_json(
        args.profile, args.region, "s3api", "head-object", "--bucket", args.bucket,
        "--key", args.manifest_key, "--checksum-mode", "ENABLED",
    )
    local_manifest_sha256 = sha256_file(args.manifest)
    remote_manifest_bytes, remote_manifest_sha256 = stream_sha256(
        f"s3://{args.bucket}/{args.manifest_key}", args.profile, args.region
    )
    if remote_manifest_bytes != args.manifest.stat().st_size or remote_manifest_sha256 != local_manifest_sha256:
        raise SystemExit("streamed manifest verification failed")

    receipt = {
        "schema_version": 1,
        "kind": "active-project-backup-verification",
        "snapshot_id": manifest["snapshot_id"],
        "verified_at": datetime.now(timezone.utc).isoformat(),
        "bucket": args.bucket,
        "region": args.region,
        "bucket_controls": controls,
        "object_prefix": object_prefix + "/",
        "manifest": {
            "local_path": str(args.manifest),
            "remote_key": args.manifest_key,
            "sha256": local_manifest_sha256,
            "bytes": args.manifest.stat().st_size,
            "remote_version_id": manifest_head.get("VersionId"),
            "remote_checksum_type": manifest_head.get("ChecksumType"),
            "streamed_restore_verified": True,
        },
        "inventory": {
            "path_count": manifest["path_count"],
            "expected_object_count": len(expected),
            "expected_object_bytes": sum(item["bytes"] for item in expected.values()),
            "available_object_store_count": len(remote),
            "all_expected_keys_and_sizes_match": True,
            "missing": 0,
            "size_mismatches": 0,
        },
        "checksum_samples": checksum_samples,
        "streamed_restore": {
            "remote_key": restore_key,
            "sha256": restored_sha256,
            "bytes": restored_bytes,
            "matches": True,
        },
        "recovery_copy_verified": True,
    }
    args.receipt.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.receipt.with_suffix(args.receipt.suffix + ".tmp")
    temporary.write_text(json.dumps(receipt, indent=2) + "\n")
    temporary.replace(args.receipt)
    print(json.dumps(receipt["bucket_controls"], indent=2))
    print(json.dumps(receipt["inventory"], indent=2))
    print(json.dumps(receipt["streamed_restore"], indent=2))


if __name__ == "__main__":
    main()
