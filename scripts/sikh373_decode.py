"""Verify encoded delivery profiles and actual decoded review images; not AV judgment."""
import json,subprocess
from pathlib import Path
from PIL import Image,ImageDraw
r=Path(__file__).resolve().parents[1];p=r/'.runtime/art-direction/sikh373-review-c80';out=p/'decoded';out.mkdir(exist_ok=True);profiles={}
for name,count in [('full-rear-with-landing',92),('landing-with-continuity',58),('landing-reference-comparison',78),('landing-comparison-three-repeats',234)]:
 v=json.loads(subprocess.check_output(['/opt/homebrew/bin/ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(p/(name+'.mp4'))]));s=v['streams'][0]
 assert int(s['nb_read_frames'])==count and s['r_frame_rate']=='24/1' and s['pix_fmt']=='yuv420p' and s['codec_name']=='h264' and abs(float(v['format']['duration'])-count/24)<.002
 assert len(v['streams'])==1;profiles[name]=v
for label,name,frames in [('candidate','full-rear-with-landing',[34,56,57,58,59,63,65,66,67,68,70,77,91]),('comparison','landing-reference-comparison',[0,57,63,67,70,77])]:
 filt='select='+'+'.join(f'eq(n\\,{n})' for n in frames)
 subprocess.run(['/opt/homebrew/bin/ffmpeg','-v','error','-i',str(p/(name+'.mp4')),'-vf',filt,'-vsync','0',str(out/(label+'-%02d.png'))],check=True)
 images=[Image.open(f).convert('RGB') for f in sorted(out.glob(label+'-*.png'))];assert len(images)==len(frames)
 cols=2;w=576 if label=='comparison' else 288;h=308 if label=='comparison' else 288;sheet=Image.new('RGB',(cols*w,((len(images)+1)//2)*(h+24)),(230,230,230));d=ImageDraw.Draw(sheet)
 for i,im in enumerate(images):
  im.thumbnail((w,h));x=i%cols*w;y=i//cols*(h+24);sheet.paste(im,(x,y));d.text((x+5,y+h+3),str(276+frames[i]),fill='black')
 sheet.save(out/(label+'-sheet.jpg'),quality=94)
(r/'results/sikh373/encoded-profile80.json').write_text(json.dumps(profiles,indent=2)+'\n');print('Profiles/framecounts and13candidate/6comparison decodecontrols verified; no playback/listening claim.')
