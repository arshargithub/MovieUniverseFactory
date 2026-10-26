"""Outer-Python local ARAP form study. Produces data, never native execution."""
import numpy as np
from scipy.sparse import coo_matrix,diags
from scipy.sparse.linalg import splu


def smooth(x):
    x=np.clip(x,0,1)
    return x*x*(3-2*x)


def body_cage(rest,posed,shape,weights):
    """Rigid body-supported target, with no inferred biological force model."""
    r=np.asarray(rest,dtype=float);p=np.asarray(posed,dtype=float);s=np.asarray(shape,dtype=float);w=np.asarray(weights,dtype=float)
    if r.shape!=p.shape or s.shape!=r.shape or r.ndim!=2 or r.shape[1]!=3 or w.shape!=(len(r),) or not all(np.isfinite(v).all() for v in (r,p,s,w)) or (w<0).any() or w.sum()<=0:raise ValueError('FORM379_CAGE')
    w=w/w.sum();a=(r*w[:,None]).sum(0);b=(p*w[:,None]).sum(0)
    U,_,V=np.linalg.svd((r-a).T@(w[:,None]*(p-b)))
    R=V.T@U.T
    if np.linalg.det(R)<0:V[-1]*=-1;R=V.T@U.T
    return (s-a)@R.T+b


def domain(rest,weights,names):
    r=np.asarray(rest);names=list(names)
    breast=weights[:,[i for i,n in enumerate(names) if n.startswith('DEF-breast.')]].sum(1)
    distal=weights[:,[i for i,n in enumerate(names) if n.startswith('DEF-forearm.')]].sum(1)
    m=smooth((r[:,2]-.98)/.18)*smooth((1.94-r[:,2])/.22)*smooth((-.22-r[:,1])/.32)*smooth((r[:,1]+1.25)/.18)
    m[distal>.45]=0
    return m,breast


class LocalForm:
    def __init__(self,rest,edges,mask,*,softness=.025,iterations=18,handle_weights=None):
        self.rest=np.asarray(rest,dtype=float);self.edges=np.asarray(edges,dtype=int)
        self.mask=np.asarray(mask,dtype=float);self.iterations=iterations
        if self.rest.ndim!=2 or self.rest.shape[1]!=3 or self.mask.shape!=(len(self.rest),) or not np.isfinite(self.rest).all() or not np.isfinite(self.mask).all() or (self.mask<0).any() or (self.mask>1).any():raise ValueError('FORM379_INPUT')
        if self.edges.ndim!=2 or self.edges.shape[1]!=2 or self.edges.min()<0 or self.edges.max()>=len(self.rest):raise ValueError('FORM379_EDGES')
        self.i,self.j=self.edges.T;self.vector=self.rest[self.i]-self.rest[self.j]
        self.active=np.flatnonzero(self.mask>.001);self.fixed=np.flatnonzero(self.mask<=.001)
        used=np.isin(self.i,self.active)|np.isin(self.j,self.active)
        self.rotation_nodes=np.unique(self.edges[used]);lookup=np.full(len(self.rest),-1,dtype=int);lookup[self.rotation_nodes]=np.arange(len(self.rotation_nodes))
        needed=np.isin(self.i,self.rotation_nodes)|np.isin(self.j,self.rotation_nodes)
        self.ri,self.rj=self.i[needed],self.j[needed];self.rv=self.vector[needed]
        self.li,self.lj=lookup[self.ri],lookup[self.rj]
        n=len(self.rest);degree=np.bincount(self.edges.ravel(),minlength=n)
        adjacency=coo_matrix((np.ones(2*len(self.i)),(np.r_[self.i,self.j],np.r_[self.j,self.i])),shape=(n,n)).tocsr()
        L=diags(degree.astype(float))-adjacency
        self.pin=degree[self.active]*(softness+2*(1-self.mask[self.active])**4)
        hw=np.zeros(n) if handle_weights is None else np.asarray(handle_weights,dtype=float)
        if hw.shape!=(n,) or not np.isfinite(hw).all() or (hw<0).any() or (hw>20).any():raise ValueError('FORM379_HANDLES')
        self.handle_pin=degree[self.active]*hw[self.active]
        self.cross=L.tocsr()[self.active][:,self.fixed]
        self.solve=splu((L.tocsr()[self.active][:,self.active]+diags(self.pin+self.handle_pin)).tocsc()).solve if len(self.active) else None

    def rotations(self,q):
        v=q[self.ri]-q[self.rj];outer=np.einsum('ni,nj->nij',self.rv,v)
        S=np.zeros((len(self.rotation_nodes),3,3));a=self.li>=0;b=self.lj>=0
        np.add.at(S,self.li[a],outer[a]);np.add.at(S,self.lj[b],outer[b])
        U,_,V=np.linalg.svd(S);R=np.einsum('nij,nkj->nik',V.transpose(0,2,1),U)
        bad=np.linalg.det(R)<0
        V[bad,-1,:]*=-1
        R[bad]=V[bad].transpose(0,2,1)@U[bad].transpose(0,2,1)
        result=np.repeat(np.eye(3)[None],len(q),axis=0);result[self.rotation_nodes]=R
        return result

    def fit(self,posed,handle_targets=None):
        p=np.asarray(posed,dtype=float)
        if p.shape!=self.rest.shape or not np.isfinite(p).all():raise ValueError('FORM379_POSE')
        if self.solve is None:return p.copy()
        handles=p if handle_targets is None else np.asarray(handle_targets,dtype=float)
        if handles.shape!=p.shape or not np.isfinite(handles).all():raise ValueError('FORM379_HANDLE_TARGETS')
        q=p.copy();fixed_term=self.cross@p[self.fixed]
        for _ in range(self.iterations):
            R=self.rotations(q)
            vectors=np.einsum('nij,nj->ni',.5*(R[self.i]+R[self.j]),self.vector)
            b=np.zeros_like(q);np.add.at(b,self.i,vectors);np.add.at(b,self.j,-vectors)
            q[self.active]=self.solve(b[self.active]-fixed_term+self.pin[:,None]*p[self.active]+self.handle_pin[:,None]*handles[self.active])
        if not np.isfinite(q).all() or np.linalg.norm(q-p,axis=1).max()>.45:raise ValueError('FORM379_TARGET_BOUND')
        return q
