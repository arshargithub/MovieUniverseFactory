# Stage specific model routing

Adopted at exchange326 for the separate runtime. This does not switch the main
chat model or qualify model superiority. Explicit model and effort overrides
are supported by the [official Codex App Server protocol](https://learn.chatgpt.com/docs/app-server).
The implemented route is locally mock-tested; it has not yet been live-tested
with this High-effort mix. Historical325 used Sol Low.

| Work package | Planning | Execution | Review |
| --- | --- | --- | --- |
| General or proven routine work | Sol 6.1 High | Sol 6.1 High | Sol 6.1 High |
| Difficult 3D modeling, rigging, animation, simulation and physical interactions | Sol 6.1 High | Astra High | Sol 6.1 High |
| Foundational or unresolved specialist strategy | Astra High, with evidence-backed escalation | Astra High | Sol High; escalate diagnostic review when justified |

The trusted parent classifies domain and risk before dispatch, not the stage
model and not a filename heuristic. Routine proven render management and
deterministic checks do not need Astra or an LLM. Complex non-3D work may justify
the same explicit escalation; the general profile is a default, not a ban.

## Dispatch and recovery

Use `stage_routing.policy('general')` or `policy('specialist_3d')` and pass it as
`routing=` to `SerialRunner`. Each stage receives an explicit route carrying
actor, model, High effort, policy digest, reason and any escalation evidence.
The runner persists the task policy and request before dispatch, refuses silent
policy changes on restart, and rejects returned runtime metadata that does not
match. Offline legacy fixtures may omit routing; real `CodexProtocol.infer`
cannot. The old live qualification CLI now requires `--routing-policy`.

Before inference, the adapter queries `model/list`, verifies the exact model and
High effort are offered, sets model and reasoning effort on the fresh thread,
checks returned settings, then explicitly repeats model/effort on `turn/start`.
No alternative model, API-key route or lower effort is tried automatically.
Requested values and thread-observed settings are recorded separately; these
are protocol observations, not proof of an inaccessible server's internals.

An operator may call `runner.escalate(task, record)` for the current stage after
a documented reassessment. The record contains `trigger`, `reason` and
`evidence` mapping repository paths to SHA256 hashes. Valid triggers are
foundational strategy, unsupported structural assumption, unresolved diagnosis,
contradictory evidence and repeated missed defects. Missing/stale evidence,
an unresolved call, or an already-Astra route blocks escalation. Previous and
new policies are retained in `route_events`. Restart with the persisted updated
policy; an old process cannot silently restore the old one.

Escalation changes neither controller state nor correction count nor call cap.
It does not re-review a failed result until someone passes it. If Astra fails,
reassess method/input/representation; there is no higher tier. Step-down after a
proven route belongs in the next scoped package, not an invisible mid-call
fallback. No extra calls, spending, tools or payload egress follow from routing.

## Review and authority

Fresh review receives the Director brief, reference roles, evidence and known
defects, not builder advocacy. Different contexts/models reduce one bias source
but do not establish independent perceptual accuracy. Full-speed audiovisual
judgment remains Director-owned; static comparisons cannot earn a motion PASS.
Existing negative controls, protected acceptance and evidence gates remain.

The runtime is still frozen-evidence/tool-free. Wiring these settings does not
add production Blender authoring. Trusted structured operations must be bound
in the next production integration package.325's four-call allowance is exhausted.

Measure first-pass acceptance, escaped/repeated defects, adjacent regressions,
actual Director decisions, active work/job/wait intervals and observed usage.
Unknown usage remains unknown; neither percentage savings nor a model quality
advantage is established by this implementation. The policy is a hypothesis to
evaluate on real work, not a reason to duplicate expensive production runs.

## Next production package

Outcome: a reviewable isolated Nihang leader/rearing/crowd passage with one-second
handles, preserving the accepted Pashtun master. Bind321 audit, faithful-motion
reference and same-film appearance floor. Use Astra for the unresolved motion
and construction strategy as well as execution; fresh Sol High review checks
the evidence. Include coordinated horse/rider performance, leader/crowd shot-tier
appearance and crowd attention; exclude principal Sikh head replacement, the
full sequence render and unrelated terrain polish. No delivery with known
visible failures. Bind the trusted authoring operations and package-specific
call allowance before dispatch; a policy file is not that authorization.
