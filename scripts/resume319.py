"""Resume only missing frames of a frozen319 movie; never overwrite output."""
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from PIL import Image
from movie_factory.production_knowledge import file_hash
from sikh319 import ROOT,BASE,validate

def batches(existing):
    missing=[f for f in range(1,697) if f not in existing]
    return [missing[i:i+6] for i in range(0,len(missing),6)]

def main():
    v=int(sys.argv[1]);assert 1<=v<=32
    out=BASE/f'movie-{v:02d}'
    task=json.loads((ROOT/f'results/sikh319/movie-{v}/task.json').read_text())
    def check():
        assert all(file_hash(ROOT/p)==h for p,h in task['inputs'].items()),'Frozen input changed'
    check();preserved={}
    for p in sorted((out/'frames').glob('frame-*.png')):
        with Image.open(p) as im:im.load();assert im.size==(720,1280)
        preserved[p.name]=file_hash(p)
    recovery=out/'recovery-01';recovery.mkdir(exist_ok=False)
    (recovery/'start.json').write_text(json.dumps({
        'preserved_frames':preserved,'bindings':task['inputs'],
        'handler_sha256':file_hash(Path(__file__))},indent=2))
    receipts=[]
    for number,frames in enumerate(batches({int(n[6:10]) for n in preserved})):
        check();folder=recovery/f'chunk-{number:03d}';folder.mkdir()
        job=folder/'job.json'
        job.write_text(json.dumps(validate({'operation':'movie','version':v,'frames':frames})))
        env={k:os.environ[k] for k in ('PATH','HOME','TMPDIR','LANG','LC_ALL') if k in os.environ}
        for k,d in [('BLENDER_USER_CONFIG','config'),('BLENDER_USER_SCRIPTS','scripts'),('BLENDER_USER_DATAFILES','data')]:
            env[k]=str(folder/d)
        tick=time.time()
        with (folder/'worker.log').open('x') as log:
            r=subprocess.run(['/usr/bin/time','-l','/Applications/Blender.app/Contents/MacOS/Blender',
                '-b','--factory-startup','--disable-autoexec','--offline-mode','--python-exit-code','7',
                '--python',str(ROOT/'scripts/sikh319_native.py'),'--',str(job)],
                env=env,stdout=log,stderr=subprocess.STDOUT)
        row={'frames':frames,'start_epoch':tick,'end_epoch':time.time(),'code':r.returncode}
        receipts.append(row);(recovery/'processes.json').write_text(json.dumps(receipts,indent=2))
        if r.returncode:raise RuntimeError(folder/'worker.log')
        for f in frames:
            with Image.open(out/'frames'/f'frame-{f:04d}.png') as im:im.load();assert im.size==(720,1280)
        print(json.dumps(row),flush=True)
    check()
    assert all(file_hash(out/'frames'/p)==h for p,h in preserved.items())
    assert {p.name for p in (out/'frames').glob('frame-*.png')}=={f'frame-{f:04d}.png' for f in range(1,697)}
    (recovery/'complete.json').write_text(json.dumps({
        'frames':696,'preserved_frames_unchanged':True,'original_failure_preserved':True},indent=2))
if __name__=='__main__':main()
