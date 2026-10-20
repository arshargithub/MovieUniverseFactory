"""Strict same-frame fresh-process comparison, separate from Director AV."""
import json
import sys
import numpy as np
from PIL import Image
from movie_factory.production_knowledge import file_hash
from sikh319 import ROOT,BASE
v=int(sys.argv[1]);assert 1<=v<=32
rows=[]
for f in (80,283,333,350,380,480):
    a=BASE/f'movie-{v:02d}/frames/frame-{f:04d}.png'
    b=BASE/f'reopen-{v:02d}/frames/frame-{f:04d}.png'
    x=np.asarray(Image.open(a)).astype(np.int16)
    y=np.asarray(Image.open(b)).astype(np.int16)
    assert x.shape==y.shape==(1280,720,4)
    delta=abs(x-y)
    rows.append({'frame':f,'maximum_channel_difference':int(delta.max()),
                 'different_channels':int(np.count_nonzero(delta)),
                 'original_sha256':file_hash(a),'reopen_sha256':file_hash(b)})
result={'status':'PASS' if all(r['maximum_channel_difference']<=1 for r in rows) else 'FAIL',
        'threshold':1,'channels':'RGBA 8bit','controls':rows,
        'limit':'Six exact-source/frame controls only; no general renderer qualification or artistic acceptance.'}
p=ROOT/f'results/sikh319/reopen-{v}/comparison.json'
assert not p.exists();p.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
