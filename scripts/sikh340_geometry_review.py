"""Orthographic data plot of retained solver vertices; not a production render."""
from pathlib import Path
import sys
import numpy as np
from PIL import Image,ImageDraw
r=Path(__file__).resolve().parents[1]
cycle=int(sys.argv[1]) if len(sys.argv)>1 else 15
actor=sys.argv[2] if len(sys.argv)>2 else 'leader'
assert cycle in range(13,18) and actor in ('leader','crowd')
base=r/f'.runtime/factory-native/sikh340-look-c{cycle}-save'
p=np.load(base/(actor+'-pattern.npz'));q=np.load(base/(actor+'-settle.npz'))
im=Image.new('RGB',(1400,750),(235,235,230));d=ImageDraw.Draw(im)
for column,(name,points) in enumerate([('Initial fitted shell',q['start']),('Settled shell',q['final'])]):
 for row,(title,axis,depth) in enumerate([('Front',0,1),('Side',1,0)]):
    x0=column*700;y0=row*375;d.text((x0+12,y0+12),name+' / '+title,fill='black')
    for face in sorted(q['faces'],key=lambda ids:float(points[ids,depth].mean()),reverse=True):
        xyz=points[face];normal=np.cross(xyz[1]-xyz[0],xyz[2]-xyz[0]);normal/=max(1e-9,np.linalg.norm(normal))
        light=.35+.65*abs(float(normal@np.array([.3,-.8,.52])))
        polygon=[(x0+350+float(v[axis])*600,y0+350-(float(v[2])-(.83 if actor=='crowd' else 0))*600) for v in xyz]
        d.polygon(polygon,fill=(int(45*light),int(100*light),int(180*light)),outline=(30,45,60))
    d.text((x0+12,y0+355),'Actual cached mesh coordinates; no smoothing/material/lighting qualification',fill='black')
out=base/(actor+'-geometry-review.png');im.save(out);print(out)
