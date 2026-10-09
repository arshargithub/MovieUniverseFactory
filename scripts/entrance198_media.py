"""Native frame review and ordinary encoding, no synthetic frames/retiming."""
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from entrance189_media import sheet
from entrance193_media import sha,pixel_parity
from entrance196_media import encode
BASE=ROOT/'.runtime/art-direction/series01-facebuilder-trial-01'
OUT=ROOT/'.runtime/art-direction/series01-entrance198'

def main():
    p=argparse.ArgumentParser();p.add_argument('--finish',action='store_true');a=p.parse_args()
    folder=BASE/'entrance198-motion04';control=BASE/'entrance198-controls03';verify=BASE/'entrance198-verify05'
    sheet([control/f'frame-{f:04d}.png' for f in (217,223,228,295,325,360)],control/'review.png',columns=3)
    if folder.exists():
        for f in range(217,361,12):sheet([folder/f'frame-{i:04d}.png' for i in range(f,f+12)],folder/f'review-{f:04d}.png')
        sheet([folder/f'frame-{f:04d}.png' for f in (217,235,253,265,277,295,309,325,343,360)],folder/'overview.png')
    if not a.finish:return
    if OUT.exists():raise ValueError('Preserve delivered evidence')
    r=json.loads((folder/'result.json').read_text());v=json.loads((verify/'result.json').read_text())
    if r['source_sha256']!=v['source_sha256'] or sorted(x['frame'] for x in r['frames'])!=list(range(217,361)):raise ValueError('Source/clock mismatch')
    for filename in ('structural-parity.json','cache-parity.json','particle-parity.json'):
        if json.loads((verify/filename).read_text())['status']!='PASS':raise ValueError('Independent verification incomplete')
    # Do not inherit196's rounding exception. New discrepancies stay failures.
    parity=[pixel_parity(folder/f'frame-{f:04d}.png',verify/f'frame-{f:04d}.png') for f in (223,295,360)]
    OUT.mkdir();media=encode(folder,217,144,OUT/'entrance-v198.mp4')
    (OUT/'manifest.json').write_text(json.dumps({'media':media,'source_sha256':r['source_sha256'],'independent_reopen':parity,
        'frames':{p.name:sha(p) for p in sorted(folder.glob('frame-*.png'))},'processing':'Exact native frames,24fps H264; no interpolation/retiming/generative video',
        'scope':'Six-second terrain-look opening proof; phone delivery deferred;18-second entrance not yet updated','visual_gate':'SEE_INTERNAL_REVIEW_DIRECTOR_PENDING'},indent=2)+'\n')

if __name__=='__main__':main()
