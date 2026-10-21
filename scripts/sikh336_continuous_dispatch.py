"""Serial admitted evidence extraction; technical receipts are not artistic passes."""
import argparse,json,subprocess,sys,os,shutil
from pathlib import Path
from movie_factory import production_workflow as wf,production_knowledge as pk
from movie_factory.native_admission import Bridge,BLENDER_BIN
from movie_factory.task_router import DATABASE
root=Path(__file__).resolve().parents[1];out=root/'results/sikh335/motion01';task='sikh335-continuous-performance'

def one(step):
    c=wf.Controller(root,DATABASE);b=Bridge(c)
    assert c.state(task)['cycle']==6
    if step=='preserve':
        p=c.packet(task);v=pk.read_json(root,'results/sikh335/motion01/challenge-verdict-c6.json')
        v['input_digest']=p['planning_input_digest']
        c.submit(task,p['actor'],p['ticket'],v,'sikh336-continuous-challenge')
        parent=pk.read_json(root,'results/sikh335/motion01/save-run-c5.json')['artifacts']['native']
    else:
        parent=pk.read_json(root,'results/sikh335/motion01/preserve-run-c6.json')['artifacts']['native']
    steps={s['id']:s for s in c.state(task)['planning_artifacts']['STRATEGIZING']['steps']}
    recipe=steps[step]['native_recipe']
    run=b.dispatch(task,step,f'sikh336-c6-{step}',parent=parent,blender_bin=BLENDER_BIN,timeout=600,recipe=recipe)
    (out/f'{step}-run-c6.json').write_text(json.dumps(run,indent=2)+'\n')
    if run['status']!='RETURNED':raise RuntimeError(run.get('error'))
    if step=='preserve':
        original=pk.read_json(root,'results/sikh335/motion01/save-run-c5.json')
        for name in ('snapshot','dependencies'):
            assert run['artifacts'][name]['sha256']==original['artifacts'][name]['sha256']
    verdict={'verdict':'PASS','run_digest':pk.digest(run),'evidence':run['artifacts'],
             'observation':'Read-only preservation/extraction receipt: exact selected native state and dependencies; requested frame hashes/profile validated by Bridge.',
             'comparison':'This step proves evidence integrity only. Motion, appearance, sound and Director acceptance are not passed; manual continuous_review remains required.',
             'open_defects':[]}
    b.record_review(task,step,verdict)
    (out/f'{step}-technical-review-c6.json').write_text(json.dumps(verdict,indent=2)+'\n')
    print(json.dumps({'step':step,'status':'RETURNED','artistic_pass':False}),flush=True)

def assemble():
    output=root/'.runtime/art-direction/series01-sikh336/motion-diagnostic'
    output.mkdir(parents=True,exist_ok=True);frames={}
    for i in range(13):
        run=pk.read_json(root,f'results/sikh335/motion01/clip{i:02d}-run-c6.json')
        assert run['status']=='RETURNED'
        for key,binding in run['artifacts'].items():
            if key.startswith('frame_'):
                f=int(key[6:]);path=root/binding['path'];assert pk.file_hash(path)==binding['sha256']
                if f in frames:assert frames[f]['sha256']==binding['sha256']
                frames[f]=binding
    assert set(frames)==set(range(252,442))
    for i,f in enumerate(sorted(frames),1):
        destination=output/f'frame-{i:04d}.png';source=root/frames[f]['path']
        if not destination.exists():os.link(source,destination)
        assert pk.file_hash(destination)==frames[f]['sha256']
    movie=output/'motion-diagnostic.mp4'
    if movie.exists():raise RuntimeError('Do not overwrite existing encoded evidence')
    ffmpeg=shutil.which('ffmpeg');ffprobe=shutil.which('ffprobe')
    assert ffmpeg and ffprobe
    subprocess.run([ffmpeg,'-hide_banner','-loglevel','error','-framerate','24','-i',str(output/'frame-%04d.png'),
                    '-frames:v','190','-an','-c:v','libx264','-preset','medium','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(movie)],check=True)
    probe=json.loads(subprocess.check_output([ffprobe,'-v','error','-select_streams','v:0','-count_frames',
                    '-show_entries','stream=nb_read_frames,r_frame_rate,width,height','-of','json',str(movie)],text=True))
    stream=probe['streams'][0];assert stream['nb_read_frames']=='190' and stream['r_frame_rate']=='24/1'
    report={'source_frames':frames,'movie':{'path':str(movie.relative_to(root)),'sha256':pk.file_hash(movie)},
            'probe':probe,'scope':'Internal silent timing diagnostic, unchanged candidate5; no artistic/AV/appearance approval.'}
    (out/'continuous-evidence-c6.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'encoded':str(movie),'frames':190,'artistic_pass':False}),flush=True)

def main():
    p=argparse.ArgumentParser();p.add_argument('--step');p.add_argument('--assemble',action='store_true');a=p.parse_args()
    if a.step:one(a.step);return
    if a.assemble:assemble();return
    for step in ['preserve']+[f'clip{i:02d}' for i in range(13)]:
        receipt=out/f'{step}-technical-review-c6.json'
        if receipt.exists():
            c=wf.Controller(root,DATABASE);b=Bridge(c)
            b.qualified(pk.read_json(root,f'results/sikh335/motion01/{step}-run-c6.json'))
            print('Retained verified step '+step,flush=True);continue
        subprocess.run([sys.executable,'-m','movie_factory.experiment_ops','job','--experiment','SIKH335',
                        '--episode','representation','--phase','continuous-evidence','--id','sikh336-c6-'+step,
                        '--kind','native','--',sys.executable,__file__,'--step',step],cwd=root,check=True)
    assemble()

if __name__=='__main__':main()
