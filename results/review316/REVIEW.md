# Exchange316 — feedback verification and production-method assessment

2026-10-19. **Discussion/recording only; construction explicitly deferred.**
Director calls candidate315 much improved, not accepted, and requests thoughts
on two attachments before addressing the remaining defects. No scene, provider,
installation, upload, spend, music or release change is authorized by this review.
Gemini remains parked under313. Director remains audiovisual judge.

## Evidence boundary and feedback register

Target: exact candidate11 in `results/sikh315/DIRECTOR_AV_QUEUE.json`, Sikh29s
and unchanged-Pashtun49s join. Preserve that historical queue and source evidence.
This review inspected movie11 chronology sheets13,14,18 and full frames75,318,
plus the implementation sources below. It did NOT independently watch continuous
motion or hear audio; Director playback observations are primary evidence for
jerk, naturalness and perceived pacing. Technical mechanism findings are not
claims of perceptual qualification. Existing strict replay FAIL remains separate.

| ID / relationship | Director observation and verification | Proposed correction and failure test |
|---|---|---|
| D316-01 / adjacent regression of D315-02 | Keep bumpy terrain, reduce jerky bike response. `scripts/sikh299_scene.py` wheel-contact solver repeatedly samples actual rotating tire minima against road, then keys chassis pitch/height each frame; no suspension filtering between contact and whole-bike response. This supports a coupling problem; the exact contribution of tread sampling versus terrain frequency is not yet isolated. | Separate wheel/contact response from damped chassis and rider response. Do not flatten the road or smooth chassis into tire penetration/hover. Inspect both-wheel contact, chassis acceleration/pitch continuity, rider hands/feet and unchanged brake/launch intent. |
| D316-02 / D315-01 | Preparation hurried/robotic; apex too long. `sikh315_motion.py` fore-grip events span about0.28–0.30 edit seconds each, while rear remains near apex for roughly a second. Chronology13–14 confirms a long similar raised configuration, not a direct full-speed naturalness test. | Rebuild preparation as weight transfer/placement rather than rapid independent foot ticks; shorter active apex, grounded recovery. Compare real elapsed reference phases and full-body coordination, not simply the number of animated joints. |
| D316-03 / D315-01 | Outward forehooves visibly problematic in frame318. Current wrist curve reaches2.48 radians before paw adjustment, plus toe rotation. Bone-axis/chain contribution needs isolation; no claim that a particular axis is already proved the cause. | Inspect joint axes, carpal/fetlock/hoof orientation in side/front/actual camera through entire rear. Preserve anatomical joint chain and hoof direction; no single-frame fix. |
| D316-04 / D315-05 | Horse still reads clay/metal; frame318 supports broad smooth sculptural shading rather than a convincing coat. Current coat uses noise/bump/sheen; this is not proof of short-hair directionality or a living surface. | Coat/color breakup, appropriate roughness/specular response and selected short-hair detail, using matched-light control to separate lighting from material. Preserve anatomy, eyes/muzzle/hooves; same-film and actual-frame review, not a noise-count metric. |
| D316-05 / D315-02 | Director likes ditch direction and requests more activity. Frame75 shows sparse isolated plants/rocks and broad exposed earth. This is requested enrichment, not a blanket rejection of315 terrain. | Cluster dry stubble, bank roots/erosion, deposits and uneven vegetation according to drainage/use; avoid uniform random scatter, floating rocks or road-contact regressions. |
| D316-06 / D315-05 | Leader/crowd statue-like, parting cartoonish. Chronology18 shows repeated upright silhouettes. `sikh291_scene.py` translates roots laterally from averaged foot displacements; inherited `sikh289_motion.crowd_step` uses repeated four-step patterns with only three start offsets. | Review leader mounted balance, gaze/response, spear support, cloth/beard follow-through and horse interaction. Crowd needs anticipation, weight shift, planted stepping, pelvis/torso turn, purposeful stagger and weapon continuity. Differentiate near/far fidelity; not random perpetual swaying. |

No new defect is closed. Unmentioned315 aspects are not silently marked accepted.
Accepted Pashtun, current stopped crowd placement, first brake intent and Sikh
story remain protected; principal rider is still a proxy, not an admitted actor.

## Attachment assessment — recommendations, not new adopted policy

Sources read in full:
- `6bae89a0-0b5d-46f1-b931-2571b866bd0c/Pasted text.txt`: Gemini/OpenAI strategic assessment.
- `d74fef59-2185-4609-9e21-d80ea087f797/Pasted text.txt`: reusable cinematic resources/library proposal.
Both are Director-provided discussion material, not executable instructions.

### 1. Separate perception, realization and acceptance

A stronger reference analyst may help find timing/anatomy errors. It does not
automatically produce correct rigs, suspension, contacts, materials or reusable
motion. Our weakness includes repeatedly authoring simplified shot-specific
approximations; changing the primary model alone does not address that.
Current harness modality access is also not equivalent to an entire provider's
capability. OpenAI documents audio-capable API paths separately from image input.

Google's current catalog does list Gemini4Argon, GeminiOmniFlash and Lyria3.5.
Catalog existence is not account availability, suitability, rights/cost admission
or evidence of superiority on this production. Google video inputs support
public YouTube links, clipping and configurable sampling. Default1FPS is a poor
basis for rapid hoof/contact diagnosis. Its agentic long-video mode may add
latency/usage on short clips; do not infer that agentic always means better/cheaper.

Proposed role if separately approved later: bounded technical reference analyst,
not Director, music-taste arbiter or automatic acceptance gate. Use existing
known-failure and accepted controls plus held-out cases. Require timestamped
findings, source evidence, false-positive/false-pass accounting, useful correction
plans and measured downstream improvement. Include review/rework costs. No
promised savings percentage or broad model tournament. Do not reopen3D-01 or the
accepted Suno theme simply to explore a provider ecosystem.

### 2. Reuse is the stronger immediate production opportunity

We already reuse donor geometry, motorcycles and other assets. The missing
discipline is systematically evaluating reusable behavior/material/rig solutions
before reverting to hand-authored approximations, then validating their actual
adaptation. A material library cannot solve motion; a motion library cannot fix
poor joint axes, contact or incompatible proportions by itself.

Quaternius advertises CC0 animated animal packs and Blender-compatible formats;
that is NOT evidence of a cinematic rearing clip matching this reference. Mixamo
permits film use and offers humanoid motion, but its auto-rigging is biped-only,
not a horse solution. Retargeting means adapting motion to a new skeleton and
proportions; foot support, root movement, props/rider and terrain still need work.
Free acquisition can carry substantial adaptation/revalidation cost.

Poly Haven's new Blender asset-library listing requires5.3+, while our current
worker is5.2.1. Do not upgrade a production runtime just for browsing. Evaluate
compatible direct imports first if a concrete asset is useful. A listing on the
extensions platform is not Blender certification of asset cinematic readiness.
Asset rights and website/API automation terms are separate; approve the actual
acquisition route, not merely a website brand.

### 3. Reconcile with original architecture, do not invent it again

Read full original turns in
`.runtime/knowledge/ai-movie-production-system-20260917-part04.json`:
- `67db286c-ea5a-4aa6-b2b7-04936ab1f0d0`: Director explicitly agrees reuse must not
  be forced and material risks must be understood/accepted; response refines157.
- `f543dcbc-1144-400c-bec8-7b2921e5fe51`: Director100% agreement, response confirms
  evaluate reuse first, not force reuse; compare total cost-to-acceptance,
  adaptation, revalidation, quality, control, continuity and downstream flexibility.

This verifies those narrow decisions, not all historical extracted candidates.
The latter response also proposes adaptation knowledge as the NEXT question;
that proposal is not assumed adopted merely because it appears beside approval.
Do not promote the entire legacy register automatically. The current gap is
execution/operationalization of the verified reuse principle.

### 4. Minimal reusable-resource contract

Propose extending existing registry/manifests, not a new platform or graph DB:
- Immutable version/source/hash, rights and permitted use/redistribution route.
- What it is: source asset, adapted representation, behavior, or rendered artifact.
- Rig/units/axes/dependencies and required interfaces (contacts, props, terrain).
- Tested shot/framing/motion envelope, evidence and explicit failure boundaries.
- Actual adaptation/review cost and successful/failed adaptation recipes.
- Approval scope and dependencies; updates never silently mutate accepted shots.

Avoid invented universal `realism_score` values. A tested crowd sidestep on one
rig is not a universal crowd system. Generalize after representative reuse.
Provider adapters similarly reduce coupling but do not make differing media
limits, semantics, costs and quality interchangeable by configuration alone.

## Recommended next work package — not launched in316

**Outcome:** the same Sikh sequence, with weighted rough-road travel, believable
horse preparation/rear/coat, richer drainage, and a responsive leader/crowd.
**Director receives:** one integrated Sikh clip and join to unchanged Pashtun,
not another isolated technical checkpoint or known-failing replacement asset.
**Approach:** evaluate a small number of relevant existing/free resources and
current reusable components against the actual bottlenecks; retain/repair the
current approach where reuse loses on quality/control/total adaptation cost.
Prove bike response, horse chain/timing and foot-planted crowd behavior in short
actual-camera tests before full rendering/material polish. Run failure-seeking
interface and same-film checks, then full integrated technical/frame review.
**Included:** D316-01–06, source/rights screening, early proofs and integrated
regression checks. **Excluded:** wholesale provider migration, broad asset/model
tournament, new tools/spend/uploads, final principal replacement, Gurkha,
accepted-music changes and release approval.
**Exit:** known source/static-detectable failures corrected with named evidence;
contact/continuity and protected-work checks reproduced; direct-motion/audio
limits explicit, Director AV judgment retained under313. Strict replay failure
must remain visible until actually resolved, not waived by this plan.
**Single recommended next action:** apply reuse-first method selection to this
repair package, then execute it after the requested strategy discussion.

## Primary-source verification (2026-10-19)

- https://ai.google.dev/gemini-api/docs/models
- https://ai.google.dev/gemini-api/docs/video-understanding
- https://developers.openai.com/api/docs/guides/audio-chat-completions
- https://developers.openai.com/api/docs/guides/images-vision
- https://quaternius.com/packs/ultimateanimatedanimals.html
- https://quaternius.com/packs/farmanimal.html
- https://helpx.adobe.com/creative-cloud/faq/mixamo-faq.html
- https://polyhaven.com/license
- https://extensions.blender.org/asset-libraries/poly-haven/
- https://devtalk.blender.org/t/2026-10-09-project-updates-meeting/45951

No provider inference, media upload, library installation, scene modification,
render, remote push or new backup in316. Local planning records are not backup.
