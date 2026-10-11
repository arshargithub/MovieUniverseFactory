"""Complete209 assembly and independently bound preservation/replay evidence."""
import argparse,json,os,subprocess
from pathlib import Path
import numpy as np
from entrance189_media import sheet
from entrance193_media import sha,pixel_parity
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'.runtime/art-direction/series01-facebuilder-trial-01';OUT=ROOT/'.runtime/art-direction/series01-entrance209'
PARTS=('proof05','proof06','opening07','route08')

def main():
    p=argparse.ArgumentParser();p.add_argument('--encode',action='store_true');p.add_argument('--verify',action='store_true');args=p.parse_args()
    qa=OUT/'qa';qa.mkdir(exist_ok=True);records={};available={};sources={}
    for part in PARTS:
        folder=BASE/('entrance209-'+part);meta=folder/'result.json'
        if not meta.exists():meta=folder/'progress.json'
        if not meta.exists():continue
        r=json.loads(meta.read_text());kind='opening' if part in ('proof05','opening07') else 'route'
        if kind in sources and sources[kind]!=r['source_sha256']:raise ValueError('Mixed source')
        sources[kind]=r['source_sha256']
        for row in r['frames']:
            i=row['index']
            if i in records:raise ValueError('Duplicate frame')
            records[i]=row;available[i]=folder/f'frame-{i:04d}.png'
    for first in range(0,432,12):
        ids=list(range(first,first+12))
        if all(i in available for i in ids):sheet([available[i] for i in ids],qa/f'all-{first:04d}.png')
    if not args.verify and not args.encode:
        print('Acknowledged frames',len(available));return
    if set(records)!=set(range(432)):raise ValueError('Incomplete chronology')
    previous={}
    for part in ('opening03','route04','opening05','route06'):
        for r in json.loads((BASE/('entrance207-'+part)/'result.json').read_text())['frames']:previous[r['index']]=r
    errors=[]
    for i,r in records.items():
        old=previous[i]
        if r['source_frame']!=i+217 or old['source_frame']!=r['source_frame'] or sha(available[i])!=r['sha256']:raise ValueError('Clock/hash mismatch')
        errors.append(max([abs(r['lens']-old['lens']),float(np.max(abs(np.array(r['camera'])-np.array(old['camera']))))]+[float(np.max(abs(np.array(r['pose'][n])-np.array(old['pose'][n])))) for n in r['pose']]))
    if max(errors)>2e-5:raise ValueError('Protected camera/performance changed')
    samples=[];contacts=[]
    for folder,part,frames in [('opening03','proof05',(245,277,300)),('route04','proof06',(390,427,454,520,620))]:
        src=BASE/('entrance209-'+folder);r=json.loads((src/'result.json').read_text())
        kind='opening' if folder.startswith('opening') else 'route'
        if sources[kind]!=r['native_sha256']:raise ValueError('Replay source mismatch')
        for f in frames:
            samples.append(dict(frame=f,**pixel_parity(src/f'control-{f}.png',available[f-217])))
            contacts.append(dict(frame=f,surfaces=records[f-217]['surface_control']))
    (qa/'technical-review.json').write_text(json.dumps(dict(status='PASS',reopen_samples=samples,camera_performance_max_error=max(errors),surface_controls=contacts,limits='Sampled surface intersection controls; not continuous collision or physics qualification. Complete visual review remains separate.'),indent=2)+'\n')
    if not args.encode:return
    for part in PARTS:
        if not (BASE/('entrance209-'+part)/'result.json').exists():raise ValueError('Worker still active')
    folder=OUT/'director-preview'
    if folder.exists():raise ValueError('Preserve prior delivery')
    folder.mkdir();rows=[]
    for i in range(432):
        os.link(available[i],folder/f'frame-{i:04d}.png');rows.append(dict(index=i,native_frame=i+217,sha256=records[i]['sha256'],source_image=str(available[i].relative_to(ROOT))))
    target=folder/'pashtun-complete-entrance.mp4'
    subprocess.run(['/opt/homebrew/bin/ffmpeg','-nostdin','-n','-v','error','-framerate','24','-i',str(folder/'frame-%04d.png'),'-frames:v','432','-c:v','libx264','-crf','16','-pix_fmt','yuv420p','-movflags','+faststart',str(target)],check=True)
    probe=json.loads(subprocess.check_output(['/opt/homebrew/bin/ffprobe','-v','error','-show_streams','-show_format','-of','json',str(target)]));s=probe['streams'][0]
    if int(s['nb_frames'])!=432 or s['avg_frame_rate']!='24/1' or abs(float(probe['format']['duration'])-18)>.001:raise ValueError('Encoded timing mismatch')
    subprocess.run(['/opt/homebrew/bin/ffmpeg','-nostdin','-v','error','-i',str(target),'-f','null','-'],check=True)
    (folder/'manifest.json').write_text(json.dumps(dict(frames=rows,native_sources=sources,fps=24,seconds=18,resolution=[432,768],video_sha256=sha(target),full_decode='PASS',processing='Exact native frames; proof frames reused only with identical source/profile; no synthetic in-betweens or retiming',visual_gate='NOT_RUN'),indent=2)+'\n')

if __name__=='__main__':main()
