# The Courier — Stage A motion brief

Status: prepared for asset diagnostics; **not ready for production or scored freeze**. Source rig names, gait range, hoof trajectories and seated rider articulation must be measured. No custom horse rig is authorized.

## Intention and admitted inputs

Urgent purposeful travel, with a brief response to a distant signal. A lateral view must show credible galloping and rider weight transfer; the action must remain legible without dust or distant framing. Use the downloaded fdoss001 horse/tack/gaits and crownjoshua rigged knight as candidates only. Their hashes are recorded in the Stage A sources. Prior Kenney motion/rig is not reused as a realistic actor.

Reference is the artist-authored gait in the candidate file, to be inspected in full, plus explicitly authored rider coordination. No human/horse video motion extraction is claimed. A file labelled gallop is not accepted as convincing gallop until playback has been checked.

| Phase | Intention | Head/torso | Arms/hands | Contact |
|---|---|---|---|---|
| Repeating approach | Travel toward destination | Forward balanced seat; pelvis follows saddle, spine absorbs pitch/heave rather than rigidly attaching the whole torso | Elbows accommodate rein target; wrists follow hand-grip direction | Saddle supports pelvis; feet align with stirrups; hoof contacts measured from source gait |
| Suspension | Visible gallop flight and effort | Rider pelvis follows horse; torso response is phase-consistent | Avoid a locked arm span that forces shoulder distortion | No frame-by-frame grounding that destroys flight; hoof support only in source stance phases |
| Landing/load | Weight and forward momentum | Coordinated hip/knee/torso flexion within existing rig controls | Arms preserve reachable rein target | Forward speed fitted to stance-foot motion, not an arbitrary translation layered over a treadmill cycle |
| Signal response | Notice a conspicuous tower cue | Head turns first, slight upper-torso attention follows while riding continues | No unrelated wave or large gesture | Continue existing seat/foot constraints; no handover of ownership |
| Continue | Purposeful resolve | Return gaze along route | Stable reins | Same horse/rider and route; no discontinuous resets across shots |

## Constraint compatibility and initial test

Read actual rest axes, parent/control hierarchy, active NLA strips, IK targets and source FPS. Do not transplant the previous rotation-only humanoid bake contract to this rig. Preserve the horse's authored cycle and rig; isolate path/root travel on an external parent where compatible. Detect any existing source root motion before adding travel.

The saddle/grip/stirrup anchors belong to evaluated horse/tack geometry. The rider pelvis follows the saddle; torso, knees and elbows must retain enough freedom for a plausible seat and reachable contacts. Do not lock the whole rider as one rigid object and call it coordinated performance. Use existing rider IK/FK controls; a new rig would require a separate scope decision.

First bounded integration: 48–72 frames with at least two source strides if source cadence permits, on a flat, marked dry road. Use an overview and lateral/contact view. Measure source cycle duration and stance-foot backward travel, derive a candidate forward speed, and retain airborne portions. No dust in the diagnostic contact view; a thin dust treatment may be added only after contact is legible.

## Measurements to freeze after actual asset inspection

- Finite evaluated transforms/mesh bounds and complete full-clip playback.
- Hoof-floor signed clearance in identified stance phases; source-appropriate tolerances derived from hoof size and intended shot scale. No borrowed Kenney thresholds.
- Stance-foot world displacement/sliding, gait/root speed relationship and seam velocity under the selected physical FPS.
- Saddle–pelvis, stirrup–foot and rein–hand separation, reachable limb positions, plus representative evaluated triangle/edge deformation near hips/knees/elbows. Explicitly distinguish contact targets from actual surface intersection checks.
- Independent source-cycle and assembled-cycle comparison; save/reopen of the integrated preview and one repeat render under fixed settings.
- Visual plausibility is a separate gate. No camera angle may conceal an unresolved requirement.

No numerical GREEN thresholds are frozen yet because source dimensions and gait have not been measured. Stage A packet must state measured ranges, proposed tolerances and reasons. Production is blocked until a viable preview and Director agreement on the envelope. At most two integration approaches, not an open-ended rig repair.

## Selected first approach after asset inspection

Astra High design (one incomplete paid attempt retained, one completed retry) selects existing all-FK rider controls following evaluated saddle geometry. Horse gallop is 0–10 at24fps, source shape keys remain present despite an orphan-key load warning. Rider is normalized from4.2m to1.8m and turned to face horse -Y. Pelvis is targeted 10cm above saddle top; initial seated knees/ankles/hands are defined in the design memo and must respect actual limb lengths. Chest compliance +/-3degrees and counter head/arm motion are provisional authored cues, not transferred rider mocap.

Source hoof-control stance velocities span roughly1–16m/s. The median3.45m/s is only a provisional path speed, not a ground-contact qualification. Actual surface/contact and motion must be examined in the integration. First preview must clearly label unqualified contact if that check remains incomplete; no claim that a control head equals a sole. Design go/no-go suggestions include pelvis<=3cm from target and sole slip<=2cm per stance, but these cannot be claimed passed without measuring the actual observables.

Embedded rig_ui.py remains disabled. Mathematical rig responses must be checked without enabling scripts. Pose/skin response checks precede the full60-frame diagnostic render. No final scoring or production freeze is implied by making the preview.

## Current Director direction: existing assets

The Director declined purchasing a replacement and requested a repair plan for the existing horse and knight. [FREE_ASSET_REPAIR_PLAN.md](FREE_ASSET_REPAIR_PLAN.md) supplies the current coordinated movement design, dependency audit, proposed execution bounds and review criteria. Earlier design hypotheses remain historical; no repaired performance is claimed accepted.

## Existing-foot-control correction diagnostic (approved repair pass)

Evaluated near-ground hoof excursion measured 0.522 m after speed calibration. A single global speed does not establish foot contact. The bounded diagnostic will retain the source gallop action unchanged and test a separate overlay on verified existing hoof IK user controls. Targets are derived from observed source stance intervals; transition envelopes must be periodic and smooth, with no correction in the remaining swing. Maximum correction is 0.30 m and no bone stretching/new rig is permitted. This is an authored contact adaptation, not faithful untouched source motion or physical simulation. Measure the frozen near-ground excursion screen again; preserve failures and report clamps. Existing rider head stabilization/hip-spine-knee-elbow design remains the intended performance.
