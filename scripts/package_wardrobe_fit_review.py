"""Package a manually reviewed static candidate; never promote failed previews."""
import base64
from io import BytesIO
import json
from pathlib import Path

from PIL import Image, ImageChops

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'.runtime/art-direction/series01-facebuilder-trial-01'
GALLERY=Path('/Users/adisharma/.codex/visualizations/2026/09/09/01a0878c-e7a2-75e0-873c-c31d97f879a1/pashtun-wardrobe-fit-review.html')
CRITERIA={'protected_foundation','standing_costume','mounted_clearance','tack_registration','partial_lean','whole_static_candidate'}


def check_review(review, root, candidate='wardrobe169-seal01', criteria=CRITERIA):
    rows=review.get('criteria',[])
    if review.get('candidate')!=candidate or review.get('known_structural_blockers')!=[]:
        raise ValueError('Known blockers or wrong candidate stay internal')
    if len(rows)!=len(criteria) or {r.get('id') for r in rows}!=criteria:
        raise ValueError('Incomplete integrated static review')
    for row in rows:
        if row.get('status')!='PASS' or not row.get('images') or not row.get('observation'):
            raise ValueError('Unreviewed or failed criterion')
        for name in row['images']:
            path=root/name
            if Path(name).is_absolute() or path.is_symlink() or not path.is_file() or root.resolve() not in path.resolve().parents:
                raise ValueError('Invalid visual evidence')


def main():
    selected=BASE/'wardrobe169-seal01';card=BASE/'wardrobe169-operating'
    review=json.loads((card/'visual-review.json').read_text());check_review(review,selected)
    result=json.loads((selected/'result.json').read_text())
    fresh=json.loads((BASE/'wardrobe169-verify01/result.json').read_text())
    assert all(result[k] for k in ('protected_data_exact','body_local_geometry_exact','source_unchanged'))
    assert fresh['reopened'] and fresh['body_basis_exact'] and fresh['protected_signatures_exact']
    assert all(v is not None and v<fresh['surface_tolerance'] for v in fresh['evaluated_local_surface_max_errors'].values())
    compared=[];reframed=[]
    for path in selected.glob('*.png'):
        previous=BASE/'wardrobe169-preview38'/path.name
        assert previous.is_file()
        if path.name in {'mounted-side.png','mounted-opposite-side.png','mounted-partial-lean.png'}:
            reframed.append(path.name)
        else:
            assert ImageChops.difference(Image.open(path).convert('RGB'),Image.open(previous).convert('RGB')).getbbox() is None
            compared.append(path.name)
    assert len(compared)==7 and len(reframed)==3
    reopened={}
    for path in (BASE/'wardrobe169-verify01').glob('reopened-*.png'):
        original=selected/path.name.removeprefix('reopened-')
        delta=ImageChops.difference(Image.open(path).convert('RGB'),Image.open(original).convert('RGB'))
        maximum=max(v[1] for v in delta.getextrema());assert maximum<=4
        reopened[path.name]=maximum
    assert len(reopened)==2
    rows=[
        ('standing-front','Front','Proposed wardrobe · standing front'),
        ('standing-side','Standing side','Proposed wardrobe · standing side'),
        ('standing-rear','Back','Proposed wardrobe · rear and shoulder harness'),
        ('mounted-side','Riding side','Static mounted fit · diagnostic horse material, not final look'),
        ('mounted-opposite-side','Other riding side','Static mounted fit · opposite side'),
        ('mounted-front-quarter','Riding ¾','Static mounted fit · front ¾'),
        ('mounted-rear-quarter','Riding rear ¾','Static mounted fit · rear ¾'),
        ('mounted-partial-lean','Partial lean','Static partial lean · pose-specific contacts, not animation proof'),
        ('mounted-hands','Hands/reins','Static finger controls and reins · dynamic grasp not qualified'),
        ('mounted-boot-stirrup','Boot/stirrup','Closed boot and actual stirrup · provisional materials'),
    ]
    frames=[(selected/(name+'.png'),short,label) for name,short,label in rows]
    refs=ROOT/'.runtime/art-direction/series01-pashtun-baseline-v01'
    frames.extend([(refs/'frontal-v02-individualized.png','Illustrated front','Approved illustrated art direction · not literal costume geometry'),(refs/'portrait-v07-individualized.png','Illustrated side','Approved illustrated portrait · accepted native head differences retained')])
    data=[]
    for path,short,label in frames:
        im=Image.open(path).convert('RGB');im.thumbnail((920,760))
        stream=BytesIO();im.save(stream,'JPEG',quality=84,optimize=True)
        data.append({'short':short,'label':label,'image':'data:image/jpeg;base64,'+base64.b64encode(stream.getvalue()).decode()})
    text=GALLERY.read_text();token='/* REVIEW_DATA */[]'
    assert token in text
    text=text.replace(token,json.dumps(data))
    assert len(text.encode())<1_000_000
    GALLERY.write_text(text)
    (card/'pixel-comparison.json').write_text(json.dumps({'selected_vs_inspected_preview_exact':sorted(compared),'camera_only_reframed_and_manually_reviewed':sorted(reframed),'fresh_open_max_channel_differences':reopened,'limits':'Replay evidence only, not aesthetic acceptance'},indent=2)+'\n')
    print(json.dumps({'gallery_bytes':len(text.encode()),'views':len(data),'compared_views':len(compared),'reopened_views':len(reopened)}))


if __name__=='__main__':main()
