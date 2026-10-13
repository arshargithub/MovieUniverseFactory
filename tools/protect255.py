"""Scoped protection preparation. No secret values are emitted; uploads are separate."""
from __future__ import annotations
import argparse
import concurrent.futures
import hashlib
import json
import os
import re
import sqlite3
import subprocess
from datetime import datetime, timezone
from pathlib import Path
import create_active_backup_manifest as base

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'results/backup/protect255'
EXTRA_PARTS = {'.aws', '.ssh', '.config', '.cache'}
EXTRA_PREFIXES = (('.runtime','protection255-restore'), ('.runtime','protection255-frozen'))
# Literal prechecks avoid applying every regular expression to large render files.
RULES = [
    (b'AKIA', re.compile(rb'AKIA[A-Z0-9]{16}'), 'aws_access'),
    (b'ASIA', re.compile(rb'ASIA[A-Z0-9]{16}'), 'aws_temporary_access'),
    (b'sk-', re.compile(rb'sk-[A-Za-z0-9_-]{20,}'), 'provider_key'),
    (b'AIza', re.compile(rb'AIza[0-9A-Za-z_-]{30,}'), 'google_key'),
    (b'g', re.compile(rb'gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}'), 'github_token'),
    (b'PRIVATE KEY', re.compile(rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----'), 'private_key'),
    (b'X-Amz-Signature=', re.compile(rb'X-Amz-Signature=[0-9a-f]{64}'), 'signed_url'),
    (b'Bearer ', re.compile(rb'Bearer [A-Za-z0-9._-]{30,}'), 'bearer'),
]
ASSIGNMENT_NAMES = (b'openai_api_key',b'gemini_api_key',b'runway_api_key',b'aws_secret_access_key',b'github_token')
ASSIGNMENT_RULE = re.compile(rb'(?:openai_api_key|gemini_api_key|runway_api_key|aws_secret_access_key|github_token)[\"\s]*[:=][\"\s]*[A-Za-z0-9_./+-]{24,}', re.I)

def scan(data):
    flags={name for prefix, pattern, name in RULES if prefix in data and pattern.search(data)}
    lower=data.lower()
    if any(name in lower for name in ASSIGNMENT_NAMES) and ASSIGNMENT_RULE.search(data):
        flags.add('credential_assignment')
    return sorted(flags)

def excluded(p):
    return (base.excluded(p) or bool(EXTRA_PARTS.intersection(p.parts))
            or p.name in {'private-link.txt', 'credentials', 'token.json', 'tokens.json'}
            or any(p.parts[:len(x)] == x for x in EXTRA_PREFIXES))

def inspect_file(path):
    rel = path.relative_to(ROOT).as_posix()
    if path.is_symlink():
        target = path.resolve()
        return {'path': rel, 'symlink': os.readlink(path), 'external': not target.is_relative_to(ROOT)}, []
    before = path.stat(); h = hashlib.sha256(); findings = set(); tail=b''
    with path.open('rb') as f:
        for block in iter(lambda:f.read(8*1024*1024), b''):
            h.update(block); findings.update(scan(tail+block)); tail=block[-512:]
    after=path.stat()
    if (before.st_ino,before.st_size,before.st_mtime_ns)!=(after.st_ino,after.st_size,after.st_mtime_ns):
        raise RuntimeError('Changed during hash: '+rel)
    return dict(path=rel, bytes=after.st_size, sha256=h.hexdigest(),mtime_ns=after.st_mtime_ns,mode=after.st_mode&0o777), sorted(findings)

def inventory():
    OUT.mkdir(parents=True,exist_ok=True)
    selected=[p for p in base.paths(ROOT) if not excluded(p.relative_to(ROOT)) and (p.is_file() or p.is_symlink())]
    rows=[]; findings=[]; objects={}
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        for n,(row,flags) in enumerate(pool.map(inspect_file,selected),1):
            rows.append(row)
            if flags: findings.append({'path':row['path'],'categories':flags})
            if 'sha256' in row:
                item=objects.setdefault(row['sha256'],dict(sha256=row['sha256'],bytes=row['bytes'],paths=[]))
                item['paths'].append(row['path'])
            if n%1000==0: print(json.dumps({'scanned':n,'total':len(selected),'flagged':len(findings)}),flush=True)
    manifest=dict(schema_version='2.0',kind='active-project-backup',snapshot_id='protect255-initial',
        created_at=datetime.now(timezone.utc).isoformat(),source_root=str(ROOT),git=base.git_metadata(ROOT),
        paths=rows,objects=sorted(objects.values(),key=lambda x:x['sha256']),path_count=len(rows),
        unique_object_count=len(objects),physical_bytes=sum(r.get('bytes',0) for r in rows),
        unique_bytes=sum(o['bytes'] for o in objects.values()),credential_like_paths=[x['path'] for x in findings],
        screening_findings=findings,external_symlinks=[r['path'] for r in rows if r.get('external')],
        excluded=['standard active-backup policy','credential stores/cache','private-link.txt bearer URLs','protection staging/restoration'],
        readiness='PREPARATION_ONLY_NEEDS_FINDING_REVIEW_AND_STABLE_FREEZE')
    (OUT/'inventory.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({k:v for k,v in manifest.items() if k not in {'paths','objects'}},indent=2))

def git_scan():
    base_ref='fd5ca98002ae074e62c88b8c9ac514cf3b29aff0'
    def git(*a):return subprocess.check_output(['git',*a],cwd=ROOT)
    refs=git('rev-list','--objects',base_ref+'..HEAD').decode().splitlines()
    candidates={line.split(' ',1)[0]:line.split(' ',1)[1] if ' ' in line else '' for line in refs}
    proc=subprocess.Popen(['git','cat-file','--batch'],cwd=ROOT,stdin=subprocess.PIPE,stdout=subprocess.PIPE)
    flagged=[]; blobs=0
    for oid,path in candidates.items():
        proc.stdin.write((oid+'\n').encode());proc.stdin.flush()
        header=proc.stdout.readline().decode().split(); size=int(header[2]); data=proc.stdout.read(size);proc.stdout.read(1)
        if header[1]!='blob':continue
        blobs+=1; flags=scan(data)
        if flags:flagged.append(dict(oid=oid,path=path,categories=flags))
    proc.stdin.close();proc.wait()
    OUT.mkdir(parents=True,exist_ok=True)
    report=dict(remote_base=base_ref,head=git('rev-parse','HEAD').decode().strip(),
       commits=int(git('rev-list','--count',base_ref+'..HEAD')),blobs_scanned=blobs,findings=flagged,
       forbidden_paths=[p for p in candidates.values() if p and excluded(Path(p))],passed=not flagged)
    (OUT/'git-screen.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['inventory','git_scan']);args=p.parse_args();globals()[args.mode]()
