"""Fetch only one hair asset from the official ZIP using bounded range reads."""
import io
import json
import hashlib
import urllib.request
import zipfile
from pathlib import Path

URL='https://files.makehumancommunity.org/asset_packs/hair01/hair01_cc0.zip'
OUT=Path(__file__).resolve().parents[1]/'.runtime/assets/series01-dressing-source/o4saken-long01'


class RemoteZip(io.RawIOBase):
    def __init__(self):
        self.pos=0
        with urllib.request.urlopen(urllib.request.Request(URL,headers={'Range':'bytes=0-0'}),timeout=30) as r:
            if r.status!=206: raise ValueError('Range support required')
            self.size=int(r.headers['Content-Range'].split('/')[-1])
    def seekable(self): return True
    def seek(self,offset,whence=0):
        self.pos=offset if whence==0 else self.pos+offset if whence==1 else self.size+offset
        return self.pos
    def tell(self): return self.pos
    def read(self,n=-1):
        n=min(self.size-self.pos,n if n>=0 else self.size-self.pos)
        if n==0:return b''
        if n<0 or n>30_000_000:raise ValueError('Oversized read')
        start=self.pos
        with urllib.request.urlopen(urllib.request.Request(URL,headers={'Range':f'bytes={start}-{start+n-1}'}),timeout=30) as r:
            if r.status!=206 or not r.headers['Content-Range'].startswith(f'bytes {start}-'):
                raise ValueError('Invalid range response')
            data=r.read(n+1)
        if len(data)!=n:raise ValueError('Truncated range')
        self.pos+=n
        return data


def main():
    if OUT.exists():raise ValueError('Refusing overwrite')
    with zipfile.ZipFile(RemoteZip()) as z:
        members=[i for i in z.infolist() if 'o4saken_long01' in i.filename.lower() and not i.is_dir()]
        if not members or sum(i.file_size for i in members)>50_000_000:raise ValueError('Asset missing or oversized')
        print([(i.filename,i.file_size) for i in members],flush=True)
        OUT.mkdir()
        records=[]
        for i in members:
            name=Path(i.filename).name
            if Path(name).suffix.lower() not in {'.obj','.mhclo','.mhmat','.png','.jpg','.txt','.json','.thumb','.license'}:
                continue
            data=z.read(i)  # CRC checked; no archive path extraction or execution.
            with (OUT/name).open('xb') as f:f.write(data)
            records.append({'archive_path':i.filename,'local':name,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
        (OUT/'acquisition.json').write_text(json.dumps({'source':URL,'files':records},indent=2))
        print('Downloaded selected data files only',flush=True)


if __name__=='__main__':main()
