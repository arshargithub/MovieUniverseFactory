"""Exact-clock205 review sheets, encoding and independent reopen checks."""
import argparse,json,os,subprocess
from pathlib import Path
import numpy as np
from entrance189_media import sheet
from entrance193_media import sha,pixel_parity
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'.runtime/art-direction/series01-facebuilder-trial-01'
OUT=ROOT/'.runtime/art-direction/series01-entrance205'
PARTS=('opening13','route14','opening15','route16')


def main():
 p=argparse.ArgumentParser();p.add_argument('--encode',choices=('internal','final'));p.add_argument('--verify',action='store_true');a=p.parse_args()
 available={};records={};sources={}
 OUT.mkdir(exist_ok=True);qa=OUT/'qa';qa.mkdir(exist_ok=True)
 for part in PARTS:
  folder=BASE/('entrance205-'+part)
  for path in folder.glob('frame-*.png'):
   i=int(path.stem[6:])
   if i in available:raise ValueError('Duplicate chronology')
   available[i]=path
  if (folder/'result.json').exists():
   r=json.loads((folder/'result.json').read_text());kind='opening' if part.startswith('opening') else 'route'
   if kind in sources and sources[kind]!=r['source_sha256']:raise ValueError('Interleaved source changed')
   sources[kind]=r['source_sha256']
   for row in r['frames']:records[row['index']]=row
 for label,step,offset in (('even',2,0),('odd',2,1),('all',1,0)):
  for first in range(offset,432,12*step):
   ids=list(range(first,min(first+12*step,432),step))
   if all(i in available for i in ids):sheet([available[i] for i in ids],qa/f'{label}-{first:04d}.png')
 if a.verify:
  rows=[]
  for original,verify in (('opening13','reopen17'),('route14','reopen18')):
   x=json.loads((BASE/('entrance205-'+original)/'result.json').read_text());y=json.loads((BASE/('entrance205-'+verify)/'result.json').read_text())
   for k in ('source_sha256','fingerprint','resolution','samples'):
    if x[k]!=y[k]:raise ValueError('Reopen state differs: '+k)
   for row in y['frames']:
    i=row['index'];prior=records[i]
    error=max(float(abs(np.array(prior['pose'][n])-row['pose'][n]).max()) for n in row['pose'])
    if error>2e-5 or row['source_frame']!=prior['source_frame']:raise ValueError('Reopen pose or clock differs')
    rows.append({'index':i,'pose_error':error,**pixel_parity(available[i],BASE/('entrance205-'+verify)/f'frame-{i:04d}.png')})
  (qa/'reopen.json').write_text(json.dumps({'status':'PASS','samples':rows,'scope':'Source, structural, pose and pixel reproduction; not Director or aesthetic approval'},indent=2)+'\n')
 if not a.encode:return
 final=a.encode=='final';ids=list(range(432)) if final else list(range(0,432,2));fps=24 if final else 12
 if not all(i in available and i in records for i in ids):raise ValueError('Incomplete chronology')
 for i in ids:
  if records[i]['source_frame']!=217+i or sha(available[i])!=records[i]['sha256']:raise ValueError('Source clock/frame changed')
 folder=OUT/('director-preview' if final else 'internal-motion')
 if folder.exists():raise ValueError('Preserve existing evidence')
 folder.mkdir();rows=[]
 for j,i in enumerate(ids):
  os.link(available[i],folder/f'frame-{j:04d}.png');rows.append({'index':i,'native_frame':217+i,'sha256':records[i]['sha256'],'source_image':str(available[i].relative_to(ROOT))})
 target=folder/'pashtun-complete-entrance.mp4'
 subprocess.run(['/opt/homebrew/bin/ffmpeg','-nostdin','-n','-v','error','-framerate',str(fps),'-i',str(folder/'frame-%04d.png'),'-frames:v',str(len(ids)),'-c:v','libx264','-crf','16','-pix_fmt','yuv420p','-movflags','+faststart',str(target)],check=True)
 probe=json.loads(subprocess.check_output(['/opt/homebrew/bin/ffprobe','-v','error','-show_streams','-show_format','-of','json',str(target)]));st=probe['streams'][0]
 if int(st['nb_frames'])!=len(ids) or st['avg_frame_rate']!=f'{fps}/1' or abs(float(probe['format']['duration'])-18)>.001:raise ValueError('Encoded chronology differs')
 subprocess.run(['/opt/homebrew/bin/ffmpeg','-nostdin','-v','error','-i',str(target),'-f','null','-'],check=True)
 (folder/'manifest.json').write_text(json.dumps({'frames':rows,'native_sources':sources,'fps':fps,'seconds':18,'full_decode':'PASS','video_sha256':sha(target),
  'processing':'Native frames at chronological217..648, no slow motion, interpolation or generated video','visual_gate':'NOT_RUN'},indent=2)+'\n')


if __name__=='__main__':main()
