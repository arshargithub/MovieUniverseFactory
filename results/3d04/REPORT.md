# 3D-04 closure report

Decision: **GREEN for the bounded 3D-04 claim.**

Movie Factory improved one authorized interval of the accepted 3D-03.1 run while preserving all motion outside it. The candidate adds a maximum 6.0001° forward chest lean and 0.035000 m pelvis correction during frames 40–70. A quintic envelope returns both value and velocity change to zero at the boundaries, and deterministic leg compensation retains the baseline support-foot trajectories.

## Authoritative evidence

- Scored run: `performance-v1-20260911T025746Z-51f59d9c`
- Execution source commit: `1d5409d0c86be6da952705a1397dd610fc9c9375`
- Execution source tree: `8782f4d5233cc7add06122d7fec0d3299df55b8d`
- Evidence tag: `3d-04-v1-green-evidence`
- Blender: 5.2.1 LTS, build `9e2066aef7ef`
- Baseline native SHA-256: `bbf05848c30e531ca31fc4632210b8344f6f35166db9c26abe4adfa6150e2488`
- Candidate native SHA-256: `dcab7b53bfd119398ded701ce17d3d2d5853047a9e5c69dbd167b171cd8acf62`
- Provider calls / known API cost: **0 / $0.00**
- Accepted edited motion: **1.25 seconds**; API cost per accepted second: **$0.00**
- Total harness elapsed time: **70.071 s**; recorded Blender-process time: **67.986 s**
- Human review duration: **NOT_RECORDED**

The scored dispatch began from a clean worktree. Save/reopen and provider-free offline replay reproduced the semantic snapshot exactly and the evaluated geometry within the frozen tolerances. The original JSON-level controls verified the outer gate logic. A later [Blender failure-control addendum](CONTROL_ADDENDUM.md) built, saved, reopened, measured, and independently replayed four actual corrupted action variants through the production evidence worker; all four failed their intended gates without changing the accepted run.

## Numerical result

| Measurement | Observed | GREEN limit |
|---|---:|---:|
| Outside-range maximum vertex delta | 0.000000000 m | ≤ 0.000001 m |
| Boundary 40 RMS velocity change | 0.000422880 m/s | ≤ 0.002 m/s |
| Boundary 70 RMS velocity change | 0.000297478 m/s | ≤ 0.002 m/s |
| Candidate-induced support slide | 0.000001135 m | ≤ 0.005 m |
| Minimum candidate Z | -0.001108356 m | ≥ -0.015 m |
| Peak RMS frame step | 0.159429890 m | ≤ 0.18 m |
| Edited-core peak RMS delta | 0.052926979 m | ≥ 0.012 m |
| Edited-core peak vertex delta | 0.113034681 m | ≥ 0.025 m |

## Blinded Director result

The mapping was frozen before rendering and revealed only after the scores were submitted: **A was the candidate; B was the baseline**.

| Clip | Revealed role | Run readability | Foot contact | Transition smoothness |
|---|---|---:|---:|---:|
| A | candidate | 5.0 | 5.0 | 5.0 |
| B | baseline | 4.5 | 5.0 | 5.0 |

The Director preferred A for the frozen goal. A reads as moving from a brisk walk to a run at frame 40 through a slight forward lean, then returning to the original pace at frame 70. The Director also noted that either performance could be appropriate under a different creative goal. That qualification is retained: the result proves successful execution of this specified edit, not a universal preference for the candidate motion.

The initially generated playback page contained valid images but invalid JavaScript because the frame map was HTML-entity escaped. The original broken HTML remains preserved. Commit `6085048d71c9c03873af0a94fde5634f01f02787` repaired only the player; a before/after frame-set digest proves that all 192 blinded review images and the mapping remained unchanged.

## Claim boundary

GREEN establishes one trusted structured pelvis-and-chest performance revision on frames 40–70 for the admitted character and in-place run. It establishes exact protected-state and outside-interval preservation, smooth numerical boundaries, baseline-relative support-contact preservation, persistence, offline replay, negative-control sensitivity, and goal-specific blinded preference.

It does not establish arbitrary natural-language animation editing, general inverse kinematics, new motion generation, retargeting, horizontal locomotion, other rigs, character-prop interaction, facial performance, cloth/hair, or production-quality acting. Its foot-contact claim is relative to the admitted in-place treadmill trajectory; stationary world-space planting during forward locomotion remains untested. Known API cost is $0.00, while total production economics remain incomplete because human review time was not recorded.

Review the preserved synchronized playback at [the scored run](../../runs/3d04/performance-v1-20260911T025746Z-51f59d9c/review/index.html).
