"""Assemble exact native blink replacement frames, preserving old evidence."""
import hashlib
import json
import shutil
import subprocess
from pathlib import Path
from entrance189_media import BASE,sheet

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
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
