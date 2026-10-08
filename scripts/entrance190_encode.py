"""Exact-frame review sheets and encoding; no interpolation or synthesis."""
import argparse
import json
import subprocess
from pathlib import Path
from entrance189_media import BASE,sheet
from entrance189_edit import digest

def main():
    p=argparse.ArgumentParser();p.add_argument('coverage',choices=['motion','geography']);args=p.parse_args()
    first,last,folder=(361,553,'entrance190-motion30') if args.coverage=='motion' else (0,48,'entrance190-geography23')
    out=BASE/folder;paths=[out/('frame-%04d.png'%i) for i in range(first,last)]
    for i in range(0,len(paths),12):
        group=paths[i:i+12]
        if all(p.exists() for p in group):sheet(group,out/('review-%04d.png'%(first+i)))
    if not (out/'result.json').exists() or not all(p.exists() for p in paths):
        print('Complete available frame groups laid out; native sequence still running');return
    target=out/(args.coverage+'-proof.mp4')
    if target.exists():raise ValueError('Preserve prior video')
    subprocess.run(['/opt/homebrew/bin/ffmpeg','-nostdin','-n','-hide_banner','-loglevel','error','-framerate','24','-start_number',str(first),'-i',str(out/'frame-%04d.png'),'-frames:v',str(last-first),'-an','-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(target)],check=True)
    subprocess.run(['/opt/homebrew/bin/ffmpeg','-nostdin','-v','error','-i',str(target),'-f','null','-'],check=True)
    r=json.loads((out/'result.json').read_text())
    (out/'media.json').write_text(json.dumps({'source_sha256':r['source_sha256'],'fps':24,'frame_count':last-first,'duration_seconds':(last-first)/24,'frames':[{'name':p.name,'sha256':digest(p)} for p in paths],'video_sha256':digest(target),'video':target.name,'processing':'Exact native frames, H264 only; full decode verified','visual_gate':'NOT_RUN'},indent=2)+'\n')

if __name__=='__main__':main()
