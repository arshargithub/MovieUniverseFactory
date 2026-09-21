# Face performance readiness — recommendation, not implementation approval

Exchange120 / CP-012, 2026-09-20. Director accepts atlas02 skin as good enough and asks what facial groundwork should precede further dressing. **Static skin work is closed at the accepted version.** Do not continue cosmetic iterations without a concrete performance defect or new Director request.

Accepted native: `.runtime/art-direction/series01-facebuilder-trial-01/bust-atlas-build-02/character-upperbody.blend`, SHA256 `408a982610f4fe9260101f34245099ae80731de9c7b56e58e46963f854a22dd5`. Original portrait pair B and approved anatomy remain authorities. Earlier candidates remain intact. The historical build record's `skin_director_accepted:false` describes its creation-time status; this later Director acceptance supersedes it without rewriting immutable evidence.

## Read-only findings

Fresh native inventory at `bust-atlas-verify-02/result.json`; asset not saved or modified. Visible `MF_continuous_head_neck`:47,273 vertices, no shape keys, no modifiers, no vertex groups, no object animation data or parent. No armature objects in scene. Hidden `FBHead`:18,024 vertices and only Basis plus an old lower-cheek-definition candidate, **not an expression library**. No independently identified eye/teeth/tongue setup; objects named buckle tongue are garment hardware. Inventory does not prove the absence of every possible internal mesh surface; mouth interior, eyelid rims and edge flow still require topology inspection.

Current atlas shader samples Object coordinates. Inference from implementation: facial deformation may cause texture sliding. Before performance, freeze texture attachment using rest-surface UV coordinates and/or bake the accepted composite color to stable UVs, then compare against the accepted renders. Do not silently change appearance during this technical preparation.

## Recommended bounded next deliverable

One **minimum facial-performance readiness pass**, within existing A5/E1; not a new generic experiment or another beauty pass. No implementation, image call, subscription or purchase authorized by this recommendation. Complete the existing motion-design brief before performance changes.

1. Freeze accepted neutral geometry/look as immutable reference. Inspect eyelid/lip topology and original FaceBuilder compatibility before broad retopology. Modified vertex count rules out blindly copying indexed shape-key arrays from the original head.
2. Stabilize material attachment and verify neutral appearance, skin/UV persistence and reopen behavior. Keep paint marks following deforming skin rather than fixed object-space positions.
3. Create independently aimable eyes with eyelids that close fully and follow gaze. Preserve approved eye shape/color and avoid painting the iris onto a lid that then closes. Separate eyelash/brow geometry only if necessary; painted brows may follow the underlying brow skin for this stylized look.
4. Minimum facial controls: brows raised/lowered and restrained unilateral lift; cheek raise/squint coordinated with eyes; jaw opening; lips closed/pressed/parted and a restrained smile/frown. Nose follows surrounding deformation; nostril flaring and specialized nose controls are later needs. Inspect lip seal and mouth cavity; basic inner-mouth/teeth/tongue setup is needed before shots reveal them, not a detailed dental modeling project now.
5. A short8–12second silent acting proof: neutral → notice an offscreen cue → blink/gaze shift → composed skepticism → small warm smile → return to accepted neutral, with front and oblique review. Also include a separate small jaw-open diagnostic. Correctives only for visible clipping/pinching/identity loss. These expressions are proposed tests, not new personality canon.

Stop when gaze/blink/lip seal and restrained expressions preserve likeness, texture does not swim, deformations do not expose holes/clipping, controls persist after reopen, and returning to neutral restores the accepted asset. Then resume hair/scarf with eyelid/brow/jaw motion clearance. Full speech/lip-sync phonemes, capture routing, exhaustive expressions, wrinkles, extreme shouting, and production polish wait for script/shot requirements. Routine shot-specific refinements will still be normal; do not promise never to revisit a recurring character.

## Reuse route and cost discipline

First investigate the already-installed FaceBuilder route on a copy of the original head. KeenTools documents51 built-in ARKit-compatible FACS blendshapes; these are deformation building blocks, not51 finished emotions. Their presence on this modified bust, transfer quality and useful expression range are **not verified**. If recoverable, transfer/adapt only needed shapes; otherwise choose a small custom/rig-based route after the topology diagnostic. Do not buy another tool or attempt a complete manual rig before checking this reuse opportunity.

Proposed first diagnostic checkpoint:20netminutes, no paid calls. Stop with findings if original shape generation/transfer or topology is incompatible; do not disguise that as a routine extension into hours of rebuilding. Agree a bounded implementation scope after diagnosis. No full-system deadline or guaranteed one-pass facial completion is claimed.

Official references checked2026-09-20: [FaceBuilder features and workflow](https://keentools.io/products/facebuilder-for-blender); [Blender modular facial components](https://docs.blender.org/manual/en/5.0/addons/rigging/rigify/rig_types/face.html); [Blender texture-coordinate semantics](https://docs.blender.org/manual/en/2.81/render/shader_nodes/input/texture_coordinate.html). Newer English manual fetches failed; stable coordinate concepts were checked against retrievable official documentation and actual handler code. No pricing promise or new license action.

## Historical continuity

ADOPT original four-layer character ownership: identity, story-time state, representation and production performance remain separate. Full original question16 turn `440963ab-ce01-495c-ac82-19693a9bec86` and following Director approval `32c16454-894f-4d22-9c8a-c0746b069297` were re-read in local source snapshots. The approved skin is a representation version; a skeptical expression is shot performance, not a canonical redesign. ADOPT [motion-before-implementation decision0004](../decisions/0004-motion-design-before-implementation.md). DEFER exhaustive facial capture/general arbitrary-rig support. No earlier capability route or identity decision is replaced.
