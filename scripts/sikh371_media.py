"""Verify admitted image receipts and package unretimed371 micro-motion proof.
No native authoring, interpolation, artistic verdict or provider call.
"""
import json,sys,shutil,subprocess
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np
from movie_factory import production_knowledge as pk
r=Path(__file__).resolve().parents[1];o=r/'results/sikh371';out=r/'.runtime/art-direction/sikh371-review-c71';out.mkdir(parents=True,exist_ok=True)
def bind(p):return dict(path=str(p.relative_to(r)),sha256=pk.file_hash(p))
def write(p,v):
 text=json.dumps(v,indent=2)+'\n'
 if p.exists():assert p.read_text()==text
 else:p.write_text(text)
def entries(step):
 run=json.loads((o/f'motion-c71-{step}-run.json').read_text());assert run['status']=='RETURNED'
 mf=r/run['artifacts']['frames']['path'];assert pk.file_hash(mf)==run['artifacts']['frames']['sha256'];rows=json.loads(mf.read_text())
 for row in rows:
  p=mf.parent/row['file'];assert pk.file_hash(p)==row['sha256'];row['binding']=bind(p)
 return rows
if sys.argv[1]=='sheet':
 step=sys.argv[2];rows=entries(step)
 if step.startswith('accepted'):rows=[x for x in rows if x['frame']!=333]
 if step in ['phase01','phase02']:rows=[x for x in rows if x['frame']!=333]
 sheet=Image.new('RGB',(3*300,((len(rows)+2)//3)*326),(230,230,230));d=ImageDraw.Draw(sheet)
 for i,row in enumerate(rows):
  im=Image.open(r/row['binding']['path']).convert('RGB');im.thumbnail((300,300));x=i%3*300;y=i//3*326;sheet.paste(im,(x,y));d.text((x+7,y+305),f"{row['frame']} / {(row['frame']-276)/24:.3f}s",fill=(0,0,0))
 p=out/f'{step}.jpg';sheet.save(p,quality=94);print(p)
elif sys.argv[1]=='assemble':
 frames={};canonical=[];camera=[]
 for step in ['accepted01','accepted02','accepted03','phase01','phase02','phase03']:
  for row in entries(step):
   camera.append(row['camera_matrix'])
   if row['frame']==333:canonical.append(row['binding'])
   if row['frame'] in frames:assert frames[row['frame']]==row['binding'] or row['frame']==333
   else:frames[row['frame']]=row['binding']
 assert set(frames)==set(range(276,334));assert all(np.allclose(camera[0],m,atol=1e-7) for m in camera)
 arrays=[np.asarray(Image.open(r/x['path'])) for x in canonical];diffs=[int(np.max(np.abs(a.astype(int)-arrays[0].astype(int)))) for a in arrays];assert max(diffs)==0
 sequence=out/'frames';sequence.mkdir(exist_ok=True)
 for i,f in enumerate(range(276,334)):
  p=sequence/f'{i:04d}.png'
  if p.exists():assert pk.file_hash(p)==frames[f]['sha256']
  else:shutil.copy2(r/frames[f]['path'],p)
 clip=out/'preparation-rise-apex-hold.mp4';assert not clip.exists()
 subprocess.run(['/opt/homebrew/bin/ffmpeg','-v','error','-framerate','24','-i',str(sequence/'%04d.png'),'-frames:v','58','-an','-c:v','libx264','-crf','17','-pix_fmt','yuv420p','-movflags','+faststart',str(clip)],check=True)
 profile=json.loads(subprocess.check_output(['/opt/homebrew/bin/ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(clip)]));s=profile['streams'][0];assert int(s['nb_read_frames'])==58 and s['r_frame_rate']=='24/1' and s['pix_fmt']=='yuv420p';assert abs(float(profile['format']['duration'])-58/24)<.002
 write(o/'media-manifest.json',dict(video=bind(clip),source_frames={str(f):frames[f] for f in sorted(frames)},canonical333=canonical,max_channel_differences=diffs,profile=profile,scope='Silent58frames276..333 unretimed24fps; acceptedpreparation rerendered in samefixedview, followedby19newrise/crestframes. No landing/finalappearance/audio/AVapproval.'));print(clip)
elif sys.argv[1]=='comparison':
 reference=r/'.runtime/art-direction/series01-sikh256/references/reference-b.mov';assert pk.file_hash(reference)=='78d0d691e8712c02931876cf0bc405e4869de357f337f531708be7a7da4898e2'
 clip=out/'preparation-rise-apex-hold.mp4';refclip=out/'reference-preparation-apex.mp4';comparison=out/'apex-reference-comparison.mp4';assert clip.exists() and not refclip.exists() and not comparison.exists()
 subprocess.run(['/opt/homebrew/bin/ffmpeg','-v','error','-ss','15','-i',str(reference),'-t',str(58/24),'-an','-vf','crop=350:328:190:338,scale=576:-2,pad=576:576:(ow-iw)/2:(oh-ih)/2:color=0x111111,fps=24','-frames:v','58','-c:v','libx264','-crf','17','-pix_fmt','yuv420p','-movflags','+faststart',str(refclip)],check=True)
 header=Image.new('RGB',(1152,40),(17,17,17));d=ImageDraw.Draw(header);font=ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc',19);d.text((12,9),'Reference: preparation to active crest',font=font,fill='white');d.text((588,9),'Candidate: accepted prep + rise / apex / hold',font=font,fill='white');header.save(out/'comparison-header.png')
 filt='[1:v]crop=400:470:130:20,scale=-2:576,pad=576:576:(ow-iw)/2:0:color=0x111111[horse];[0:v][horse]hstack=inputs=2,pad=1152:616:0:40:color=0x111111[base];[base][2:v]overlay=0:0:shortest=0[v]'
 subprocess.run(['/opt/homebrew/bin/ffmpeg','-v','error','-i',str(refclip),'-i',str(clip),'-i',str(out/'comparison-header.png'),'-filter_complex',filt,'-map','[v]','-frames:v','58','-an','-c:v','libx264','-crf','17','-pix_fmt','yuv420p','-movflags','+faststart',str(comparison)],check=True)
 repeats=out/'apex-comparison-three-repeats.mp4';subprocess.run(['/opt/homebrew/bin/ffmpeg','-v','error','-stream_loop','2','-i',str(comparison),'-map','0:v','-frames:v','174','-an','-c:v','libx264','-crf','17','-pix_fmt','yuv420p','-movflags','+faststart',str(repeats)],check=True)
 write(o/'comparison-manifest.json',dict(reference=bind(reference),reference_crop=[190,338,350,328],candidate_display_crop=[130,20,400,470],reference_start_seconds=15,duration_seconds=58/24,reference_clip=bind(refclip),candidate=bind(clip),comparison=bind(comparison),three_normal_speed_repeats=bind(repeats),scope='Private diagnostic comparison, both normal-time24fps, three repeats without timewarp/interpolation/addedholds. Reference30fps resampled to24fps, sourcecaptions excluded, no mirroring. Landing/appearance/audio/AVapproval excluded.'));print(repeats)
else:raise SystemExit('sheet STEP | assemble | comparison')
