"""Read/decode/hash actual completed batches; diagnostic sheets, not art PASS."""
import json,sys
from pathlib import Path
from PIL import Image,ImageDraw
from movie_factory import production_knowledge as pk
r=Path(__file__).resolve().parents[1];o=r/'results/sikh363/contact-sheets';o.mkdir(exist_ok=True)
for n in map(int,sys.argv[1:]):
 step='frames'+str(n).zfill(2);record=json.loads((r/'results/sikh363'/('motion-c42-'+step+'-run.json')).read_text());assert record['status']=='RETURNED'
 folder=r/'.runtime/factory-native'/('sikh363-motion-c42-'+step);rows=json.loads((folder/'frames.json').read_text());recipe=json.loads((r/record['recipe']['path']).read_text());assert {x['frame'] for x in rows}==set(recipe['frames'])
 im=Image.new('RGB',(864,808),(28,28,28));draw=ImageDraw.Draw(im)
 for j,row in enumerate(sorted(rows,key=lambda z:z['frame'])):
  p=folder/row['file'];assert pk.file_hash(p)==row['sha256'];a=Image.open(p).convert('RGB');assert a.size==(432,768);a.thumbnail((216,384));x=j%4*216;y=j//4*404;im.paste(a,(x,y+20));draw.text((x+5,y+3),str(row['frame']),fill='white')
 path=o/('batch'+str(n).zfill(2)+'.jpg');im.save(path,quality=94);print(path.relative_to(r))
