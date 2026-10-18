"""Sanitized local launcher with fresh knowledge packet and pinned sources."""
import sys,json,os,subprocess,hashlib,shutil,time
from pathlib import Path
from movie_factory import production_knowledge as pk
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'.runtime/art-direction/series01-sikh304'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    op,v=sys.argv[1],int(sys.argv[2])
    if op not in ('control','build','render','reopen') or v not in (1,2,3):raise ValueError('Unadmitted repair')
    src=BASE/('build-08/sequence.blend' if op in ('control','build') else f'repair-build-{v:02d}/sequence.blend')
    task=json.loads((ROOT/'results/sikh304/movie-8/task.json').read_text())
    for rel,h in task['inputs'].items():
        if sha(ROOT/rel)!=h:raise ValueError('Parent input drift '+rel)
    paths=[Path(__file__),ROOT/'scripts/repair304_native.py',ROOT/'results/sikh304/FORELIMB_REASSESSMENT.md',src]
    task.update(id=f'sikh304-repair-{op}-{v}',intent='Correct horse carpal folding within authorized304 whole scene; all other action protected')
    task['inputs'].update({str(p.relative_to(ROOT)):sha(p) for p in paths})
    packet=pk.task_packet(ROOT,task);proof=ROOT/'results/sikh304'/f'repair-{op}-{v}';proof.mkdir(exist_ok=True)
    for name,data in [('task',task),('packet',packet)]:(proof/(name+'.json')).write_text(json.dumps(data,indent=2))
    (proof/'packet.md').write_text(pk.packet_markdown(packet))
    if not packet['dispatch_ready']:raise ValueError(packet['blockers'])
    if '--prepare' in sys.argv:print(proof/'packet.md');return
    out=BASE/f'repair-{op}-{v:02d}';out.mkdir(exist_ok=False);snap=out/'source';snap.mkdir()
    for rel,h in task['inputs'].items():
        if Path(rel).suffix=='.py':
            dest=snap/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/rel,dest)
            if sha(dest)!=h:raise ValueError('Dispatch drift')
    (snap/'bindings.json').write_text(json.dumps(task['inputs'],indent=2))
    jp=out/'job.json';jp.write_text(json.dumps({'operation':op,'variant':v}))
    env={k:os.environ[k] for k in ('PATH','HOME','TMPDIR','LANG','LC_ALL') if k in os.environ};env['CYCLES_METAL_DISABLE_BINARY_ARCHIVES']='1'
    for k,d in [('BLENDER_USER_CONFIG','config'),('BLENDER_USER_SCRIPTS','scripts'),('BLENDER_USER_DATAFILES','data')]:env[k]=str(out/'sandbox'/d)
    start=time.monotonic()
    with (out/'worker.log').open('w') as log:p=subprocess.run(['/Applications/Blender.app/Contents/MacOS/Blender','-b','--factory-startup','--disable-autoexec','--offline-mode','--python-exit-code','7','--python',str(ROOT/'scripts/repair304_native.py'),'--',str(jp)],env=env,stdout=log,stderr=subprocess.STDOUT)
    (proof/'receipt.json').write_text(json.dumps({'returncode':p.returncode,'process_seconds':time.monotonic()-start,'packet_digest':packet['packet_digest']},indent=2))
    if p.returncode:raise RuntimeError(str(out/'worker.log'))
    print(out)
if __name__=='__main__':main()
