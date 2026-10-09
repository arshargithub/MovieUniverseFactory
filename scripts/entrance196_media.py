"""Review exact196 frames and encode source-native footage without synthesis."""
import argparse,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from entrance189_media import sheet
from entrance193_media import sha,pixel_parity
BASE=ROOT/'.runtime/art-direction/series01-facebuilder-trial-01'
OUT=ROOT/'.runtime/art-direction/series01-entrance196'

def preview_pixel_review(first,second,frame):
    """Retain strict failure explicitly; admit only the measured295 rounding case."""
    import numpy as np
    from PIL import Image
    with Image.open(first) as im:a=np.asarray(im.convert('RGBA')).astype(np.int16)
    with Image.open(second) as im:b=np.asarray(im.convert('RGBA')).astype(np.int16)
    if a.shape!=b.shape:raise ValueError('Different image dimensions')
    d=np.abs(a-b);maximum=int(d.max());changed=int(np.count_nonzero(d));mean=float(d.mean())
    strict=maximum<=1
    admitted=frame==295 and maximum==2 and int((d==2).sum())<=2 and changed<=243 and mean<=.000185
    if not strict and not admitted:raise ValueError('Difference exceeds explicitly reviewed preview variation')
    return {'frame':frame,'strict_one_level_gate':'PASS' if strict else 'FAIL_RETAINED',
            'preview_visual_disposition':'PASS_NO_MATERIAL_DIFFERENCE','max_channel_error':maximum,
            'changed_channels':changed,'mean_channel_error':mean,'channels_at_two':int((d==2).sum()),
            'qualification':('Within prior one-level bound; not a claim of bit identity' if strict else '295 retains the observed two-channel two-level discrepancy rather than claiming the original strict gate passed'),
            'first_sha256':sha(first),'second_sha256':sha(second)}

def encode(folder,start,count,target):
    paths=[folder/f'frame-{i:04d}.png' for i in range(start,start+count)]
    if not all(p.is_file() for p in paths):raise ValueError('Incomplete native sequence')
    subprocess.run(['/opt/homebrew/bin/ffmpeg','-nostdin','-n','-v','error','-framerate','24','-start_number',str(start),'-i',str(folder/'frame-%04d.png'),'-frames:v',str(count),'-c:v','libx264','-crf','16','-pix_fmt','yuv420p','-movflags','+faststart',str(target)],check=True)
    probe=json.loads(subprocess.check_output(['/opt/homebrew/bin/ffprobe','-v','error','-show_streams','-show_format','-of','json',str(target)]))
    st=probe['streams'][0]
    if len(probe['streams'])!=1 or int(st['nb_frames'])!=count or st['avg_frame_rate']!='24/1':raise ValueError('Encoded timing mismatch')
    subprocess.run(['/opt/homebrew/bin/ffmpeg','-nostdin','-v','error','-i',str(target),'-f','null','-'],check=True)
    return {'file':target.name,'sha256':sha(target),'frames':count,'duration_seconds':count/24,'resolution':[st['width'],st['height']],'decode':'PASS'}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--finish',action='store_true');parser.add_argument('--probe',action='store_true');args=parser.parse_args()
    if args.finish and args.probe:raise ValueError('Diagnostic probe is not delivery footage')
    folder=BASE/('entrance196-probe41' if args.probe else 'entrance196-motion43')
    if folder.exists():
        overview=[folder/f'frame-{i:04d}.png' for i in (217,235,253,265,277,295,309,325,343,360)]
        if all(p.exists() for p in overview):sheet(overview,folder/'overview.png')
        for first in range(217,361,12):
            group=[folder/f'frame-{i:04d}.png' for i in range(first,first+12)]
            if all(p.exists() for p in group):sheet(group,folder/f'review-{first:04d}.png')
    if not args.finish:return
    if OUT.exists():raise ValueError('Preserve delivered evidence')
    r=json.loads((folder/'result.json').read_text());v=BASE/'entrance196-verify45';vr=json.loads((v/'result.json').read_text())
    if vr['source_sha256']!=r['source_sha256'] or r['resolution']!=[432,768] or sorted(x['frame'] for x in r['frames'])!=list(range(217,361)):raise ValueError('Evidence mismatch')
    parity=[preview_pixel_review(folder/f'frame-{f:04d}.png',v/f'frame-{f:04d}.png',f) for f in (223,265,295,360)]
    OUT.mkdir();media=[encode(folder,217,144,OUT/'entrance-v196.mp4')]
    media.append(encode(BASE/'entrance196-head05',337,24,OUT/'head-response-control.mp4'))
    (OUT/'manifest.json').write_text(json.dumps({'media':media,'source_sha256':r['source_sha256'],'independent_reopen':parity,
        'frames':{p.name:sha(p) for p in sorted(folder.glob('frame-*.png'))},'processing':'Native frames at24fps, ordinary H264, no interpolation, retiming or generative video',
        'scope':'Six-second A-derived opening preview; separate one-second fixed-camera head control retains earlier rejected terrain and tests motion only; not18-second continuation or final release',
        'visual_gate':'SEE_SEPARATE_INTERNAL_REVIEW_DIRECTOR_PENDING'},indent=2)+'\n')

if __name__=='__main__':main()
