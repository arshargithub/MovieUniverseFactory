"""Bounded local331 jobs. Reviewed handlers only; no executable input strings."""
import json, os, subprocess, sys, time, shutil
from pathlib import Path
from movie_factory import production_knowledge as pk
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'.runtime/art-direction/series01-sikh331'
SOURCE=ROOT/'.runtime/art-direction/series01-sikh320/build-10/sequence.blend'
def validate(j):
    if set(j)!={'operation','version','frames'}: raise ValueError('Unexpected fields')
    if j['operation'] not in ('inspect','pose','look','motion'): raise ValueError('Unknown operation')
    if type(j['version']) is not int or not 1<=j['version']<=20: raise ValueError('Version')
    if not isinstance(j['frames'],list) or not 1<=len(j['frames'])<=8: raise ValueError('Frames')
    if any(type(f) is not int or not 252<=f<=441 for f in j['frames']): raise ValueError('Frame range')
    return j
def source(j):
    return SOURCE if j['operation'] in ('inspect','pose') else BASE/f"pose-{j['version']:02d}/sequence.blend"
def require_open(root=ROOT):
    """Package closure, not a generally qualified native-authoring controller."""
    status=root/'results/sikh331/STATUS.json'
    if status.exists():
        record=json.loads(status.read_text())
        if record.get('native_dispatch_closed') is not False:
            raise ValueError('SIKH331_REPLAN_REQUIRED: no further native dispatch or renamed variant allowance')
def main():
    require_open()
    j=validate({'operation':sys.argv[1],'version':int(sys.argv[2]),'frames':[int(x) for x in sys.argv[3].split(',')]})
    op,v=j['operation'],j['version']; record=ROOT/f'results/sikh331/{op}-{v:02d}'
    paths=[source(j),ROOT/'results/sikh331/STRATEGY.md',ROOT/'results/workflow330/NIHANG_PROSPECTIVE_BRIEF.md',ROOT/'results/sikh321/evidence.json']
    paths += list((ROOT/'scripts').glob('sikh331*.py'))
    paths += [ROOT/'src/movie_factory/sikh331_motion.py',ROOT/'src/movie_factory/sikh318_motion.py',ROOT/'scripts/sikh305_scene.py',ROOT/'scripts/sikh320_performance.py']
    task=json.loads((ROOT/'results/sikh320/build-1/task.json').read_text())
    task.update(id=f'sikh331-{op}-{v}',query='Nihang supported whole horse rider rearing pose anatomy contact cloth face saddle crowd attention same film proof',intent='Director331 frozen330 production proof',inputs={str(p.relative_to(ROOT)):pk.file_hash(p) for p in paths},execution_authority={'source':'results/sikh331/STRATEGY.md','scope':'Local isolated native proof; no paid calls or egress'})
    packet=pk.task_packet(ROOT,task)
    record.mkdir(parents=True,exist_ok=True)
    for name,value in [('task',task),('packet',packet)]: (record/(name+'.json')).write_text(json.dumps(value,indent=2))
    (record/'packet.md').write_text(pk.packet_markdown(packet))
    if not packet['dispatch_ready']: raise ValueError(packet['blockers'])
    if '--prepare' in sys.argv: print(record/'packet.md');return
    out=BASE/f'{op}-{v:02d}';out.mkdir(parents=True,exist_ok=False);(out/'frames').mkdir()
    for p in paths:
        if p.suffix in ('.py','.md'):
            target=out/'source-snapshot'/p.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target)
    job=out/'job.json';job.write_text(json.dumps(j))
    env={k:os.environ[k] for k in ('PATH','LANG','LC_ALL') if k in os.environ}
    for key,sub in [('HOME','home'),('TMPDIR','tmp'),('BLENDER_USER_CONFIG','config'),('BLENDER_USER_SCRIPTS','scripts'),('BLENDER_USER_DATAFILES','data')]:
        p=out/'sandbox'/sub;p.mkdir(parents=True);env[key]=str(p)
    for p,h in task['inputs'].items(): assert pk.file_hash(ROOT/p)==h
    tick=time.monotonic()
    with (out/'worker.log').open('x') as log:
        run=subprocess.run(['/Applications/Blender.app/Contents/MacOS/Blender','-b','--factory-startup','--disable-autoexec','--offline-mode','--python-exit-code','7','--python',str(ROOT/'scripts/sikh331_native.py'),'--',str(job)],env=env,stdout=log,stderr=subprocess.STDOUT)
    (out/'receipt.json').write_text(json.dumps({'seconds':time.monotonic()-tick,'exit':run.returncode,'job':j},indent=2))
    for p,h in task['inputs'].items(): assert pk.file_hash(ROOT/p)==h
    if run.returncode: raise RuntimeError(str(out/'worker.log'))
    print(out)
if __name__=='__main__': main()
