"""Review and encode exact native frames; no generated or retimed footage."""
import argparse,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from entrance189_media import sheet
from entrance193_media import sha,pixel_parity
from entrance196_media import encode
BASE=ROOT/'.runtime/art-direction/series01-facebuilder-trial-01'
OUT=ROOT/'.runtime/art-direction/series01-entrance200'

def reviewed_final_parity(folder,verify,source_sha):
    """Retain, never relabel, the exact inspected two-channel background failure."""
    import numpy as np
    from PIL import Image
    first=folder/'frame-0360.png';second=verify/'frame-0360.png'
    try:return pixel_parity(first,second)
    except ValueError:
        review=json.loads((verify/'pixel-review.json').read_text())
        if (review['status']!='SCOPED_BACKGROUND_ROUNDING_EXCEPTION' or
            review['source_sha256']!=source_sha or sha(first)!=review['full_frame_sha256'] or
            sha(second)!=review['verify_frame_sha256']):raise ValueError('Unreviewed pixel mismatch')
        repeat=BASE/'entrance200-repeat20';third=repeat/'frame-0360.png'
        if (sha(third)!=review['repeat_sha256'] or
            json.loads((repeat/'result.json').read_text())['source_sha256']!=source_sha or
            json.loads((repeat/'structural-parity.json').read_text())['status']!='PASS'):
            raise ValueError('Repeat source differs')
        arrays=[np.asarray(Image.open(p).convert('RGBA')).astype(np.int16) for p in (first,second,third)]
        for other in arrays[1:]:
            delta=np.abs(arrays[0]-other)
            if int(delta.max())!=2 or np.argwhere(delta>1).tolist()!=[[116,97,0],[116,97,1]]:
                raise ValueError('Mismatch exceeds specifically inspected background pixel')
        repeat_match=pixel_parity(second,third)
        return {'status':'STRICT_FAIL_RETAINED_SCOPED_BACKGROUND_ROUNDING_EXCEPTION',
                'strict_threshold':1,'max_channel_error':2,'channels_above_threshold':2,
                'first_sha256':sha(first),'second_sha256':sha(second),'repeat_vs_verify':repeat_match,
                'review':'entrance200-verify19/pixel-review.json','bit_identical_rendering':False}

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
    parity=[pixel_parity(folder/f'frame-{f:04d}.png',v/f'frame-{f:04d}.png') for f in (223,295,343,350)]
    parity.append(reviewed_final_parity(folder,v,r['source_sha256']))
    OUT.mkdir();media=[encode(folder,217,144,OUT/'entrance-v200.mp4')]
    media.append(encode(BASE/'entrance200-fixed05',337,24,OUT/'fixed05.mp4'))
    (OUT/'manifest.json').write_text(json.dumps({'source_sha256':r['source_sha256'],'media':media,'independent_reopen':parity,
      'frames':{p.name:sha(p) for p in sorted(folder.glob('frame-*.png'))},
      'processing':'Native frames at24fps H264; no interpolation, retiming or generative video',
      'scope':'Six-second integrated rider performance and costume/skin look proof, not completed18-second entrance or final release',
      'fixed_cycle_source':'candidate10; same artwork as seal17, earlier diagnostic render profile; not the full-sequence master',
      'visual_gate':'SEE_SOURCE_BOUND_INTERNAL_REVIEW; DIRECTOR_PENDING'},indent=2)+'\n')

if __name__=='__main__':main()
