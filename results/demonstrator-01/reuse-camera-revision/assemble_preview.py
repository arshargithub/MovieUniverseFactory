"""Present complete receipt-bound camera frames using the accepted player pattern."""
from pathlib import Path
import json,hashlib,os,subprocess
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[3]
R=ROOT/'results/demonstrator-01/reuse-camera-revision';RUN=ROOT/'runs/demonstrator-01/reuse-01/revision';OUT=ROOT/'runs/demonstrator-01/reuse-camera-continuous-review'
r=json.loads((RUN/'reuse.json').read_text());job=json.loads((R/'request.json').read_text());p=job['profile']
assert r['profile']==p and r['protected_before']==r['protected_after'] and r['protected_reopen']
assert json.loads((RUN/'runner-status.json').read_text())['ok']
assert r['source_sha256']==p['source_sha256']
assert hashlib.sha256((RUN/'scene.blend').read_bytes()).hexdigest()==r['scene_sha256']
assert sorted(x['frame'] for x in r['frames'])==list(range(p['start'],p['start']+p['duration_frames']))
OUT.mkdir(exist_ok=True);(OUT/'frames').mkdir(exist_ok=True)
rows=[]
for local,frame in enumerate(range(p['start'],p['start']+p['duration_frames'])):
 src=RUN/f'frame_{frame:04d}.png'
 with Image.open(src) as im:assert im.size==(640,360);im.verify()
 link=OUT/'frames'/f'{local:04d}.png'
 if link.is_symlink():assert link.resolve()==src.resolve()
 else:assert not link.exists();link.symlink_to(os.path.relpath(src,link.parent))
 rows.append({'preview_frame':local,'global_frame':frame,'path':str(src.relative_to(ROOT)),'sha256':hashlib.sha256(src.read_bytes()).hexdigest()})
subprocess.run(['/opt/homebrew/bin/ffmpeg','-hide_banner','-loglevel','warning','-n','-framerate','24','-start_number','0','-i',str(OUT/'frames/%04d.png'),'-frames:v','120','-an','-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(OUT/'camera-preview.mp4')],check=True)
probe=json.loads(subprocess.check_output(['/opt/homebrew/bin/ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(OUT/'camera-preview.mp4')]))
v=probe['streams'][0];assert int(v['nb_read_frames'])==120 and v['r_frame_rate']=='24/1' and abs(float(v['duration'])-5)<.001
(R/'media-probe.json').write_text(json.dumps(probe,indent=2)+'\n')
(R/'frame-inventory.json').write_text(json.dumps({'scene_sha256':r['scene_sha256'],'source_sha256':r['source_sha256'],'frames':rows,'adjacent_identical_frames':[a['preview_frame'] for a,b in zip(rows,rows[1:]) if a['sha256']==b['sha256']]},indent=2)+'\n')
html=(ROOT/'results/demonstrator-01/rough-cut/review-template.html').read_text()
html=html.replace('The Courier — 24-second rough cut','The Courier — five-second camera preview').replace('DEMONSTRATOR 01 · DEVELOPMENT ROUGH CUT · DIRECTOR REVIEW','DEMONSTRATOR 01 · CAMERA-ONLY PREVIEW · DIRECTOR REVIEW').replace('<h1>The Courier</h1>','<h1>One continuous camera move</h1>')
a=html.index('<p>A continuous gallop');b=html.index('</p>',a)+4
html=html[:a]+'<p>Your five-second camera move using the accepted horse, rider and world. Centered high rear view, a slower continuous descent past the right side, gentle approach, then offset frontal tracking. 5 seconds · 24 fps · 640 × 360 · silent preview.</p>'+html[b:]
html=html.replace('../cut-world-v4/preflight/shot2_f0220.png','frames/0000.png').replace('the-courier-24s.mp4','camera-preview.mp4').replace('575','119')
html=html.replace('Sound can be muted using the video controls.','Preview frame 0 corresponds to global scene frame 144. This preview is silent.')
a=html.index('<div class="beats">');b=html.index('<h2>',a)
html=html[:a]+'''<div class="beats"><div><b>0–2.75s</b><br>Slower rear-to-side descent</div><div><b>2.75–3.5s</b><br>Move closer while turning</div><div><b>3.5–5s</b><br>Flow into the front view</div><div><b>No middle hold</b><br>Continuous camera travel</div></div>'''+html[b:]
a=html.index('<h2>');b=html.index('</main>',a)
html=html[:a]+'''<h2>Review the camera move</h2><p>Does the opening feel high enough and centered behind the horse? Does the side view feel dynamic and flow naturally into the next view? Does the ending settle into the requested offset front view? Does this now feel like one seamless move rather than separate phases? Please note roughly how long your review took.</p><p>The rider motion, gallop speed, dust and scenery are unchanged. Their requested improvements, the halt/rear and dismount are captured for a later production experiment.</p><details><summary>Evidence</summary><p>This revision adds continuous interior camera velocity following Director feedback; it is a further disclosed code intervention. It is code-assisted reuse, not a parameter-only held-out pass. Source scene and noncamera mesh/identity/animation fingerprints are checked through save/reopen.</p><a href="contact-sheet.jpg">Contact sheet</a> · <a href="camera-preview.mp4" download>Download MP4</a> · <a href="../../../results/demonstrator-01/reuse-camera-revision/REPORT.md">Technical record</a></details>'''+html[b:]
a=html.index('<div class="beats">');b=html.index('<h2>',a);html=html[:a]+html[b:]
(OUT/'review.html').write_text(html)
board=Image.new('RGB',(960,590),(16,23,21));draw=ImageDraw.Draw(board)
for i,local in enumerate([0,20,41,60,90,119]):
 x=i%3*320;y=i//3*295
 with Image.open(OUT/'frames'/f'{local:04d}.png') as im:board.paste(im.resize((320,180)),(x,y))
 draw.text((x+6,y+187),f'{local/24:.2f}s / frame {local}',fill='white')
board.save(OUT/'contact-sheet.jpg',quality=90)
print(json.dumps({'review':str(OUT/'review.html'),'frames':120,'duration_seconds':5}))
