"""Encode the selected, freshly reopened native views for Director review.

Presentation-only JPEG resizing; never generative editing of native evidence.
"""
import base64
from io import BytesIO
import json
from pathlib import Path
from PIL import Image,ImageChops

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'.runtime/art-direction/series01-facebuilder-trial-01'
GALLERY=Path('/Users/adisharma/.codex/visualizations/2026/09/09/01a0878c-e7a2-75e0-873c-c31d97f879a1/pashtun-double-wrap-moving-review.html')


def main():
    selected=BASE/'wardrobe185-seal01';fresh=BASE/'wardrobe185-verify01'
    verified=json.loads((fresh/'result.json').read_text())
    if not all(verified[k] for k in ('packed_images','local_cache_paths','protected_exact')):raise ValueError('Incomplete native verification')
    for key in ('moving_surface_errors','neutral_surface_errors'):
        if any(v is None or v>2e-5 for v in verified[key].values()):raise ValueError('Native verification mismatch')
    if GALLERY.exists():raise ValueError('Preserve prior review gallery')
    rows=[]
    for name,label in (('front','Front'),('left','Left profile'),('right','Right profile'),('rear','Back')):
        rows.append((selected/('neutral-master-'+name+'.png'),label,'Standing double wrap · '+label+' · Director acceptance pending'))
    rows.append((selected/'neutral-whole-front.png','Whole character','Standing whole character · accepted face and body retained'))
    current=BASE/'wardrobe185-redressreview02'
    for name,label in (('front','Riding front'),('left','Riding left'),('right','Riding right'),('rear','Riding back')):
        rows.append((current/(name+'-265.png'),label,'Required gallop frame265 · '+label+' · free cloth and declared concealed supports'))
    rows.append((fresh/'alternate-camera-325.png','Alternate camera','Fresh-open camera reuse · same performance and cloth cache'))
    refs=ROOT/'.runtime/art-direction/series01-pashtun-baseline-v01'
    rows.extend([(refs/'frontal-v02-individualized.png','Illustrated front','Approved illustrated art direction · accepted native differences retained'),
        (refs/'portrait-v07-individualized.png','Illustrated portrait','Approved illustrated portrait · folds are not a literal reconstruction target')])
    template=(ROOT/'scripts/templates/wardrobe185-review.html').read_text()
    if template.count('/* REVIEW_DATA */[]')!=1:raise ValueError('Unexpected gallery template')
    for quality in (86,82,78,74):
        data=[]
        for path,short,label in rows:
            with Image.open(path) as source:
                im=source.convert('RGB');im.thumbnail((920,820));stream=BytesIO();im.save(stream,'JPEG',quality=quality,optimize=True)
            data.append({'short':short,'label':label,'image':'data:image/jpeg;base64,'+base64.b64encode(stream.getvalue()).decode()})
        content=template.replace('/* REVIEW_DATA */[]',json.dumps(data))
        if len(content.encode())<970000:break
    if len(content.encode())>=1000000:raise ValueError('Gallery exceeds host limit')
    delta=ImageChops.difference(Image.open(selected/'neutral-master-front.png').convert('RGB'),Image.open(fresh/'reopened-neutral-front.png').convert('RGB'))
    comparison=max(v[1] for v in delta.getextrema())
    if comparison>4:raise ValueError('Fresh-open appearance differs; inspect before handoff')
    GALLERY.write_text(content)
    record={'gallery':str(GALLERY),'gallery_bytes':len(content.encode()),'views':len(data),
        'jpeg_quality':quality,'reopened_front_max_channel_difference':comparison,
        'scope':'Presentation encoding only; original PNGs and native retained; Director appearance acceptance pending'}
    (BASE/'wardrobe185-operating/gallery-receipt.json').write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps(record))


if __name__=='__main__':main()
