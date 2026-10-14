"""Bounded recovery delta over the immutable base; no production edits or deletions."""
import json
import sqlite3
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from freeze_protect255 import scanned,copy_independent,STAGE
from upload_protect255 import ROOT,OUT,BUCKET,PREFIX,PROFILE,REGION,AWS,object_key
from protect255 import excluded

BASE_HEAD='adff3bd1af362952c12f132ffe4dc820a004cadb'

def put(path,key):
    subprocess.run([AWS,'s3','cp',str(path),f's3://{BUCKET}/{key}',
        '--checksum-algorithm','SHA256','--only-show-errors','--profile',PROFILE,'--region',REGION],check=True)

def main():
    restore=json.loads((OUT/'remote-capsule-restore.json').read_text())
    if not (restore['all_hashes_match'] and restore['native_dependency_checks_pass']):
        raise ValueError('Remote native restore prerequisite')
    target=OUT/'final-manifest.json'
    if target.exists():raise ValueError('Refuse replacement of final snapshot')
    manifest=json.loads((OUT/'frozen-manifest.json').read_text())
    rows={r['path']:r for r in manifest['paths']}
    git=lambda *args:subprocess.check_output(['git',*args],cwd=ROOT).decode().strip()
    if git('diff','--name-only') or git('diff','--cached','--name-only'):
        raise ValueError('Commit scoped tracked changes before final delta')
    changed=set(filter(None,git('diff','--name-only',BASE_HEAD,'HEAD').splitlines()))
    changed.update(str(p.relative_to(ROOT)) for p in (ROOT/'.runtime/knowledge-pilot213/calibration255').rglob('*') if p.is_file())
    changed.add('.runtime/experiment-ops.sqlite3')
    # Backup records are intentionally outside the worktree manifest and travel separately.
    records=sorted(p for p in changed if p.startswith('results/backup/'))
    selected=sorted(p for p in changed if not excluded(Path(p)))
    stage=STAGE/'final-delta';stage.mkdir(exist_ok=False)
    uploads={}
    for rel in selected:
        source=ROOT/rel
        if not source.is_file() or source.is_symlink():raise ValueError('Delta needs an ordinary existing file: '+rel)
        frozen=stage/'files'/rel;frozen.parent.mkdir(parents=True,exist_ok=True)
        if source.suffix in {'.sqlite3','.sqlite','.db'}:
            with sqlite3.connect('file:'+str(source)+'?mode=ro',uri=True) as src,sqlite3.connect(frozen) as dst:
                src.backup(dst)
                if dst.execute('PRAGMA integrity_check').fetchone()[0]!='ok':raise ValueError('DB integrity')
        else:copy_independent(source,frozen)
        sha,flags=scanned(frozen)
        if flags:raise ValueError('Delta credential-like finding: '+rel)
        rows[rel]={'path':rel,'sha256':sha,'bytes':frozen.stat().st_size,'mode':source.stat().st_mode&0o777}
        uploads[sha]=frozen
    prior={o['sha256'] for o in manifest['objects']}
    for sha,source in uploads.items():
        if sha not in prior:put(source,object_key(sha))
    objects={}
    for row in rows.values():
        if 'sha256' not in row:continue
        obj=objects.setdefault(row['sha256'],{'sha256':row['sha256'],'bytes':row['bytes'],'paths':[]})
        obj['paths'].append(row['path'])
    manifest.update(snapshot_id='protect255-20261013-final',created_at=datetime.now(timezone.utc).isoformat(),
        paths=sorted(rows.values(),key=lambda r:r['path']),objects=sorted(objects.values(),key=lambda r:r['sha256']),
        path_count=len(rows),unique_object_count=len(objects),physical_bytes=sum(r.get('bytes',0) for r in rows.values()),
        unique_bytes=sum(o['bytes'] for o in objects.values()),
        git={'head':git('rev-parse','HEAD'),'branch':git('branch','--show-current')},
        bounded_delta={'base_snapshot':'protect255-20261013','base_commit':BASE_HEAD,
            'updated_paths':selected,'scope':'Committed recovery changes, calibration evidence and consistent current operating ledger only; no production changes',
            'final_receipts':'Verification receipts created afterward are separately uploaded and Git committed; not part of this immutable manifest'},
        recovery_copy_verified=False)
    target.write_text(json.dumps(manifest,indent=2)+'\n')
    prefix=f'movie-factory/backup/active/movie-universe-factory/snapshots/{manifest["snapshot_id"]}'
    key=prefix+'/manifest.json';put(target,key)
    subprocess.run([str(ROOT/'.venv/bin/python'),str(ROOT/'tools/verify_active_backup.py'),
        '--manifest',str(target),'--receipt',str(OUT/'final-verification.json'),
        '--bucket',BUCKET,'--object-prefix',PREFIX,'--manifest-key',key,'--profile',PROFILE,'--region',REGION],check=True)
    # Small, explicitly named recovery records; never arbitrary files in the backup folder.
    names={'accepted-capsule.json','remote-verification.json','remote-capsule-restore.json',
           'native-inspect-remote-opening.json','native-inspect-remote-route.json','final-verification.json','git-push-receipt.json'}
    for name in sorted(names):
        path=OUT/name
        sha,flags=scanned(path)
        if flags:raise ValueError('Receipt credential-like finding: '+name)
        put(path,prefix+'/records/'+name)
    print(json.dumps({'final_snapshot':manifest['snapshot_id'],'updated_paths':len(selected),'records_uploaded':len(names),'remote_verified':True}),flush=True)

if __name__=='__main__':main()
