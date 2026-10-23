"""Bounded evidence packaging, never Blender launch or perceptual approval."""
import json,hashlib,sys,subprocess
import numpy as np
from pathlib import Path
from PIL import Image,ImageDraw
r=Path(__file__).resolve().parents[1];o=r/'results/sikh362';media=r/'.runtime/art-direction/sikh362-review';media.mkdir(parents=True,exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rows(step,cycle=26):
    p=o/f'motion-c{cycle}-{step}-run.json';run=json.loads(p.read_text());assert run['status']=='RETURNED'
    for binding in run['artifacts'].values():assert sha(r/binding['path'])==binding['sha256']
    path=r/run['artifacts']['frames']['path'];frames=json.loads(path.read_text())
    result=[]
    for item in frames:
        image=path.parent/item['file'];assert sha(image)==item['sha256'];assert Image.open(image).size==(432,768)
        result.append((item['frame'],image,item['sha256']))
    return result
mode=sys.argv[1]
if mode=='sheet':
    step=sys.argv[2];items=sorted(rows(step,int(sys.argv[3]) if len(sys.argv)>3 else 26));w,h=216,384;cols=3;nr=(len(items)+cols-1)//cols
    sheet=Image.new('RGB',(cols*w,nr*(h+24)),(30,30,30));d=ImageDraw.Draw(sheet)
    for i,(frame,path,_) in enumerate(items):
        x=i%cols*w;y=i//cols*(h+24);im=Image.open(path).convert('RGB');im.thumbnail((w,h));sheet.paste(im,(x,y));d.text((x+6,y+h+4),str(frame),fill='white')
    dest=media/(step+'-sheet.jpg');sheet.save(dest,quality=94);print(dest)
elif mode=='encode':
    frames={};duplicates=[]
    batches=[rows(f'frames{i:02d}') for i in range(1,17)]+[rows('tail_context',27)]
    for batch in batches:
        for f,p,h in batch:
            if f in frames:
                a=np.asarray(Image.open(frames[f][0]).convert('RGB'),dtype=np.int16);b=np.asarray(Image.open(p).convert('RGB'),dtype=np.int16);delta=np.abs(a-b)
                duplicates.append(dict(frame=f,paths=[str(frames[f][0].relative_to(r)),str(p.relative_to(r))],hash_equal=frames[f][1]==h,max_channel_levels=int(delta.max()),changed_channels=int(np.count_nonzero(delta)),within_one_level=bool(delta.max()<=1)))
            else:frames[f]=(p,h)
    assert set(frames)==set(range(252,381))
    sequence=media/'frames';sequence.mkdir(exist_ok=True)
    for f,(p,h) in frames.items():
        dest=sequence/f'{f-252:04d}.png'
        if dest.exists() or dest.is_symlink():assert dest.resolve()==p.resolve()
        else:dest.symlink_to(p)
    video=media/'nihang-leader-horse-362.mp4'
    assert not video.exists(),'Preserve any prior export rather than overwrite'
    cmd=['/opt/homebrew/bin/ffmpeg','-hide_banner','-loglevel','error','-framerate','24','-i',str(sequence/'%04d.png'),'-frames:v','129','-c:v','libx264','-crf','17','-preset','medium','-pix_fmt','yuv420p','-movflags','+faststart','-an',str(video)]
    subprocess.run(cmd,check=True)
    probe=json.loads(subprocess.run(['/opt/homebrew/bin/ffprobe','-v','error','-count_frames','-show_streams','-of','json',str(video)],check=True,capture_output=True,text=True).stdout)
    stream=probe['streams'][0];assert stream['nb_read_frames']=='129' and stream['avg_frame_rate']=='24/1' and stream['pix_fmt']=='yuv420p'
    report=dict(video=dict(path=str(video.relative_to(r)),sha256=sha(video)),fps=24,count=129,source_frames=[252,380],core_frames=[276,356],handles='24 frames before and24 after the actual shot',resolution=[432,768],sound='EXCLUDED, silent appearance/motion review',scope='Leader and horse only; existing crowd and principal in handles deferred/unqualified',duplicates=duplicates,frames=[dict(frame=f,path=str(p.relative_to(r)),sha256=h) for f,(p,h) in sorted(frames.items())],probe=probe,limitations='Technical decode and montage inspection are not direct audiovisual or release approval.')
    (o/'media-manifest.json').write_text(json.dumps(report,indent=2)+'\n');print(video)
else:raise ValueError('mode')
