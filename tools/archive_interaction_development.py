"""Snapshot historical 3D-05 evidence into deduplicated, split gzip tar parts.

Excludes private/runtime directories. Current closure-* probes are a subsequent
work package and are not misrepresented as part of the accepted preview backup.
"""
import gzip,hashlib,json,subprocess,tarfile,time
from pathlib import Path
from movie_factory.packages import atomic_json,file_digest

class Parts:
    def __init__(self,root,limit=512*1024*1024):self.root=root;self.limit=limit;self.size=0;self.stream=None;self.paths=[]
    def write(self,data):
        total=len(data);view=memoryview(data)
        while view:
            if self.stream is None or self.size==self.limit:
                if self.stream:self.stream.close()
                path=self.root/f'evidence.tar.gz.part{len(self.paths)+1:03d}';self.paths.append(path);self.stream=path.open('wb');self.size=0
            n=min(len(view),self.limit-self.size);self.stream.write(view[:n]);self.size+=n;view=view[n:]
        return total
    def flush(self):
        if self.stream:self.stream.flush()
    def close(self):
        if self.stream:self.stream.close()


def main():
    repo=Path.cwd();out=repo/'exports'/time.strftime('3d05-development-backup-%Y%m%dT%H%M%SZ',time.gmtime());out.mkdir(parents=True)
    roots=[repo/'runs/3d05']
    roots.extend(p for p in (repo/'runs/3d05-development').iterdir() if p.is_dir() and not p.name.startswith('closure-'))
    files=sorted({p for root in roots for p in root.rglob('*') if p.is_file() and not p.is_symlink() and not any(x in {'.worker_runtime','__pycache__','.env','.env.local','.venv'} for x in p.parts) and p.suffix!='.pyc'})
    entries=[]
    for index,p in enumerate(files):
        entries.append({'path':str(p.relative_to(repo)),'bytes':p.stat().st_size,'sha256':file_digest(p)})
        if index%1000==0:print('inventoried',index,'/',len(files),flush=True)
    manifest={'schema_version':'1.0','scope':'Historical 3D-05 scored attempts and development evidence through Director-accepted coordinated prototype; closure-* follow-up probes excluded','source_commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'entries':entries,'excluded':['.worker_runtime','__pycache__','.env','.env.local','.venv','closure-* follow-up probes'],'status':'DEVELOPMENT_BACKUP_NOT_GREEN_EXPORT'}
    atomic_json(out/'INVENTORY.json',manifest)
    subprocess.run(['git','bundle','create',str(out/'source-history.bundle'),'--all'],check=True)
    (out/'REPRODUCIBILITY.md').write_text('''# 3D-05 historical development backup

This is not a GREEN closure bundle. It preserves rejected/scored attempts and the accepted coordinated development preview with its unresolved technical finding. The follow-up closure repair is a separate work package.

Download every numbered `evidence.tar.gz.partNNN` asset and verify each SHA-256 in `PARTS.json`. Concatenate in lexical order to reconstruct `evidence.tar.gz`, then extract with a tar implementation supporting hard links. Duplicate bytes are stored once, but extraction restores the original file paths. Verify every restored path, size and SHA-256 against INVENTORY.json.

`source-history.bundle` contains the repository history and exact source commits recorded by the runs. Clone it into a new directory with `git clone source-history.bundle MovieUniverseFactory`, restore the `runs/` tree there, and follow the relevant source revision's reproduction guide. Use a project-local virtual environment and the recorded Blender build. Staged source assets may need restoration according to the earlier experiment guides; packed native scenes are included for inspection. No .env or worker runtime homes are included.

The `.blend` files, complete original rendered frames, playback HTML, measured geometry, actual negative controls, original pending/failed results and subsequent Director review records are preserved as evidence. A development visual pass does not override a frozen technical failure. GitHub publication/closure remains a separate decision.
''')
    packed=Parts(out);seen={}
    with gzip.GzipFile(fileobj=packed,mode='wb',compresslevel=3,mtime=0) as gz:
        with tarfile.open(fileobj=gz,mode='w|') as tar:
            for name in ('INVENTORY.json','REPRODUCIBILITY.md','source-history.bundle'):
                tar.add(out/name,arcname=name,recursive=False)
            for index,item in enumerate(entries):
                p=repo/item['path'];key=(item['sha256'],item['bytes']);info=tar.gettarinfo(str(p),arcname=item['path']);info.uid=info.gid=0;info.uname=info.gname=''
                if p.stat().st_size!=item['bytes']:raise ValueError('Source changed after inventory')
                if key in seen:
                    info.type=tarfile.LNKTYPE;info.linkname=seen[key];info.size=0;tar.addfile(info)
                else:
                    with p.open('rb') as source:tar.addfile(info,source)
                    seen[key]=item['path']
                if index%1000==0:print('packed',index,'/',len(entries),flush=True)
    packed.close()
    atomic_json(out/'PARTS.json',{'schema_version':'1.0','scope':manifest['scope'],'source_commit':manifest['source_commit'],'artifact_count':len(entries),'logical_bytes':sum(i['bytes'] for i in entries),'unique_content_count':len(seen),'inventory_sha256':file_digest(out/'INVENTORY.json'),'parts':[{'name':p.name,'bytes':p.stat().st_size,'sha256':file_digest(p)} for p in packed.paths]})
    print('ARCHIVE',out,flush=True)

if __name__=='__main__':main()
