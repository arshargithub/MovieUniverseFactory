# Runway preview adapter

Narrow integration authorized in planning exchange 79. Not a general Factory provider router or a qualification of generative video.

## Contract and safety

- Fixed `gen4.5`, five seconds, 720:1280, seed 303, default silent MP4. Frozen prompts under `config/series01-motion/`.
- Reuses `BudgetLedger`: USD 5 overall, USD 0.60/request, six maximum requests, two attempts per named treatment; retries use contingency. No automatic generation retries. Policy cannot change on reopen.
- Each request is claimed exclusively, then reserved and persisted as uncertain **before** network submission. Missing/uncertain response IDs require reconciliation, not resubmission. Polling never generates.
- Key loaded only inside trusted provider. Lowercase `runway_api_key` accepted and redacted by shared settings. The adapter alone admits the verified SSD migration `.env` symlink to the user's `.config/movie-factory/.env`; target must still be owned, regular and private. Other links fail closed. Global symlink policy is unchanged.
- API host is fixed, redirects disabled, raw error bodies/headers not printed. Media retrieval uses a separate unauthenticated client, an HTTPS host allowlist, a 50 MB bound and non-overwriting output. Partial downloads are preserved; an operator must reconcile/remove a partial before retrying retrieval. API keys are not passed to Blender or media hosts.
- Output records and signed URLs stay in ignored runtime storage. Successful downloads get SHA-256 hashes. Runtime evidence is not backed up by Git commits.
- Monetary reservations remain outstanding until charges can be independently reconciled. A successful task alone is not a per-task bill; balance observations and pricebook estimates remain explicitly distinguished.

## Existing preview commands

Use `.venv/bin/python -m movie_factory.providers.runway_provider` with `--output .runtime/art-direction/series01-motion-v01` and one of:

- `account`: read API balance/limits and preserve a private timestamped snapshot.
- `budget`: inspect local ledger (currently initializes provider settings as well).
- `poll --name cinematic` (or `illustrated`, `comic`): query existing task only.
- `download --name cinematic`: retain one successful output without overwriting.
- `submit --name NAME --image PATH --prompt-file PATH`: paid, reserved first; do not repeat an existing item. The three initial jobs are already submitted. Do not run this merely to reproduce a status check.

## Verification and limitations

Mocked tests cover key alias/redaction, exact migration-link permission checks, reservation before dispatch, duplicate refusal, ambiguous charge retention, prompt/name validation, per-request and attempt limits, polling without regeneration, restricted downloads and credential exclusion from media requests. Existing provider-budget tests also pass. Whole unit suite: 235 passed after retrieval helper added. No live paid unit tests.

Physical plausibility, aesthetic preference, literal timing control, cross-shot continuity, representation handoffs beyond this single image-to-video input, recovery from all possible filesystem failures and detailed billing reconciliation remain outside that test claim. No general promise of identical re-generation from a seed.

Sources checked 2026-09-18: [API pricing](https://docs.dev.runwayml.com/guides/pricing/), [official request types](https://github.com/runwayml/sdk-python/blob/main/src/runwayml/types/image_to_video_create_params.py), [organization response types](https://github.com/runwayml/sdk-python/blob/main/src/runwayml/types/organization_retrieve_response.py). Pipeline decisions/approval sources are linked in `docs/planning/SERIES_01_ART_DIRECTION_C.md`.
