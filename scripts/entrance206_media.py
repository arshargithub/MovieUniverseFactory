"""Exact-clock206 media and construction-versus-fresh-open pixel checks."""
import argparse,json,os,subprocess
from pathlib import Path
import numpy as np
from entrance189_media import sheet
from entrance193_media import sha,pixel_parity
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'.runtime/art-direction/series01-facebuilder-trial-01';OUT=ROOT/'.runtime/art-direction/series01-entrance206'
PARTS=('attention16','hair14','opening10','route11')

def main():
 p=argparse.ArgumentParser();p.add_argument('--encode',action='store_true');p.add_argument('--verify',action='store_true');args=p.parse_args();available={};records={};sources={}
 OUT.mkdir(exist_ok=True);qa=OUT/'qa';qa.mkdir(exist_ok=True)
 for part in PARTS:
  folder=BASE/('entrance206-'+part)
  for path in folder.glob('frame-*.png'):
   i=int(path.stem[6:])
   if i in available:raise ValueError('Duplicate chronology')
   available[i]=path
  meta=folder/'result.json'
  if not meta.exists():meta=folder/'progress.json'
  if meta.exists():
   r=json.loads(meta.read_text());kind='opening' if part in ('opening10','attention16') else 'route'
   if kind in sources and sources[kind]!=r['source_sha256']:raise ValueError('Interleaved source changed')
   sources[kind]=r['source_sha256']
   for row in r['frames']:records[row['index']]=row
 for first in range(0,432,12):
  ids=list(range(first,first+12))
  if all(i in available for i in ids):sheet([available[i] for i in ids],qa/f'all-{first:04d}.png')
 for part in ('attention16','hair14'):
  files=sorted((BASE/('entrance206-'+part)).glob('frame-*.png'))
  for first in range(0,len(files),12):
   if len(files[first:first+12])==12 or (BASE/('entrance206-'+part)/'result.json').exists():sheet(files[first:first+12],qa/f'{part}-{first:03d}.png')
 if args.verify:
  rows=[]
  for folder,frames in (('opening20',(311,321,327,339,350,360)),('route07',(361,372,384,390,409,472,487,529,577,648))):
   source=BASE/('entrance206-'+folder);r=json.loads((source/'result.json').read_text())
   for f in frames:
    i=f-217
    if i not in available:raise ValueError('Missing fresh-open frame')
    if r['native_sha256']!=sources['opening' if folder.startswith('opening') else 'route']:raise ValueError('Control source differs')
    rows.append(dict(frame=f,**pixel_parity(source/f'control-{f}.png',available[i])))
  (qa/'fresh-open.json').write_text(json.dumps(dict(status='PASS',samples=rows,scope='Construction controls versus independent factory-startup full-motion workers; source/pixel reproduction, not Director approval'),indent=2)+'\n')
 if not args.encode:return
 if set(available)!=set(range(432)) or set(records)!=set(range(432)):raise ValueError('Incomplete chronological footage')
 for part in PARTS:
  if not (BASE/('entrance206-'+part)/'result.json').exists():raise ValueError('Worker not finished')
 folder=OUT/'director-preview'
 if folder.exists():raise ValueError('Preserve existing delivery')
 folder.mkdir();rows=[]
 for i in range(432):
  r=records[i]
  if r['source_frame']!=217+i or sha(available[i])!=r['sha256']:raise ValueError('Source clock/hash mismatch')
  os.link(available[i],folder/f'frame-{i:04d}.png');rows.append(dict(index=i,native_frame=217+i,sha256=r['sha256'],source_image=str(available[i].relative_to(ROOT))))
 target=folder/'pashtun-complete-entrance.mp4';subprocess.run(['/opt/homebrew/bin/ffmpeg','-nostdin','-n','-v','error','-framerate','24','-i',str(folder/'frame-%04d.png'),'-frames:v','432','-c:v','libx264','-crf','16','-pix_fmt','yuv420p','-movflags','+faststart',str(target)],check=True)
 probe=json.loads(subprocess.check_output(['/opt/homebrew/bin/ffprobe','-v','error','-show_streams','-show_format','-of','json',str(target)]));s=probe['streams'][0]
 if int(s['nb_frames'])!=432 or s['avg_frame_rate']!='24/1' or abs(float(probe['format']['duration'])-18)>.001:raise ValueError('Encoded clock differs')
 subprocess.run(['/opt/homebrew/bin/ffmpeg','-nostdin','-v','error','-i',str(target),'-f','null','-'],check=True)
 (folder/'manifest.json').write_text(json.dumps(dict(frames=rows,native_sources=sources,fps=24,seconds=18,resolution=[432,768],video_sha256=sha(target),full_decode='PASS',processing='Exact native chronological217..648; no slow motion, frame synthesis or generated video',visual_gate='NOT_RUN'),indent=2)+'\n')

if __name__=='__main__':main()
