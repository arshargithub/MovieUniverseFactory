"""Fresh knowledge gate, immutable output and isolated fixed Blender handler."""
import sys,json,os,time,hashlib,subprocess,shutil
from pathlib import Path
from movie_factory import production_knowledge as pk
from movie_factory.sikh292_motion import validate_job
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    op,ver=sys.argv[1:3];job=validate_job({'operation':op,'version':int(ver)})
    old=json.loads((ROOT/'results/sikh291/reopen-1/task.json').read_text())
    paths=list(old['inputs']);paths.remove('.runtime/art-direction/series01-sikh291/movie-03/sequence.blend')
    paths+=['results/sikh292/STRATEGY.md','scripts/sikh292_run.py','scripts/sikh292_native.py','scripts/sikh292_scene.py','scripts/sikh292_assets.py','src/movie_factory/sikh292_motion.py','.runtime/assets/series01-body-blender-studio/human-base-meshes-bundle-v1.4.1/human_base_meshes_bundle.blend']
    paths+=['src/movie_factory/sikh257_contract.py']
    if op=='reopen':paths+=['.runtime/art-direction/series01-sikh292/movie-01/sequence.blend']
    old.update(id=f'sikh292-{op}-{ver}',intent='Director292 substantial environmental/crowd/horse fidelity with corrected stop/sky/tire response; main actor explicitly provisional, not admitted.',inputs={p:sha(ROOT/p) for p in paths},execution_authority={'source':'results/sikh292/STRATEGY.md','scope':'Director292 local substantial fidelity and joined music preview, no new spend/install/cloud/publication'})
    p=pk.task_packet(ROOT,old);proof=ROOT/'results/sikh292'/f'{op}-{ver}';proof.mkdir(parents=True,exist_ok=True)
    for name,data in [('task',old),('packet',p)]: (proof/(name+'.json')).write_text(json.dumps(data,indent=2)+'\n')
    (proof/'packet.md').write_text(pk.packet_markdown(p))
    if not p['dispatch_ready']:raise ValueError(p['blockers'])
    if '--prepare' in sys.argv:print(proof/'packet.md');return
    out=ROOT/'.runtime/art-direction/series01-sikh292'/f'{op}-{int(ver):02d}'
    out.mkdir(parents=True,exist_ok=False);jp=out/'job.json';jp.write_text(json.dumps(job))
    # Immutable copies of every bound handler support later reconstruction;
    # assets stay content-hash bound without duplicating large native files.
    snapshot=out/'source';snapshot.mkdir()
    for rel,digest in old['inputs'].items():
        if Path(rel).suffix=='.py':
            target=snapshot/rel;target.parent.mkdir(parents=True,exist_ok=True)
            shutil.copy2(ROOT/rel,target)
            if sha(target)!=digest:raise ValueError('Source changed during snapshot: '+rel)
    (snapshot/'bindings.json').write_text(json.dumps(old['inputs'],indent=2))
    env={k:os.environ[k] for k in ('PATH','HOME','TMPDIR','LANG','LC_ALL') if k in os.environ};env['CYCLES_METAL_DISABLE_BINARY_ARCHIVES']='1'
    for k,d in [('BLENDER_USER_CONFIG','config'),('BLENDER_USER_SCRIPTS','scripts'),('BLENDER_USER_DATAFILES','data')]:env[k]=str(out/'sandbox'/d)
    start=time.monotonic()
    with (out/'worker.log').open('w') as log:r=subprocess.run(['/Applications/Blender.app/Contents/MacOS/Blender','-b','--factory-startup','--disable-autoexec','--python-exit-code','7','--python',str(ROOT/'scripts/sikh292_native.py'),'--',str(jp)],env=env,stdout=log,stderr=subprocess.STDOUT)
    (proof/'receipt.json').write_text(json.dumps({'returncode':r.returncode,'process_seconds':time.monotonic()-start,'packet_digest':p['packet_digest'],'output':str(out.relative_to(ROOT))},indent=2))
    if r.returncode:raise RuntimeError(str(out/'worker.log'))
    print(out)
if __name__=='__main__':main()
