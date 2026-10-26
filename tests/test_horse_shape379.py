import numpy as np
import pytest
from movie_factory.horse_shape379 import LocalForm,domain,body_cage
from movie_factory.adapters.blender import nihang_chest379 as h,nihang_patch


def test_rigid_pose_is_not_shrunk_by_form_solver():
    p=np.array([[0,0,0],[1,0,0],[0,1,0],[0,0,1],[1,1,1]],float)
    e=np.array([[a,b] for a in range(5) for b in range(a+1,5)])
    rot=np.array([[0,-1,0],[1,0,0],[0,0,1]])
    posed=p@rot.T+[2,3,4]
    q=LocalForm(p,e,np.array([0,1,1,1,0]),iterations=8).fit(posed)
    assert np.max(np.abs(q-posed))<1e-10
    assert np.array_equal(q[[0,4]],posed[[0,4]])


def test_body_cage_follows_body_rigid_transform_excluding_limb_motion():
    r=np.array([[0,0,0],[1,0,0],[0,1,0],[0,0,1],[2,2,2]],float)
    R=np.array([[0,-1,0],[1,0,0],[0,0,1]])
    p=r@R.T+[2,3,4];p[-1]+=[.2,.4,.1]
    shape=r+[.02,.01,-.01];q=body_cage(r,p,shape,np.array([1,1,1,1,0]))
    assert np.max(np.abs(q-(shape@R.T+[2,3,4])))<1e-12
    with pytest.raises(ValueError,match='CAGE'):body_cage(r,p,shape,np.zeros(5))


def test_deformation_keeps_fixed_interface_and_finite_volume():
    rng=np.random.default_rng(379);p=rng.normal(size=(12,3))*.05
    e=np.array([[a,b] for a in range(12) for b in range(a+1,12)])
    posed=p.copy();posed[-3:]+=[.02,.015,-.01]
    mask=np.ones(12);mask[[0,1,9,10,11]]=0
    q=LocalForm(p,e,mask,iterations=12).fit(posed)
    assert np.array_equal(q[mask==0],posed[mask==0])
    assert np.isfinite(q).all() and np.linalg.norm(q-posed,axis=1).max()<.1
    assert np.linalg.det(np.cov(q.T))>0


def test_closed_data_handler_rejects_code_and_unbound_paths(tmp_path):
    e=dict(kind='mounted_horse_chest379',target='horse',data=dict(path='.runtime/art-direction/sikh379-targets/c137.npz',sha256='a'*64))
    h.validate(e);nihang_patch.validate(dict(operation='nihang_patch',frame=367,width=432,height=768,samples=8,edits=[e]))
    for bad in [dict(e,code='x'),dict(e,target='leader'),dict(e,data=dict(path='../arbitrary.npz',sha256='a'*64))]:
        with pytest.raises(ValueError):h.validate(bad)
    with pytest.raises((ValueError,FileNotFoundError)):h.load(tmp_path,e['data'])


def test_nonfinite_target_is_not_a_successful_control():
    p=np.array([[0,0,0],[1,0,0],[0,1,0]],float);e=np.array([[0,1],[0,2],[1,2]])
    solver=LocalForm(p,e,np.array([0,1,0]))
    p[1]=np.nan
    with pytest.raises(ValueError,match='POSE'):solver.fit(p)


def test_domain_protects_face_distal_limb_and_back():
    points=np.array([[0,-.8,1.5],[0,-1.7,1.8],[0,-.8,.8],[0,.4,1.5]])
    mask,_=domain(points,np.zeros((4,1)),['DEF-breast.L'])
    assert mask[0]>.5 and not mask[1:].any()


def test_explicit_handle_changes_shape_without_moving_fixed_boundary():
    p=np.array([[0,0,0],[.1,0,0],[0,.1,0],[0,0,.1],[.1,.1,.1]],float)
    e=np.array([[a,b] for a in range(5) for b in range(a+1,5)])
    m=np.array([0,1,1,1,0]);target=p.copy();target[2]+=[0,0,.04]
    q=LocalForm(p,e,m,handle_weights=np.array([0,0,8,0,0])).fit(p,target)
    assert q[2,2]>.025 and np.array_equal(q[[0,4]],p[[0,4]])


def test_local_rotation_optimization_matches_full_neighborhood_solve():
    points=np.array([[x*.02,y*.02,.01*np.sin(x+y)] for x in range(6) for y in range(6)])
    edges=np.array([(i,j) for i in range(36) for j in range(i+1,36) if np.linalg.norm(points[i,:2]-points[j,:2])<.029])
    mask=np.zeros(36);mask[[14,15,20,21]]=1;posed=points.copy();posed[:,2]+=.01*np.cos(points[:,0]*20)
    fast=LocalForm(points,edges,mask,iterations=5);full=LocalForm(points,edges,mask,iterations=5)
    def dense(q):
        a,b=edges.T;d=points[a]-points[b];v=q[a]-q[b];outer=np.einsum('ni,nj->nij',d,v);S=np.zeros((36,3,3));np.add.at(S,a,outer);np.add.at(S,b,outer)
        U,_,V=np.linalg.svd(S);R=V.transpose(0,2,1)@U.transpose(0,2,1);bad=np.linalg.det(R)<0;V[bad,-1,:]*=-1;R[bad]=V[bad].transpose(0,2,1)@U[bad].transpose(0,2,1);return R
    full.rotations=dense
    assert np.max(np.abs(fast.fit(posed)-full.fit(posed)))<1e-12
