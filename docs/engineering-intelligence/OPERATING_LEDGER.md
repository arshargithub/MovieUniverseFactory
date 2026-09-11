# Experiment operating records

This is a small prospective extension to campaign records, not a replacement harness. Start capture when authorized design work begins. Colour and lifecycle are independent: an experiment may close GREEN, YELLOW, RED or abandoned with findings. A reopen starts a new episode linked by `prior_episode_id`. Post-closure archival maintenance gets its own linked episode, rather than changing the original elapsed time.

3D-05 remains closed YELLOW. Its final scores and unknown historical engineering usage are not changed by this tooling. The existing provider ledger remains the authority for experiment API budgets and charges. No paid engineering calls are introduced.

## Commands and record contract

Run all commands from the repository in its existing `.venv`; no new dependency is needed. The local ledger is `.runtime/experiment-ops.sqlite3`. SQLite transactions prevent torn append records; event IDs make retries idempotent. A different payload with the same ID fails. A correction is a new complete event with `supersedes` naming the previous effective event. Export retains original and superseding events; reports use the effective version. Do not edit or delete prior rows.

```sh
.venv/bin/python -m movie_factory.experiment_ops --help
.venv/bin/python -m movie_factory.experiment_ops emit --experiment 3D-06A --episode first --type start --id 3d06a-start --phase design --fields '{"task_id":"ACTUAL_TASK_ID","reason":"authorized design starts","evidence_ref":"feasibility/3d/3d-06a/SPEC.md"}'
.venv/bin/python -m movie_factory.experiment_ops emit --experiment 3D-06A --episode first --type work_started --id 3d06a-design-start --phase design --fields '{"activity_id":"design-1","actor":"assistant","task_id":"ACTUAL_TASK_ID"}'
```

These are prospective examples, not commands to start 3D-06A during the bookkeeping delivery. Events require `event_id`, `experiment_id`, `episode_id`, explicit UTC, `event_type` and `phase`. Task/turn/run IDs, reason and evidence reference are nullable. Provide actual identifiers where observed, not guesses. `emit` stamps UTC; `append event.json` imports an explicit record. Model observations must state `setting_attribution` (`runtime_turn_context`, `user_reported`, or UNKNOWN), model and effort. A proposed policy is not an observation.

Before yielding for Director input or the next prompt, end the current `work_started` interval with `work_ended` using the same `activity_id`, then emit `wait_started` with a unique `wait_id` and reason. On resumption emit `wait_ended` before starting another activity. An explicit user pause is `user_pause`. Keep genuinely continuing background activities/jobs open; their overlap with a question is work, not excluded waiting. This initial delivery uses explicit commands; it does not install an automatic desktop hook. Missing capture stays visible.

Wait reasons: `director_response`, `next_prompt`, `user_pause`, `provider_limit`, `machine_failure`, `infrastructure`. Only the first three can be excluded. A missing end, a crash, an unexplained gap, an invalid reopen, or a discontinuous clock makes exact net time UNKNOWN. Do not silently bridge an overnight gap with an assistant-work interval. Review duration is a separate `human_review` event with `duration_seconds`; it is not subtracted a second time.

Use the job wrapper for local commands whose duration matters. It records UTC and same-process monotonic boundaries, exit outcome and a unique job ID. `--kind native` is for Blender jobs; ordinary tests and packaging use the default `local`. Killing the wrapper leaves an unmatched start and incomplete coverage, never a fabricated success. The wrapper refuses to redispatch an existing job ID. It runs an explicit trusted command without a shell; it does not bypass structured Blender operation validation or provider budgets.

```sh
.venv/bin/python -m movie_factory.experiment_ops job --experiment SETUP --episode one --phase tests --id unit-check-1 -- .venv/bin/pytest tests/unit/test_experiment_ops.py -q
.venv/bin/python -m movie_factory.experiment_ops report --experiment SETUP --output results/operating-setup
.venv/bin/python -m movie_factory.experiment_ops export --output results/operating-setup/events.json
.venv/bin/python -m movie_factory.experiment_ops demo --output results/operating-demo
```

Record `proxy_observed` increments with `name` and `count` for turns, tool calls, candidate variants, failed attempts and repeated suites when measurable. Each observation needs a unique event ID. They are operational counts, not token estimates. Do not report absent counts as zero. Phase changes are experiment-level; totals subtract the reconciled excluded union. Assistant activity is the union of recorded assistant blocks, not token generation time. The JSON reports both native-job sum and union, and separate known monotonic durations. Job sums are process-seconds, not CPU core-seconds.

Close only after the disposition and compact handoff exist. Include explicit counts `technical_outputs` and `director_outputs` when supported; they are independent of colour. Reports include closed YELLOW/RED work in consumption and show per-closed-episode, per-technical-output and per-Director-output denominators. Missing usage or denominators stay null. Development effort remains separate from repeatable runtime generation cost.

## Usage source and bounded discovery

Read-only capability check on 2026-09-11 found **codex-cli 0.153.4**. The exact current task's local record contained `token_usage_record` entries with thread/turn/session/response IDs, per-response `usage`, cumulative turn/thread counters and explicit categories. Its latest `turn_context` reported `gpt-6-astra`, effort `medium`. This is an observed local setting, not inferred from assistant self-description. No setting was changed.

The [official app-server documentation](https://learn.chatgpt.com/docs/app-server#turn-events) documents `thread/tokenUsage/updated`. The present tool connection has no exposed subscription to that live event. No replacement server was started. The supported event documents the opportunity; the optional local-file parser is a separate version-specific mechanism, not a stable public API.

`engineering_usage.import_rollout` admits only the probed 0.153.4 metadata format. It reads a bounded tail of an explicitly supplied task-local file, selects the exact thread ID and UTC window, retains numeric usage and runtime setting metadata, and discards messages, prompts, reasoning and tool content. It never scans unrelated task content or `.env`. The default tail is 4 MB; truncated or otherwise unproven coverage is PARTIAL. Missing records or an unsupported version produce UNKNOWN. The source version, scope and definitions travel with the output.

```sh
.venv/bin/python -m movie_factory.experiment_ops import-usage --path /explicit/current-task-record.jsonl --task ACTUAL_TASK_ID --start 2026-09-11T22:00:00Z --end 2026-09-11T22:10:00Z --version 0.153.4 --output results/operating-setup/usage-import.json
.venv/bin/python -m movie_factory.experiment_ops report --experiment SETUP --usage results/operating-setup/usage-import.json --output results/operating-setup
```

Generic normalized usage records support incremental counts and cumulative counters. They retain source, UTC, task/turn ID, stream/epoch, model/effort provenance and category values. Import one source stream per capture, never both equivalent incremental and cumulative views. Reconciliation rejects mixed modes in one stream, deduplicates identities, flags contradictory duplicates, differences cumulative snapshots, and treats a reset as an unknown gap with a new uncounted baseline. A cumulative stream needs a snapshot at the experiment boundary or an explicit boundary baseline; the inherited initial total is never charged as new work. Scope is `(start, end]` for increments. Parent-thread entries and explicitly inherited response IDs are excluded. Missing linked tasks and missing fields are visible. Unknown category values stay null. Observed counts can be partial; exact totals require independently complete capture.

Account allowance percentages are separate capacity observations with window/reset IDs, concurrent-use and rounding caveats. They are not tokens and are never differenced into experiment charges. This first delivery stores no inferred quota cost. `--api-costs` may attach the existing campaign's compact provider ledger evidence; absent evidence means UNKNOWN, not $0. Subscription is shared fixed overhead. No per-token subscription bill, allocation or API-equivalent estimate is generated. Future optional estimates require explicit allocation assumptions or a dated official pricebook and sufficient model/cache/context metadata.

## Prospective process budget and model routing

Default checkpoints: 20 net minutes per diagnostic reassessment, at most three variants per hypothesis, and 60 net minutes overall. Estimate full work including setup, tests, render, packaging and disk growth before dispatch. These are process checkpoints, not qualification thresholds. A user hard budget takes precedence. Exceeding a forecast requires a smaller or explicitly justified plan; do not remove required controls or quietly lower a gate. During waits, use bounded blocking/event tools and update only on meaningful progress.

The next-run routing hypothesis retains Astra: Medium for specified implementation, routine orchestration and packaging; High for unfamiliar motion design, unresolved transform/rig/collision diagnosis or material disagreement between machine and visual evidence. Return to Medium after a demonstrated cause and concrete repair contract. Actual changes require a supported interface or a user setting change at a natural handoff. Do not claim this policy guarantees savings or quality parity; compare observational net time and usage including rework, without an expensive duplicate benchmark.
