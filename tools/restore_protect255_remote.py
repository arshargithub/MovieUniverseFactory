"""Restore representative final dependencies from S3, never from local originals."""
import concurrent.futures
import hashlib
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from upload_protect255 import ROOT,OUT,BUCKET,PREFIX,PROFILE,REGION,AWS,object_key

DEST=ROOT/'.runtime/protection255-restore/remote-source'

def digest(path):
    with path.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def safe_destination(relative):
    p=Path(relative)
    if p.is_absolute() or '..' in p.parts or not p.parts:raise ValueError('Unsafe restore path')
    result=DEST/p
    if not result.resolve().is_relative_to(DEST.resolve()):raise ValueError('Restore escape')
    return result

def download(key,path):
    path.parent.mkdir(parents=True,exist_ok=True)
    subprocess.run([AWS,'s3','cp',f's3://{BUCKET}/{key}',str(path),'--only-show-errors',
        '--profile',PROFILE,'--region',REGION],check=True)

def main():
    proof=json.loads((OUT/'remote-verification.json').read_text())
    if not proof['recovery_copy_verified']:raise ValueError('Remote snapshot verification prerequisite')
    if DEST.exists():raise ValueError('Refuse overwrite of prior remote restore')
    manifest_copy=OUT/'remote-restored-manifest.json'
    download(proof['manifest']['remote_key'],manifest_copy)
    if digest(manifest_copy)!=proof['manifest']['sha256']:raise ValueError('Remote manifest mismatch')
    manifest=json.loads(manifest_copy.read_text());rows={x['path']:x for x in manifest['paths']}
    capsule=json.loads((OUT/'accepted-capsule.json').read_text())
    for row in capsule['files']:
        frozen=rows.get(row['path'],{})
        if any(frozen.get(k)!=row[k] for k in ('sha256','bytes')):raise ValueError('Capsule not bound to remote manifest')
        safe_destination(row['path'])
    DEST.mkdir(parents=True,exist_ok=False)
    def restore(row):
        target=safe_destination(row['path'])
        download(object_key(row['sha256']),target)
        if target.stat().st_size!=row['bytes'] or digest(target)!=row['sha256']:raise ValueError('Remote restore mismatch')
        return row
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        checked=list(pool.map(restore,capsule['files']))
    env={k:os.environ[k] for k in ('PATH','HOME','TMPDIR','LANG','LC_ALL') if k in os.environ}
    for op in ('inspect-remote-opening','inspect-remote-route'):
        job=OUT/(op+'.json');job.write_text(json.dumps({'operation':op})+'\n')
        with (OUT/(op+'.log')).open('w') as log:
            subprocess.run(['/Applications/Blender.app/Contents/MacOS/Blender','--background','--factory-startup',
                '--disable-autoexec','--python-exit-code','7','--python',str(ROOT/'scripts/protection255_native_check.py'),
                '--',str(job)],env=env,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
        evidence=json.loads((OUT/('native-'+op+'.json')).read_text())
        if not evidence['passed']:raise ValueError('Native dependency check failed')
    result={'kind':'remote-accepted-unit-restore','verified_at':datetime.now(timezone.utc).isoformat(),
        'snapshot_id':manifest['snapshot_id'],'manifest_sha256':digest(manifest_copy),'files':len(checked),
        'bytes':sum(x['bytes'] for x in checked),'all_hashes_match':True,'source':'S3 only; no local asset fallback',
        'restore_root':str(DEST),'native_reopens':2,'native_dependency_checks_pass':True,
        'rendered':False,'scope':'Representative accepted unit, not every historical experiment or all possible add-on dependencies',
        'clean_sha256':capsule['clean_sha256']}
    (OUT/'remote-capsule-restore.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result),flush=True)

if __name__=='__main__':main()
