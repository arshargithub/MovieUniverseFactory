"""Mechanically embed resized review copies of actual native renders."""
import base64,io,json
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'.runtime/art-direction/series01-facebuilder-trial-01'
OUT=Path('/Users/adisharma/.codex/visualizations/2026/09/09/01a0878c-e7a2-75e0-873c-c31d97f879a1/rider-treatment-200.html')

def main():
    paths={'before':{'close':BASE/'entrance198-motion04/frame-0360.png','side':BASE/'entrance198-motion04/frame-0349.png','grip':BASE/'entrance200-controls02/grip-L.png'},
           'after':{'close':BASE/'entrance200-motion18/frame-0360.png','side':BASE/'entrance200-motion18/frame-0349.png','grip':BASE/'entrance200-controls11/grip-L.png'}}
    images={}
    for version,views in paths.items():
        images[version]={}
        for view,p in views.items():
            with Image.open(p) as im:
                b=io.BytesIO();im.convert('RGB').save(b,format='JPEG',quality=90,optimize=True)
            images[version][view]='data:image/jpeg;base64,'+base64.b64encode(b.getvalue()).decode('ascii')
    text=Path(__file__).with_name('entrance200_review.template.html').read_text().replace('__IMAGES__',json.dumps(images))
    if len(text.encode())>=1_000_000:raise ValueError('Inline size exceeded')
    OUT.write_text(text);print(json.dumps({'path':str(OUT),'bytes':len(text.encode()),'images':6}))

if __name__=='__main__':main()
