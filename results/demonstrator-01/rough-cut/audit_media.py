"""Read-only media integrity and image diagnostics; no perceptual pass invented."""
from pathlib import Path
import json,hashlib,subprocess
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parents[3];R=ROOT/'results/demonstrator-01/rough-cut';B=ROOT/'runs/demonstrator-01'
inv=json.loads((R/'frame-inventory.json').read_text());rows=[];previous=None
for rec in inv['frames']:
 p=ROOT/rec['path'];assert hashlib.sha256(p.read_bytes()).hexdigest()==rec['sha256']
 a=np.asarray(Image.open(p).convert('RGB').resize((160,90)),dtype=float)/255
 mean=float(a.mean());black=float(np.mean(np.max(a,axis=2)<.025));rms=None if previous is None else float(np.sqrt(np.mean((a-previous)**2)));previous=a
 rows.append({'frame':rec['frame'],'mean_rgb':mean,'near_black_fraction':black,'adjacent_rms_rgb':rms,'cut_boundary':rec['frame'] in (144,312,432)})
# Independent re-open render is compared with the scene-build preflight of the same frame.
ref=B/'cut-world-v4/preflight/shot2_f0220.png';rec=inv['frames'][220];actual=ROOT/rec['path']
a=np.array(Image.open(ref).convert('RGB'),dtype=float);b=np.array(Image.open(actual).convert('RGB'),dtype=float)
replay={'scene_sha256':inv['scene_sha256'],'frame':220,'reference':str(ref.relative_to(ROOT)),'reopened_render':str(actual.relative_to(ROOT)),'reference_sha256':hashlib.sha256(ref.read_bytes()).hexdigest(),'reopened_sha256':rec['sha256'],'pixels_identical':bool(np.array_equal(a,b)),'max_channel_error_8bit':float(np.abs(a-b).max()),'rms_channel_error_8bit':float(np.sqrt(np.mean((a-b)**2))),'scope':'scene-build preflight versus independently loaded receipt-bound render worker; no provider call'}
(R/'replay.json').write_text(json.dumps(replay,indent=2)+'\n')
# Check every encoded video timestamp, not only stream metadata.
p=json.loads(subprocess.check_output(['/opt/homebrew/bin/ffprobe','-v','error','-select_streams','v:0','-show_entries','frame=best_effort_timestamp_time','-of','json',str(B/'cut-review/the-courier-24s.mp4')]))
ts=[float(f['best_effort_timestamp_time']) for f in p['frames']];timing=len(ts)==576 and all(abs(t-i/24)<.00001 for i,t in enumerate(ts))
assert timing
report={'frames':576,'timestamp_check_pass':timing,'adjacent_identical_source_pngs':inv['adjacent_identical_pngs'],'minimum_mean_rgb':min(x['mean_rgb'] for x in rows),'maximum_near_black_fraction':max(x['near_black_fraction'] for x in rows),'largest_noncut_rms':sorted([x for x in rows if x['adjacent_rms_rgb'] is not None and not x['cut_boundary']],key=lambda x:x['adjacent_rms_rgb'],reverse=True)[:5],'samples':rows,'interpretation':'integrity and image diagnostics only; not a temporal or photorealism acceptance score'}
(R/'media-audit.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='samples'}));print(json.dumps(replay))
