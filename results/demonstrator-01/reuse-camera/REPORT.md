# Five-second camera-only preview

**Delivered for Director review. Classification: code-assisted reuse.** Parameter-only held-out reuse remains not demonstrated because the requested multi-stage camera and holds required an extension after the original freeze. No broader production work was performed.

[Watch the complete preview](../../../runs/demonstrator-01/reuse-camera-review/review.html) · [MP4](../../../runs/demonstrator-01/reuse-camera-review/camera-preview.mp4) · [Contact sheet](../../../runs/demonstrator-01/reuse-camera-review/contact-sheet.jpg)

The five-second120-frame clip begins centered high behind the horse, descends to its right, holds a parallel side view, and settles into offset frontal tracking. See [motion-free camera plan](PLAN.md), [structured request](request.json), [successor freeze](FREEZE.json) and [authorization](authorization.json). Global frames144–263 reuse the existing world at24fps,640×360,16 Eevee samples. Preview is silent. Horse/rider motion, speed, dust, grass/scenery and lighting are unchanged.

## Verification and limits

26 relevant offline tests passed. Strict2–6-knot input, finite bounded offsets, monotonically increasing normalized times, explicit holds and exact segment clearance were verified. The worker bound the baseline scene SHA, matched noncamera identity/mesh/animation fingerprints before/after and on reopen, and rendered the saved derived scene. Full media contains120 frames at24fps/5seconds; the frame inventory binds all source PNGs. Original accepted movie/native scene hashes are unchanged. The working camera runtime was intentionally extended; original source evidence stays preserved in its commits. Successor runtime still matches its freeze.

Selected-frame replay: PIXEL_DIFFERENCE_RECORDED. Maximum difference1/255; RMS0.006804/255. Protected-state fingerprints matched. No exact pixel-reproduction claim is made. See [replay evidence](replay.json) when present. These checks do not establish physical contact, material equivalence, arbitrary-world support or final production realism. Selected early views were inspected; complete creative playback acceptance remains the Director's decision.

## Costs and disposition

This shot consumed12.80 native process-minutes. Cumulative native processing across all reuse attempts, failures and any replay is25.98/90minutes. API calls/cost:$0. Existing active engineering ceiling60min and API ceiling$5 remain; known local activity/checkpoints and gaps are in operating records. Native processing overlaps supervision and is not added to engineering time. Historical exact active/token usage and current review duration are unknown. Disk free at finalization:6.48GiB. No paid assets, cloud render, public push or backup transfer.

Director acceptance and one possible composition revision are pending; no scores or review duration invented. Ask whether the height/centering, side hold and frontal ending match the requested move, then obtain one meaningful camera revision if desired. Further code repair would remain disclosed; it cannot erase the original interface gap.

The remaining racing posture/speed, larger dust, detailed grass, stop/rear and dismount requests are preserved in the [next production brief](../../../docs/planning/NEXT_PRODUCTION_EXPERIMENT_BRIEF.md). Its8h engineering/12h native/$30 proposal requires separate authorization and storage preparation. This preview does not authorize that work.
