# 3D-03 qualification report

**Decision: YELLOW — temporal animation claim not qualified**

The frozen persistent-character experiment passed verified asset ingestion, canonical rig construction, native save/reopen, targeted wardrobe and action revision, representative-still Director review, and provider-free replay. A later every-frame addendum invalidated the broader claim that idle, run, and jump motion were visually qualified.

- Authoritative run: `character-v1-20260910T201716Z-dd48f85a`
- Source commit: `c31859272bce7bb083bf0a9ead002368606111ea`
- Source tree: `87416f2adeed7419f3bae66408363c55673d9d49`
- Implementation tag: `3d-03-v1-green` (historical name; points to the clean source used for the original still-based qualification)
- Representative-still Director score: **4.7/5**; no hands-on edits
- Provider calls and API cost: **0 / $0**
- Replay differences: **0**
- Baseline/revision save-reopen differences: **0 / 0**
- Temporal addendum: `motion-v1-20260910T232321Z-f260e19a`, bound before dispatch to commit `4d86e3fac0e47b44c290e1923ac66997eae4e6e6`
- Character topology: **804 vertices / 826 polygons**
- Rig coverage: **58 stable bones / 32 weighted bones**
- Structurally persisted action datablocks and skins: **idle, run, jump / cyborg, skater**
- Full clips visually qualified: **none**

The sealed implementation evaluates each verified animation source, transfers rotation-only motion to the canonical weighted bones, preserves canonical proportions and joint connections, removes lateral root motion, and adds bounded vertical grounding. The revision changes only the active skin from cyborg to skater and the active action from idle to run. Those state and revision claims remain supported.

The Director accepted extremely slight residual deformation at the forward left foot in revised Shot B and forward left hand in revised Shot C as minor low-poly finish limitations in the three representative comparisons. That review did not cover complete playback.

The provider-free temporal addendum rendered and inspected all 63 frames. It found excessive frame-to-frame displacement and failed loop seams in every clip. Peak RMS vertex steps were 0.348 m for idle, 0.637 m for run, and 0.479 m for jump; the frozen ceiling is 0.18 m. Jump also had no airborne frame above the 0.06 m clearance gate. The worst transitions occur near the beginning of each clip, matching the visible contortions missed by the representative frames. Because deterministic validation failed, the optional paid visual evaluator was correctly not called; API cost remained $0.

The YELLOW result now qualifies persistent semantic identity for this frozen character, packed skins, action datablock persistence, protected-state preservation, targeted skin/action switching, exact reopen, and provider-free replay. It does not qualify the visual or temporal quality of idle, run, or jump. The next corrective experiment needs a source with a neutral bind/reference pose or a separately qualified retargeting method, followed by full-clip validation and Director playback review. Two earlier rejected qualification attempts and the later retargeting development attempts remain preserved as diagnostic evidence.
