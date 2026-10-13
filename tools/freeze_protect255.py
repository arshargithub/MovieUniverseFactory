"""Freeze a recoverable worktree snapshot locally; never uploads or deletes."""
from __future__ import annotations
import concurrent.futures
import hashlib
import json
import os
import shutil
import sqlite3
import subprocess
from datetime import datetime, timezone
from pathlib import Path
import protect255 as p

ROOT=p.ROOT
STAGE=ROOT/'.runtime/protection255-frozen'
OUT=p.OUT

def copy_independent(source,dest):
    dest.parent.mkdir(parents=True,exist_ok=True)
    if dest.exists(): raise RuntimeError('Refuse overwrite: '+str(dest))
    run=subprocess.run(['/bin/cp','-c',str(source),str(dest)],capture_output=True)
    if run.returncode:
        if dest.exists(): raise RuntimeError('Partial clone requires inspection: '+str(dest))
        shutil.copy2(source,dest)
    if source.stat().st_ino==dest.stat().st_ino: raise RuntimeError('Not independent')

def scanned(path):
    h=hashlib.sha256(); flags=set();tail=b''
    with path.open('rb') as f:
        for block in iter(lambda:f.read(8*1024*1024),b''):
            h.update(block);flags.update(p.scan(tail+block));tail=block[-512:]
    return h.hexdigest(),sorted(flags)

def main():
    if (OUT/'frozen-manifest.json').exists(): raise RuntimeError('Snapshot already exists; use a new bounded delta, never overwrite')
    STAGE.mkdir(parents=True,exist_ok=True)
    old=json.loads((OUT/'inventory.json').read_text());oldrows={r['path']:r for r in old['paths']}
    files=[x for x in p.base.paths(ROOT) if not p.excluded(x.relative_to(ROOT)) and (x.is_file() or x.is_symlink())]
    groups={};rows=[];symlinks=[]
    for path in files:
        rel=path.relative_to(ROOT).as_posix()
        if path.is_symlink():
            target=os.readlink(path);portable=target
            if target.startswith('/Users/adisharma/projects/MovieUniverseFactory/'):
                intended=ROOT/target.split('/MovieUniverseFactory/',1)[1]
                portable=os.path.relpath(intended,path.parent)
            resolved=(path.parent/portable).resolve()
            if not resolved.is_relative_to(ROOT):raise RuntimeError('Unresolved external link: '+rel)
            symlinks.append({'path':rel,'symlink':portable,'original_symlink':target,'target_exists':resolved.exists()})
            continue
        stat=path.stat();row=oldrows.get(rel,{})
        # A consistent database export has its own digest, not the mutable original's.
        if path.suffix in {'.db','.sqlite','.sqlite3'}:
            staged=STAGE/'databases'/rel;staged.parent.mkdir(parents=True,exist_ok=True)
            if not staged.exists():
                with sqlite3.connect('file:'+str(path)+'?mode=ro',uri=True) as src,sqlite3.connect(staged) as dst:
                    src.backup(dst)
                    if dst.execute('PRAGMA integrity_check').fetchone()[0]!='ok':raise RuntimeError('Database integrity')
            else:
                with sqlite3.connect('file:'+str(staged)+'?mode=ro',uri=True) as db:
                    if db.execute('PRAGMA integrity_check').fetchone()[0]!='ok':raise RuntimeError('Database integrity')
            digest,flags=scanned(staged)
            if flags:raise RuntimeError('Database credential finding: '+rel)
            source=staged;size=staged.stat().st_size
        else:
            source=path;size=stat.st_size
            if row.get('bytes')==size and row.get('mtime_ns')==stat.st_mtime_ns:
                digest=row['sha256']
            else:
                digest,flags=scanned(path)
                if flags:raise RuntimeError('New credential finding: '+rel)
        rows.append({'path':rel,'bytes':size,'sha256':digest,'mode':stat.st_mode&0o777})
        groups.setdefault(digest,{'sha256':digest,'bytes':size,'paths':[],'source':source})['paths'].append(rel)
    findings=[]
    def freeze(item):
        dest=STAGE/'objects'/item['sha256'][:2]/item['sha256']
        existing=scanned(dest) if dest.exists() else None
        if existing and existing[0]!=item['sha256']:
            # Interrupted preparation, never an authoritative source. Preserve it.
            import uuid
            quarantine=STAGE/'quarantine'/(item['sha256']+'-'+str(uuid.uuid4()))
            quarantine.parent.mkdir(parents=True,exist_ok=True);dest.rename(quarantine)
            existing=None
        if not dest.exists():copy_independent(item['source'],dest)
        actual,flags=existing if existing else scanned(dest)
        if actual!=item['sha256']:raise RuntimeError('Source changed: '+item['paths'][0])
        disposition=None
        if flags:
            # Narrow, content-bound inspected false positive: Inkscape SVG mask fragment.
            if item['paths']==['.runtime/brushstroke-tools-1.2.3-inspection/icons/random.svg'] and flags==['provider_key']:
                import re
                data=dest.read_bytes()
                matches=list(re.finditer(rb'sk-[A-Za-z0-9_-]{20,}',data))
                if all(data[max(0,m.start()-8):m.start()]==b'uri="#ma' for m in matches):
                    disposition='Reviewed SVG mask fragment, not a provider key'
            if not disposition:raise RuntimeError('Unresolved credential-like content: '+item['paths'][0])
        return {'sha256':actual,'bytes':item['bytes'],'paths':item['paths']},flags,disposition
    objects=[]
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        for n,(item,flags,disposition) in enumerate(pool.map(freeze,groups.values()),1):
            objects.append(item)
            if flags:findings.append({'sha256':item['sha256'],'paths':item['paths'],'categories':flags,'disposition':disposition})
            if n%1000==0:print(json.dumps({'frozen':n,'total':len(groups)}),flush=True)
    manifest={'schema_version':'2.0','kind':'active-project-backup','snapshot_id':'protect255-20261013',
       'created_at':datetime.now(timezone.utc).isoformat(),'source_root':str(ROOT),'git':p.base.git_metadata(ROOT),
       'paths':sorted(rows+symlinks,key=lambda r:r['path']),'objects':sorted(objects,key=lambda r:r['sha256']),
       'path_count':len(rows)+len(symlinks),'unique_object_count':len(objects),
       'physical_bytes':sum(x['bytes'] for x in rows),'unique_bytes':sum(x['bytes'] for x in objects),
       'credential_like_paths':[],'reviewed_scanner_findings':findings,
       'excluded':old['excluded'],'database_method':'SQLite online backup with integrity_check; independent copies; initial capture retained on resume, final ledger belongs in bounded delta',
       'freeze_method':'Independent copy-on-write clone or full copy, then full-byte hash and expanded credential scan; not hardlinks',
       'symlink_policy':'Old Mac project absolute test aliases remapped in manifest only to relative SSD tree; dangling targets reported; originals untouched',
       'recovery_copy_verified':False}
    (OUT/'frozen-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({k:v for k,v in manifest.items() if k not in {'paths','objects','git'}},indent=2))

if __name__=='__main__':main()
