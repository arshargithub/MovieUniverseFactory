# Stage A full motion preview

**YELLOW / incomplete — do not start full production.** The complete 2.5-second, 60-frame clip is available in [the player](../../../runs/demonstrator-01/motion-v2/review.html) and [MP4](../../../runs/demonstrator-01/motion-v2/preview.mp4). No Director full-motion acceptance is recorded.

## What changed and what is demonstrated

The source horse had a FOLLOW_PATH object constraint. Moving its inherited path and adding a travel parent doubled its displacement. The motion-v1 pre-render guard rejected that case. In motion-v2 the source path constraint is muted and its evaluated starting transform preserved, leaving one travel owner. Expected travel is -8.481250 m over frames 0–59; saddle displacement is -8.481249809 m. The source authored gallop remains assigned through NLA.

The rider uses the demonstrated root normalization, refreshed dependency evaluation and disabled leftover presentation animation. Only intended rider controls are keyed; mechanism/deformation bones are left to the existing rig. Camera framing is fitted at frame zero to evaluated nonempty actor meshes. Original render subdivision settings are retained. Three malformed structured jobs were rejected by the fixed operation boundary. No arbitrary code input or embedded source scripts are enabled.

All 60 PNGs exist; ffprobe confirms 60 video frames, 24 fps, 640×360 and 2.500 seconds. Native worker completed successfully. This verifies artifact completeness, not creative acceptance or contact quality. Supervisor inspection of selected frames found the defects below; no claim of independent full-clip temporal validation is made.

## Remaining visual and asset problems

- The tail becomes unstable and extends dramatically during the sequence. The cause has not yet been isolated; simulation/state handling is a hypothesis.
- The rider is stiff relative to the gallop; hands do not hold the reins. Correct pelvis placement alone is insufficient.
- Source saddle SurfaceDeform reports no valid target mesh and dependency cycles. Tack/back motion is not qualified. Do not conceal this warning as harmless because the scene rendered.
- Forward speed remains provisional 3.45 m/s. Correct total travel is not evidence of calibrated hoof stance or low sliding. No evaluated sole-slip or penetration gate has passed.
- Materials, scenery, dust, sound and film editing are not finished. The preview demonstrates an assembled animated fixture, not the four-shot story.

## Measured envelope and scope-freeze status

Apple M4 / 16 GiB, Blender 5.2.1 LTS, Cycles CPU, 640×360, eight samples with denoising. Frame rendering totaled **199.50 seconds**, median **3.35 s/frame**, mean **3.32 s/frame**. Full worker job was **210.71 seconds**. Encoding completed locally. No additional paid calls; campaign remains $1.326285001 calculated, no outstanding reservations.

At identical settings a provisional 24-second / 576-frame cut extrapolates to **31.9 minutes** of frame rendering, excluding setup and rerenders. Allowing 2× for one rough-cut revision suggests roughly **64 minutes** local rendering at the same quality. Pure pixel scaling to 720p is four times this cost, but is not a benchmark; 1080p, higher sampling, dust and final look remain unmeasured. The current scene is unsuitable as a finished-look cost reference.

No honest full-production active-work ceiling can be frozen while core contact/asset repairs remain unresolved. The original 24-second, four-shot dry-road plan and >=4/5 proposed creative scorecard remain proposals. Stage A gate is not passed.

## Recommended decision

Do not continue piecemeal repairs indefinitely. This was the first integration approach (separate horse and knight), including the bounded recovery. Use the charter's second candidate approach only after presenting this evidence: a verified preassembled mounted rider/horse with compatible authored gallop. Preserve the horse/rider brief; purchases remain unapproved. If no suitable fixture can be qualified promptly, stop with a scope alternative rather than begin a custom rigging project. No second asset was acquired in this pass.

[Earlier failed checkpoint](STAGE_A_GATE.md), [pose recovery](RECOVERY.md), [motion brief](../../../feasibility/demonstrator-01/MOTION_BRIEF.md) and source histories remain preserved. No closed campaign, remote repository or large export was changed by this preview.
