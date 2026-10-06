import importlib.util
from pathlib import Path

import numpy as np
import pytest

path=Path(__file__).resolve().parents[2]/'scripts/wardrobe_doublewrap185.py'
spec=importlib.util.spec_from_file_location('doublewrap185',path)
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)

@pytest.mark.parametrize('job',[{},'route01',{'operation':'eval'}, {'operation':'route01','path':'/tmp'}])
def test_rejects_arbitrary_payload(job):
    with pytest.raises(ValueError):module.validate(job)


def test_current_delivery_does_not_require_obsolete_failed_head_input(tmp_path,monkeypatch):
    protected=tmp_path/'protected.blend';protected.write_bytes(b'protected fixture')
    monkeypatch.setattr(module.base,'SOURCE',protected);monkeypatch.setattr(module.base,'SOURCE_SHA','expected')
    monkeypatch.setattr(module.base,'BASE',tmp_path)
    monkeypatch.setattr(module,'HEAD',tmp_path/'absent-obsolete-head.npz')
    def digest(path):
        if path==protected:return 'expected'
        raise FileNotFoundError(path)
    monkeypatch.setattr(module.base,'digest',digest)
    assert module.validate({'operation':'shotlayout01'})==tmp_path/'wardrobe185-shotlayout01'
    with pytest.raises(FileNotFoundError):module.validate({'operation':'route01'})


def test_fixed_length_limb_solver_preserves_both_lengths_and_pole_side():
    from wardrobe185_riding import hinge_point
    for target in ((1,0,0),(1.2,.2,.1),(.2,-1.5,.3)):
        root=np.array([0.,0.,0.]);pole=np.array([0.,0.,2.])
        hinge=hinge_point(root,target,pole,1.,.8)
        assert np.linalg.norm(hinge-root)==pytest.approx(1.)
        assert np.linalg.norm(hinge-target)==pytest.approx(.8)
        assert hinge[2]>0
    with pytest.raises(ValueError):hinge_point(root,(3,0,0),pole,1.,.8)
    with pytest.raises(ValueError):hinge_point(root,(0,0,0),pole,1.,.8)
    with pytest.raises(ValueError):hinge_point(root,(1,0,0),(2,0,0),1.,.8)


def test_whole_motion_reach_has_reserve_without_per_frame_clipping():
    from wardrobe185_riding import comfortable_reach
    direction=np.array([0.,-4.,0.]);offsets=np.array([[0,0,0],[0,-.5,.2],[0,.3,-.1]])
    gain=comfortable_reach(direction,offsets,4.1)
    assert .65<gain<.93
    assert np.linalg.norm(direction*gain+offsets,axis=1).max()<=4.1-.18+1e-12
    with pytest.raises(ValueError):comfortable_reach(direction,[[0,-8,0]],4.1)


def test_gallop_action_transfer_refuses_rest_or_hierarchy_drift():
    from types import SimpleNamespace as NS
    from wardrobe185_gallop import rest_parity
    class Bones(dict):
        def __iter__(self):return iter(self.values())
    def rig():
        root=NS(name='root',length=1.,matrix_local=np.eye(4),parent=None)
        tip=NS(name='tip',length=.5,matrix_local=np.eye(4),parent=root)
        return NS(data=NS(bones=Bones(root=root,tip=tip)))
    a,b=rig(),rig();assert rest_parity(a,b)==0
    b.data.bones['tip'].length+=.01
    with pytest.raises(ValueError):rest_parity(a,b)
    b=rig();b.data.bones['tip'].matrix_local[0,3]=.01
    with pytest.raises(ValueError):rest_parity(a,b)
    b=rig();b.data.bones['tip'].parent=None
    with pytest.raises(ValueError):rest_parity(a,b)
    b=rig();del b.data.bones['tip']
    with pytest.raises(ValueError):rest_parity(a,b)


def test_racing_airflow_opposes_travel_and_is_steady_during_gallop():
    from wardrobe185_gallop import apparent_airflow
    direction,strength=apparent_airflow(217)
    assert np.linalg.norm(direction)==pytest.approx(1.)
    assert direction@np.array([0,-1,0])<-.98
    assert apparent_airflow(169)[1]==0
    assert 0<apparent_airflow(193)[1]<strength
    assert strength==apparent_airflow(360)[1]==4.


def test_convex_half_spaces_reject_outside_points():
    from wardrobe185_convex import convex_outside,region_masks
    v=np.array([[0.,0.,0.],[1,0,0],[0,1,0],[0,0,1]])
    f=np.array([[0,2,1],[0,1,3],[0,3,2],[1,2,3]])
    assert convex_outside(np.array([[.1,.1,.1],[1.,1.,1.],[-.1,0,0]]),v,f).tolist()==[False,True,True]
    assert not convex_outside(v,v,f).any()
    masks=region_masks(np.array([[0,0,-2],[1.6,0,-2],[-1.6,0,-2],[0,0,-6]]))
    assert masks['torso'].tolist()==[True,False,False,False]


def test_rear_wrap_supports_are_declared_headfall_seams_not_shoulders():
    from wardrobe185_convex import rear_support_indices
    ids=rear_support_indices(2501)
    assert len(ids)==len(set(ids))==50
    assert min(ids)>=2501 and max(ids)<7205
    for i in ids:
        row,col=divmod((i-2501)%2352,21)
        assert row in (110,111,0,1,2) and 8<=col<=12


def test_tail_seams_use_free_inner_course_and_reject_distant_join():
    from wardrobe185_cut import front_tail_stitches
    p=np.zeros((7205,3))
    for side,heads,rows in ((-1,[0,61,122],range(64,85)),(1,[60,121,182],range(28,49))):
        p[heads]=[side,-1,-2]
        for row in rows:
            for col in range(14,21):p[2501+row*21+col]=[side,-1,-2+col*.001]
    pairs=front_tail_stitches(p)
    assert len(pairs)==6 and len({b for a,b in pairs})==6
    assert {a for a,b in pairs}=={0,61,122,60,121,182}
    assert all(2501<=b<4853 and (b-2501)%21>=14 for a,b in pairs)
    p[:2501,2]+=10
    with pytest.raises(ValueError,match='re-cutting'):front_tail_stitches(p)


def test_buckle_surface_frame_is_rigid_and_covariant():
    from wardrobe185_belt import band_frame
    q=np.array([(np.sin(i*np.pi*2/96),np.cos(i*np.pi*2/96),j*.1) for i in range(96) for j in range(5)])
    a=band_frame(q);np.testing.assert_allclose(a[:3,:3].T@a[:3,:3],np.eye(3),atol=1e-12)
    assert np.linalg.det(a[:3,:3])==pytest.approx(1)
    r=np.array([[0.,0,1],[1,0,0],[0,1,0]]);shift=np.array([2.,3,4]);b=band_frame(q@r.T+shift)
    np.testing.assert_allclose(b[:3,:3],r@a[:3,:3],atol=1e-12)
    np.testing.assert_allclose(b[:3,3],r@a[:3,3]+shift,atol=1e-12)
    with pytest.raises(ValueError,match='Degenerate'):band_frame(np.zeros_like(q))


def test_fabric_coordinates_have_two_directions_and_only_edge_wear():
    from wardrobe185_finish import fabric_coordinates
    from wardrobe185_head_dress import pattern
    from wardrobe185_cut import closed_course
    _,_,head=pattern();_,_,a,_=closed_course(0);_,_,b,_=closed_course(1)
    uv,wear=fabric_coordinates(np.concatenate([head,a,b]))
    assert uv.shape==(7205,3) and np.isfinite(uv).all()
    assert np.ptp(uv[:2501,0])>1 and np.ptp(uv[:2501,2])>1
    assert np.ptp(uv[2501:4853,0])>1 and np.ptp(uv[2501:4853,2])>1
    assert wear.max()==.1 and wear[30*61+30]==0
    with pytest.raises(ValueError):fabric_coordinates(np.zeros((5,3)))


def test_vertical_shot_path_has_bounded_continuous_travel():
    from wardrobe185_shot import camera_path
    np.testing.assert_allclose(camera_path(0),[0,42,42])
    np.testing.assert_allclose(camera_path(1),[-7,-17,2.6])
    p=np.array([camera_path(t) for t in np.linspace(0,1,144)])
    assert np.isfinite(p).all() and np.linalg.norm(p,axis=1).min()>15
    assert np.max(np.linalg.norm(np.diff(p,axis=0),axis=1))<1.5
    for t in (.55,.72):
        h=1e-6
        np.testing.assert_allclose((camera_path(t)-camera_path(t-h))/h,
            (camera_path(t+h)-camera_path(t))/h,atol=.003)
    with pytest.raises(ValueError):camera_path(-.1)
    with pytest.raises(ValueError):camera_path(1.1)


def test_lower_contact_broadphase_keeps_triangles_spanning_query_box():
    from wardrobe185_exit_audit import broadphase
    p=np.array([[-2.,0,0],[2,0,0],[0,2,0],[8,0,0],[9,0,0],[9,1,0]])
    f=np.array([[0,1,2],[3,4,5]])
    np.testing.assert_array_equal(broadphase(p,f,[-.1,-.1,-.1],[.1,.1,.1]),f[:1])
    with pytest.raises(ValueError):broadphase(p,f,[2,2,2],[-2,-2,-2])


def test_neutral_staging_refuses_incompatible_settled_pose():
    from wardrobe185_delivery import compatible_rest
    proof={n:np.tile(np.eye(4),(360,1,1)) for n in ('head_matrices','chest_matrices')}
    compatible_rest(proof)
    proof['head_matrices'][168,2,3]=.01
    with pytest.raises(ValueError):compatible_rest(proof)


def test_asset_selection_needs_every_visual_criterion_and_real_evidence(tmp_path):
    from wardrobe185_delivery import review_gate,CRITERIA
    evidence=tmp_path/'review.png';evidence.write_bytes(b'diagnostic fixture')
    record={'status':'INTERNAL_REVIEW_READY','criteria':{n:{'status':'PASS','judgment':'manually reviewed fixture','evidence':['review.png']} for n in CRITERIA}}
    review_gate(record,tmp_path)
    first=record['criteria'][next(iter(CRITERIA))];first['status']='NOT_RUN'
    with pytest.raises(ValueError):review_gate(record,tmp_path)
    first['status']='PASS';first['evidence']=['absent.png']
    with pytest.raises(ValueError):review_gate(record,tmp_path)


def test_double_precision_contact_hull_contains_original_and_near_coplanar_samples():
    from wardrobe185_convex import robust_hull,convex_outside
    rng=np.random.default_rng(185)
    p=rng.normal(size=(600,3));p/=np.linalg.norm(p,axis=1)[:,None]
    p=np.concatenate([p,p[:200]+1e-7])
    q,f=robust_hull(p)
    assert not convex_outside(p,q,f).any()
    assert not convex_outside(q,q,f).any()
    assert len(q)<len(p)*6


def test_surface_contact_binding_preserves_rigid_motion_and_offset():
    from wardrobe185_contact import deform
    p=np.array([[0.,0,0],[1,0,0],[0,1,0]])
    ids=np.array([[0,1,2]]);bary=np.array([[.2,.3,.5]]);offset=np.array([[.1,-.1,.2]])
    q=deform(p,ids,bary,offset)
    np.testing.assert_allclose(q,[[.4,.4,.2]])
    rotation=np.array([[0.,0,1],[1,0,0],[0,1,0]])
    shift=np.array([.4,-.3,2.])
    np.testing.assert_allclose(deform(p@rotation.T+shift,ids,bary,offset),q@rotation.T+shift)
    with pytest.raises(ValueError):deform(np.zeros_like(p),ids,bary,offset)

@pytest.mark.parametrize('revised',[False,True,3])
def test_section_continuity_and_course_topology(revised):
    for layer in (0,1):
        p,f=module.course(layer,revised=revised)
        assert p.shape==(96*17,3) and f.shape==(96*16,4)
        assert np.isfinite(p).all()
        assert f.min()==0 and f.max()==len(p)-1
        edges=np.concatenate([p[f[:,i]]-p[f[:,(i+1)%4]] for i in range(4)])
        assert np.linalg.norm(edges,axis=1).min()>.001
        assert np.linalg.norm(edges,axis=1).max()<.4
    with pytest.raises(ValueError):module.course(2)

def test_revised_courses_have_distinct_exterior_layers():
    a,fa=module.course(0,revised=3)
    b,fb=module.course(1,revised=3)
    np.testing.assert_array_equal(fa,fb)
    # A geometric screen, not visual or exhaustive collision qualification.
    distances=np.linalg.norm(a-b,axis=1)
    assert distances.min()>.06
    assert distances.max()<1
    assert b[:,1].max()>a[:,1].max()

def test_periodic_section_is_exact_at_authored_stations():
    p=np.array([[0,0,0],[1,2,0],[2,0,1],[0,-1,2]])
    for i in range(4):np.testing.assert_allclose(module.periodic_section(p,i/4),p[i])
    np.testing.assert_allclose(module.periodic_section(p,0),module.periodic_section(p,1))

def test_contact_envelope_voxel_surface_is_closed_outward_cube():
    import wardrobe185_proxy as proxy
    cells=np.zeros((5,5,5),dtype=bool);cells[2,2,2]=True
    p,f=proxy.surface(cells,np.zeros(3),.1)
    assert p.shape==(8,3) and f.shape==(6,4)
    volume=sum(np.einsum('ij,ij->i',p[f[:,0]],np.cross(p[f[:,k]],p[f[:,k+1]])).sum()/6 for k in (1,2))
    assert volume==pytest.approx(.001)
    e=np.sort(np.concatenate([f[:,[i,(i+1)%4]] for i in range(4)]),axis=1)
    _,counts=np.unique(e,axis=0,return_counts=True)
    assert np.all(counts==2)

def test_contact_envelope_closing_preserves_solid_cube():
    import wardrobe185_proxy as proxy
    cells=np.zeros((9,9,9),dtype=bool);cells[3:6,3:6,3:6]=True
    result=proxy.neighborhood(proxy.neighborhood(cells,True),False)
    np.testing.assert_array_equal(result,cells)

def test_open_wrap_strips_have_rectangular_rest_and_open_ends():
    import wardrobe185_cut as cut
    for layer in (0,1):
        p,f,r,pins=cut.strips(layer)
        assert p.shape==r.shape==(113*21,3)
        assert f.shape==(112*20,4)
        assert np.isfinite(p).all() and np.isfinite(r).all()
        assert np.all(r[:,2]==0)
        edges=np.concatenate([r[f[:,i]]-r[f[:,(i+1)%4]] for i in range(4)])
        assert np.linalg.norm(edges,axis=1).min()>.02
        assert max(pins)<len(p) and all(0<w<=1 for w in pins.values())
        assert not any(min(face)<21 and max(face)>=112*21 for face in f)

def test_solid_angle_interior_on_closed_tetrahedron():
    import wardrobe185_cut as cut
    p=np.array([[0,0,0],[1,0,0],[0,1,0],[0,0,1]])
    f=np.array([[0,2,1],[0,1,3],[0,3,2],[1,2,3]])
    assert cut.winding_inside([.1,.1,.1],p[f])
    assert not cut.winding_inside([2,2,2],p[f])


def test_rectangular_metric_preserves_flat_sheet_dimensions():
    import wardrobe185_cut as cut
    p=np.array([(i*.2,j*.3,4.) for i in range(5) for j in range(7)])
    rest=cut.rectangular_metric(p,5,7)
    np.testing.assert_allclose(np.ptp(rest,axis=0),[.8,1.8,0.])
    assert np.isfinite(rest).all()


@pytest.mark.parametrize('operation',module.OPERATIONS)
def test_dispatch_has_an_explicit_handler_for_every_admitted_operation(operation,monkeypatch,tmp_path):
    import sys,types
    target=tmp_path/'out';job=tmp_path/'job.json';job.write_text('{"operation":"'+operation+'"}')
    monkeypatch.setattr(module,'validate',lambda _:target)
    calls=[]
    def record(*_):calls.append(operation)
    for name in ('route','contact','screen'):monkeypatch.setattr(module,name,record)
    for name,methods in {
        'wardrobe_doublewrap185_solve':('settle','volumecheck'),
        'wardrobe185_isolate':('run',),'wardrobe185_proxy':('run',),
        'wardrobe185_lower_pants':('run',),'wardrobe185_airflow_control':('run',),'wardrobe185_lower_union':('run','audit','gap_audit'),
        'wardrobe185_lower_gap':('run',),
        'wardrobe185_mount_fit':('run',),
        'wardrobe185_cut_solve':('run',),'wardrobe185_rest_unit':('run',),
        'wardrobe185_intersections':('run',),
        'wardrobe185_head_dress':('run','screen'),
        'wardrobe185_belt':('screen','inspect'),
        'wardrobe185_shot':('layout','motion'),
        'wardrobe185_exit_audit':('run',),
        'wardrobe185_lower':('inspect','capture'),
            'wardrobe185_lower_drape':('dress',),
            'wardrobe185_lower_surface':('capture',),
            'wardrobe185_lower_cloth':('solve',),
            'wardrobe185_lower_review':('run',),
            'wardrobe185_lower_belt':('capture',),
        'wardrobe185_delivery':('seal','verify'),
        'wardrobe185_harness_contact':('run',),
        'wardrobe185_motion':('prep','simulate','screen'),
        'wardrobe185_integration':('audit','gaze_screen','garment_screen'),
        'wardrobe185_horse':('probe','gait_cache'),
        'wardrobe185_riding':('preview',),
        'wardrobe185_grip':('audit',),
        'wardrobe185_gallop':('prep','screen','rescreen','contact_audit'),
        'wardrobe185_contact':('capture','fidelity','structure'),
        'wardrobe185_convex':('capture','screen'),
    }.items():
        fake=types.ModuleType(name)
        for method in methods:setattr(fake,method,record)
        monkeypatch.setitem(sys.modules,name,fake)
    monkeypatch.setattr(sys,'argv',['test','--',str(job)])
    module.main()
    assert calls==[operation]


def test_fresh_head_sheet_has_authored_dimensions_and_regular_metric():
    import wardrobe185_head_dress as head
    p,f,r=head.pattern()
    assert p.shape==r.shape==(41*61,3) and f.shape==(40*60,4)
    np.testing.assert_allclose(np.ptp(r,axis=0)*.12292759120464325,[.55,.78,0])
    assert np.isfinite(p).all()


def test_closed_course_uses_uniform_periodic_fabric_metric():
    import wardrobe185_cut as cut
    for layer in (0,1):
        p,f,r,pins=cut.closed_course(layer)
        assert p.shape==r.shape==(112*21,3) and f.shape==(112*20,4)
        g=r.reshape(112,21,3)
        circum=np.linalg.norm(np.roll(g,-1,axis=0)-g,axis=2)
        across=np.linalg.norm(np.diff(g,axis=1),axis=2)
        assert np.ptp(circum)<1e-10 and np.ptp(across)<1e-10
        assert across[0,0]*20*.12292759120464325==pytest.approx(.175)
        assert np.isfinite(p).all() and len(pins)==18


def test_tailored_courses_have_concealed_rear_support_and_uniform_width():
    import wardrobe185_cut as cut
    for layer in (0,1):
        p,f,r,pins=cut.closed_course(layer,tailored=True)
        across=np.linalg.norm(np.diff(r.reshape(112,21,3),axis=1),axis=2)
        assert np.ptp(across)<1e-10
        assert across[0,0]*20*.12292759120464325==pytest.approx(.135)
        assert len(pins)==63 and min(pins)>=0 and max(pins)<len(p)
        assert 10 in pins and 28*21+16 in pins


def test_tailored_head_has_planar_trapezoid_rest_not_distorted_surface_metric():
    import wardrobe185_head_dress as head
    p,f,r=head.pattern(1.10,.94)
    grid=r.reshape(41,61,3)
    assert np.all(grid[:,:,2]==0)
    assert np.ptp(grid[0,:,1])*.12292759120464325==pytest.approx(.94)
    assert np.ptp(grid[-1,:,1])*.12292759120464325==pytest.approx(.78)


def test_motion_schedule_preserves_dressing_then_coordinates_lean():
    from wardrobe185_motion import schedule
    assert schedule(1)['lean']==schedule(169)['lean']==0
    assert schedule(1)['legs']==0 and schedule(145)['legs']==1
    assert schedule(193)['lean']==pytest.approx(.5)
    assert schedule(217)['lean']==1
    assert schedule(1)['wind']==schedule(169)['wind']==0
    assert schedule(265)['wind']>0


def test_head_weights_keep_face_rigid_and_lower_clavicles_unchanged():
    from wardrobe185_integration import head_weights
    for z in np.linspace(-3,2,101):
        weights=head_weights(z)
        assert min(weights.values())>=0 and sum(weights.values())==pytest.approx(1)
    assert head_weights(-1.72)=={'chest':1.,'MF185_neck':0.,'MF185_head':0.}
    assert head_weights(-1.)=={'chest':0.,'MF185_neck':0.,'MF185_head':1.}


def test_lower_world_transform_is_vectorized_affine_without_mutation():
    from wardrobe185_lower import world_points
    p=np.array([[1.,2.,3.],[-1.,0.,4.]]);before=p.copy();m=np.diag([2.,3.,4.,1.]);m[:3,3]=[5.,6.,7.]
    np.testing.assert_allclose(world_points(p,m),[[7.,12.,19.],[3.,6.,23.]])
    np.testing.assert_array_equal(p,before)
    with pytest.raises(ValueError):world_points([[np.nan,0,0]],np.eye(4))


def test_lower_pattern_is_connected_with_real_vents_and_only_waist_support():
    from wardrobe185_lower_pattern import pattern,lower_region_masks
    p,f,pins=pattern();assert np.isfinite(p).all()
    assert len(np.unique(f))==len(p) and len(f)==1920
    e=np.sort(np.concatenate([f[:,[0,1]],f[:,[1,2]],f[:,[2,3]],f[:,[3,0]]]),axis=1)
    edges,counts=np.unique(e,axis=0,return_counts=True)
    assert counts.max()==2 and np.linalg.norm(p[edges[:,0]]-p[edges[:,1]],axis=1).min()>.01
    assert all(p[i,2]>-5.5 for i in pins)
    assert np.ptp(p[:,2])*.12292759120464325==pytest.approx(.2581479415297508)
    assert set(lower_region_masks(p))=={'pelvis','thighL','thighR'}


def test_lower_hull_support_reduction_preserves_dense_enclosure():
    from wardrobe185_lower_prepare import build_hull,support_candidates
    from wardrobe185_convex import convex_outside
    p=np.random.default_rng(185).normal(size=(9000,3))
    small=support_candidates(p);assert len(small)<=102
    q,f=build_hull(p);assert not convex_outside(p,q,f).any()


def test_lower_mapping_uses_convex_coordinates_for_edges_and_degenerate_faces():
    from wardrobe185_lower_drape import triangle_weights
    t=np.array([[0.,0,0],[1.,0,0],[0.,1,0]])
    np.testing.assert_allclose(triangle_weights([.2,.3,.1],t),[.5,.2,.3])
    np.testing.assert_allclose(triangle_weights([.5,-1e-5,0],t),[.5,.5,0])
    w=triangle_weights([2,0,0],np.zeros((3,3)))
    assert np.isfinite(w).all() and w.min()>=0 and w.sum()==pytest.approx(1)


def test_lower_mounted_dressing_preserves_support_and_leaves_free_hem():
    from wardrobe185_lower_pattern import pattern
    from wardrobe185_lower_drape import mounted_dressing
    p,f,pins=pattern();q=mounted_dressing(p,p)
    np.testing.assert_allclose(q[list(pins)],p[list(pins)])
    assert np.isfinite(q).all() and np.max(np.linalg.norm(q-p,axis=1))>1.


def test_lower_solid_angle_interiors_are_independent_of_ray_edge_hits():
    from wardrobe185_lower_surface import winding_numbers
    from scipy.spatial import ConvexHull
    p=np.array([[x,y,z] for x in (-1.,1.) for y in (-1.,1.) for z in (-1.,1.)])
    h=ConvexHull(p);f=h.simplices.copy();t=p[f]
    reverse=np.einsum('ij,ij->i',np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]),h.equations[:,:3])<0
    f[reverse]=f[reverse,::-1]
    np.testing.assert_allclose(winding_numbers([[0,0,0],[2,0,0],[.999,0,0]],p,f),[1,0,1],atol=1e-9)


def test_body_bound_cloth_support_tracks_rotating_surface_not_world_normal():
    from wardrobe185_lower_drape import attachment_targets
    p=np.array([[0.,0,0],[1.,0,0],[0.,1,0]])
    rotation=np.array([[1.,0,0],[0.,0,-1],[0.,1,0]])
    shift=np.array([2.,3,4]);sequence=np.array([p,p@rotation.T+shift])
    q=attachment_targets(sequence,[[0,1,2]],[[.5,.2,.3]],.04)
    np.testing.assert_allclose(q[0,0],[.2,.3,.04])
    np.testing.assert_allclose(q[1],q[0]@rotation.T+shift)
    q=attachment_targets(sequence,[[0,1,2]],[[.5,.2,.3]],.04,[[.02,.01,.10]])
    np.testing.assert_allclose(q[0,0],[.22,.31,.10])
    np.testing.assert_allclose(q[1],q[0]@rotation.T+shift)


def test_clipped_body_contact_components_do_not_join_detached_limbs():
    from wardrobe185_lower_waist import components
    groups=components(np.array([[0,1,2],[2,1,3],[4,5,6]]),7)
    assert {frozenset(g) for g in groups}=={frozenset((0,1,2,3)),frozenset((4,5,6))}


def test_continuous_belt_boundary_preserves_free_hem_and_rigid_motion():
    from wardrobe185_lower_belt import boundary
    from wardrobe185_lower_pattern import pattern
    r,f,pins=pattern();theta=np.arange(96)*2*np.pi/96
    grid=np.array([[[1.4*np.sin(a),1.0*np.cos(a),-5.4+.1*j] for j in range(5)] for a in theta])
    shift=np.array([1.,2.,3.]);cut,targets=boundary(r,pins,np.array([grid,grid+shift]))
    np.testing.assert_allclose(cut[r[:,2]<-6.3],r[r[:,2]<-6.3])
    np.testing.assert_allclose(targets[1]-targets[0],np.tile(shift,(len(pins),1)))
    np.testing.assert_allclose(cut[list(pins)],targets[0])


def test_trouser_rise_changes_only_upper_garment_and_preserves_order():
    from wardrobe185_lower_pants import rise
    p=np.array([[1.,.3,z] for z in np.linspace(-10,-5.72,100)])
    q,w=rise(p)
    np.testing.assert_allclose(q[p[:,2]<=-6.8],p[p[:,2]<=-6.8])
    np.testing.assert_allclose(q[:,:2],p[:,:2])
    assert np.all(np.diff(q[:,2])>0) and q[-1,2]==pytest.approx(-5.12)


def test_trouser_rise_fits_under_sewn_waist_without_changing_lower_region():
    from wardrobe185_lower_pants import rise_fit
    w,c=rise_fit(np.array([-7.,-6.4,-5.8,-5.4,-5.1]))
    np.testing.assert_allclose(w,[0,0,1,1,1])
    assert np.all((c>=.03)&(c<=.075)) and c[-1]==pytest.approx(.03)


def test_conditioned_support_motion_rotates_initial_offset_once():
    from wardrobe185_lower_drape import support_motion
    matrices=np.repeat(np.eye(4)[None],2,axis=0)
    matrices[1,:3,:3]=[[0,-1,0],[1,0,0],[0,0,1]]
    target=np.array([[[1.,0,0]],[[2.,1,0]]])
    actual=support_motion([[1.1,0,0]],target,matrices,matrices[0])
    np.testing.assert_allclose(actual,[[[1.1,0,0]],[[2.,1.1,0]]])


def test_sewn_margin_exception_does_not_waive_skin_pants_or_soft_anchors():
    from wardrobe185_lower_drape import constraint_clearance
    assert constraint_clearance([.001,.004],'upper',[0])==.004
    assert constraint_clearance([.004,.001],'upper',[0])==.001
    for name in ('body','pants'):
        assert constraint_clearance([.001,.004],name,[0])==.001


def test_exterior_contact_frame_is_rigid_covariant_and_rejects_degenerate():
    from wardrobe185_lower_union import surface_frames
    tri=np.array([[0.,0,0],[2.,0,0],[0.,3.,0]])
    rotation=np.array([[0.,0,1],[1.,0,0],[0,1.,0]])
    np.testing.assert_allclose(surface_frames(tri),np.eye(3))
    np.testing.assert_allclose(surface_frames(tri@rotation.T+2),rotation)
    with pytest.raises(ValueError):surface_frames(np.zeros((3,3)))


def test_lower_regional_rigid_fit_preserves_rotation_translation():
    from wardrobe185_lower_regions import rigid_fit,masks
    p=np.array([[0.,0,0],[1.,0,0],[0,2.,0],[0,0,3.]])
    r=np.array([[0.,-1.,0],[1.,0,0],[0,0,1.]])
    m=rigid_fit(p,p@r.T+[1,2,3])
    np.testing.assert_allclose(m[:3,:3],r,atol=1e-12)
    np.testing.assert_allclose(m[:3,3],[1,2,3],atol=1e-12)
    assert not masks(np.array([[0.,0,-7.]]))['pelvis'][0]


def test_exact_gap_crop_keeps_crossing_triangles_not_only_inside_vertices():
    from wardrobe185_lower_gap import local_faces
    p=np.array([[-2.,0,0],[2.,0,0],[0,2.,0],[3,3,3],[4,3,3],[3,4,3]])
    f=np.array([[0,1,2],[3,4,5]])
    np.testing.assert_array_equal(local_faces(p,f,(-.1,-.1,-.1),(.1,.1,.1)),f[:1])
