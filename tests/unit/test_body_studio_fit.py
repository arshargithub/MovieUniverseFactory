import importlib.util
from pathlib import Path
import pytest

FILE = Path(__file__).resolve().parents[2] / 'src/movie_factory/adapters/blender/body_studio_fit.py'
spec = importlib.util.spec_from_file_location('body_studio_fit', FILE)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


@pytest.mark.parametrize('job', [{}, {'operation':'inspect01','path':'/tmp/other'}, {'operation':'exec'}, None])
def test_reject_nonfixed_jobs(job):
    with pytest.raises(ValueError):
        module.validate(job)


def test_reject_changed_source(monkeypatch):
    monkeypatch.setattr(module, 'digest', lambda p: '0'*64)
    with pytest.raises(ValueError, match='Pinned'):
        module.validate({'operation':'inspect01'})


def test_chest_blend_is_continuous_and_bounded():
    assert module.chest_blend(-4)==0
    assert module.chest_blend(-1)==1
    values=[module.chest_blend(-3.1+i*.01) for i in range(131)]
    assert all(0<=v<=1 for v in values)
    assert values==sorted(values)
    assert max(b-a for a,b in zip(values,values[1:]))<.014


def test_fixed_fit_job_and_no_overwrite(monkeypatch,tmp_path):
    monkeypatch.setattr(module,'BASE',tmp_path)
    monkeypatch.setattr(module,'digest',lambda p:module.ARCHIVE_SHA if p==module.ARCHIVE else module.SOURCE_SHA)
    out=module.validate({'operation':'fit04'})
    out.mkdir()
    with pytest.raises(ValueError,match='overwrite'):
        module.validate({'operation':'fit04'})


def test_weight_sharpening_preserves_sum_support_and_dominance():
    result=module.sharpen_weights({'upper':.8,'lower':.2,'hand':0})
    assert sum(result.values())==pytest.approx(1)
    assert result['upper']>.8 and result['hand']==0
    assert module.sharpen_weights({})=={}
    assert module.sharpen_weights({'a':.5,'b':.5})=={'a':.5,'b':.5}


@pytest.mark.parametrize('operation', ['fit17','fit18','fit19','fit20','fit21','fit22','fit23','fit24','fit25','fit26','fit27'])
def test_correction_operations_are_fixed_and_non_overwriting(monkeypatch,tmp_path,operation):
    monkeypatch.setattr(module,'BASE',tmp_path)
    monkeypatch.setattr(module,'digest',lambda p:module.ARCHIVE_SHA if p==module.ARCHIVE else module.SOURCE_SHA)
    job={'operation':operation}
    path=module.validate(job)
    assert path.name=='body158-'+operation
    with pytest.raises(ValueError):module.validate({**job,'code':'anything'})
    path.mkdir()
    with pytest.raises(ValueError):module.validate(job)


@pytest.mark.parametrize('job', [{'operation':'fit48'}, {'operation':'fit27','path':'other'}, {'operation':'fit27','python':'pass'}])
def test_correction_rejects_unreviewed_variants_and_payload(job):
    with pytest.raises(ValueError):module.validate(job)


@pytest.mark.parametrize('operation',['fit28','fit29','fit30','fit31','fit32','fit33'])
def test_restored_bust_outputs_are_separate(monkeypatch,tmp_path,operation):
    monkeypatch.setattr(module,'BASE',tmp_path)
    monkeypatch.setattr(module,'digest',lambda p:module.ARCHIVE_SHA if p==module.ARCHIVE else module.SOURCE_SHA)
    path=module.validate({'operation':operation})
    assert path.name=='body159-'+operation
    path.mkdir()
    with pytest.raises(ValueError):module.validate({'operation':operation})


def test_lateral_shoulder_weight_is_continuous_at_source_boundary():
    values=[module.shoulder_chest_weight(1.5,-2.5+i*.01) for i in range(121)]
    assert all(0<=v<=1 for v in values)
    assert values==sorted(values)
    assert max(b-a for a,b in zip(values,values[1:]))<.012
    assert module.shoulder_chest_weight(1.5,-1.9)<.6
    assert module.shoulder_chest_weight(.5,-1.8)==1.


@pytest.mark.parametrize('operation',['fit34','fit35','fit36','fit37','fit38','fit39'])
def test_continuous_donor_operations_are_fixed(monkeypatch,tmp_path,operation):
    monkeypatch.setattr(module,'BASE',tmp_path)
    monkeypatch.setattr(module,'digest',lambda p:module.ARCHIVE_SHA if p==module.ARCHIVE else module.SOURCE_SHA)
    path=module.validate({'operation':operation})
    assert path.name=='body160-'+operation
    with pytest.raises(ValueError):module.validate({'operation':operation,'path':'other'})
    path.mkdir()
    with pytest.raises(ValueError):module.validate({'operation':operation})


def test_anatomical_support_fades_with_flat_endpoints():
    assert module.smooth_transition(-.1)==0
    assert module.smooth_transition(1.1)==1
    assert module.smooth_transition(.001)<1e-7
    assert 1-module.smooth_transition(.999)<1e-7


def test_curved_anatomical_boundary_preserves_central_landmarks():
    assert module.anatomical_boundary(0)==pytest.approx(-1.885)
    assert module.anatomical_boundary(1.65)==pytest.approx(-1.405)
    assert module.anatomical_boundary(-1.45)==module.anatomical_boundary(1.45)


def test_anatomical_skin_support_is_normalized_and_region_restricted():
    definitions={'upperarm.L':((1.55,.12,-2.2),(2.48,-.1,-4.6),'chest'),'forearm.L':((2.48,-.1,-4.6),(3.14,-.33,-6.07),'upperarm.L'),'hand.L':((3.14,-.33,-6.07),(3.52,-.46,-6.95),'forearm.L'),'thigh.L':((.79,.16,-6.6),(.85,-.03,-9.77),'pelvis'),'shin.L':((.85,-.03,-9.77),(.85,.16,-12.73),'thigh.L'),'foot.L':((.85,.16,-12.73),(.85,-.92,-13.17),'shin.L')}
    definitions.update({name.replace('.L','.R'):((-h[0],h[1],h[2]),(-t[0],t[1],t[2]),parent.replace('.L','.R')) for name,(h,t,parent) in list(definitions.items())})
    for point in ((0,0,-5.5),(2.48,-.1,-4.6),(.85,0,-9.77),(.79,0,-7.2)):
        weights=module.regional_weights(point,definitions)
        assert sum(weights.values())==pytest.approx(1)
        assert all(0<=w<=1 for w in weights.values())
        assert not any(n.endswith('.R') for n in weights)
    assert not any('.' in n for n in module.regional_weights((0,0,-5.5),definitions))
    assert module.regional_weights((3.6,-.5,-7.8),definitions)=={'hand.L':1.0}
    middle=module.regional_weights((0,0,-6.65),definitions)
    assert middle['thigh.L']==pytest.approx(middle['thigh.R'])


@pytest.mark.parametrize('operation',['fit40','fit41','fit42','fit43','fit44','fit45','fit46','fit47','verify48'])
def test_new_patch_operation_is_fixed_and_non_overwriting(monkeypatch,tmp_path,operation):
    monkeypatch.setattr(module,'BASE',tmp_path)
    monkeypatch.setattr(module,'digest',lambda p:module.ARCHIVE_SHA if p==module.ARCHIVE else module.SOURCE_SHA)
    path=module.validate({'operation':operation})
    assert path.name=='body161-'+operation
    path.mkdir()
    with pytest.raises(ValueError):module.validate({'operation':operation})


def test_connection_fairing_does_not_smooth_central_anatomical_landmarks():
    for x in (0,.5,1.,1.3):
        assert module.connection_fairing_weight(x,-1.7)==0
    assert module.connection_fairing_weight(1.7,-1.6)>.9
    assert module.connection_fairing_weight(-1.7,-1.6)==module.connection_fairing_weight(1.7,-1.6)
    assert module.connection_fairing_weight(0,-3.4)==0


def test_surface_digest_binds_point_order_and_positions():
    points=[(0.,1.,2.),(3.,4.,5.)]
    assert module.coordinates_digest(points)==module.coordinates_digest(iter(points))
    assert module.coordinates_digest(points)!=module.coordinates_digest(points[::-1])
    assert module.coordinates_digest(points)!=module.coordinates_digest([(0.,1.,2.001),(3.,4.,5.)])


def test_boundary_order_follows_connectivity_not_coordinate_sort():
    loops=module.boundary_loops([(3,0),(2,3),(1,2),(0,1),(4,5),(5,6),(6,4)])
    assert {frozenset(v) for v in loops}=={frozenset(range(4)),frozenset((4,5,6))}
    for loop in loops:
        edges={frozenset((a,b)) for a,b in zip(loop,loop[1:]+loop[:1])}
        assert all(e in {frozenset((a,b)) for a,b in [(3,0),(2,3),(1,2),(0,1),(4,5),(5,6),(6,4)]} for e in edges)
    with pytest.raises(ValueError):module.boundary_loops([(0,1),(1,2)])


def test_semantic_ring_anchors_do_not_drift_with_long_front_transition():
    sequence=[(0,-1,-3),(1,-.5,-2),(2,0,-1),(1,.5,-1),(0,1,-1),(-1,.5,-1),(-2,0,-1),(-1,-.5,-2)]
    order,fractions=module.anchored_ring_parameters(sequence[3:]+sequence[:3])
    arranged=[(sequence[3:]+sequence[:3])[i] for i in order]
    assert arranged[0]==sequence[0]
    assert fractions[2]==.25 and fractions[4]==.5 and fractions[6]==.75


def test_shoulder_restoration_protects_central_neck_and_fades_locally():
    for p in ((0,0,-1.8),(1.,.5,-1.8),(1.6,0,-.9),(1.6,0,-3.4)):
        assert module.shoulder_restore_weight(p)==0
    assert module.shoulder_restore_weight((1.6,.3,-2.2))==1
    assert module.shoulder_restore_weight((-1.6,.3,-2.2))==1
    assert 0<module.shoulder_restore_weight((1.3,.3,-2.2))<1


@pytest.mark.parametrize('operation',['inspect49','fit50','fit52'])
def test_shoulder_operations_are_fixed_and_non_overwriting(monkeypatch,tmp_path,operation):
    monkeypatch.setattr(module,'BASE',tmp_path)
    monkeypatch.setattr(module,'digest',lambda p:module.ARCHIVE_SHA if p==module.ARCHIVE else module.SOURCE_SHA)
    path=module.validate({'operation':operation})
    assert path.name=='body162-'+operation
    with pytest.raises(ValueError):module.validate({'operation':operation,'code':'anything'})
    path.mkdir()
    with pytest.raises(ValueError):module.validate({'operation':operation})


def test_surface_connectivity_keeps_inner_arm_with_arm_not_nearby_torso():
    points=[(0.,0.,-4.-i*.001) for i in range(120)]
    points.extend((1.6,0.,-4.-i*.001) for i in range(110))
    points.extend((-1.6,0.,-4.-i*.001) for i in range(110))
    edges=[(i,i+1) for start,end in ((0,120),(120,230),(230,340)) for i in range(start,end-1)]
    points.extend(((1.3,0.,-2.4),(-1.3,0.,-2.4),(1.6,0.,0.)))
    edges.extend(((0,340),(340,120),(0,341),(341,230),(0,342)))
    support,result=module.connected_arm_support(points,edges)
    assert all(v==0 for v in support[:120])
    assert all(v==1 for v in support[120:340])
    assert 0<support[340]<1 and support[340]==pytest.approx(support[341])
    assert support[342]==0
    assert result['lower_arm_vertices']==220
    with pytest.raises(AssertionError,match='disconnected'):
        module.connected_arm_support(points,edges+[(0,120)])


@pytest.mark.parametrize('operation',['inspect53','inspect54'])
def test_seated_diagnosis_is_pinned_read_only_and_non_overwriting(monkeypatch,tmp_path,operation):
    monkeypatch.setattr(module,'BASE',tmp_path)
    pinned='8e9db951953034113e51c0be55f8acb39b96486826d0fa404a28631c5d08ce81'
    def digest(path):
        return module.ARCHIVE_SHA if path==module.ARCHIVE else module.SOURCE_SHA if path==module.SOURCE else pinned
    monkeypatch.setattr(module,'digest',digest)
    path=module.validate({'operation':operation})
    assert path.name=='body163-'+operation
    with pytest.raises(ValueError):module.validate({'operation':operation,'path':'other'})
    path.mkdir()
    with pytest.raises(ValueError,match='overwrite'):module.validate({'operation':operation})
    import inspect
    source=inspect.getsource(module.inspect_seated_proportions)
    assert 'save_as_mainfile' not in source and 'save_mainfile' not in source


def test_seated_diagnosis_rejects_changed_native(monkeypatch,tmp_path):
    monkeypatch.setattr(module,'BASE',tmp_path)
    monkeypatch.setattr(module,'digest',lambda p:module.ARCHIVE_SHA if p==module.ARCHIVE else module.SOURCE_SHA if p==module.SOURCE else '0'*64)
    with pytest.raises(ValueError,match='seated diagnosis'):module.validate({'operation':'inspect53'})


@pytest.mark.parametrize('operation',['legs55','legs56','legs57'])
def test_leg_repair_operations_are_fixed_pinned_and_non_overwriting(monkeypatch,tmp_path,operation):
    monkeypatch.setattr(module,'BASE',tmp_path)
    monkeypatch.setattr(module,'digest',lambda p:module.SOURCE_SHA if p==module.SOURCE else '8e9db951953034113e51c0be55f8acb39b96486826d0fa404a28631c5d08ce81')
    path=module.validate({'operation':operation})
    assert path.name=='body164-'+operation
    with pytest.raises(ValueError):module.validate({'operation':operation,'hip_z':-5.9})
    path.mkdir()
    with pytest.raises(ValueError,match='overwrite'):module.validate({'operation':operation})


def test_leg_repair_rejects_unpinned_native(monkeypatch,tmp_path):
    monkeypatch.setattr(module,'BASE',tmp_path)
    monkeypatch.setattr(module,'digest',lambda p:module.SOURCE_SHA if p==module.SOURCE else '0'*64)
    with pytest.raises(ValueError,match='leg-repair'):module.validate({'operation':'legs55'})


def test_higher_lateral_hip_support_is_normalized_and_leaves_torso_unchanged():
    definitions={'thigh.L':((.84,.20,-5.95),(.90,.04,-9.03),'pelvis'),'shin.L':((.90,.04,-9.03),(.95,.16,-12.23),'thigh.L'),'foot.L':((.95,.16,-12.23),(.95,-.92,-12.85),'shin.L')}
    definitions.update({n.replace('.L','.R'):((-h[0],h[1],h[2]),(-t[0],t[1],t[2]),p.replace('.L','.R')) for n,(h,t,p) in list(definitions.items())})
    assert module.regional_weights((.8,0,-5.4),definitions,0.,(5.65,1.10))==module.regional_weights((.8,0,-5.4),definitions,0.)
    old=module.regional_weights((.8,0,-6.3),definitions,0.)
    new=module.regional_weights((.8,0,-6.3),definitions,0.,(5.65,1.10))
    assert new['thigh.L']>old['thigh.L']
    assert sum(new.values())==pytest.approx(1)
    assert not any(n.endswith('.R') for n in new)


def test_selected_hip_transition_is_bilateral_and_continuous():
    definitions={'thigh.L':((.84,.20,-5.95),(.90,.04,-9.03),'pelvis'),'shin.L':((.90,.04,-9.03),(.95,.16,-12.23),'thigh.L'),'foot.L':((.95,.16,-12.23),(.95,-.92,-12.85),'shin.L')}
    definitions.update({n.replace('.L','.R'):((-h[0],h[1],h[2]),(-t[0],t[1],t[2]),p.replace('.L','.R')) for n,(h,t,p) in list(definitions.items())})
    for x in (0.,.1,.3,.8):
        left=module.regional_weights((x,0,-6.3),definitions,0.,(5.80,1.30))
        right=module.regional_weights((-x,0,-6.3),definitions,0.,(5.80,1.30))
        assert sum(left.values())==pytest.approx(1)
        assert left.get('thigh.L',0)==pytest.approx(right.get('thigh.R',0))
        assert left.get('thigh.R',0)==pytest.approx(right.get('thigh.L',0))
    above=module.regional_weights((.3,0,-5.79),definitions,0.,(5.80,1.30))
    below=module.regional_weights((.3,0,-5.81),definitions,0.,(5.80,1.30))
    assert abs(sum(w for n,w in below.items() if n.startswith('thigh.'))-sum(w for n,w in above.items() if n.startswith('thigh.')))<.001


def test_hip_blend_mask_is_local_bilateral_and_smooth():
    for z in (-4.,-5.35,-7.7,-9.):assert module.hip_linear_support((.8,0,z))==0
    assert module.hip_linear_support((.8,0,-6.3))==1
    values=[module.hip_linear_support((.8,0,-5.-i*.01)) for i in range(301)]
    assert all(0<=v<=1 for v in values)
    assert max(abs(a-b) for a,b in zip(values,values[1:]))<.035
    assert module.hip_linear_support((-.8,0,-6.3))==module.hip_linear_support((.8,0,-6.3))


@pytest.mark.parametrize('operation',['hip58','hip59','hip61','hip62'])
def test_hip_correction_is_fixed_pinned_and_non_overwriting(monkeypatch,tmp_path,operation):
    monkeypatch.setattr(module,'BASE',tmp_path)
    monkeypatch.setattr(module,'digest',lambda p:module.SOURCE_SHA if p==module.SOURCE else 'cedce781c0980ce387b925d4b1cab6b510a8dcdd42453d6da243131440924f2f')
    path=module.validate({'operation':operation})
    assert path.name=='body166-'+operation
    with pytest.raises(ValueError):module.validate({'operation':operation,'strength':1})
    path.mkdir()
    with pytest.raises(ValueError,match='overwrite'):module.validate({'operation':operation})


def test_hip_correction_rejects_unpinned_input(monkeypatch,tmp_path):
    monkeypatch.setattr(module,'BASE',tmp_path)
    monkeypatch.setattr(module,'digest',lambda p:module.SOURCE_SHA if p==module.SOURCE else '0'*64)
    with pytest.raises(ValueError,match='hip-correction'):module.validate({'operation':'hip58'})


def test_flexion_fairing_has_a_broad_smooth_waist_fade():
    for z in (-2.,-4.65,-7.7,-9.):assert module.hip_fairing_support((.8,0,z))==0
    assert 0<module.hip_fairing_support((.8,0,-5.3))<1
    assert module.hip_fairing_support((.8,0,-6.3))==1
    values=[module.hip_fairing_support((.8,0,-4.-i*.01)) for i in range(401)]
    assert max(abs(a-b) for a,b in zip(values,values[1:]))<.03
    assert module.hip_fairing_support((-.8,0,-5.3))==module.hip_fairing_support((.8,0,-5.3))


@pytest.mark.parametrize('operation',['hip63','hip64','hip66'])
def test_shape_preserving_hip_correction_is_fixed_pinned_and_non_overwriting(monkeypatch,tmp_path,operation):
    monkeypatch.setattr(module,'BASE',tmp_path)
    monkeypatch.setattr(module,'digest',lambda p:module.SOURCE_SHA if p==module.SOURCE else 'cedce781c0980ce387b925d4b1cab6b510a8dcdd42453d6da243131440924f2f')
    path=module.validate({'operation':operation})
    assert path.name=='body168-'+operation
    with pytest.raises(ValueError):module.validate({'operation':operation,'code':'anything'})
    path.mkdir()
    with pytest.raises(ValueError,match='overwrite'):module.validate({'operation':operation})


def test_anatomical_hip_support_is_bilateral_and_posterior_transition_is_broader():
    front=module.anatomical_hip_transition((.8,-.6,-6.5))
    rear=module.anatomical_hip_transition((.8,.8,-6.5))
    assert front==(5.35,1.70)
    assert rear==pytest.approx((5.70,2.15))
    assert rear==module.anatomical_hip_transition((-.8,.8,-6.5))
