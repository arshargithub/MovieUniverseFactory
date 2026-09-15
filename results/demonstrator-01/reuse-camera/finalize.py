"""Record measured camera-only delivery without inventing Director acceptance."""
from pathlib import Path
import json,hashlib,shutil
from movie_factory.telemetry import utc_now
ROOT=Path(__file__).resolve().parents[3];R=ROOT/'results/demonstrator-01/reuse-camera';RUN=ROOT/'runs/demonstrator-01/reuse-01';OUT=ROOT/'runs/demonstrator-01/reuse-camera-review'
freeze=json.loads((R/'FREEZE.json').read_text())
for row in freeze['implementation_files']:
 assert hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest()==row['sha256'],row['path']
shot=json.loads((RUN/'shot/runner-status.json').read_text());assert shot['ok']
receipt=json.loads((RUN/'shot/reuse.json').read_text())
a=json.loads((ROOT/'results/demonstrator-01/rough-cut/director-acceptance/acceptance.json').read_text())
assert hashlib.sha256((ROOT/a['film_path']).read_bytes()).hexdigest()==a['film_sha256']
assert hashlib.sha256((ROOT/'runs/demonstrator-01/cut-world-v4/scene.blend').read_bytes()).hexdigest()==a['scene_sha256']
statuses=[(p.parent.name,json.loads(p.read_text())) for p in RUN.glob('*/runner-status.json')]
native=sum(s['elapsed'] for _,s in statuses);assert native<=5400
replay=json.loads((R/'replay.json').read_text()) if (R/'replay.json').exists() else {'status':'NOT_RUN'}
result={'utc':utc_now(),'classification':'CODE_ASSISTED; parameter-only reuse NOT_DEMONSTRATED','delivery':'five-second120-frame camera-only preview','director_acceptance':'PENDING','director_review_duration_seconds':None,'protected_fingerprint':receipt['protected_after'],'protected_reopen':receipt['protected_reopen'],'accepted_scene_and_film_unchanged':True,'new_runtime_matches_successor_freeze':True,'runtime_digest':freeze['implementation_digest'],'all_original_reuse_native_seconds':native,'native_ceiling_seconds':5400,'shot_native_seconds':shot['elapsed'],'native_jobs':[{'name':name,'ok':s['ok'],'seconds':s['elapsed']} for name,s in statuses],'api_calls':0,'api_cost_usd':0,'free_disk_GiB':shutil.disk_usage(ROOT).free/2**30,'replay':replay,'future_production_executed':False}
(R/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
(R/'REPORT.md').write_text(f'''# Five-second camera-only preview

**Delivered for Director review. Classification: code-assisted reuse.** Parameter-only held-out reuse remains not demonstrated because the requested multi-stage camera and holds required an extension after the original freeze. No broader production work was performed.

[Watch the complete preview](../../../runs/demonstrator-01/reuse-camera-review/review.html) · [MP4](../../../runs/demonstrator-01/reuse-camera-review/camera-preview.mp4) · [Contact sheet](../../../runs/demonstrator-01/reuse-camera-review/contact-sheet.jpg)

The five-second120-frame clip begins centered high behind the horse, descends to its right, holds a parallel side view, and settles into offset frontal tracking. See [motion-free camera plan](PLAN.md), [structured request](request.json), [successor freeze](FREEZE.json) and [authorization](authorization.json). Global frames144–263 reuse the existing world at24fps,640×360,16 Eevee samples. Preview is silent. Horse/rider motion, speed, dust, grass/scenery and lighting are unchanged.

## Verification and limits

26 relevant offline tests passed. Strict2–6-knot input, finite bounded offsets, monotonically increasing normalized times, explicit holds and exact segment clearance were verified. The worker bound the baseline scene SHA, matched noncamera identity/mesh/animation fingerprints before/after and on reopen, and rendered the saved derived scene. Full media contains120 frames at24fps/5seconds; the frame inventory binds all source PNGs. Original accepted movie/native scene hashes are unchanged. The working camera runtime was intentionally extended; original source evidence stays preserved in its commits. Successor runtime still matches its freeze.

Selected-frame replay: {replay.get('status','NOT_RUN')}. See [replay evidence](replay.json) when present. These checks do not establish physical contact, material equivalence, arbitrary-world support or final production realism. Selected early views were inspected; complete creative playback acceptance remains the Director's decision.

## Costs and disposition

This shot consumed{shot['elapsed']/60:.2f} native process-minutes. Cumulative native processing across all reuse attempts, failures and any replay is{native/60:.2f}/{5400/60:.0f}minutes. API calls/cost:$0. Existing active engineering ceiling60min and API ceiling$5 remain; known local activity/checkpoints and gaps are in operating records. Native processing overlaps supervision and is not added to engineering time. Historical exact active/token usage and current review duration are unknown. Disk free at finalization:{result['free_disk_GiB']:.2f}GiB. No paid assets, cloud render, public push or backup transfer.

Director acceptance and one possible composition revision are pending; no scores or review duration invented. Ask whether the height/centering, side hold and frontal ending match the requested move, then obtain one meaningful camera revision if desired. Further code repair would remain disclosed; it cannot erase the original interface gap.

The remaining racing posture/speed, larger dust, detailed grass, stop/rear and dismount requests are preserved in the [next production brief](../../../docs/planning/NEXT_PRODUCTION_EXPERIMENT_BRIEF.md). Its8h engineering/12h native/$30 proposal requires separate authorization and storage preparation. This preview does not authorize that work.
''')
i=ROOT/'results/demonstrator-01/INDEX.md';s=i.read_text();s+='\n## Current camera-only successor\n\nThe Director narrowed the next request to the multistage5-second camera preview. See [current delivery](reuse-camera/REPORT.md). This is a disclosed code-assisted extension; it does not convert the original parameter-only reuse test into a pass. Remaining production changes are [captured for later](../../docs/planning/NEXT_PRODUCTION_EXPERIMENT_BRIEF.md), not started.\n';i.write_text(s)
print(json.dumps({'native_minutes':native/60,'shot_minutes':shot['elapsed']/60,'free_GiB':result['free_disk_GiB']}))
