"""Editorial assembly only; exact accepted Pashtun source is never rerendered."""
from pathlib import Path
import subprocess,json,hashlib,sys
from movie_factory import production_knowledge as pk
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'.runtime/art-direction/series01-sikh304'
PASHTUN=ROOT/'.runtime/art-direction/series01-finish248/delivery01/pashtun-20s.mp4'
AUDIO=BASE/'audio-01'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run(args):subprocess.run(['/opt/homebrew/bin/ffmpeg','-v','error']+args,check=True)
def prepare(mode):
    paths=[Path(__file__),ROOT/'results/sikh304/STRATEGY.md',ROOT/'results/sikh304/STRATEGY.md',PASHTUN]
    if mode=='full':paths += [AUDIO/'sikh-mix.wav',AUDIO/'joined-mix.wav',BASE/'movie-08/frame-provenance.json',BASE/'build-08/sequence.blend']
    else:paths += [BASE/'motion-01/source/bindings.json']
    task=json.loads((ROOT/'results/sikh304/movie-8/task.json').read_text());task.update(id='sikh304-edit-'+mode,operation='audio',phase='execution')
    task['preserve_accepted_artifact']='1004ed9f2e06d2eafb008c925eb9d266e8a13b8603086020e28d19e3b606722b'
    task['inputs'].update({str(p.relative_to(ROOT)):sha(p) for p in paths})
    packet=pk.task_packet(ROOT,task);folder=ROOT/'results/sikh304'/('edit-'+mode);folder.mkdir(exist_ok=True)
    for name,data in [('task',task),('packet',packet)]:(folder/(name+'.json')).write_text(json.dumps(data,indent=2))
    (folder/'packet.md').write_text(pk.packet_markdown(packet))
    if not packet['dispatch_ready']:raise ValueError(packet['blockers'])
    return folder
def main():
    mode=sys.argv[1] if len(sys.argv)>1 else 'full'
    if mode not in ('full','motion'):raise ValueError('Unknown edit')
    folder=prepare(mode)
    if '--prepare' in sys.argv:print(folder/'packet.md');return
    if mode=='motion':
        for start,folder,name in ((105,'frames','skid'),(290,'rear-frames','horse-rear')):
            run(['-framerate','24','-start_number',str(start),'-i',str(BASE/f'motion-01/{folder}/frame-%04d.png'),'-c:v','libx264','-crf','16','-pix_fmt','yuv420p',str(BASE/f'motion-01/{name}-motion.mp4')])
            run(['-framerate','24','-start_number',str(start),'-i',str(BASE/f'motion-01/{folder}/frame-%04d.png'),'-vf',"scale=144:256,drawtext=fontfile=/System/Library/Fonts/Supplemental/Arial.ttf:text='%{n}':fontsize=12:fontcolor=white:box=1:boxcolor=black@0.6:x=3:y=3,tile=9x8",str(BASE/f'motion-01/{name}-chronology.png')])
        return
    assert sha(PASHTUN)=='1004ed9f2e06d2eafb008c925eb9d266e8a13b8603086020e28d19e3b606722b'
    frames=BASE/'movie-08/frames';assert len(list(frames.glob('frame-*.png')))==528
    out=BASE/'edit-01';out.mkdir(exist_ok=False);font='/System/Library/Fonts/Supplemental/Arial.ttf'
    label=f"drawtext=fontfile={font}:text='DEVELOPMENT - PRINCIPAL RIDER PROXY':fontsize=15:fontcolor=white@0.8:box=1:boxcolor=black@0.35:x=12:y=h-28"
    picture=out/'sikh-picture.mp4'
    run(['-framerate','24','-i',str(frames/'frame-%04d.png'),'-vf',label,'-an','-c:v','libx264','-crf','17','-pix_fmt','yuv420p',str(picture)])
    run(['-i',str(picture),'-i',str(AUDIO/'sikh-mix.wav'),'-map','0:v','-map','1:a','-c:v','copy','-c:a','aac','-b:a','256k','-movflags','+faststart',str(out/'sikh-22s.mp4')])
    filt='[0:v]setsar=1,setpts=PTS-STARTPTS[a];[1:v]scale=1080:1920,setsar=1,setpts=PTS-STARTPTS[b];[a][b]concat=n=2:v=1:a=0[v]'
    run(['-i',str(PASHTUN),'-i',str(picture),'-i',str(AUDIO/'joined-mix.wav'),'-filter_complex',filt,'-map','[v]','-map','2:a','-c:v','libx264','-crf','17','-pix_fmt','yuv420p','-c:a','aac','-b:a','256k','-movflags','+faststart',str(out/'pashtun-sikh-42s.mp4')])
    vf=f"scale=144:256,drawtext=fontfile={font}:text='%{{n}}':fontsize=12:fontcolor=white:box=1:boxcolor=black@0.6:x=3:y=3,tile=8x8"
    run(['-framerate','24','-i',str(frames/'frame-%04d.png'),'-vf',vf,str(out/'chronology-%02d.png')])
    (out/'manifest.json').write_text(json.dumps({'pashtun_native_rendered':False,'pashtun_source_sha256':sha(PASHTUN),'audio_reused':{p.name:sha(p) for p in (AUDIO/'sikh-mix.wav',AUDIO/'joined-mix.wav')},'new_paid_calls':0,'frames':528,'duration_seconds':22,'files':{p.name:sha(p) for p in out.glob('*.mp4')}},indent=2))
    print(out/'pashtun-sikh-42s.mp4')
if __name__=='__main__':main()


