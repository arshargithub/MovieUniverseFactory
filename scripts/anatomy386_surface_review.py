"""Read-only proper-crossing and outward-normal diagnostics.

Relative normal rotation is not a general triangle-inversion test. These controls
are scoped diagnostics, not full collision/contact or artistic qualification.
"""
from pathlib import Path
import json,sys,hashlib
import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
from anatomy386_volume185 import inside


def segment_hit(p,d,tri,eps=1e-8):
 a=tri[:,0];e1=tri[:,1]-a;e2=tri[:,2]-a;h=np.cross(d,e2);det=np.einsum('ni,ni->n',e1,h);valid=abs(det)>eps;safe=np.where(valid,det,1);s=p-a;u=np.einsum('ni,ni->n',s,h)/safe;q=np.cross(s,e1);v=np.einsum('ni,ni->n',d,q)/safe;t=np.einsum('ni,ni->n',e2,q)/safe
 return valid&(u>eps)&(v>eps)&(u+v<1-eps)&(t>eps)&(t<1-eps)


def crossing(a,b):
 hit=np.zeros(len(a),dtype=bool)
 for i,j in [(0,1),(1,2),(2,0)]:
  hit|=segment_hit(a[:,i],a[:,j]-a[:,i],b);hit|=segment_hit(b[:,i],b[:,j]-b[:,i],a)
 return hit


def pairs_for(points,faces,affected):
 tri=points[faces];lo=tri.min(1);hi=tri.max(1);pairs=[]
 for i in np.flatnonzero(affected):
  candidates=np.flatnonzero(np.all(hi>=lo[i]-1e-8,axis=1)&np.all(lo<=hi[i]+1e-8,axis=1));candidates=candidates[candidates!=i]
  if len(candidates):
   shared=np.any(faces[candidates,:,None]==faces[i][None,None,:],axis=(1,2));candidates=candidates[~shared]
   pairs.extend((min(i,int(j)),max(i,int(j))) for j in candidates)
 if not pairs:return np.empty((0,2),dtype=int)
 pairs=np.unique(np.array(pairs,dtype=int),axis=0);return pairs[crossing(tri[pairs[:,0]],tri[pairs[:,1]])]


def run(root,cy):
 path=root/f'.runtime/art-direction/anatomy386-targets/rest{cy}.npz';q=np.load(path,allow_pickle=False);top=np.load(root/'.runtime/factory-native/sikh374-appearance-c124-inspect/horse-form374.npz',allow_pickle=False);e=top['edges'];N=len(q['rest']);_,lab=connected_components(coo_matrix((np.ones(len(e)*2),(np.r_[e[:,0],e[:,1]],np.r_[e[:,1],e[:,0]])),shape=(N,N)));main=lab==np.bincount(lab).argmax();faces=top['triangles'];faces=faces[np.all(main[faces],axis=1)];affected=np.any(q['mask'][faces]>0,axis=1)
 before=q['rest'].astype(float);after=q['target'].astype(float);p=before[faces];t=after[faces];n0=np.cross(p[:,1]-p[:,0],p[:,2]-p[:,0]);n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);a0=np.linalg.norm(n0,axis=1);a=np.linalg.norm(n,axis=1);valid=a0>1e-8;cos=(n*n0).sum(1)/np.maximum(a*a0,1e-20);rotation=affected&valid&(cos<.05)
 old=pairs_for(before,faces,affected);new=pairs_for(after,faces,affected);oldset={tuple(x) for x in old};introduced=[list(map(int,x)) for x in new if tuple(x) not in oldset]
 norm=n[rotation]/a[rotation,None];c=t[rotation].mean(1)
 signed=float(np.einsum('ni,ni->n',t[:,0],np.cross(t[:,1],t[:,2])).sum()/6)
 if signed<0:norm=-norm
 pos=inside(c+.0005*norm,t);neg=inside(c-.0005*norm,t)
 result=dict(binding=dict(path=str(path.relative_to(root)),sha256=hashlib.sha256(path.read_bytes()).hexdigest()),affected_faces=int(affected.sum()),large_relative_normal_rotations=int(rotation.sum()),near_collapsed_faces=int(np.sum(affected&valid&(a/a0<.1))),area_extrema=[float((a/a0)[affected&valid].min()),float((a/a0)[affected&valid].max())],old_proper_nonadjacent_crossings=len(old),new_proper_nonadjacent_crossings=len(new),introduced_crossing_pairs=introduced,rotated_face_positive_probe_inside=int(pos.sum()),rotated_face_negative_probe_outside=int((~neg).sum()),signed_volume=signed,scope='Read-onlyrest structuraldiagnostic. Sharedvertex/coplanarcontact andfullpose/productionconsumer notuniversallyqualified. Nativeappearance stillrequiresactualreview.')
 (root/f'results/sikh386/surface{cy}-review.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))

if __name__=='__main__':run(Path(__file__).resolve().parents[1],int(sys.argv[1]))
