"""Fresh knowledge-bound local launcher for allowlisted299 operations."""
import sys,json,os,time,hashlib,subprocess,shutil
from pathlib import Path
from movie_factory import production_knowledge as pk
from movie_factory.sikh299_motion import validate
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'.runtime/art-direction/series01-sikh299'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    op,ver=sys.argv[1:3];j=validate({'operation':op,'version':int(ver)})
    task=json.loads((ROOT/'results/sikh299/task.json').read_text())
    # Verify inherited source bindings, never rehash historical sources to hide drift.
    for rel,digest in task['inputs'].items():
        if sha(ROOT/rel)!=digest:raise ValueError('Unreviewed source drift: '+rel)
    paths=['scripts/sikh299_run.py','scripts/sikh299_native.py','scripts/sikh299_scene.py','src/movie_factory/sikh299_motion.py','results/sikh299/MOTION_BRIEF.md','results/sikh299/MOON_PROVENANCE.md','.runtime/art-direction/series01-sikh299/moon/lroc_color_2k.jpg']
    if op in ('motion','movie','reopen'):paths+=['.runtime/art-direction/series01-sikh299/'+('controls-06' if op=='motion' else 'controls-07')+'/sequence.blend']
    if op=='inspect' and int(ver)>=3:paths+=['.runtime/art-direction/series01-sikh299/controls-04/sequence.blend']
    if op=='controls' and int(ver)>=6:paths+=['.runtime/art-direction/series01-sikh299/'+('controls-05' if int(ver)==6 else 'controls-06')+'/sequence.blend']
    task['inputs'].update({p:sha(ROOT/p) for p in paths});task.update(id=f'sikh299-{op}-{ver}',phase='execution')
    packet=pk.task_packet(ROOT,task);proof=ROOT/'results/sikh299'/f'{op}-{ver}';proof.mkdir(parents=True,exist_ok=True)
    for name,data in [('task',task),('packet',packet)]:(proof/(name+'.json')).write_text(json.dumps(data,indent=2)+'\n')
    (proof/'packet.md').write_text(pk.packet_markdown(packet))
    if not packet['dispatch_ready']:raise ValueError(packet['blockers'])
    if '--prepare' in sys.argv:print(proof/'packet.md');return
    out=BASE/f'{op}-{int(ver):02d}';out.mkdir(parents=True,exist_ok=False);jp=out/'job.json';jp.write_text(json.dumps(j));snap=out/'source';snap.mkdir()
    for rel,digest in task['inputs'].items():
        if Path(rel).suffix=='.py':
            dest=snap/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/rel,dest)
            if sha(dest)!=digest:raise ValueError('Source changed')
    (snap/'bindings.json').write_text(json.dumps(task['inputs'],indent=2))
    env={k:os.environ[k] for k in ('PATH','HOME','TMPDIR','LANG','LC_ALL') if k in os.environ};env['CYCLES_METAL_DISABLE_BINARY_ARCHIVES']='1'
    for k,d in [('BLENDER_USER_CONFIG','config'),('BLENDER_USER_SCRIPTS','scripts'),('BLENDER_USER_DATAFILES','data')]:env[k]=str(out/'sandbox'/d)
    start=time.monotonic()
    with (out/'worker.log').open('w') as log:
        p=subprocess.run(['/Applications/Blender.app/Contents/MacOS/Blender','-b','--factory-startup','--disable-autoexec','--python-exit-code','7','--python',str(ROOT/'scripts/sikh299_native.py'),'--',str(jp)],env=env,stdout=log,stderr=subprocess.STDOUT)
    (proof/'receipt.json').write_text(json.dumps({'returncode':p.returncode,'process_seconds':time.monotonic()-start,'packet_digest':packet['packet_digest'],'output':str(out.relative_to(ROOT))},indent=2))
    if p.returncode:raise RuntimeError(str(out/'worker.log'))
    print(out)
if __name__=='__main__':main()
