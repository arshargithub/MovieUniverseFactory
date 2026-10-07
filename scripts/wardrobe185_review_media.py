"""Lossless-source contact sheets and ordinary encoding of native proof frames.

No generative processing, frame interpolation or automatic visual acceptance.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
from PIL import Image,ImageDraw,ImageOps

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'.runtime/art-direction/series01-facebuilder-trial-01'


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--final',action='store_true')
    parser.add_argument('--recut',action='store_true')
    parser.add_argument('--correction186',action='store_true');args=parser.parse_args()
    out=BASE/('wardrobe186-motion06' if args.correction186 else 'wardrobe185-shotmotion03' if args.recut else 'wardrobe185-shotmotion02')
    names=[out/('frame-%04d.png'%f) for f in range(217,361)]
    if args.final and (not all(p.is_file() for p in names) or not (out/'motion-render.json').is_file()):
        raise ValueError('Incomplete native sequence')
    for start in range(0,len(names),12):
        chunk=names[start:start+12]
        if not all(p.is_file() for p in chunk):continue
        target=out/('review-%03d-%03d.png'%(217+start,228+start))
        if target.exists():continue
        sheet=Image.new('RGB',(864,1212),(245,245,245));draw=ImageDraw.Draw(sheet)
        for j,path in enumerate(chunk):
            with Image.open(path) as im:thumb=ImageOps.contain(im.convert('RGB'),(216,384))
            x=(j%4)*216;y=(j//4)*404;sheet.paste(thumb,(x,y));draw.text((x+6,y+386),path.stem,fill=(15,15,15))
        sheet.save(target)
    if args.final:
        target=out/'entrance-proof.mp4'
        if target.exists():raise ValueError('Preserve existing encoded proof')
        subprocess.run(['/opt/homebrew/bin/ffmpeg','-nostdin','-n','-hide_banner','-loglevel','error',
            '-framerate','24','-start_number','217','-i',str(out/'frame-%04d.png'),'-frames:v','144',
            '-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(target)],check=True)
        record={'source_frames':[{ 'path':p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in names],
            'video_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'fps':24,'frames':144,'duration_seconds':6,
            'processing':'Native frames only; contact-sheet resizing and H264 encoding; no generative changes or interpolation',
            'visual_gate':'NOT_RUN','realtime_playback_review':'NOT_RUN'}
        (out/'media.json').write_text(json.dumps(record,indent=2)+'\n')


if __name__=='__main__':main()
