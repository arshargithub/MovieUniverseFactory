"""Verify admitted frame receipts and package the unretimed preparation proof.

No Blender launch, artistic verdict, frame interpolation or provider call.
"""
import json, sys, shutil, subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from movie_factory import production_knowledge as pk

r=Path(__file__).resolve().parents[1]
o=r/'results/sikh368'
out=r/'.runtime/art-direction/sikh368-review-c51'
out.mkdir(parents=True,exist_ok=True)
def write(p,value):
    text=json.dumps(value,indent=2)+'\n'
    if p.exists():assert p.read_text()==text,str(p)
    else:p.write_text(text)
def bind(p):
    return dict(path=str(p.relative_to(r)),sha256=pk.file_hash(p))
def entries(batch):
    run=json.loads((o/f'motion-c51-phase{batch:02d}-run.json').read_text())
    assert run['status']=='RETURNED'
    mf=r/run['artifacts']['frames']['path']
    assert pk.file_hash(mf)==run['artifacts']['frames']['sha256']
    rows=json.loads(mf.read_text())
    for row in rows:
        p=mf.parent/row['file']
        assert pk.file_hash(p)==row['sha256']
        row['binding']=bind(p)
    return rows
if sys.argv[1]=='sheet':
    batch=int(sys.argv[2]);rows=entries(batch)
    # Canonical314 is a repeat control, not an extra chronological pose.
    rows=[x for x in rows if x['frame']!=314 or batch==6]
    sheet=Image.new('RGB',(3*300,((len(rows)+2)//3)*326),(230,230,230))
    d=ImageDraw.Draw(sheet)
    for i,row in enumerate(rows):
        im=Image.open(r/row['binding']['path']).convert('RGB');im.thumbnail((300,300))
        x=(i%3)*300;y=(i//3)*326
        sheet.paste(im,(x,y));d.text((x+7,y+305),f"{row['frame']} / {(row['frame']-276)/24:.3f}s",fill=(0,0,0))
    p=out/f'phase{batch:02d}.jpg';sheet.save(p,quality=94)
    print(p)
elif sys.argv[1]=='assemble':
    frames={};canonical=[];camera=[]
    for batch in range(1,7):
        for row in entries(batch):
            camera.append(row['camera_matrix'])
            if row['frame']==314:canonical.append(row['binding'])
            if row['frame'] in frames:assert frames[row['frame']]==row['binding'] or row['frame']==314
            else:frames[row['frame']]=row['binding']
    assert set(frames)==set(range(276,315))
    assert all(np.allclose(camera[0],m,atol=1e-7) for m in camera)
    arrays=[np.asarray(Image.open(r/x['path'])) for x in canonical]
    diffs=[int(np.max(np.abs(a.astype(int)-arrays[0].astype(int)))) for a in arrays]
    assert max(diffs)==0
    sequence=out/'frames';sequence.mkdir(exist_ok=True)
    for i,f in enumerate(range(276,315)):
        p=sequence/f'{i:04d}.png'
        if p.exists():assert pk.file_hash(p)==frames[f]['sha256']
        else:shutil.copy2(r/frames[f]['path'],p)
    clip=out/'preparation-firstlift.mp4'
    assert not clip.exists()
    subprocess.run(['/opt/homebrew/bin/ffmpeg','-v','error','-framerate','24','-i',str(sequence/'%04d.png'),'-frames:v','39','-c:v','libx264','-crf','17','-pix_fmt','yuv420p','-movflags','+faststart',str(clip)],check=True)
    profile=json.loads(subprocess.check_output(['/opt/homebrew/bin/ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(clip)]))
    stream=profile['streams'][0]
    assert int(stream['nb_read_frames'])==39 and stream['r_frame_rate']=='24/1' and stream['pix_fmt']=='yuv420p'
    assert abs(float(profile['format']['duration'])-39/24)<.002
    write(o/'media-manifest.json',dict(video=bind(clip),source_frames={str(f):frames[f] for f in sorted(frames)},canonical314=canonical,max_channel_differences=diffs,profile=profile,scope='Silent39frame276..314 preparation only; unretimed24fps, fixed diagnostic oblique camera. No final rear/appearance/cloth/AV acceptance.'))
    print(clip)
elif sys.argv[1]=='comparison':
    reference=r/'.runtime/art-direction/series01-sikh256/references/reference-b.mov'
    assert pk.file_hash(reference)=='78d0d691e8712c02931876cf0bc405e4869de357f337f531708be7a7da4898e2'
    clip=out/'preparation-firstlift.mp4';assert clip.exists()
    refclip=out/'reference-preparation.mp4';comparison=out/'preparation-reference-comparison.mp4'
    assert not refclip.exists() and not comparison.exists()
    subprocess.run(['/opt/homebrew/bin/ffmpeg','-v','error','-ss','15','-i',str(reference),'-t','1.625','-an','-vf','crop=350:308:190:338,scale=432:-2,pad=432:432:(ow-iw)/2:(oh-ih)/2:color=0x111111,fps=24','-frames:v','39','-c:v','libx264','-crf','17','-pix_fmt','yuv420p','-movflags','+faststart',str(refclip)],check=True)
    header=Image.new('RGB',(864,40),(17,17,17));draw=ImageDraw.Draw(header);font=ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc',19)
    draw.text((12,9),'Reference 15.0-16.625s',font=font,fill='white');draw.text((444,9),'Candidate: preparation / first lift',font=font,fill='white')
    header.save(out/'comparison-header.png')
    subprocess.run(['/opt/homebrew/bin/ffmpeg','-v','error','-i',str(refclip),'-i',str(clip),'-i',str(out/'comparison-header.png'),'-filter_complex','[1:v]crop=330:330:60:25,scale=432:432[horse];[0:v][horse]hstack=inputs=2,pad=864:472:0:40:color=0x111111[base];[base][2:v]overlay=0:0:shortest=0[v]','-map','[v]','-frames:v','39','-an','-c:v','libx264','-crf','17','-pix_fmt','yuv420p','-movflags','+faststart',str(comparison)],check=True)
    repeats=out/'preparation-comparison-three-repeats.mp4'
    subprocess.run(['/opt/homebrew/bin/ffmpeg','-v','error','-stream_loop','2','-i',str(comparison),'-map','0:v','-frames:v','117','-an','-c:v','libx264','-crf','17','-pix_fmt','yuv420p','-movflags','+faststart',str(repeats)],check=True)
    write(o/'comparison-manifest.json',dict(reference=bind(reference),crop=[190,338,350,308],candidate_display_crop=[60,25,330,330],reference_start_seconds=15,duration_seconds=1.625,reference_clip=bind(refclip),candidate=bind(clip),comparison=bind(comparison),three_normal_speed_repeats=bind(repeats),scope='Private reference crop and candidate both normal-time24fps. Three repeats are review convenience only. No mirroring, optical flow, timewarp or extra pose hold; source captions cropped out and not adopted. Diagnostic phase comparison only.'))
    print(repeats)
else:raise SystemExit('sheet BATCH | assemble | comparison')
