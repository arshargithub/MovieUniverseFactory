"""Plot retained diagnostic geometry; no image generation or asset editing."""
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw

root=Path(__file__).resolve().parents[1]/'.runtime/art-direction/series01-facebuilder-trial-01'
out=root/'wardrobe185-contact05/contact-comparison.png'
if out.exists():raise ValueError('Preserve existing diagnostic plot')
fig=Image.new('RGB',(1200,500),'white');draw=ImageDraw.Draw(fig)
draw.text((20,8),'Native cloth centre sections: blue lower layer, orange upper layer. Not garment appearance.',fill='black')
for row,name in enumerate(('contact05','contactoff05')):
    with np.load(root/('wardrobe185-'+name)/'trajectory.npz') as d:a=d['frames']
    for col,frame in enumerate((1,12,36,72)):
        x0=col*300+35;y0=row*225+55
        draw.text((x0,y0-20),('Contact on' if row==0 else 'Contact off')+' / frame '+str(frame),fill='black')
        draw.rectangle((x0,y0,x0+240,y0+170),outline='gray')
        for layer,c in enumerate(('steelblue','darkorange')):
            p=a[frame-1,layer*289:(layer+1)*289].reshape(17,17,3)[:,8]
            draw.line([(x0+(float(q[0])+.25)/.6*240,y0+170-(float(q[2])+.01)/.19*170) for q in p],fill=c,width=3)
        draw.text((x0,y0+175),'x: -0.25..0.35 m; height: -0.01..0.18 m',fill='black')
fig.save(out)
