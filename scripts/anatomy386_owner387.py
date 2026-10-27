"""Actual-owner regional curvature reconstruction; no native or provider calls."""
from pathlib import Path
import json
import numpy as np
from scipy.sparse import coo_matrix,diags
from movie_factory.adapters.blender.anatomy_domain386 import main_skin

def fair(points,edges,mask,steps=120):
    p=np.asarray(points,dtype=float).copy();e=np.asarray(edges,dtype=int);m=np.asarray(mask,dtype=float)
    if p.ndim!=2 or p.shape[1]!=3 or m.shape!=(len(p),) or not np.isfinite(p).all() or not np.isfinite(m).all() or m.min()<0 or m.max()>1:raise ValueError('OWNER387_DATA')
    a,b=e.T;deg=np.bincount(e.ravel(),minlength=len(p));A=coo_matrix((np.ones(2*len(e)),(np.r_[a,b],np.r_[b,a])),shape=(len(p),len(p))).tocsr();N=diags(1/np.maximum(deg,1))@A
    # Alternating contraction/expansion limits the global volume loss of plain
    # Laplacian smoothing. This is a shape hypothesis, not a physical simulator.
    for _ in range(steps):
        p+=(N@p-p)*(.5*m[:,None]);p+=(N@p-p)*(-.53*m[:,None])
    p[m==0]=points[m==0]
    return p

def build(root):
    q=np.load(root/'.runtime/factory-native/sikh386-appearance-c193-source/anatomy386-source.npz',allow_pickle=False);r=q['rest'];edges=q['edges'];names=list(q['group_names']);w=q['weights'];skin=main_skin(edges,len(r))
    s=lambda x:np.clip(x,0,1)**2*(3-2*np.clip(x,0,1))
    owner=w[:,[j for j,n in enumerate(names) if n.startswith(('DEF-upper_arm.','DEF-forearm.','DEF-shoulder.','DEF-breast.'))]].sum(1)
    mask=skin*s((r[:,2]-.72)/.25)*s((1.88-r[:,2])/.25)*s((r[:,1]+1.4)/.25)*s((-.23-r[:,1])/.25)*s(owner/.3)
    src=q['source'];target=src.copy();i=list(q['times']).index(339);target[i]=fair(src[i],edges,mask).astype(np.float32)
    zero=fair(src[i],edges,np.zeros(len(r)),steps=2);assert np.array_equal(zero,src[i]);assert np.array_equal(target[:,mask==0],src[:,mask==0]);delta=np.linalg.norm(target[i]-src[i],axis=1);assert delta.max()<.45
    old=np.load(root/'.runtime/factory-native/sikh374-appearance-c124-inspect/horse-form374.npz',allow_pickle=False);faces=old['triangles'];faces=faces[np.all(skin[faces],axis=1)]
    tri0=src[i][faces];tri1=target[i][faces];n0=np.cross(tri0[:,1]-tri0[:,0],tri0[:,2]-tri0[:,0]);n1=np.cross(tri1[:,1]-tri1[:,0],tri1[:,2]-tri1[:,0]);a0=np.linalg.norm(n0,axis=1);a1=np.linalg.norm(n1,axis=1);active=np.any(mask[faces]>0,axis=1)&(a0>1e-9);ratio=a1[active]/a0[active]
    volume=lambda t:float(np.sum(np.einsum('ij,ij->i',t[:,0],np.cross(t[:,1],t[:,2])))/6)
    report=dict(frame=339,changed_vertices=int((delta>0).sum()),max_delta=float(delta.max()),area_ratio_p01_p50_p99=np.percentile(ratio,[1,50,99]).tolist(),near_collapsed_faces=int((ratio<.1).sum()),opposed_normal_diagnostics=int((np.sum(n0[active]*n1[active],axis=1)<0).sum()),closed_skin_volume_before=volume(tri0),closed_skin_volume_after=volume(tri1),zero_error=float(abs(zero-src[i]).max()),source_joint_paths_untouched=True,scope='One-pose actual-owner curvature experiment, including proximal forearm transition previously frozen. No fixed-volume or anatomy/embedding/motion approval; all other183 samples unchanged.')
    out=root/'.runtime/art-direction/anatomy386-targets/owner387-241.npz';np.savez_compressed(out,source=src,target=target,rest=r,mask=mask.astype(np.float32),times=q['times']);np.savez_compressed(out.with_name('owner387-241-diagnostic.npz'),before=src[i],after=target[i],mask=mask,delta=delta,faces=faces)
    (root/'results/sikh387/numeric241.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))

if __name__=='__main__':build(Path(__file__).resolve().parents[1])
