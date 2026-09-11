"""Add synchronized A/B video copies while preserving all original PNGs/HTML."""
import argparse,json,shutil,subprocess
from pathlib import Path
from movie_factory.packages import atomic_json,file_digest,manifest_for


def main():
    parser=argparse.ArgumentParser();parser.add_argument('run',type=Path);args=parser.parse_args();run=args.run.resolve();review=run/'review'
    ffmpeg=shutil.which('ffmpeg');ffprobe=shutil.which('ffprobe')
    if not ffmpeg or not ffprobe:raise ValueError('Local ffmpeg and ffprobe are required')
    receipt=review/'video-provenance.json'
    if receipt.exists():raise FileExistsError('Keep the original video provenance')
    before=run/'artifact-manifest-before-video.json'
    if before.exists():raise FileExistsError(before)
    shutil.copy2(run/'artifact-manifest.json',before)
    records=[]
    for view in ('primary','side','rear'):
        folders=[review/'frames'/label/view for label in ('A','B')]
        for folder in folders:
            if sorted(p.name for p in folder.glob('frame-*.png'))!=[f'frame-{i:04d}.png' for i in range(1,97)]:raise ValueError('Incomplete frozen frames')
        output=review/f'{view}-AB.mp4'
        if output.exists():raise FileExistsError(output)
        command=[ffmpeg,'-hide_banner','-loglevel','error']
        for folder in folders:command+=['-framerate','24','-i',str(folder/'frame-%04d.png')]
        command+=['-filter_complex','[0:v][1:v]hstack=inputs=2[out]','-map','[out]','-frames:v','96','-c:v','libx264','-crf','14','-pix_fmt','yuv420p','-movflags','+faststart',str(output)]
        subprocess.run(command,check=True)
        metadata=json.loads(subprocess.check_output([ffprobe,'-v','error','-select_streams','v:0','-show_entries','stream=nb_frames,r_frame_rate,width,height','-show_entries','format=duration','-of','json',str(output)],text=True))
        stream=metadata['streams'][0]
        if stream['nb_frames']!='96' or stream['r_frame_rate']!='24/1' or abs(float(metadata['format']['duration'])-4)>1e-6:raise ValueError('Incorrect convenience video timing')
        records.append({'view':view,'path':str(output.relative_to(run)),'sha256':file_digest(output),'metadata':metadata,'inputs':manifest_for(run,[p for folder in folders for p in folder.glob('frame-*.png')])})
    page='''<!doctype html><meta charset="utf-8"><title>3D-05 anonymous video review</title><style>body{background:#171717;color:white;font:16px system-ui;margin:2rem}video{width:100%;max-width:1280px}.labels{display:flex;justify-content:space-around;max-width:1280px}</style><h1>3D-05 complete A/B interaction</h1><p>Clip A is on the left; Clip B is on the right. Each video contains the full four-second interaction at 24 fps. Review all three views. Replay resets to the starting pose; this pickup is not a seamless loop. Original PNGs and the frame-by-frame player remain available.</p>'''
    for view in ('primary','side','rear'):
        page+=f'<h2>{view.title()}</h2><div class="labels"><b>Clip A</b><b>Clip B</b></div><video controls playsinline preload="metadata" src="{view}-AB.mp4"></video>'
    page+='<p>Record scores for both clips: readability, grasp/contact, transition smoothness, hold/clearance; then preference, defects and total review seconds. Scores use 1–5 in 0.5 steps. <a href="index.html">Original frame-by-frame player</a>.</p>'
    (review/'video.html').write_text(page)
    atomic_json(receipt,{'schema_version':'1.0','scope':'Convenience H.264 copies; original PNGs remain exact visual evidence','left_label':'A','right_label':'B','original_player_sha256':file_digest(review/'index.html'),'ffmpeg_version':subprocess.check_output([ffmpeg,'-version'],text=True).splitlines()[0],'encoding':{'codec':'libx264','crf':14,'fps':24,'frames':96,'duration_seconds':4},'videos':records})
    atomic_json(run/'artifact-manifest.json',{'schema_version':'1.0','run_id':run.name,'artifacts':manifest_for(run,[p for p in run.rglob('*') if p.is_file() and p!=run/'artifact-manifest.json'])})
    print(review/'video.html')

if __name__=='__main__':main()
