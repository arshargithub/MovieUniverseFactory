"""Verify source-bound reuse/actual frames and package unretimed crest proof."""
import json,sys,shutil,subprocess
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np
from movie_factory import production_knowledge as pk
r=Path(__file__).resolve().parents[1];o=r/'results/sikh372';action=sys.argv[1];cy=int(sys.argv[2]);out=r/f'.runtime/art-direction/sikh372-review-c{cy}';out.mkdir(parents=True,exist_ok=True)
def bind(p):return dict(path=str(p.relative_to(r)),sha256=pk.file_hash(p))
def write(p,v):
 t=json.dumps(v,indent=2)+'\n'
 if p.exists():assert p.read_text()==t
 else:p.write_text(t)
def entries(step,old=False):
 d=r/'results/sikh371' if old else o;cycle=71 if old else cy;run=json.loads((d/f'motion-c{cycle}-{step}-run.json').read_text());assert run['status']=='RETURNED';mf=r/run['artifacts']['frames']['path'];assert pk.file_hash(mf)==run['artifacts']['frames']['sha256'];rows=json.loads(mf.read_text())
 for row in rows:
  p=mf.parent/row['file'];assert pk.file_hash(p)==row['sha256'];row['binding']=bind(p)
 return rows
if action=='sheet':
 step=sys.argv[3];rows=entries(step)
 if step in ['phase01','phase02']:rows=[x for x in rows if x['frame']!=333]
 sheet=Image.new('RGB',(900,((len(rows)+2)//3)*326),(230,230,230));d=ImageDraw.Draw(sheet)
 for i,row in enumerate(rows):
  im=Image.open(r/row['binding']['path']).convert('RGB');im.thumbnail((300,300));x=i%3*300;y=i//3*326;sheet.paste(im,(x,y));d.text((x+7,y+305),f"{row['frame']} / {(row['frame']-276)/24:.3f}s",fill='black')
 p=out/f'{step}.jpg';sheet.save(p,quality=94);print(p)
elif action=='assemble':
 old=json.loads((r/'results/sikh371/media-manifest.json').read_text());frames={int(f):v for f,v in old['source_frames'].items() if int(f)<=314};assert set(frames)==set(range(276,315));metadata={}
 for step in ['accepted01','accepted02','accepted03']:
  for row in entries(step,True):
   if row['frame']<=314:metadata[row['frame']]=row
 assert set(metadata)==set(frames)
 for f,v in frames.items():assert pk.file_hash(r/v['path'])==v['sha256'] and metadata[f]['binding']==v
 prefix=entries('prefix');diffs={};camera=prefix[0]['camera_matrix']
 for row in prefix:
  assert np.allclose(camera,row['camera_matrix'],atol=1e-7)
  if row['frame']<=314:
   f=row['frame'];a=np.asarray(Image.open(r/frames[f]['path'])).astype(int);b=np.asarray(Image.open(r/row['binding']['path'])).astype(int);diffs[f]=int(np.max(np.abs(a-b)));assert diffs[f]==0
 assert set(diffs)=={276,306,314};assert all(np.allclose(camera,v['camera_matrix'],atol=1e-7) for v in metadata.values())
 canonical=[]
 for step in ['phase01','phase02','phase03']:
  for row in entries(step):
   assert np.allclose(camera,row['camera_matrix'],atol=1e-7)
   if row['frame']==333:canonical.append(row['binding'])
   if row['frame'] in frames:assert row['frame']==333
   else:frames[row['frame']]=row['binding']
 assert set(frames)==set(range(276,334));arr=[np.asarray(Image.open(r/v['path'])).astype(int) for v in canonical];cd=[int(np.max(np.abs(a-arr[0]))) for a in arr];assert max(cd)==0
 sequence=out/'frames';sequence.mkdir(exist_ok=True)
 for i,f in enumerate(range(276,334)):
  p=sequence/f'{i:04d}.png'
  if p.exists():assert pk.file_hash(p)==frames[f]['sha256']
  else:shutil.copy2(r/frames[f]['path'],p)
 clip=out/'preparation-rise-apex-hold.mp4';assert not clip.exists();subprocess.run(['/opt/homebrew/bin/ffmpeg','-v','error','-framerate','24','-i',str(sequence/'%04d.png'),'-frames:v','58','-an','-c:v','libx264','-crf','17','-pix_fmt','yuv420p','-movflags','+faststart',str(clip)],check=True)
 profile=json.loads(subprocess.check_output(['/opt/homebrew/bin/ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(clip)]));s=profile['streams'][0];assert int(s['nb_read_frames'])==58 and s['r_frame_rate']=='24/1' and s['pix_fmt']=='yuv420p';assert abs(float(profile['format']['duration'])-58/24)<.002
 write(o/f'media-manifest{cy}.json',dict(video=bind(clip),source_frames={str(f):v for f,v in sorted(frames.items())},reused_accepted_frames=39,new_frames=19,prefix_pixel_differences=diffs,canonical333_differences=cd,profile=profile,scope='Silent58unretimed24fpsframes;39acceptedprepimagesreusedonlyafterhash/source/camera/pixelchecks. No landing/fullspeed/artisticapproval.'));print(clip)
elif action=='comparison':
 old=json.loads((r/'results/sikh371/comparison-manifest.json').read_text());ref=r/old['reference_clip']['path'];assert pk.file_hash(ref)==old['reference_clip']['sha256'];clip=out/'preparation-rise-apex-hold.mp4';comparison=out/'apex-reference-comparison.mp4';assert clip.exists() and not comparison.exists()
 header=Image.new('RGB',(1152,40),(17,17,17));d=ImageDraw.Draw(header);font=ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc',19);d.text((12,9),'Reference: preparation to active crest',font=font,fill='white');d.text((588,9),'Current: accepted prep + rise / apex / hold',font=font,fill='white');header.save(out/'comparison-header.png')
 filt='[1:v]crop=400:500:130:0,scale=-2:576,pad=576:576:(ow-iw)/2:0:color=0x111111[horse];[0:v][horse]hstack=inputs=2,pad=1152:616:0:40:color=0x111111[base];[base][2:v]overlay=0:0:shortest=0[v]'
 subprocess.run(['/opt/homebrew/bin/ffmpeg','-v','error','-i',str(ref),'-i',str(clip),'-i',str(out/'comparison-header.png'),'-filter_complex',filt,'-map','[v]','-frames:v','58','-an','-c:v','libx264','-crf','17','-pix_fmt','yuv420p','-movflags','+faststart',str(comparison)],check=True)
 repeat=out/'apex-comparison-three-repeats.mp4';subprocess.run(['/opt/homebrew/bin/ffmpeg','-v','error','-stream_loop','2','-i',str(comparison),'-map','0:v','-frames:v','174','-an','-c:v','libx264','-crf','17','-pix_fmt','yuv420p','-movflags','+faststart',str(repeat)],check=True)
 write(o/f'comparison-manifest{cy}.json',dict(reference=old['reference'],reference_clip=bind(ref),reference_start_seconds=15,duration_seconds=58/24,candidate=bind(clip),candidate_display_crop=[130,0,400,500],comparison=bind(comparison),three_normal_speed_repeats=bind(repeat),scope='Bothnormal-time,24fps, no mirroring/interpolation/addedholds. Partialreferencecaptionsremain sourcecontent, notproductiontext. No directAV/productionapproval.'));print(repeat)
else:raise SystemExit('sheet CYCLE STEP | assemble CYCLE | comparison CYCLE')
