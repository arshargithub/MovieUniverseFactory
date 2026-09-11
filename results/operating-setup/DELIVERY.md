# Operating handoff delivery

Scope: local bookkeeping and prospective experiment specification. The handoff source is preserved in [EXPERIMENT_OPERATING_HANDOFF.md](../../docs/planning/EXPERIMENT_OPERATING_HANDOFF.md). No 3D-05 animation or qualification is changed, no 3D-06A animation is implemented, no actual model setting is changed, and no paid engineering API call is made.

Delivered:

- Transactional append-only lifecycle ledger with idempotent IDs, superseding corrections and exported history; UTC/monotonic job boundaries and reconciled input waits, job overlap, phases, coverage and reopening.
- Optional 0.153.4 task-local metadata importer and conservative usage reconciler; cumulative counts, resets, duplicate records, shared-task/episode boundaries and inherited counters are covered. Unsupported or absent sources return UNKNOWN. Metadata includes observed Astra Medium, not a fabricated setting change. Dollar attribution remains unknown.
- Generated [simulated JSON](../operating-demo/summary.json) and [Markdown](../operating-demo/REPORT.md): 120 calendar minutes, 35 excluded, 85 net; jobs sum to 15 minutes with a 10-minute union. All data are labelled simulated.
- Prospective [operating instructions](../../docs/engineering-intelligence/OPERATING_LEDGER.md), motion-brief integration, learning-delta and experiment-card templates, [3D-05 card](../3d05/EXPERIMENT_CARD.md), central learning events and [3D-06A draft](../../feasibility/3d/3d-06a/SPEC.md).

Validation: the offline suite passed **158 tests**, with **11 native/opt-in tests deselected**. The 26 new operating tests also passed after the final missing-source/date-order guard changes. No Blender suite was rerun. Tests exercise the requested wait/job fixture, background activity, overlapping waits, missing events, transactional recovery, clock jumps, reopening, cumulative/reset/duplicate/subset usage, cross-episode scope and unsupported sources.

Setup effort is recorded separately under `OPERATING-SETUP`, not charged retrospectively to 3D-05 or started as 3D-06A. This bootstrap began before its own recorder existed: the start comes from runtime turn metadata, the first local timestamp is 23.284 seconds later, and two intermediate phase boundaries are explicitly approximate. Exact net time must therefore stay UNKNOWN; the report provides coverage instead of silently filling that gap. The scope-limited token import is PARTIAL. Final response generation and later backup/push are outside the closed report's snapshot and must not be described as captured.

The initial plan budgeted 30–45 minutes, with 20-minute reassessment and 60-minute overall checkpoints. This delivery used one final offline suite plus small targeted test batches; no native work. The local ledger remains in `.runtime/operating-setup.sqlite3`; its portable event export and closing summaries are included here. The current frozen 3D-05 supplement remains untouched. Repository history and these compact records should join the next authorized backup; the large native/image archive still requires its separate upload authorization.

Next authorized animation task: start a new 3D-06A episode, complete manual reference landmarks and the fixture screen, then freeze numerical criteria and dependencies before scoring. A failed small-gesture fixture screen should lead to separate fixture admission, not another round of 3D-05 repairs. The spec's reference is explicitly a manually authored pose/time board; it does not establish automatic video-to-motion transfer.
