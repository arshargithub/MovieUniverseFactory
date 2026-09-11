import hashlib,json,sys,tarfile
from pathlib import Path
from movie_factory.packages import atomic_json,file_digest
class Joined:
    def __init__(self,paths):self.paths=iter(paths);self.current=None
    def read(self,n=-1):
        if n<0:raise ValueError('Unbounded archive read refused')
        chunks=[]
        while n:
            if self.current is None:
                p=next(self.paths,None)
                if p is None:break
                self.current=p.open('rb')
            data=self.current.read(n)
            if not data:self.current.close();self.current=None;continue
            chunks.append(data);n-=len(data)
        return b''.join(chunks)
r=Path(sys.argv[1]);parts=json.loads((r/'PARTS.json').read_text());expected={x['path']:x for x in json.loads((r/'INVENTORY.json').read_text())['entries']};seen={}
for part in parts['parts']:assert file_digest(r/part['name'])==part['sha256']
with tarfile.open(fileobj=Joined([r/p['name'] for p in parts['parts']]),mode='r|gz') as tar:
 for member in tar:
  if member.islnk():digest,size=seen[member.linkname]
  elif member.isfile():
   h=hashlib.sha256();size=0
   with tar.extractfile(member) as data:
    for chunk in iter(lambda:data.read(1024*1024),b''):h.update(chunk);size+=len(chunk)
   digest=h.hexdigest()
  else:raise ValueError('Unexpected archive member type')
  seen[member.name]=(digest,size)
  if member.name in expected:
   item=expected[member.name];assert digest==item['sha256'] and size==item['bytes'],member.name
assert set(expected)<=set(seen)
atomic_json(r/'LOCAL-VERIFICATION.json',{'passed':True,'restored_logical_files_verified':len(expected),'part_count':len(parts['parts']),'inventory_sha256':file_digest(r/'INVENTORY.json'),'verification':'Streaming decompression and content hash verification, including hard-link reconstruction'})
print('VERIFIED',len(expected),'restored files')
