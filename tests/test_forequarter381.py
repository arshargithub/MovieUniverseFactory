import numpy as np
import pytest
from movie_factory.adapters.blender import nihang_forequarter381 as h,nihang_patch


def test_partial_rotation_preserves_radius_and_exact_attachment_endpoints():
 theta=1.4;R=np.array([[1,0,0],[0,np.cos(theta),-np.sin(theta)],[0,np.sin(theta),np.cos(theta)]])
 p=np.tile([.1,-.2,-.3],(5,1));a=np.linspace(0,1,5);q=h.rotate_partial(p,R,a)
 assert np.allclose(np.linalg.norm(q,axis=1),np.linalg.norm(p,axis=1))
 assert np.allclose(q[0],p[0]) and np.allclose(q[-1],p[-1]@R.T)


def test_fixed_sternum_and_distal_source_are_not_dragged_by_lateral_rotation():
 p=np.array([[0,-.9,1.3],[.22,-.85,1.3],[.2,-.7,.7]])
 names=['DEF-breast.L','DEF-breast.R'];w=np.array([[.5,.5],[1.,0],[0,0]])
 I=np.eye(4);T=I.copy();a=1.;T[:3,:3]=[[1,0,0],[0,np.cos(a),-np.sin(a)],[0,np.sin(a),np.cos(a)]]
 ts={'DEF-breast.L':I,'DEF-breast.R':I,'DEF-upper_arm.L':T,'DEF-upper_arm.R':T};pivot=np.array([.2,-.8,1.43]);T[:3,3]=pivot-T[:3,:3]@pivot;heads={'L':pivot,'R':pivot}
 q,m=h.attached(p,p,p,w,names,ts,heads)
 assert np.array_equal(q[0],p[0]) and np.array_equal(q[-1],p[-1]);assert not np.allclose(q[1],p[1])


def test_closed_native_registration_and_no_script_payload():
 e={'kind':'mounted_forequarter381','target':'horse','profile':'attached_arch'}
 nihang_patch.validate(dict(operation='nihang_patch',frame=367,width=640,height=640,samples=8,edits=[e]))
 for bad in [dict(e,code='x'),dict(e,profile='arbitrary'),dict(e,target='rider')]:
  with pytest.raises(ValueError):h.validate(bad)


def test_positive_envelope_field_closed_and_continuous():
 from movie_factory import horse_envelope381 as e
 p=np.array([[0,-.63,1.49],[0,-2,1.49],[0,-.9,1.5]])
 d=e.field(p,[])
 assert d[0]<0 and d[1]>0 and np.isfinite(d).all()
 near=e.field(p+np.array([1e-5,0,0]),[])
 assert np.max(np.abs(near-d))<1e-4


def test_donor_inspection_is_pinned_to_existing_local_source():
 e={'kind':'mounted_forequarter381_donor_inspect','target':'horse','source':{'path':'.runtime/assets/demonstrator-01/horse.blend','sha256':'a'*64}}
 assert h.validate(e)==e
 with pytest.raises(ValueError):h.validate(dict(e,source=dict(e['source'],path='/tmp/arbitrary.blend')))


def test_native_volume_binding_keeps_mass_and_outside_groups():
 names=['DEF-breast.L','DEF-breast.R','DEF-upper_arm.L','DEF-upper_arm.R','DEF-forearm.L']
 w=np.array([[.5,.5,0,0,0],[.8,0,.2,0,0],[0,0,0,0,1.]])
 p=np.array([[0,-.9,1.25],[.25,-.9,1.25],[.2,-.7,.7]])
 q=h.volume_binding(w,names,p)
 assert np.allclose(q.sum(1),w.sum(1)) and np.array_equal(q[2],w[2])
 assert q[0,0]>q[1,0] and q[1,2]>w[1,2]


def test_posterior_thoracic_origin_does_not_rotate_as_limb_insertion():
 names=['DEF-breast.L','DEF-breast.R','DEF-upper_arm.L','DEF-upper_arm.R']
 w=np.array([[0,.8,0,.2],[0,.8,0,.2]])
 p=np.array([[-.25,-.489,1.343],[-.25,-.90,1.343]])
 q=h.volume_binding(w,names,p)
 assert np.array_equal(q[0],w[0])
 assert q[1,3]>w[1,3] and np.allclose(q.sum(1),w.sum(1))


def test_compact_rest_reduces_lower_bulk_without_moving_distal_or_high_neck():
 p=np.array([[.2,-.95,1.25],[.2,-.8,.7],[.1,-.8,2.]])
 q=h.compact_rest(p,np.ones(3))
 assert q[0,2]>p[0,2] and q[0,1]>p[0,1] and abs(q[0,0])<abs(p[0,0])
 assert np.array_equal(q[1:],p[1:])


def test_smooth_rest_warp_has_positive_local_jacobian_and_fixed_distal_region():
 pts=np.array([[x,y,z] for x in [-.3,0,.3] for y in [-1.1,-.85,-.5] for z in [.8,1.05,1.3,1.55,1.8]])
 eps=1e-5;J=np.empty((len(pts),3,3))
 for k in range(3):
  d=np.eye(3)[k]*eps;J[:,:,k]=(h.smooth_rest(pts+d)-h.smooth_rest(pts-d))/(2*eps)
 assert np.linalg.det(J).min()>.3
 assert np.array_equal(h.smooth_rest(pts[pts[:,2]<.94]),pts[pts[:,2]<.94])


def test_front_cap_preserves_all_outside_points_and_solves_finite_surface():
 from movie_factory.horse_cap381 import FrontCap
 # Real topology is tested as a source control in the generated report; this
 # planar lattice is an independent boundary/translation control.
 pts=np.array([[x,y,z] for z in np.linspace(.8,1.9,12) for x in np.linspace(-.4,.4,15) for y in [-.8]])
 edges=[]
 for row in range(12):
  for col in range(15):
   i=row*15+col
   if row<11:edges.append((i,i+15))
   if col<14:edges.append((i,i+1))
 names=['DEF-forearm.L'];w=np.zeros((len(pts),1));s=FrontCap(pts,np.array(edges),w,names)
 q=s.fit(pts);assert np.array_equal(q[s.fixed],pts[s.fixed]) and np.isfinite(q).all()
 shift=np.array([.1,.2,.3]);assert np.allclose(s.fit(pts+shift),q+shift)


def test_front_cap_data_binding_is_closed_and_local():
 e={'kind':'mounted_forequarter381_data','target':'horse','data':{'path':'.runtime/art-direction/sikh381-targets/c155.npz','sha256':'b'*64}}
 nihang_patch.validate(dict(operation='nihang_patch',frame=367,width=640,height=640,samples=8,edits=[e]))
 for bad in [dict(e,code='x'),dict(e,data=dict(e['data'],path='.runtime/art-direction/sikh381-targets/../code.npz')),dict(e,data=dict(e['data'],sha256='x'*64))]:
  with pytest.raises(ValueError):h.validate(bad)
