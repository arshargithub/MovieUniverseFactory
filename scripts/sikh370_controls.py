"""Verify returned control manifests and create review contact sheets only."""
import json,sys
from pathlib import Path
from PIL import Image,ImageDraw
from movie_factory import production_knowledge as pk
r=Path(__file__).resolve().parents[1];step=sys.argv[1];p=r/f'results/sikh370/motion-c66-{step}-run.json';run=json.loads(p.read_text());assert run['status']=='RETURNED';b=run['artifacts']['frames'];mf=r/b['path'];assert pk.file_hash(mf)==b['sha256'];rows=json.loads(mf.read_text());size=360
sheet=Image.new('RGB',(size*3,((len(rows)+2)//3)*(size+26)),(230,230,230));d=ImageDraw.Draw(sheet)
for i,row in enumerate(rows):
 image=mf.parent/row['file'];assert pk.file_hash(image)==row['sha256'];im=Image.open(image).convert('RGB');im.thumbnail((size,size));x=(i%3)*size;y=(i//3)*(size+26);sheet.paste(im,(x,y));d.text((x+5,y+size+5),str(row['frame']),fill='black')
out=r/'.runtime/art-direction/sikh370-review-c66';out.mkdir(parents=True,exist_ok=True);p=out/(step+'-controls.jpg');assert not p.exists();sheet.save(p,quality=95);print(p)
