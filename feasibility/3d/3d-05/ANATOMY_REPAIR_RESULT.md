# 3D-05 anatomy repair: scored result awaiting Director

Run: `interaction-v1-20260911T160515Z-85655dd3`.

[Complete anonymous A/B playback](../../../runs/3d05/interaction-v1-20260911T160515Z-85655dd3/review/index.html)

Decision: **YELLOW, machine checks passed, Director PENDING**. The earlier thumb-down run remains RED. This result does not assert Director acceptance or establish general anatomical correctness.

- Implementation correction commit: `403c66a`; final pre-run source/configuration commit: `2bed69e`. The worktree was clean before dispatch and the recorded source binding is EXACT_PRE_RUN.
- Native scene SHA-256: `4ff4a28c1d2f7628b64a5eebba87f5f32bf39def240281ec6de7ec6571950e6f`.
- 76 deterministic checks passed, including six save/reopen checkpoints, exact semantic replay, and matching evaluated replay metrics.
- All ten real Blender corruption controls failed their designated gates.
- 515 sampled times per clip; maximum wrist twist 16.645 degrees; minimum held contact coverage 186.495 degrees. Thumb/finger distances remain within 3.599/2.536 mm. Sampled hand–support penetration is zero.
- Complete playback: 96 frames × two clips × three views, all 576 image references decoded and verified. All 1,470 inventoried artifacts matched their recorded sizes and SHA-256 hashes.
- Scored execution took 717.24 seconds. Provider calls: 0; known API cost: $0. Engineering token/cost totals and Director review time remain unknown, not zero.
- Offline suite: 125 passed, 11 opt-in tests deselected. Pre-score native test history, including the ineffective connected-bone failure injection and its verified geometry replacement, is preserved in [ANATOMY_REPAIR.md](ANATOMY_REPAIR.md).

Review the complete approach, thumb-up closure, wrist/elbow posture, lift, and hold in all three views. Record A/B scores, visible defects, preference, and review duration. The player estimates visible-page time. Engineering attribution and this pending outcome are recorded in the central engineering-intelligence ledger; there is no accepted Astra-versus-Sol result or Sol handoff yet.

## Subsequent Director feedback: coordinated motion planning requested

The Director reports that the lift appears driven by the shoulder/upper arm with a level wrist/forearm presentation and slight elbow distortion. They also note absent head/torso attention as a more minor issue, possibly outside the existing criteria. They request a natural-movement planning pass before further implementation.

Machine results remain unchanged. Status remains YELLOW / acceptance PENDING; no numerical scores, preference, review duration or major-defect severity were supplied. The earlier result and review manifest are preserved in the run's `review-history/before-organic-motion-feedback/` directory. The updated inventory includes the new feedback and this history; the 1,470-artifact figure above describes the original pre-feedback verification.

See [MOTION_PLAN.md](MOTION_PLAN.md) for the proposed coordinated lift and [Decision 0004](../../../docs/decisions/0004-motion-design-before-implementation.md) for the adopted planning workflow. No new animation or scored campaign was executed in this planning pass.
