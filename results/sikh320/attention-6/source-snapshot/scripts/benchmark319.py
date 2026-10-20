"""Measured bounded worker selection, not render or artistic qualification."""
import json,re,sys
import numpy as np
from PIL import Image
from movie_factory.production_knowledge import file_hash
from sikh319 import BASE,ROOT,source_for
v=int(sys.argv[1]);assert 1<=v<=32
result={}
serial_only='--serial-only' in sys.argv
for kind in (('benchserial',) if serial_only else ('benchserial','benchpair')):
    folder=BASE/f'{kind}-{v:02d}';jobs=json.loads((folder/'processes.json').read_text())
    rss=[]
    for p in (folder/'chunks').glob('*/worker.log'):
        m=re.search(r'(\d+)\s+maximum resident set size',p.read_text())
        if not m:raise ValueError('Missing measured memory receipt')
        rss.append(int(m.group(1)))
    assert len(jobs)==len(rss)==2 and all(j['code']==0 for j in jobs)
    result[kind]={'wall_seconds':max(j['end_epoch'] for j in jobs)-min(j['start_epoch'] for j in jobs),
                  'peak_worker_rss_bytes':max(rss),'summed_worker_peak_bytes':sum(rss)}
if serial_only:
    prior=ROOT/'results/sikh319/render-benchmark-16.json'
    previous=json.loads(prior.read_text())
    assert previous['workers']==1
    assert result['benchserial']['peak_worker_rss_bytes']<8*1024**3
    result.update(status='PASS',workers=1,native_sha256=file_hash(source_for('movie',v)),
                  conservative_prior={'path':str(prior.relative_to(ROOT)),'sha256':file_hash(prior)},
                  limits='Current twelve-frame serial measurement only. Prior candidate16 rejected concurrency; no parallel speedup or memory claim for this changed native.')
    p=ROOT/f'results/sikh319/render-benchmark-{v}.json'
    assert not p.exists();p.write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
    raise SystemExit(0)
comparisons=[]
for a in sorted((BASE/f'benchserial-{v:02d}/frames').glob('*.png')):
    b=BASE/f'benchpair-{v:02d}/frames'/a.name
    x=np.asarray(Image.open(a)).astype(np.int16);y=np.asarray(Image.open(b)).astype(np.int16)
    comparisons.append({'frame':a.name,'max_channel_difference':int(np.max(abs(x-y)))})
assert len(comparisons)==12
gain=1-result['benchpair']['wall_seconds']/result['benchserial']['wall_seconds']
safe=result['benchpair']['summed_worker_peak_bytes']<8*1024**3 and all(c['max_channel_difference']<=1 for c in comparisons)
result.update(status='PASS',workers=2 if safe and gain>.05 else 1,measured_wall_reduction=gain,
              native_sha256=file_hash(source_for('movie',v)),comparisons=comparisons,
              limits='Twelve-frame throughput/memory check, not a full-scene deadline, general concurrency qualification or AV pass.')
p=ROOT/f'results/sikh319/render-benchmark-{v}.json'
assert not p.exists();p.write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
