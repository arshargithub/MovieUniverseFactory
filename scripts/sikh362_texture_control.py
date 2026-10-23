"""Read-only source-domain measurement; no rendered-appearance claim."""
import json,hashlib
from pathlib import Path
import numpy as np
from PIL import Image
r=Path(__file__).resolve().parents[1]
p=r/'.runtime/art-direction/series01-facebuilder-trial-01/bust-atlas-input-02/skin-authored.png'
a=np.asarray(Image.open(p).convert('RGB'),dtype=float)/255;h,w=a.shape[:2]
a=a[int(h*.76):int(h*.99),int(w*.01):int(w*.24)]
linear=np.where(a<=.04045,a/12.92,((a+.055)/1.055)**2.4)
# Cycles grayscale uses colour-management luminance. The exact box-projection
# interpolation still needs native validation; these are source pixel controls.
lum=linear@np.array([.2126,.7152,.0722])
report=dict(source=str(p.relative_to(r)),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),uv_crop=[.01,.01,.24,.24],linear_luminance_percentiles=dict(zip(['p0','p1','p5','p25','p50','p75','p95','p99','p100'],np.percentile(lum,[0,1,5,25,50,75,95,99,100]).tolist())),old_range=[.16,.34],old_upper_clipped_fraction=float(np.mean(lum>=.34)),proposed_range=[.295,.390],proposed_upper_clipped_fraction=float(np.mean(lum>=.390)),scope='Source-domain control only; not proof of Cycles sample distribution or actual visual texture quality.')
(r/'results/sikh362/texture-control.json').write_text(json.dumps(report,indent=2)+'\n')
print({k:report[k] for k in ['old_upper_clipped_fraction','proposed_upper_clipped_fraction']})
