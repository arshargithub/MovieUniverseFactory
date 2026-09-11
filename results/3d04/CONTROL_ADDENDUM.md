# 3D-04 Blender failure-control addendum

Decision: **PASS.**

The earlier fast controls in `validators/performance.py` mutate measured JSON and remain useful unit tests for gate logic. This addendum closes the separate integration question: each corruption below is an actual disposable Blender action saved to a `.blend`, reopened in a fresh Blender process, and measured by the same `performance_evidence` worker used for the accepted run. Each variant was then rebuilt independently and remeasured to verify deterministic replay.

- Addendum run: `blender-controls-v1-20260911T032852Z-b0545a82`
- Source commit/tree: `ade45ca1103b2bdbcd69f390e70cf9bd54500a61` / `b5f41233ad5d86dd4712448f816acb3902479b55`
- Artifacts: **160**, all inventoried
- Provider calls / known API cost: **0 / $0.00**
- Accepted run modified: **no**; its manifest SHA-256 remained `bd726af2744bc01968d24ef5b8fe66cde641b516de7cc827e15bbf705edbd6a4`

| Disposable scene control | Required detected failures | Result | Native scene SHA-256 |
|---|---|---|---|
| `no_op` | `meaningful.chest_lean`, `meaningful.core_max_vertex`, `meaningful.core_rms_vertex`, `meaningful.pelvis` | PASS | `32c121e90e4eed66f2619e6cc377f1591f0ae1e6f984d03e268761edc348a67d` |
| `edit_every_cycle` | `preservation.outside_max`, `preservation.outside_rms` | PASS | `f893afdfb7ed97d419c6730ce7309a324041de6ce581e68e48dfa74c4ee17672` |
| `boundary_leakage` | `boundary.40.value`, `boundary.40.velocity_max`, `boundary.40.velocity_rms` | PASS | `832a26a6c75a34445ee5172377640fb5f51e6e878a7412155f52efb8d714b012` |
| `support_foot_slide` | `contacts.induced_slide`, `contacts.slide_regression` | PASS | `5566e60a2a72314c27a9e6007ffc14ce1fe20cae32d19d6097d2589eaad7a647` |

`no_op` replaces the candidate with the measured repeating baseline and fails every minimum-change gate. `edit_every_cycle` applies the body treatment across the full 96-frame action and fails exact outside-range preservation. `boundary_leakage` inserts a nonzero frame-40 edit with a nonzero central slope and fails the boundary value and velocity gates. `support_foot_slide` adds a transverse action-level location ramp during support and fails both candidate-induced slide and slide-regression gates.

Some intentionally severe controls trigger additional gates. That is expected and retained in the individual validation records; qualification requires every designated gate to fail, not exclusivity.

This addendum does not broaden 3D-04. The accepted result remains one structured edit on one rig and interval. Contact is compared with the admitted in-place treadmill trajectory, so this does not establish a stationary planted foot during forward locomotion.
