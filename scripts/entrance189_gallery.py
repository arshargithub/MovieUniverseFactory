"""Populate the literal review fragment with compact local preview images."""
import base64
import io
import json
from pathlib import Path
from PIL import Image,ImageOps

ROOT=Path(__file__).resolve().parents[1]
ART=ROOT/'.runtime/art-direction'
BASE=ART/'series01-facebuilder-trial-01'
TARGET=Path('/Users/adisharma/.codex/visualizations/2026/09/09/01a0878c-e7a2-75e0-873c-c31d97f879a1/entrance189-review.html')


def main():
    specs=[
        ('Close reveal',BASE/'entrance189-decision-overview19/large-0360.png','Current native close reveal - internal review complete, Director acceptance pending'),
        ('Horse and trail',BASE/'entrance189-decision-overview19/large-0309.png','Current side view - fuller groom, dust cloud and terrain'),
        ('High opening',BASE/'entrance189-motion16/frame-0217.png','Current overhead opening - native preview resolution'),
        ('Attention',BASE/'entrance189-decision-motion20/frame-0336.png','Current decision-shot coverage - unchanged acting, closer camera'),
        ('Illustrated direction',ART/'series01-entrances-v04/C-illustrated-landscape.png','Approved illustrated-C direction - style reference, not native footage')]
    for name in ('entrance189-motion16','entrance189-decision-motion20'):
        gate=json.loads((BASE/name/'internal-review.json').read_text())
        result=json.loads((BASE/name/'result.json').read_text())
        if (gate.get('status')!='PROCEED_TO_EDIT' or not result.get('source_sha256') or
            gate.get('source_sha256')!=result['source_sha256']):raise ValueError('Source-bound visual review not complete')
    views=[]
    for name,path,description in specs:
        with Image.open(path) as im:
            thumb=ImageOps.contain(im.convert('RGB'),(960,960));stream=io.BytesIO();thumb.save(stream,format='JPEG',quality=79,optimize=True)
        views.append({'name':name,'description':description,'image':'data:image/jpeg;base64,'+base64.b64encode(stream.getvalue()).decode('ascii')})
    template=Path(__file__).with_suffix('.html').read_text()
    content=template.replace('__VIEWS__',json.dumps(views,separators=(',',':')))
    if len(content.encode())>=1000000 or '__VIEWS__' in content:raise ValueError('Fragment admission failed')
    if TARGET.exists():raise ValueError('Preserve previous review')
    TARGET.write_text(content)
    print(json.dumps({'path':str(TARGET),'bytes':len(content.encode()),'views':len(views)}))


if __name__=='__main__':main()
