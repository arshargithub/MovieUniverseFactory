"""Source-bound fixed local300 launcher; no credentials or asset scripts."""
import sys,json,os,time,hashlib,subprocess,shutil
from pathlib import Path
from movie_factory import production_knowledge as pk
from movie_factory.sikh300_motion import validate
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'.runtime/art-direction/series01-sikh300'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    op,ver=sys.argv[1:3];j=validate({'operation':op,'version':int(ver)})
    task=json.loads((ROOT/'results/sikh300/task.json').read_text())
    for rel,digest in task['inputs'].items():
        if sha(ROOT/rel)!=digest:raise ValueError('Unreviewed source drift: '+rel)
    paths=['scripts/sikh300_run.py','scripts/sikh300_native.py','src/movie_factory/sikh300_motion.py','results/sikh300/MOTION_BRIEF.md']
    paths += [str(p.relative_to(ROOT)) for p in (ROOT/'scripts').glob('sikh300_scene*.py')]
    if op in ('motion','movie','reopen') or (op=='inspect' and int(ver)>=4):paths.append('.runtime/art-direction/series01-sikh300/controls-08/sequence.blend')
    elif (op=='inspect' and int(ver)==3) or (op=='controls' and int(ver)>=8):paths.append('.runtime/art-direction/series01-sikh300/controls-07/sequence.blend')
    elif op=='controls' and int(ver)>=7:paths.append('.runtime/art-direction/series01-sikh300/controls-06/sequence.blend')
    task['inputs'].update({p:sha(ROOT/p) for p in paths});task.update(id=f'sikh300-{op}-{ver}',phase='execution')
    packet=pk.task_packet(ROOT,task);proof=ROOT/'results/sikh300'/f'{op}-{ver}';proof.mkdir(parents=True,exist_ok=True)
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
    with (out/'worker.log').open('w') as log:p=subprocess.run(['/Applications/Blender.app/Contents/MacOS/Blender','-b','--factory-startup','--disable-autoexec','--python-exit-code','7','--python',str(ROOT/'scripts/sikh300_native.py'),'--',str(jp)],env=env,stdout=log,stderr=subprocess.STDOUT)
    (proof/'receipt.json').write_text(json.dumps({'returncode':p.returncode,'process_seconds':time.monotonic()-start,'packet_digest':packet['packet_digest'],'output':str(out.relative_to(ROOT))},indent=2))
    if p.returncode:raise RuntimeError(str(out/'worker.log'))
    print(out)
if __name__=='__main__':main()
