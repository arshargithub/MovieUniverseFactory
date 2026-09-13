"""Checksums for this pass; no archive duplication and no private settings read."""
from pathlib import Path
import hashlib,json,os
ROOT=Path(__file__).resolve().parents[3];R=ROOT/'results/demonstrator-01/rough-cut';files=set()
for directory in [R,*sorted((ROOT/'runs/demonstrator-01').glob('cut-*'))]:
 if directory.is_dir():
  for p in directory.rglob('*'):
   if p.is_file() and '__pycache__' not in p.parts and p.name not in ('.DS_Store','ARTIFACTS.json'):files.add(p)
frozen=json.loads((R/'FROZEN_CUT.json').read_text())
files.update(ROOT/row['path'] for row in frozen['dirty_implementation_binding'])
rows=[]
for p in sorted(files):
 row={'path':str(p.relative_to(ROOT))}
 if p.is_symlink():row['symlink']=os.readlink(p)
 else:
  with p.open('rb') as f:row.update(bytes=p.stat().st_size,sha256=hashlib.file_digest(f,'sha256').hexdigest())
 rows.append(row)
result={'scope':'current rough-cut pass, source bindings and local native/media evidence; self excluded','count':len(rows),'physical_file_bytes':sum(r.get('bytes',0) for r in rows),'artifacts':rows}
(R/'ARTIFACTS.json').write_text(json.dumps(result,indent=2)+'\n');print({k:v for k,v in result.items() if k!='artifacts'})
