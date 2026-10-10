"""Native sequence review/encoding, retaining exact image and edit provenance."""
import argparse,json,os,subprocess
from pathlib import Path
from entrance189_media import sheet
from entrance193_media import sha,pixel_parity
from entrance204_story import shot_frame
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'.runtime/art-direction/series01-facebuilder-trial-01';OUT=ROOT/'.runtime/art-direction/series01-entrance204'
PARTS=('opening08','recognition09','route10','opening14','recognition15','route16')
def frames():
 found={}
 for part in PARTS:
  folder=BASE/('entrance204-'+part)
  for p in sorted(folder.glob('frame-*.png')):
   index=int(p.stem[6:])
   if index in found:raise ValueError('Duplicate frame')
   found[index]=p
 return found
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--encode',choices=('internal','final'));parser.add_argument('--verify',action='store_true');args=parser.parse_args();available=frames();OUT.mkdir(exist_ok=True);qa=OUT/'qa';qa.mkdir(exist_ok=True)
 for parity in ('even','all'):
  step=2 if parity=='even' else 1
  for first in range(0,432,12*step):
   ids=list(range(first,min(first+12*step,432),step))
   if all(i in available for i in ids):sheet([available[i] for i in ids],qa/f'{parity}-{first:04d}.png')
 if args.verify:
  rows=[]
  for kind,part,verification in [('opening','opening08','openverify11'),('recognition','recognition09','recognitionverify12'),('route','route10','routeverify13')]:
   actual=json.loads((BASE/('entrance204-'+part)/'result.json').read_text());other=json.loads((BASE/('entrance204-'+verification)/'result.json').read_text())
   if any(actual[k]!=other[k] for k in ('source_sha256','fingerprint','cache_hashes','resolution','samples','persistent_data')):raise ValueError('Fresh-open state differs')
   lookup={}
   for name in PARTS:
    p=BASE/('entrance204-'+name)/'result.json'
    if p.exists():lookup.update({r['frame']:r for r in json.loads(p.read_text())['frames']})
   import numpy as np
   for row in other['frames']:
    f=row['frame'];prior=lookup[f]
    if prior['source_frame']!=row['source_frame'] or prior['shot']!=row['shot']:raise ValueError('Edit clock differs')
    error=max(float(abs(np.array(prior['pose'][n])-row['pose'][n]).max()) for n in row['pose'])
    if error>2e-5:raise ValueError('Fresh-open pose differs')
    rows.append({'frame':f,'pose_error':error,**pixel_parity(available[f],BASE/('entrance204-'+verification)/f'frame-{f:04d}.png')})
  (qa/'reopen.json').write_text(json.dumps({'status':'PASS','samples':rows,'scope':'Independent source/structure/cache hash, pose and one-channel-level pixel controls; not visual acceptance'},indent=2)+'\n')
 if not args.encode:return
 final=args.encode=='final';ids=list(range(432)) if final else list(range(0,432,2));fps=24 if final else 12
 if not all(i in available for i in ids):raise ValueError('Incomplete full chronology')
 recorded={};sources={}
 for part in PARTS if final else PARTS[:3]:
  record=json.loads((BASE/('entrance204-'+part)/'result.json').read_text());kind=record['kind']
  if kind in sources and sources[kind]!=record['source_sha256']:raise ValueError('Interleaved native source differs')
  sources[kind]=record['source_sha256']
  for row in record['frames']:recorded[row['frame']]=row
 for i in ids:
  row=recorded[i];_,shot,f=shot_frame(i)
  if sha(available[i])!=row['sha256'] or row['source_frame']!=f or row['shot']!=shot:raise ValueError('Frame/source clock changed')
 folder=OUT/('director-preview' if final else 'internal-motion')
 if folder.exists():raise ValueError('Preserve existing proof')
 folder.mkdir();rows=[]
 for j,i in enumerate(ids):
  path=available[i];os.link(path,folder/f'frame-{j:04d}.png');kind,shot,f=shot_frame(i);rows.append({'edit_frame':i,'source_frame':f,'kind':kind,'shot':shot,'path':str(path.relative_to(ROOT)),'sha256':sha(path)})
 target=folder/'pashtun-complete-entrance.mp4'
 subprocess.run(['/opt/homebrew/bin/ffmpeg','-nostdin','-n','-v','error','-framerate',str(fps),'-i',str(folder/'frame-%04d.png'),'-frames:v',str(len(ids)),'-c:v','libx264','-crf','16','-pix_fmt','yuv420p','-movflags','+faststart',str(target)],check=True)
 probe=json.loads(subprocess.check_output(['/opt/homebrew/bin/ffprobe','-v','error','-show_streams','-show_format','-of','json',str(target)]));st=probe['streams'][0]
 if int(st['nb_frames'])!=len(ids) or st['avg_frame_rate']!=f'{fps}/1' or abs(float(probe['format']['duration'])-18)>.001:raise ValueError('Encoded clock differs')
 subprocess.run(['/opt/homebrew/bin/ffmpeg','-nostdin','-v','error','-i',str(target),'-f','null','-'],check=True)
 (folder/'manifest.json').write_text(json.dumps({'frames':rows,'native_sources':sources,'frame_count':len(ids),'fps':fps,'seconds':18,'video_sha256':sha(target),'full_decode':'PASS','visual_gate':'NOT_RUN','scope':'Complete silent choreography preview; final motion-dependent finish and release render remain separate','processing':'Native frames with shared evaluated source clock, ordinary H264, no image interpolation or generated video'},indent=2)+'\n')
if __name__=='__main__':main()
