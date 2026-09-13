# Demonstrator 01 — existing-asset repair plan

Historical plan, 2026-09-12. Execution was subsequently authorized by the Director’s “go for it”; see `results/demonstrator-01/stage-a/FREE_REPAIR.md` for outcomes. Original planning text follows unchanged: Director declined the paid package and requested repairs/improvements using the existing free assets. This supersedes the acquisition recommendation, not the historical evidence. No implementation, asset search, purchase, API request or render is authorized by this planning document alone. The existing charter still controls Stage A and production gates.

## Objective and preserved work

Produce one convincing 2.5-second mounted gallop with the existing fdoss001 horse/tack and crownjoshua knight. Keep the working hierarchy normalization, one owner for forward travel, authored horse gallop, script-disabled execution, actor identities and fitted camera. Preserve all failed previews. The requested method now stays with these assets; no replacement acquisition or custom horse rig.

Inputs: hash-admitted `.runtime/assets/demonstrator-01/horse.blend` and `Knight_0.blend`; implementation in `src/movie_factory/adapters/blender/demo_riding.py`; latest evidence in `runs/demonstrator-01/motion-v2`. These are development fixtures, not accepted production assets. Work in fresh run directories; never save over source downloads. Hash current inputs and implementation at execution start.

## Diagnosis before repair

| Issue | Established evidence | Unproven cause / discriminating check | Preferred bounded repair |
|---|---|---|---|
| Tail grows/whips unnaturally | Progressive instability in rendered frames | Inspect particle/hair systems, cache, modifiers and evaluated strands. Compare an isolated source cycle against assembled cycle, sequential and isolated samples. Determine whether deformation is simulation-dependent or comes from rig/transform evaluation. | If dynamics are responsible, compare a clean correctly initialized cache with dynamics disabled while preserving the visible authored tail. Prefer a deterministic tail with modest authored sway to unstable simulation. Do not remove the tail or hide it with framing. |
| Saddle/tack does not follow convincingly | SurfaceDeform reports no valid target mesh; dependency cycles remain | Identify exact target and cycle paths, bind state, topology and modifier order. Current code aligns subdivision only after pose sampling, so inspect whether measurements and rendering use different evaluated geometry. | Establish one evaluation configuration before binding, measurements and rendering. Restore valid source dependencies first. Rebind only in an identified compatible bind/rest state on a disposable copy. If unsuitable, use a documented rigid saddle/pad attachment to an existing back control, preserving its world transform; retain horse rig and declare this kinematic fixture adaptation. |
| Stiff rider | Code follows bounding-box top, fixed target offsets, sinusoidal chest lean; latest clip reads rigid | Measure saddle translation/orientation over a stride. Test control/DEF/skin response together. A tiny pelvis-head error cannot prove a seated body. | Replace bounding-box top with an explicit stable seat coordinate frame. Derive pelvis motion from seat position and orientation, then coordinated hip/knee/spine response from actual gait phases. |
| Hands miss reins; feet/stirrups uncertain | Visible hand/rein gap; endpoint-target error around 147 mm in pose probe | Locate actual hand grip, rein endpoints and stirrup surfaces. Solve reachability with admitted limb lengths and joint bends. | Use existing rig controls for reachable arms/legs, orient wrists and apply a modest existing-finger-control grasp. Keep tack placement plausible instead of stretching limbs to arbitrary targets. |
| Speed/contact uncertain | 3.45 m/s is provisional; total displacement now correct | Sample evaluated hoof sole patches during stance, independently of hoof control heads; fit forward speed against backward foot travel at source FPS. | Apply one calibrated speed or coordinated cycle time scale. Preserve airborne phases and avoid per-frame whole-character grounding. |

These are diagnostic hypotheses and planned alternatives, not promised fixes. Do not disable unknown modifiers wholesale or repeatedly rebind until warnings disappear. A warning-free run must also preserve the intended geometry and motion.

## Coordinated riding design

Intention: a purposeful, balanced courier absorbing the horse's gallop. Authored performance using an artist-authored horse cycle; no mocap transfer or physical riding simulation claim. Reference is the supplied cycle and observed preview, not an unreviewed external video. Annotate actual support/flight events before assigning phase timing; do not assume evenly spaced phases.

| Gait phase | Pelvis, spine and gaze | Legs | Arms, hands and reins |
|---|---|---|---|
| Load / landing | Seat receives horse heave/pitch; hips and spine flex to absorb motion. Head follows smoothly without rigid cancellation of all torso movement. | Knees/ankles accommodate seat motion while feet remain near stirrups. | Elbows flex; shoulders remain relaxed; wrist stays aligned with grip. |
| Push-off | Pelvis follows saddle; torso inclines modestly with effort. | Maintain knee bend and plausible barrel clearance. | Arms accommodate changing bit/hand separation, not a locked world-space hand target. |
| Suspension | Continuous seat relationship; modest delayed upper-body response, not an arbitrary extra vertical bounce. | Preserve foot/stirrup relationship without forcing contact with the ground. | Grip stays closed; rein slack changes smoothly. |
| Recovery / next contact | Return continuously to repeated phase; no snap at source-cycle seam. | No knee flips or hyperextension. | No wrist flips or rein teleportation. |

The horse owns the bit attachment; the rider owns the hand grip; a rein spans those endpoints with controlled slack. Do not create a feedback cycle by letting reins drive both hand and horse. Existing stirrup and seat anchors belong to the horse/tack frame; limb controls accommodate them. Use parent-first evaluation and key only intended user controls. Full seat orientation matters: do not use a world-space bounding box as a riding frame.

Deliberate stillness: gaze stays down the route during this diagnostic. The tower signal/head turn belongs to later shot assembly. No decorative head motion, finger acting, cloth simulation or cinematic dust is required here.

## One bounded execution pass

Proposed ceiling: **60 active engineering minutes, 15 minutes local compute/rendering, at most two new paid work items totaling $2 committed exposure including retries** within the existing $100 ledger. No live call is mandatory. Use existing Astra diagnosis first; route a narrowly specified implementation proposal to Sol Medium only when the repair contract is concrete. Escalate a demonstrated transform/dependency problem to Astra High within the same $2 allowance; no unbounded subscription fallback. These are proposed execution ceilings, not time already spent or a guarantee of repair.

1. **0–15 active minutes: dependency and source-motion audit.** Inventory tail/caches, tack binds, rig owners and actual foot/hand anchors. Use numeric probes and cheap viewport evidence. Stop at the earliest corrupted stage. Maximum three variants for a hypothesis.
2. **15–30: stabilize horse/tack and calibrate travel.** Choose the smallest proved tail/tack repair. Confirm identical evaluation settings in inspection and render. If the foundational geometry remains broken, stop before rider polish.
3. **30–45: author coordinated rider/contact.** Use a four-phase pose board and constraint check above. Solve seat, knees, feet, elbows, wrists and grip as a whole. Inspect three phase poses before baking.
4. **45–60: full cheap clip, regression checks and one review packet.** Prefer workbench/viewport motion first. Once valid, render one lateral 60-frame clip plus an inexpensive three-quarter/contact view. Do not render separate near-identical campaigns for every joint adjustment.

Reassess at 20 active minutes on one unresolved diagnosis and stop at 60 overall. If blocked, deliver the precise failing dependency and evidence; do not silently extend the pass, purchase assets, change the film brief or start a third approach. At current settings a lateral clip measured 3m31s including worker setup; two such views suggest roughly seven minutes before rerender allowance. The proposed 15-minute compute cap must be revised before dispatch if settings or measured complexity make it implausible. Retain >=5 GB free space; target <=1 GB new artifacts and one native scene, not repeated exports.

## Validation and review

Separate screening measurements from creative acceptance. No new GREEN threshold is frozen by this plan. During the initial audit, record hoof/stirrup/hand dimensions, source deformation and stance intervals, then freeze explicit tolerances before the repaired candidate is evaluated. Do not raise them afterward to accommodate a failed run.

- Compare source and assembled horse motion in their own local coordinates; preserve horse mesh, rig and gallop action unless a narrowly documented fixture repair requires a change. Verify single path ownership.
- Measure evaluated hoof sole clearance/penetration and horizontal slip during stance; preserve flight. Use small surface patches, not bone heads or a single bounding-box minimum.
- Measure seat-frame position/orientation, actual grip/rein and foot/stirrup gaps, unwanted body/tack intersections, limb lengths and representative skin deformation. Intentional grip/seat contact is allowed and explicitly identified.
- Sample every frame plus fractional frames near hoof contact and the stride seam. Check NaNs, sudden bounds/strand-length growth, orientation flips, and positional/velocity discontinuities. Express rates in physical seconds.
- Compare posed state to baked state and save/reopen state. Repeat selected frames with the same simulation/cache policy; forward/isolated evaluation differences must be reported, not hidden by one favorable render order.
- Reuse prior negative-control lessons: a disposable doubled-travel constraint must fail travel measurement; an offset rein endpoint must fail contact measurement; a rigid rider must fail the visual coordination criterion even if technically finite. Use actual scene variants through the same inspector, not edited result JSON. Keep these small and out of the accepted scene.

Director receives synchronized old/new full playback with the same cadence and comparable views. Improvement means a stable visible tail; saddle/pelvis connected to back motion; visible knee/elbow/spine absorption; credible hands/reins and feet/stirrups; and no conspicuous sliding, intersections or snap. Show any deterministic/kinematic simplification explicitly. Record review duration and actual observations; do not invent scores. If these conditions hold, update the measured film forecast and seek Stage A scope agreement before four-shot production.

## Look improvements after motion admission

Restore usable source material distinctions for coat, leather, metal and hair instead of uniform brown/dark overrides. Check body proportions, tail silhouette and readable lighting on one representative frame. Then develop road/mountain depth, watchtower, dust, shot variety and sound in the complete rough cut. Do not use finishing to conceal failed motion.

## Learning delta and deliverables

| Prior failure | Change in this plan |
|---|---|
| Source and generated path combined | One explicit travel owner with a native failure control |
| Accurate control anchor, wrong evaluated body | Stable oriented seat frame plus mesh/contact measurements |
| Three-second pose looked good, full motion did not | Complete inexpensive motion before expensive renders |
| Reactive isolated-joint edits | Phase-based coordinated movement and reachability before implementation |
| Free replacement search led to an unapproved purchase | Existing fixtures only; explicit modest adaptations and a repair stop rule |

Deliver: diagnosis/repair log, updated motion brief, one hash-bound candidate scene, complete comparison video(s), compact machine checks, source/configuration binding, timings and API ledger references. Preserve old failed evidence. No harness rewrite, new character, paid asset, cloud rendering, public upload or modification of closed campaigns.

Planning attribution: supervising assistant, based on repository code and retained evidence; no new paid model call or external human-motion reference used for this plan. Ready for a bounded diagnostic assignment, not scored qualification or production.
