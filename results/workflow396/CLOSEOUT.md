# Director396 — completion protection and retention recorded

Adopted standing retention: one latest verified active project backup. Preserve
the prior copy until replacement manifest/inventory/checksum/restore verification
succeeds; then remove superseded active generations and unreferenced eligible
payload/object-version storage. Verify newest recoverability and post-cleanup
inventory. Shared newest/archive dependencies and unrelated S3 material remain
protected; no generic bucket deletion or versioning-policy change.

Full-framework completion now includes tested/migrated implementation, scoped
Git push with remote verification, verified S3 recovery backup, and verified
single-latest retention cleanup. The complete scope clarification395is backfilled
in the release counter and completion contract;396is the current exchange.

Files: `docs/operations/ACTIVE_S3_BACKUP_POLICY.md` and
`docs/planning/WORKFLOW_IMPLEMENTATION_COMPLETION_CONTRACT_396.md`.
`VERIFICATION.json` confirms unchanged canonical production state and native count.
This pass only records the instruction: implementation, remote push, backup and
S3 deletion are NOT_RUN. Existing knowledge-freshness blocks are not waived.

AWS primary documentation corroborates why the retention plan must address object
versions rather than only delete markers:
https://docs.aws.amazon.com/AmazonS3/latest/userguide/DeletingObjectVersions.html
No live bucket/account inventory was requested or read in this pass.

Next: carry the complete integrated framework through implementation, tests and
safe migration, then execute the authorized Git/S3 protection sequence above.
Report exact remote commits, backup/restore receipt and retention deletion evidence;
local policy commits alone do not meet the completion gate.
