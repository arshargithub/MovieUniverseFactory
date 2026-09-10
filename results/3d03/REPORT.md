# 3D-03 qualification report

**Decision: GREEN**

The frozen persistent-character experiment passed verified asset ingestion, canonical rig construction, deterministic same-skeleton animation baking, per-frame grounding, native save/reopen, targeted wardrobe and action revision, Director review, and provider-free replay.

- Authoritative run: `character-v1-20260910T201716Z-dd48f85a`
- Source commit: `c31859272bce7bb083bf0a9ead002368606111ea`
- Source tree: `87416f2adeed7419f3bae66408363c55673d9d49`
- Evidence tag: `3d-03-v1-green`
- Director score: **4.7/5**; no hands-on edits
- Provider calls and API cost: **0 / $0**
- Replay differences: **0**
- Baseline/revision save-reopen differences: **0 / 0**
- Character topology: **804 vertices / 826 polygons**
- Rig coverage: **58 stable bones / 32 weighted bones**
- Qualified clips and skins: **idle, run, jump / cyborg, skater**

The accepted implementation evaluates each verified animation source, transfers rotation-only motion to the canonical weighted bones, preserves canonical proportions and joint connections, removes lateral root motion, and adds bounded vertical grounding. The revision changes only the active skin from cyborg to skater and the active action from idle to run.

The Director accepted extremely slight residual deformation at the forward left foot in revised Shot B and forward left hand in revised Shot C as minor low-poly finish limitations. Two earlier authoritative attempts remain preserved as rejected evidence: the first exposed raw-curve/rest-pose incompatibility, and the second exposed extremity stretching and inadequate grounding.

GREEN qualifies this frozen Kenney skeleton, its three verified clips, two skins, deterministic same-skeleton rotation transfer, and the two supported structured revisions. It does not qualify arbitrary retargeting, rig generation, facial performance, lip sync, cloth or hair simulation, motion-capture cleanup, nonlinear animation editing, or production character quality.
