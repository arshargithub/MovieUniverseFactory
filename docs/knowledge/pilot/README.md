# Local production knowledge bridge

Use this pilot before covered production work and before its internal handoff. It supplies source-backed requirements and checks; it does not replace visual judgment, the governing AGENTS.md instructions or Director authority. See [the implementation report](../../planning/KNOWLEDGE_PILOT_213.md).

## What is authoritative

**217 amendment:** [reviewed reconciliation](reconciliation217.md) adopts Director215's narration A, keeps the performed voice/paid route open, and maps Director217's glove/whole-fist correction. Current coverage is nine documents/89 sections/28 records; the original213 figures and generated files below are historical. Fresh task packets, not those historical files, govern current work. Manual anatomical review remains essential: earlier thumb contact math did not prevent a visible backward-bending pose.

Existing source documents and actual Director approvals remain authority. `catalog.json` is a curated, versioned interpretation:28 records, typed entity relationships, applicability facets and explicit status. `source-pins.json` binds nine reviewed documents and their88 sections. `expectations.json` was authored from the source reading before retrieval code ran; it is a finite, agent-authored oracle, not independent human ground truth. Search results are supporting material, never approval.

The derived SQLite index is local at `.runtime/knowledge-pilot213/search.sqlite3`. Packets rebuild a fresh in-memory index from pinned sources, so a stale on-disk index cannot silently govern execution. No server, embedding model, API key, cloud call or new dependency is used. Fine-grained source invalidation, automatic scene extraction, independent-model review and integration into every production launcher are not implemented. The current conservative source hash check blocks on any change in the nine-document corpus.

## Start a task

1. Read the active work strategy and governing instructions. Create or update a task JSON following `tasks/rein.json`: precise operation and affected entities, desired audience result, phase, actual input hashes, open decisions and execution prerequisites. Use `planning` until the required execution inputs and authority are bound. A provenance record alone is not a native/cache validation.
2. Generate and read the packet. Mandatory global and applicable rules bypass search. Graph expansion brings adjacent interfaces into the review; examine that impact set manually for missing edges. Unknown entities or operations block rather than quietly select nothing. Broadly described work must be decomposed or its full impact set mapped; this pilot does not infer scope from prose.
3. Reconcile supporting search/history and mandatory deep documents for that specific task. Apply actions in the work package. Do not paste the whole corpus into context or treat missing retrieval as proof that no obligation exists.
4. Before a substantial dispatch, use a freshly generated execution packet with explicit authority and actual bound inputs. Exit code2 means blocked. A passing planning packet does not authorize production, spending or a creative option.

```sh
.venv/bin/python -m movie_factory.production_knowledge packet --task docs/knowledge/pilot/tasks/rein.json --output .runtime/knowledge-pilot213/rein-current.json
```

This writes JSON plus a readable Markdown companion. Change the task/input bindings when camera, motion, framing, assets or intent change; do not reuse an earlier review blindly. Packets include catalog/source, entity and engine fingerprints. If mandatory context exceeds the explicit character budget, the packet blocks rather than truncates obligations. Character counts are not token measurements.

## Before handoff

Create a review JSON containing the packet digest and one check per obligation: ID, matching evidence kind, PASS/FAIL/NOT_RUN, action taken, actual observation and evidence paths with SHA256. Include tested hypotheses, adjacent-regression findings and the stopping rationale. Use `generated/pilot-review.json` as the software-pilot example, not as visual evidence for the character. Tests use explicitly synthetic fixtures; never copy their PASS into a production review.

```sh
.venv/bin/python -m movie_factory.production_knowledge check --packet docs/knowledge/pilot/generated/pilot-packet.json --review docs/knowledge/pilot/generated/pilot-review.json --output .runtime/knowledge-pilot213/pilot-gate.json
```

The check blocks missing/failed checks, absent actions/observations, wrong evidence kinds, stale or missing artifacts, modified packets, unresolved hypotheses and missing regression/stopping review. It verifies structure, current hashes and declared state—not whether the agent's observation is true, whether an image is attractive or whether the Director accepts it. The current agent must honor the gate; unrelated commands are not intercepted. A future orchestrator should call the same interface before dispatch/handoff.

## Rebuild and evaluate

```sh
.venv/bin/python -m movie_factory.production_knowledge build --output .runtime/knowledge-pilot213/search.sqlite3
.venv/bin/python scripts/verify_knowledge213.py
```

Verification runs offline unit/regression tests, regenerates source coverage and all four packets, checks fresh-process identity and deliberately attempts unsupported audio execution and a rein handoff with no evidence. It does not run Blender or a provider. All outputs are scoped to the pilot folders.

When a source changes, inspect the diff and actual approvals, update affected records/edges and the independently justified applicability expectations, then explicitly amend pins and task bindings. Preserve earlier failed evidence. `freeze` refuses to overwrite an existing pin. Do not mechanically rehash unreviewed changes to clear a blocker. Rerun the affected cases and broad offline regressions; mark previously held-out cases as regression cases after using their failures to adjust routing.

## Coverage and current limits

The coverage report inventories all88 sections of nine fully read documents and maps them to relevant records at source-document granularity. This is broader source coverage than indexing14 summary labels, but it is not a sentence-level independent audit. Detailed linked histories, all original architecture decisions, other conversations and attachments are not exhaustively reconciled. The historical capture still has one truncated response. No whole-project lossless-memory claim.

All109 required case/obligation pairs now retrieve correctly in the finite nine-case set, after the first run exposed two missing contact dependencies. Those failures are retained. Three extra obligations are conservative adjacent checks; optional useful-lesson selection is incomplete. There is no measured audience-judgment accuracy or generalization guarantee. Keep manual source audit in shadow with the pilot during the first real correction and sound package; expand records/tests when a new domain is encountered. Semantic search is deferred until actual misses justify it.

The three next-work packets preserve: an open rein-grasp correction; unselected narration/voice and external-call authority; and Metal's conditional timing benefit with strict replay failure and unrun final-sequence qualification. None is marked production-complete. The next production objective remains the first complete Pashtun audiovisual unit, then the trailer and two episodes.
