import importlib.util
from pathlib import Path
import pytest

spec = importlib.util.spec_from_file_location('wardrobe_motion178', Path(__file__).resolve().parents[2] / 'scripts/wardrobe_motion178.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


@pytest.mark.parametrize('job', [None, {}, {'operation': 'exec'}, {'operation': 'inspect01', 'code': 'x'}, {'operation': '../outside'}])
def test_enum_only(job):
    with pytest.raises(ValueError):
        m.validate(job)


def test_source_and_evidence_guards(monkeypatch, tmp_path):
    source = tmp_path / 'input.blend'
    source.write_bytes(b'pinned fixture')
    monkeypatch.setattr(m, 'SOURCE', source)
    monkeypatch.setattr(m, 'SOURCE_SHA', m.digest(source))
    monkeypatch.setattr(m, 'BASE', tmp_path)
    out = m.validate({'operation': 'inspect01'})
    out.mkdir()
    with pytest.raises(ValueError, match='overwrite'):
        m.validate({'operation': 'inspect01'})
    source.write_bytes(b'changed')
    with pytest.raises(ValueError, match='Pinned'):
        m.validate({'operation': 'inspect01'})


def test_bounded_clean_grid():
    points, faces = m.sheet_grid(4, 5, lambda u, v: (u, v, 0))
    assert len(points) == 20 and len(faces) == 12
    assert len(set(faces[0])) == 4
    assert all(0 <= i < len(points) for f in faces for i in f)


def test_closed_course_has_no_overlapping_pinned_tabs():
    points,faces=m.periodic_grid(12,5,lambda u,v:(u,v,0))
    assert len(points)==60 and len(faces)==48
    assert faces[-1]==(58,59,4,3)
    edges={}
    for face in faces:
        for a,b in zip(face,face[1:]+face[:1]):
            edge=tuple(sorted((a,b)));edges[edge]=edges.get(edge,0)+1
    assert sum(n==1 for n in edges.values())==24


def test_moving_start_is_hash_bound(monkeypatch,tmp_path):
    source=tmp_path/'source.blend';source.write_bytes(b'fixture')
    start=tmp_path/'start.npz';start.write_bytes(b'bounded fixture')
    monkeypatch.setattr(m,'SOURCE',source)
    monkeypatch.setattr(m,'SOURCE_SHA',m.digest(source))
    monkeypatch.setattr(m,'BASE',tmp_path)
    monkeypatch.setattr(m,'MOVING_START',start)
    monkeypatch.setattr(m,'MOVING_START_SHA',m.digest(start))
    assert m.validate({'operation':'move01'})==tmp_path/'wardrobe178-move01'
    start.write_bytes(b'replaced')
    with pytest.raises(ValueError,match='moving start'):
        m.validate({'operation':'move01'})


def test_simulation_not_frozen_or_projected():
    import inspect
    source = inspect.getsource(m.settle)
    assert "'CLOTH'" in source
    assert 'modifiers.remove' not in source
    assert 'outer_clearance' not in source
    assert "'motion_gate':'NOT_RUN'" in source


def test_authored_motion_envelope():
    spec2 = importlib.util.spec_from_file_location('controls178', Path(m.__file__).with_name('wardrobe_motion178_controls.py'))
    controls = importlib.util.module_from_spec(spec2);spec2.loader.exec_module(controls)
    assert controls.phase(1)['wind'] == 0
    assert controls.phase(97)['wind'] == 0
    assert controls.phase(289)['wind'] == 0
    assert controls.phase(289)['bob'] == 0
    assert controls.phase(289)['lean'] == 1
    assert controls.phase(193)['wind'] > 0
    assert all(abs(controls.phase(f)['bob']) <= .065 for f in range(1,290))
    assert all(controls.phase(f,neutral_entry=True)['lean']==0 for f in range(1,98))
    assert controls.phase(145,neutral_entry=True)['lean']==1


def test_geometry_pause_restores_exact_state_even_on_error(monkeypatch):
    from types import SimpleNamespace
    import sys
    spec2=importlib.util.spec_from_file_location('controls178_pause',Path(m.__file__).with_name('wardrobe_motion178_controls.py'))
    controls=importlib.util.module_from_spec(spec2);spec2.loader.exec_module(controls)
    objects=[SimpleNamespace(name='body',type='MESH',hide_viewport=False),
             SimpleNamespace(name='old hidden cloth',type='MESH',hide_viewport=True),
             SimpleNamespace(name='MF178_support',type='MESH',hide_viewport=False),
             SimpleNamespace(name='rig',type='ARMATURE',hide_viewport=False)]
    fake=SimpleNamespace(context=SimpleNamespace(scene=SimpleNamespace(objects=objects),
                         view_layer=SimpleNamespace(update=lambda:None)))
    monkeypatch.setitem(sys.modules,'bpy',fake)
    with pytest.raises(RuntimeError):
        with controls.render_geometry_paused():
            assert [o.hide_viewport for o in objects]==[True,True,False,False]
            raise RuntimeError('diagnostic interruption')
    assert [o.hide_viewport for o in objects]==[False,True,False,False]


def test_bone_objects_admit_names_and_never_silent_chest_fallback():
    from types import SimpleNamespace
    spec2=importlib.util.spec_from_file_location('controls178_names',Path(m.__file__).with_name('wardrobe_motion178_controls.py'))
    controls=importlib.util.module_from_spec(spec2);spec2.loader.exec_module(controls)
    bones=[SimpleNamespace(name=n) for n in ('chest','upperarm.L','forearm.L')]
    assert controls.admitted_weights({'upperarm.L':.7,'forearm.L':.3,'legacy':1},bones)=={'upperarm.L':.7,'forearm.L':.3}
    with pytest.raises(ValueError,match='No admitted'):
        controls.admitted_weights({'legacy':1},bones)


def test_supported_head_has_arc_not_flat_pin_patch(monkeypatch):
    import sys
    from types import SimpleNamespace
    monkeypatch.setitem(sys.modules,'wardrobe_motion178_controls',SimpleNamespace(smooth=lambda x:max(0,min(1,x))))
    points,faces,pins,components=m.supported_head_pattern()
    assert components==[1395] and len(faces)==1320
    assert len(pins)==15 and all(i<31 for i in pins)
    assert max(points[i][1] for i in pins)>min(points[i][1] for i in pins)
    assert abs(points[-1][0])<abs(points[30][0])


def test_dressed_opening_arc_has_lower_free_corners():
    points,faces,pins,components=m.dressed_head_pattern()
    assert components==[1395] and len(faces)==1320
    assert len(pins)==19
    assert points[0][2]<points[6][2]<points[15][2]
    assert points[30][2]<points[24][2]<points[15][2]
    assert min(points[i][2] for i in pins)<max(points[i][2] for i in pins)-.4


def test_concealed_tacks_link_components_without_world_locks():
    spec2=importlib.util.spec_from_file_location('playback178_stitch',Path(m.__file__).with_name('wardrobe_motion178_playback.py'))
    playback=importlib.util.module_from_spec(spec2);spec2.loader.exec_module(playback)
    points=[(i*.001,0.,0.) for i in range(3891)]
    edges=playback.concealed_stitches(points,[1395,1248,1248])
    assert len(edges)==8 and len(set(edges))==8
    assert all(0<=a<b<3891 for a,b in edges)
    assert sum(a<1395<=b<2643 for a,b in edges)==4
    assert sum(1395<=a<2643<=b for a,b in edges)==4
    joined=playback.concealed_stitches(points,[1395,1248,1248],front_overlap=True)
    assert len(joined)==21 and len(set(joined))==21
    assert all(1395<=a<2643<=b for a,b in joined[8:])
    with pytest.raises(ValueError,match='topology'):
        playback.concealed_stitches(points,[1395,1248])


def test_two_wrap_ribbon_is_one_open_strip_with_rear_ends():
    points,faces,pins,components=m.twice_wrapped_patterns()
    assert components==[1395,2496] and len(points)==3891
    assert all(0<=i<3891 for f in faces for i in f)
    assert m.ribbon_path(0)[1]>2 and m.ribbon_path(1)[1]>2
    assert m.ribbon_path(0)!=m.ribbon_path(1)
    assert len([i for i in pins if i>=1395])==12
    # Second turn is linked by actual quad faces, not another disconnected ring.
    assert any(min(f)<1395+96*13<=max(f) for f in faces)


def test_mass_is_distributed_not_garment_mass_at_every_vertex():
    spec2=importlib.util.spec_from_file_location('playback178_mass',Path(m.__file__).with_name('wardrobe_motion178_playback.py'))
    playback=importlib.util.module_from_spec(spec2);spec2.loader.exec_module(playback)
    result=playback.cloth_profile([(0,0,0),(1,0,0),(1,1,0),(0,1,0)],[(0,1,2,3)],1)
    assert result['estimated_dressed_area_m2']==pytest.approx(1.)
    assert result['estimated_total_mass_kg']==pytest.approx(.35)
    assert result['vertex_mass']*4==pytest.approx(.35)
    assert result['effector_gain']==pytest.approx(result['vertex_mass']/.22)
    with pytest.raises(ValueError,match='cloth area'):
        playback.cloth_profile([(0,0,0)]*4,[(0,1,2,3)],1)


def test_zero_length_edges_are_rejected_before_physics():
    spec2=importlib.util.spec_from_file_location('playback178_geometry',Path(m.__file__).with_name('wardrobe_motion178_playback.py'))
    playback=importlib.util.module_from_spec(spec2);spec2.loader.exec_module(playback)
    with pytest.raises(ValueError,match='Collapsed'):
        playback.geometry_preflight([(0,0,0),(0,0,0),(1,1,0)],[(0,1,2)])
    assert playback.geometry_preflight([(0,0,0),(1,0,0),(1,1,0)],[(0,1,2)])['collapsed_edge_gate']=='PASS'


def test_supported_border_is_actual_upper_edge():
    spec2=importlib.util.spec_from_file_location('playback178_border',Path(m.__file__).with_name('wardrobe_motion178_playback.py'))
    playback=importlib.util.module_from_spec(spec2);spec2.loader.exec_module(playback)
    points,_,_,components=m.twice_wrapped_patterns(True)
    assert playback.supported_border(points,components)==12
    points[1395+48*13+12]=(0,0,-100)
    with pytest.raises(ValueError,match='orientation'):
        playback.supported_border(points,components)


def test_unrolled_rest_preserves_head_and_has_positive_flat_ribbon_metric():
    spec2=importlib.util.spec_from_file_location('playback178_rest',Path(m.__file__).with_name('wardrobe_motion178_playback.py'))
    playback=importlib.util.module_from_spec(spec2);spec2.loader.exec_module(playback)
    points,faces,_,components=m.twice_wrapped_patterns(True)
    flat=playback.flat_ribbon_rest(points,points,components)
    assert flat[:1395]==points[:1395]
    assert len(flat)==3891 and all(p[2]==0 for p in flat[1395:])
    assert all(flat[1395+(r+1)*13][0]>flat[1395+r*13][0] for r in range(191))
    assert playback.geometry_preflight(flat,faces)['collapsed_edge_gate']=='PASS'


@pytest.mark.parametrize('job',[None,{}, {'operation':'exec'},
                              {'operation':[]},{'operation':None},
                              {'operation':'screen18','path':'outside'},
                              {'operation':'../screen18'}])
def test_cache_presenter_admits_only_fixed_enum(job):
    spec2=importlib.util.spec_from_file_location('proof178',Path(m.__file__).with_name('wardrobe_motion178_proof.py'))
    proof=importlib.util.module_from_spec(spec2);spec2.loader.exec_module(proof)
    with pytest.raises(ValueError,match='enum'):proof.validate(job)


def test_cache_presenter_hash_and_overwrite_guards(monkeypatch,tmp_path):
    spec2=importlib.util.spec_from_file_location('proof178_guard',Path(m.__file__).with_name('wardrobe_motion178_proof.py'))
    proof=importlib.util.module_from_spec(spec2);spec2.loader.exec_module(proof)
    source=tmp_path/'source.blend';source.write_bytes(b'fixture')
    cache=tmp_path/'wardrobe178-move18'/'cloth-trajectory.npz';cache.parent.mkdir();cache.write_bytes(b'cache')
    monkeypatch.setattr(proof.recipe,'BASE',tmp_path)
    monkeypatch.setattr(proof.recipe,'SOURCE',source)
    monkeypatch.setattr(proof.recipe,'SOURCE_SHA',proof.recipe.digest(source))
    monkeypatch.setattr(proof,'CACHES',{'18':proof.recipe.digest(cache)})
    out,actual=proof.validate({'operation':'screen18'});assert actual==cache
    out.mkdir()
    with pytest.raises(ValueError,match='overwrite'):proof.validate({'operation':'screen18'})
    cache.write_bytes(b'changed')
    with pytest.raises(ValueError,match='trajectory'):proof.validate({'operation':'screen18'})


def test_matched_rest_uses_actual_continuous_held_edge_not_old_centerline():
    import math
    spec2=importlib.util.spec_from_file_location('playback178_matched',Path(m.__file__).with_name('wardrobe_motion178_playback.py'))
    playback=importlib.util.module_from_spec(spec2);spec2.loader.exec_module(playback)
    points,faces,_,components=m.twice_wrapped_patterns(True)
    flat=playback.flat_ribbon_rest(points,points,components,matched_guide=True)
    assert flat[:1395]==points[:1395]
    for row in range(1,192):
        a=points[1395+(row-1)*13+12];b=points[1395+row*13+12]
        expected=math.dist(a,b)*1.01
        assert flat[1395+row*13][0]-flat[1395+(row-1)*13][0]==pytest.approx(expected)
    assert playback.geometry_preflight(flat,faces)['collapsed_edge_gate']=='PASS'


def test_sparse_shoulders_preserve_head_and_free_front_rear_border():
    spec2=importlib.util.spec_from_file_location('playback178_sparse',Path(m.__file__).with_name('wardrobe_motion178_playback.py'))
    playback=importlib.util.module_from_spec(spec2);spec2.loader.exec_module(playback)
    pins={i:1. for i in range(1395,3891)};pins[6]=1.
    reduced=playback.sparse_shoulder_attachments(pins)
    assert reduced[6]==1. and len(reduced)==9
    assert sorted((i-1395)//13 for i in reduced if i>=1395)==[24,24,72,72,119,119,167,167]
    assert sum(w==1. for i,w in reduced.items() if i>=1395)==4


def test_flat_head_cut_preserves_measured_arc_not_dressed_bag():
    import math
    spec2=importlib.util.spec_from_file_location('playback178_headcut',Path(m.__file__).with_name('wardrobe_motion178_playback.py'))
    playback=importlib.util.module_from_spec(spec2);spec2.loader.exec_module(playback)
    source,faces,_,_=m.dressed_head_pattern()
    flat=playback.flat_head_rest(source)
    assert len(flat)==1395 and all(p[2]==0 for p in flat)
    assert flat[30][0]==pytest.approx(sum(math.dist(source[c-1],source[c]) for c in range(1,31)))
    assert flat[-1][1]==pytest.approx(4.7)
    assert playback.geometry_preflight(flat,faces)['collapsed_edge_gate']=='PASS'
    with pytest.raises(ValueError,match='head cut'):playback.flat_head_rest(source[:-1])


def test_ordered_angular_cut_never_backtracks_and_shoulder_roll_is_bounded():
    import math
    spec2=importlib.util.spec_from_file_location('cut178',Path(m.__file__).with_name('wardrobe_motion178_cut.py'))
    cut=importlib.util.module_from_spec(spec2);spec2.loader.exec_module(cut)
    rows=[cut.route(r,12) for r in range(192)]
    assert rows[0]['theta']==0 and rows[-1]['theta']==pytest.approx(4*math.pi)
    assert all(a['theta']<b['theta'] for a,b in zip(rows,rows[1:]))
    assert all(cut.route(r,0)['z']<cut.route(r,12)['z'] for r in range(192))
    assert cut.route(24,0)['side_ease']>.7
    assert cut.route(48,0)['side_ease']<.001
    with pytest.raises(ValueError,match='cut bounds'):cut.route(192,12)


def test_gathered_shoulder_cut_does_not_start_as_horizontal_wing():
    spec2=importlib.util.spec_from_file_location('cut178_gather',Path(m.__file__).with_name('wardrobe_motion178_cut.py'))
    cut=importlib.util.module_from_spec(spec2);spec2.loader.exec_module(cut)
    assert cut.route(24,0,True)['side_ease']<.001
    assert max(cut.route(24,c,True)['side_ease'] for c in range(13))<.07
    assert cut.route(24,12,True)['z']-cut.route(24,0,True)['z']>.4
    assert cut.route(48,0,True)['z']==pytest.approx(cut.route(48,0)['z'],abs=1e-6)


def test_gathered_motion_input_is_hash_bound_and_never_overwritten(monkeypatch,tmp_path):
    source=tmp_path/'source.blend';source.write_bytes(b'fixture source')
    curved=tmp_path/'curved.npz';curved.write_bytes(b'fixture head')
    layout=tmp_path/'gathered.npz';layout.write_bytes(b'fixture cut')
    for attr,path in (('SOURCE',source),('CURVED_HEAD',curved),('GATHERED_LAYOUT',layout)):
        monkeypatch.setattr(m,attr,path);monkeypatch.setattr(m,attr+'_SHA',m.digest(path))
    monkeypatch.setattr(m,'BASE',tmp_path)
    out=m.validate({'operation':'move38'});out.mkdir()
    with pytest.raises(ValueError,match='overwrite'):m.validate({'operation':'move38'})
    layout.write_bytes(b'changed')
    with pytest.raises(ValueError,match='gathered'):m.validate({'operation':'move38'})


def test_existing_donor_warp_is_bounded_and_preserves_crown_without_new_sources():
    import math
    spec2=importlib.util.spec_from_file_location('donor178',Path(m.__file__).with_name('wardrobe_motion178_donor.py'))
    donor=importlib.util.module_from_spec(spec2);spec2.loader.exec_module(donor)
    for p in ((0,-1,2.49),(1,-1,0),(1.5,-1,-3.57),(-1.5,-1,-3.57),(0,1,0)):
        assert all(math.isfinite(v) and abs(v)<6 for v in donor.fit_point(p))
    assert donor.fit_point((0,-1,2.49))[2]==pytest.approx(2.49*.85-.70)
    with pytest.raises(ValueError,match='Bounded'):donor.fit_point((0,0,float('nan')))


def test_supported_major_cut_uses_downward_rear_route_and_narrow_crossing():
    spec2=importlib.util.spec_from_file_location('cut178_supported',Path(m.__file__).with_name('wardrobe_motion178_cut.py'))
    cut=importlib.util.module_from_spec(spec2);spec2.loader.exec_module(cut)
    assert cut.route(0,12,True,True)['z']<-2.4
    assert cut.route(0,0,True,True)['z']<-3.6
    assert max(cut.route(24,c,True,True)['side_ease'] for c in range(13))<.02
    assert all(cut.route(r,0,True,True)['z']<cut.route(r,12,True,True)['z'] for r in range(192))


@pytest.mark.parametrize('operation',['move44','move45'])
def test_hybrid_move_validates_every_read_input_and_never_overwrites(monkeypatch,tmp_path,operation):
    for attr in ('SOURCE','CURVED_HEAD','GATHERED_LAYOUT','HYBRID_LAYOUT'):
        path=tmp_path/(attr+'.fixture');path.write_bytes(attr.encode())
        monkeypatch.setattr(m,attr,path);monkeypatch.setattr(m,attr+'_SHA',m.digest(path))
    monkeypatch.setattr(m,'BASE',tmp_path)
    out=m.validate({'operation':operation});out.mkdir()
    with pytest.raises(ValueError,match='overwrite'):m.validate({'operation':operation})
    m.GATHERED_LAYOUT.write_bytes(b'changed')
    with pytest.raises(ValueError,match='gathered'):m.validate({'operation':operation})
