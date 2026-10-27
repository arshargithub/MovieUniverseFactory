"""Normal-aware anatomical fitting with local rigidity and intersection guards.

Surface proximity alone failed211/212:57self crossings/28compressed faces.
Keep a valid embedding while fitting the guide; do not project every vertex
independently onto the nearest branch. Original topology/action are retained.
"""
from pathlib import Path
import json
import numpy as np
from scipy.sparse import coo_matrix,diags
from scipy.sparse.csgraph import dijkstra
from scipy.sparse.linalg import spsolve
from scipy.spatial import cKDTree
from anatomy386_surface_review import pairs_for
from movie_factory.adapters.blender.anatomy_domain386 import main_skin,pectoral_domains,preserve_pectoral_interfaces
from movie_factory.adapters.blender.anatomy_rest386 import load
import hashlib

def smooth(a,b,x):
    t=np.clip((x-a)/(b-a),0,1);return t*t*(3-2*t)

def vertex_normals(p,faces):
    t=p[faces];normal=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);out=np.zeros_like(p)
    for k in range(3):np.add.at(out,faces[:,k],normal)
    volume=np.einsum('ni,ni->n',t[:,0],np.cross(t[:,1],t[:,2])).sum()/6
    if volume<0:out=-out
    return out/np.maximum(np.linalg.norm(out,axis=1)[:,None],1e-14)

def rotations(rest,current,edges,ids):
    a,b=edges.T;old=rest[a]-rest[b];new=current[a]-current[b];outer=new[:,:,None]*old[:,None,:];cov=np.zeros((len(rest),3,3));np.add.at(cov,a,outer);np.add.at(cov,b,outer)
    U,_,V=np.linalg.svd(cov[ids]);U[:,:,-1]*=np.linalg.det(U@V)[:,None];result=np.tile(np.eye(3),(len(rest),1,1));result[ids]=U@V
    return result

def oriented_goal(points,normals,vertices,faces):
    tri=vertices[faces];centers=tri.mean(1);_,idx=cKDTree(centers).query(points,k=min(64,len(faces)));idx=np.asarray(idx).reshape(len(points),-1);t=tri[idx];P=points[:,None,:];a=t[:,:,0];ab=t[:,:,1]-a;ac=t[:,:,2]-a;n=np.cross(ab,ac);nn=(n*n).sum(-1);unit=n/np.maximum(np.sqrt(nn)[:,:,None],1e-14)
    compatible=(unit*normals[:,None,:]).sum(-1)>.15
    proj=P-(((P-a)*n).sum(-1)/np.maximum(nn,1e-14))[:,:,None]*n
    v2=proj-a;d00=(ab*ab).sum(-1);d01=(ab*ac).sum(-1);d11=(ac*ac).sum(-1);d20=(v2*ab).sum(-1);d21=(v2*ac).sum(-1);den=d00*d11-d01*d01;u=(d11*d20-d01*d21)/np.maximum(den,1e-14);v=(d00*d21-d01*d20)/np.maximum(den,1e-14)
    distance=np.where((u>=0)&(v>=0)&(u+v<=1)&compatible& (nn>1e-14),((proj-P)**2).sum(-1),np.inf);best=proj.copy()
    for j,k in [(0,1),(1,2),(2,0)]:
        a=t[:,:,j];e=t[:,:,k]-a;alpha=np.clip(((P-a)*e).sum(-1)/np.maximum((e*e).sum(-1),1e-14),0,1);q=a+alpha[:,:,None]*e;d=np.where(compatible,((q-P)**2).sum(-1),np.inf);take=d<distance;best=np.where(take[:,:,None],q,best);distance=np.minimum(distance,d)
    choose=distance.argmin(1);d=distance[np.arange(len(points)),choose];goal=best[np.arange(len(points)),choose];valid=np.isfinite(d);goal[~valid]=points[~valid]
    return goal,np.sqrt(np.where(valid,d,0)),valid

def triangle_vectors(p,faces):
    t=p[faces];return np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0])

def build(root):
    q=np.load(root/'.runtime/factory-native/sikh386-appearance-c193-source/anatomy386-source.npz',allow_pickle=False);r=q['rest'].astype(float);edges=q['edges'];n=len(r);weights=q['weights'];names=q['group_names'];skin=main_skin(edges,n)
    faces=np.load(root/'.runtime/factory-native/sikh374-appearance-c124-inspect/horse-form374.npz')['triangles'];faces=faces[np.all(skin[faces],axis=1)]
    ref=np.load(root/'.runtime/art-direction/anatomy386-references/lyndon-body-reference.npz');v=ref['vertices'].astype(float).copy();f=ref['faces'].copy();v[:,0]*=.84;v[:,1]=v[:,1]*.82-.22;v[:,2]=v[:,2]*.95+.07
    t=v[f];volume=np.einsum('ni,ni->n',t[:,0],np.cross(t[:,1],t[:,2])).sum()/6
    if volume<0:f=f[:,[0,2,1]]
    centers=v[f].mean(1);f=f[(centers[:,1]<-.15)&(centers[:,2]>.86)&(centers[:,2]<1.85)]
    frozen,prox=pectoral_domains(r,weights,names);a,b=edges.T;length=np.linalg.norm(r[a]-r[b],axis=1);graph=coo_matrix((np.r_[length,length],(np.r_[a,b],np.r_[b,a])),shape=(n,n)).tocsr();distance=dijkstra(graph,directed=False,indices=np.flatnonzero(skin&frozen),min_only=True)
    x,y,z=r.T;mask=skin*smooth(.95,1.04,z)*(1-smooth(1.5,1.74,z))*(1-smooth(.27,.36,abs(x)))*smooth(-1.2,-1.1,y)*(1-smooth(-.43,-.25,y))*smooth(0,.20,distance);ids=np.flatnonzero(mask>1e-5);outside=np.flatnonzero(mask<=1e-5)
    adj=coo_matrix((np.ones(2*len(a)),(np.r_[a,b],np.r_[b,a])),shape=(n,n)).tocsr();L=diags(np.asarray(adj.sum(1)).ravel())-adj;LI=L[ids][:,ids];boundary=L[ids][:,outside]@r[outside]
    affected=np.any(mask[faces]>1e-5,axis=1);initial_n=triangle_vectors(r,faces);initial_area=np.linalg.norm(initial_n,axis=1);valid_area=initial_area>1e-8;current=r.copy();initial_cross={tuple(x) for x in pairs_for(current,faces,affected)};allowed_cross=set(initial_cross);audit=[]
    rest_edge=r[a]-r[b]
    for iteration in range(24):
        normal=vertex_normals(current,faces);goal,dist,valid=oriented_goal(current[ids],normal[ids],v,f)
        fidelity=min(2.,.04*1.23**iteration)*mask[ids]*np.exp(-(dist/.18)**2)*valid+1e-6
        R=rotations(r,current,edges,ids);average=(R[a]+R[b])*.5;edge=np.einsum('nij,nj->ni',average,rest_edge);rhs=np.zeros_like(r);np.add.at(rhs,a,edge);np.add.at(rhs,b,-edge)
        proposal=current.copy();proposal[ids]=spsolve((LI+diags(fidelity)).tocsc(),rhs[ids]-boundary+fidelity[:,None]*goal)
        d=proposal-r;length=np.linalg.norm(d,axis=1);scale=min(1.,.179/max(float(length.max()),1e-12),.149/max(float(length[prox].max()),1e-12));proposal=r+d*scale
        previous_n=triangle_vectors(current,faces);accepted=False
        for alpha in [1.,.5,.25,.125,.0625,.03125,.015625,.0078125]:
            candidate=(current+alpha*(proposal-current)).astype(np.float32).astype(float);candidate[outside]=r[outside]
            new_n=triangle_vectors(candidate,faces);area=np.linalg.norm(new_n,axis=1);ratio=area/np.maximum(initial_area,1e-20);cos=(new_n*previous_n).sum(1)/np.maximum(area*np.linalg.norm(previous_n,axis=1),1e-20)
            # This is an incremental-step guard, not a final normal-versus-raw
            # proxy. Large cumulative legitimate rotations may occur gradually.
            if np.any(affected&valid_area&((ratio<.15)|(ratio>8)|(cos<.01))):continue
            crossings={tuple(x) for x in pairs_for(candidate,faces,affected)}
            if not crossings<=allowed_cross:continue
            accepted=True;current=candidate;allowed_cross=crossings;break
        audit.append(dict(iteration=iteration,accepted=accepted,alpha=alpha if accepted else 0.,valid_correspondences=int(valid.sum()),median_distance=float(np.median(dist[valid])) if valid.any() else None,crossings=len(allowed_cross),max_delta=float(np.linalg.norm(current-r,axis=1).max())))
        print(json.dumps(audit[-1]),flush=True)
        if not accepted:break
    target=current.astype(np.float32);source=q['rest'];changed=np.any(target!=source,axis=1).astype(np.float32);protection=preserve_pectoral_interfaces(source,target,source,weights,names,max_proximal=.15)
    dest=root/'.runtime/art-direction/anatomy386-targets/rest215.npz';np.savez_compressed(dest,rest=source,target=target,mask=changed);load(root,dict(path=str(dest.relative_to(root)),sha256=hashlib.sha256(dest.read_bytes()).hexdigest()),depth_only=False)
    final_cross=pairs_for(target.astype(float),faces,affected);final_area=np.linalg.norm(triangle_vectors(target,faces),axis=1)/np.maximum(initial_area,1e-20)
    report=dict(iterations=audit,initial_crossings=len(initial_cross),final_crossings=len(final_cross),new_crossings=len({tuple(x) for x in final_cross}-initial_cross),near_collapsed_faces=int(np.sum(affected&valid_area&(final_area<.15))),protection=protection,max_original_delta=float(np.linalg.norm(target-source,axis=1).max()),scope='Normal-aware ARAP/injectivity-guarded construction control. No artistic PASS from a valid embedding; actual native neutral/raised review and consumer/AV remain mandatory.')
    (root/'results/sikh386/rest215-numeric.json').write_text(json.dumps(report,indent=2)+'\n')
    if len(final_cross) or report['near_collapsed_faces']:raise ValueError('ARAP215_FINAL_STRUCTURE_UNRESOLVED')

if __name__=='__main__':build(Path(__file__).resolve().parents[1])
