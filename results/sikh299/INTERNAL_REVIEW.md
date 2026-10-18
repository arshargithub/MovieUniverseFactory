# 299 internal review log — incomplete, no delivery admission

## Controls01 /02

01 failed at Blender Metal enumeration inside the OS sandbox, before scene work.02 ran with explicit local GPU access and failed an arm-reach assertion when the larger requested body yaw was incorrectly mapped1:1 into steering. Both retained. Corrective change: bound steering independently of vehicle yaw, preserve actual limb lengths. This is interface reconciliation, not longer arms or a creative downgrade.

## Controls03 — rejected

Compared actual frames0120/0133/0148/0215 with297 and the known quality floor. Lean and final53.3-degree body heading are present. The flame has several tongues but still reads too sharply outlined/paper-like. Root independently identified the same concern. More importantly,0148 and0215 show the tire visibly above its shadow. Axle-height-minus-radius measurements falsely reported errors below0.000001m. Those values are a valid measurement of the wrong proxy, not a contact PASS.

04 changes the representation of the test: actual tire mesh extrema, including width, tread, steering and wheel rotation, are raycast against actual road height. Root pitch and elevation solve both tire supports; marks and debris originate at that actual contact rather than an axle projection. This control must still pass images; its numerical success will not itself admit it.

Fire04 instead replaces opaque surfaces with an emissive tapered turbulent volume. Controls03 incurred25–35s/frame around the stop versus297 movie average4.08s/frame. This is an observed representation regression, not a reason to lower resolution or samples. No general speedup is claimed.

## Controls04 / contact discrimination — not admitted

Actual mesh contact gaps are approximately0.0008m, but contact-side and actual-camera0148 still visually float. Root independently rejected this. Inspect02/03 establish that road transform is identity, tire/road have no modifiers, every tire vertex is used by rendered polygons, and reopened evaluated minima agree with the build. Inspect04's orthographic camera looked partly through foreground ground and is an unusable control. Inspect05 fixes that camera and places a small green marker at measured contact: the tire meets that marker/road, while broad multi-light shadows create a detached reading. This is a rendering/contact-readability failure, not permission to call numeric contact sufficient.

Inspect06 initially changed an unused292 material; no claim follows. Inspect07 applies local AO to the actual297 road material and only slightly improves contact. Controls05 therefore explicitly uses a very localized, feathered ground-projected occlusion accent bound to measured contacts, hidden if the tire is more than0.012m airborne. It is authored stylized shading, not physical shadow simulation. It must not read as a moving black disc. The same reassessment corrects skid material inheritance from unused292 to the actual297 ground shader. No bike-lowering patch is used.

Controls05 raises volume spatial sampling (tile4/96 samples) to give the flame more structure. The moon diagnostic04 looked from the opposite hemisphere to the real camera;05 corrects that diagnostic direction without changing the underlying map merely to fit the wrong view. Actual-camera lunar evidence remains authoritative.

No final motion review, audio hearing, same-film production pass or character admission has occurred. Known principal proxy is preserved and remains explicitly unqualified. Final planned deliverable is complete22s Sikh + unchanged-picture Pashtun join; only a completed internal scoped review may admit it.
# Additional adjacent finding — greeting eyeline

Movie01 stopped at roughly frame170 after math/source review found that moving final bike yaw from23 to53 degrees left the inherited local head yaw aimed about39 degrees beyond the leader. Root agreed this is an in-scope regression, not a Director choice. Partial frames and the terminated process receipt are retained. Controls07 must prove leader attention and neighboring uncover/greeting/support before the replacement full render. This is an evidence-ordering failure: the stop proof should have included downstream attention before the full render started.

