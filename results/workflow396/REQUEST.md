# Director396 — completion protection and one-backup retention

Director adds Git push and S3 backup after the complete framework is implemented and tested. Standing future backup instruction: after a new backup is successfully created and verified, delete older S3 backups so only the most recent backup remains, to control S3 costs.

Current pass: record conditional completion requirements and update project backup policy. No immediate remote push/upload/deletion is requested before implementation/testing. Preserve prior backup until replacement verification. Future execution must inspect exact Git ancestry, backup scope, checksums/restore evidence and safe scoped retention deletion; no unrelated S3 cleanup.
