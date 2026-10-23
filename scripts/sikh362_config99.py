"""Persist the reviewed99 construction proof; no worker or controller mutation."""
import json
from pathlib import Path
r=Path(__file__).resolve().parents[1];p=r/'results/sikh362'
cfg=json.loads((p/'appearance-c98.json').read_text())
cfg.update(parent='.runtime/factory-native/sikh362-appearance-c98-save/scene.blend',cause='98 seam is visibly fixed; whole look fails pointed stacked crown and smooth surface. Source crop linear-domain test demonstrates59.65percent upper clipping, so new contrast is measured rather than more noise.',method='Preserve98 seam,24 rein paths, roots, identity/anatomy and all action keys. Apply the fixed reviewed finish362: common bounded monotone upper-crown rounding with fitted lower edge unchanged, rest-attached crossed textile relief, and exact old pigment-range correction to measured source domain. Keep palette and pose ownership; actual front/oblique and intended framing must reject residual shell, noise, smoothing or adjacent regression.',proof='Actions exact, fitted crown lower edge unchanged and no unknown cranial mesh or shape-key state. First actual front and intended frame proof must show credible rounded layered crown and perceptible rich material without dirt/tiling. Then both sides, front/reverse rest/crest/landing and whole horse/rider. No whole art or AV pass from tests.',scope='Same supporting leader and horse integrated appearance; no identity redesign, new assets, crowd, sound, spending or external operations.')
cfg['sources']+=['src/movie_factory/adapters/blender/nihang_finish362.py','tests/test_nihang362_finish.py','results/sikh362/HANDLER_REVIEW.md','results/sikh362/texture-control.json','results/sikh362/appearance-c98-production-review.json']
cfg['steps'][0]['recipe']['edits']=[dict(kind='mounted_finish362',target='mounted leader')]
# Early front and intended proof before expensive reverse/side completion.
order=['save','leader_face','production','leader_face_left','leader_face_right','leader_front','leader_reverse']
cfg['steps']=sorted(cfg['steps'],key=lambda x:order.index(x['id']))
dest=p/'appearance-c99.json';text=json.dumps(cfg,indent=2)+'\n'
if dest.exists():assert dest.read_text()==text
else:dest.write_text(text)
