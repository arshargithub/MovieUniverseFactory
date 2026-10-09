"""Review and encode exact native frames; no generated or retimed footage."""
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from entrance189_media import sheet
from entrance193_media import sha,pixel_parity
from entrance196_media import encode
BASE=ROOT/'.runtime/art-direction/series01-facebuilder-trial-01'
OUT=ROOT/'.runtime/art-direction/series01-entrance200'

def main():
    p=argparse.ArgumentParser();p.add_argument('--finish',action='store_true');args=p.parse_args()
    c=BASE/'entrance200-controls11';folder=BASE/'entrance200-motion18';v=BASE/'entrance200-verify19'
    sheet([c/f'frame-{f:04d}.png' for f in (217,265,295,325,349,360)],c/'review.png',columns=3)
    for stage,start,end in [('fixed05',337,361),('before06',337,361),('motion07',217,361),('motion18',217,361)]:
        d=BASE/('entrance200-'+stage)
        if d.exists():
            for first in range(start,end,12):sheet([d/f'frame-{i:04d}.png' for i in range(first,min(first+12,end))],d/f'review-{first:04d}.png')
    if not args.finish:return
    if OUT.exists():raise ValueError('Preserve delivery history')
    r=json.loads((folder/'result.json').read_text());vr=json.loads((v/'result.json').read_text())
    if r['source_sha256']!=vr['source_sha256'] or sorted(x['frame'] for x in r['frames'])!=list(range(217,361)):raise ValueError('Incomplete clock/source')
    for fn in ('structural-parity.json','cache-parity.json','particle-parity.json','pose-parity.json'):
        if json.loads((v/fn).read_text())['status']!='PASS':raise ValueError('Verification failed')
    parity=[pixel_parity(folder/f'frame-{f:04d}.png',v/f'frame-{f:04d}.png') for f in (223,295,343,350,360)]
    OUT.mkdir();media=[encode(folder,217,144,OUT/'entrance-v200.mp4')]
    media.append(encode(BASE/'entrance200-fixed05',337,24,OUT/'fixed05.mp4'))
    (OUT/'manifest.json').write_text(json.dumps({'source_sha256':r['source_sha256'],'media':media,'independent_reopen':parity,
      'frames':{p.name:sha(p) for p in sorted(folder.glob('frame-*.png'))},
      'processing':'Native frames at24fps H264; no interpolation, retiming or generative video',
      'scope':'Six-second integrated rider performance and costume/skin look proof, not completed18-second entrance or final release',
      'fixed_cycle_source':'candidate10; same artwork as seal17, earlier diagnostic render profile; not the full-sequence master',
      'visual_gate':'SEE_SOURCE_BOUND_INTERNAL_REVIEW; DIRECTOR_PENDING'},indent=2)+'\n')

if __name__=='__main__':main()
