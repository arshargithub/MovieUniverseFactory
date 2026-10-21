# Always route first

Director332 adopts mandatory entry. **Bypass means bypass production planning,
not bypass the router.** No new model call, installation or cloud service.

1. Bootstrap only what is needed to understand the request: instructions, current
   state, source pointers and authority. Record original text, operation list,
   scope rationale and an exact authority binding in a small request JSON.
2. Run `python -m movie_factory.task_router --request PATH --id REQUEST_ID`
   through the project `.venv`. It writes an immutable decision in the canonical
   `.runtime/factory-entry.sqlite3`. Read that decision before task actions.
3. Production effects select grounding → derivation → strategy → challenge →
   execution → review. Display, status, explanation, research, planning,
   engineering and operations select explicit lightweight routes. A mixed request
   with production effects cannot select research simply because it also needs
   research. A route is not permission to spend, upload, publish or install.
4. Create the task with its admission ID. For `local_native`, missing admission
   or a noncanonical database fails. For a continuation use `--continue-task ID`
   and `continuation: true`; resume that task, never recreate its correction budget.
   A scope expansion requires explicit reconciliation, not silently adding effects.
5. Native work uses the registered bridge, which admits a step only after its
   plan is admitted and prerequisite outputs have actual recorded internal review.
   Source/plan/output drift fails closed. Results enter final controller review;
   a successful worker, source hash or step review cannot directly deliver media.

Example request structure (replace the binding with actual source/hash):

```json
{"text":"Show the approved clip", "operations":["display"],
 "rationale":"Existing-file display; no edit or rendering",
 "authority":{"path":"results/example/request.md", "sha256":"..."}}
```

Operations: `display`, `status`, `explain`, `research`, `plan`, `code`, `test`,
`document`, `backup`, `upload`, `publish`, `asset`, `motion`, `render`, `sound`,
`edit`, `native_inspect`. Unknown operations block for classification. The agent
must reconcile every requested effect; this finite vocabulary is not automatic
natural-language understanding. The regression suite deliberately demonstrates
that dishonestly labeling “render” as “display” is not detected from prose alone.
It still cannot launch Blender through the lightweight controller.

## Native boundary and honest limits

The shared Blender runner refuses execution without a bridge-issued single-use,
exact-job capability. Legacy callers of that runner now fail closed; they are
not automatically migrated or reauthorized. The bridge currently exposes only
read-only native inspection. Register and qualify a trusted authoring handler
before the next artistic proof. No arbitrary command, Python string or script
path is accepted. No live model allowance was added;325 remains exhausted.

Job reservation happens before process launch. A worker failure cannot qualify a
dependency. An interrupted process leaves an unresolved reservation/lease; verify
termination and reconcile it explicitly, never automatically replay. Same step,
cycle and plan cannot run twice under another job name. Replanning uses the
existing controller allowance and invalidates dependent step qualifications.
The persisted native step review records observations and comparisons against
actual output bindings; truth of those judgments remains a human/agent duty.

This is **supported-entry-point enforcement**, not a sandbox over all Codex tools.
Historical scripts containing direct subprocess launches still exist for evidence
and reuse. They are quarantined by the core instructions, not magically intercepted
by Python. Do not use them as a fallback. A future runtime with restricted tool
access can close that residual boundary. Current entry-point inventory and tests
must disclose it rather than claim universal interception.

Offline/frozen historical fixture creation now records a labeled compatibility
route first. It is not proof that those historical tasks were prospectively
routed. New real work requires an explicit request.332 bootstrap registration is
also labeled retrospective to installation; timestamps are not backdated.

No scene acceptance changes.331 remains closed/rejected;253 remains provisionally
accepted. New native attempts need their own authorized scope and remaining
allowance, never a renamed331. Semantic wrong-method controls remain required.
