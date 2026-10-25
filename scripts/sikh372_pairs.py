"""Pair actual early poses with bound reference frames; no native or art verdict."""
import json,sys
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from movie_factory import production_knowledge as pk
r=Path(__file__).resolve().parents[1];cy=int(sys.argv[1]);o=r/'results/sikh372';out=r/f'.runtime/art-direction/sikh372-review-c{cy}';out.mkdir(parents=True,exist_ok=True)
def bind(p):return dict(path=str(p.relative_to(r)),sha256=pk.file_hash(p))
def images(step):
 run=json.loads((o/f'motion-c{cy}-{step}-run.json').read_text());assert run['status']=='RETURNED';mf=r/run['artifacts']['frames']['path'];assert pk.file_hash(mf)==run['artifacts']['frames']['sha256'];rows=json.loads(mf.read_text());result={}
 for x in rows:
  p=mf.parent/x['file'];assert pk.file_hash(p)==x['sha256'];result[x['frame']]=p
 return result
side=images('early_side');oblique=images('early_oblique');font=ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc',18);records=[]
for frame,refno in [(315,5),(319,10),(323,15),(333,27)]:
 ref=r/f'.runtime/art-direction/sikh371-reference/ref-{refno:03d}.png';sheet=Image.new('RGB',(1440,510),(17,17,17));d=ImageDraw.Draw(sheet)
 for i,(p,label) in enumerate([(ref,f'Reference {(16.5+(refno-1)/30):.3f}s'),(side[frame],f'Current side {frame}'),(oblique[frame],f'Current oblique {frame}')]):
  im=Image.open(p).convert('RGB');im.thumbnail((480,480));sheet.paste(im,(i*480+(480-im.width)//2,30+(480-im.height)//2));d.text((i*480+10,6),label,font=font,fill='white')
 target=out/f'early-pair-{frame:04d}.jpg';sheet.save(target,quality=95);records.append(dict(frame=frame,reference=bind(ref),side=bind(side[frame]),oblique=bind(oblique[frame]),pair=bind(target)))
p=o/f'early-pairs{cy}.json';assert not p.exists();p.write_text(json.dumps(dict(rows=records,scope='Actualunmirrored reference/posedviews; staticearlyproof, notfullspeedorartisticapproval.'),indent=2)+'\n');print(out)
