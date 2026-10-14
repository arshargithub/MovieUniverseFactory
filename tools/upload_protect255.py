"""Approved private snapshot transfer; immutable frozen inputs only, no deletion."""
from __future__ import annotations
import hashlib
import json
import os
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from verify_active_backup import aws_json, bucket_controls
from freeze_protect255 import ROOT, OUT, STAGE

BUCKET='movie-factory-archive'
PREFIX='movie-factory/backup/objects/sha256'
PROFILE='adi-sso'
REGION='ca-central-1'
AWS='/usr/local/bin/aws'

def object_key(digest):
    if not re.fullmatch('[0-9a-f]{64}',digest):
        raise ValueError('Invalid content digest')
    return f'{PREFIX}/{digest[:2]}/{digest}'

def main():
    manifest_path=OUT/'frozen-manifest.json'
    manifest=json.loads(manifest_path.read_text())
    if manifest['snapshot_id']!='protect255-20261013' or manifest['credential_like_paths']:
        raise ValueError('Unapproved or unscreened snapshot')
    identity=aws_json(PROFILE,REGION,'sts','get-caller-identity')
    if identity['Account']!='281482331395':raise ValueError('Wrong AWS account')
    controls=bucket_controls(PROFILE,REGION,BUCKET)
    listing=aws_json(PROFILE,REGION,'s3api','list-objects-v2','--bucket',BUCKET,'--prefix',PREFIX+'/')
    remote={x['Key']:x['Size'] for x in listing.get('Contents',[])}
    missing=[]
    for item in manifest['objects']:
        key=object_key(item['sha256'])
        if key in remote and remote[key]!=item['bytes']:raise ValueError('Immutable remote size collision: '+key)
        if key not in remote:missing.append(item)
    # A new upload-only directory cannot include old partial or quarantined files.
    stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    upload=STAGE/('upload-'+stamp)
    upload.mkdir(exist_ok=False)
    for n,item in enumerate(missing,1):
        digest=item['sha256'];source=STAGE/'objects'/digest[:2]/digest
        if source.is_symlink() or source.stat().st_size!=item['bytes']:raise ValueError('Frozen input changed')
        with source.open('rb') as f: actual=hashlib.file_digest(f,'sha256').hexdigest()
        if actual!=digest:raise ValueError('Frozen input hash mismatch')
        target=upload/digest[:2]/digest;target.parent.mkdir(exist_ok=True)
        # Hardlink only the independent frozen object, never the live worktree.
        os.link(source,target)
        if n%2000==0:print(json.dumps({'staged':n,'total':len(missing)}),flush=True)
    receipt={'snapshot_id':manifest['snapshot_id'],'started_at':stamp,'bucket':BUCKET,
        'controls':controls,'missing_objects':len(missing),'missing_bytes':sum(x['bytes'] for x in missing),
        'source_manifest_sha256':hashlib.sha256(manifest_path.read_bytes()).hexdigest(),
        'upload_root':str(upload),'remote_verified':False}
    receipt_path=OUT/('transfer-'+stamp+'.json')
    receipt_path.write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt),flush=True)
    if missing:
        subprocess.run([AWS,'s3','cp',str(upload),f's3://{BUCKET}/{PREFIX}/','--recursive',
            '--no-follow-symlinks','--checksum-algorithm','SHA256','--only-show-errors',
            '--profile',PROFILE,'--region',REGION],check=True)
    key=f'movie-factory/backup/active/movie-universe-factory/snapshots/{manifest["snapshot_id"]}/manifest.json'
    subprocess.run([AWS,'s3','cp',str(manifest_path),f's3://{BUCKET}/{key}',
        '--checksum-algorithm','SHA256','--only-show-errors','--profile',PROFILE,'--region',REGION],check=True)
    receipt['upload_completed_at']=datetime.now(timezone.utc).isoformat()
    receipt_path.write_text(json.dumps(receipt,indent=2)+'\n')
    subprocess.run([str(ROOT/'.venv/bin/python'),str(ROOT/'tools/verify_active_backup.py'),
        '--manifest',str(manifest_path),'--receipt',str(OUT/'remote-verification.json'),
        '--bucket',BUCKET,'--object-prefix',PREFIX,'--manifest-key',key,'--profile',PROFILE,'--region',REGION],check=True)
    receipt['remote_verified']=True
    receipt['verification_receipt']='results/backup/protect255/remote-verification.json'
    receipt_path.write_text(json.dumps(receipt,indent=2)+'\n')
    print('Remote inventory and representative stream verified; native capsule restore is separate.',flush=True)

if __name__=='__main__':main()
