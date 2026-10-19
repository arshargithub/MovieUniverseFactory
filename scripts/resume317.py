"""Resume frozen317 movie with short processes; preserve every completed frame."""
import json,os,subprocess,time,shutil
from pathlib import Path
from PIL import Image
from movie_factory.production_knowledge import file_hash
from render317 import ROOT,BASE,validate

def batches(existing):
    result=[]
    for a,b in ((275,430),(1,48),(49,274),(431,696)):
        missing=[f for f in range(a,b+1) if f not in existing]
        i=0
        while i<len(missing):
            chunk=[missing[i]];i+=1
            while i<len(missing) and len(chunk)<6 and missing[i]==chunk[-1]+1:
                chunk.append(missing[i]);i+=1
            result.append((chunk[0],chunk[-1]))
    return result

def main():
    out=BASE/'movie-05';bindings=json.loads((out/'bindings.json').read_text())
    def check():
        changed=[p for p,h in bindings.items() if file_hash(ROOT/p)!=h]
        if changed:raise ValueError('Changed original inputs: '+str(changed))
    check();preserved={}
    for p in sorted((out/'frames').glob('frame-*.png')):
        with Image.open(p) as im:
            im.load();assert im.size==(720,1280)
        preserved[p.name]=file_hash(p)
    recovery=out/'recovery-short';recovery.mkdir(exist_ok=False)
    shutil.copy2(__file__,recovery/'resume317.py')
    (recovery/'start.json').write_text(json.dumps({'reason':'Increasing frame times inside24-frame worker; preserve partial interrupted chunk and use six-frame fresh processes. No setting or native change.',
        'preserved_frames':preserved,'bindings':bindings,'recovery_handler_sha':file_hash(Path(__file__))},indent=2))
    env={k:os.environ[k] for k in ('PATH','HOME','TMPDIR','LANG','LC_ALL') if k in os.environ}
    for k,d in (('BLENDER_USER_CONFIG','config'),('BLENDER_USER_SCRIPTS','scripts'),('BLENDER_USER_DATAFILES','data')):env[k]=str(out/'sandbox'/d)
    receipts=[];tick=time.monotonic()
    for a,b in batches({int(p[6:10]) for p in preserved}):
        check();folder=out/'chunks'/str(a);folder.mkdir(exist_ok=False)
        job=folder/'job.json';job.write_text(json.dumps(validate({'operation':'movie','version':5,'start':a,'end':b})))
        started=time.monotonic()
        with (folder/'worker.log').open('x') as log:
            r=subprocess.run(['/Applications/Blender.app/Contents/MacOS/Blender','-b','--factory-startup','--disable-autoexec','--offline-mode','--python-exit-code','7','--python',str(ROOT/'scripts/render317_native.py'),'--',str(job)],env=env,stdout=log,stderr=subprocess.STDOUT)
        receipts.append({'start':a,'end':b,'seconds':time.monotonic()-started,'returncode':r.returncode})
        (recovery/'processes.json').write_text(json.dumps(receipts,indent=2));print(json.dumps(receipts[-1]),flush=True)
        if r.returncode:raise RuntimeError(folder/'worker.log')
    check()
    assert all(file_hash(out/'frames'/p)==h for p,h in preserved.items())
    assert len(list((out/'frames').glob('frame-*.png')))==696
    receipt={'returncode':0,'recovery_seconds':time.monotonic()-tick,'recovery':str(recovery.relative_to(ROOT)),
        'frames':696,'original_interrupted':True,'preserved_frames_unchanged':True,'batch_limit':6}
    with (ROOT/'results/sikh317/movie-5/receipt.json').open('x') as f:json.dump(receipt,f,indent=2)
if __name__=='__main__':main()
