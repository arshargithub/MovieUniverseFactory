import sys
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from anatomy386_graft390 import recover_polygons,boundary_loops,zipper,sample_ring,harmonic

def test_recovers_quad_without_changing_true_diagonal_topology():
    tris=np.array([[0,1,2],[0,2,3]]);edges=np.array([[0,1],[1,2],[2,3],[3,0]])
    p,m=recover_polygons(tris,edges);assert len(p)==1 and list(p[0])==[0,1,2,3] and m==[[0,1]]
    p,_=recover_polygons(tris,np.vstack([edges,[0,2]]));assert len(p)==2

def test_constant_weights_sample_on_geometric_arclength():
    points=np.array([[1.,0],[0,1],[-1,0],[0,-1]])
    w=np.tile([.2,.8],(4,1));a=sample_ring(w,np.arange(8)/8,geometry=points)
    np.testing.assert_allclose(a,np.tile([.2,.8],(8,1)))

def test_zipper_has_expected_two_boundaries_and_no_duplicate_triangles():
    s=np.array([[1.,0,0],[0,1,0],[-1,0,0],[0,-1,0]])
    d=np.array([[.8,0,.2],[0,.8,.2],[-.8,0,.2],[0,-.8,.2]])
    f=zipper(np.arange(4),np.arange(4,8),s,d);assert len(f)==8
    loops=boundary_loops(list(f));assert sorted(map(len,loops))==[4,4]
    assert len({tuple(sorted(t)) for t in f})==8

def test_harmonic_nonnegative_partition_and_exact_boundary():
    v=np.zeros((5,3));edges=np.array([[0,4],[1,4],[2,4],[3,4],[0,1],[1,2],[2,3],[3,0]])
    w=harmonic(v,edges,np.arange(4),np.array([[1.,0],[1,0],[0,1],[0,1]]))
    np.testing.assert_allclose(w[4],[.5,.5]);assert w.min()>=0;np.testing.assert_allclose(w.sum(1),1)


def test_collar_control_prevents_interior_row_folding_across_cut():
    from anatomy386_graft390 import collar_controls
    ring=np.array([[1.,0,0],[0,1,0],[-1,0,0],[0,-1,0]])
    rest=np.vstack([ring,ring+[0,0,1]])
    edges=np.array([[0,1],[1,2],[2,3],[3,0],[4,5],[5,6],[6,7],[7,4],[0,4],[1,5],[2,6],[3,7]])
    initial=rest.copy();initial[4:,2]=-.2
    ids,p=collar_controls(rest,initial,edges,{'leg':np.arange(4)},{'leg':(np.array([0.,0,-1.]),0.)})
    assert list(ids)==[4,5,6,7];np.testing.assert_allclose(p[:,2],1.)
    np.testing.assert_allclose(p[:,:2],rest[ids,:2])


def test_reference_separation_axis_proves_disjoint_patches():
    import pytest
    from anatomy386_graft390 import separating_axis
    a=np.array([[0.,0,0],[1,0,0],[0,1,0]]);b=a+[0,0,.1]
    gap,n=separating_axis(a,b);assert gap>.099
    assert (b@n).min()>(a@n).max()
    with pytest.raises(ValueError,match='NO_REFERENCE_SEPARATION'):separating_axis(a,a)


def test_contact_qp_keeps_pins_and_separates_without_flattening(monkeypatch):
    import anatomy386_graft390 as g
    # The two faces overlap in the candidate; reference puts B clearly above A.
    a=np.array([[0.,0,0],[.01,0,0],[0,.01,0]])
    reference=np.vstack([a,a+[0,0,.01],[.02,.02,0]])
    candidate=reference.copy();candidate[3:6,2]=-.001
    edges=np.array([[0,1],[1,2],[2,0],[3,4],[4,5],[5,3],[0,6],[3,6]])
    faces=np.array([[0,1,2],[3,4,5]])
    monkeypatch.setattr(g,'crossing_pairs',lambda *args:{(0,1)})
    target,audit=g.contact_separation(candidate,reference,faces,edges,np.array([6]))
    np.testing.assert_array_equal(target[6],candidate[6]);assert audit['max_delta']<.002
    n=np.array(audit['normal']);assert (target[3:6]@n).min()>(target[:3]@n).max()
