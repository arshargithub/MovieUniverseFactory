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
        'wardrobe185_cut_solve':('run',),'wardrobe185_rest_unit':('run',),
        'wardrobe185_intersections':('run',),
    }.items():
        fake=types.ModuleType(name)
        for method in methods:setattr(fake,method,record)
        monkeypatch.setitem(sys.modules,name,fake)
    monkeypatch.setattr(sys,'argv',['test','--',str(job)])
    module.main()
    assert calls==[operation]
