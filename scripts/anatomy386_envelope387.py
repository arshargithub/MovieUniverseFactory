"""Positive anatomical volume construction, not a source-curvature repair.

Fixed actor-scale modeling hypotheses, constrained by the source shoulder/elbow
centers and the physical reference roles. Primitives are not anatomical truth;
surface embedding and actual native images can reject this whole method.
"""
from pathlib import Path
import json
import numpy as np
from movie_factory.adapters.blender.anatomy_domain386 import main_skin,preserve_owner387
from movie_factory.adapters.blender.anatomy_bind386 import crossing_pairs

def ellipsoid(p,center,radii):
    r=np.asarray(radii);v=(p-center)/r
    return (np.linalg.norm(v,axis=-1)-1)*r.min()

def capsule(p,a,b,r0,r1):
    a=np.asarray(a);b=np.asarray(b);d=b-a;t=np.clip((p-a)@d/(d@d),0,1)
    return np.linalg.norm(p-(a+t[:,None]*d),axis=-1)-(r0+(r1-r0)*t)

def union(a,b,k=.075):
    h=np.clip(.5+.5*(b-a)/k,0,1);return b+(a-b)*h-k*h*(1-h)

def field(p,bones):
    # Source-calibrated proportions for a single connected thorax/sternum, not
    # two hanging pectoral balls. Dimensions are explicit hypotheses, not photo
    # measurements. The shoulder/limb coordinates are actual source FK joints.
    d=ellipsoid(p,np.array([0,-.05,1.30]),np.array([.34,.72,.44]))
    d=union(d,ellipsoid(p,np.array([0,-.72,1.27]),np.array([.235,.25,.25])))
    neck=bones[2];d=union(d,capsule(p,[0,-.68,1.49],neck[0]+.6*(neck[1]-neck[0]),.235,.205))
    for upper,fore in [(5,7),(6,8)]:
        S=bones[upper,0];E=bones[fore,0];K=E+2*(bones[fore,1]-E)
        d=union(d,capsule(p,S,E,.115,.08),.055)
        d=union(d,capsule(p,E,K,.08,.055),.045)
    return d

def project(p,bones):
    p=np.asarray(p,dtype=float).copy();eps=1e-4
    for _ in range(32):
        d=field(p,bones);g=np.column_stack([(field(p+np.eye(3)[j]*eps,bones)-field(p-np.eye(3)[j]*eps,bones))/(2*eps) for j in range(3)])
        step=d[:,None]*g/np.maximum((g*g).sum(1),1e-9)[:,None];length=np.linalg.norm(step,axis=1);step*=np.minimum(1,.025/np.maximum(length,1e-12))[:,None];p-=step
    return p

def build(root):
    q=np.load(root/'.runtime/factory-native/sikh386-appearance-c193-source/anatomy386-source.npz',allow_pickle=False);r=q['rest'];edges=q['edges'];names=list(q['group_names']);w=q['weights'];skin=main_skin(edges,len(r));s=lambda x:np.clip(x,0,1)**2*(3-2*np.clip(x,0,1))
    own=w[:,[j for j,n in enumerate(names) if n.startswith(('DEF-upper_arm.','DEF-forearm.','DEF-shoulder.','DEF-breast.'))]].sum(1)
    foot=w[:,[j for j,n in enumerate(names) if n.startswith(('DEF-forefoot.','DEF-f_toe.','DEF-f_hoof.'))]].sum(1)
    mask=skin*s((r[:,2]-.72)/.25)*s((1.88-r[:,2])/.25)*s((r[:,1]+1.4)/.25)*s((-.23-r[:,1])/.25)*s(own/.3)*(foot<.05);ids=np.flatnonzero(mask>0);i=list(q['times']).index(339);src=q['source'];before=src[i];candidate=project(before[ids],q['bones'][i]);after=before.copy();after[ids]=(before[ids]+(candidate-before[ids])*mask[ids,None]).astype(np.float32)
    target=src.copy();target[i]=after;delta=np.linalg.norm(after-before,axis=1)
    faces=np.load(root/'.runtime/factory-native/sikh374-appearance-c124-inspect/horse-form374.npz',allow_pickle=False)['triangles'];faces=faces[np.all(skin[faces],axis=1)];tri0=before[faces];tri1=after[faces];n0=np.cross(tri0[:,1]-tri0[:,0],tri0[:,2]-tri0[:,0]);n1=np.cross(tri1[:,1]-tri1[:,0],tri1[:,2]-tri1[:,0]);a0=np.linalg.norm(n0,axis=1);a1=np.linalg.norm(n1,axis=1);relevant=np.any(mask[faces]>0,axis=1);active=relevant&(a0>1e-9);ratio=a1[active]/a0[active]
    old=crossing_pairs(before,faces,relevant);new=crossing_pairs(after,faces,relevant)
    volume=lambda t:float(np.sum(np.einsum('ij,ij->i',t[:,0],np.cross(t[:,1],t[:,2])))/6)
    report=dict(frame=339,changed_vertices=int((delta>0).sum()),max_delta=float(delta.max()),area_ratio_p01_p50_p99=np.percentile(ratio,[1,50,99]).tolist(),near_collapsed_faces=int((ratio<.1).sum()),opposed_normal_diagnostics=int((np.sum(n0[active]*n1[active],axis=1)<0).sum()),crossings_before=len(old),crossings_after=len(new),introduced_crossings=len(new-old),closed_volume_before=volume(tri0),closed_volume_after=volume(tri1),unfeathered_field_error=float(abs(field(candidate,q['bones'][i])).max()),scope='Singleposed positivevolume hypothesis. Reference photography judges anatomy; analytic surface convergence cannot qualify topology, source skeleton, motion or film look.')
    np.savez_compressed(root/'.runtime/art-direction/anatomy386-targets/envelope387-244-diagnostic.npz',before=before,after=after,mask=mask,faces=faces,delta=delta)
    try:report['domain']=preserve_owner387(src,target,r,w,names,edges)
    except ValueError as e:report['domain_failure']=str(e)
    (root/'results/sikh387/numeric244.json').write_text(json.dumps(report,indent=2)+'\n')
    # Explicit proof may return a failed target as diagnostic data, never adopt it.
    if report.get('domain_failure') or report['introduced_crossings'] or report['near_collapsed_faces']:raise ValueError('ENVELOPE387_EMBEDDING_OR_DOMAIN_FAILED')
    np.savez_compressed(root/'.runtime/art-direction/anatomy386-targets/envelope387-244.npz',source=src,target=target,rest=r,mask=mask.astype(np.float32),times=q['times'])
    print(json.dumps(report))

if __name__=='__main__':build(Path(__file__).resolve().parents[1])
