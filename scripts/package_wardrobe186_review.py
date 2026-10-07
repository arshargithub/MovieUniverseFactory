"""Presentation-only encoding of directly reviewed native evidence."""
import base64
from io import BytesIO
import json
from pathlib import Path
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'.runtime/art-direction/series01-facebuilder-trial-01'
GALLERY=Path('/Users/adisharma/.codex/visualizations/2026/09/09/01a0878c-e7a2-75e0-873c-c31d97f879a1/pashtun-riding-arms-review.html')


def main():
    fresh=BASE/'wardrobe186-reopen06';record=json.loads((fresh/'result.json').read_text())
    if not record['protected_exact'] or max(record['surface_errors'].values())>2e-5:raise ValueError('Reopen not verified')
    if GALLERY.exists():raise ValueError('Preserve existing gallery')
    views=[(fresh/'front-265.png','Corrected front','Corrected riding arms · broad fill lighting'),
           (BASE/'wardrobe185-redressreview02/front-265.png','Previous front','Previous riding arms and lighting · retained comparison'),
           (BASE/'wardrobe186-delivery06/repaired-original-light-front.png','Same-light correction','Corrected arms with previous lighting · isolates the arm change'),
           (fresh/'left-265.png','Left','Corrected riding left profile'),
           (fresh/'right-265.png','Right','Corrected riding right profile'),
           (BASE/'wardrobe186-audit04/filled-rear-265.png','Back','Corrected riding back · two exterior wraps retained'),
           (fresh/'front-360.png','Late motion','Corrected arms at the end of the riding passage'),
           (BASE/'wardrobe185-seal02/neutral-master-front.png','Standing','Preserved standing master · unchanged accepted proportions')]
    rows=[]
    for path,short,label in views:
        with Image.open(path) as im:
            im=im.convert('RGB');stream=BytesIO();im.save(stream,'JPEG',quality=88,optimize=True)
        rows.append({'short':short,'label':label,'image':'data:image/jpeg;base64,'+base64.b64encode(stream.getvalue()).decode()})
    template=(ROOT/'scripts/templates/wardrobe185-review.html').read_text().replace('pashtun-doublewrap-review','pashtun-riding186-review')
    content=template.replace('/* REVIEW_DATA */[]',json.dumps(rows))
    if len(content.encode())>970000:raise ValueError('Gallery too large')
    GALLERY.write_text(content)
    print(json.dumps({'path':str(GALLERY),'bytes':len(content.encode()),'views':len(rows)}))


if __name__=='__main__':main()
