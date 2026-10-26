#377 proposal — purpose-qualified references for micro work

Status: discussion/proposed implementation, not shipped or production-resume authority. Director377 explicitly pauses construction and directs reference decisions at micro-unit entry and retrospectives. Image search and routine built-in image generation are agent-owned; paid generative video requires specific Director spend approval. Runway is the service used historically. No new references/provider calls in this pass. Production pause: PRODUCTION_PAUSE.json. Remaining137 preserved, Astra proposal deferred/unapproved.

## What already exists, and the actual gap

Inspected current production_workflow.py95..118: references already require role, authority, scope, fidelity, allowed_variation, not_authority, aspects linked to requirements; faithful_motion needs timestamps. Planning/execution/review bind reference use. expert_planning.py derives requirements from reference IDs and retains original-intent veto. work_units.py requires positive reference features and multi-pose/view coverage for appearance. retrospective350 preserves causal triggers and invalidates downstream assumptions.

Missing: a mandatory per-aspect decision about needing/reusing/acquiring references, explicit evidence that the selected sources answer that aspect, acquisition routing/approval state and mandatory reference-sufficiency reconsideration on relevant failure. A general reference's presence is currently easy to mistake for a sufficient positive target. This is a process gap AND a failure of agent application; adding fields cannot prove truth.

376 case: a broad real rearing clip and anatomy reading did not establish a qualified multi-angle visual target for lower-neck/sternum/pectoral/foreleg shape. Source/weight/inverse/cache experiments then reproduced inadequately grounded targets more precisely. These findings warrant reference reassessment before further model escalation or constructing137. This is not proof that references alone solve the modeling problem, that the original motion video is bad, or that every failure needs new media.

## Intended flow, inside existing controller

Router FIRST -> creative intent/micro-unit scope -> reference-needs triage and acquisition/qualification -> existing grounding/derivation/strategy/challenge -> execution -> evidence-based review. Review/retro route back to reference establishment when evidence shows a reference gap. The initial triage is part of Grounding with lightweight domain/expert assessment; Derivation can discover a new gap and return there. No extra inference session, worker or database just to name a stage. Lightweight S3/display/bookkeeping routes stay light.

At micro-motion/micro-appearance entry, record one decision for each audience-critical aspect: `reuse_existing`, `acquire`, or `none_needed`, with reason. No mandatory new-image quota. Reuse adequate current sources rather than accumulate references. Unknown or unsupported critical aspects are unresolved; do not turn them into assumptions hidden in implementation.

For each needed reference, bind:

- The exact question/aspect and requirement it answers; source ID, provenance, file/hash, relevant crop/view/time interval, source status.
- Purpose: physical/anatomical form, motion mechanics, character/prop/environment design, staging/composition, or production-style/quality authority. One source can govern multiple explicitly separated aspects.
- Authority/fidelity: what must match, what may vary, what the reference does NOT govern. Preserve existing accepted native identities and faithful-motion commitments. A realism photo must not silently import photorealistic shading/palette or override the film's larger-than-life language.
- Coverage and actual observed features: views, poses, phases, contact/load visibility and sufficient clarity at the problem scale. Identify missing/ambiguous/conflicting coverage. File presence or a status string alone is not sufficiency.
- Acquisition/selection rationale and appropriate approval/rights state. A generated candidate does not become Director-approved identity or proven biomechanics by generation alone.

The planning exit requires applicable critical aspects to have sufficient qualified reference coverage, or a justified no-reference decision. Derive requirements/methods/early proofs from what is actually observed. Construction and review receive the same aspect contracts. Review compares the relevant crop/phase at appropriate framing; a builder's application paragraph is not visual proof.

## Acquisition paths and authority

1. Director-supplied media: assess purpose and coverage, use it where adequate; do not discard or weaken faithful/exact authority without a material Director decision.
2. Image search: agent selects suitable images/crops/diagrams and records provenance. Prefer real photos/real footage/credible anatomical sources for physical truth. Internal reference use is distinct from incorporating an image into released artwork; publication/asset rights remain separately checked.
3. Built-in generative images: agent-owned within current creative scope, useful for design alternatives, integrating cues, stylized targets and clarifying a proposed look. Qualify their role; they are not independent proof of anatomical/physical correctness.
4. Video: search/reuse suitable real or supplied footage where it answers motion. If a generated video is needed, prepare purpose, prompt/input, provider/rights/privacy/deployment route, expected length/variants and bounded cost/retries, then request Director spend approval and use the campaign ledger. Runway is a known historical path, not an automatic current-provider qualification or reusable spending grant. Generated motion can hallucinate mechanics; validate before adopting it as a physical benchmark.

Selecting clarifying references within approved intent is not a routine Director gate. A reference that materially changes identity, culture, style, action or another accepted choice still requires the appropriate creative decision. No installation, external specialist, cloud or new publication authority is inferred.

## Review and retrospectives

Mandatory questions: Are we matching the right target? Are references adequate for the failing aspect and actual view/phase? Are we using the intended authority rather than importing unrelated style? Is the problem reference/input, requirement, method, execution, evidence or judgment?

Choose `retain`, `supplement`, `replace`, or `no_reference_issue`, with actual supporting evidence and uncertainty. Supplement/replace returns to acquisition/qualification and invalidates affected downstream artifacts; preserve old refs/failures and cumulative cycle/call/spend limits. Do not rename a task to reset allowance. Do not generate more images automatically after every failure. An evident reference gap should trigger this immediately, not wait for the third-failure retrospective threshold.

Before an artistic model escalation, establish whether missing/inadequate reference input is the real problem. Technical tasks can justify no-reference-needed; this is not a blanket search requirement or prohibition on necessary escalation. This supplements360, not a new automatic Astra grant.

## Proposed implementation, not executed

Extend existing reference/aspect manifests, micro-unit contract, Grounding readiness/challenge, review mappings and retrospective responses. Reuse current knowledge/resource manifests and retrieval bindings; no separate reference knowledge service. Mandatory constraints bypass semantic ranking. Return bounded selected media/crops and role metadata to tasks instead of dumping every reference/history into context. Legacy immutable briefs remain historical; new live continuation requires explicit source/schema reconciliation without budget reset or global307 repinning.

Validators can require decisions, source bindings, coverage mappings, current qualified state and paid-video authority. They cannot determine anatomical truth, motion realism or whether an assertion was honestly grounded. Preserve the existing well-formed-wrong-method negative control. Actual adequacy needs image/phase inspection and a fresh failure-seeking challenge, with Director313 fullspeed AV boundary intact. Sol default; no new LLM call/session per checklist.

## Calibration before resuming production

Use known-history cases, labeled as such rather than blind evaluation:

- Horse chest: a broad rearing video alone does not settle the hidden/unclear chest junction; require appropriate angle/pose anatomy coverage before more construction. Anatomical photos do not set the movie's shader/palette.
- Rear preparation: a still photo cannot qualify loading/timing/contact mechanics; the existing supplied reference video should be reused without needless new generation.
- Design concept: a directional concept remains creative material rather than a literal pixel blueprint; exact accepted native identity and explicitly faithful requirements stay protected.
- Existing adequate references: reuse passes, no acquisition busywork. Expiring-S3-link task bypasses production reference work via router.
- Paid generated video: no scoped approval/ledger means no provider dispatch even if many construction cycles are approved. Built-in images/search do not add a routine approval gate.
- Retro: insufficient-reference failure returns to Grounding/acquisition; adequate-reference implementation failure retains refs and repairs the actual method/execution. Old failures and limits survive both.
- Missing/stale media, irrelevant crop/phase and incompatible authority are negative controls. A plausible but semantically wrong adequacy assertion remains an explicit limitation, not a claimed automatic catch.

Then prospectively apply to the paused chest unit: assemble role-qualified physical form references plus the original faithful motion clip and separate accepted film-style comparator; freeze a small visible positive target before constructing137. Do not resume until Director explicitly does so. Model escalation remains a separate deferred choice, considered after reference adequacy is known.

Track reference gaps caught before construction versus escaping review, cycles to first credible positive target, repeated failures by cause, unnecessary acquisition and Director interventions. No percentage savings or quality improvement claimed before observations.
