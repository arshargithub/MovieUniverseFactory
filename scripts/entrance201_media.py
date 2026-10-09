"""Exact-frame contact sheets and encodes; never grants a visual pass."""
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from entrance189_media import sheet
from entrance196_media import encode
from entrance189_edit import digest
BASE=ROOT/'.runtime/art-direction/series01-facebuilder-trial-01'
STAGES={'opening06':(217,144),'attention07':(289,48),'route08':(361,192),'geography09':(0,48)}

def main():
    p=argparse.ArgumentParser();p.add_argument('stage',choices=STAGES);p.add_argument('--encode',action='store_true');args=p.parse_args()
    folder=BASE/('entrance201-'+args.stage);start,count=STAGES[args.stage]
    for i in range(start,start+count,12):sheet([folder/f'frame-{f:04d}.png' for f in range(i,min(i+12,start+count))],folder/f'review-{i:04d}.png')
    if not args.encode:return
    r=json.loads((folder/'result.json').read_text())
    if [x['frame'] for x in r['frames']]!=list(range(start,start+count)):raise ValueError('Incomplete clock')
    for row in r['frames']:
        if digest(folder/f"frame-{row['frame']:04d}.png")!=row['sha256']:raise ValueError('Frame changed')
    media=encode(folder,start,count,folder/'proof.mp4');media.update(source_sha256=r['source_sha256'],frames=r['frames'],visual_gate='NOT_RUN')
    (folder/'media.json').write_text(json.dumps(media,indent=2)+'\n')

if __name__=='__main__':main()
