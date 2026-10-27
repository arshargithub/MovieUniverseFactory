"""Closed surface/view boundary and real dispatch; not artistic qualification."""
import pytest
from movie_factory.adapters.blender import warhorse384 as w, nihang_patch as p, nihang_control as c


def test_closed_surface():
    edit = dict(kind='warhorse_surface384', target='warhorse383')
    w.validate(edit)
    p.validate(dict(operation='nihang_patch', frame=283, width=640, height=640, samples=8, edits=[edit]))
    for key in ['code', 'path', 'color', 'mask']:
        with pytest.raises(ValueError): w.validate({**edit, key: 'untrusted'})
    with pytest.raises(ValueError): w.validate({**edit, 'target': 'horse'})


def test_real_dispatch(monkeypatch, tmp_path):
    sentinel = object()
    monkeypatch.setattr(w, 'surface', lambda bpy, out: sentinel)
    assert w.run(None, tmp_path, dict(kind='warhorse_surface384', target='warhorse383')) is sentinel


@pytest.mark.parametrize('view', sorted(w.VIEWS))
def test_evidence_views(view):
    c.validate(dict(operation='nihang_frames', frame=283, frames=[283,333,339],
                    view=view, width=640, height=640, samples=8))


def test_no_recipe_view_injection():
    with pytest.raises(ValueError): c.validate(dict(operation='nihang_frames', frame=283,
        frames=[283], view='warhorse_head_evil384', width=640, height=640, samples=8))


def test_bounded_head_relaxation():
    points=[[0,0,0],[1,0,0],[1,1,1],[0,1,0]]
    result=w.relax(points,[{1,3},{0,2},{1,3},{0,2}],[0,0,1,0])
    assert result[0]==points[0] and result[1]==points[1] and result[3]==points[3]
    assert result[2][2]<1
    assert sum((a-b)**2 for a,b in zip(result[2],points[2])) <= .045**2+1e-12


def test_headblend_dispatch(monkeypatch,tmp_path):
    calls=[]
    monkeypatch.setattr(w,'headblend',lambda bpy,out:calls.append('head'))
    monkeypatch.setattr(w,'surface',lambda bpy,out:calls.append('surface'))
    w.run(None,tmp_path,dict(kind='warhorse_headblend384',target='warhorse383'))
    assert calls==['head','surface']


def test_rebuild_closed_dispatch(monkeypatch,tmp_path):
    calls=[]
    for name in ['headrebuild','surface','skin_material']:
        monkeypatch.setattr(w,name,lambda *args,n=name:calls.append(n))
    w.run(None,tmp_path,dict(kind='warhorse_headrebuild384',target='warhorse383'))
    assert calls==['headrebuild','surface','skin_material']


def test_graft_closed_dispatch(monkeypatch,tmp_path):
    calls=[]
    monkeypatch.setattr(w,'graft',lambda *args:calls.append('graft'))
    monkeypatch.setattr(w,'surface',lambda *args:calls.append('surface'))
    edit=dict(kind='warhorse_headgraft384',target='warhorse383')
    w.run(None,tmp_path,edit)
    assert calls==['graft','surface']
    with pytest.raises(ValueError):w.validate({**edit,'source_path':'elsewhere'})


def test_reused_head_maps_chain_and_eye_owners():
    from movie_factory.adapters.blender.warhorse_graft384 import mapped_group
    assert mapped_group('DEF-jaw.001')=='jaw'
    assert mapped_group('DEF-ear.001.L')=='ear_L'
    assert mapped_group('DEF-eye.R')=='head'
    assert mapped_group('DEF-neck.004')=='neck_03'


def test_component_extraction_uses_complete_owners():
    from movie_factory.adapters.blender.warhorse_graft384 import component_member
    assert component_member({'DEF-ear.L':1.})
    assert component_member({'DEF-jaw.001':1.})
    assert component_member({'DEF-neck.004':.9,'DEF-neck.003':.1})
    assert not component_member({'DEF-spine.003':1.})
    assert not component_member({'DEF-neck.001':1.})


def test_boundary_stitch_shares_both_unequal_loops():
    import math
    from movie_factory.adapters.blender.warhorse_join384 import boundary,stitch
    points=[(math.cos(i*math.tau/8),math.sin(i*math.tau/8),0) for i in range(8)]
    faces=[[i,(i+1)%8,(i+1)%8+8,i+8] for i in range(8)]
    points += [(x,y,-1) for x,y,z in points]
    a,components=boundary(points,faces,(0,0,0),(0,0,1));assert len(a)==8
    b=[]
    for i in range(12):b.append(len(points));points.append((.8*math.cos(i*math.tau/12),.8*math.sin(i*math.tau/12),.12))
    bridge,b=stitch(points,a,b)
    assert len(bridge)==20
    assert {i for f in bridge for i in f}==set(a+b)
    assert all(len(set(f))==3 for f in bridge)
    from collections import Counter
    counts=Counter(tuple(sorted(e)) for f in bridge for e in zip(f,f[1:]+f[:1]))
    expected={tuple(sorted(e)) for ring in [a,b] for e in zip(ring,ring[1:]+ring[:1])}
    assert {e for e,v in counts.items() if v==1}==expected


def test_complete_cut_loop_is_not_clipped_by_old_search_window():
    import math
    from movie_factory.adapters.blender.warhorse_join384 import boundary
    ring=[(math.cos(i*math.tau/8),math.sin(i*math.tau/8),.212 if i==0 else 0.) for i in range(8)]
    points=ring+[(x,y,-1) for x,y,z in ring]
    faces=[[i,(i+1)%8,(i+1)%8+8,i+8] for i in range(8)]
    loop,_=boundary(points,faces,(0,0,0),(0,0,1))
    assert len(loop)==8 and 0 in loop
