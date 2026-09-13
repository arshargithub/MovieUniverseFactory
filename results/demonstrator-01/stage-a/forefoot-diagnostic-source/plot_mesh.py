from pathlib import Path
import json
from PIL import Image,ImageDraw
base=Path('runs/demonstrator-01/forefoot-diagnosis')
img=Image.new('RGB',(1400,1000),'white');draw=ImageDraw.Draw(img)
for col,f in enumerate((2.75,3.875)):
 for row,kind in enumerate(('source','candidate')):
  d=json.loads((base/f'{kind}-mesh-{f}.json').read_text());pts={int(k):v for k,v in d['points'].items()}
  xs=[v[1] for v in pts.values()];ys=[v[2] for v in pts.values()];cx=(max(xs)+min(xs))/2;cy=(max(ys)+min(ys))/2;s=340/max(max(xs)-min(xs),max(ys)-min(ys))
  def xy(i):p=pts[i];return(col*700+350+(p[1]-cx)*s,row*500+270-(p[2]-cy)*s)
  for tri in sorted(d['triangles'],key=lambda t:sum(pts[i][0] for i in t)):
   draw.polygon([xy(i) for i in tri],fill=(191,199,206),outline=(91,105,113))
  draw.text((col*700+25,row*500+20),f'{kind.upper()} frame {f} | right lower forelimb | side projection',fill='black')
  draw.text((col*700+25,row*500+45),'Independently centered/scaled; mesh shape diagnostic, not a render',fill='black')
img.save(base/'mesh-comparison.png')
