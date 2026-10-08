"""Exact native-frame review sheets and synchronized A/B encoding; no synthesis."""
import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from PIL import Image
import numpy as np
from entrance189_media import sheet

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'.runtime/art-direction/series01-facebuilder-trial-01'
OUT=ROOT/'.runtime/art-direction/series01-motion-style193'


def sha(path):
    with path.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()


def pixel_parity(first,second):
    with Image.open(first) as im:a=np.asarray(im.convert('RGBA')).astype(np.int16)
    with Image.open(second) as im:b=np.asarray(im.convert('RGBA')).astype(np.int16)
    if a.shape!=b.shape:raise ValueError('Reopen dimensions differ')
    d=np.abs(a-b)
    if d.max()>1:raise ValueError('Reopen differs by more than one 8-bit channel level')
    return {'status':'PASS','max_channel_error':int(d.max()),'changed_channels':int(np.count_nonzero(d)),
            'mean_channel_error':float(d.mean()),'tolerance':1,'first_sha256':sha(first),'second_sha256':sha(second)}


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--finish',action='store_true');args=parser.parse_args()
    folders=[BASE/'entrance193-lookA10',BASE/'entrance193-lookB18']
    for folder in folders:
        if not folder.exists():continue
        paths=[folder/f'frame-{f:04d}.png' for f in range(217,361)]
        for i in range(0,144,12):
            group=paths[i:i+12]
            if all(p.exists() for p in group):sheet(group,folder/f'review-{217+i:04d}.png')
    if not args.finish:return
    records=[json.loads((p/'result.json').read_text()) for p in folders]
    if records[0]['animation_sha256']!=records[1]['animation_sha256']:raise ValueError('A/B animation differs')
    parity=[]
    for folder,control,record in zip(folders,('entrance193-parityA14','entrance193-parityB19'),records):
        p=BASE/control;r=json.loads((p/'result.json').read_text())
        if r['source_sha256']!=record['source_sha256'] or r['animation_sha256']!=record['animation_sha256'] or r['viewport_only_flags']:
            raise ValueError('Independent control source/action/flags mismatch')
        if record['resolution']!=[360,640] or record['fps']!=24 or [row['frame'] for row in record['frames']]!=list(range(217,361)):
            raise ValueError('Unexpected native frame sequence')
        parity.append({'treatment':folder.name,**pixel_parity(folder/'frame-0360.png',p/'frame-0360.png')})
    if OUT.exists():raise ValueError('Preserve delivered comparison')
    OUT.mkdir();(OUT/'handler.py').write_bytes(Path(__file__).read_bytes())
    pair_image=Image.new('RGB',(720,640))
    for i,folder in enumerate(folders):
        with Image.open(folder/'frame-0360.png') as im:pair_image.paste(im.convert('RGB'),(i*360,0))
    pair_image.save(OUT/'matched-close.png')
    videos=[]
    for folder,label in zip(folders,('current','illustrated')):
        paths=[folder/f'frame-{f:04d}.png' for f in range(217,361)]
        if not all(p.exists() for p in paths):raise ValueError('Incomplete sequence')
        target=OUT/(label+'.mp4')
        subprocess.run(['/opt/homebrew/bin/ffmpeg','-nostdin','-n','-v','error','-framerate','24','-start_number','217',
            '-i',str(folder/'frame-%04d.png'),'-frames:v','144','-c:v','libx264','-crf','17','-pix_fmt','yuv420p','-movflags','+faststart',str(target)],check=True)
        videos.append(target)
    pair=OUT/'matched-comparison.mp4'
    subprocess.run(['/opt/homebrew/bin/ffmpeg','-nostdin','-n','-v','error','-i',str(videos[0]),'-i',str(videos[1]),
        '-filter_complex','[0:v][1:v]hstack=inputs=2[v]','-map','[v]','-c:v','libx264','-crf','17','-pix_fmt','yuv420p','-movflags','+faststart',str(pair)],check=True)
    checks=[]
    for video in videos+[pair]:
        probe=json.loads(subprocess.check_output(['/opt/homebrew/bin/ffprobe','-v','error','-show_streams','-show_format','-of','json',str(video)]))
        stream=probe['streams'][0]
        if len(probe['streams'])!=1 or stream['nb_frames']!='144' or stream['avg_frame_rate']!='24/1' or abs(float(probe['format']['duration'])-6)>.001:raise ValueError('Unexpected encoded clock')
        subprocess.run(['/opt/homebrew/bin/ffmpeg','-nostdin','-v','error','-i',str(video),'-f','null','-'],check=True)
        checks.append({'name':video.name,'sha256':sha(video),'frames':144,'seconds':6,'fps':24,
                       'resolution':[stream['width'],stream['height']],'full_decode':'PASS'})
    (OUT/'manifest.json').write_text(json.dumps({'media':checks,'animation_sha256':records[0]['animation_sha256'],
        'sources':[{'folder':str(p.relative_to(ROOT)),'native_sha256':r['source_sha256']} for p,r in zip(folders,records)],
        'frame_hashes':{p.name:{f.name:sha(f) for f in sorted(p.glob('frame-*.png'))} for p in folders},
        'processing':'Exact native frames and ordinary H264; synchronized hstack, no interpolation/generative video',
        'independent_reopen':parity,'close_comparison_sha256':sha(OUT/'matched-close.png'),
        'visual_gate':'NOT_RUN','scope':'Silent preview-resolution visual-language comparison, not a finished trailer'},indent=2)+'\n')


if __name__=='__main__':main()
