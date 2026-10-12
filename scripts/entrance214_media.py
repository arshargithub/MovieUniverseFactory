"""Contact-review chronology and ordinary encoding of acknowledged native frames."""
import argparse
import json
import os
import subprocess
from pathlib import Path
from entrance189_media import sheet
from entrance193_media import sha,pixel_parity
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'.runtime/art-direction/series01-facebuilder-trial-01'
OUT=ROOT/'.runtime/art-direction/series01-entrance214'

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--encode',action='store_true');args=parser.parse_args()
    qa=OUT/'qa';qa.mkdir(exist_ok=True);available={};records={};sources={}
    for name in ('motion11','motion12'):
        folder=BASE/('entrance214-'+name);p=folder/'result.json'
        if not p.exists():p=folder/'progress.json'
        if not p.exists():continue
        data=json.loads(p.read_text());sources[name]=data['source_sha256']
        for row in data['frames']:
            i=row['index'];path=folder/f'frame-{i:04d}.png'
            if i in records or not path.is_file() or sha(path)!=row['sha256']:raise ValueError('Bad acknowledged frame')
            records[i]=row;available[i]=path
    for start in range(0,432,12):
        ids=list(range(start,start+12))
        if all(i in available for i in ids):sheet([available[i] for i in ids],qa/f'all-{start:04d}.png')
    print('Acknowledged frames',len(records))
    if not args.encode:return
    if set(records)!=set(range(432)) or any(records[i]['native_frame']!=i+217 for i in records):raise ValueError('Incomplete chronology')
    comparisons=[]
    for src,proof,full,frames in [('opening08','proof09','motion11',(277,330,360)),('route07','proof10','motion12',(390,427,472,550,620))]:
        native=BASE/('entrance214-'+src);r=json.loads((native/'result.json').read_text())
        if r['native_sha256']!=sources[full] or sha(native/'scene.blend')!=r['native_sha256']:raise ValueError('Source changed')
        result=BASE/('entrance214-'+proof)/'result.json'
        if not result.exists():raise ValueError('Reopen proof missing')
        proofrecord=json.loads(result.read_text())
        if not proofrecord.get('complete') or proofrecord['source_sha256']!=r['native_sha256']:raise ValueError('Reopen proof incomplete or stale')
        for f in frames:
            proofpath=result.parent/f'frame-{f-217:04d}.png'
            comparisons.append(dict(frame=f,build_vs_reopen=pixel_parity(native/f'actual-{f}.png',proofpath),
                                    full_vs_reopen=pixel_parity(available[f-217],proofpath)))
        complete=BASE/('entrance214-'+full)/'result.json'
        if not complete.exists() or not json.loads(complete.read_text()).get('complete'):raise ValueError('Worker not complete')
    target=OUT/'director-preview'
    if target.exists():raise ValueError('Preserve prior delivery')
    target.mkdir()
    for i in range(432):os.link(available[i],target/f'frame-{i:04d}.png')
    video=target/'pashtun-complete-entrance.mp4'
    subprocess.run(['/opt/homebrew/bin/ffmpeg','-nostdin','-n','-hide_banner','-loglevel','error','-framerate','24',
                    '-i',str(target/'frame-%04d.png'),'-frames:v','432','-c:v','libx264','-crf','18','-pix_fmt','yuv420p',
                    '-movflags','+faststart',str(video)],check=True)
    subprocess.run(['/opt/homebrew/bin/ffmpeg','-nostdin','-v','error','-i',str(video),'-f','null','-'],check=True)
    probe=json.loads(subprocess.check_output(['/opt/homebrew/bin/ffprobe','-v','error','-show_streams','-show_format','-of','json',str(video)]))
    streams=probe['streams'];stream=streams[0]
    if len(streams)!=1 or stream['codec_name']!='h264' or stream['pix_fmt']!='yuv420p' or stream['nb_frames']!='432' or stream['avg_frame_rate']!='24/1' or [stream['width'],stream['height']]!=[432,768] or abs(float(probe['format']['duration'])-18)>.001:
        raise ValueError('Encoded preview has wrong format or clock')
    (qa/'technical-review.json').write_text(json.dumps(dict(status='PASS',reopen=comparisons,frames=list(records.values()),
       video_sha256=sha(video),fps=24,duration=18,resolution=[432,768],visual_gate='NOT_RUN',
       limits='Silent preview, not final resolution, sound, Director acceptance or general grasp physics.'),indent=2)+'\n')

if __name__=='__main__':main()
