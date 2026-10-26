# Purpose-qualified references — Director377–378

Adopted at378. This extends the existing controller; it does not add another
agent, LLM session, database or approval checkpoint. The Director377 production
pause remains active. Implementation evidence: [378 closeout](../../results/workflow378/CLOSEOUT.md).

## Entry and stage contract

Router first. At entry to a micro-motion, micro-appearance or other substantial
production plan, the working agent identifies the audience-critical questions
and decides whether existing references answer them. This is part of Grounding,
before choosing a construction method. Lightweight display/research/link tasks
still use their existing lightweight route.

`direction.reference_scope` declares version1, an ID, kind (`micro_motion`,
`micro_appearance`, `production`) and needs. Each need has an ID, purpose,
question, critical boolean and required coverage labels. Purposes are
`physical_form`, `motion_mechanics`, `design`, `staging`, `film_style`,
`technical_validation`. Coverage describes the actual question: relevant views,
poses, load/contact or motion phases, not a quota of new images.

`GROUNDING.reference_readiness` contains that exact scope and a decision for
every need: `reuse_existing`, `acquire`, or `none_needed`, with reason and
reopening trigger. A needed input must be acquired and qualified before that
stage can complete. Unknown or partial critical coverage stays unresolved.
Critical physical-form/motion needs cannot be waived with `none_needed`.
Deterministic technical tasks may justify no external reference.

Every selected reference binds its existing reference ID, origin, inspected
source media, observation, coverage-to-observed-feature mapping, provenance,
rights-use, what it governs and what it excludes. Existing reference roles,
fidelity and motion time intervals remain binding. Qualification evidence must
include the original bound source media; a written assertion alone is refused.
Brief source bindings must cover qualification evidence too.

Physical photographs/footage govern anatomy/mechanics only unless separately
adopted for another purpose. They do not silently impose photorealistic surface,
identity, palette, costume or camera. Directional concepts remain creative raw
material; accepted native identity and explicitly faithful motion retain their
stronger authority. Generated physical/motion references need non-generated
corroboration for the relevant aspect; generated imagery cannot prove itself.

Derivation copies readiness and maps every requirement to its applicable needs;
critical needs and their selected source IDs cannot disappear. Strategy copies
both contracts unchanged. The planning challenge records an observation,
counterexample and evidence for every need. Execution records actual aspect
application; review independently compares each aspect against bound evidence.
Omissions, stale bindings and FAIL/NOT_RUN do not pass.

The same contracts and compact instructions appear in the existing stage
packets. No blanket full-reference dump or new model call is required. Needs
and scope remain trusted-parent classifications: software cannot infer whether
the agent omitted an important anatomical question.

## Acquisition and approval paths

1. Reuse Director-supplied or accepted material when adequate. Do not replace a
   faithful authority simply because another reference is easier to match.
2. Image/video search: agent-owned selection, provenance and coverage assessment.
   Prefer actual footage/photos or credible anatomy for physical truth. Internal
   reference use is distinct from incorporating pixels into released artwork.
3. Built-in image generation: agent-owned within approved creative scope. Use the
   imagegen skill/tool, preserve prompt/input/provenance and qualify the result's
   limited role. No routine Director approval or two-image cap. Identity/style
   changes remain material creative decisions.
4. Paid video generation: prepare the exact purpose, provider/model/input/prompt,
   commercial/output and dependency/export rights, privacy, deployment route,
   call ceiling and total cost. Obtain explicit Director approval, then reserve
   against the persistent campaign ledger before dispatch. Runway is the
   historical service, not a standing current-rights qualification or spend grant.

`reference_acquisition.route(method)` supplies the ownership boundary.
`dispatch_video(root, plan, approval_binding, ledger, trusted_provider_adapter)`
guards a host-side paid call. The exact approval binds plan digest, human source,
campaign path, total cap and maximum calls. The ledger's immutable campaign/call
limits may be tighter, never larger. Reserve before provider; failed or unknown
charges remain reserved across restarts. Another run ID does not renew allowance.
Result status is `candidate_not_qualified_reference`, not automatic adoption.

This pass tests that adapter using mocks only. It does not install or qualify a
new live Runway client. Provider qualification and human provenance are trusted
source-backed records, not cryptographic authentication or legal judgment.
Raw chat tools are not OS-intercepted: these instructions prohibit bypassing
approval/ledger guards. No new tool, installation, cloud or publication authority.

## Retrospectives and escalation

A declared `reference_gap: true` outcome creates an immediate scoped obligation,
including in a negative control; it does not wait for three failed attempts.
Responses for current-contract work must include `reference_assessment`: exact
readiness digest, diagnosis, disposition, affected aspect IDs, reason and bound
evidence. Dispositions are retain/supplement/replace/no_reference_issue. A gap
requires supplement/replace and return to Grounding. A known gap cannot be
reclassified as a method patch merely to continue. Adequate-reference method or
execution failure can retain references and repair the actual method. Admission
rechecks assessment bindings; effectiveness still requires subsequent evidence.

Do not automatically acquire more images after every failure. Ask whether the
missing information would change the target, versus whether a clear target is
being missed. Before micro-unit Astra escalation, validate reference readiness
and bind the evidence for `execution_gap` or
`unresolved_after_adequate_references`. This supplements360's exact human
approval, retrospective, scope and call allowance; it grants no automatic Astra
use. Purely technical non-micro escalation retains the existing360 procedure.

Regrounding invalidates downstream artifacts and retains the original task,
history and correction/call/spend limits. On the currently paused task,137 is
still unused. Do not call replan and then revise as two separate corrections;
an eventual authorized fresh revision must make one atomic136→137 transition.

## Compatibility, testing and limits

New `local_native` Grounding/brief admission requires this contract. Historical
offline/frozen no-contract fixtures remain readable, explicitly non-native; if
the new contract is supplied it is enforced in all modes. Engine/source changes
invalidate old native planning admissions.378 does not migrate, repin or resume
the paused task or the blocked global307 review state.

Relevant mandatory330/328/350/360 guides link here. Controller admission and
packet instructions enforce the requirement independently of semantic retrieval.
The legacy pilot catalog has not been silently expanded or repinned; manually
reconcile this source alongside its packet. There is no universal-memory claim.

Run the synthetic control suite with:

```
.venv/bin/python -m pytest -q tests/test_reference_readiness378.py
```

The suite exercises real staged-controller paths with synthetic media and mocked
provider/native boundaries. It preserves a deliberately admitted false semantic
claim: valid bytes/hashes/coverage declarations cannot prove real anatomy,
truthful viewing, an adequate angle, artistic quality or causality. Director313
full-speed AV remains separate. No percentage efficiency or fewer Director
inputs is claimed. Measure gaps caught before construction, reference-role
violations, repeated failures by cause, unnecessary acquisition, and later
credible output/Director corrections against declared work scope.
