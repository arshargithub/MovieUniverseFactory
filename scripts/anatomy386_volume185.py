"""Volumetric chest deformation proof. Numeric data only; no Blender calls.

The first actual asset solve is admitted separately. This is a local appearance
hypothesis, not a verified equine biomechanics or animation solver.
"""
from pathlib import Path
import json,sys
import numpy as np
from scipy.spatial import Delaunay,cKDTree
from scipy.sparse import coo_matrix
from scipy.sparse.linalg import splu
from scipy.sparse.csgraph import connected_components


def inside(points,tri,chunk=128):
    """Parity ray alongX with deterministic tinyYZ offset, no asset execution."""
    result=[]
    a=tri[:,0];e=tri[:,1]-a;f=tri[:,2]-a;det=e[:,1]*f[:,2]-e[:,2]*f[:,1];valid=abs(det)>1e-12;safe=np.where(valid,det,1)
    for begin in range(0,len(points),chunk):
        p=points[begin:begin+chunk];y=p[:,None,1]+1.337e-7-a[None,:,1];z=p[:,None,2]+2.713e-7-a[None,:,2]
        u=(y*f[None,:,2]-z*f[None,:,1])/safe;v=(e[None,:,1]*z-e[None,:,2]*y)/safe
        hit=valid[None,:]&(u>=0)&(v>=0)&(u+v<=1)
        x=a[None,:,0]+u*e[None,:,0]+v*f[None,:,0]
        result.append(((hit&(x>p[:,None,0])).sum(1)%2)==1)
    return np.concatenate(result) if result else np.zeros(0,dtype=bool)


def system(rest,tets,fixed):
    D=np.transpose(rest[tets[:,1:]]-rest[tets[:,0,None]],(0,2,1));inv=np.linalg.inv(D);vol=abs(np.linalg.det(D))/6
    grad=np.concatenate([-inv.sum(1)[:,None,:],inv],axis=1)
    values=vol[:,None,None]*np.einsum('tai,tbi->tab',grad,grad)
    rows=np.repeat(tets,4,axis=1).ravel();cols=np.tile(tets,(1,4)).ravel()
    L=coo_matrix((values.ravel(),(rows,cols)),shape=(len(rest),len(rest))).tocsc()
    free=np.setdiff1d(np.arange(len(rest)),fixed);factor=splu(L[free][:,free]);cross=L[free][:,fixed]
    return dict(grad=grad,vol=vol,L=L,free=free,fixed=fixed,factor=factor,cross=cross)


def gradients(x,tets,grad):return np.einsum('tai,taj->tij',x[tets],grad)


def solve(rest,tets,S,target,initial=None,iterations=60):
    x=rest.copy() if initial is None else initial.copy();x[S['fixed']]=target;trace=[]
    for i in range(iterations):
        F=gradients(x,tets,S['grad']);U,_,V=np.linalg.svd(F);sign=np.linalg.det(U@V);U[:,:,-1]*=sign[:,None];R=U@V
        right=np.zeros_like(x);local=S['vol'][:,None,None]*np.einsum('tij,taj->tai',R,S['grad']);np.add.at(right,tets.ravel(),local.reshape(-1,3))
        new=x.copy();new[S['free']]=S['factor'].solve(right[S['free']]-S['cross']@target);new[S['fixed']]=target
        change=float(np.max(np.linalg.norm(new-x,axis=1)));x=new
        energy=float(np.sum(S['vol']*np.sum((gradients(x,tets,S['grad'])-R)**2,axis=(1,2))))
        trace.append(dict(iteration=i,change=change,energy=energy))
        if change<1e-6:break
    F=gradients(x,tets,S['grad']);jac=np.linalg.det(F)
    return x,dict(iterations=len(trace),trace=trace,min_jacobian=float(jac.min()),max_jacobian=float(jac.max()),volume_ratio=float((S['vol']*jac).sum()/S['vol'].sum()),constraint_error=float(np.max(abs(x[S['fixed']]-target))))


def rigid(a,b):
    ca=a.mean(0);cb=b.mean(0);U,_,V=np.linalg.svd((b-cb).T@(a-ca));U[:,-1]*=np.linalg.det(U@V);R=U@V;return R,cb-R@ca


def smooth(a,b,x):
    u=np.clip((x-a)/(b-a),0,1);return u*u*(3-2*u)


def cage(q,triangles):
    p=q['source'][14].astype(float);edges=q['edges'];N=len(p)
    adj=coo_matrix((np.ones(len(edges)*2),(np.r_[edges[:,0],edges[:,1]],np.r_[edges[:,1],edges[:,0]])),shape=(N,N));_,lab=connected_components(adj);main=lab==np.bincount(lab).argmax();faces=triangles[np.all(main[triangles],axis=1)];tri=p[faces]
    lo=np.array([-.43,-1.25,.88]);hi=np.array([.43,.08,1.85]);patch=main&np.all((p>lo)&(p<hi),axis=1);ids=np.flatnonzero(patch)
    norm=np.zeros_like(p);fn=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);np.add.at(norm,faces.ravel(),np.repeat(fn,3,axis=0));norm/=np.maximum(np.linalg.norm(norm,axis=1)[:,None],1e-12)
    sign=np.sum(tri[:,0]*np.cross(tri[:,1],tri[:,2]))
    if sign<0:norm=-norm
    vox=np.floor(p[ids]/.075).astype(int);_,pick=np.unique(vox,axis=0,return_index=True);skinids=ids[pick]
    surface=p[skinids]+.016*norm[skinids]
    axes=[np.linspace(lo[j],hi[j],int(np.ceil((hi[j]-lo[j])/.11))+1) for j in range(3)];grid=np.stack(np.meshgrid(*axes,indexing='ij'),axis=-1).reshape(-1,3)
    grid=grid[inside(grid,tri)]
    points=np.concatenate([surface,grid]);kind=np.r_[skinids,np.full(len(grid),-1)];_,unique=np.unique(np.round(points,7),axis=0,return_index=True);unique.sort();points=points[unique];kind=kind[unique]
    D=Delaunay(points);t=D.simplices;v=points[t];cent=v.mean(1);dm=np.transpose(v[:,1:]-v[:,0,None],(0,2,1));vol=abs(np.linalg.det(dm))/6
    condition=np.linalg.cond(dm);near=cKDTree(p[main]).query(cent)[0]
    keep=(inside(cent,tri)|(near<.026))&(vol>1e-9)&(condition<2500)
    longest=np.max(np.linalg.norm(v[:,:,None,:]-v[:,None,:,:],axis=-1),axis=(1,2));keep&=longest<.36
    original_tets=t[keep];used=np.unique(original_tets);index=np.full(len(points),-1);index[used]=np.arange(len(used));rest=points[used];kind=kind[used];tets=index[original_tets]
    boundary=(abs(rest[:,1]-lo[1])<.055)|(abs(rest[:,1]-hi[1])<.055)|(abs(rest[:,2]-lo[2])<.055)|(abs(rest[:,2]-hi[2])<.055)
    fixed=np.flatnonzero(boundary)
    if len(fixed)<8 or len(rest)<50:raise ValueError('VOLUME185_CAGE_BOUNDARY')
    # A rigid driven cut for each material interface, derived from source skin.
    x,y,z=p.T
    anchors=[np.flatnonzero(main&(x>0)&(z>.75)&(z<1.09)&(y<-.3)),np.flatnonzero(main&(x<0)&(z>.75)&(z<1.09)&(y<-.3)),np.flatnonzero(main&(z>1.72)&(z<1.98)&(y<-.5)),np.flatnonzero(main&(y>-.15)&(y<.22)&(z>1.05)&(z<1.8))]
    if min(map(len,anchors))<5:raise ValueError('VOLUME185_ANCHOR_COVERAGE')
    label=np.full(len(fixed),3);label[(rest[fixed,2]>hi[2]-.08)|(rest[fixed,1]<lo[1]+.08)]=2;bottom=rest[fixed,2]<lo[2]+.08;label[bottom&(rest[fixed,0]>0)]=0;label[bottom&(rest[fixed,0]<=0)]=1
    # Bind all visible skin to a kept volumetric cell, allowing a small boundary extrapolation.
    centers=rest[tets].mean(1);_,candidates=cKDTree(centers).query(p[ids],k=min(40,len(tets)))
    candidates=np.asarray(candidates).reshape(len(ids),-1);tv=rest[tets[candidates]];M=np.transpose(tv[:,:,1:]-tv[:,:,0,None],(0,1,3,2));uvw=np.linalg.solve(M,(p[ids,None]-tv[:,:,0])[...,None])[...,0]
    weights=np.concatenate([1-uvw.sum(-1,keepdims=True),uvw],axis=-1);score=np.minimum(weights,0)**2;score=score.sum(-1)+1e-5*np.sum((p[ids,None]-centers[candidates])**2,axis=-1);which=score.argmin(1);cell=candidates[np.arange(len(ids)),which];bary=weights[np.arange(len(ids)),which]
    if bary.min()<-.65 or bary.max()>1.65:raise ValueError(('VOLUME185_BINDING_GAP',float(bary.min()),float(bary.max())))
    mask=smooth(lo[1],lo[1]+.12,p[ids,1])*(1-smooth(hi[1]-.14,hi[1],p[ids,1]))*smooth(lo[2],lo[2]+.12,p[ids,2])*(1-smooth(hi[2]-.12,hi[2],p[ids,2]))
    return dict(rest=rest,tets=tets,fixed=fixed,kind=kind,label=label,anchors=anchors,skinids=ids,cell=cell,bary=bary,mask=mask,p0=p,stats=dict(nodes=len(rest),tets=len(tets),fixed=len(fixed),skin=len(ids),min_barycentric=float(bary.min()),max_barycentric=float(bary.max()),min_tet_volume=float(vol[keep].min()),max_tet_condition=float(condition[keep].max())))


def run(source,topology,target,report,cagefile):
    q=np.load(source,allow_pickle=False);tri=np.load(topology,allow_pickle=False)['triangles'];C=cage(q,tri);S=system(C['rest'],C['tets'],C['fixed']);x=C['rest'].copy();history=[]
    # Actual source trajectory continuation; this is numerical solving, not an emitted motionpreview.
    frames=list(range(283,340,4));frames.append(339);frames=sorted(set(frames))
    for frame in frames:
        posed=q['source'][int((frame-276)*2)];goal=np.empty((len(C['fixed']),3))
        for group,a in enumerate(C['anchors']):
            R,t=rigid(C['p0'][a],posed[a]);sel=np.flatnonzero(C['label']==group);nodes=C['fixed'][sel];goal[sel]=C['rest'][nodes]@R.T+t
            actual=nodes[C['kind'][nodes]>=0]
            if len(actual):
                local=np.flatnonzero(np.isin(nodes,actual));sk=C['kind'][actual];offset=C['rest'][actual]-C['p0'][sk];goal[sel[local]]=posed[sk]+offset@R.T
        # Harmonic incremental prediction avoids imposing a large jump on free tissue.
        diff=goal-x[C['fixed']];guess=x.copy();guess[C['fixed']]=goal;guess[S['free']]+=S['factor'].solve(-S['cross']@diff)
        x,diag=solve(C['rest'],C['tets'],S,goal,initial=guess,iterations=50);history.append(dict(frame=frame,**diag))
        report.write_text(json.dumps(dict(phase='solving',cage=C['stats'],history=history),indent=2)+'\n')
    if history[-1]['min_jacobian']<=.02 or history[-1]['max_jacobian']>5:raise ValueError(('VOLUME185_JACOBIAN',history[-1]['min_jacobian'],history[-1]['max_jacobian']))
    bound=np.einsum('ni,nij->nj',C['bary'],x[C['tets'][C['cell']]])
    data=q['source'].copy();i=126;delta=(bound-data[i,C['skinids']])*C['mask'][:,None]
    if np.linalg.norm(delta,axis=1).max()>.45:raise ValueError('VOLUME185_DELTA')
    data[i,C['skinids']]+=delta;mask=np.zeros(len(q['rest']),dtype=np.float32);mask[C['skinids']]=C['mask']
    np.savez_compressed(target,source=q['source'],target=data,rest=q['rest'],mask=mask,times=q['times'])
    np.savez_compressed(cagefile,rest=C['rest'],posed=x,tets=C['tets'],fixed=C['fixed'],skinids=C['skinids'],cell=C['cell'],bary=C['bary'])
    final=dict(phase='numeric_prototype_complete',cage=C['stats'],history=history,max_delta=float(np.linalg.norm(delta,axis=1).max()),corrected_frames=[339],other_samples='exact uncorrected source; NOT a motioncandidate',scope='Static worstpose volumetric deformation hypothesis. Positive metrics cannot pass anatomy. Nativefront/side/opposite/whole required.')
    report.write_text(json.dumps(final,indent=2)+'\n');return final

if __name__=='__main__':
    r=Path(__file__).resolve().parents[1];o=r/'results/sikh386';base=r/'.runtime/art-direction/anatomy386-targets'
    result=run(r/'.runtime/factory-native/sikh386-appearance-c185-source/anatomy386-source.npz',r/'.runtime/factory-native/sikh374-appearance-c124-inspect/horse-form374.npz',base/'volume185-static339.npz',o/'volume185-numeric.json',base/'volume185-cage.npz')
    print(json.dumps({k:v for k,v in result.items() if k!='history'}))
