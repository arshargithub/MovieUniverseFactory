"""Fixed local319 supporting-cast workflow; structured jobs only."""
import json, os, sys, subprocess, time, shutil
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from movie_factory import production_knowledge as pk

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'.runtime/art-direction/series01-sikh319'
SOURCE=ROOT/'.runtime/art-direction/series01-sikh318/build-04/sequence.blend'
OPS=('inspect','donor','build','look','study','movie','reopen','check','verify','benchserial','benchpair')

def validate(j):
    if set(j)!={'operation','version','frames'} or j['operation'] not in OPS:
        raise ValueError('Invalid operation')
    if type(j['version']) is not int or not 1<=j['version']<=32:
        raise ValueError('Invalid version')
    if not isinstance(j['frames'],list) or not 1<=len(j['frames'])<=6:
        raise ValueError('Invalid batch')
    if any(type(f) is not int or not 1<=f<=696 for f in j['frames']):
        raise ValueError('Invalid frame')
    return j

def source_for(op,v):
    return SOURCE if op in ('inspect','donor','build') else BASE/f'build-{v:02d}/sequence.blend'

def main():
    op=sys.argv[1];v=int(sys.argv[2]);validate({'operation':op,'version':v,'frames':[1]})
    task=json.loads((ROOT/'results/sikh318/build-4/task.json').read_text())
    task.update(id=f'sikh319-{op}-{v}',intent='Supporting leader and crowd form material performance integration',
        execution_authority={'source':'results/sikh319/STRATEGY.md','scope':'Director319 supporting-cast pass; local existing resources only'})
    paths={ROOT/p for p in task['inputs'] if p.endswith('.py')}
    paths.update({source_for(op,v),ROOT/'scripts/sikh319.py',ROOT/'scripts/sikh319_native.py',
                  ROOT/'scripts/sikh319_cast.py',ROOT/'scripts/sikh319_finish.py',ROOT/'scripts/sikh319_verify.py',
                  ROOT/'.runtime/assets/series01-body-blender-studio/human-base-meshes-bundle-v1.4.1/human_base_meshes_bundle.blend',
                  ROOT/'results/sikh319/STRATEGY.md',ROOT/'results/sikh318/CARRY_FORWARD.md',
                  ROOT/'results/sikh318/SUPPORTING_CAST_REVIEW.md',
                  ROOT/'docs/knowledge/SIKH_FOUNDATION_REJECTION_271.md'})
    if op=='movie':
        paths.update({ROOT/f'results/sikh319/render-benchmark-{v}.json',ROOT/'scripts/benchmark319.py'})
    task['inputs']={str(p.relative_to(ROOT)):pk.file_hash(p) for p in paths}
    packet=pk.task_packet(ROOT,task);assert packet['dispatch_ready'],packet['blockers']
    record=ROOT/f'results/sikh319/{op}-{v}';record.mkdir(parents=True,exist_ok=True)
    for n,d in [('task',task),('packet',packet)]:(record/(n+'.json')).write_text(json.dumps(d,indent=2))
    (record/'packet.md').write_text(pk.packet_markdown(packet))
    if '--prepare' in sys.argv:print(record/'packet.md');return
    out=BASE/f'{op}-{v:02d}';out.mkdir(parents=True,exist_ok=False);(out/'frames').mkdir()
    for p in paths:
        if p.suffix in ('.py','.md'):
            dest=record/'source-snapshot'/p.relative_to(ROOT);dest.parent.mkdir(parents=True,exist_ok=True)
            shutil.copy2(p,dest)
    frames=[283,333,375,480] if op=='look' else [283,333] if op=='study' else [80,283,333,350,380,480] if op=='reopen' else list(range(1,697)) if op=='movie' else [283,294,306,315,324,333,342,350,375,420,450,480] if op.startswith('bench') else [1]
    receipts=[]
    def batch(fs):
        folder=out/'chunks'/str(fs[0]);folder.mkdir(parents=True)
        job=folder/'job.json';job.write_text(json.dumps(validate({'operation':op,'version':v,'frames':fs})))
        assert all(pk.file_hash(ROOT/p)==h for p,h in task['inputs'].items())
        env={k:os.environ[k] for k in ('PATH','HOME','TMPDIR','LANG','LC_ALL') if k in os.environ}
        for k,d in [('BLENDER_USER_CONFIG','config'),('BLENDER_USER_SCRIPTS','scripts'),('BLENDER_USER_DATAFILES','data')]:env[k]=str(folder/'sandbox'/d)
        tick=time.monotonic();epoch=time.time()
        with (folder/'worker.log').open('x') as log:
            r=subprocess.run(['/usr/bin/time','-l','/Applications/Blender.app/Contents/MacOS/Blender','-b','--factory-startup','--disable-autoexec','--offline-mode','--python-exit-code','7','--python',str(ROOT/'scripts/sikh319_native.py'),'--',str(job)],env=env,stdout=log,stderr=subprocess.STDOUT)
        receipt={'frames':fs,'seconds':time.monotonic()-tick,'start_epoch':epoch,'end_epoch':time.time(),'code':r.returncode}
        (folder/'receipt.json').write_text(json.dumps(receipt,indent=2))
        if r.returncode:raise RuntimeError(folder/'worker.log')
        if op in ('look','study','movie','reopen','benchserial','benchpair'):
            from PIL import Image
            for f in fs:
                with Image.open(out/'frames'/f'frame-{f:04d}.png') as im:
                    assert im.size==(720,1280);im.verify()
        return receipt
    workers=2 if op=='benchpair' else 1
    if op=='movie':
        decision=json.loads((ROOT/f'results/sikh319/render-benchmark-{v}.json').read_text())
        assert decision['native_sha256']==pk.file_hash(source_for(op,v))
        assert decision['status']=='PASS' and decision['workers'] in (1,2)
        workers=decision['workers']
    batches=[frames[ix:ix+6] for ix in range(0,len(frames),6)]
    with ThreadPoolExecutor(max_workers=workers) as pool:
        for i in range(0,len(batches),workers):
            futures=[pool.submit(batch,fs) for fs in batches[i:i+workers]]
            for future in futures:
                receipts.append(future.result())
                (out/'processes.json').write_text(json.dumps(receipts,indent=2))
    assert all(pk.file_hash(ROOT/p)==h for p,h in task['inputs'].items())
    (record/'receipt.json').write_text(json.dumps({'jobs':receipts,'packet_digest':packet['packet_digest']},indent=2))
    print(out)
if __name__=='__main__':main()
