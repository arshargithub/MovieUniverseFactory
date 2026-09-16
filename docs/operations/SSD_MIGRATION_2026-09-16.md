# External SSD workspace migration

Date: 2026-09-16  
Status: migrated and validated; original local workspace retained as a safety
copy pending separate deletion approval.

## Workspace

- Active path: `/Volumes/MovieFactorySSD/MovieUniverseFactory`
- Volume: `MovieFactorySSD`
- Filesystem: APFS
- Capacity after migration: approximately 918 GiB available
- Previous path: `/Users/adisharma/projects/MovieUniverseFactory`

The Git repository was reconstructed from a verified `git bundle --all`, then
the live working tree was overlaid with metadata, symlinks and hard links
preserved. Git heads and tags have the same aggregate digest in both copies,
and the uncommitted planning work was preserved.

## Credentials and Python

The removable SSD is not encrypted. `.env` therefore remains on the internal
disk at `/Users/adisharma/.config/movie-factory/.env` with mode `0600`; the
workspace `.env` is a symlink to that protected file. Credential contents were
not printed or copied to the SSD.

The project `.venv` was rebuilt on the SSD from the repository's Python
3.12.11 runtime. All dependencies were installed from `requirements.lock`, and
the package was installed in editable mode. No global Python packages were
installed.

## Portability repair

Trusted Demonstrator Blender handlers previously embedded the old absolute
repository path. They now derive the repository root from each handler's
`__file__` path. Historical evidence records retain their original paths.

## Validation

- Source-to-destination content checksum comparison passed for the migrated
  workspace, excluding `.git`, `.venv`, `.cache`, `.env`, worker scratch data
  and `.DS_Store` by design.
- Complete Git object verification passed. One Codex checkpoint tree is
  intentionally dangling in both repository history and does not indicate
  corruption.
- Git heads and tags matched the local source digest.
- Package import and `mf3d --help` resolved from the SSD-local `.venv`.
- Two frozen test fixtures removed during the earlier archival cleanup were
  restored from the verified S3 archive by SHA-256. Only the 365 KB character
  fixture and 9 KB sword fixture were restored.
- Offline suite: 226 passed, 11 deselected.
- Blender 5.2.1 opened the active `sustained-fx/scene.blend` directly from the
  SSD with embedded scripts disabled and exited successfully. The scene emits
  pre-existing missing ear-bone dependency warnings.

## Operating notes

The SSD must be mounted at `/Volumes/MovieFactorySSD` before opening the Codex
project or running Movie Factory. Eject the volume cleanly before disconnecting
it. The old local workspace must not be deleted until the SSD project has been
opened as the active Codex project and the user separately approves removal.
