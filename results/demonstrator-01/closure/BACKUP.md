# Private backup plan — not transferred

`backup-manifest.json` is a checksum inventory, not a backup. Destination and cost remain unspecified/unapproved. No archive was built; no files were transferred; no off-machine restore is claimed.

The minimal recovery set covers the accepted scene/movie/player/audio and frame symlink targets, validated compressed motion base, original local fixture dependencies, source/tests/toolchain/configuration and documentary bindings. Preserve relative paths and symlinks, or explicitly materialize them during an approved transfer. Exclude `.env`, credentials, `.venv`, caches and unrelated campaigns. Recreate `.venv` using the locked project dependencies; install Blender separately per the existing reproduction guide. Source history should be captured at transfer time in a Git bundle including the final closure commit, then independently hashed; no Git bundle is created now.

This is final-cut recovery, not a complete backup of every historical development attempt. Historical evidence remains local and separately retained. External dependency completeness has not been proven by an off-machine restore. The final scene can render without expanding compressed intermediate scenes; full motion validation requires restoring the archived base and verifying its original hash. See the unchanged reproduction guide.

After destination/cost approval: verify manifest against files, include committed closure/source records, transfer privately, verify destination hashes, and perform a separately bounded restore check. Resolve upstream horse provenance before distribution; do not infer public redistribution permission from private backup planning.
