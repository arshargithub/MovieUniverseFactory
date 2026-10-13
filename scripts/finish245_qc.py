"""Read source-bound render progress and create review contact sheets/metrics."""
import json,sys
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
from finish242_audition import ROOT,sha
OUT=ROOT/'.runtime/art-direction/series01-finish245'
def differences(a,b):
    aa=np.asarray(Image.open(a).convert('RGB')).astype(float);bb=np.asarray(Image.open(b).convert('RGB')).astype(float)
    if aa.shape!=bb.shape:raise ValueError('Mismatched image dimensions')
    d=abs(aa-bb);pixel=d.max(2)
    return dict(mean=float(d.mean()),maximum=float(d.max()),fraction_over4=float(np.mean(pixel>4)),fraction_over20=float(np.mean(pixel>20)),strict_one_level=bool(d.max()<=1))
def profile():
    cpu=OUT/'cpu-delivery';gpu=OUT/'gpu-delivery02'
    result={'compared':[]}
    for idx in (0,173):
        a=cpu/f'frame-{idx:04d}.png';b=gpu/f'frame-{idx:04d}.png';d=differences(a,b)
        d.update(frame=idx,pass_alarm=d['mean']<=2 and d['fraction_over20']<=.01);result['compared'].append(d)
    d=differences(gpu/'frame-0000.png',gpu/'repeat-02-0000.png')
    d['pass_alarm']=d['mean']<=.05 and d['fraction_over4']<=.001 and d['maximum']<=12;result['repeat']=d
    path=OUT/'profile-metrics.json'
    if path.exists():raise ValueError('Preserve metrics')
    path.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
def sheets(op):
    if op not in ('opening-final','opening-resume-final','route-final','opening-coarse','route-coarse'):raise ValueError('Closed sheet op')
    folder=OUT/op;progress=folder/('result.json' if (folder/'result.json').exists() else 'progress.json')
    data=json.loads(progress.read_text());frames=data['frames'];out=OUT/'sheets'/op;out.mkdir(parents=True,exist_ok=True)
    made=[]
    for offset in range(0,len(frames),20):
        rows=frames[offset:offset+20]
        if len(rows)<20 and not data['complete']:continue
        dest=out/f"sheet-{rows[0]['index']:04d}.jpg"
        if dest.exists():continue
        canvas=Image.new('RGB',(5*216,4*408),(235,230,215));draw=ImageDraw.Draw(canvas)
        for j,r in enumerate(rows):
            p=folder/r['file']
            if sha(p)!=r['sha256']:raise ValueError('Unacknowledged/changed frame')
            im=Image.open(p).convert('RGB');im.thumbnail((216,384));x=j%5*216;y=j//5*408;canvas.paste(im,(x,y));draw.text((x+5,y+387),f"{r['index']} | {r['index']/24:.3f}s",fill=(20,20,20))
        canvas.save(dest,quality=94);made.append(str(dest))
    print(json.dumps(made))
if __name__=='__main__':
    if sys.argv[1:]==['profile']:profile()
    elif len(sys.argv)==2:sheets(sys.argv[1])
    else:raise ValueError('Closed245 QC')
