"""Matched existing206/207 frame layout; no synthesized or retouched pixels."""
from pathlib import Path
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'.runtime/art-direction/series01-facebuilder-trial-01'
OUT=ROOT/'.runtime/art-direction/series01-entrance207/qa'
def main():
 for kind,fs,part in [('opening',(313,325,337),'opening03'),('ending',(583,595,607),'route04')]:
  target=OUT/(kind+'-matched206207.png')
  if target.exists():continue
  pairs=[(ROOT/f'.runtime/art-direction/series01-entrance206/director-preview/frame-{f-217:04d}.png',BASE/f'entrance207-{part}/frame-{f-217:04d}.png') for f in fs]
  if not all(p.exists() for pair in pairs for p in pair):continue
  result=Image.new('RGB',(432*3,440*2),(238,238,238));draw=ImageDraw.Draw(result)
  for j,pair in enumerate(pairs):
   for i,path in enumerate(pair):
    with Image.open(path) as im:crop=im.convert('RGB').crop((0,30,432,430))
    result.paste(crop,(j*432,i*440));draw.text((j*432+8,i*440+411),f'{206+i} native {fs[j]} - identical camera/clock',fill=(15,15,15))
  result.save(target)
if __name__=='__main__':main()
