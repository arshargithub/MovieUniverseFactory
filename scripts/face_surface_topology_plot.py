"""Diagnostic numeric mesh chart, not a texture or source-image alteration."""
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw

base=Path(__file__).resolve().parents[1]/'.runtime/art-direction/series01-facebuilder-trial-01/face-surface-inspect-01'
a=np.load(base/'surface.npz');v=a['vertices'];edges=a['edges']
im=Image.new('RGB',(1500,1000),'white');draw=ImageDraw.Draw(im)
for panel,key in enumerate(('vertices','eyeBlinkLeft')):
    q=a[key]
    def point(i):return (int(panel*750+50+(q[i,0]-.15)*1150),int(920-(q[i,2]-.15)*1600))
    ids=set(np.where((v[:,0]>.15)&(v[:,0]<.72)&(v[:,2]>.15)&(v[:,2]<.68)&(v[:,1]<-.4))[0])
    for e in edges:
        if all(int(i) in ids for i in e):draw.line([point(e[0]),point(e[1])],fill=(120,120,120),width=1)
    # Label only center-front geometry, easing anatomical patch selection.
    for i in ids:
        if .27<v[i,0]<.52 and .27<v[i,2]<.41:
            p=point(i);draw.ellipse((p[0]-2,p[1]-2,p[0]+2,p[1]+2),fill='red')
            draw.text(p,str(i),fill='blue')
    draw.text((panel*750+30,20),key,fill='black')
im.save(base/'eye-topology-chart.png')
