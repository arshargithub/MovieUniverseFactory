# Private S3 archive setup — requirements, not transfer authorization

## Inputs needed from the Director

1. AWS account and either an existing private bucket or authorization to create a dedicated bucket.
2. Bucket region and archive prefix, e.g. `movie-factory/history/`. Canada Central (`ca-central-1`) is a reasonable location to consider if no existing regional requirement applies; actual pricing is checked before approval.
3. A named local AWS CLI profile authenticated through IAM Identity Center/SSO or another temporary-credential role. No root access, secrets in chat, or project `.env` additions. AWS CLI is already installed on this Mac; login/account/bucket access has not been tested.
4. Approval for the exact initial archive payload and recurring storage-cost ceiling after inventory/pricing. Retrieval/egress and request costs are distinct from storage. No existing model API allowance authorizes AWS charges.
5. Desired restore speed/retention. Initially keep data in S3 Standard for immediate verification/restoration; consider lifecycle archival only after checking access frequency, minimum-duration charges and restore latency.

## Suggested bucket configuration

Dedicated private bucket; all S3 Block Public Access settings enabled; bucket-owner-enforced object ownership/ACLs disabled; server-side encryption (SSE-S3 is sufficient unless account policy requires KMS); HTTPS-only access; versioning for recovery from accidental replacement. Use immutable run/commit/hash-bound prefixes to avoid unnecessary new versions. Lifecycle may clean up incomplete multipart uploads; no object-expiration/deletion rule without an explicit retention decision.

The upload role should be scoped to the selected bucket/prefix. Needed operations include bucket location/listing, object PUT/GET and attributes/checksum verification, and multipart upload list/abort support. It does not need public ACL or object-delete permission. Bucket configuration is a separate one-time administrative action. KMS use additionally needs appropriate key permissions and cost review.

## Transfer and local cleanup contract

- Inventory selected closed historical runs, scenes and dependencies; preserve failure evidence, manifests and source/evidence bindings. Exclude `.env`, credentials, `.venv` and disposable caches.
- Expand the existing final-cut backup manifest as needed; it is not an inventory of all historical heavy files.
- Avoid building another full-size local archive on the nearly full disk. Upload individual manifest-bound files or bounded chunks, preserving symlink relationships explicitly. Local paths and file hashes form the restore map.
- Verify remote object presence, length and supported checksums, record bucket/key/version/checksum receipts, and download/restore a representative complete scene with dependencies before proposing cleanup. ETag is not a universal SHA-256/content checksum, especially for multipart uploads.
- Remote metadata that merely repeats a locally supplied hash is not independent payload verification. Use S3 checksum semantics correctly and an actual restore comparison.
- Present an exact local-deletion list and recovered-space estimate for approval. No automatic deletion from upload success alone. Preserve compact local reports, indexes, manifests and useful review media.
- Historical horse upstream CC-BY version uncertainty remains recorded; a private archive does not imply redistribution clearance. Do not publish native assets.

No AWS resource, upload, charge or local deletion has been executed by preparing this document.

## Official references checked

- [AWS CLI SSO setup](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-sso.html)
- [S3 Block Public Access](https://docs.aws.amazon.com/AmazonS3/latest/userguide/access-control-block-public-access.html)
- [Default encryption](https://docs.aws.amazon.com/AmazonS3/latest/userguide/default-bucket-encryption.html)
- [S3 storage classes and retrieval trade-offs](https://docs.aws.amazon.com/AmazonS3/latest/userguide/storage-class-intro.html)
- [Lifecycle management](https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lifecycle-mgmt.html)
