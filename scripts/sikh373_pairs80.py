"""Actual phase-aligned reference/side/oblique display, no artistic verdict."""
import json
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from movie_factory import production_knowledge as pk
r=Path(__file__).resolve().parents[1];o=r/'results/sikh373';out=r/'.runtime/art-direction/sikh373-review-c80';out.mkdir(exist_ok=True,parents=True)
def bind(p):return dict(path=str(p.relative_to(r)),sha256=pk.file_hash(p))
def frames(step):
 run=json.loads((o/f'motion-c80-{step}-run.json').read_text());assert run['status']=='RETURNED';mf=r/run['artifacts']['frames']['path'];assert pk.file_hash(mf)==run['artifacts']['frames']['sha256'];res={}
 for row in json.loads(mf.read_text()):
  p=mf.parent/row['file'];assert pk.file_hash(p)==row['sha256'];res[row['frame']]=p
 return res
side=frames('early_side');oblique=frames('early_oblique');records=[];font=ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc',17)
for f,n,phase in [(335,23,'release'),(339,25,'reaching descent'),(343,32,'forehoof support'),(346,35,'absorption')]:
 ref=r/f'.runtime/art-direction/sikh373-reference/ref-{n:03d}.png';sheet=Image.new('RGB',(1440,525),(15,15,15));d=ImageDraw.Draw(sheet)
 for i,(p,label) in enumerate([(ref,f'Reference {17.2+(n-1)/30:.3f}s'),(side[f],f'Current side {f}'),(oblique[f],f'Current oblique {f}')]):
  im=Image.open(p).convert('RGB')
  if i==0:im=im.crop((55,250,576,810))
  im.thumbnail((480,480));sheet.paste(im,(i*480+(480-im.width)//2,35+(480-im.height)//2));d.text((i*480+8,8),label+' | '+phase,font=font,fill='white')
 dest=out/f'early-pair-{f:04d}.jpg';sheet.save(dest,quality=94);records.append(dict(frame=f,phase=phase,reference=bind(ref),side=bind(side[f]),oblique=bind(oblique[f]),pair=bind(dest)))
(o/'early-pairs80.json').write_text(json.dumps(dict(rows=records,scope='Unmirroredactualphasecomparison, cropdisplayonly; originalreferenceboundseparately. No directmotion orartisticapproval.'),indent=2)+'\n')
print(out)
