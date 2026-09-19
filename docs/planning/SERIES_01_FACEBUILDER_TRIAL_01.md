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

## Clean two-view candidate

Director authorized removing the malformed camera and described the initial likeness as coming along nicely, while flagging neck artifacts. This is encouraging feedback, not final likeness approval.

- Removed only the malformed first FaceBuilder view and its pins through the add-on. The original `head-v01-diagnostic.blend` remains recoverable and unchanged by this cleanup.
- Re-ran Auto Align on both valid views and regenerated texture. The Views panel now contains only the correctly imported frontal and three-quarter references.
- Compared solid shading against the texture at front and a modest approximately 30-degree novel angle. The neck sliver disappears in solid shading; it is projected scarf imagery, not a visible mesh tear. Dark side-neck regions are also texture coverage problems. This visual check is not a topology audit.
- Saved packed candidate `.runtime/art-direction/series01-facebuilder-trial-01/head-v02-two-view.blend` separately. Both saved scene files exist. Portable mesh export and independent reopen verification remain NOT_RUN.
- Face geometry appears coherent in this limited inspection, but likeness across angles still needs Director review. Hair/ears/neck textures include inferred or contaminated regions. Do not treat projected hair as modeled hair or the current preview as the final illustrated style.

Next: a small front/angled likeness review, then mask/repair the neck texture and build the scarf/hair as separate assets if this candidate is accepted. Do not repeatedly refit facial geometry to fix texture-only artifacts. No paid calls or purchases in this cleanup. Experiment remains open pending review and portability verification.

## Texture comparison and portable round-trip

Director requested continued autonomous progress, yielding only for material creative/approval decisions rather than small implementation steps.

- Preserved a third candidate, `head-v03-frontal-texture.blend`: unchanged two-view fitted geometry, frontal-only texture source, AutoFill enabled. This removes the central blue neck sliver but introduces side-face stretching/appearance differences and does not resolve all rear-neck coverage. It is a diagnostic comparison, not the selected replacement for v02. No further variants were generated.
- Exported `head-v03-frontal-texture.fbx` using selected-object export, Copy path mode and embedded textures. Imported it through Blender's standard FBX importer into a fresh General scene, with its default cube hidden. Head geometry and textured material appeared successfully without restoring FaceBuilder cameras or fitting data. Saved packed evidence as `head-v03-fbx-roundtrip.blend`.
- Round-trip has **partial portability evidence**, not full parity: the imported material looks different; imported transform shows X rotation 90 degrees and uniform scale 0.010. No dimensions/vertex-digest comparison, add-on-disabled test, rig test or animation test was performed. Do not call this a production-ready asset or a proven add-on-free pipeline yet.
- Reopened `head-v02-two-view.blend` successfully and inspected both modest three-quarter sides. v02 remains the preferred likeness-review candidate; the third variant illustrates why neck repair should use local masking/painting rather than replacing the whole face texture. The source image cannot supply unseen anatomy or covered skin.

### Decision checkpoint

The meaningful next decision is whether **v02 facial likeness is an acceptable 3D starting point**, explicitly excluding projected hair/scarf, unfinished ears/neck, final shading and animation. Recommendation: conditionally accept it as a base if the Director recognizes her at front and both modest angles, then perform targeted neck/texture repair and separate hair/scarf construction. Otherwise identify the specific facial mismatch before spending on more modeling. Neither automatic matching nor the Director's earlier encouraging comment establishes full likeness approval.

No paid provider calls or purchases were made. Assets are local and not backed up by the documentation commit. Experiment remains open pending this creative review; no additional major scope is authorized by technical progress alone.

## Previous recovery plan (resolved)

Check for a macOS removable-volume access prompt. Do not force-quit without accounting for the unsaved scene. If restart is necessary, only the default unfitted head is known to exist from this task. A temporary copy of the two references on internal storage is a possible diagnostic after recovery, preserving the SSD originals. Resume fitting only after basic file access works.

Operating ledger: `SERIES01-LIKENESS-ASSET` / `facebuilder-trial-01`; report under `.runtime/art-direction/series01-facebuilder-trial-01/operating`. Earlier installation/research effort was not captured; exact total engineering usage remains unknown. Prior failed-pointer proxy count was partial and must not be interpreted as exhaustive. Preserve the 20-net-minute diagnostic / 60-net-minute overall checkpoints, with Director waits excluded. No paid model calls dispatched by this retry. Likeness and portability qualification remain NOT_RUN.
