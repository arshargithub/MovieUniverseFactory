"""Local recovery rehearsal of exact accepted files; not an off-device restore claim."""
import json
import os
import subprocess
from pathlib import Path
from freeze_protect255 import ROOT,OUT,STAGE,copy_independent,scanned

def main():
    dest=ROOT/'.runtime/protection255-restore'
    capsule=json.loads((OUT/'accepted-capsule.json').read_text())
    for row in capsule['files']:
        p=dest/row['path']
        if p.exists():
            if scanned(p)[0]!=row['sha256']:raise RuntimeError('Restoration collision')
            continue
        frozen=STAGE/'objects'/row['sha256'][:2]/row['sha256']
        # Freeze may still be running. Copy live only as an explicitly local rehearsal.
        source=frozen if frozen.exists() and frozen.stat().st_size==row['bytes'] else ROOT/row['path']
        copy_independent(source,p)
        if scanned(p)[0]!=row['sha256']:raise RuntimeError('Rehearsal hash mismatch')
    env={k:os.environ[k] for k in ('PATH','HOME','TMPDIR','LANG','LC_ALL') if k in os.environ}
    for op in ('inspect-restored-opening','inspect-restored-route'):
        job=OUT/(op+'.json');job.write_text(json.dumps({'operation':op})+'\n')
        attempt=1
        while (OUT/f'{op}-{attempt:02d}.log').exists():attempt+=1
        with (OUT/f'{op}-{attempt:02d}.log').open('w') as log:
            subprocess.run(['/Applications/Blender.app/Contents/MacOS/Blender','--background','--factory-startup','--disable-autoexec','--python-exit-code','7','--python',str(ROOT/'scripts/protection255_native_check.py'),'--',str(job)],env=env,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
    (OUT/'local-rehearsal.json').write_text(json.dumps({'local_only':True,'files':len(capsule['files']),'bytes':capsule['bytes'],'hashes_match':True,'native_dependency_checks_pass':True,'remote_restore':'NOT_RUN'},indent=2)+'\n')
    print('Local rehearsal complete; no remote recovery claim')

if __name__=='__main__':main()
