# Active S3 Backup and Closure Policy

## Purpose

The SSD workspace is the authoritative working copy. A private, verified S3
snapshot is the independent recovery copy while work is active. An archive is
created only when a body of work closes.

Backups and archives have different jobs:

- **Active backup:** recover current work after loss or corruption of the SSD.
- **Closed archive:** preserve a frozen, documented outcome for long-term
  history and reproducibility.

The same immutable, content-addressed S3 objects may support both jobs. Closing
work should normally create a new archive manifest that references verified
objects rather than uploading duplicate payloads.

## Single latest backup retention — adopted by Director396

Director396 explicitly requests one most-recent active project backup in S3 to
control storage costs. This supersedes retaining multiple active snapshot
generations or waiting for a separate grace-period approval for each replacement.
Bucket versioning remains a required storage control; it is not permission to
retain superseded billable backup versions indefinitely.

1. Keep the current verified backup while creating its replacement. Temporary
   overlap is required; never delete first to reduce peak storage.
2. Freeze the intended scope and use the manifest, remote inventory/checksum and
   representative streamed-restore checks below. Upload completion alone is not
   verification. Record a durable receipt for the exact replacement manifest.
3. Promote that replacement only after successful verification. Compute an exact
   deletion plan for superseded active snapshot generations in this project's
   backup namespace. Check that the replacement remains recoverable independently
   of every object/version proposed for deletion.
4. Delete superseded active manifests/receipts and garbage-collect their payloads
   only when no retained manifest references those payloads. Content objects shared
   with the newest backup or separately retained archives must remain. Resolve
   unknown references before garbage collection; no broad bucket deletion/sync.
5. In the versioned bucket, inventory exact superseded version IDs and delete
   eligible old versions too. A delete marker alone does not reclaim their storage.
   This authority covers superseded project-backup material, not unrelated keys,
   archives, access controls, versioning configuration or retention-lock bypass.
6. Verify remote inventory afterward: one recoverable active snapshot generation,
   intact newest manifest/payload references, and no eligible superseded backup
   versions remaining. Record retained/deleted keys/versions and observed storage
   totals. Report actual incomplete cleanup instead of claiming costs were reduced.

This is standing authority for scoped older-backup deletion **after** replacement
verification; do not request the same routine retention approval every time.
Before executing it, record the exact payload/destination/deletion plan, exclusions
and verification results. If creation, verification, promotion or cleanup fails,
preserve the newest verified recovery copy and reconcile the recorded state.
The rule is not a timer/automation and does not delete local project material.

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
8. Apply Director396's single-latest retention transaction above, then verify
   the post-cleanup inventory and replacement recovery references.

## Snapshot scope

The snapshot includes the recoverable project worktree, including tracked and
untracked source, documentation, planning, results, active run evidence, active
assets, replays, and operating ledgers.

This includes irreplaceable native masters, references and active evidence even
when their paths contain `worker` or live under `.runtime`. Classify by recovery
role, not directory name. Capture canonical workflow/budget/knowledge state in a
transaction-consistent way (e.g. SQLite online backup or a verified quiescent
snapshot); do not rely on a casual live database-file copy. Bind the actual
included scope and exclusions in the manifest before upload.

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
5. Retire superseded active snapshots under Director396's verified-replacement
   rule. Separately retained closed archives remain distinct; do not remove a
   payload object while any retained active or archive manifest references it.
6. Local closed material may be removed after the archive is verified. Keep a
   local working cache only when it remains a live dependency.

Director396 supplies the retention decision for superseded active project
backups. Broader S3 expiration, archive retirement or unrelated object deletion
still requires its own authority; it is not implied by project closure.

## Current storage contract

- Bucket: `movie-factory-archive`
- Region: `ca-central-1`
- Content objects: `movie-factory/backup/objects/sha256/<first-two>/<sha256>`
- Snapshot manifests:
  `movie-factory/backup/active/movie-universe-factory/snapshots/<snapshot-id>/manifest.json`

Required bucket controls are S3 Block Public Access, bucket-owner-enforced
ownership, enabled versioning, and default server-side encryption.
