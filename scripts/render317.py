"""Bounded, immutable local render batches for the fixed317 native derivative."""
import sys,json,os,time,subprocess,shutil
from pathlib import Path
from movie_factory import production_knowledge as pk
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'.runtime/art-direction/series01-sikh317'
def validate(j):
    if set(j)!={'operation','version','start','end'}:raise ValueError('Unexpected job fields')
    if j['operation'] not in ('proof','movie','reopen') or type(j['version']) is not int or not 1<=j['version']<=9:raise ValueError('Invalid operation')
    if any(type(j[k]) is not int for k in ('start','end')) or not 1<=j['start']<=j['end']<=696 or j['end']-j['start']>=24:raise ValueError('Invalid frame batch')
    return j
def main():
    op=sys.argv[1];v=int(sys.argv[2]);validate({'operation':op,'version':v,'start':1,'end':1})
    out=BASE/f'{op}-{v:02d}';source=BASE/f'build-{v:02d}/sequence.blend'
    task=json.loads((ROOT/f'results/sikh317/build-{v}/task.json').read_text())
    task.update(id=f'sikh317-{op}-{v}',operation='render',query='Actual frame motion support coat and crowd review')
    paths=[source,ROOT/'scripts/render317.py',ROOT/'scripts/render317_native.py',ROOT/'src/movie_factory/production_knowledge.py',ROOT/pk.CATALOG,ROOT/pk.PINS,ROOT/'results/sikh317/STRATEGY.md']
    task['inputs']={str(p.relative_to(ROOT)):pk.file_hash(p) for p in paths}
    packet=pk.task_packet(ROOT,task)
    if not packet['dispatch_ready']:raise ValueError(packet['blockers'])
    dest=ROOT/f'results/sikh317/{op}-{v}';dest.mkdir(parents=True,exist_ok=True)
    for name,data in (('task',task),('packet',packet)):(dest/(name+'.json')).write_text(json.dumps(data,indent=2))
    (dest/'packet.md').write_text(pk.packet_markdown(packet))
    if '--prepare' in sys.argv:print(dest/'packet.md');return
    out.mkdir(exist_ok=False);(out/'frames').mkdir();(out/'bindings.json').write_text(json.dumps(task['inputs'],indent=2))
    for p in paths:
        if p.suffix in ('.py','.json','.md'):
            d=out/'source-snapshot'/p.relative_to(ROOT);d.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,d)
    env={k:os.environ[k] for k in ('PATH','HOME','TMPDIR','LANG','LC_ALL') if k in os.environ}
    for k,d in (('BLENDER_USER_CONFIG','config'),('BLENDER_USER_SCRIPTS','scripts'),('BLENDER_USER_DATAFILES','data')):env[k]=str(out/'sandbox'/d)
    # Difficult windows first: permit failure-seeking frame review before
    # spending on the rest of the exact same frozen full-resolution native.
    windows=[(1,48),(275,365),(365,430)] if op=='proof' else [(359,430),(275,358),(1,274),(431,696)]
    if op=='reopen':windows=[(f,f) for f in (41,80,126,294,306,315,324,333,342,350,375,380,402,430,480,600)]
    jobs=[]
    for a,b in windows:
        for start in range(a,b+1,6):jobs.append((start,min(b,start+5)))
    # Remove duplicate seam frames in proof windows without overwriting evidence.
    if op=='proof':jobs=[(366 if a==365 else a,b) for a,b in jobs]
    receipts=[]
    for a,b in jobs:
        if any(pk.file_hash(ROOT/p)!=h for p,h in task['inputs'].items()):raise ValueError('Changed bound render source')
        folder=out/'chunks'/str(a);folder.mkdir(parents=True);job=folder/'job.json';job.write_text(json.dumps({'operation':op,'version':v,'start':a,'end':b}))
        start=time.monotonic()
        with (folder/'worker.log').open('w') as log:
            r=subprocess.run(['/Applications/Blender.app/Contents/MacOS/Blender','-b','--factory-startup','--disable-autoexec','--offline-mode','--python-exit-code','7','--python',str(ROOT/'scripts/render317_native.py'),'--',str(job)],env=env,stdout=log,stderr=subprocess.STDOUT)
        receipts.append({'start':a,'end':b,'seconds':time.monotonic()-start,'code':r.returncode});(out/'processes.json').write_text(json.dumps(receipts,indent=2))
        if r.returncode:raise RuntimeError(folder/'worker.log')
    (dest/'receipt.json').write_text(json.dumps({'jobs':receipts,'packet_digest':packet['packet_digest'],'returncode':0},indent=2));print(out)
if __name__=='__main__':main()
