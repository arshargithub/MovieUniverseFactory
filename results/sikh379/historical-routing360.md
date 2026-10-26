# Stage model routing — Director360

Director359/360 adopts **Sol6.1 High for all stages and task classes**, including
difficult3D planning, execution, review and retrospective reasoning. This
supersedes326's automatic Astra specialist builder and earlier broad Astra
continuation instructions. The quality bar and original task/correction limits
stay in force. Source: [approved request](../../results/workflow360/REQUEST.md).

| Work | Default | Exception |
| --- | --- | --- |
| Planning, execution and review | Sol6.1 High | Specific Director-approved Astra High assignment |
| Retrospective reasoning and other workflows | Sol6.1 High | Same evidence/approval requirement |
| Deterministic rendering, checks and bookkeeping | Existing trusted code | No extra LLM call required |

## Before requesting Astra

The agent owns detection and reassessment. Read the relevant retrospective,
identify unresolved causes and failed methods, and run a discriminating control
where useful. Explain why a particular Astra contribution is likely to help.
Slow renders, environment errors, missing review or exhausted corrections alone
do not justify escalation. Foundational uncertainty can justify an early request
before repeated costly attempts. Astra remains the top tier.

The Director approves a concrete assignment: question, necessary evidence,
expected output, success test, exact scope and allowance. Approval to adopt this
policy is not approval of an individual Astra call. Broader work or an extension
requires new explicit approval. Full-speed AV remains Director-owned under313.

## Enforced separate-runtime contract

`stage_routing.policy('general')` and `policy('specialist_3d')` both select Sol
High in version2. The current [default JSON](SOL_DEFAULT_ROUTING.json) is suitable
for the existing qualification CLI; it does not renew exhausted call authority.
Legacy version1 policies fail with `LEGACY_ROUTING_REQUIRES_RECONCILIATION`.
Historical326 fixtures and recorded calls retain their original settings.

An escalation record has `id`, `trigger`, `reason`, `evidence`, `retrospective`,
`assignment` and `director_approval`. The assignment binds:

- task and digest of the current stage/cycle/requirements/authority/retrospective;
- original runner database and `max_calls` (one to four within existing limits);
- `expected_output` and `success_test`.

The Director approval is a bound JSON record with decision
`approve_astra_escalation`, an exact copy of that record except its approval
binding, the actual `director_reply`, and a bound original human source.
Retrospective and other evidence are hash-checked before active dispatch.
These are trusted-parent records, not cryptographic human authentication or
automated proof that a source actually warrants escalation. The agent must
verify the human authorization and reasoning; models cannot grant themselves
authority by supplying a JSON file.

`runner.escalate(task, record)` validates scope/approval and retains original
policy history, controller state, correction counts and call cap. Reserved,
failed and aborted calls count toward the assignment. Restart reads the retained
requests; the assignment cannot be reused or reset under another database path.
An unresolved call still blocks until explicit recovery/reconciliation.

When the stage/cycle/input scope changes or the approved call allowance is used,
the next dispatch selects Sol automatically. Expired approvals remain in history;
unrelated work does not inherit them. A new grant needs current evidence and
approval. `runner.adopt_sol_default(task, authority)` explicitly reconciles an
existing persisted policy with an `adopt_sol_default` decision bound to that
task and Director source, preserving old policy/calls and cap. It never silently
reinterprets a version1 policy.

CodexProtocol validates an Astra route and approval before runtime startup,
then preserves exact model/High overrides and returned-metadata checks. There is
no automatic alternative model or effort fallback. Per-model settings follow the
[official app-server protocol](https://learn.chatgpt.com/docs/app-server).

## Main chat and verification boundary

The Director controls this chat's model selector. The reported switch to Sol
High is recorded with its provenance. Main-chat work follows this policy through
the agent's instructions; runtime code cannot intercept arbitrary chat tools or
automatically switch the UI back from Astra. For a manual chat escalation, state
when its assignment is complete and request the return to Sol before unrelated
work. The separate runtime can select Sol on its next call automatically.

Keep grounded planning, fresh failure-seeking review and retrospectives without
automatically creating separate inference sessions for each stage. The existing
runtime remains frozen-evidence/tool-free; this change adds no authoring ability
or live call allowance.325 remains exhausted. Offline tests establish routing
and accounting behavior, not artistic performance or a measured saving. Compare
accepted outcomes, escaped/repeated defects, Director interventions, active
effort and observed usage; unknown usage stays unknown.
