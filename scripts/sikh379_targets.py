"""Read frozen source arrays and author a bounded data-only target, not a blend."""
import argparse,time,json
from pathlib import Path
import numpy as np
from movie_factory.horse_shape379 import LocalForm,domain,body_cage
from movie_factory import production_knowledge as pk

p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--restore',type=float,default=.28);p.add_argument('--softness',type=float,default=.025);p.add_argument('--iterations',type=int,default=18);p.add_argument('--gather',type=float,default=0);p.add_argument('--body-cage',action='store_true');p.add_argument('--cage-blend',type=float,default=1);a=p.parse_args()
if not a.name.startswith('c') or not a.name[1:].isdigit() or not 0<=a.restore<=1 or not .001<=a.softness<=1 or not 1<=a.iterations<=40 or not 0<=a.gather<=1.2 or not 0<=a.cage_blend<=1:raise ValueError('TARGET379_CONFIG')
r=Path(__file__).resolve().parents[1];out=r/'.runtime/art-direction/sikh379-targets';out.mkdir(exist_ok=True,parents=True);dest=out/(a.name+'.npz')
if dest.exists():raise ValueError('TARGET379_PRESERVE_PRIOR')
source='.runtime/factory-native/sikh376-appearance-c136-repair/horse-cache376.npz';geometry='.runtime/factory-native/sikh374-appearance-c124-inspect/horse-form374.npz'
q=np.load(r/source,allow_pickle=False);g=np.load(r/geometry,allow_pickle=False);rest=q['rest'];mask,breast=domain(rest,g['weights'],g['group_names']);reference_rest=rest+(g['mesh']-rest)*(a.restore*mask[:,None])
from movie_factory.horse_shape379 import smooth
hw=6*breast*mask*smooth((rest[:,2]-1.04)/.14)*smooth((1.58-rest[:,2])/.16) if a.gather or a.body_cage else None
solver=LocalForm(reference_rest,g['edges'],mask,softness=a.softness,iterations=a.iterations,handle_weights=hw)
groups=list(g['group_names']);anchors=[]
body_weights=g['weights'][:,[groups.index(n) for n in ['DEF-spine.005','DEF-spine.006']]].sum(1)
for side in ('L','R'):
 arm=g['weights'][:,groups.index('DEF-upper_arm.'+side+'.001')];chest=g['weights'][:,groups.index('DEF-breast.'+side)]
 anchors.append((arm/arm.sum(),chest/chest.sum(),chest))
targets=[];start=time.monotonic();print('active',len(solver.active),flush=True)
for index,(t,posed) in enumerate(zip(q['times'],q['source'])):
    handles=posed.copy()
    if a.body_cage:
        handles=posed+a.cage_blend*(body_cage(rest,posed,reference_rest,body_weights)-posed)
    elif a.gather:
        for arm,chest,blend in anchors:
            motion=posed-rest;relative=(motion*arm[:,None]).sum(0)-(motion*chest[:,None]).sum(0)
            handles+=a.gather*relative[None,:]*(blend/np.maximum(breast,1e-8))[:,None]
    targets.append(solver.fit(posed,handles).astype(np.float32))
    if index%30==0:print('sample',index,'elapsed',round(time.monotonic()-start,2),flush=True)
targets=np.array(targets);np.savez_compressed(dest,times=q['times'],rest=rest,source=q['source'],target=targets,mask=mask)
report=dict(config=vars(a),source=dict(path=source,sha256=pk.file_hash(r/source)),geometry=dict(path=geometry,sha256=pk.file_hash(r/geometry)),generator_sha256=pk.file_hash(Path(__file__)),shape_module_sha256=pk.file_hash(r/'src/movie_factory/horse_shape379.py'),maximum_delta=float(np.linalg.norm(targets-q['source'],axis=2).max()),outside_domain_exact=bool(np.array_equal(targets[:,mask==0],q['source'][:,mask==0])),seconds=time.monotonic()-start,artifact=dict(path=str(dest.relative_to(r)),sha256=pk.file_hash(dest)),limits='Unqualified proposed shape; actual native view/motion/contact required. No bone/action change or general-rig claim.')
(out/(a.name+'.json')).write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)
