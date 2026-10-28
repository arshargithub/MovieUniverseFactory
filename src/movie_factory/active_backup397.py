"""Private verified recovery and keep-one retention. AWS CLI, no new SDK.

Never sync-delete, never delete before a replacement restore receipt. Exact
scoped plans/versions are retained locally. Caller must have Director authority.
"""
import argparse
import base64
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import sqlite3
import subprocess
import shutil

BUCKET='movie-factory-archive'
OWNER='281482331395'
BASE='movie-factory/backup/'
OBJECTS=BASE+'objects/sha256/'
SNAPSHOTS=BASE+'active/movie-universe-factory/snapshots/'
SKIP_DIRS={'.git','.venv','node_modules','__pycache__','.pytest_cache','.mypy_cache','.ruff_cache',
           '.aws','.Trash','.Spotlight-V100','.fseventsd'}
SKIP_PREFIXES=('.runtime/workflow397/', '.runtime/backup/', '.runtime/backup397/',
               '.runtime/python/', '.runtime/protection255-frozen/', '.runtime/protection255-restore/',
               '.runtime/knowledge-pilot213/backup-', 'results/backup/protect255/restored',
               'results/backup/protect255/staging', 'results/backup/protect255/snapshot')
SECRET=re.compile(rb'(?:AKIA|ASIA)[0-9A-Z]{16}|AIza[0-9A-Za-z_-]{30,}|hf_[0-9A-Za-z]{25,}|sk-[0-9A-Za-z_-]{28,}')
TEXT={'.py','.json','.jsonl','.md','.txt','.yaml','.yml','.toml','.ini','.cfg','.xml','.svg','.html','.js','.cjs','.sh','.log'}


def require(ok,message):
    if not ok:raise ValueError(message)


def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda:f.read(4*1024*1024),b''):h.update(chunk)
    return h.hexdigest()


def save(path,data):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    temp=path.with_suffix(path.suffix+'.tmp');temp.write_text(json.dumps(data,indent=2)+'\n');temp.replace(path)


def key(digest):
    require(re.fullmatch('[0-9a-f]{64}',digest) is not None,'INVALID_DIGEST')
    return OBJECTS+digest[:2]+'/'+digest


def excluded(rel,is_dir=False):
    p=Path(rel)
    return (any(x in SKIP_DIRS for x in p.parts) or any(rel.startswith(x) for x in SKIP_PREFIXES)
            or p.name=='.DS_Store' or p.name.startswith('.env') and p.name!='.env.example'
            or p.suffix.lower() in {'.env','.pem','.key','.pyc'}
            or p.name in {'credentials','token','tokens','id_rsa','id_ed25519'}
            or p.name=='private-link.txt'
            or p.name.endswith(('-wal','-shm')))


class Client:
    def __init__(self,profile='hindsight-sso'):
        self.profile=profile

    def call(self,operation,**args):
        cmd=['aws','s3api',operation,'--profile',self.profile,'--bucket',BUCKET,
             '--expected-bucket-owner',OWNER,'--output','json','--cli-read-timeout','0']
        output_path=args.pop('_output_path',None)
        for k,v in args.items():
            cmd.extend(['--'+k.replace('_','-'),json.dumps(v) if isinstance(v,(dict,list)) else str(v)])
        if output_path is not None:cmd.append(str(output_path))
        r=subprocess.run(cmd,capture_output=True,text=True)
        require(r.returncode==0,'AWS_'+operation+': '+r.stderr[-1800:])
        return json.loads(r.stdout) if r.stdout.strip() else {}

    def inventory(self,prefix):
        return {o['Key']:o for o in self.call('list-objects-v2',prefix=prefix).get('Contents',[])}

    def put(self,path,remote_key,digest=None):
        digest=digest or sha(path)
        require(Path(path).stat().st_size<=5*1024**3,'MULTIPART_NOT_IMPLEMENTED_NO_SILENT_SCOPE_DROP')
        checksum=base64.b64encode(bytes.fromhex(digest)).decode()
        result=self.call('put-object',key=remote_key,body=str(path),checksum_algorithm='SHA256',
                         checksum_sha256=checksum,metadata={'sha256':digest})
        require(result.get('ChecksumSHA256')==checksum,'PUT_CHECKSUM_NOT_CONFIRMED')
        return result

    def get(self,remote_key,path):
        return self.call('get-object',key=remote_key,checksum_mode='ENABLED',_output_path=path)


def manifest_references(manifest):
    """Closed support for historical255 and397 manifest schemas."""
    if manifest.get('schema_version') in {1,2,'1.0'} and isinstance(manifest.get('objects'),list):
        return {o.get('key') or key(o['sha256']) for o in manifest['objects']}
    raise ValueError('UNKNOWN_RETAINED_MANIFEST_SCHEMA_NO_GC')


def inspect_controls(client):
    version=client.call('get-bucket-versioning')
    public=client.call('get-public-access-block')['PublicAccessBlockConfiguration']
    enc=client.call('get-bucket-encryption')['ServerSideEncryptionConfiguration']['Rules']
    ownership=client.call('get-bucket-ownership-controls')['OwnershipControls']['Rules']
    require(version.get('Status')=='Enabled','VERSIONING_REQUIRED')
    require(all(public.get(x) is True for x in ['BlockPublicAcls','IgnorePublicAcls','BlockPublicPolicy','RestrictPublicBuckets']), 'PRIVATE_BUCKET_REQUIRED')
    require(any(r['ApplyServerSideEncryptionByDefault']['SSEAlgorithm'] in {'AES256','aws:kms'} for r in enc),'ENCRYPTION_REQUIRED')
    require(any(r.get('ObjectOwnership')=='BucketOwnerEnforced' for r in ownership),'OWNERSHIP_REQUIRED')
    return dict(versioning=version,public=public,encryption=enc,ownership=ownership)


def prepare(root,work,*,snapshot_id,prior=None):
    root=Path(root).resolve();work=Path(work).resolve();work.mkdir(parents=True,exist_ok=True)
    cache_path=work/'hash-cache.json'
    cache=json.loads(cache_path.read_text()) if cache_path.exists() else {}
    allow={x['sha256'] for x in (prior or {}).get('reviewed_scanner_findings',[])}
    files=[];objects={};flags=[];symlinks=[];scanned=0
    for folder,dirs,names in os.walk(root,followlinks=False):
        rel_folder=Path(folder).relative_to(root)
        dirs[:]=[n for n in dirs if not excluded(str(rel_folder/n)+'/',True) and not (Path(folder)/n).is_symlink()]
        for name in names:
            source=Path(folder)/name;rel=str(source.relative_to(root))
            if excluded(rel):continue
            if source.is_symlink():
                # No external files/credentials by following a link.
                target=source.resolve()
                legacy=Path('/Users/adisharma/projects/MovieUniverseFactory')
                if target.is_relative_to(legacy):
                    relocated=root/target.relative_to(legacy)
                    require(relocated.exists() and relocated.resolve().is_relative_to(root), 'UNRESOLVED_MIGRATED_SYMLINK:'+rel)
                    target=relocated.resolve()
                require(target.is_relative_to(root),'EXTERNAL_SYMLINK_NOT_BACKED_UP:'+rel)
                symlinks.append(dict(path=rel,target=os.path.relpath(target,source.parent)));continue
            if not source.is_file():continue
            st=source.stat();read_path=source
            with source.open('rb') as f: header=f.read(16)
            if header==b'SQLite format 3\x00':
                snap=work/'databases'/rel;snap.parent.mkdir(parents=True,exist_ok=True)
                with sqlite3.connect('file:'+str(source)+'?mode=ro',uri=True) as src,sqlite3.connect(snap) as dst:
                    src.backup(dst,pages=4096)
                read_path=snap;st=read_path.stat()
            identity=[st.st_size,st.st_mtime_ns,st.st_ctime_ns]
            old=cache.get(rel)
            digest=old['sha256'] if old and old['stat']==identity else sha(read_path)
            if source.suffix.lower() in TEXT and digest not in allow:
                found=False;tail=b''
                with read_path.open('rb') as f:
                    for chunk in iter(lambda:f.read(1024*1024),b''):
                        if SECRET.search(tail+chunk):found=True;break
                        tail=chunk[-100:]
                if found:flags.append(dict(path=rel,sha256=digest))
            now=read_path.stat();require(identity==[now.st_size,now.st_mtime_ns,now.st_ctime_ns],'SOURCE_CHANGED_DURING_FREEZE:'+rel)
            cache[rel]=dict(stat=identity,sha256=digest)
            object_identity=identity
            # Capture mutable code/records at manifest time. Parallel research
            # may append a usage log before transfer starts; retaining only its
            # old live path is not a frozen snapshot. Never omit those records.
            if source.suffix.lower() in TEXT and st.st_size<=16*1024**2:
                frozen=work/'frozen-text'/digest[:2]/digest;frozen.parent.mkdir(parents=True,exist_ok=True)
                if not frozen.exists():shutil.copyfile(read_path,frozen)
                require(sha(frozen)==digest,'TEXT_CHANGED_DURING_FREEZE:'+rel)
                read_path=frozen;fs=frozen.stat();object_identity=[fs.st_size,fs.st_mtime_ns,fs.st_ctime_ns]
            files.append(dict(path=rel,bytes=st.st_size,sha256=digest,mode=st.st_mode & 0o777))
            objects.setdefault(digest,dict(sha256=digest,bytes=st.st_size,key=key(digest),
                                          source=str(read_path),stat=object_identity,paths=[]))['paths'].append(rel)
            scanned+=1
            if scanned%2000==0:
                save(cache_path,cache);print(json.dumps({'scanned':scanned,'unique':len(objects)}),flush=True)
    save(cache_path,cache)
    save(work/'scanner-findings.json',flags)
    require(not flags,'CREDENTIAL_LIKE_CONTENT_REQUIRES_LOCAL_REVIEW_NO_UPLOAD')
    git=subprocess.run(['git','rev-parse','HEAD'],cwd=root,capture_output=True,text=True,check=True).stdout.strip()
    result=dict(schema_version=2,kind='active_verified_recovery',snapshot_id=snapshot_id,
        created_at=datetime.now(timezone.utc).isoformat(),source_root=str(root),git_head=git,
        paths=files,objects=list(objects.values()),symlinks=symlinks,path_count=len(files),
        unique_object_count=len(objects),unique_bytes=sum(o['bytes'] for o in objects.values()),
        database_method='SQLite online backup; original target paths retained',
        credential_like_paths=[],reviewed_scanner_findings=(prior or {}).get('reviewed_scanner_findings',[]),
        exclusions='Exact active_backup397.excluded policy; all native masters/evidence included')
    save(work/'manifest-local.json',result)
    remote=dict(result,objects=[{k:v for k,v in o.items() if k not in {'source','stat'}} for o in result['objects']])
    save(work/'manifest.json',remote)
    return result


def upload(client,work):
    work=Path(work);m=json.loads((work/'manifest-local.json').read_text())
    controls=inspect_controls(client);inventory=client.inventory(OBJECTS)
    save(work/'controls.json',controls)
    uploaded=[];reused=[]
    def one(o):
        path=Path(o['source']);s=path.stat()
        require([s.st_size,s.st_mtime_ns,s.st_ctime_ns]==o['stat'],'FROZEN_SOURCE_CHANGED:'+o['paths'][0])
        if o['key'] in inventory:
            require(inventory[o['key']]['Size']==o['bytes'],'REMOTE_SIZE_COLLISION')
            return dict(key=o['key'],kind='reused')
        require(sha(path)==o['sha256'],'FROZEN_DIGEST_CHANGED')
        result=client.put(path,o['key'],o['sha256'])
        return dict(key=o['key'],kind='uploaded',version=result.get('VersionId'),checksum=result['ChecksumSHA256'])
    with ThreadPoolExecutor(max_workers=2) as pool:
        for index,r in enumerate(pool.map(one,m['objects'])):
            (uploaded if r['kind']=='uploaded' else reused).append(r)
            if index%100==0:
                save(work/'transfer.json',dict(uploaded=uploaded,reused=reused))
                print(json.dumps({'processed':index+1,'uploaded':len(uploaded),'reused':len(reused)}),flush=True)
    save(work/'transfer.json',dict(uploaded=uploaded,reused=reused))
    manifest_key=SNAPSHOTS+m['snapshot_id']+'/manifest.json'
    client.put(work/'manifest.json',manifest_key)
    save(work/'uploaded.json',dict(manifest_key=manifest_key,manifest_sha256=sha(work/'manifest.json')))
    receipt=verify(client,work)
    client.put(work/'verification.json',SNAPSHOTS+m['snapshot_id']+'/verification.json')
    return receipt


def upload_bulk(client,work):
    """Installed CLI transfer manager supplies multipart, checksums and concurrency.

    Staging is a separate frozen payload namespace, never a sync-delete source.
    New byte streams use S3 SHA256 validation, including composite checksums for
    multipart objects; a composite checksum is not misreported as whole-file SHA.
    """
    work=Path(work);m=json.loads((work/'manifest-local.json').read_text())
    save(work/'controls.json',inspect_controls(client));inventory=client.inventory(OBJECTS)
    stage=work/'transfer-payload';stage.mkdir(exist_ok=True)
    pending=[];reused=[]
    for o in m['objects']:
        if o['key'] in inventory:
            require(inventory[o['key']]['Size']==o['bytes'],'REMOTE_SIZE_COLLISION');reused.append(o['key']);continue
        source=Path(o['source']);s=source.stat()
        require([s.st_size,s.st_mtime_ns,s.st_ctime_ns]==o['stat'],'FROZEN_SOURCE_CHANGED:'+o['paths'][0])
        require(sha(source)==o['sha256'],'FROZEN_DIGEST_CHANGED')
        dest=stage/o['sha256'][:2]/o['sha256'];dest.parent.mkdir(exist_ok=True)
        if not dest.exists():
            # Small implementation/receipt files are copied; large static assets
            # use a hardlink and a post-transfer stat guard, avoiding100GB copies.
            if o['bytes']<16*1024**2:shutil.copyfile(source,dest)
            else:os.link(source,dest)
        require(sha(dest)==o['sha256'],'STAGING_DIGEST_CHANGED')
        pending.append(o)
    expected={o['sha256'] for o in pending}
    for p in stage.glob('*/*'):
        require(p.name in expected,'STALE_TRANSFER_STAGE_REPREPARE_REQUIRED')
    log=work/'bulk-transfer.log'
    cmd=['aws','s3','sync',str(stage),'s3://'+BUCKET+'/'+OBJECTS,
         '--profile',client.profile,'--no-progress','--no-follow-symlinks','--checksum-algorithm','SHA256']
    with log.open('w') as stream:
        result=subprocess.run(cmd,stdout=stream,stderr=subprocess.STDOUT)
    require(result.returncode==0,'BULK_TRANSFER_FAILED_RETAIN_OLD_BACKUP')
    after=client.inventory(OBJECTS)
    require(all(o['key'] in after and after[o['key']]['Size']==o['bytes'] and
                'SHA256' in after[o['key']].get('ChecksumAlgorithm',[]) for o in pending), 'BULK_CHECKSUM_INVENTORY_MISSING')
    for o in pending:
        # Creating our own hardlink changes the original inode's ctime. Copied
        # small files may also legitimately change after this checkpoint. The
        # actual uploaded, frozen payload is the contract, not live-path ctime.
        frozen=stage/o['sha256'][:2]/o['sha256']
        require(frozen.stat().st_size==o['bytes'] and sha(frozen)==o['sha256'],
                'FROZEN_PAYLOAD_CHANGED_DURING_TRANSFER')
    save(work/'transfer.json',dict(uploaded=[o['key'] for o in pending],reused=reused,
        checksum_scope='AWS CLI SHA256-validated uploads; multipart composite checksum; exact local manifest digests and representative whole-file restore.'))
    manifest_key=SNAPSHOTS+m['snapshot_id']+'/manifest.json';client.put(work/'manifest.json',manifest_key)
    save(work/'uploaded.json',dict(manifest_key=manifest_key,manifest_sha256=sha(work/'manifest.json')))
    receipt=verify(client,work)
    client.put(work/'verification.json',SNAPSHOTS+m['snapshot_id']+'/verification.json')
    return receipt


def verify(client,work):
    work=Path(work);m=json.loads((work/'manifest.json').read_text());u=json.loads((work/'uploaded.json').read_text())
    remote=client.inventory(OBJECTS)
    require(all(o['key'] in remote and remote[o['key']]['Size']==o['bytes'] for o in m['objects']), 'REMOTE_INVENTORY_INCOMPLETE')
    restored=work/'restored-manifest.json';client.get(u['manifest_key'],restored)
    require(sha(restored)==u['manifest_sha256'],'MANIFEST_RESTORE_MISMATCH')
    # A native file and a small operational object prove actual streamed recovery.
    native=next((o for o in m['objects'] if any(p.endswith('.blend') for p in o['paths']) and o['bytes']<256*1024**2),None)
    small=next((o for o in m['objects'] if any('production_governance.py' in p for p in o['paths'])),None)
    samples=[]
    for index,o in enumerate(x for x in [native,small] if x):
        dest=work/('restored-sample-'+str(index));head=client.get(o['key'],dest)
        actual=sha(dest);require(actual==o['sha256'],'OBJECT_RESTORE_MISMATCH')
        samples.append(dict(key=o['key'],bytes=o['bytes'],sha256=actual,stored_checksums={k:v for k,v in head.items() if k.startswith('Checksum')}))
    require(samples,'REPRESENTATIVE_RESTORE_REQUIRED')
    receipt=dict(snapshot_id=m['snapshot_id'],manifest_key=u['manifest_key'],manifest_sha256=u['manifest_sha256'],
        verified=True,restore_samples=samples,path_count=m['path_count'],unique_object_count=len(m['objects']),
        unique_bytes=m['unique_bytes'],inventory_missing=0,size_mismatches=0,git_head=m['git_head'],
        checksum_scope='SHA256-validated new uploads (multipart may use composite checksums); full size/key inventory; manifest and representative streamed whole-file SHA256 restores; no exhaustive full-data restore.')
    save(work/'verification.json',receipt)
    return receipt


def retention_plan(client,work):
    work=Path(work);receipt=json.loads((work/'verification.json').read_text())
    require(receipt.get('verified') is True,'NO_VERIFIED_REPLACEMENT_NO_DELETE')
    # Re-verify latest inventory and restore before any destructive plan.
    verify(client,work)
    m=json.loads((work/'manifest.json').read_text());latest=SNAPSHOTS+m['snapshot_id']+'/'
    all_keys=client.inventory('movie-factory/')
    refs=manifest_references(m)
    protected_manifests=[]
    for k in all_keys:
        if k.endswith('.json') and 'manifest' in Path(k).name.lower() and not k.startswith(SNAPSHOTS):
            dest=work/('retained-'+hashlib.sha256(k.encode()).hexdigest()+'.json');client.get(k,dest)
            retained=json.loads(dest.read_text())
            # Historical1.0 manifests are hash-only. Conservatively protect any
            # shared copy too, even where the archive has its own namespace.
            refs|=manifest_references(retained)
            protected_manifests.append(k)
    versions=client.call('list-object-versions',prefix=BASE)
    delete=[];protected=[]
    for obj in versions.get('Versions',[])+versions.get('DeleteMarkers',[]):
        k=obj['Key'];eligible=(k.startswith(SNAPSHOTS) and (not k.startswith(latest) or obj.get('IsLatest') is False)) or (
            k.startswith(OBJECTS) and (k not in refs or obj.get('IsLatest') is False))
        if eligible:delete.append(dict(Key=k,VersionId=obj['VersionId'],bytes=obj.get('Size',0)))
        else:protected.append(dict(Key=k,VersionId=obj['VersionId']))
    plan=dict(snapshot_id=m['snapshot_id'],latest_prefix=latest,latest_manifest_sha256=receipt['manifest_sha256'],
        delete=delete,protected=protected,protected_manifests=protected_manifests,
        total_delete_bytes=sum(x['bytes'] for x in delete),scope='Superseded active project backups and unreferenced content objects only')
    save(work/'retention-plan.json',plan);return plan


def cleanup(client,work):
    work=Path(work);p=json.loads((work/'retention-plan.json').read_text())
    receipt=json.loads((work/'verification.json').read_text())
    require(receipt.get('verified') and receipt['manifest_sha256']==p['latest_manifest_sha256'],'RETENTION_RECEIPT_MISMATCH')
    verify(client,work)
    require(all((x['Key'].startswith(SNAPSHOTS) and not x['Key'].startswith(p['latest_prefix'])) or
                x['Key'].startswith(OBJECTS) for x in p['delete']), 'OUT_OF_SCOPE_DELETION')
    original=work/'retention-plan-original.json'
    if original.exists():
        p=json.loads(original.read_text())
        require(p['latest_manifest_sha256']==receipt['manifest_sha256'],'ORIGINAL_RETENTION_SCOPE_CHANGED')
    else:save(original,p)
    fresh=retention_plan(client,work)
    allowed={(x['Key'],x['VersionId']) for x in fresh['delete']}
    versions=client.call('list-object-versions',prefix=BASE)
    present={(x['Key'],x['VersionId']) for x in versions.get('Versions',[])+versions.get('DeleteMarkers',[])}
    pending=[x for x in p['delete'] if (x['Key'],x['VersionId']) in present]
    require({(x['Key'],x['VersionId']) for x in pending} <= allowed,'RETENTION_PLAN_WOULD_DELETE_REFERENCED_COPY')
    # Exact version IDs: no broad lifecycle/sync-delete or delete-marker substitute.
    for start in range(0,len(pending),100):
        batch=[{k:x[k] for k in ['Key','VersionId']} for x in pending[start:start+100]]
        result=client.call('delete-objects',delete={'Objects':batch,'Quiet':True})
        require(not result.get('Errors'),'PARTIAL_DELETION_FAILURE')
        save(work/'retention-progress.json',dict(processed=start+len(batch),total=len(pending)))
    versions=client.call('list-object-versions',prefix=BASE)
    remain=versions.get('Versions',[])+versions.get('DeleteMarkers',[])
    forbidden={(x['Key'],x['VersionId']) for x in p['delete']}
    require(not forbidden.intersection((x['Key'],x['VersionId']) for x in remain),'SUPERSEDED_VERSIONS_REMAIN')
    generation={x['Key'][len(SNAPSHOTS):].split('/')[0] for x in remain if x['Key'].startswith(SNAPSHOTS)}
    require(generation=={p['snapshot_id']},'MORE_THAN_ONE_ACTIVE_GENERATION')
    verify(client,work)
    result=dict(snapshot_id=p['snapshot_id'],one_active_generation=True,deleted_versions=len(p['delete']),
        deleted_bytes=p['total_delete_bytes'],remaining_backup_version_bytes=sum(x.get('Size',0) for x in remain),
        newest_restore_verified_after_cleanup=True)
    save(work/'retention-verification.json',result)
    client.put(work/'retention-verification.json',p['latest_prefix']+'retention-verification.json')
    return result


def main():
    p=argparse.ArgumentParser();p.add_argument('action',choices=['prepare','upload','upload-bulk','verify','plan-retention','cleanup'])
    p.add_argument('--work',required=True);p.add_argument('--root',default='.');p.add_argument('--snapshot-id')
    p.add_argument('--prior');p.add_argument('--profile',default='hindsight-sso');a=p.parse_args()
    if a.action=='prepare':
        require(a.snapshot_id is not None,'SNAPSHOT_ID_REQUIRED')
        result=prepare(a.root,a.work,snapshot_id=a.snapshot_id,prior=json.loads(Path(a.prior).read_text()) if a.prior else None)
        result={k:result[k] for k in ['snapshot_id','path_count','unique_object_count','unique_bytes']}
    else:
        client=Client(a.profile)
        result={'upload':upload,'upload-bulk':upload_bulk,'verify':verify,'plan-retention':retention_plan,'cleanup':cleanup}[a.action](client,a.work)
        if a.action=='plan-retention':result={k:result[k] for k in ['snapshot_id','total_delete_bytes','scope']}|{'versions':len(result['delete'])}
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
