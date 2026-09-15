from pathlib import Path
import json,hashlib,os,shutil,subprocess,time
from PIL import Image,ImageStat
from movie_factory.telemetry import utc_now
from movie_factory.experiment_ledger import Ledger
ROOT=Path(__file__).resolve().parents[3];R=ROOT/'results/demonstrator-01/reuse-camera-revision';B=ROOT/'runs/demonstrator-01/reuse-01';OUT=ROOT/'runs/demonstrator-01/reuse-camera-continuous-review'
f=json.loads((R/'FREEZE.json').read_text())
for row in f['implementation_files']:assert hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest()==row['sha256'],row['path']
status=json.loads((B/'revision/runner-status.json').read_text());assert status['ok']
r=json.loads((B/'revision/reuse.json').read_text());assert r['protected_before']==r['protected_after'] and r['protected_reopen']
assert hashlib.sha256((ROOT/'runs/demonstrator-01/cut-world-v4/scene.blend').read_bytes()).hexdigest()==r['source_sha256']
pts=json.loads(subprocess.check_output(['/opt/homebrew/bin/ffprobe','-v','error','-select_streams','v:0','-show_frames','-show_entries','frame=best_effort_timestamp_time','-of','json',str(OUT/'camera-preview.mp4')]))['frames']
assert len(pts)==120 and all(abs(float(x['best_effort_timestamp_time'])-i/24)<1e-5 for i,x in enumerate(pts))
means=[]
for p in (OUT/'frames').glob('*.png'):
 with Image.open(p) as im:means.append(sum(ImageStat.Stat(im.convert('RGB')).mean)/3)
assert len(means)==120 and min(means)>5
native=sum(json.loads(p.read_text())['elapsed'] for p in B.glob('*/runner-status.json'));assert native<5400
result={'utc':utc_now(),'classification':'CODE_ASSISTED; second disclosed code intervention following explicit Director revision','director_acceptance':'PENDING','director_review_duration_seconds':None,'seconds':5,'frames':120,'timestamps_match_24fps':True,'nonblack_frames':120,'protected_reopen':True,'protected_fingerprint':r['protected_after'],'runtime_matches_revision_freeze':True,'native_revision_seconds':status['elapsed'],'cumulative_reuse_native_seconds':native,'native_ceiling_seconds':5400,'api_calls':0,'api_cost_usd':0,'free_disk_GiB':shutil.disk_usage(ROOT).free/2**30,'independent_revision_replay':'NOT_RUN; normal worker reopened saved scene before rendering; prior preview replay remains separate','aws_actions':'Requirements documentation only; no account authentication, provisioning, upload or deletion'}
(R/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
(R/'REPORT.md').write_text(f'''# Continuous camera revision — Director review pending

[Watch the revised five-second preview](../../../runs/demonstrator-01/reuse-camera-continuous-review/review.html) · [Previous preview](../../../runs/demonstrator-01/reuse-camera-review/review.html)

The Director found the earlier move too segmented: fast descent, stationary side hold and fast final sweep. The new curve takes longer to descend, moves closer while turning through the side view, and carries velocity into the final sweep. Endpoints, five-second duration and actor/world motion are preserved. The existing horse/rider/dust/scenery have not been repaired or embellished.

This is **code-assisted reuse**, with a second disclosed camera-code intervention under the explicit feedback request. It does not satisfy the original parameter-only/one-repair contract. Old requests, freezes, failures and preview remain preserved. To replay the previous runtime, use its source commit60fc086; its old source fingerprints are historical rather than assertions about the current checkout. See [feedback](feedback.json), [plan](PLAN.md), [request](request.json) and [current freeze](FREEZE.json).

28 focused tests passed, including shared nonzero interior velocity, dense bounded path sampling and conservative curve clearance. Normal native execution checked source SHA and protected noncamera fingerprints before/after and after saved-scene reopen. All120 source frames and encoded timestamps verified at24fps/5seconds; no black frames. The prior selected independent replay belongs to the previous preview and is not claimed for this revision. No repeated broad suite or additional native replay was needed for this camera adjustment.

Revision native time:{status['elapsed']/60:.2f}min. Cumulative reuse native time including every retained attempt:{native/60:.2f}/90min. Paid API:$0. Free disk:{result['free_disk_GiB']:.2f}GiB. Historical exact active/token totals and current review duration remain unknown. Director acceptance is pending; no score invented.

AWS work this turn was limited to the [S3 setup requirements](../../../docs/planning/S3_ARCHIVE_SETUP.md) and reading CLI version. No cloud resource, transfer, charge or local deletion. The next production brief remains deferred.
''')
l=Ledger(ROOT/'.runtime/experiment-ops.sqlite3')
l.append(dict(event_id='camera-continuous-review-wait',experiment_id='DEMONSTRATOR-01',episode_id='reuse-camera',event_type='wait_started',phase='director-review',utc=utc_now(),wait_id='camera-continuous-review',reason='director_response',evidence_ref=str((R/'REPORT.md').relative_to(ROOT))))
(R/'operating-events.json').write_text(json.dumps([e for e in l.events() if e['experiment_id']=='DEMONSTRATOR-01' and e['episode_id']=='reuse-camera'],indent=2)+'\n')
files=set()
for d in [R,B/'revision',OUT]:
 for p in d.rglob('*'):
  if p.is_file() and p.name not in ['ARTIFACTS.json','.DS_Store'] and not any(x in p.parts for x in ['.worker_runtime','__pycache__']):files.add(p)
files.add(ROOT/'docs/planning/S3_ARCHIVE_SETUP.md')
rows=[]
for p in sorted(files):
 row={'path':str(p.relative_to(ROOT))}
 if p.is_symlink():row['symlink']=os.readlink(p)
 else:
  with p.open('rb') as fd:row.update(bytes=p.stat().st_size,sha256=hashlib.file_digest(fd,'sha256').hexdigest())
 rows.append(row)
(R/'ARTIFACTS.json').write_text(json.dumps({'artifacts':rows,'scope':'continuous revision supplement, self excluded'},indent=2)+'\n')
print(json.dumps(result,indent=2))
