# 3D-04 — Timeline-local performance revision

## Question

Can Movie Factory improve a bounded section of the accepted character's run performance while preserving the motion, character state, camera, lighting, and timing outside the authorized interval?

## Frozen baseline

- Use the 3D-03.1 character and corrected run action bound by `3d-03-1-v1-green-evidence`.
- Build a 96-frame, 24 fps timeline from the admitted 24 fps run cycle. The reviewed shot lasts four seconds.
- Use explicit physical-time mapping. For an action authored at `source_fps` on a `timeline_fps` timeline, the NLA scale is `timeline_fps / source_fps`, and timeline-to-action evaluation may use fractional source frames.
- Do not include a duplicate loop endpoint as an additional held playback frame.
- Freeze camera B, lighting, skin, rig, mesh, weights, and all motion outside frames 40–70.

## Revision

Apply exactly one structured operation:

```json
{
  "op": "adjust_run_body_dynamics",
  "entity_id": "character_01",
  "frame_start": 40,
  "frame_end": 70,
  "vertical_body_amplitude_m": 0.035,
  "forward_torso_lean_degrees": 6.0
}
```

The operation adds a bounded vertical body rhythm synchronized to support changes and a small forward torso lean. Boundary blending must give identical evaluated state at frames 39 and 71 before and after revision. The implementation is fixed trusted code; no generated Blender Python is accepted.

## Validation

- Compare evaluated meshes, action channels, and semantic snapshots before and after save/reopen.
- Require exact preservation for frames 1–39 and 71–96, including fractional samples at 38.5, 39.5, 70.5, and 71.5.
- Require the edited interval to differ materially while retaining finite geometry, limb lengths, grounding, alternating support, and bounded frame-to-frame velocity.
- Measure support-foot sliding during contact, vertical body range, contact transitions, seam position and velocity, motion arcs, and discontinuities at both edit boundaries.
- Render and play the complete four-second before/after clips at 24 fps. Director review must decide whether the revised interval reads more clearly as running and whether the transition into and out of it is visible.
- Track total local compute, provider calls, and known API cost per accepted second. Provider use is restricted to a separately frozen secondary evaluator and cannot override deterministic or Director gates.

## Gates

- **GREEN:** exact outside-range preservation, machine-valid timing and contacts, save/reopen and offline replay, stronger Director-rated run readability, and all cost evidence pass.
- **YELLOW:** engineering gates pass but Director review is pending or the improvement is too subtle to distinguish reliably.
- **RED:** any outside-range state changes, visible boundary pops, worse foot sliding, invalid timing, deformation, loss of grounding, replay drift, or Director rejection.

## Non-goals

This experiment does not qualify arbitrary natural-language animation editing, new action generation, retargeting, horizontal locomotion, character-prop interaction, facial acting, or production-quality performance.
