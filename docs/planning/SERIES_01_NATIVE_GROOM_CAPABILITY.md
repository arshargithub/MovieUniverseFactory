# Agent-only hair workflow investigation

2026-09-26. Continues the integrated front-hair objective after Director exchange138. Implementation/research, not a new planning exchange; counter remains138. This record and its compact operating card are the current continuation point, not another approved hairstyle.

## Capability result

**Latest: the Director-approved free-donor route has executed through three fits. Two MakeHuman card fits fail; the official Daniel Bystedt groom supplies coherent whole-head coverage, but still fails pair-B hairstyle/illustrated-language fidelity.** See the donor-route result below. It is a promising diagnostic, not approved hair or a live editable transferred groom. Earlier recommendations are proposal history, not permission to repeat stopped methods.

**Native hair authoring/control demonstrated; approved illustrated hair fidelity NOT_DEMONSTRATED.** These are different conclusions. The agent can create attached editable guides, operate installed interpolation/clumping nodes, render the preserved character, save the native, reopen it in a fresh process and make a controlled guide revision. The tested authoring recipes still fail the approved front/both-oblique target. No Director acceptance was requested for the known failures.

Authority remains `frontal-v02-individualized.png` and `portrait-v07-individualized.png` (pair B). Face width, accepted skin/anatomy/expressions are not revised to accommodate hair. The back is regression evidence, not a likeness target absent from those references. No scarf conceals the failures.

## What was tested, and what it teaches

| Mechanism | Actual evidence | Boundary / learning |
|---|---|---|
| Native part guides with Duplicate Hair Curves and Clump Hair Curves | Two rendered variants | Technically controllable but sparse part-only roots produce coverage gaps; higher clumping worsens them. Stop this hypothesis. |
| Two-dimensional scalp-root field with native interpolation | Three rendered variants, with one additional failed projection job and repair | Continuous coverage improves. Global shared sweeps still look generic/combed; support exposure, mechanical part and rear/style competition remain. Correct root distribution is necessary, not sufficient. Stop global field tuning. |
| Independently traced clump volumes over a native undercoat | Three rendered variants | Broad reference traces alone do not solve depth. An oversized undercoat hides the clumps; automatic scalp fitting exposes them but flattens the crown and creates bad transitions. Guide organization and three-dimensional overlap need authoring, not more density. Stop this fitting hypothesis. |
| Official painterly Brushstroke Tools node resources | Two setup variants plus one material-repair render; all internally rejected | Specialist-tool-mediated route, not a pre-made hairstyle. The repaired adapter renders painterly strips, but there are coverage holes, a mechanical part and an overly regular striped appearance. Not review-ready. |

These are related experiments in one integrated objective, not independent model benchmarks. Three-variant bounds are per hypothesis; the prior integrated19 activity remains in cumulative accounting. No human sculpting/technical coaching, new model switch, paid model calls or ready-made groom entered this turn. Existing reference images, FaceBuilder-derived head, earlier accepted work, original rear locks and prior Director feedback remain dependencies of the overall character—not a from-scratch human-free character claim.

## Verified native checkpoint — diagnostic only

Paths below are relative to `.runtime/art-direction/series01-facebuilder-trial-01/` on the project SSD:

- `native-groom-checkpoint-02/diagnostic-groom.blend`: recoverable **DIAGNOSTIC_NOT_APPROVED** native, rebuilding scalp-field variant2. Not canon, not a review candidate, not permission to replace edge03.
- `native-groom-checkpoint-02/checkpoint.json`: pinned source/reference/library bindings, guide and evaluated-geometry digests.
- `native-groom-verify-02/verification.json`: fresh-process verification and reversible revision test.
- `native-groom-operating/`: cumulative card, events and artifact checksums.

The native has448 editable guides /32,704 guide points, generating9,632 curves with the pinned local node library. Fresh-process reopen preserves guide positions/attributes, evaluated positions/count, accepted non-hair state and original visible rear-lock geometry exactly. The front render is pixel-identical to the saved checkpoint's baseline and the earlier corresponding preview. A fixed lift of three guides changes the evaluated output; rollback restores it exactly, without resaving or mutating the checkpoint. The changed render is a technical probe, not an approved artistic revision. Motion, rig attachment, portable interchange and production performance remain NOT_RUN.

Relevant unit tests cover structured-operation allowlists, input pins, fresh-output/symlink rejection and guide math. They do not establish beauty, collision-free generated children, or a general hair tool API. Source and failed previews remain immutable; each preview retains the handler that actually ran. The current handler is a diagnostic research implementation, not a Factory product module qualification.

80 relevant unit tests pass. All11 complete preview sets preserve accepted non-hair state and existing visible rear-lock geometry exactly. This does not imply pixel-identical face lighting: hair can cast different shadows onto the unchanged face.

Local implementation commit: `b25da06`. This report, learning delta and handoff are a separate design/evidence commit; neither is pushed remotely. The unrelated untracked `.DS_Store` is left untouched.

## Specialist-tool research and provenance

Installed Blender5.2.1 exposes native `Curves` creation and the stock hair node library. Local interfaces were inspected rather than assuming the online manual's socket layout. [Interpolate Hair Curves](https://docs.blender.org/manual/en/5.1/modeling/geometry_nodes/hair/generation/interpolate_hair_curves.html) describes surface-root interpolation from guides; [Clump Hair Curves](https://docs.blender.org/manual/en/5.1/modeling/geometry_nodes/hair/guides/clump_hair_curves.html) supplies grouped strand control. These explain tool mechanisms, not autonomous quality guarantees.

[Blender Studio Brushstroke Tools](https://extensions.blender.org/add-ons/brushstroke-tools/) provides procedural painterly stroke geometry and materials; its [grooming workflow](https://studio.blender.org/training/stylized-rendering-with-brushstrokes/brushstroke-grooming/) uses hair curves. The [tool documentation](https://studio.blender.org/tools/addons/brushstroke_tools) distinguishes surface fill from drawn strokes. This is a concrete alternative to finely shaded strands, but stylization cannot repair an incorrectly authored hairstyle silhouette or lock hierarchy. The official page warns of substantial geometry/render cost; low-density previews are essential.

Official version1.2.3 archive, downloaded for this investigation:

- `.runtime/brushstroke-tools-1.2.3-b66728b7.zip`, SHA256 `b66728b70b2d6af5ad942b5aa27fcc540db0972c22169480aa552d1e22061fe4` matches the official download binding.
- Extracted inspection copy `.runtime/brushstroke-tools-1.2.3-inspection/`;27 entries checked for path traversal/absolute paths/symlinks before extraction.
- Manifest declares `GPL-3.0-or-later`, Blender4.2+ and file access. No account, subscription or purchase was required. This records the package declaration, not a blanket distribution clearance for future productions.
- Core node resource SHA256 `11db84523ea8578b4aea112f227b7d1019c7d939d551c13701e3322a7b0bd95d`.
- No global add-on installation, downloaded Python execution or preferences modification. Only selected node groups/materials were appended with auto-execution disabled through the trusted fixed handler. Source inspection found explicit Blender5.2 modifier-API compatibility handling, but the node-only trial does not validate every add-on operator.

All Blender jobs use factory startup, disabled auto-execution and a stripped environment; no `.env` is passed. Failed root projection, JSON metadata serialization and evaluated-CURVES mesh-inspection jobs remain in the ledger. They are implementation failures, not additional artistic variants or evidence that Blender lacks the feature.

The specialist trial also exposed an agent integration mistake: the official material subtracts backfacing from its stroke mask. Zeroing the first input erased the strokes instead of making them two-sided. Inspection established the actual connections; the repair removes only the backface subtraction, binds `brush_stroke.color` and supplies a fixed strength for non-tablet-authored guides. `native-groom-brush-retry-03/` shows that repair rendering. It still fails artistically. Do not dismiss the tool based on the bald intermediate render, or mistake the repaired striped result for reference fidelity.

## Next decision and limits

Do not return to more fringe/density tweaks, replace the approved references with a better-looking failure, or default to hiring an artist. Tool access is no longer the principal unknown for native grooming. The unresolved work is reference-led spatial authoring plus coherent illustrated appearance. Retain the native-control proof and failed methods; assess the specialist painterly integration separately before committing to it. Neither tool-mediated nor asset-assisted routes should be relabelled native from-scratch success.

**Recommended next step, requiring a bounded continuation decision at the cumulative checkpoint:** one30-net-minute extension of the specialist-tool-mediated route, not an open-ended series of whole-hairstyle generators. Use the now-inspected brushstroke contract and author a small, explicit group of dominant part-to-temple strokes with fixed scalp roots, independently editable lifted depth and intentional overlap; establish their coverage and silhouette before adding fine strands or increasing density. Inspect the complete front and both obliques after integration. Use no more than three variants; retain current accepted non-hair guards, pair-B criteria and no-purchase/no-paid-call controls. Count the extension on this same objective. A passing subset is diagnostic only, not acceptance of the whole head. If this still cannot preserve the intended shape/appearance, report that authoring limit and compare further agent tool routes versus free-donor adaptation explicitly—without claiming a human artist is inherently required.

Why this is worth considering but not guaranteed: the established painterly tool addresses the fine-strand visual-language mismatch and can be driven without manual asset edits. It does not supply the missing artistic depth decisions. A more capable tool or model alone is not a success criterion. This proposal is **not executed or automatically budget-approved** by the current research result.

The current investigation produced19 reconciled native jobs (three failed jobs),11 full four-view preview sets plus three persistence/revision images, and one diagnostic native. That is not19 hairstyles. Local diagnostic artifacts total94,858,301 bytes before the compact card; the downloaded archive plus extracted resources add60,298,591 bytes. About464 native process seconds overlap captured assistant activity; they are not added to it. The final card includes integrated19's728.396053 captured seconds in the same cumulative objective. It excludes Director waits and leaves uncaptured intervals unknown.

Time and dependencies belong in the compact card. Engineering model/effort/tokens/subscription allocation and human review duration remain UNKNOWN. No quota-to-token/cost inference. Local code/docs commits do not back up ignored native/media files, and no remote push or backup occurs in this investigation.

## Approved extension result — dominant painterly locks, 2026-09-26

Director approved the proposed extension with “go ahead.” Activity `groom21` retains the previous **3,393.305756 captured seconds** rather than restarting objective accounting. Limit: 30 additional net minutes and at most three visual variants. The three-variant checkpoint was reached before the time allowance; unused allowance is not permission for a fourth variant. The FaceBuilder episode remains open, but this construction method is stopped.

The same pinned edge03 native, approved pair-B images and official Brushstroke Tools resources were used. No new download, installation, provider call, purchase, model switch or human asset edit. Four native jobs completed: three four-view renders and one resource-graph inspection. All12 images were inspected, including both obliques and back; no scarf or clothing conceals failures.

| Variant | Implemented difference | Internal visual outcome against pair B |
|---|---|---|
|01 |14 reference-led locks,70 editable strokes, fixed roots, explicit lifted depth and collision guard; quiet foundation instead of the448-guide visible field | FAIL: broad solid plates, toothed central part, outward-pointing ends and detached oblique layers. The reference's prominent forehead alone is not a pass. |
|02 |126 strokes separating dark supporting shapes from shorter warm accents; lateral clamping and progressive front-ray depth blending | FAIL: more deliberate colour hierarchy, but blocky oblique layers, discontinuous turns, exposed foundation and poor temple joins. This is not merely a texture issue. |
|03 |Same126-stroke organization; continuous radial wrap on the outer path and direct official strip conversion with analytic scalp normals | FAIL: some extreme lateral spikes reduced, but repeated ribbons, curled temple tips, a segmented part and conflicting front/rear languages remain. No integrated fidelity. |

The third variant changes both depth fitting and orientation. It **does not isolate their individual causal contributions**. The graph inspection clarifies the actual radius/color/normal connections; it does not prove that Brushstroke Tools is intrinsically unsuitable. Neither a lower-level converter nor a new add-on automatically supplies good three-dimensional artistic organization. Variant03 also returns to substantial outer-path surface fitting: the build-time `depth_policy` shorthand must not be interpreted as completely unconstrained authored depth in every variant.

Readiness: forehead/part **FAIL** (segmented part despite exposed forehead); lifted overlapping flow **FAIL**; temple/ear transition **FAIL**; coherent illustrated language **FAIL**; accepted non-hair preservation **PASS**; integrated side/rear appearance **FAIL**. Existing rear-lock geometry is exactly preserved, but the added front layers alter the total rear silhouette. This is not a pixel-level no-regression claim. Motion, fresh persistence/reopen of these candidates and release qualification **NOT_RUN**. No failed derivative was promoted or saved as a new character native.

Evidence, relative to the trial directory:

- `native-groom-brush-locks-01/` through `native-groom-brush-locks-03/`: immutable previews, result records and the exact handler snapshot used by each run.
- `native-groom-brush-inspect-03/inspection.json`: inspected official geometry-node contract.
- `native-groom-extension-operating/`: scoped event/card export, preview results, SHA-256 manifest and handler-dependency bindings. The previous card remains unchanged.

All three runs preserve accepted non-hair state and original rear-lock geometry exactly in-process, and the pinned source is unchanged. **76 focused unit tests pass** for the current native-groom, integrated-front, front-fit and edge-refinement handlers. These are technical guards, not an artistic success rate. There were no failed native jobs in this extension. Preview/inspection files total8,500,408 bytes before the compact card. Final captured time is in the extension card; it includes this turn's bookkeeping and excludes the Director wait. The cumulative number covers integrated19 + groom20 + groom21 only, **not all historical hair work**. Engineering usage and cost remain unknown. Implementation commit: `895782f`; these findings are a separate scoped local design/evidence commit. Neither is pushed; ignored render/operating artifacts are not backed up by Git. Unrelated `.DS_Store` preserved.

### Learning and next route decision

This strengthens a narrow conclusion: **this agent's tested guide-to-strip construction has not reproduced the approved hairstyle**, even with a specialist painterly renderer. It does not establish that agent-only character creation is impossible, that Blender is unsuitable, or that a human artist is necessary. Native editing/control remains demonstrated; reference-faithful spatial authoring remains unproven.

Do not spend another continuation on denser strips, another material, or another front-only generator. A library change that still produces the same strip-based spatial organization is not a genuinely new shape-authoring strategy. The next evidence-producing route I recommend is **agent-driven adaptation of an already-authored, free, editable hairstyle with suitable center-part/long-wave volume**. Its purpose is to test the asset-assisted boundary separately from de-novo authoring. No new donor has been found or verified by this extension, and success is not promised.

Start from the existing acquisition record, not a fresh uninformed search: `SERIES_01_FREE_DRESSING_ASSETS.md` records the prior `o4saken_long01` donor, failed first fit and embedded CC-BY/catalog license discrepancy. Do not blindly refit that rejected fringe/card asset. A new candidate must show an appropriate part, crown volume and both side transitions in actual mesh inspection, with usable individual terms and editable components. If none meets those prerequisites, report no suitable donor instead of importing a vaguely related asset and generating another long repair loop. Preserve the face, original pair-B target and no-purchase boundary. A donor-assisted result would be agent-only **adaptation with a pre-created asset**, not from-scratch creation.

This is a material workflow recommendation awaiting Director choice, not an executed acquisition or permission to expand work. No further hairstyle variant, new costume work, remote push or backup follows automatically.

## Approved free-donor route result — 2026-09-26

The Director approved the previous route recommendation. Activity `donor22` carries forward **4405.427814 captured seconds** from integrated19 + groom20 + groom21, not all historical hair work. Its20-minute reassessment rejects further fringe repair, checks the remaining21 Hair02 catalogue previews and permits one distinct official authored-groom source within the existing60-minute checkpoint. Work stops at **three total fit variants**, before60 minutes. No fourth fit is authorized by unused time.

### Acquisition and suitability

- [Long Wavy Hair by zHairezt](https://sketchfab.com/3d-models/long-wavy-hair-396fba6fb55046f7aea5ce4dc59b6c28) looks promising in the viewer, but the uploader states in the page comments that it was extracted from the Roblox Studio Marketplace. Its CC Attribution badge does not resolve upstream permission. **Excluded for unresolved provenance**, not an allegation that infringement is established; no download or account creation.
- [MakeHuman Hair02](https://static.makehumancommunity.org/assets/assetpacks/hair02.html), Elvaerwyn: complete official alternate-mirror archive downloaded, SHA256 `c681e5efd37df4007a52253a8d071aedbfe3b614f199d8dae4ae76d5bd7d95c9`. All147 archive paths checked; only six selected data files extracted for `elvs_lady_hippy_hair`, plus21 diagnostic thumbnails. The first mirror's incomplete timeout file is retained separately, never used. Embedded `CC_by` agrees with catalogue CC-BY at the family level; exact version remains unresolved. The individual page was unavailable. **Local diagnostic, not release-cleared.** All21 thumbnails inspected; none establishes a stronger lifted center-part target. One actual mesh inspected and fit:4001 vertices,2502 faces,52 connected sections, UV retained. Long waves alone were insufficient: its low side-swept fringe contradicts the approved forehead/part.
- [Official Blender Hair Styles demo](https://www.blender.org/download/demo-files/#hair), **Daniel Bystedt**: downloaded from the official page's public mirror link; SHA256 `1ad6202095c1793678fee7d69a7e9f8b5fdb6e5c293d300eb1062d2d437e8d48`. Catalogue and embedded credits say **CC BY-SA**, without an exact version in inspected credits. Local diagnostic only; resolve exact terms and ShareAlike implications before any derivative distribution. Embedded Python was present but never executed. Only native hair evaluation/data were used under disabled auto-execution; no donor face, eyebrows, skin or body were reused.

Acquisition manifests and originals: `.runtime/assets/series01-hair-donor22/`. A free price is not evidence of suitable rights, shape or technical structure. No purchase, subscription, global add-on install, project upload, paid model call or engineering-model switch.

### Three actual fits, not three successful hairstyles

| Fit | Method | Internal result against approved pair B |
|---|---|---|
|01 | MakeHuman authored topology/UVs, uniform fit and original texture | FAIL: fringe covers an eye, low/off-center framing, major scalp intersections/coverage gaps. Original blonde colour is diagnostic, not a proposed identity change. |
|02 | Same52 sections, front-only section lifting/sweeping, deeper fit and brown remap | FAIL: eyes exposed but low curtain framing persists; bare crown/back, projecting tips and flat card language. Stop donor, not another repair loop. |
|03 | Bystedt authored long-hair groom; affine retarget, collision-only correction, plain reconstructed brown shader | **PROMISING STRUCTURAL DIAGNOSTIC; reference fidelity FAIL.** Coherent front/both-oblique/rear coverage and natural continuous flow, without the prior plate construction. Still side-parted, too strand-dominant and straight, insufficient reference-specific forehead framing and broad painted sweeps; flyaways/ends need control. No Director cosmetic acceptance requested. |

Fit03 source has346 main guides +30 secondary guides. Native evaluation produced11193 +30 rendered curves, all retained (sampling stride1);349 point adjustments include rendered and guide-copy points, not349 unique collision sites or a collision-free guarantee. A simple collision guard does not certify every strand segment. The side/rear coverage assessment is visual at the four static diagnostic views. Back remains provisional because pair B does not show it.

**Important control limitation:** Fit03 renders copied evaluated curves. Copies of376 authored guides are retained in the in-memory scene but are **not connected to drive that baked render**. This proves agent-operated transfer of an existing authored shape, not a qualified editable groom-transfer pipeline. No new `.blend` was saved or promoted. Future guide adaptation must preserve/rebuild a functioning guide-to-render relationship rather than editing thousands of baked strands. Motion, scalp attachment under expression/head movement, fresh native reopen and portable reuse remain NOT_RUN for this donor.

All12 renders were inspected. Three runs preserve accepted non-hair state exactly in process; source edge03 remains unchanged. Original portrait pair B remains the authority. This is not pixel-identical face lighting, because replacement hair changes shadows. No face, neck, skin, eyes or facial-control adjustment was used to improve the fit.

### Evidence and next decision

Trial-directory evidence: `authored-donor22-01/`, `-02/`, `-03/`; `authored-donor22-demo-inspection/`; compact card `authored-donor22-operating/`. Each job retains its exact handler snapshot. Four native jobs completed successfully; one test command named a nonexistent test file and ran no tests, then corrected suites passed **102 tests** in total. This failure is retained in the operating ledger. These tests check structured jobs, pins/output guards and existing hair controls—not creative quality.

The current acquisition/adaptation scope is complete at its variant checkpoint; final hair is not. **Recommend a bounded30-net-minute continuation on the Bystedt donor, at most three variants, not a new broad asset search:** first reconnect the authored guides and native interpolation on the unchanged character; then adjust the part/root lift and front-to-temple sweep against pair B, using both obliques as mandatory guards. Establish shape before illustrated shading. Save/reopen a diagnostic native only when useful; never mark it accepted merely because it is technically editable. The continuation requires a new allowance beyond the three-fit bound. It is not automatically authorized here, and it must retain cumulative objective time.

This result supports **agent-only asset-assisted adaptation as a promising route**. It does not demonstrate from-scratch creation, finished reference fidelity, production readiness, model superiority or a requirement for a human artist. The supplied artistic structure is a material pre-created dependency and must remain visible in capability claims.

Local implementation commit: `f36905a`; design/evidence committed separately. Neither is pushed. Ignored downloads/renders/cards are not backed up by Git. Engineering model, effort, tokens and cost remain unknown; known paid model calls and asset purchases are zero. Final captured activity and cumulative time are in the compact card, excluding Director waits and without adding overlapping native process time again. Planning counter stays138; next checkpoint140. Unrelated `.DS_Store` remains untouched.

The compact six-view comparison contains the unchanged approved pair and fit03 front/both obliques/back, clearly labelled diagnostic. Display-size JPEGs are for comparison only, not replacement authorities. Navigation/state logic passed a local check; browser layout verification was unavailable because local-file navigation is blocked. Original full-resolution PNGs remain in the evidence folders.
