"""Assemble exact native blink replacement frames, preserving old evidence."""
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path
from entrance189_media import BASE,sheet

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    if sys.argv[1:] in (['--route-overview'],['--route-motion']):
        motion=sys.argv[1:]==['--route-motion']
        out=BASE/('entrance190-route-motion06' if motion else 'entrance190-route-overview05')
        # Landscape diagnostics use their own compact aspect-preserving sheet.
        from PIL import Image,ImageDraw,ImageOps
        paths=sorted(out.glob('frame-*.png'))
        count=12 if motion else 9
        columns=4 if motion else 3
        for start in range(0,len(paths),count):
            target=out/('sheet-%02d.png'%start)
            if target.exists():continue
            result=Image.new('RGB',(320*columns,780),(240,240,240));draw=ImageDraw.Draw(result)
            for j,p in enumerate(paths[start:start+count]):
                with Image.open(p) as im:thumb=ImageOps.contain(im.convert('RGB'),(320,240))
                x=j%columns*320;y=j//columns*260;result.paste(thumb,(x,y));draw.text((x+5,y+241),p.stem,fill=(10,10,10))
            result.save(target)
        if motion and len(paths)==192 and (out/'result.json').exists():
            target=out/'coarse-route.mp4'
            if not target.exists():
                subprocess.run(['/opt/homebrew/bin/ffmpeg','-nostdin','-n','-hide_banner','-loglevel','error','-framerate','24','-start_number','0','-i',str(out/'frame-%04d.png'),'-frames:v','192','-c:v','libx264','-crf','18','-pix_fmt','yuv420p',str(target)],check=True)
        return
    if sys.argv[1:]:raise ValueError('Unsupported media operation')
    old=BASE/'entrance189-decision-motion20'
    new=BASE/'entrance190-blink03'
    out=BASE/'entrance190-blink-review04'
    if out.exists():raise ValueError('Preserve review media')
    record=json.loads((new/'result.json').read_text())
    if digest(new/'scene.blend')!=record['native_sha256']:raise ValueError('Changed blink source')
    prior=json.loads((old/'media.json').read_text())
    for r in prior['frames']:
        if digest(old/r['name'])!=r['sha256']:raise ValueError('Changed reused frame')
    out.mkdir();rows=[]
    for f in range(289,337):
        # All affected integer samples310..314 are covered, with315 as an
        # unchanged boundary control. No synthetic image interpolation.
        p=(new if 310<=f<=315 else old)/('frame-%04d.png'%f)
        target=out/p.name;shutil.copy2(p,target)
        rows.append({'name':target.name,'sha256':digest(target),'source':str(p.relative_to(BASE))})
    sheet([out/('frame-%04d.png'%f) for f in range(309,316)],out/'blink-sheet.png',columns=4)
    target=out/'decision-proof.mp4'
    subprocess.run(['/opt/homebrew/bin/ffmpeg','-nostdin','-n','-hide_banner','-loglevel','error','-framerate','24','-start_number','289','-i',str(out/'frame-%04d.png'),'-frames:v','48','-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(target)],check=True)
    (out/'media.json').write_text(json.dumps({'source_sha256':record['native_sha256'],'frames':rows,'fps':24,'frame_count':48,'duration_seconds':2,'video_sha256':digest(target),'visual_gate':'NOT_RUN','reuse':'Unchanged prior frames outside blink interval; exact native replacements inside'},indent=2)+'\n')

if __name__=='__main__':main()
