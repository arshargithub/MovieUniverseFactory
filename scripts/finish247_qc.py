"""Actual encoded checks for the audio/graphic-only finishing derivative."""
import json, subprocess, sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw
from finish247_refine import OUT, BASE, PREV, RATE, load, sha

def main():
    d=OUT/'qc01'; d.mkdir(exist_ok=False)
    video=OUT/'delivery01/pashtun-B-refined.mp4'
    captioned=OUT/'delivery01/pashtun-B-refined-captioned.mp4'
    probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(video)],text=True))
    v=next(x for x in probe['streams'] if x['codec_type']=='video')
    assert (v['width'],v['height'],v['nb_frames'],v['r_frame_rate'])==(1080,1920,'540','24/1')
    assert abs(float(probe['format']['duration'])-22.5)<.05
    for p in [video,captioned]:
        subprocess.run(['ffmpeg','-v','error','-i',str(p),'-f','null','-'],check=True)
    subprocess.run(['ffmpeg','-v','error','-i',str(video),'-vf','fps=2,scale=216:384','-fps_mode','vfr',str(d/'frame-%03d.png')],check=True)
    files=sorted(d.glob('frame-*.png'))
    for page in range(3):
        sheet=Image.new('RGB',(216*5,410*3),'#eeeeee');draw=ImageDraw.Draw(sheet)
        for i,p in enumerate(files[page*15:page*15+15]):
            x=i%5*216;y=i//5*410;sheet.paste(Image.open(p),(x,y));draw.text((x+5,y+386),f'{(page*15+i)/2:.1f}s',fill='black')
        sheet.save(d/f'chronology-{page+1}.jpg',quality=93)
    for frame in [90,92,96,120,144,180,198,203,204,234,282,539]:
        subprocess.run(['ffmpeg','-v','error','-i',str(video),'-vf',f'select=eq(n\\,{frame})','-frames:v','1',str(d/f'full-{frame:03d}.png')],check=True)
    subprocess.run(['ffmpeg','-v','error','-i',str(captioned),'-vf','select=eq(n\\,144)','-frames:v','1',str(d/'caption-144.png')],check=True)
    before=load(OUT/'audio01/hoof-before.wav');after=load(OUT/'audio01/hoof-after.wav')
    lift=[]
    for a,b in [(0,1.25),(1.5,6.68),(7,11.75),(11.75,22.5)]:
        i,j=round(a*RATE),round(b*RATE)
        lift.append({'interval':[a,b],'rms_lift_db':float(20*np.log10(np.sqrt(np.mean(after[i:j]**2))/np.sqrt(np.mean(before[i:j]**2))))})
    record={'probe':probe,'decode_pass':True,'hoof_lift':lift,'visual_evidence':{str(p.relative_to(OUT)):sha(p) for p in d.glob('*.png')},'contact_sheets':{p.name:sha(p) for p in d.glob('*.jpg')},'inspection':'PENDING_MANUAL','direct_audio_listening':'NOT_RUN'}
    (d/'checks.json').write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps({'hoof_lift':lift,'frames':v['nb_frames']}))

if __name__=='__main__':main()
