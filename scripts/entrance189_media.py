"""Review layouts and ordinary encoding of exact native frames, never synthesis."""
import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from PIL import Image,ImageDraw,ImageOps

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'.runtime/art-direction/series01-facebuilder-trial-01'


def sheet(paths,target,columns=4):
    if target.exists() or not all(p.exists() for p in paths):return
    rows=(len(paths)+columns-1)//columns
    result=Image.new('RGB',(216*columns,404*rows),(238,238,238));draw=ImageDraw.Draw(result)
    for i,p in enumerate(paths):
        with Image.open(p) as im:thumb=ImageOps.contain(im.convert('RGB'),(216,384))
        x=(i%columns)*216;y=(i//columns)*404
        result.paste(thumb,(x,y));draw.text((x+5,y+386),p.stem,fill=(15,15,15))
    result.save(target)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--overview',action='store_true');parser.add_argument('--decision',action='store_true');args=parser.parse_args()
    out=BASE/(('entrance189-decision-overview19' if args.overview else 'entrance189-decision-motion20') if args.decision else ('entrance189-overview15' if args.overview else 'entrance189-motion16'))
    start,end=(289,337) if args.decision else (217,361)
    ids=list(range(start,end,6))+[end-1] if args.overview else list(range(start,end))
    paths=[out/('frame-%04d.png'%f) for f in ids]
    for i in range(0,len(ids),12):sheet(paths[i:i+12],out/('review-%04d.png'%ids[i]))
    if args.overview:return
    if not (out/'result.json').exists() or not all(p.exists() for p in paths):
        print('Completed groups laid out; full native sequence not complete');return
    target=out/('decision-proof.mp4' if args.decision else 'entrance-proof.mp4')
    if target.exists():raise ValueError('Preserve existing video')
    subprocess.run(['/opt/homebrew/bin/ffmpeg','-nostdin','-n','-hide_banner','-loglevel','error',
        '-framerate','24','-start_number',str(start),'-i',str(out/'frame-%04d.png'),'-frames:v',str(end-start),
        '-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(target)],check=True)
    record={'fps':24,'frame_count':end-start,'duration_seconds':(end-start)/24,'processing':'Exact native frames, normal H264; no interpolation or generative video',
        'frames':[{'name':p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in paths],
        'video_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'visual_gate':'NOT_RUN'}
    (out/'media.json').write_text(json.dumps(record,indent=2)+'\n')


if __name__=='__main__':main()
