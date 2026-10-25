"""Decode review samples and verify actual media profile; no AV judgment."""
import json,subprocess
from pathlib import Path
from PIL import Image,ImageDraw
r=Path(__file__).resolve().parents[1];p=r/'.runtime/art-direction/sikh372-review-c75';out=p/'decoded';out.mkdir(exist_ok=True)
for label,name,frames in [('candidate','preparation-rise-apex-hold',[0,27,37,38,39,43,47,52,57]),('comparison','apex-reference-comparison',[0,38,43,47,57])]:
 filt='select='+'+'.join(f'eq(n\\,{n})' for n in frames)
 subprocess.run(['/opt/homebrew/bin/ffmpeg','-v','error','-i',str(p/(name+'.mp4')),'-vf',filt,'-vsync','0',str(out/(label+'-%02d.png'))],check=True)
 images=[Image.open(f).convert('RGB') for f in sorted(out.glob(label+'-*.png'))];assert len(images)==len(frames)
 w,h=images[0].size;sheet=Image.new('RGB',(2*w,((len(images)+1)//2)*(h+24)),(230,230,230));d=ImageDraw.Draw(sheet)
 for i,im in enumerate(images):
  x=(i%2)*w;y=(i//2)*(h+24);sheet.paste(im,(x,y));d.text((x+6,y+h+4),f'Encoded sourceframe {276+frames[i]}',fill='black')
 sheet.save(out/(label+'-sheet.jpg'),quality=94)
profiles={}
for name,count,duration in [('preparation-rise-apex-hold',58,58/24),('apex-comparison-three-repeats',174,174/24)]:
 v=json.loads(subprocess.check_output(['/opt/homebrew/bin/ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(p/(name+'.mp4'))]));s=v['streams'][0]
 assert int(s['nb_read_frames'])==count and s['r_frame_rate']=='24/1' and s['pix_fmt']=='yuv420p' and abs(float(v['format']['duration'])-duration)<.002
 profiles[name]=v
f=r/'results/sikh372/encoded-profile75.json';assert not f.exists();f.write_text(json.dumps(profiles,indent=2)+'\n')
print('Actual9candidate/5comparison decode samples and58/174frame profiles verified; no playback/listening assertion.')
