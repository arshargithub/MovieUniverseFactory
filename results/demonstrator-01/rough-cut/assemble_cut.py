"""Assemble only complete, receipt-bound final frames; preserve original files."""
from pathlib import Path
import hashlib,json,os,subprocess
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[3];BASE=ROOT/'runs/demonstrator-01';OUT=BASE/'cut-review';RESULT=ROOT/'results/demonstrator-01/rough-cut'
receipt=json.loads((RESULT/'scene-receipt.json').read_text());sha=receipt['scene_sha256'];frames={}
for folder in sorted(BASE.glob('cut-frames-shot*-*-*')):
 record=folder/'render.json'
 if not record.exists():continue
 r=json.loads(record.read_text())
 if r['scene_sha256']!=sha:continue
 for f in range(r['start'],r['end']):
  p=folder/f'frame_{f:04d}.png'
  if f in frames:raise ValueError(f'Duplicate frame {f}')
  if not p.is_file():raise ValueError(f'Missing frame {f}')
  frames[f]=p
scene_dir=Path(receipt['scene_path']).parent
for f,shot in [(143,'shot1'),(575,'shot4')]:
 if f in frames:raise ValueError('Unexpected duplicate extreme frame')
 frames[f]=scene_dir/'preflight'/f'{shot}_f{f:04d}.png'
if set(frames)!=set(range(576)):raise ValueError(f'Incomplete: {len(frames)} / 576')
OUT.mkdir(exist_ok=True);sequence=OUT/'frames';sequence.mkdir(exist_ok=True)
records=[]
for f,p in sorted(frames.items()):
 with Image.open(p) as im:
  if im.size!=(960,540):raise ValueError('Incorrect frame size')
 target=sequence/f'{f:04d}.png'
 if target.is_symlink():
  if target.resolve()!=p.resolve():raise ValueError('Conflicting frame link')
 elif target.exists():raise ValueError('Existing frame file')
 else:target.symlink_to(os.path.relpath(p,sequence))
 records.append({'frame':f,'path':str(p.relative_to(ROOT)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size})
subprocess.run(['/opt/homebrew/bin/ffmpeg','-hide_banner','-loglevel','warning','-n','-framerate','24','-start_number','0','-i',str(sequence/'%04d.png'),'-i',str(OUT/'temp-sound.wav'),'-map','0:v:0','-map','1:a:0','-frames:v','576','-c:v','libx264','-preset','medium','-crf','18','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k','-af','afade=t=in:d=0.03,afade=t=out:st=23.8:d=0.2','-t','24','-movflags','+faststart',str(OUT/'the-courier-24s.mp4')],check=True)
probe=json.loads(subprocess.check_output(['/opt/homebrew/bin/ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(OUT/'the-courier-24s.mp4')]))
v=next(s for s in probe['streams'] if s['codec_type']=='video');a=next(s for s in probe['streams'] if s['codec_type']=='audio')
if int(v['nb_read_frames'])!=576 or v['r_frame_rate']!='24/1' or abs(float(v['duration'])-24)>.001:raise ValueError('Encoded video timing mismatch')
if abs(float(a['duration'])-24)>.1:raise ValueError('Audio duration mismatch')
(RESULT/'media-probe.json').write_text(json.dumps(probe,indent=2)+'\n')
(RESULT/'frame-inventory.json').write_text(json.dumps({'scene_sha256':sha,'frames':records,'adjacent_identical_pngs':[a['frame'] for a,b in zip(records,records[1:]) if a['sha256']==b['sha256']]},indent=2)+'\n')
# Whole film contact sheets, one sample each second. Supplemental to playback.
board=Image.new('RGB',(1440,620));draw=ImageDraw.Draw(board)
for i,f in enumerate(range(12,576,24)):
 x=i%6*240;y=i//6*155;board.paste(Image.open(frames[f]).resize((240,135)),(x,y));draw.text((x+4,y+137),f'{f/24:.1f}s / frame {f}',fill='white')
board.save(OUT/'contact-sheet.jpg',quality=92)
print(json.dumps({'video':str(OUT/'the-courier-24s.mp4'),'frames':576,'seconds':24,'audio':'original provisional synthesis'}))
