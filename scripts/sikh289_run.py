"""Fixed operation launcher with fresh knowledge admission and sanitized Blender env."""
import hashlib,json,os,sys,subprocess,time,shutil
from pathlib import Path
from movie_factory import production_knowledge as pk
from movie_factory.sikh289_motion import validate_job

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'.runtime/art-direction/series01-sikh289'
BIKE=ROOT/'.runtime/assets/series01-motorcycle289/royal_enfield.glb'

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    operation,version=sys.argv[1:3]
    job=validate_job({'operation':operation,'version':int(version)})
    if not BIKE.exists():
        donor=Path('/Users/adisharma/Downloads/royal_enfield.glb')
        if donor.is_symlink():raise ValueError('No redirected donor')
        BIKE.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(donor,BIKE)
        if sha(donor)!=sha(BIKE):raise ValueError('Copy mismatch')
    bound=['results/sikh289/STRATEGY.md','docs/planning/SERIES_01_SIKH_SEQUENCE.md',
        'docs/knowledge/SIKH_FOUNDATION_REJECTION_271.md','docs/knowledge/CURRENT_PRODUCTION_STATE.md',
        'scripts/sikh289_run.py','scripts/sikh289_native.py','scripts/sikh289_scene.py','src/movie_factory/sikh289_motion.py',
        'scripts/sikh257_native.py','scripts/sikh257_layout.py','src/movie_factory/sikh257_geometry.py',
        str(BIKE.relative_to(ROOT)),'.runtime/assets/demonstrator-01/horse.blend']
    if operation!='inspect':bound.extend([
        '.runtime/art-direction/series01-sikh289/inspect-03/donor.blend',
        '.runtime/art-direction/series01-sikh289/inspect-03/components.json'])
    if operation=='diagnose':bound.append('.runtime/art-direction/series01-sikh289/controls-09/sequence.blend')
    if operation=='camera_patch':bound.append('.runtime/art-direction/series01-sikh289/movie-03/sequence.blend')
    if operation=='reopen':bound.append('.runtime/art-direction/series01-sikh289/camera_patch-01/sequence.blend')
    task={'id':f'sikh289-{operation}-{version}','operation':'motion','entities':['sikh_camera','renderer'],
        'query':'Sikh motorcycle Punjab moonlight crowd parting supported skid horse rear anatomy contacts staging',
        'intent':'Director-authorized staging study with actual motorcycle donor and explicit character stand-ins. No character or production admission.',
        'phase':'execution','inputs':{p:sha(ROOT/p) for p in bound},'open_decisions':[],
        'execution_authority':{'source':'results/sikh289/STRATEGY.md','scope':'Director approves independent staging study then actual motorcycle donor, no paid calls or launch'},'max_context_characters':42000}
    packet=pk.task_packet(ROOT,task);proof=ROOT/'results/sikh289'/f'{operation}-{version}'
    proof.mkdir(parents=True,exist_ok=True)
    for name,data in [('task',task),('packet',packet)]:
        (proof/f'{name}.json').write_text(json.dumps(data,indent=2)+'\n')
    (proof/'packet.md').write_text(pk.packet_markdown(packet))
    if not packet['dispatch_ready']:raise ValueError(packet['blockers'])
    if '--prepare' in sys.argv:print(proof/'packet.md');return
    out=BASE/f'{operation}-{int(version):02d}'
    if out.exists():raise ValueError('Immutable output already exists')
    out.mkdir(parents=True);jp=out/'job.json';jp.write_text(json.dumps(job))
    for p in bound:
        if p.startswith('scripts/') or p.startswith('src/'):
            shutil.copy2(ROOT/p,out/Path(p).name)
    env={k:os.environ[k] for k in ('PATH','HOME','TMPDIR','LANG','LC_ALL') if k in os.environ}
    env['CYCLES_METAL_DISABLE_BINARY_ARCHIVES']='1'
    for key,folder in [('BLENDER_USER_CONFIG','config'),('BLENDER_USER_SCRIPTS','scripts'),('BLENDER_USER_DATAFILES','data')]:env[key]=str(out/'sandbox'/folder)
    start=time.monotonic()
    with (out/'worker.log').open('w') as log:
        p=subprocess.run(['/Applications/Blender.app/Contents/MacOS/Blender','-b','--factory-startup','--disable-autoexec','--python-exit-code','7','--python',str(ROOT/'scripts/sikh289_native.py'),'--',str(jp)],env=env,stdout=log,stderr=subprocess.STDOUT)
    (proof/'receipt.json').write_text(json.dumps({'returncode':p.returncode,'process_seconds':time.monotonic()-start,'packet_digest':packet['packet_digest'],'output':str(out.relative_to(ROOT))},indent=2))
    if p.returncode:raise RuntimeError(str(out/'worker.log'))
    print(out)

if __name__=='__main__':main()
