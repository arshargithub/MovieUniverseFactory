"""One-pose reference-informed anatomical landmark sculpt; no native dispatch."""
from pathlib import Path
import json
import numpy as np
from scipy.sparse import coo_matrix,diags
from scipy.sparse.linalg import spsolve
from scipy.spatial import cKDTree
from movie_factory.adapters.blender.anatomy_domain386 import main_skin,foreleg_ownership


def build(root):
    q=np.load(root/'.runtime/factory-native/sikh386-appearance-c193-source/anatomy386-source.npz',allow_pickle=False)
    r=q['rest'].astype(float);edges=q['edges'];n=len(r);skin=main_skin(edges,n);own=foreleg_ownership(q['weights'],q['group_names'])
    free=skin&(r[:,1]>-1.25)&(r[:,1]<-.22)&(r[:,2]>.97)&(r[:,2]<1.84)&(own<.35)
    a,b=edges.T;boundary=np.zeros(n,bool);cross=free[a]!=free[b];boundary[a[cross]]=True;boundary[b[cross]]=True;free&=~boundary
    ids=np.flatnonzero(free);tree=cKDTree(r[ids]);weight=np.zeros(n);rhs=np.zeros((n,3));handles=[]
    # Positive side target: a lower-neck-to-sternum slope, not a cap, isolated
    # sphere or rig-handle interpretation. Center sternum remains lower than
    # lateral root transitions; no pair of hanging lobes is prescribed.
    specs=[('sternum_center',[0,-.98,1.10],[0,.23,.045],30),
           ('chest_center',[0,-1.01,1.30],[0,.17,.015],24),
           ('neck_base',[0,-1.04,1.53],[0,.075,0],24)]
    for sign in [-1,1]:
        specs.extend([(f'lower_root{sign}',[sign*.17,-.96,1.11],[0,.20,.09],24),
                      (f'pectoral{sign}',[sign*.19,-.99,1.28],[0,.15,.035],24),
                      (f'upper_transition{sign}',[sign*.24,-.91,1.49],[0,.06,0],20),
                      (f'point_shoulder{sign}',[sign*.29,-.73,1.47],[0,0,0],30)])
    for name,point,delta,count in specs:
        distance,local=tree.query(point,k=count);vertex=ids[np.atleast_1d(local)]
        if distance[0]>.14:raise ValueError('LANDMARK387_MISSING_SURFACE:'+name)
        w=40*np.exp(-(np.asarray(distance)/.10)**2);weight[vertex]+=w;rhs[vertex]+=w[:,None]*np.array(delta)
        handles.append(dict(name=name,material_landmark=point,requested_displacement=delta,nearest_distance=float(distance[0]),vertices=vertex.tolist(),scope='Anatomical modeling hypothesis; physical and native views must veto incorrect shape.'))
    degree=np.bincount(np.r_[a,b],minlength=n);L=coo_matrix((np.r_[degree,-np.ones(len(a)),-np.ones(len(a))],(np.r_[np.arange(n),a,b],np.r_[np.arange(n),b,a])),shape=(n,n)).tocsr()
    A=L[ids][:,ids]+diags(weight[ids]);delta=np.zeros((n,3));delta[ids]=spsolve(A.tocsc(),rhs[ids])
    zero=spsolve(A.tocsc(),np.zeros_like(rhs[ids]));assert abs(zero).max()==0
    # Harmonic displacement's maximum principle bounds each component by its
    # authored handles. No extrapolated field or unrelated surface changes.
    assert np.isfinite(delta).all() and abs(delta[:,0]).max()<1e-12 and delta[:,1].min()>-1e-9 and delta[:,1].max()<=.230001 and delta[:,2].min()>-1e-9 and delta[:,2].max()<=.090001
    source=q['source'];target=source.copy();i=int((339-276)*2);target[i,ids]=(source[i,ids]+delta[ids]).astype(np.float32)
    assert np.array_equal(target[:,own>=.35],source[:,own>=.35]);assert np.linalg.norm(target-source,axis=2).max()<.45
    out=root/'.runtime/art-direction/anatomy386-targets/landmark387-237.npz';np.savez_compressed(out,source=source,target=target,rest=q['rest'],mask=free.astype(np.float32),times=q['times'])
    np.savez_compressed(root/'.runtime/art-direction/anatomy386-targets/landmark387-237-diagnostic.npz',rest=q['rest'],before=source[i],after=target[i],delta=delta,free=free,weights=weight,edges=edges)
    topology=np.load(root/'.runtime/factory-native/sikh374-appearance-c124-inspect/horse-form374.npz',allow_pickle=False)['triangles'];faces=topology[np.all(skin[topology],axis=1)]
    triangles0=source[i][faces];triangles1=target[i][faces];n0=np.cross(triangles0[:,1]-triangles0[:,0],triangles0[:,2]-triangles0[:,0]);n1=np.cross(triangles1[:,1]-triangles1[:,0],triangles1[:,2]-triangles1[:,0]);area0=np.linalg.norm(n0,axis=1);area1=np.linalg.norm(n1,axis=1);active=np.any(free[faces],axis=1)&(area0>1e-9);ratio=area1[active]/area0[active]
    report=dict(frame=339,area_ratio_p01_p50_p99=np.percentile(ratio,[1,50,99]).tolist(),near_collapsed_faces=int((ratio<.1).sum()),opposed_normals=int((np.sum(n0[active]*n1[active],axis=1)<0).sum()),changed_vertices=int(np.any(target[i]!=source[i],axis=1).sum()),max_delta=float(np.linalg.norm(target[i]-source[i],axis=1).max()),zero_control_error=float(abs(zero).max()),forearm_policy='Oldstrict>=.35exact for this first causal shape proof',handles=handles,scope='Single posed surface reconstruction only; other samples unchanged. Not motion-ready, not image matching, no skeleton/identity/source-master edit. Native form/embedding/contact still unqualified.')
    (root/'results/sikh387/numeric237.json').write_text(json.dumps(report,indent=2)+'\n');print('237one-pose target',report['changed_vertices'],report['max_delta'])
if __name__=='__main__':build(Path(__file__).resolve().parents[1])
