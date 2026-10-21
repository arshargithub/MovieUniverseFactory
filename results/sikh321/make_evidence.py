"""Local audit only: label existing frames; no scene edits or external calls."""
import hashlib
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / '.runtime/art-direction/series01-sikh321'
FONT = ImageFont.truetype('/System/Library/Fonts/Menlo.ttc', 16)

def sheet(rows, path, width=384, height=240, cols=4):
    canvas = Image.new('RGB', (cols*width, ((len(rows)+cols-1)//cols)*height), '#202020')
    d = ImageDraw.Draw(canvas)
    for i, (source, label, crop) in enumerate(rows):
        im = Image.open(source).convert('RGB')
        if crop: im = im.crop(crop)
        im.thumbnail((width, height-30))
        x, y = (i % cols)*width, (i//cols)*height
        canvas.paste(im, (x+(width-im.width)//2,y))
        d.text((x+5,y+height-25), label, font=FONT, fill='white')
    canvas.save(path)

refs=sorted((BASE/'reference').glob('sample-*.png'))
for start in range(0,len(refs),16):
    rows=[(p,f'Reference ~{14+(start+i)/10:.1f}s',None) for i,p in enumerate(refs[start:start+16])]
    sheet(rows,BASE/'comparisons'/f'reference-{start//16+1}.jpg')
frames=[276,286,298,305,310,315,321,326,332,338,344,348,350,353,355,356]
rows=[(ROOT/f'.runtime/art-direction/series01-sikh320/motion-10/frames/frame-{f:04d}.png',f'Candidate f{f} {(f-252)/24:.3f}s',(80,320,620,1100)) for f in frames]
sheet(rows, BASE/'comparisons'/'candidate-phases.jpg',360,470)
rows=[(ROOT/'.runtime/art-direction/series01-sikh320/motion-10/frames/frame-0298.png','Leader f298',(275,430,490,850)),
      (ROOT/'.runtime/art-direction/series01-sikh320/motion-10/frames/frame-0321.png','Leader f321',(275,420,535,850)),
      (ROOT/'.runtime/art-direction/series01-sikh320/pashtun-floor.png','Accepted Pashtun',(480,710,800,1135))]
sheet(rows,BASE/'comparisons'/'appearance.jpg',430,650,3)
rows=[]
for sample,frame,phase in [(20,298,'Gather'),(25,310,'Drive begins'),(29,318,'Lift'),(34,326,'Crest'),(42,344,'Descent'),(44,350,'Contact/recovery')]:
    rows.append((refs[sample-1],f'Ref ~{14+(sample-1)/10:.1f}s {phase}',None))
    rows.append((ROOT/f'.runtime/art-direction/series01-sikh320/motion-10/frames/frame-{frame:04d}.png',f'f{frame} {phase}',(35,350,650,1080)))
sheet(rows,BASE/'comparisons'/'phase-comparison.jpg',470,390,2)
inputs=[ROOT/'.runtime/art-direction/series01-sikh256/references/reference-b.mov',ROOT/'.runtime/art-direction/series01-sikh320/delivery-10/nihang-crowd-review.mp4']
manifest={'purpose':'Rejected candidate audit only; not new production media', 'reference_samples':'ffmpeg fps=10 over source 14-19s; nominal labels within 0.1s, not exact event detection', 'reference_crop':[0,338,576,308], 'candidate_times':'(source_frame-252)/24 relative to isolated clip', 'inputs':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}, 'sheets':[str(p.relative_to(ROOT)) for p in sorted((BASE/'comparisons').glob('*.jpg'))]}
(ROOT/'results/sikh321/evidence.json').write_text(json.dumps(manifest,indent=2)+'\n')
