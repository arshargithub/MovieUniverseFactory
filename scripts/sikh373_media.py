"""Source/pixel/camera verified reuse and original-speed landing review packaging."""
import json,sys,shutil,subprocess
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import numpy as np
from movie_factory import production_knowledge as pk
r=Path(__file__).resolve().parents[1];o=r/'results/sikh373';out=r/'.runtime/art-direction/sikh373-review-c80';out.mkdir(parents=True,exist_ok=True);action=sys.argv[1]
def bind(p):return dict(path=str(p.relative_to(r)),sha256=pk.file_hash(p))
def write(p,v):
 text=json.dumps(v,indent=2)+'\n'
 if p.exists():assert p.read_text()==text
 else:p.write_text(text)
def entries(step):
 run=json.loads((o/f'motion-c80-{step}-run.json').read_text());assert run['status']=='RETURNED';mf=r/run['artifacts']['frames']['path'];assert pk.file_hash(mf)==run['artifacts']['frames']['sha256'];rows=json.loads(mf.read_text())
 for row in rows:
  p=mf.parent/row['file'];assert pk.file_hash(p)==row['sha256'];row['binding']=bind(p)
 return rows
if action=='sheet':
 step=sys.argv[2];rows=entries(step)
 if step.startswith('phase'):rows=[x for x in rows if x['frame']!=367 or step=='phase03']
 cols=3;sheet=Image.new('RGB',(900,((len(rows)+cols-1)//cols)*326),(230,230,230));d=ImageDraw.Draw(sheet)
 for i,row in enumerate(rows):
  im=Image.open(r/row['binding']['path']).convert('RGB');im.thumbnail((300,300));x=i%cols*300;y=i//cols*326;sheet.paste(im,(x,y));d.text((x+7,y+305),f"{row['frame']}",fill='black')
 target=out/f'{step}.jpg';sheet.save(target,quality=94);print(target)
elif action=='assemble':
 old=json.loads((r/'results/sikh372/media-manifest75.json').read_text());frames={int(f):v for f,v in old['source_frames'].items()};assert set(frames)==set(range(276,334))
 for f,v in frames.items():assert pk.file_hash(r/v['path'])==v['sha256']
 prefix=entries('prefix');camera=prefix[0]['camera_matrix'];diffs={}
 for row in prefix:
  assert np.allclose(camera,row['camera_matrix'],atol=1e-7)
  f=row['frame']
  if f<=333:
   a=np.asarray(Image.open(r/frames[f]['path'])).astype(int);b=np.asarray(Image.open(r/row['binding']['path'])).astype(int);diffs[f]=int(np.max(np.abs(a-b)));assert diffs[f]==0,(f,diffs[f])
 assert set(diffs)=={306,314,333}
 canonical=[]
 for step in ['phase01','phase02','phase03']:
  for row in entries(step):
   assert np.allclose(camera,row['camera_matrix'],atol=1e-7)
   if row['frame']==367:canonical.append(row['binding'])
   if row['frame'] in frames:assert row['frame']==367
   else:frames[row['frame']]=row['binding']
 assert set(frames)==set(range(276,368))
 arrays=[np.asarray(Image.open(r/v['path'])).astype(int) for v in canonical];cd=[int(np.max(np.abs(a-arrays[0]))) for a in arrays];assert max(cd)==0
 sequence=out/'frames';sequence.mkdir(exist_ok=True)
 for i,f in enumerate(range(276,368)):
  target=sequence/f'{i:04d}.png'
  if target.exists():assert pk.file_hash(target)==frames[f]['sha256']
  else:shutil.copy2(r/frames[f]['path'],target)
 videos={}
 for name,start,count in [('full-rear-with-landing',0,92),('landing-with-continuity',34,58)]:
  clip=out/(name+'.mp4');assert not clip.exists();subprocess.run(['/opt/homebrew/bin/ffmpeg','-v','error','-framerate','24','-start_number',str(start),'-i',str(sequence/'%04d.png'),'-frames:v',str(count),'-an','-c:v','libx264','-crf','17','-pix_fmt','yuv420p','-movflags','+faststart',str(clip)],check=True);videos[name]=bind(clip)
 write(o/'media-manifest80.json',dict(videos=videos,source_frames={str(f):v for f,v in sorted(frames.items())},reused_accepted_frames=58,new_frames=34,prefix_pixel_differences=diffs,canonical367_differences=cd,scope='Silentoriginal24fps; full92frames andfocused58frames. Approvedprefixreuseonlyafteractualpose/action/geometry/sourceandfreshpixelcontrols. No directAV/appearance/FX/fullsequenceapproval.'));print(videos)
elif action=='comparison':
 ref=r/'.runtime/art-direction/series01-sikh256/references/reference-b.mov';assert pk.file_hash(ref)=='78d0d691e8712c02931876cf0bc405e4869de357f337f531708be7a7da4898e2'
 reference=out/'reference-rear-landing.mp4';comparison=out/'landing-reference-comparison.mp4';repeat=out/'landing-comparison-three-repeats.mp4';clip=out/'full-rear-with-landing.mp4'
 # Both originalspeed; align the landing phases, preserve sourcecut and avoid
 # nextmotorcycle shot. Fullcandidatecontinuity remains separatelyavailable.
 subprocess.run(['/opt/homebrew/bin/ffmpeg','-v','error','-ss','15.4','-i',str(ref),'-t','3.25','-vf','crop=400:300:140:350,scale=576:-2,pad=576:576:0:(oh-ih)/2:color=0x111111,fps=24','-an','-c:v','libx264','-crf','17','-pix_fmt','yuv420p',str(reference)],check=True)
 header=Image.new('RGB',(1152,40),(17,17,17));d=ImageDraw.Draw(header);font=ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc',19);d.text((12,9),'Reference | original speed',font=font,fill='white');d.text((588,9),'Current | approved rear + new landing',font=font,fill='white');header.save(out/'comparison-header.png')
 filt='[1:v]crop=450:500:85:0,scale=-2:576,pad=576:576:(ow-iw)/2:0:color=0x111111[horse];[0:v][horse]hstack=inputs=2,pad=1152:616:0:40:color=0x111111[base];[base][2:v]overlay=0:0:shortest=0[v]'
 subprocess.run(['/opt/homebrew/bin/ffmpeg','-v','error','-i',str(reference),'-i',str(clip),'-i',str(out/'comparison-header.png'),'-filter_complex',filt,'-map','[v]','-frames:v','78','-an','-c:v','libx264','-crf','17','-pix_fmt','yuv420p','-movflags','+faststart',str(comparison)],check=True)
 subprocess.run(['/opt/homebrew/bin/ffmpeg','-v','error','-stream_loop','2','-i',str(comparison),'-frames:v','234','-an','-c:v','libx264','-crf','17','-pix_fmt','yuv420p','-movflags','+faststart',str(repeat)],check=True)
 write(o/'comparison-manifest80.json',dict(reference=bind(ref),reference_clip=bind(reference),reference_interval=[15.4,18.65],comparison=bind(comparison),three_normal_speed_repeats=bind(repeat),candidate_interval=[276,353],scope='Normal-time originals, no mirroring/timewarp/addedholds. Sourcecropfordisplayonly. Comparisonendsbefore referenceshotcut; fullcandidate367settlinghandle separatelyavailable. No directAVjudgment.'));print(repeat)
else:raise SystemExit('sheet STEP | assemble | comparison')
