"""Coupled rest-metric skin proof, original data only; no Blender dispatch.

Unlike227, the actual elbow/proximalforearm is free. Unlike241, the metric is
original rest shape, not curvature smoothing of a defective posed surface.
"""
from pathlib import Path
import json
import numpy as np
from anatomy386_structural387 import arap,self_test
from movie_factory.adapters.blender.anatomy_domain386 import main_skin,preserve_owner387
from movie_factory.adapters.blender.anatomy_bind386 import crossing_pairs

def domain(rest,weights,names,edges):
    r=np.asarray(rest);foot=weights[:,[i for i,n in enumerate(names) if n.startswith(('DEF-forefoot.','DEF-f_toe.','DEF-f_hoof.'))]].sum(1)
    allowed=main_skin(edges,len(r))&(r[:,2]>.72)&(r[:,2]<1.88)&(r[:,1]>-1.4)&(r[:,1]<-.23)&(foot<.05)
    a,b=edges.T;boundary=np.zeros(len(r),bool);cross=allowed[a]!=allowed[b];boundary[a[cross]]=True;boundary[b[cross]]=True
    return allowed&~boundary

def build(root):
    q=np.load(root/'.runtime/factory-native/sikh386-appearance-c193-source/anatomy386-source.npz',allow_pickle=False);r=q['rest'];src=q['source'];edges=q['edges'];free=domain(r,q['weights'],list(q['group_names']),edges);skin=main_skin(edges,len(r))
    fs=np.load(root/'.runtime/factory-native/sikh374-appearance-c124-inspect/horse-form374.npz',allow_pickle=False)['triangles'];fs=fs[np.all(skin[fs],axis=1)];affected=np.any(free[fs],axis=1)
    target=src.copy();report=dict(controls=self_test(),free_vertices=int(free.sum()),poses=[],scope='Three diagnostic poses, coupled original-rest skin reconstruction; no full-speed or anatomical pass.')
    for frame in [333,339,346]:
        i=list(q['times']).index(frame);before=src[i];after,changes=arap(r.astype(float),before.astype(float),edges,free,iterations=100);after=after.astype(np.float32);after[~free]=before[~free];target[i]=after
        a=before[fs];b=after[fs];n0=np.cross(a[:,1]-a[:,0],a[:,2]-a[:,0]);n1=np.cross(b[:,1]-b[:,0],b[:,2]-b[:,0]);ar0=np.linalg.norm(n0,axis=1);ar1=np.linalg.norm(n1,axis=1);valid=affected&(ar0>1e-9);ratio=ar1[valid]/ar0[valid]
        old=crossing_pairs(before,fs,affected);new=crossing_pairs(after,fs,affected)
        row=dict(frame=frame,max_delta=float(np.linalg.norm(after-before,axis=1).max()),outside_error=float(abs(after[~free]-before[~free]).max()),iterations=len(changes),last_step=changes[-1],near_collapsed_faces=int((ratio<.1).sum()),area_ratio=np.percentile(ratio,[1,50,99]).tolist(),crossings_before=len(old),crossings_after=len(new),introduced_crossings=len(new-old));report['poses'].append(row);print(json.dumps(row),flush=True)
    try:report['domain']=preserve_owner387(src,target,r,q['weights'],list(q['group_names']),edges)
    except ValueError as e:report['domain_failure']=str(e)
    dest=root/'.runtime/art-direction/anatomy386-targets/coupled388-247.npz';np.savez_compressed(dest,source=src,target=target,rest=r,mask=free.astype(np.float32),times=q['times'])
    (root/'results/sikh387/numeric247.json').write_text(json.dumps(report,indent=2)+'\n')
    # Rejected numerical topology can still be examined as a labeled native
    # diagnostic if safe domain holds; it can never be passed as anatomy.
    if report.get('domain_failure'):raise ValueError(report['domain_failure'])
if __name__=='__main__':build(Path(__file__).resolve().parents[1])
