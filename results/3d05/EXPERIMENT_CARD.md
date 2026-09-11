# 3D-05 closure card

**Closed YELLOW: technical execution and minimum visual quality passed; timing preference was not demonstrated. No further iteration planned.**

Goal: one stationary admitted humanoid reaches, encloses the modified sword handle, attaches continuously, lifts and holds it; revise pickup timing within a bounded interval while preserving other motion and state.

Demonstrated: technical gates for both variants, 18 discriminative native scene controls, six checkpoint/reopen pairs and exact replay. Both clips received 5/5 readability, transition smoothness and hold/clearance, and 4.5/5 grasp/contact. Preference was tied; review took approximately 120 seconds. Neither required readability improvement nor candidate preference was demonstrated. A handle seating reservation remains.

Observed causes and lessons: fixture fit and closed collision representation had to be qualified; parent-pose/constraint relationships and coordinated motion mattered; isolated joint tuning and late measurement corrections caused rework. The timing-only preference gate lacked a clear dramatic objective. Stronger-model use coincided with changed fixtures, contracts and feedback, so it is not a controlled model advantage.

Bindings: [final report](closure-v1/REPORT.md), execution commit `1bc89a3`, evidence bundle `c37634b`, completed review `c4842c0`, [checksummed supplement](../../exports/3d05-closure-v1-supplement/README.md) committed at `adb17cb`. Historical rejected records and the large bundle are unchanged.

Effort: user-reported approximately 150 minutes of engineering; exact calendar/net breakdown and engineering tokens/cost UNKNOWN. Full preflight 876.56 seconds and scored campaign 1529.82 seconds; these are separate job walls, not total elapsed or CPU time. API calls/cost were 0/$0; Director review was approximately 120 seconds. See [process review](closure-v1/PROCESS_REVIEW.md). New telemetry must not manufacture a historical total.

Reusable: evaluated-parent motion transfer, fixture screening, surface/enclosure/ownership checks, fractional boundary probes, native control sensitivity, synchronized review and portable evidence supplements. Limits: one low-poly rig, modified sword, stationary root and scripted kinematics; no arbitrary assets, physical grasp, release, locomotion or combat.

Next question: can a small no-prop upper-body gesture match a declared reference cue, survive a timing revision and retain quality? Transfer the relevant lessons to [3D-06A](../../feasibility/3d/3d-06a/SPEC.md). Preserve the known rig as a control; admit a better-deforming fixture separately before richer motion. No more 3D-05 repairs are planned.
