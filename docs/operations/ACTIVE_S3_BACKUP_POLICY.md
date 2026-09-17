# Active S3 Backup and Closure Policy

## Purpose

The SSD workspace is the authoritative working copy. A private, versioned S3
snapshot is the independent recovery copy while work is active. An archive is
created only when a body of work closes.

Backups and archives have different jobs:

- **Active backup:** recover current work after loss or corruption of the SSD.
- **Closed archive:** preserve a frozen, documented outcome for long-term
  history and reproducibility.

The same immutable, content-addressed S3 objects may support both jobs. Closing
work should normally create a new archive manifest that references verified
objects rather than uploading duplicate payloads.

## Active backup lifecycle

1. Work normally in `/Volumes/MovieFactorySSD/MovieUniverseFactory`.
2. Create an active snapshot at meaningful checkpoints and before destructive,
   migratory, or high-risk operations.
3. Build a SHA-256 manifest before upload. Refuse upload if credential-like
   content is detected.
4. Upload immutable payload objects by digest. Never use a delete-propagating
   sync for the object store.
5. Upload the snapshot manifest with an S3 checksum.
6. Verify bucket privacy, encryption, versioning and ownership controls; verify
   every expected remote key and size; inspect stored checksums; and stream a
   representative object plus the manifest back through SHA-256.
7. Retain the verification receipt with the project. A snapshot is not a usable
   backup until its receipt records a successful remote restore check.

## Snapshot scope

The snapshot includes the recoverable project worktree, including tracked and
untracked source, documentation, planning, results, active run evidence, active
assets, replays, and operating ledgers.

It excludes:

- `.env` and other private environment files;
- `.git` internals;
- `.venv`, Python/test caches, and bundled/reproducible Python runtimes;
- macOS metadata;
- archive/backup staging trees, disposable worker state, and smoke-test copies;
- generated backup manifests and receipts, which are uploaded separately.

The exclusions are recoverable tooling or security boundaries, not project
evidence. If a future workflow adds irreplaceable data beneath an excluded
location, change the policy before relying on the next snapshot.

## Closure and archive transition

When work closes:

1. Stop writers and freeze the accepted state.
2. Create an archive manifest with scope, provenance, acceptance state and
   restoration instructions.
3. Verify all referenced S3 objects and perform a representative restore.
4. Record the archive receipt and mark the work closed.
5. After a stated grace period and explicit approval, retire superseded active
   snapshot manifests. Do not remove a payload object while any retained active
   or archive manifest references it.
6. Local closed material may be removed after the archive is verified. Keep a
   local working cache only when it remains a live dependency.

S3 expiration, garbage collection and object deletion require a separate
retention decision. They are never implied by snapshot creation or project
closure.

## Current storage contract

- Bucket: `movie-factory-archive`
- Region: `ca-central-1`
- Content objects: `movie-factory/backup/objects/sha256/<first-two>/<sha256>`
- Snapshot manifests:
  `movie-factory/backup/active/movie-universe-factory/snapshots/<snapshot-id>/manifest.json`

Required bucket controls are S3 Block Public Access, bucket-owner-enforced
ownership, enabled versioning, and default server-side encryption.
