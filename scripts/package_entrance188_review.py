"""Compact carousel of verified native entrance evidence; no appearance edits."""
import base64
from io import BytesIO
import json
from pathlib import Path
from PIL import Image

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'.runtime/art-direction/series01-facebuilder-trial-01'
GALLERY=Path('/Users/adisharma/.codex/visualizations/2026/09/09/01a0878c-e7a2-75e0-873c-c31d97f879a1/horse-and-rider-entrance188.html')


def main():
    review=json.loads((BASE/'entrance188-operating/visual-review.json').read_text())
    if review['scoped_internal_visual_gate']!='PASS':raise ValueError('No visual exit')
    fresh=BASE/'entrance188-reopen07'
    record=json.loads((fresh/'result.json').read_text())
    if record['frames']!=[217,265,309,360] or not record['protected_sources_unchanged']:
        raise ValueError('Incomplete reopen')
    if GALLERY.exists():raise ValueError('Preserve previous presentation')
    views=[(360,'Close reveal'),(309,'Lateral gallop'),(265,'Descending camera'),(217,'High opening')]
    rows=[]
    for frame,label in views:
        with Image.open(fresh/('frame-%04d.png'%frame)) as im:
            stream=BytesIO();im.convert('RGB').save(stream,'JPEG',quality=90,optimize=True)
        rows.append({'short':label,'label':label+' · native look candidate · Director acceptance pending',
                     'image':'data:image/jpeg;base64,'+base64.b64encode(stream.getvalue()).decode()})
    template=(ROOT/'scripts/templates/wardrobe185-review.html').read_text().replace('pashtun-doublewrap-review','horse-rider-entrance188')
    text=template.replace('/* REVIEW_DATA */[]',json.dumps(rows))
    if len(text.encode())>970000:raise ValueError('Oversized presentation')
    GALLERY.write_text(text)
    print(json.dumps({'path':str(GALLERY),'bytes':len(text.encode()),'views':len(rows)}))


if __name__=='__main__':main()
