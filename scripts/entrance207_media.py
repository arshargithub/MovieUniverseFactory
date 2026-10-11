"""Exact207 native footage assembly, full chronology and source/replay checks."""
import argparse,json,os,subprocess
from pathlib import Path
import numpy as np
from entrance189_media import sheet
from entrance193_media import sha,pixel_parity
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'.runtime/art-direction/series01-facebuilder-trial-01';OUT=ROOT/'.runtime/art-direction/series01-entrance207'
PARTS=('opening03','route04','opening05','route06')
def main():
 p=argparse.ArgumentParser();p.add_argument('--encode',action='store_true');p.add_argument('--verify',action='store_true');args=p.parse_args();available={};records={};sources={}
 OUT.mkdir(exist_ok=True);qa=OUT/'qa';qa.mkdir(exist_ok=True)
 for part in PARTS:
  folder=BASE/('entrance207-'+part)
  for path in folder.glob('frame-*.png'):
   i=int(path.stem[6:])
   if i in available:raise ValueError('Duplicate frame')
   available[i]=path
  meta=folder/'result.json'
  if not meta.exists():meta=folder/'progress.json'
  if meta.exists():
   try:r=json.loads(meta.read_text())
   except json.JSONDecodeError:
    if meta.name=='progress.json':continue
    raise
   kind='opening' if part.startswith('opening') else 'route'
   if kind in sources and sources[kind]!=r['source_sha256']:raise ValueError('Interleaved source changed')
   sources[kind]=r['source_sha256']
   for row in r['frames']:records[row['index']]=row
 # A PNG can exist briefly before its render/write has completed. Review
 # only frames acknowledged by the worker, never a partially written file.
 available={i:path for i,path in available.items() if i in records}
 for first in range(0,432,12):
  ids=list(range(first,first+12))
  if all(i in available for i in ids):sheet([available[i] for i in ids],qa/f'all-{first:04d}.png')
 for part in ('opening03','route04'):
  files=sorted((BASE/('entrance207-'+part)).glob('frame-*.png'))
  for first in range(0,len(files),12):
   if len(files[first:first+12])==12 or (BASE/('entrance207-'+part)/'result.json').exists():sheet(files[first:first+12],qa/f'{part}-{first:03d}.png')
 if args.verify:
  if set(records)!=set(range(432)):raise ValueError('Full chronology required')
  previous={}
  for part in ('attention16','hair31','opening10','route11'):
   old=json.loads((BASE/('entrance206-'+part)/'result.json').read_text())
   for row in old['frames']:previous[row['index']]=row
  body=[];camera=[]
  for i,r in records.items():
   old=previous[i]
   if r['source_frame']!=old['source_frame']:raise ValueError('Source clock changed')
   body.append(max(float(np.max(abs(np.array(r['pose'][n])-np.array(old['pose'][n])))) for n in ('pelvis','chest','hand.L','hand.R','foot.L','foot.R')))
   camera.append(max(float(np.max(abs(np.array(r['camera'])-np.array(old['camera'])))),abs(r['lens']-old['lens'])))
  if max(body)>2e-5 or max(camera)>2e-5:raise ValueError('Protected contact/choreography camera changed')
  rows=[]
  for folder,fs in (('opening09',(313,319,325,331,337,343,350,360)),('threat10',(361,372,384,390,409,427,472,487,577,583,589,595,601,607,648))):
   src=BASE/('entrance207-'+folder);r=json.loads((src/'result.json').read_text());kind='opening' if folder.startswith('opening') else 'route'
   if sources[kind]!=r['native_sha256']:raise ValueError('Control source mismatch')
   for f in fs:rows.append(dict(frame=f,**pixel_parity(src/f'control-{f}.png',available[f-217])))
  (qa/'fresh-open.json').write_text(json.dumps(dict(status='PASS',samples=rows,protected_contact_max_error=max(body),all_camera_max_error=max(camera),limits='Technical scoped preservation and replay, not Director acceptance'),indent=2)+'\n')
 if not args.encode:return
 if set(available)!=set(range(432)) or set(records)!=set(range(432)):raise ValueError('Incomplete footage')
 if not (qa/'fresh-open.json').exists():raise ValueError('Verify before delivery')
 for part in PARTS:
  if not (BASE/('entrance207-'+part)/'result.json').exists():raise ValueError('Worker incomplete')
 folder=OUT/'director-preview'
 if folder.exists():raise ValueError('Preserve previous delivery')
 folder.mkdir();rows=[]
 for i in range(432):
  r=records[i]
  if r['source_frame']!=217+i or sha(available[i])!=r['sha256']:raise ValueError('Hash/clock mismatch')
  os.link(available[i],folder/f'frame-{i:04d}.png');rows.append(dict(index=i,native_frame=i+217,sha256=r['sha256'],source_image=str(available[i].relative_to(ROOT))))
 target=folder/'pashtun-complete-entrance.mp4';subprocess.run(['/opt/homebrew/bin/ffmpeg','-nostdin','-n','-v','error','-framerate','24','-i',str(folder/'frame-%04d.png'),'-frames:v','432','-c:v','libx264','-crf','16','-pix_fmt','yuv420p','-movflags','+faststart',str(target)],check=True)
 probe=json.loads(subprocess.check_output(['/opt/homebrew/bin/ffprobe','-v','error','-show_streams','-show_format','-of','json',str(target)]));s=probe['streams'][0]
 if int(s['nb_frames'])!=432 or s['avg_frame_rate']!='24/1' or abs(float(probe['format']['duration'])-18)>.001:raise ValueError('Encoded clock mismatch')
 subprocess.run(['/opt/homebrew/bin/ffmpeg','-nostdin','-v','error','-i',str(target),'-f','null','-'],check=True)
 (folder/'manifest.json').write_text(json.dumps(dict(frames=rows,native_sources=sources,fps=24,seconds=18,resolution=[432,768],video_sha256=sha(target),full_decode='PASS',processing='Exact native frames; no slow motion, synthetic in-betweens or generated video',visual_gate='NOT_RUN'),indent=2)+'\n')
if __name__=='__main__':main()
