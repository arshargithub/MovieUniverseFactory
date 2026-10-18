"""Fixed local operations; fresh source-bound knowledge gate, isolated Blender."""
import sys,json,os,subprocess,hashlib,shutil,time
from pathlib import Path
from movie_factory import production_knowledge as pk
from movie_factory.sikh305_motion import validate
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'.runtime/art-direction/series01-sikh305'
SOURCE=ROOT/'.runtime/art-direction/series01-sikh304/repair-build-03/sequence.blend'
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
    return h.hexdigest()
def main():
    op,v=sys.argv[1],int(sys.argv[2]);j=validate({'operation':op,'version':v})
    task=json.loads((ROOT/'results/sikh304/movie-8/task.json').read_text())
    for rel,h in task['inputs'].items():
        if sha(ROOT/rel)!=h:raise ValueError('Parent source drift: '+rel)
    parent=7 if op=='refine' and v==9 else 11 if op=='finish' and v==13 else v-1
    source=SOURCE if op in ('inspect','build') else BASE/f'build-{parent if op in ("refine","finish") else v:02d}/sequence.blend'
    paths=[source,ROOT/'results/sikh305/STRATEGY.md',ROOT/'src/movie_factory/sikh305_motion.py']+[ROOT/'scripts'/('sikh305_'+n+'.py') for n in ('run','native','scene','land','audit','finish','impacts')]
    if op in ('refine','finish'):paths.append(BASE/f'build-{parent:02d}/source/bindings.json')
    task.update(id=f'sikh305-{op}-{v}',intent='Director305 integrated camera/action/horse/environment correction; preserve stop location per amendment; extended departure',phase='execution')
    task['entities']+=['nihang_leader','nihang_horse']
    task['inputs'].update({str(p.relative_to(ROOT)):sha(p) for p in paths})
    task['execution_authority']={'source':'results/sikh305/STRATEGY.md','scope':'Local reversible entire correction; no spend, installation, upload or principal admission'}
    packet=pk.task_packet(ROOT,task);proof=ROOT/'results/sikh305'/f'{op}-{v}';proof.mkdir(parents=True,exist_ok=True)
    for name,data in [('task',task),('packet',packet)]:(proof/(name+'.json')).write_text(json.dumps(data,indent=2)+'\n')
    (proof/'packet.md').write_text(pk.packet_markdown(packet))
    if not packet['dispatch_ready']:raise ValueError(packet['blockers'])
    if '--prepare' in sys.argv:print(proof/'packet.md');return
    out=BASE/f'{"build" if op in ("refine","finish") else op}-{v:02d}';out.mkdir(parents=True,exist_ok=False)
    snap=out/'source';snap.mkdir()
    for rel,h in task['inputs'].items():
        if Path(rel).suffix=='.py':
            target=snap/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/rel,target)
            if sha(target)!=h:raise ValueError('Dispatch drift')
    (snap/'bindings.json').write_text(json.dumps(task['inputs'],indent=2))
    jp=out/'job.json';jp.write_text(json.dumps(j))
    env={k:os.environ[k] for k in ('PATH','HOME','TMPDIR','LANG','LC_ALL') if k in os.environ}
    for k,d in [('BLENDER_USER_CONFIG','config'),('BLENDER_USER_SCRIPTS','scripts'),('BLENDER_USER_DATAFILES','data')]:env[k]=str(out/'sandbox'/d)
    started=time.monotonic()
    with (out/'worker.log').open('w') as log:
        result=subprocess.run(['/Applications/Blender.app/Contents/MacOS/Blender','-b','--factory-startup','--disable-autoexec','--offline-mode','--python-exit-code','7','--python',str(ROOT/'scripts/sikh305_native.py'),'--',str(jp)],env=env,stdout=log,stderr=subprocess.STDOUT)
    (proof/'receipt.json').write_text(json.dumps({'returncode':result.returncode,'process_seconds':time.monotonic()-started,'packet_digest':packet['packet_digest']},indent=2))
    if result.returncode:raise RuntimeError(str(out/'worker.log'))
    print(out)
if __name__=='__main__':main()
