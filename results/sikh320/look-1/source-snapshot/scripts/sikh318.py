"""Fixed, local, source-bound318 operations. No external code or provider inputs."""
import json,os,sys,subprocess,time,shutil
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from movie_factory import production_knowledge as pk
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'.runtime/art-direction/series01-sikh318'
SOURCE=ROOT/'.runtime/art-direction/series01-sikh317/build-08/sequence.blend'
OPS=('inspect','build','look','movie','reopen','check')
def source_for(op,v):
    if op=='inspect' or (op=='build' and v<3):return SOURCE
    if op=='build':return BASE/'build-01/sequence.blend'
    return BASE/f'build-{v:02d}/sequence.blend'
def validate(j):
    if set(j)!={'operation','version','start','end'} or j['operation'] not in OPS:raise ValueError('Invalid operation')
    if type(j['version']) is not int or not 1<=j['version']<=4:raise ValueError('Invalid version')
    if any(type(j[k]) is not int for k in ('start','end')) or not 1<=j['start']<=j['end']<=696 or j['end']-j['start']>=6:raise ValueError('Invalid batch')
    return j
def main():
    op=sys.argv[1];v=int(sys.argv[2]);validate(dict(operation=op,version=v,start=1,end=1))
    source=source_for(op,v)
    task=json.loads((ROOT/'results/sikh317/build-8/task.json').read_text())
    task.update(id=f'sikh318-{op}-{v}',intent='Continuous rearing dark horse grounded ditch and supporting cast review',
        execution_authority={'source':'results/sikh318/STRATEGY.md','scope':'Director318 local horse/ditch correction and supporting fidelity review; no new providers spend or principal change'})
    paths=[source,ROOT/'results/sikh318/STRATEGY.md',ROOT/'scripts/sikh318.py',ROOT/'scripts/sikh318_native.py',ROOT/'src/movie_factory/sikh318_motion.py']
    # Preserve the reviewed helper dependency bindings, not just the entrypoint.
    for p in task['inputs']:
        if p.endswith('.py'):paths.append(ROOT/p)
    paths += [ROOT/'scripts/check317.py',ROOT/'scripts/render317_native.py',ROOT/'scripts/sikh317_scene.py',ROOT/'scripts/sikh315_scene.py',ROOT/'scripts/sikh305_scene.py',ROOT/'scripts/sikh305_impacts.py']
    task['inputs']={str(p.relative_to(ROOT)):pk.file_hash(p) for p in set(paths)}
    packet=pk.task_packet(ROOT,task);assert packet['dispatch_ready'],packet['blockers']
    dest=ROOT/f'results/sikh318/{op}-{v}';dest.mkdir(parents=True,exist_ok=True)
    for n,d in (('task',task),('packet',packet)):(dest/(n+'.json')).write_text(json.dumps(d,indent=2))
    (dest/'packet.md').write_text(pk.packet_markdown(packet))
    if '--prepare' in sys.argv:print(dest/'packet.md');return
    out=BASE/f'{op}-{v:02d}';out.mkdir(parents=True,exist_ok=False);(out/'frames').mkdir()
    (out/'bindings.json').write_text(json.dumps(task['inputs'],indent=2))
    for p in set(paths):
        if p.suffix in ('.py','.md'):
            q=out/'source-snapshot'/p.relative_to(ROOT);q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
    env={k:os.environ[k] for k in ('PATH','HOME','TMPDIR','LANG','LC_ALL') if k in os.environ}
    for k,d in (('BLENDER_USER_CONFIG','config'),('BLENDER_USER_SCRIPTS','scripts'),('BLENDER_USER_DATAFILES','data')):env[k]=str(out/'sandbox'/d)
    if op=='movie':windows=[(275,358),(1,274),(359,696)]
    elif op=='look':windows=[(f,f) for f in (283,324,333,350,1,80,126,294,306,315,342,380,450,600)]
    elif op=='reopen':windows=[(f,f) for f in (80,294,315,324,342,350,380,600)]
    else:windows=[(1,1)]
    receipts=[];batches=[(start,min(b,start+5)) for a,b in windows for start in range(a,b+1,6)]
    def batch(pair):
        start,end=pair;folder=out/'chunks'/str(start);folder.mkdir(parents=True)
        j=validate(dict(operation=op,version=v,start=start,end=end));job=folder/'job.json';job.write_text(json.dumps(j))
        assert all(pk.file_hash(ROOT/p)==h for p,h in task['inputs'].items()),'Changed input'
        local_env=env.copy()
        for k,d in (('BLENDER_USER_CONFIG','config'),('BLENDER_USER_SCRIPTS','scripts'),('BLENDER_USER_DATAFILES','data')):local_env[k]=str(folder/'sandbox'/d)
        tick=time.monotonic();epoch=time.time()
        with (folder/'worker.log').open('x') as log:
            r=subprocess.run(['/Applications/Blender.app/Contents/MacOS/Blender','-b','--factory-startup','--disable-autoexec','--offline-mode','--python-exit-code','7','--python',str(ROOT/'scripts/sikh318_native.py'),'--',str(job)],env=local_env,stdout=log,stderr=subprocess.STDOUT)
        receipt={'start':start,'end':end,'start_epoch':epoch,'end_epoch':time.time(),'seconds':time.monotonic()-tick,'code':r.returncode}
        (folder/'receipt.json').write_text(json.dumps(receipt,indent=2))
        if r.returncode:raise RuntimeError(folder/'worker.log')
        if op in ('look','movie','reopen'):
            from PIL import Image
            for f in range(start,end+1):
                p=out/'frames'/f'frame-{f:04d}.png'
                with Image.open(p) as image:
                    assert image.size==(720,1280);image.verify()
        return receipt
    # Measured worker RSS around1.5GB on this16GB host. Two isolated local
    # workers only; preserve six-frame lifetime and all render settings.
    with ThreadPoolExecutor(max_workers=2 if op=='movie' else 1) as pool:
        # Submit only a bounded pair, so failure never queues a whole render.
        size=2 if op=='movie' else 1
        for index in range(0,len(batches),size):
            futures=[pool.submit(batch,pair) for pair in batches[index:index+size]]
            for future in futures:
                receipts.append(future.result());(out/'processes.json').write_text(json.dumps(receipts,indent=2))
    assert all(pk.file_hash(ROOT/p)==h for p,h in task['inputs'].items())
    (dest/'receipt.json').write_text(json.dumps({'jobs':receipts,'packet_digest':packet['packet_digest'],'returncode':0},indent=2));print(out)
if __name__=='__main__':main()
