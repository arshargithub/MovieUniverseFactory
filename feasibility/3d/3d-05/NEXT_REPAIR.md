# 3D-05 Director rejection and Astra repair handoff

Current thumb-up repair: see [ANATOMY_REPAIR.md](ANATOMY_REPAIR.md). Full Director acceptance remains pending.

Repair progress and the diagnosed causes are recorded in [GRASP_REPAIR.md](GRASP_REPAIR.md). The original handoff below is retained as history.

Recorded 2026-09-11. The user announced switching to **Astra for the next repair and run**. This records the requested engineering model; it does not verify or change app model settings or the experiment's API evaluator.

Latest rejected run: `runs/3d05/interaction-v1-20260911T143452Z-281f2ecf`.

Director feedback:

> the hand now forms a fist and touches the sword handle instead of grasping it. I would rank this as bad, if not worse then the previous run.

The run is RED / Director REJECTED. No numerical scores or review duration were supplied. Its native scenes, playback, and machine results remain preserved; the artifact manifest includes the rejection record.

The previous repair moved the hand to an offset from the handle centre and treated stable surface contact as adequate. The Director explicitly rejects that outcome: touching with a fist does not meet the original reach–grasp–lift–hold brief. Machine-valid anchor tracking does not establish believable grasp geometry. Do not narrow the acceptance question to mere surface contact or describe this repair as successful.

For the next Astra pass, inspect the actual hand mesh, available rig controls, handle dimensions, and evaluated contact geometry before choosing a correction. Establish a visible grasp around the handle with a natural wrist approach, and inspect side/rear evidence before launching another scored campaign. If the admitted hand or prop cannot support that pose within the current scope, document the limitation and the required fixture or scope change explicitly. Preserve the rejected attempts and freeze any justified contract changes before scoring. Full playback and explicit Director acceptance remain required.

Paid API calls remain limited to experiment evaluation under the campaign ledger. The current 3D-05 campaign has a zero-call budget.
