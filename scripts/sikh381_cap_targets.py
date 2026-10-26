"""Generate exact data-only boundary-supported targets from frozen source cache."""
import argparse,json,time
from pathlib import Path
import numpy as np
from movie_factory.horse_cap381 import FrontCap
from movie_factory import production_knowledge as pk
p=argparse.ArgumentParser();p.add_argument('--cycle',type=int,required=True);p.add_argument('--relief',type=float,default=.045);a=p.parse_args();assert 155<=a.cycle<=156 and 0<=a.relief<=.08
r=Path(__file__).resolve().parents[1];dest=r/f'.runtime/art-direction/sikh381-targets/c{a.cycle}.npz';assert not dest.exists();dest.parent.mkdir(parents=True,exist_ok=True)
sp='.runtime/factory-native/sikh376-appearance-c136-repair/horse-cache376.npz';gp='.runtime/factory-native/sikh374-appearance-c124-inspect/horse-form374.npz';q=np.load(r/sp);g=np.load(r/gp);solver=FrontCap(q['rest'],g['edges'],g['weights'],g['group_names'],relief=a.relief);start=time.monotonic();target=np.array([solver.fit(v) for v in q['source']],dtype=np.float32);assert np.array_equal(target[:,solver.fixed],q['source'][:,solver.fixed]);np.savez_compressed(dest,source=q['source'],target=target,rest=q['rest'],mask=solver.mask,times=q['times'])
report=dict(method='Boundary-supported biharmonic3D front cap plus smooth paired muscle relief; no preservation of old interior bulge coordinates',source=dict(path=sp,sha256=pk.file_hash(r/sp)),geometry=dict(path=gp,sha256=pk.file_hash(r/gp)),generator=pk.file_hash(Path(__file__)),solver=pk.file_hash(r/'src/movie_factory/horse_cap381.py'),vertices=len(solver.ids),relief=a.relief,maximum_delta=float(np.linalg.norm(target-q['source'],axis=2).max()),outside_exact=True,seconds=time.monotonic()-start,data=dict(path=str(dest.relative_to(r)),sha256=pk.file_hash(dest)),artistic_pass=False)
(dest.with_suffix('.json')).write_text(json.dumps(report,indent=2)+'\n');print(report)
