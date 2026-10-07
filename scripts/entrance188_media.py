"""Review-only contact sheets and H264 of immutable native frames. No interpolation."""
import json
import hashlib
import subprocess
from pathlib import Path
from PIL import Image,ImageDraw,ImageOps

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'.runtime/art-direction/series01-facebuilder-trial-01/entrance188-motion07'


def main():
    frames=[OUT/('frame-%04d.png'%f) for f in range(217,361)]
    for start in range(0,144,12):
        group=frames[start:start+12];target=OUT/('review-%04d.png'%(217+start))
        if target.exists() or not all(p.exists() for p in group):continue
        sheet=Image.new('RGB',(864,1212),(240,240,240));draw=ImageDraw.Draw(sheet)
        for i,path in enumerate(group):
            with Image.open(path) as im:thumb=ImageOps.contain(im.convert('RGB'),(216,384))
            x=(i%4)*216;y=(i//4)*404;sheet.paste(thumb,(x,y));draw.text((x+5,y+385),path.stem,fill=(15,15,15))
        sheet.save(target)
    if not (OUT/'result.json').exists() or not all(p.exists() for p in frames):
        print('Complete contact sheets generated; sequence still incomplete');return
    target=OUT/'entrance-proof.mp4'
    if target.exists():raise ValueError('Preserve existing video')
    subprocess.run(['/opt/homebrew/bin/ffmpeg','-nostdin','-n','-hide_banner','-loglevel','error',
        '-framerate','24','-start_number','217','-i',str(OUT/'frame-%04d.png'),'-frames:v','144',
        '-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(target)],check=True)
    data={'fps':24,'frame_count':144,'duration_seconds':6,'processing':'Native frames, ordinary H264 encoding; no interpolation or generated video',
          'frames':[{'name':p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in frames],
          'video_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'visual_gate':'NOT_RUN'}
    (OUT/'media.json').write_text(json.dumps(data,indent=2)+'\n')
    print(target)


if __name__=='__main__':main()
