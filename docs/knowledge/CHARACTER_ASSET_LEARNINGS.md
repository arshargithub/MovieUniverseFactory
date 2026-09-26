# Character asset learning and review contract

2026-09-26 · Release 01 exchange 137 · applies to the Pashtun character and subsequent asset work.

## Executive conclusion

The Director sees incremental progress but rejects the sustainability of many short passes followed by predictable requests for review. The goal remains the approved illustrated character, not a succession of technically sound hair derivatives. The assistant has repeatedly documented the main visual failure and then presented a partial candidate anyway. **That is an internal quality-control and stopping-rule failure, not missing Director feedback.**

This record changes the working process now. It does not approve edge03, change the aesthetic, authorize purchases/provider calls, start a replacement groom, or claim Blender is incapable. Existing assets and failed evidence stay intact. No native edits or renders were made for this retrospective.

## Evidence, scope and economics

[Audited card summary](CHARACTER_HAIR_RETROSPECTIVE_EVIDENCE.json) records eleven existing card paths and SHA-256 digests, with their field-normalized totals:

| Recorded measure | Observed total | Meaning and limit |
|---|---:|---|
| Hair-related work packages | 11 | Hair/anatomy through edge03; includes wider hair and some neck work, not solely the front |
| Captured assistant activity | 15,155.05 seconds, about 4 h 13 min | Sum of recorded activities; excludes Director waits, misses some setup/handoff effort and human review time |
| Blender job attempts | 68 | Includes diagnostics, previews, failed attempts, native rebuilds, packaging and verification; **not 68 distinct designs** |
| Native process time | 2,867.03 seconds, about 48 min | Already occurs within work; do not add to activity time or treat as CPU time |
| Reported artifact growth | 1,157,348,421 bytes, about 1.16 GB | Sum of card scopes, not a fresh deduplicated disk audit or backup check |
| Finished hairstyle acceptance | None found | Directional encouragement is not full acceptance; accepted face/skin are separate |
| Engineering token/cost total | UNKNOWN | Cards lack it; subscription usage is not free or an inferable API bill |

The evidence suggests the problem is not primarily waiting for renders. Diagnosis, authoring, integration, orchestration and repeated handoffs matter, but the cards do not support a precise overhead breakdown. Do not invent an 81% waste statistic by subtracting incompatible totals. This subset is not the entire character project's cost. One built-in hair-texture generation is recorded in hair-flow; it is separate from the cards' zero project-provider calls and has unknown usage/cost.

## What worked — retain and reuse

| Finding | Evidence | Carry forward |
|---|---|---|
| Separate geometry, material and illumination before editing | [Bilateral face review](../planning/SERIES_01_BILATERAL_FACE_REVIEW.md); matched camera-relative light helped review the face | Keep paired clay, color-only and lit diagnostics internal and use only the ones needed to isolate the defect |
| Preserve liked identity while fixing a bounded region | Bilateral face accepted; [posterior anatomy16 accepted](../planning/SERIES_01_NECK_ANATOMY_REVIEW_04.md) | Keep protected state explicit; don't slim the face or deform an accepted neck to disguise hair problems |
| Change representation when local patching stops helping | [Rejected procedural skin infill](../planning/SERIES_01_BUST_SKIN_REVIEW_03.md) → [authored atlas01](../planning/SERIES_01_BUST_SKIN_REVIEW_04.md) → [accepted atlas02](../planning/SERIES_01_BUST_SKIN_REVIEW_05.md) | Map-scale authored texture plus protected original face succeeded where more tiny repeated patches did not. This is evidence for an authoring-method change, not proof that generated maps solve all materials |
| Test a whole meaningful behaviour | [Restrained facial performance accepted](../planning/SERIES_01_FACE_SURFACE_INTEGRATION_01.md) | Validate complete target behaviour, not isolated parameter movement; scope acceptance to tested expressions, not speech/general rig capability |
| Matched face scale exposes framing mistakes | [Forehead review and rejection](../planning/SERIES_01_FOREHEAD_PROPORTION_REVIEW_01.md); [front-fit](../planning/SERIES_01_HAIR_FRONT_FIT_01.md) | Compare the whole frontal composition at consistent eye scale; expose full originals as well as detail crops |
| Immutable inputs, source snapshots and protected-state checks prevent regressions | Hair preview/package manifests and native reopen records | Keep these inexpensive safeguards. Passing them proves preservation, not beauty. They should not become the headline artistic result |
| Preview first; save and verify a delivery candidate once | [Illustrated section](../planning/SERIES_01_ILLUSTRATED_HAIR_SECTION_01.md) retained four failures without promoting a native | Keep failed previews and recipes; avoid rebuilding a large review package at every routine milestone |
| Actual donor inspection beats labels | [Free asset record](../planning/SERIES_01_FREE_DRESSING_ASSETS.md) corrected a shemagh assumption and a catalog/file license discrepancy | Verify geometry, openings, adaptability and embedded license before investing in a supposedly free donor |

## What failed — do not repeat under a new pass name

1. **Optimizing symptoms independently.** A higher hairline can reveal more skin while making the entire head look more receded and wig-like. Forehead opening, part, root lift, temple volume and lock flow are one visual composition. The rejected larger lift proves that parameter direction is not improvement.
2. **Polishing a structurally inadequate base.** The shape study already said the crown was too regular and lacked secondary overlap. Later texture, lift and edge work inherited that limitation. A fine fringe cannot turn a fused cap into the reference's distinct overlapping locks.
3. **Treating texture projection as solved 3D appearance.** Front brushwork helped identity, but narrow source strips/clamped rows created bands; obliques stretched highlights. The illustration's painted shadows and highlights are not a calibrated albedo/shape reconstruction. Preserve successful front detail without assuming it transfers to every view.
4. **Competing visual languages.** Regular modeled fibers over the preferred painted hair looked like separate systems. Broad rolled ribbons and repeated lofts also failed. More strands, randomness or resolution did not address the required lock hierarchy.
5. **Trading one defect for another.** Body-surface fitting copied ear contours; root burial exposed rear skin; remeshing damaged the part and tips. Review the full claimed region after every change, not only the repaired spot.
6. **Repeatedly asking whether an unfinished mismatch is closer.** Several reports explicitly admitted cap-like mass/temple joins, then delivered another review. The Director had already told us what was wrong. Marking a candidate YELLOW is honest labeling, but does not make the interruption useful.
7. **Resetting the stopping rule by naming another pass.** Three variants per hypothesis and a short pass did not cap cumulative effort on the same unresolved objective. Extra 'defect repairs' still consume work. Track the integrated deliverable across prompts, methods and days.
8. **Over-packaging partial work.** Repeated custom handlers, large galleries, near-identical reports and native rebuilds add cognitive/storage cost. Keep exact recipes and failure evidence, but one current work card and one reusable comparison should carry an integrated attempt. Do not build a generalized harness merely to optimize this one asset.
9. **Incomplete cost visibility.** Time capture is useful but often began after context recovery; tokens remained unknown. Start before substantive work, retain cumulative work by objective, distinguish jobs from variants and measure review burden. Do not substitute test counts, quota percentages or artifact volume for value delivered.

## Binding process clarification: internal work versus Director review

The existing instruction to continue in-scope work is reaffirmed by exchange137. Apply these rules to the current hair objective and future agreed asset objectives:

- A routine improvement, local commit, three-preview check or end of a 20-minute diagnostic interval is **not a Director approval gate**. Reassess internally, keep concise progress commentary, and continue within the existing scope/budget.
- Maintain one defect list tied to approved references. A candidate that still obviously fails a known must-have stays internal. Do not ask the Director to rediscover it.
- Ask for review when the **integrated agreed visual target is review-ready**, when the user asks to see progress, or when a genuine creative tradeoff requires taste rather than more execution.
- Escalate a genuine blocker with the failed hypothesis, evidence, remaining options and one recommendation. 'Still looks like a cap; should I keep going?' is not a decision.
- Do not silently relax the reference target, hide defects with scarf/lighting, alter approved identity, buy assets, switch providers/spend or expand scope. Such changes still require authorization.
- Retain the operating ledger's 20-net-minute diagnostic / three-variant-per-hypothesis / 60-net-minute overall reassessment. For the **next integrated hair attempt**, count the overall work across prompts and renamed passes; do not restart the allowance. At 60 minutes without a review-ready result, stop for an honest capability/method decision, not another cosmetic approval request. This is not a guarantee of completion in one hour or permission for unlimited work.
- Three variants is a ceiling, not a requirement. Change a hypothesis after evidence of failure; do not run two more versions merely to fill the budget. Defect corrections and packaging count toward time/storage, even when not artistic variants.
- Save recoverable checkpoints as needed without promoting them to review packages. Use cheap matched previews during iteration. Run relevant fast tests and protection checks throughout, full packaging/reopen validation at actual handoff. Preserve failures; no deletion authorized.

## Next hair deliverable: one integrated front, not another edge pass

**Target:** the approved pair-B hair framing reads convincingly on the preserved character from the front and both current obliques. No hairstyle/back reinvention, clothes, motion or face redesign. The back remains a regression view and provisional extrapolation, not a matching target that the references cannot establish.

**Proposed authoring method for the next execution (not executed here):** use explicit, editable reference-led guides for the few dominant part-to-temple sweeps and their overlaps. Treat the present fused front shell as support/reference, not sacred geometry. Rework only hair if the shell cannot support the required shape hierarchy. This must be materially different from another global lift, shallow sinusoidal warp, rolled-tube set or denser fringe. Fit guide shapes, taper, depth ordering and roots as a connected composition; put illustrated material on those forms only after they read correctly. Reuse known scalp-only fitting and preservation handlers rather than rebuilding the accepted bust.

Before authoring, inspect both references and current front at comparable eye scale, mark the actual part/root/temple landmarks and dominant lock paths, and declare which mismatch each proposed shape edit addresses. A simple annotated guide is an internal execution aid, **not a new Director concept approval round**. Do not claim two stylized illustrations determine unique 3D geometry. Pose/light differences and the accepted wider 3D jaw are fixed comparison caveats, not excuses to change the face.

Internal review sheet; all must be PASS or justified NOT_APPLICABLE for a review-ready candidate:

| Must-have | Evidence required |
|---|---|
| Prominent, tapered forehead and recognizable part | Reference/new fronts at matched face scale; no broad receded arch or low heavy edge |
| Root lift and unequal overlapping sweeps | Front plus both obliques; reject flat cap, mirrored tubes and rolled ribbon forms |
| Natural temple/ear transition | Both temple views; no floating root, solid sideburn plate, exposed support or disconnected side join |
| One illustrated hair language | Textured views match pair B's broad selective highlights, dark separation and flow; no competing painted/fiber layers or obvious projection bands |
| Character and geometry protection | Non-hair preservation checks; no changes to accepted face/skin/anatomy/expressions |
| No regression in claimed region | Both obliques and rear sanity view, not one flattering angle; unknown back design not mislabeled a match |
| Ordinary-view readability | Inspect compact final-review size as well as defect crops; detail invisible at delivery size is not a reason for more cosmetic loops |

This is an assistant readiness gate, **not automatic Director acceptance**. Do not invent a 90% similarity score, aggregate unlike dimensions into a flattering number, or use tests to override visible failure. Record the dominant remaining defect after each preview. Repeated failure of the same must-have triggers a method reassessment, not another presentation of 'closer.'

If explicit guide/layer authoring still fails within the next integrated bound, report that **this autonomous authoring route has not met the target economically**. Then compare concrete alternatives with the Director—different acquisition/authoring route or a scoped hybrid finish—without claiming they will work, abandoning approved likeness, assuming paid-asset authority, or interpreting this as Blender's overall failure. No new provider, model setting, dependency or purchase is selected here.

## Applying this beyond hair

### Execution follow-through, 2026-09-26

The [first integrated attempt](../planning/SERIES_01_INTEGRATED_HAIR_ATTEMPT_01.md) tested three explicit-guide section variants and **rejected all three internally**, with no new native promoted. Editable guide paths alone were insufficient: hand-authored depth floated, scalp fitting buried the sections, and quiet-support/envelope fitting exposed segmented roots and temple joins. This did not become a successful sculptural representation change. Stop this hypothesis; recommend a materially different, hands-on authoring route rather than another geometry-handler family. The useful process change is stopping before requesting predictable cosmetic feedback, not declaring the visual objective achieved. Costs are separately captured in the linked operating card and are not added silently to the eleven-card historical table above.

- **Scarf and garments:** solve silhouette, opening, major folds, weight and body clearance together before weave/microfolds. Use actual donor topology and license checks. Test the visible continuous shoulder/belt path before detailed leather shading.
- **Skin/anatomy:** retain accepted results; classify a new defect with clay/emission/light controls before editing. A local texture fix should not initiate a face remodel.
- **Performance:** motion brief first, complete low-cost motion with all coordinated joints before high-quality frames; evaluate identity and contact/clearance, not isolated key poses. Static hair acceptance will not qualify gallop or cloth/hair dynamics.
- **Environments/props:** invest detail where recurrence and shot visibility justify it. Reuse an asset/scene when it serves the image; do not let a convenient donor dictate art direction.
- **Sound/music:** use a representative complete cue or scene with timing/intelligibility/identity/rights criteria, not endless isolated timbre variants. No sound provider qualification follows from the hair result.
- **Factory handoff:** keep approved references, rejected methods, current defects, source pointers, operating capture and the exact next objective in portable project records. Do not require reconstruction of hundreds of chat messages.

## Decision continuity and adoption

Consulted [knowledge index](README.md), the historical register and [Release applicability](RELEASE_01_APPLICABILITY.md). Re-read full source turns `a253f9d8-af6f-4a6d-91f7-87a06b6e7200` and `239aaa29-fb22-44f7-a8d7-886a9ad8dc5b`: the Director explicitly required agreed review checkpoints. **ADOPT** that contract; exchange137 changes this asset's checkpoint granularity, not the Director's final authority. The old example checkpoint list is not a mandate for this production.

Re-read full asset-creation proposal `e2c7fcd8-04a8-4696-98d5-cf88ff29f3e8` and acceptance `c989f205-885e-4232-8bca-4902f9579c30`: a persistent controllable asset is the goal, not proving that the agent personally models every polygon. **ADOPT**, no global renderer switch. Hybrid/direct/acquired routes remain possible; current autonomous hair authoring is unqualified, not evidence against the whole persistent-world architecture. Existing [realization review](../planning/SERIES_01_REALIZATION_REVIEW.md) remains applicable.

No new release gate passes. Planning checkpoint remains 140. This is a scoped local design record; remote push and off-device media backup are separate operations.
