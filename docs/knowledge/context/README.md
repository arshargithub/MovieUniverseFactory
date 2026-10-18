# Context handling and task routing

The mandatory core is `AGENTS.md`. `rules.json` preserves all42 original
instruction paragraphs verbatim with their applicability and core mapping.
Use this system to avoid repeated historical dumps, not to lower the information
needed for a sound decision. Source/authority disagreements require inspection.

## Start or resume

```sh
.venv/bin/python -m movie_factory.context_hygiene current
.venv/bin/python -m movie_factory.context_hygiene route --topics horse wardrobe sound pashtun
```

`current` reads release status fresh and validates the existing307 source,
knowledge, candidate and protected-artifact bindings. It returns current
constraints/defects and source hashes, not the entire historical status record.
It does not grant authority or replace the full review capsule or work strategy.
It is currently specific to the active Sikh307 review contract; reconcile its
state and next-step description deliberately when that work changes. Historical
`CURRENT_PRODUCTION_STATE.md` contains earlier256-260 authority; the current
306/307 pause takes precedence. Do not interpret older approval as permission
to resume a paused task.

`route` selects exact original rules for all named topics and their prerequisite
topics, deduplicating by rule ID. Read them and the applicable required deep
sources. A budget overflow blocks instead of dropping rules. Unknown topics
block. It does not infer topics from natural language, identify every adjacent
interface, or replace the existing knowledge graph/task packet. A recognized
topic such as `character` is not admission for an unreconciled Gurkha entity.
Mixed work requires multiple topics plus manual interface/source reconciliation.

Universal core rules always apply. The `workflow` route retains exact historical
wording for ambiguity; routine work need not reread all of it. Already-read,
unchanged source content need not be printed again within the task. Verify its
binding before reuse, and record what was actually inspected. Read original
decisions when meaning or approval scope is uncertain.

## Bounded evidence and verbose commands

```sh
.venv/bin/python -m movie_factory.context_hygiene read results/context311/STRATEGY.md --lines 30 --chars 4000
.venv/bin/python -m movie_factory.context_hygiene run --label unique-test-run -- .venv/bin/pytest tests/test_context_hygiene.py -q
.venv/bin/python -m movie_factory.context_hygiene usage
```

`read` gives a bounded UTF8 excerpt, original path/hash/size, line numbers and an
explicit omission flag. It scans the complete text for lexical warning/error
signals, includes up to12 samples and reports omitted samples. This scanning
adds local I/O; it is not semantic warning detection. No matching signal does
not imply no problem. Inspect omitted regions when a failure or ambiguity needs
them. Binary input blocks rather than silently substituting text.

`run` executes an explicit trusted command without a shell. Complete stdout and
stderr plus an exit/timing/hash receipt stay in a unique directory under
`.runtime/context-hygiene/runs/`. It returns bounded summaries and propagates
the exit code; a zero exit is not review/production acceptance. Existing run
labels cannot be overwritten. Wrap it with `experiment_ops job` when lifecycle
capture is required. If interrupted, inspect captured logs and the operating
ledger; do not infer successful completion from incomplete output. If a command
produces non-UTF8 output, summary may block while raw bytes/exit receipt remain.

This helper is not a sandbox, secret scrubber, provider adapter or extra
execution authority. Use only already-authorized, non-sensitive commands/logs.
Never run credential-printing commands or pass secrets in arguments. Path checks
reject obvious private paths, traversal and escaping symlinks; they cannot prove
arbitrary approved logs contain no sensitive content. It does not bypass trusted
Blender-handler requirements or provider budget/egress rules.

## Measurements and limits

The local append-only use log stores timestamp, operation, path/identity,
content hash where available, emitted UTF8 bytes, source bytes and omission
status. No output body or command arguments are copied into telemetry. Repeated
reads are counts, not necessarily waste: inspecting a new section may be useful.
Only helper calls are covered. Tokens and compactions remain null here; use the
existing version-qualified usage importer when applicable metadata is available.
No account quota-to-token or byte-to-token conversion is made.
Schema2 counts the actual formatted JSON response plus newline. Earlier local
initialization events are retained but excluded from this byte sum and counted
separately; no historical telemetry is rewritten.

Shorter instructions do not erase this conversation, change app/system/tool
instructions or guarantee faster rendering. A fresh task context at a natural
work boundary can use the new entry point; no new task or setting is created by
this implementation. Documentation follows the repository's existing location
and format; there is no new cloud Page/source of truth.

## Maintenance and rollback

Source changes must be reviewed, mapped and tested before updating hashes. Never
run an automatic re-pin to unblock work. `scripts/context311_prepare.py` is a
one-time initializer and refuses to overwrite records. To revise the core later,
preserve the prior version, review its diff, amend the core hash and coverage
mapping together and rerun frozen routing and review regression tests. Do not
add another long chronological paragraph to the core for every new incident.

The exact pre-cleanup file is `results/context311/AGENTS.before.md`; the activated
candidate is also recorded as `AGENTS.proposed.md`. If a critical obligation is
lost, restore the prior instructions through a reviewed scoped edit (or revert
only the cleanup commit after checking subsequent changes), retaining new
evidence and unrelated work. A successful hash/route test proves preservation
and selected coverage, not semantic equivalence or independent judgment.
