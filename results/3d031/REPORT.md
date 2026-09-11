# 3D-03.1 closure report

Decision: **GREEN for the bounded 3D-03.1 claim.**

The production importer now captures source animation before touching the target and solves each bone against its current-frame parent pose. This removes the stale-parent corruption that caused the rejected opening contortions. Quaternion signs are canonicalized, source frame rates are recorded, and a static placement offset preserves source vertical motion.

The official Kenney archive contains no animation beyond `idle.fbx`, `run.fbx`, and `jump.fbx`. The admitted jump evaluates as a near-static crouched pose, so it cannot support a complete source-jump claim. 3D-03.1 therefore keeps idle and run as corrected transfers and labels jump separately as deterministic authored motion. The authored action blends the admitted idle and crouched poses with a frozen 0.34 m vertical trajectory; it does not claim faithful transfer of a complete jump.

## Authoritative evidence

- Source commit: `6afb4d8b382437bb4629f9168e4d40261b441bd9`
- Source tree: `b47304d4ce56d4f8e41c49ef3feac1a8c7654df6`
- Qualification run: `character-v2-20260911T012644Z-2d7d8605`
- Source native SHA-256: `bbf05848c30e531ca31fc4632210b8344f6f35166db9c26abe4adfa6150e2488`
- Temporal run: `motion-v2-20260911T012703Z-335b367f`
- Offline replay: `runs/3d031-replay/replay-01`
- Provider calls and known API cost: **0 / $0**

Both qualification and temporal dispatches started from a clean worktree bound to the source commit above. Save/reopen, structured skin and idle-to-run revision, protected-state comparison, and provider-free replay passed. Replay produced an exact semantic snapshot with zero differences.

## Every-frame results

| Clip | Role | FPS | Peak RMS step | Peak vertex step | Endpoint RMS | Result |
|---|---|---:|---:|---:|---:|---|
| Idle | corrected source transfer | 30 | 0.002255 m | 0.004689 m | 0 | PASS |
| Run | corrected source transfer | 24 | 0.153485 m | 0.365414 m | 0 | PASS |
| Jump | separately authored motion | 24 | 0.114098 m | 0.189570 m | 0 | PASS |

All 63 frames passed finite geometry, topology, bounds, floor penetration, height, complete limb-field, continuity, and timestamp checks. Run showed actual right-to-left-to-right support rather than merely counting foot contacts. Jump begins and ends in contact and has seven airborne frames, with a 0.34 m peak clearance.

The Director accepted all complete clips. Run received **4/5** because its limited visible vertical body movement makes it read somewhat like fast walking. Idle and the separately authored jump were judged decent. This is retained as a performance-quality limitation rather than hidden by the machine pass.

## Claim boundary

GREEN establishes the corrected same-skeleton transfer for this character's idle and run actions, plus this exact bounded authored-jump recipe, persistence, structured revision, and offline replay. It does not establish faithful transfer of a complete source jump, arbitrary animation import or retargeting, general motion authoring, horizontal root motion, facial performance, or production character quality.

The next animation experiment should use this accepted character and focus on timeline-local performance editing, stronger run dynamics, foot sliding, contacts, motion arcs, and preservation outside an edited frame range.
