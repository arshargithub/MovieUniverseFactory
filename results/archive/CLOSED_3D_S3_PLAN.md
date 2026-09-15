# Closed 3D experiment S3 archive

Status: uploaded and independently verified on 2026-09-15. The separately
approved local cleanup completed on the same date. Bucket: private
`movie-factory-archive` in `ca-central-1`, prefix
`movie-factory/history/closed-3d-v1/`.

The archive covers all available closed 3D evidence beginning with 3D-01:
3D-01, 3D-01.1, 3D-02, 3D-03/3D-03.1, 3D-04, 3D-05 and the discontinued
3D-06A work. It includes authoritative exports, historical and failed run
evidence, results/specifications, and staged 3D-02/03 assets. The active
Demonstrator run and its horse/rider assets stay local for the next production
experiment.

The path inventory contains 31,378 entries representing 58.76 GiB. A
content-addressed layout stores 15,788 unique SHA-256 objects totaling 28.66
GiB, avoiding 30.10 GiB of duplicate payload. The path table preserves all
original names and symlinks for reconstruction. `.env`, credentials, worker
runtimes and caches are excluded. A credential-pattern scan found zero candidate
files; `.env.example`, specifications and tests that merely mention setting
names remain valid documentary evidence.

Bucket safeguards verified before upload: all public access blocked, SSE-S3
default encryption, bucket-owner-enforced ownership, and versioning enabled on
2026-09-15. The bucket was empty before this archive.

Cost guard: 28.66 GiB at a deliberately conservative $0.03/GiB-month is
$0.86/month. Approximately 15,800 PUTs are conservatively budgeted below $0.10,
keeping the initial operation under the approved $1 ceiling. This is an upper
bound for this batch, not a reconciled AWS invoice. Retrieval, future versions
and later archives are separate costs.

Upload individual unique objects with AWS CLI checksum support, then upload the
immutable manifest. Verify remote object count and total bytes, inspect stored
checksums, and stream at least one large object back through local SHA-256.
Record remote evidence. Do not delete local files until a precise deletion list
and recovered-space estimate receive separate approval.

## Verification result

The remote prefix contains exactly 15,788 payload objects totaling
30,772,370,396 bytes. Every expected content-addressed key and size matched;
there were zero missing, unexpected or size-mismatched objects. Five objects
were inspected for stored checksum metadata. A 93,266,197-byte payload object
and the multipart reconstruction manifest were streamed back without writing a
second local copy, and both matched their local SHA-256 values. The detailed
receipt is `closed-3d-v1-remote-verification.json`.

The first sync encountered a transient S3 endpoint interruption. It was stopped
after the connection failed, then resumed idempotently after connectivity was
confirmed. The resumed sync completed successfully and the independent audit
above verified the final state.

## Local cleanup result

After separate Director approval, the archived `runs/3d*` trees, large closed
exports, staged 3D-02/03 assets and temporary content-addressed staging tree
were removed locally. A small tracked 3D-05 closure supplement was restored
from Git and retained. Source, tests, specifications, results, archive
manifests and the active Demonstrator run/assets remain local.

Available disk space increased from approximately 7.7 GiB to 38 GiB. The
physical recovery was lower than the 58.83 GiB logical file total because the
filesystem shared some underlying blocks. See `closed-3d-v1-local-cleanup.json`
for the machine-readable receipt.
