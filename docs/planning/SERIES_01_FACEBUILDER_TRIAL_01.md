# FaceBuilder likeness trial — operational record

2026-09-19. Director authorized installation, then one bounded fitting attempt using approved portrait pair B; subsequently requested another UI attempt after bringing Blender forward. Installation and setup are implementation activity, not additional substantive creative-planning exchanges.

## Verified state

- Blender 5.2.1 LTS at `/Applications/Blender.app`; KeenTools extension and Core 2026.3.1 installed and confirmed in Preferences. FaceBuilder enabled; GeoTracker and FaceTracker disabled. No purchase or account created.
- One default FaceBuilder head created in an unsaved Untitled scene. No fitted character, texture, export or accepted likeness output exists yet. Earlier messages described the trial as active; exact license activation/expiry has not been read and remains unverified.
- Approved inputs: `.runtime/art-direction/series01-pashtun-baseline-v01/frontal-v02-individualized.png` and `portrait-v07-individualized.png`. Originals remain unchanged.
- Retry after Director foregrounding succeeded: pointer clicks opened the FaceBuilder tab and Add Images picker. Earlier pointer failures therefore do not establish a permanent FaceBuilder/Factory limitation. No console code was executed.
- Navigating the picker to the reference folder on the SSD remained at Loading. Requesting the frontal image then left Blender unresponsive. Process 45153 remained alive; no new Blender crash report was found.
- One-second native stack sample shows main thread waiting for file-browser worker termination (`ED_fileselect_exit` → `WM_jobs_kill_all_from_owner` → `_pthread_join`), with the directory worker blocked at `__opendir2` → `open$NOCANCEL`. This localizes the stall to directory access; it does not prove SSD failure or a macOS permission cause. Diagnostic sample: `/private/tmp/moviefactory-blender-import-sample.txt` (temporary, not backed up).

## Permission recovery and initial fitting

Director approved SSD access; the file picker subsequently listed and loaded the approved portraits. FaceBuilder visibly reports **Trial: 14 days left**. This supersedes the earlier activation uncertainty and unresponsive-directory state above.

An initial textured diagnostic head is saved at `.runtime/art-direction/series01-facebuilder-trial-01/head-v01-diagnostic.blend`. Blender's Pack Resources command was invoked and the scene saved again; independent reopen/export verification is still pending. No originals were edited. The default cube is hidden, not deleted.

The first placeholder camera acquired an incorrectly framed frontal image. Re-importing through Add Images created a correctly proportioned frontal view; Auto Align detected and pinned that view and the approved three-quarter view. The malformed original camera remains in the scene with pins: it was excluded from texture generation, **but not yet removed from the geometric solve**. Therefore this diagnostic must not be accepted as a clean two-view fit. Preserve it as failed/setup evidence before removing the malformed camera and refitting.

The generated texture produces a recognizable face in the frontal viewport, but side/back coverage is incomplete and clothing/hair projections contaminate parts of the head/neck. This is not a production likeness or style approval. Hair, headscarf, unseen anatomy and texture cleanup remain unresolved; no portable export or controlled multi-angle review has been completed. No purchase or paid provider call was made during this recovery.

Next bounded action: remove only the malformed first FaceBuilder camera and its pins (GUI deletion requires Director confirmation), refit the two valid views, then inspect plain/textured modest novel angles. Do not expand into body/horse/animation work. Native diagnostic assets remain local and outside Git; this note does not imply off-machine backup.

## Previous recovery plan (resolved)

Check for a macOS removable-volume access prompt. Do not force-quit without accounting for the unsaved scene. If restart is necessary, only the default unfitted head is known to exist from this task. A temporary copy of the two references on internal storage is a possible diagnostic after recovery, preserving the SSD originals. Resume fitting only after basic file access works.

Operating ledger: `SERIES01-LIKENESS-ASSET` / `facebuilder-trial-01`; report under `.runtime/art-direction/series01-facebuilder-trial-01/operating`. Earlier installation/research effort was not captured; exact total engineering usage remains unknown. Prior failed-pointer proxy count was partial and must not be interpreted as exhaustive. Preserve the 20-net-minute diagnostic / 60-net-minute overall checkpoints, with Director waits excluded. No paid model calls dispatched by this retry. Likeness and portability qualification remain NOT_RUN.
