# 3D-05 closure campaign — coordinated stationary pickup and timing revision

Status: technical preflight passed; numerical contract prepared for the next scored freeze. This addendum supersedes the original specification's fixed-hand orientation, old held position, nearest-normal penetration method and broad grip-sphere exclusion **only for the new closure campaign**. Original campaign files and all historical decisions remain unchanged. Frozen JSON in this directory will be authoritative for exact inputs and numerical gates.

## Scope and motion plan

Qualify one stationary admitted character, one explicitly fitted sword variant, one scripted enclosing pickup and one four-frame timing advance. The baseline already contains coordinated forearm/wrist motion and head attention. The scored candidate changes timing only; it is not a comparison against the earlier rigid-arm performance. Keep topology, weights, rig, source actions, lower body, lighting and world protected. No physical grasp simulation, general retargeting, arbitrary-prop fit, release/drop, locomotion, autonomous direction or combat is qualified.

Use the accepted 3D-03.1 character native SHA-256 `bbf05848c30e531ca31fc4632210b8344f6f35166db9c26abe4adfa6150e2488` and source sword SHA-256 `8e69eb27977f8c84a9b7cd423cd5830eddcf0d07ac1d7fed1969931387015b28`. The sword keeps the documented fixture-specific handle/guard/blade fitting; the imported source is unchanged.

Preparation turns the head toward the work. Reach uses the preserved two-segment arm lengths, a smaller inward clearance bow, and a 6 cm pregrasp standoff. The open hand first arrives in the admitted acquisition orientation, then aligns with the outward-tilted handle over source frames 24–32. A temporary 2 cm standoff pulse during this alignment clears the guard: quintic entry over 24–26, exit over 28–32, zero value and slope at the interval ends. Fingers then close using the admitted controls. Lift retains 25° hand rotation and coordinated elbow/forearm participation, plus a small 1.5 cm take-up arc; the held grip moves forward/lower to improve head clearance. These are explicitly authored fixture motions, not reference transfer or inferred physics.

Contact frame tilt is -20° and held grip is `[-0.36,-0.39,1.20]` world metres. The final sword orientation follows the hand through a full rigid hand-to-sword transform, rather than remaining globally blade-up. Surface geometry and visual review independently qualify that relationship.

## Timing, ownership and preservation

Keep the original 96-frame, 24 fps timeline and supported → reaching → grasped → lifting → held states. Baseline transitions are 16/40/48/68; candidate transitions are 16/36/44/64. The original candidate time warp `t + 4E(t)` is unchanged: quintic rise over 28–36, unity over 36–68, quintic fall over 68–76, zero outside `[28,76]`. Value and derivative vanish at both edit boundaries.

The support and hand each have an explicit evaluated CHILD_OF relationship. At every frozen integer/fractional sample, exactly one valid, unmuted constraint has influence 1 (tolerance 1e-8), with the correct target and hand bone when applicable. Schedule labels alone cannot satisfy this gate. At grasp the support turns off as the hand turns on, preserving evaluated world transforms. Dual- and missing-influence controls must fail even where intended schedule labels remain correct.

Save/reopen before grasp, just after grasp and during hold for each timing variant. Compare actual evaluated constraint inventories, object identities and transforms. Rebuild independently from original inputs, and require identical semantic snapshots and metric digests. Metadata/protected-state equality is exact; numerical geometry thresholds are separately specified in campaign JSON. Outside `[28,76]`, maximum/RMS character displacement is at most 1e-6/2.5e-7 m, sword translation at most 1e-6 m and orientation at most 1e-4°. Boundary RMS-character/sword velocity differences are at most 0.002/0.005 m/s. Attachment second differences are at most 0.002 m and 0.5°.

Sampling retains every half-frame, dense 0.125-frame windows over 16–50 and 62–78, and off-grid probes ±0.061, ±0.01 and ±0.001 around the contract boundaries/transitions. This is finite temporal validation, not a proof at every real-valued instant.

## Independent contact, deformation and clearance

Original gates remain unchanged: digit contact ≤5 mm, angular enclosure ≥170°, sampled hand/sword and hand/support penetration ≤4 mm, wrist/forearm regression limits, 0.35–1.50 elbow-edge ratios, and the coordinated motion/attention gains in `campaign.json`. Both variants must pass, across the complete clip, including the earlier reach. The 26-edge screen remains a limited skin-regression metric; it does not establish arbitrary skin quality.

The original render sword has open edges. Signed nearest-normal distance produced a verified exterior-point false positive. Each explicit handle/guard/blade region now has a closed convex collision proxy whose planes enclose that rendered section's vertices. The render mesh remains unchanged. Actual render-surface hits still determine contact distance and angular enclosure. Closed proxies determine hand penetration and conservative protected-surface checks. This is an admitted, conservative fixture representation, not arbitrary open-mesh collision support.

For both variants at every frozen sample:

- Handle-to-nonhand-body conservative clearance ≥0.010 m.
- Guard/blade-to-nonhand-body conservative clearance ≥0.040 m.
- Every sword region-to-head conservative clearance ≥0.120 m, separately from nonintersection.
- Zero forbidden triangle intersections and contained vertices. Only hand–handle contact is intentional. Guard/blade–hand intersection is forbidden.
- Complete triangle covers subdivide to ≤0.03 m edges; nearest-surface distance minus each cover radius bounds clearance conservatively. BVH overlap is a broad phase followed by triangle intersection tests, including coplanar cases.
- Proxy closure/enclosure is checked during construction. Character containment retains the admitted fixture's closure assumption; intersections and conservative positive clearance supply additional independent evidence.

Retain the old vertex clearance metric as historical comparison, but it cannot replace these new gates. Comfortable visual clearance remains a Director judgment even if 12 cm is achieved.

## Controls and Director review

All 18 frozen controls are actual disposable Blender scenes measured through the normal inspector: the original 10 contact/anatomy/timing controls, five coordinated-motion controls, dual ownership, missing ownership, and a blade-face crossing whose corners lie outside the head while its interior crosses it. Each must trigger its designated error absent from the positive scene. JSON-only mutation tests complement these controls but cannot substitute for them.

Before scoring, inspect complete inexpensive playback, freeze source/configuration/toolchain/render-profile bindings and zero provider budget, and retain that preflight evidence. Then render a new anonymous synchronized A/B comparison with complete primary, side and rear views. Do not reveal assignments before review.

Retain the existing Director gate: score both clips in 0.5 increments for interaction readability, grasp/contact believability, transition smoothness and hold/clearance. Candidate scores must each be ≥4, readability must improve by ≥0.5, other dimensions must not regress, candidate preference is required and no major defect is allowed. Record specific defects and review duration in seconds. These thresholds are not retrospectively inferred from the previous development pass. A legitimate review can fail to prefer the timing revision; report that outcome honestly.

GREEN requires machine gates, all control sensitivities, replay/persistence, exact source binding and this fresh Director gate. Passing machines with missing Director review is YELLOW. A technical failure is RED for the new run; previous YELLOW and development acceptance remain historical facts.

## Packaging and economics

Package source/tests, frozen inputs, native scenes, six state checkpoints and reopen evidence, deterministic replay, actual controls, all playback frames, blinded player and separate key, Director record, original player provenance, checksums, report and reproduction guide. Retain rejected/development attempts and their history separately. Evidence tags must bind final evidence commits, not imply closure from an implementation tag.

Provider budget is zero calls / $0. Record local run elapsed time and fresh Director review time. Historical human time and interactive engineering-model cost were not measured, so total production economics are incomplete. No paid evaluation work is moved outside the ledger to improve reported economics.
