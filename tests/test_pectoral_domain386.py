import numpy as np
import pytest
from movie_factory.adapters.blender.anatomy_domain386 import pectoral_domains,preserve_pectoral_interfaces
from movie_factory.adapters.blender import nihang_anatomy386,nihang_patch

def data():
 names=['body','DEF-forearm.L','DEF-forearm.R','DEF-forefoot.L','DEF-forefoot.R'];r=np.array([[0,-.7,.7],[0,-.7,1.1],[0,-.9,1.2],[0,-.7,.3]])
 w=np.array([[1,.9,0,0,0],[1,.9,0,0,0],[1,.01,0,0,0],[1,0,0,.9,0]])
 return r,w,names

def test_proximal_skin_has_a_small_bound_but_distal_is_exact():
 r,w,n=data();a=r.copy();a[1,1]+=.03;a[2,1]+=.15
 frozen,proximal=pectoral_domains(r,w,n);assert frozen.tolist()==[True,False,False,True]
 assert preserve_pectoral_interfaces(r,a,r,w,n)['proximal_max_delta']<.031
 a[1,1]+=.04
 with pytest.raises(ValueError,match='PROXIMAL_SKIN_LIMIT'):preserve_pectoral_interfaces(r,a,r,w,n)
 a=r.copy();a[0,1]+=.001
 with pytest.raises(ValueError,match='DISTAL_LEG_DRIFT'):preserve_pectoral_interfaces(r,a,r,w,n)

def test_pectoral_operation_is_a_separate_closed_kind():
 e=dict(kind='mounted_anatomy386_pectoral',target='horse',data=dict(path='.runtime/art-direction/anatomy386-targets/a.npz',sha256='a'*64));nihang_anatomy386.validate(e)
 nihang_patch.validate(dict(operation='nihang_patch',frame=283,width=640,height=640,samples=8,edits=[e]))
 with pytest.raises(ValueError):nihang_anatomy386.validate(dict(e,allow_proximal=True))

def test_actual_pose_guard_checks_surface_and_skeleton_separately():
 from movie_factory.adapters.blender.anatomy_domain386 import evaluated_preservation
 a=np.zeros((3,4,3));b=a.copy();b[:,2,1]=.05;outside=np.array([True,True,False,True]);rig=np.zeros((3,2,4,4))
 assert evaluated_preservation(a,b,outside,rig,rig)['outside_surface_max_error']==0
 b[:,0,0]=.001
 with pytest.raises(ValueError,match='EVALUATED_PRESERVATION'):evaluated_preservation(a,b,outside,rig,rig)
 b[:,0,0]=0;r=rig.copy();r[1,0,0,0]=.001
 with pytest.raises(ValueError,match='EVALUATED_PRESERVATION'):evaluated_preservation(a,b,outside,rig,r)

def test_bilateral_sternum_blend_is_not_dominant_foreleg_skin():
 r,w,n=data();r[2,2]=1.06;w[2]=[1,.18,.18,0,0];frozen,proximal=pectoral_domains(r,w,n)
 assert not frozen[2] and not proximal[2]
 target=r.copy();target[2,1]+=.09
 assert preserve_pectoral_interfaces(r,target,r,w,n)['max_protected_delta']==0

def test_connected_policy_preserves_distal_and_old_policy():
 r,w,n=data();a=r.copy();a[1,1]+=.12
 with pytest.raises(ValueError,match='PROXIMAL_SKIN_LIMIT'):preserve_pectoral_interfaces(r,a,r,w,n)
 assert preserve_pectoral_interfaces(r,a,r,w,n,max_proximal=.15)['proximal_limit']==.15
 a[0,0]+=.001
 with pytest.raises(ValueError,match='DISTAL_LEG_DRIFT'):preserve_pectoral_interfaces(r,a,r,w,n,max_proximal=.15)
 with pytest.raises(ValueError,match='PROXIMAL_POLICY'):preserve_pectoral_interfaces(r,r,r,w,n,max_proximal=1.)
 e=dict(kind='mounted_anatomy386_connected',target='horse',data=dict(path='.runtime/art-direction/anatomy386-targets/a.npz',sha256='a'*64))
 nihang_anatomy386.validate(e)
 nihang_patch.validate(dict(operation='nihang_patch',frame=283,width=640,height=640,samples=8,edits=[e]))
 with pytest.raises(ValueError):nihang_anatomy386.validate(dict(e,proximal_limit=1.))
