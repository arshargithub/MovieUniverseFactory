# Forefoot pose repair: bounded contract

Authorized after the six-minute diagnosis. Scope: at most 20 recorded minutes, two native process-minutes initially (one 90-second worker plus bounded follow-up), no paid API calls, no full gait bake or FX render until a pose-level checkpoint. Existing assets, head, cameras, source scenes and failed results remain unchanged. This is a manually authored engineering brief adapting the motion-design template; no new reference media was reviewed.

## Movement and constraints

Intention remains a full-pace extended gallop. During recovery, allow the hoof recovery trajectory to change to preserve the complete limb's articulation; a predefined 62 cm lift is not intrinsically required. During support, retain the existing 12 m/s world-stationary hoof targets and <=5 cm target error / <=2 cm penetration screens. Foot orientation, heel roll and shoulder/elbow articulation must cooperate. Keep source upper-body motion and accepted rider/head design for this pose test; no speculative human motion additions.

Use clean source control bases and the unchanged third candidate. At the three previously diagnosed recovery frames (1.875, 3.25, 3.875), solve a deterministic blend toward source foot location, rotation and heel orientation. Examine translation-only and orientation-only controls first; these are unkeyed numerical search samples, not rendered gait variants. Include source and untouched candidate controls. Check support poses separately before claiming the corrected controls can support a gait.

## Pre-dispatch development screens

The old same-frame bone comparison remains a recorded failure; it is superseded only for this prospective *pose development test*, not retroactively. Its source changes bone length with phase, so it cannot be the sole anatomy criterion.

- Segment lengths must remain within the complete clean-source cycle envelope, with 3% numerical allowance at each end. This admits the source's own deform mechanism rather than forcing its same-frame stretch into a differently timed gait. Record ratios to rest separately.
- Upper-arm/forearm and forearm/forefoot direction angles must remain in the clean source-cycle range with 5 degrees development margin. These are rig-relative feasibility bounds, not universal horse anatomy.
- Each measured right-forelimb edge length and triangle area must stay within its clean source-cycle envelope with the previously used 5% diagnostic margin. No looser mesh ceiling is adopted to fit the candidate. Finite geometry and identical topology required. The weighted region is incomplete; full-mesh coverage is required before gait qualification.
- Source poses must pass the envelope screen; the unchanged candidate and deliberate 30% scale distortion must fail. Do not credit control failure on an unrelated pre-existing error.
- Search preserves scale and original rest/skin data. Recovery hoof placement may change, so record its deviation from the previous trajectory; this is not evidence of preserving that discarded swing target. All three recovery poses must pass to call the pose repair complete.

Use at most 21 predetermined interpolation samples per recovery frame plus bounded component-isolation samples; choose the smallest reference blend satisfying the angle, segment and mesh screens. No model-generated runtime code or scene scripts. Fixed repository handler and hash-bound input only.

## Stop and handoff

No complete gait is established by passing isolated poses. Before a new gait: fit a smooth recovery curve through feasible poses, retain support targets, test stance compatibility and all four legs, dense fractional sampling, finite meshes, contacts, seam continuity and saved-scene replay. Review inexpensive complete motion before freezing scored configuration. Combine tail/dust in the subsequent consolidated preview once motion qualifies. If no pose solution exists under this contract, preserve the failed test and identify the binding constraint; do not relax limits or silently extend the budget.

## Bounded parent-space follow-up, before dispatch

The first local-basis interpolation passes only frame 3.25. Corrected distortion control now fails after modifying active shape-key coordinates, while the clean source passes. Preserve the first ineffective control as a failed test implementation.

Within the same 20-minute scope, test the parent-space hypothesis using the evaluated source control pose matrices rather than local bases. At most 21 interpolation samples per recovery frame, fixed 50-second native timeout; retain all thresholds. This tests a distinct transform-conversion hypothesis, not a fourth gait or a changed acceptance screen. Local-space source values can produce different evaluated poses when the parent mechanism differs. No production bake unless all required checks pass.
