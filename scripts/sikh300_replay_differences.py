"""Localize numerical replay discrepancies without changing admission thresholds."""
import json
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'.runtime/art-direction/series01-sikh300'
def main():
    out=BASE/'replay-differences';out.mkdir(exist_ok=False);rows=[]
    for frame in (1,120,148,215,276,300,335,355,435,470):
        a=Image.open(BASE/f'final-01/frames/frame-{frame:04d}.png').convert('RGB')
        b=Image.open(BASE/f'ground-reopen-01/frame-{frame:04d}.png').convert('RGB')
        diff=abs(np.asarray(a).astype(int)-np.asarray(b).astype(int));mask=diff.max(axis=2)>1
        yy,xx=np.where(mask)
        row={'frame':frame,'maximum':int(diff.max()),'pixels_over_one':int(mask.sum()),'total_pixels':int(mask.size),'channels_over_one':int((diff>1).sum())}
        if len(xx):
            row['affected_bounds']=[int(xx.min()),int(yy.min()),int(xx.max()),int(yy.max())]
            y,x=np.unravel_index(np.argmax(diff.max(axis=2)),mask.shape)
            box=(max(0,int(x)-55),max(0,int(y)-55),min(a.width,int(x)+56),min(a.height,int(y)+56))
            panel=Image.new('RGB',(666,242),(24,24,24));draw=ImageDraw.Draw(panel)
            for i,(im,label) in enumerate(((a,'Final'),(b,'Reopened'),(Image.fromarray(np.uint8(np.clip(diff*32,0,255))),'Difference x32'))):
                panel.paste(im.crop(box).resize((222,222)),(i*222,20));draw.text((i*222+5,3),label,fill='white')
            panel.save(out/f'frame-{frame:04d}-maximum.png');row['maximum_crop']=list(box)
        rows.append(row)
    result={'strict_threshold_unchanged':1,'strict_result':'FAIL' if any(r['pixels_over_one'] for r in rows) else 'PASS','scope':'Tiny numerical discrepancies localized; no renderer stability promotion or perceptual inference from counts','frames':rows}
    (out/'localization.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
