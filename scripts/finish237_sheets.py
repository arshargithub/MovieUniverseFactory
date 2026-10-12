"""Contact sheets from already rendered native review frames; no image edits."""
import json,sys
from pathlib import Path
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'.runtime/art-direction/series01-finish237'
OPS={'opening03-full','route04-full','edit01'}
def main():
    if len(sys.argv)!=2 or sys.argv[1] not in OPS:raise ValueError('Closed contact-sheet operation')
    op=sys.argv[1];src=BASE/op;out=BASE/'sheets'/op;out.mkdir(parents=True,exist_ok=True)
    paths=sorted((src/'frames' if op=='edit01' else src).glob('frame-*.png'))
    completed=[]
    for offset in range(0,len(paths),24):
        group=paths[offset:offset+24]
        # Partial tail may still be rendering. Never silently freeze it as a
        # completed batch; write only full groups or a completed source tail.
        if len(group)<24 and not (src/'result.json').exists() and op!='edit01':continue
        dest=out/f"sheet-{int(group[0].stem.split('-')[-1]):04d}.jpg"
        if dest.exists():continue
        canvas=Image.new('RGB',(6*216,4*408),(245,242,230));draw=ImageDraw.Draw(canvas)
        for j,p in enumerate(group):
            im=Image.open(p).convert('RGB');im.thumbnail((216,384));x=(j%6)*216;y=(j//6)*408
            canvas.paste(im,(x,y));index=int(p.stem.split('-')[-1]);draw.text((x+5,y+387),f'{index} | {index/24:.3f}s',fill=(20,20,20))
        canvas.save(dest,quality=92);completed.append(str(dest))
    print(json.dumps(completed))
if __name__=='__main__':main()
