# Recovering the active Martials project

## Status and scope

Current receipt/report: `results/backup/protect255/` and
[protection/calibration255](../planning/PROTECTION_CALIBRATION_255.md).
The final snapshot `protect255-20261013-final` has passed remote verification;
`final-verification.json` binds its exact manifest. The base snapshot also passed a
61-file accepted-unit recovery test, including both final Blender scene reopens.
The older September17 snapshot and the252 phone-review MP4 are not the full current project.

The active worktree snapshot includes native assets, failed evidence, renders,
source, design, selected music/stems and ledgers. Git independently preserves
committed source/history. Neither alone is the whole project. This task does not
archive/delete active work, publish the film or qualify all source rights.

## If the SSD and Mac are lost

1. On a replacement machine, recover GitHub access and AWS SSO access from the
   account owner's independent account/password/MFA recovery arrangements. Those
   arrangements are not verified here. Secrets are deliberately **not** in S3 or
   Git. Recreate credentials in protected local storage, never on an unencrypted
   removable SSD. Git/S3 recovery does not restore ChatGPT/Codex chat UI history;
   sanitized project decision/audit records are separate.
2. Clone `https://github.com/arshargithub/MovieUniverseFactory` and verify the
   recorded remote commit. Read the latest recovery receipt, not just `HEAD` or
   an old “backup complete” paragraph. Do not execute asset-embedded scripts.
3. Fetch the named manifest under
   `s3://movie-factory-archive/movie-factory/backup/active/movie-universe-factory/snapshots/`
   in `ca-central-1`. Verify its SHA256 against the receipt. Each payload object is
   at `movie-factory/backup/objects/sha256/<first-two>/<sha256>`.
4. Restore into a **new empty root**. Validate every relative path against traversal
   and external symlink escape; materialize files from their object hashes, verify
   SHA256/size, then restore safe relative symlinks. The255 manifest maps three
   historical Mac-root test aliases to relative paths; originals are not edited.
   Check `target_exists` and distinguish dangling historical test aliases from
   required production inputs. Never overwrite the only surviving copy blindly.
5. Recreate the project virtual environment and the recorded Blender/tool versions.
   Environments, credentials and installed applications are excluded from the
   snapshot. Do not assume a FaceBuilder/add-on installation or license transfers
   automatically. Use the setup/lock files; keep outer Python separate from Blender.
6. Verify the accepted-unit capsule: exact20s clean clip SHA256
   `1004ed9f2e06d2eafb008c925eb9d266e8a13b8603086020e28d19e3b606722b`,
   both final natives and their38 declared cache bindings, captions and audio join.
   Open with auto-execution disabled and test dependency resolution from the new
   root, not the old SSD path. A byte-perfect clip alone cannot prove editability.
7. Rebuild the derived knowledge index from reviewed pinned sources; read
   `CURRENT_PRODUCTION_STATE.md`. Director253 approval is provisional for the unit;
   full trailer release, rights and strict renderer replay remain separate.

The media snapshot records a fixed source point. Later Git commits carry closure
receipts and current status; do not overwrite those newer records with the older
snapshot copies. For exact historical reproduction, use the manifest's source
commit in a separate checkout. An operating database recovered from a snapshot
can contain jobs that were still running at capture time: reconcile its later
closure records before resuming any work, rather than treating that stale state
as permission to dispatch jobs.

## Verification boundaries

The full snapshot uses independent local clones/copies, then streamed SHA256 and
credential-pattern checks. SQLite uses a consistent online backup and integrity
check. Pattern screening reduces risk; it is not a mathematical guarantee against
all secrets in arbitrary opaque formats. The one known `sk-` scanner match is a
reviewed SVG mask identifier, bound to its exact file hash.

Remote success requires every expected object key/size, checksum inspection,
manifest restoration and a representative restored dependency set. S3 receipts
must distinguish a local rehearsal, a remote byte restore, an actual native reopen
and a full re-render. They are different evidence. Full disaster restoration of
every historical experiment is not claimed by a representative test.

Keep the local immutable staging tree until remote verification and an explicit
retention decision; it can occupy approximately136GB if the filesystem cannot
share copy-on-write blocks. No deletion is authorized by this procedure.
