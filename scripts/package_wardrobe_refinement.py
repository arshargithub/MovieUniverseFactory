"""Encode one manually reviewed wardrobe170 candidate and matched references."""
import base64
from io import BytesIO
import json
from pathlib import Path
from PIL import Image, ImageChops
from package_wardrobe_fit_review import check_review

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'.runtime/art-direction/series01-facebuilder-trial-01'
GALLERY=Path('/Users/adisharma/.codex/visualizations/2026/09/09/01a0878c-e7a2-75e0-873c-c31d97f879a1/pashtun-wardrobe-tailored-review.html')
CRITERIA={'protected_foundation','tailored_silhouette','costume_character','open_scarf_fit','single_tail_assembly','mounted_and_partial_regressions'}


def main():
    selected=BASE/'wardrobe170-seal03';receipt=BASE/'wardrobe170-operating'
    review=json.loads((receipt/'visual-review.json').read_text())
    check_review(review,selected,'wardrobe170-seal03',CRITERIA)
    result=json.loads((selected/'result.json').read_text())
    fresh=json.loads((BASE/'wardrobe170-verify03/result.json').read_text())
    assert result['protected_data_exact'] and result['body_basis_exact'] and result['source_pins_unchanged']
    assert fresh['reopened'] and fresh['protected_signatures_exact'] and fresh['body_basis_exact'] and fresh['static_tail_curve_data_exact']
    assert all(v is not None and v<fresh['surface_tolerance'] for v in fresh['evaluated_local_surface_max_errors'].values())
    compared={}
    for path in (BASE/'wardrobe170-verify03').glob('reopened-*.png'):
        original=selected/path.name.removeprefix('reopened-')
        delta=ImageChops.difference(Image.open(path).convert('RGB'),Image.open(original).convert('RGB'))
        maximum=max(v[1] for v in delta.getextrema());assert maximum<=4
        compared[path.name]=maximum
    assert len(compared)==2
    rows=[('standing-front','New front','Tailored standing front · accepted anatomy unchanged'),
          ('standing-side','New side','Tailored standing side'),('standing-rear','New back','Tailored rear · open scarf and shoulder harness'),
          ('head-scarf-quarter','Scarf/hair','Fitted open indigo scarf · approved forehead and hair retained'),
          ('mounted-side','Riding side','Static riding fit · not gait or dynamic-contact qualification'),
          ('mounted-opposite-side','Other riding side','Static riding fit · opposite side'),
          ('mounted-front-quarter','Riding ¾','Static mounted front ¾'),('mounted-rear-quarter','Riding rear ¾','Static mounted rear ¾'),
          ('tail-rear-quarter','Tail join','Single refitted static tail · source scene unchanged'),
          ('mounted-partial-lean','Partial lean','Static partial riding lean · not continuous-motion proof')]
    frames=[(selected/(name+'.png'),short,label) for name,short,label in rows]
    previous=BASE/'wardrobe169-seal01'
    for name,short in [('standing-front','Before front'),('standing-side','Before side'),('standing-rear','Before back'),('mounted-side','Before riding')]:
        frames.append((previous/(name+'.png'),short,'Prior coarse costume · matched camera/light · not accepted costume'))
    refs=ROOT/'.runtime/art-direction/series01-pashtun-baseline-v01'
    frames.extend([(refs/'frontal-v02-individualized.png','Illustrated front','Approved illustrated identity/art direction · not literal costume geometry'),
                   (refs/'portrait-v07-individualized.png','Illustrated portrait','Approved illustrated portrait · accepted native differences protected')])
    data=[]
    for path,short,label in frames:
        picture=Image.open(path).convert('RGB');picture.thumbnail((920,760))
        stream=BytesIO();picture.save(stream,'JPEG',quality=84,optimize=True)
        data.append({'short':short,'label':label,'image':'data:image/jpeg;base64,'+base64.b64encode(stream.getvalue()).decode()})
    template=GALLERY.read_text();marker='/* REVIEW_DATA */[]';assert marker in template
    text=template.replace(marker,json.dumps(data));assert len(text.encode())<1_000_000
    GALLERY.write_text(text)
    (receipt/'pixel-comparison.json').write_text(json.dumps({'fresh_open_max_channel_differences':compared,'limits':'Native/render replay, not creative approval'},indent=2)+'\n')
    print(json.dumps({'views':len(data),'gallery_bytes':len(text.encode()),'reopened_max_channel_differences':compared}))


if __name__=='__main__':main()
