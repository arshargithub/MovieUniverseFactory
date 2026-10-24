import pytest
import numpy as np
from movie_factory.adapters.blender import nihang_padsolve370 as p, nihang_padcontact369 as transport


def test_exact_envelope_transport():
    transport.validate(dict(kind='mounted_padcontact369', target='fitted saddle blanket292', mode='envelope'))
    with pytest.raises(ValueError):
        transport.validate(dict(kind='mounted_padcontact369', target='horse', mode='envelope'))
    with pytest.raises(ValueError):
        transport.validate(dict(kind='mounted_padcontact369', target='fitted saddle blanket292', mode='envelope', code='anything'))


def test_semantic_radial_directions():
    assert p.radial((0, 0, 1), 0) == (0., 0., 1.)
    for x in (-.7, -.2, .2, .7):
        d = p.radial((x, 10, -3), 0)
        assert x*d[0] > 0 and d[1] == 0 and d[2] > 0


def test_outside_vertices_can_still_have_an_inside_face():
    # A known convex-surface counterexample: vertex-only contact is insufficient.
    points=np.array([[.6,0,.85],[-.3,.52,.85],[-.3,-.52,.85]])
    assert np.all(np.linalg.norm(points,axis=1)>1.)
    assert np.linalg.norm(points.mean(0))<1.
    def project(p):
        n=np.linalg.norm(p)
        return p if n>=1.012 else p*1.012/n
    solved=p.face_contacts(points,[(0,1,2)],project)
    assert np.linalg.norm(solved.mean(0))>=1.011
    assert np.all(np.linalg.norm(solved,axis=1)>1.)
    clear=points+np.array([0,0,1.])
    assert np.array_equal(p.face_contacts(clear,[(0,1,2)],project),clear)


def test_final_solidified_constraints_share_source_support_without_double_count():
    points=np.zeros((4,3))
    # A final rim triangle can reference two copies of a source vertex.
    # Its correction must move that source once, keeping unconstrained support.
    moved=p.apply_contact_moves(points,[((0,0,1),(0,0,.03)),((1,2),(0,0,.01))])
    assert moved[0,2]==pytest.approx(.03)
    assert moved[1,2]==pytest.approx(.02)
    assert moved[2,2]==pytest.approx(.01)
    assert np.array_equal(moved[3],points[3])
    assert np.array_equal(points,np.zeros((4,3)))
