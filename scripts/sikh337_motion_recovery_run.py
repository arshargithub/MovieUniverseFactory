"""Complete admitted remaining images serially, preserving old immutable frames."""
import json,subprocess,sys,os,hashlib
from PIL import Image
from pathlib import Path
from movie_factory import production_workflow as wf,production_knowledge as pk
from movie_factory.native_admission import Bridge,BLENDER_BIN
from movie_factory.task_router import DATABASE
root=Path(__file__).resolve().parents[1];out=root/'results/sikh335/motion01';task='sikh335-continuous-performance'
def one(step):
    c=wf.Controller(root,DATABASE);b=Bridge(c);assert c.state(task)['cycle']==9
    if step=='preserve':
        p=c.packet(task);v=pk.read_json(root,'results/sikh335/motion01/challenge-verdict-c9.json')
        v['input_digest']=p['planning_input_digest'];c.submit(task,p['actor'],p['ticket'],v,'sikh337-motion-c9-challenge')
        parent=pk.read_json(root,'results/sikh335/motion01/save-run-c5.json')['artifacts']['native']
    else:parent=pk.read_json(root,'results/sikh335/motion01/preserve-run-c9.json')['artifacts']['native']
    stepdata=next(s for s in c.state(task)['planning_artifacts']['STRATEGIZING']['steps'] if s['id']==step)
    dest=out/f'{step}-run-c9.json';assert not dest.exists()
    run=b.dispatch(task,step,'sikh337-c9-'+step,parent=parent,blender_bin=BLENDER_BIN,timeout=600,recipe=stepdata['native_recipe'])
    dest.write_text(json.dumps(run,indent=2)+'\n')
    if run['status']!='RETURNED':raise RuntimeError(run.get('error'))
    original=pk.read_json(root,'results/sikh335/motion01/save-run-c5.json')
    for name in ('snapshot','dependencies'):assert run['artifacts'][name]['sha256']==original['artifacts'][name]['sha256']
    review={'verdict':'PASS','run_digest':pk.digest(run),'evidence':run['artifacts'],
      'observation':'Exact selected candidate5 state/dependencies retained; native frame/profile hashes verified. Evidence extraction only.',
      'comparison':'No motion, appearance, audio or Director acceptance. Actual-frame review remains required; known appearance defects remain open outside extraction scope.',
      'open_defects':[]}
    b.record_review(task,step,review);(out/f'{step}-technical-review-c9.json').write_text(json.dumps(review,indent=2)+'\n')
    print(json.dumps({'step':step,'status':'RETURNED','artistic_pass':False}),flush=True)
def assemble():
    output=root/'.runtime/art-direction/series01-sikh337/motion-diagnostic-c9';output.mkdir(parents=True,exist_ok=True)
    frames={}
    for i in range(13):
        cycle=6 if i<6 else 9
        path=(f'results/sikh335/motion01/clip{i:02d}-run-c{cycle}.json' if i!=6 else 'results/sikh335/motion01/clip06-historical-source.json')
        run=pk.read_json(root,path)
        assert run['status']==('HISTORICAL_WORKER_OUTPUT_NOT_NATIVE_ADMITTED' if i==6 else 'RETURNED')
        for key,b in run['artifacts'].items():
            if key.startswith('frame_'):
                f=int(key[6:]);assert pk.file_hash(root/b['path'])==b['sha256']
                if f in frames:
                    with Image.open(root/frames[f]['path']) as a,Image.open(root/b['path']) as other:
                        assert a.size==other.size and a.convert('RGBA').tobytes()==other.convert('RGBA').tobytes()
                frames[f]=b
    assert set(frames)==set(range(252,442))
    for i,f in enumerate(sorted(frames),1):
        dest=output/f'frame-{i:04d}.png'
        if not dest.exists():os.link(root/frames[f]['path'],dest)
        assert pk.file_hash(dest)==frames[f]['sha256']
    movie=output/'motion-diagnostic.mp4';assert not movie.exists()
    subprocess.run(['/opt/homebrew/bin/ffmpeg','-hide_banner','-loglevel','error','-framerate','24','-i',str(output/'frame-%04d.png'),'-frames:v','190','-an','-c:v','libx264','-crf','18','-pix_fmt','yuv420p','-movflags','+faststart',str(movie)],check=True)
    probe=json.loads(subprocess.check_output(['/opt/homebrew/bin/ffprobe','-v','error','-select_streams','v:0','-count_frames','-show_entries','stream=nb_read_frames,r_frame_rate,width,height','-of','json',str(movie)]))
    assert probe['streams'][0]['nb_read_frames']=='190' and probe['streams'][0]['r_frame_rate']=='24/1'
    (out/'continuous-evidence-c9.json').write_text(json.dumps({'frames':frames,'probe':probe,'movie':{'path':str(movie.relative_to(root)),'sha256':pk.file_hash(movie)},'scope':'Silent internal timing evidence only; first105 frames include verified historical outputs and explicitly unadmitted c8 worker images; no artistic pass.'},indent=2)+'\n')
if len(sys.argv)>1:one(sys.argv[1])
else:
    for step in ['preserve']+[f'clip{i:02d}' for i in range(7,13)]:
        subprocess.run([sys.executable,'-m','movie_factory.experiment_ops','job','--experiment','SIKH335','--episode','representation','--phase','continuous-evidence','--id','sikh337-c9-'+step,'--kind','native','--',sys.executable,__file__,step],cwd=root,check=True)
    assemble()
