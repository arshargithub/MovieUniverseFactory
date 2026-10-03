"""Package only an internally reviewed exchange171 candidate, no API calls."""
import base64
from io import BytesIO
import json
from pathlib import Path
from PIL import Image,ImageChops
from package_wardrobe_fit_review import check_review

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'.runtime/art-direction/series01-facebuilder-trial-01'
GALLERY=ROOT/'.runtime/reviews/pashtun-wardrobe-correction.html'
CRITERIA={'protected_foundation','full_scarf','sleeves','flared_hem','rugged_fabric','skin_continuity','posed_interfaces','adjacent_regressions','whole_static_candidate'}
ROWS=[
 ('standing-front','Front','Corrected wardrobe · standing front'),
 ('upper-front','Front close-up','Neckline, skin, open scarf and sleeve joins · front'),
 ('upper-left','Left ¾','Skin, scarf and sleeve joins · left ¾'),
 ('upper-right','Right ¾','Skin, scarf and sleeve joins · right ¾'),
 ('standing-side','Standing side','Whole silhouette and flared hem · standing side'),
 ('standing-rear','Back','Full rear scarf, harness and hem · standing back'),
 ('mounted-side','Riding side','Static mounted fit · neutral diagnostic horse, not final motion'),
 ('mounted-opposite-side','Other riding side','Static mounted fit · opposite side'),
 ('mounted-front-quarter','Riding ¾','Static mounted fit · front ¾'),
 ('mounted-rear-quarter','Riding rear ¾','Static mounted fit · rear ¾'),
 ('mounted-sleeve-interface','Riding close-up','Both sleeve joins, neckline, belt and hem · left ¾'),
 ('mounted-sleeve-opposite','Other riding close-up','Both sleeve joins, neckline, belt and hem · right ¾'),
 ('mounted-partial-lean','Partial lean','Prescribed partial lean · not continuous animation qualification'),
]

def main():
 selected=BASE/'wardrobe171-seal01';card=BASE/'wardrobe171-operating';preview=BASE/'wardrobe171-preview09';fresh=BASE/'wardrobe171-verify01'
 review=json.loads((card/'visual-review.json').read_text());check_review(review,selected,'wardrobe171-seal01',CRITERIA)
 result=json.loads((selected/'result.json').read_text());verified=json.loads((fresh/'result.json').read_text())
 assert all(result[k] for k in ('protected_data_exact','body_basis_exact','source_unchanged','cloth_thickness_after_fitting'))
 assert all(verified[k] for k in ('reopened','protected_signatures_exact','body_basis_exact','static_tail_curve_data_exact','source_unchanged'))
 assert all(v is not None and v<verified['surface_tolerance'] for v in verified['evaluated_local_surface_max_errors'].values())
 compared=[];other_views=[]
 for name,_,_ in ROWS:
  if not (preview/(name+'.png')).is_file():
   other_views.append(name)
   continue
  delta=ImageChops.difference(Image.open(selected/(name+'.png')).convert('RGB'),Image.open(preview/(name+'.png')).convert('RGB'))
  assert delta.getbbox() is None,name
  compared.append(name)
 assert len(compared)==4
 reopened={}
 for path in fresh.glob('reopened-*.png'):
  delta=ImageChops.difference(Image.open(path).convert('RGB'),Image.open(selected/path.name.removeprefix('reopened-')).convert('RGB'))
  maximum=max(v[1] for v in delta.getextrema());assert maximum<=4,path.name
  reopened[path.name]=maximum
 assert len(reopened)==2
 frames=[(selected/(name+'.png'),short,label) for name,short,label in ROWS]
 refs=ROOT/'.runtime/art-direction/series01-pashtun-baseline-v01'
 frames.extend([(refs/'frontal-v02-individualized.png','Illustrated front','Approved illustrated art direction · accepted native differences retained'),(refs/'portrait-v07-individualized.png','Illustrated portrait','Approved illustrated identity and costume vocabulary · not literal geometry')])
 data=[]
 for path,short,label in frames:
  im=Image.open(path).convert('RGB');im.thumbnail((920,760));stream=BytesIO();im.save(stream,'JPEG',quality=84,optimize=True)
  data.append({'short':short,'label':label,'image':'data:image/jpeg;base64,'+base64.b64encode(stream.getvalue()).decode()})
 html=GALLERY.read_text();token='/* REVIEW_DATA */[]';assert token in html
 html=html.replace(token,json.dumps(data));assert len(html.encode())<1_000_000
 GALLERY.write_text(html)
 (card/'pixel-comparison.json').write_text(json.dumps({'selected_vs_inspected_preview_exact':compared,'selected_other_views_manually_reviewed':other_views,'fresh_open_max_channel_differences':reopened,'limits':'Reproducibility, not Director appearance acceptance; only four targeted previews are claimed identical'},indent=2)+'\n')
 print(json.dumps({'gallery_bytes':len(html.encode()),'views':len(data),'compared_views':len(compared),'reopened_views':len(reopened)}))

if __name__=='__main__':main()
