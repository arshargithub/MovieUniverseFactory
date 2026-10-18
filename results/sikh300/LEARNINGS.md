# Sikh300 applied findings — working record

## Rig ownership before local pose corrections

The inherited horse had a structurally wrong neutral forelimb, not merely a poor rear pose. Inspection found zero armature drivers: construction257 used `animation_data_clear()`, which removed Rigify property drivers along with the action. Setting the visible IK/FK property alone therefore had no effect (controls01 negative). Explicitly routing existing ORG fore-chain constraints to the FK targets restored the neutral forelimbs (controls02). The rear still needed coordinated articulation; neutral success alone did not qualify it.

Carry forward: inspect actions, drivers, constraints, custom properties and evaluation ownership before changing IK targets or adding offsets. To replace animation, clear the action deliberately rather than deleting all animation data unless driver removal is intended. Require neutral, rise, apex and landing controls plus adjacent rider/bridle/spear checks. This300 local bypass is a scoped representation, not a generic repaired Rigify asset.

Independent review also triggered a hind-hoof diagnostic. Evaluated toe mesh showed approximately5cm heel penetration at the rear apex, while neutral was supported. The inherited handler keyed quaternion channels on XYZ-mode foot controllers; translating a target did not preserve its full ground frame.300 binds hind feet explicitly in quaternion mode and re-keys the neutral world target through the rear. Check visible/evaluated hoof surfaces, not just target locations or broad side shadows.

## Rendered support and terrain share one surface

A new road/ditch cross-section invalidates old tire, crowd-foot, scuff and pebble heights. Preserve a single rendered road owner and rebuild dependent support rather than laying a ditch alongside an unrelated flat track. Numeric zero-gap remains separate from visual groundedness. Existing299 localized stylized contact occlusion is not a claim of physical shadow simulation.

Controls05 exposed a necessary adjacent dependency: a crowd foot stepping into the new swale cannot stay planted while its pelvis follows only the higher field surface. The exact-length solver rejected that target.300 resolves pelvis support using both foot surfaces before solving knees; it does not lengthen the legs. This is why terrain changes require complete moving-character support checks, not just correct crop roots.

Full-output review found another dependency missed by that list: the leader mound included a large flat rectangular apron. The new lowered shoulder exposed it as a straight material patch. Disabling shadows, headlamp and named skid overlays did not change the boundary; camera rays on opposite sides hit different objects, and uniform clay/emission made the rectangle unmistakable. Object names and a single new road material had not established a single **visible** surface owner. Carry forward: survey all terrain overlaps, ray-test suspicious pixels, check winding, and include the entire camera range. A new continuous road does not automatically integrate old mound bases. Keep known artificial seams internal; a development label is not a waiver of the requested correction.

## Dense geometry is not crop density

Individual ear topology cannot make a field dense when plant spacing is sparse. Inspect shot-visible canopy/clumps before scaling geometry blindly. Near-camera stalks, middle-distance masses and far-field silhouette may require distinct representations. This is an explicit control question, not an asserted300 success.

Controls06 confirmed the sparse-field failure.07 replaces isolated high-topology ears with reusable seven-tiller clumps and denser near-road instancing: continuous cultivated canopy at actual shot size with approximately unchanged3s control render cost. Large diagnostic crops still reveal simplified leaves; do not confuse this shot-scale treatment with a hero botanical asset.

## Efficient construction without changing quality

Controls03 was stopped after profiling showed expensive repeated dependency evaluation during contact authoring; unrelated animated crop geometry is hidden from viewport evaluation during those solves and restored before save/render. Controls04 profiling then isolated per-coordinate shape-key RNA updates, which tag the full key repeatedly. Replacing them with an equivalent bulk `foreach_set` update removes that bottleneck without reducing rendered density. Preserve interrupted receipts; do not count wall occupancy as additional assistant labor or an arbitrary timeout failure.

## Donor materials are interfaces too

Added wear must preserve existing color and normal inputs and shared material assignments. New procedural noise alone is not an artistic finish; compare paint, rubber, leather and metal under the actual night lighting. Keep the machine silhouette and readable highlights ahead of imperceptible microtexture.

## Time and review language

Inherited motion functions use26 source seconds mapped onto22 output seconds. Beat briefs must name that conversion explicitly. Continuous frame chronology, pixel replay, encoded playback validity and real-time perceptual watching/listening are different evidence. Do not promote one into another.

## Carry-forward trigger map

| When next encountered | Required action |300 evidence / regression |
|---|---|---|
| Import or replace animation on a driver-based rig | Inventory driver/constraint owners before clearing anything; prove neutral structure |01 failed property-only switch,02 corrected fore-chain ownership; final reopen asserts explicit FK constraint influences |
| Key a pose control or preserve ground contact | Match rotation mode to keyed channels; verify full evaluated hoof/hand surface, not just target translation |03 heel penetration versus04 stable hind toe surface; final reopen asserts both hind feet QUATERNION |
| Replace terrain beneath an animated cast | Rebind wheels, planted feet, pelvis, marks, particles and crop roots; exact-length constraints must not be bypassed |05 unreachable crowd leg detected;06 pelvis support correction and new continuous road |
| Integrate a new terrain surface with old banks/props | Inspect hidden flat aprons and mesh winding; discriminate visible owner with camera rays, clay/emission and lighting controls |300-L02, ground-01 camera rays hit road on one side and old mound apron on the other; repair must preserve plateau/support |
| Increase environment fidelity | Evaluate spatial density and screen silhouette before per-object topology; prefer reusable clumps/instances where suitable |06 sparse detailed wheat rejected;07 dense instanced canopy admitted for this shot scale |
| Slow Blender authoring | Profile actual stage; separate irrelevant evaluation and use bulk data access before lowering quality |03 dependency cost and04 shape-key per-coordinate update cost;05 bulk path progressed |
| Add donor material wear | Preserve existing normal/color links and shared slots; test each material class in shot light |300 bike material handler and actual opening/stopped frames |
| Change action timing | State source/output clock, retime physical effects without silently remapping selected music |300 two lock intervals and bit-exact selected music check |

Root owns reconciliation into the shared learning catalog. This local map is a concrete manual application contract, not a claim that all these rules are already automatically retrieved or visually tested by the existing pilot.
