"""Dedicated fixed replay launcher; leaves dispatched movie sources unchanged."""
import sys,json,os,time,hashlib,subprocess,shutil
from pathlib import Path
from movie_factory import production_knowledge as pk
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'.runtime/art-direction/series01-sikh300'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    task=json.loads((ROOT/'results/sikh300/movie-1/task.json').read_text())
    for rel,digest in task['inputs'].items():
        if sha(ROOT/rel)!=digest:raise ValueError('Unreviewed source drift: '+rel)
    task['inputs'].update({p:sha(ROOT/p) for p in ('scripts/sikh300_reopen_run.py','scripts/sikh300_reopen.py')});task.update(id='sikh300-reopen-1',phase='execution')
    packet=pk.task_packet(ROOT,task);proof=ROOT/'results/sikh300/reopen-1';proof.mkdir(parents=True,exist_ok=True)
    for name,data in [('task',task),('packet',packet)]:(proof/(name+'.json')).write_text(json.dumps(data,indent=2)+'\n')
    (proof/'packet.md').write_text(pk.packet_markdown(packet))
    if not packet['dispatch_ready']:raise ValueError(packet['blockers'])
    if '--prepare' in sys.argv:print(proof/'packet.md');return
    out=BASE/'reopen-01';out.mkdir(exist_ok=False);jp=out/'job.json';jp.write_text(json.dumps({'operation':'reopen','version':1}));snap=out/'source';snap.mkdir()
    for rel,digest in task['inputs'].items():
        if Path(rel).suffix=='.py':
            dest=snap/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/rel,dest)
            if sha(dest)!=digest:raise ValueError('Source changed')
    (snap/'bindings.json').write_text(json.dumps(task['inputs'],indent=2))
    env={k:os.environ[k] for k in ('PATH','HOME','TMPDIR','LANG','LC_ALL') if k in os.environ};env['CYCLES_METAL_DISABLE_BINARY_ARCHIVES']='1'
    for k,d in [('BLENDER_USER_CONFIG','config'),('BLENDER_USER_SCRIPTS','scripts'),('BLENDER_USER_DATAFILES','data')]:env[k]=str(out/'sandbox'/d)
    start=time.monotonic()
    with (out/'worker.log').open('w') as log:p=subprocess.run(['/Applications/Blender.app/Contents/MacOS/Blender','-b','--factory-startup','--disable-autoexec','--python-exit-code','7','--python',str(ROOT/'scripts/sikh300_reopen.py'),'--',str(jp)],env=env,stdout=log,stderr=subprocess.STDOUT)
    (proof/'receipt.json').write_text(json.dumps({'returncode':p.returncode,'process_seconds':time.monotonic()-start,'packet_digest':packet['packet_digest'],'output':str(out.relative_to(ROOT))},indent=2))
    if p.returncode:raise RuntimeError(str(out/'worker.log'))
    print(out)
if __name__=='__main__':main()
