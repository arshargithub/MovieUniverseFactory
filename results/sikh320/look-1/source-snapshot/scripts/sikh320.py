"""Local, fixed Sikh320 shot-isolation jobs. No executable input payloads."""
import json,os,subprocess,sys,shutil,time
from pathlib import Path
from movie_factory import production_knowledge as pk
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'.runtime/art-direction/series01-sikh320'
SOURCE=ROOT/'.runtime/art-direction/series01-sikh319/refine-19/sequence.blend'
START,END=252,441
def validate(j):
    assert set(j)=={'operation','version','frames'}
    assert j['operation'] in ('inspect','build','look','motion','reopen')
    assert type(j['version']) is int and 1<=j['version']<=20
    assert isinstance(j['frames'],list) and 1<=len(j['frames'])<=6
    assert all(type(f) is int and START<=f<=END for f in j['frames'])
    return j
def source(op,v):return SOURCE if op in ('inspect','build') else BASE/f'build-{v:02d}/sequence.blend'
def main():
    op=sys.argv[1];v=int(sys.argv[2]);validate({'operation':op,'version':v,'frames':[START]})
    task=json.loads((ROOT/'results/sikh319/movie-19/task.json').read_text())
    task.update(id=f'sikh320-{op}-{v}',intent='Isolated leader/rear and crowd performance and costume realism,24-frame context handles',execution_authority={'source':'results/sikh320/STRATEGY.md','scope':'Director320 local isolated corrections; no provider or egress'})
    paths={ROOT/p for p in task['inputs'] if p.endswith('.py')}
    paths.update([source(op,v),ROOT/'results/sikh320/STRATEGY.md',ROOT/'docs/knowledge/CONSTRUCTION_INTERFACES_319.md'])
    paths.update(ROOT/'scripts'/p for p in ('sikh320.py','sikh320_native.py','sikh320_performance.py','sikh320_costume.py'))
    task['inputs']={str(p.relative_to(ROOT)):pk.file_hash(p) for p in paths}
    packet=pk.task_packet(ROOT,task);assert packet['dispatch_ready'],packet['blockers']
    record=ROOT/f'results/sikh320/{op}-{v}';record.mkdir(parents=True,exist_ok=True)
    for name,value in [('task',task),('packet',packet)]: (record/(name+'.json')).write_text(json.dumps(value,indent=2))
    (record/'packet.md').write_text(pk.packet_markdown(packet))
    if '--prepare' in sys.argv: print(record/'packet.md');return
    out=BASE/f'{op}-{v:02d}';out.mkdir(parents=True,exist_ok=False);(out/'frames').mkdir()
    for p in paths:
        if p.suffix in ('.py','.md'):
            dest=record/'source-snapshot'/p.relative_to(ROOT);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
    frames=list(range(START,END+1)) if op=='motion' else [276,298,321,344,381,417] if op in ('look','reopen') else [START]
    for k in range(0,len(frames),6):
        fs=frames[k:k+6];folder=out/'chunks'/str(fs[0]);folder.mkdir(parents=True)
        j=folder/'job.json';j.write_text(json.dumps(validate({'operation':op,'version':v,'frames':fs})))
        assert all(pk.file_hash(ROOT/p)==h for p,h in task['inputs'].items())
        env={k:os.environ[k] for k in ('PATH','HOME','TMPDIR','LANG','LC_ALL') if k in os.environ}
        for key,sub in [('BLENDER_USER_CONFIG','config'),('BLENDER_USER_SCRIPTS','scripts'),('BLENDER_USER_DATAFILES','data')]:env[key]=str(folder/'sandbox'/sub)
        tick=time.time()
        with (folder/'worker.log').open('x') as log:
            run=subprocess.run(['/Applications/Blender.app/Contents/MacOS/Blender','-b','--factory-startup','--disable-autoexec','--offline-mode','--python-exit-code','7','--python',str(ROOT/'scripts/sikh320_native.py'),'--',str(j)],env=env,stdout=log,stderr=subprocess.STDOUT)
        (folder/'receipt.json').write_text(json.dumps({'frames':fs,'seconds':time.time()-tick,'exit':run.returncode}))
        assert run.returncode==0,folder/'worker.log'
        print(f'{op} {fs[0]}..{fs[-1]} complete',flush=True)
    print(out)
if __name__=='__main__':main()
