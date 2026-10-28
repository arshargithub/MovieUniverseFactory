"""Screen outgoing blob bytes without printing any matching values."""
import json,re,subprocess
from pathlib import Path
lines=subprocess.check_output(['git','rev-list','--objects','origin/main..HEAD'],text=True).splitlines()
items={line.split(' ',1)[0]:line.split(' ',1)[1] if ' ' in line else '' for line in lines}
pattern=re.compile(rb'(?:AKIA|ASIA)[0-9A-Z]{16}|AIza[0-9A-Za-z_-]{30,}|hf_[0-9A-Za-z]{25,}|sk-[0-9A-Za-z_-]{28,}')
p=subprocess.Popen(['git','cat-file','--batch'],stdin=subprocess.PIPE,stdout=subprocess.PIPE)
findings=[];scanned=total=0
for oid,path in items.items():
 p.stdin.write((oid+'\n').encode());p.stdin.flush();h=p.stdout.readline().split()
 size=int(h[2]);data=p.stdout.read(size);assert p.stdout.read(1)==b'\n'
 if h[1]!=b'blob':continue
 scanned+=1;total+=size
 if pattern.search(data):findings.append(dict(oid=oid,path=path,category='credential_like',bytes=size))
p.stdin.close();p.wait()
out=dict(blobs=scanned,bytes=total,findings=findings,range=subprocess.check_output(['git','rev-parse','origin/main','HEAD'],text=True).splitlines(),limit='Lexical scan and exact path/range inspection; not a proof against every possible secret.')
Path('results/workflow397/GIT_SCREEN.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(dict(blobs=scanned,bytes=total,findings=findings),indent=2))
