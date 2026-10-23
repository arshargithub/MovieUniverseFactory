"""Bounded new handler controls; not Blender or artistic qualification."""
import numpy as np
import pytest
from movie_factory.adapters.blender.nihang_rein361 import trajectory_metrics,advect,relax
from test_nihang358_rein_route import V,Box
from movie_factory.adapters.blender.nihang_beard361 import guide,refine
from movie_factory.adapters.blender.nihang_patch import validate
from movie_factory.adapters.blender.nihang_look361 import crop_bounds,outside,winding_number,seam_profile


def test_metrics_remove_shared_translation_not_interior_pop():
    base=np.column_stack((np.linspace(0,1,129),np.zeros(129),np.zeros(129)))
    paths=np.array([base+[i*.01,0,0] for i in range(4)])
    assert trajectory_metrics(paths)['maximum_residual_step']<1e-12
    paths[2,64,1]=.2
    assert trajectory_metrics(paths)['maximum_residual_step']>.19


@pytest.mark.parametrize('kind',['mounted_layers361','mounted_look361','mounted_rein361','mounted_rein361_audit','mounted_beard361'])
def test_fixed_handlers_accept_no_code_or_parameter_payload(kind):
    recipe=dict(operation='nihang_patch',frame=327,width=640,height=640,samples=8,
                edits=[dict(kind=kind,target='mounted leader')])
    validate(recipe)
    recipe['edits'][0]['code']='not allowed'
    with pytest.raises(ValueError,match='PATCH_ACTOR_FIELDS'):validate(recipe)


def test_beard_keeps_root_and_continuous_irregular_free_length():
    rows=[]
    for i,x in enumerate(np.linspace(-.065,.065,31)):
        root=np.array([x,-.08,1.72-.095])
        p=guide(root,1.72,i,'cheek')
        assert np.array_equal(root,p[0]) and np.isfinite(p).all()
        assert np.linalg.norm(np.diff(p,axis=0),axis=1).max()<.009
        rows.append(p[-1,2])
    assert max(rows)-min(rows)>.025


def test_refinement_preserves_retained_volume_without_quantized_locks():
    p=guide([.03,-.08,1.62],1.72,22,'cheek')
    q=refine(p,22)
    assert np.array_equal(q[0],p[0])
    assert np.array_equal(q[-1],p[-1])
    assert np.linalg.norm(q-p,axis=1).max()<.0045


def test_owner_advection_keeps_two_exact_contacts():
    class Translation:
        def __matmul__(self,p):return p+V(.1,.2,0)
    p=[V(t,.8,0) for t in np.linspace(0,1,129)]
    q=advect(p,Translation(),V(-.2,0,.1))
    assert (q[0]-(p[0]+V(.1,.2,0))).length<1e-12
    assert (q[-1]-(p[-1]+V(-.2,0,.1))).length<1e-12


def test_local_relaxation_never_waives_an_uncertified_segment():
    p=[V(t,.8,0) for t in np.linspace(0,1,129)]
    q,_=relax(p,Box(),lambda *args:True)
    assert (q[0]-p[0]).length==0 and (q[-1]-p[-1]).length==0
    with pytest.raises(ValueError,match='NOT_CERTIFIED'):
        relax(p,Box(),lambda *args:False)


def test_grain_uses_only_featureless_corner_in_every_projection_pair():
    offset,extent=crop_bounds()
    assert offset>=0 and offset+extent<.25


def test_closed_volume_ray_distinguishes_outside_from_inside():
    class Slab:
        def ray_cast(self,p,d,limit):
            hits=[x for x in (0.,1.) if x>p.x+1e-8]
            if not hits:return None,None,None,None
            x=min(hits);return V(x,p.y,p.z),None,0,x-p.x
    assert outside(Slab(),V(-1,0,0),V(1,0,0))
    assert not outside(Slab(),V(.5,0,0),V(1,0,0))


def test_solid_angle_independently_distinguishes_closed_volume():
    v=np.array([[0,0,0],[1,0,0],[0,1,0],[0,0,1]],dtype=float)
    tri=v[np.array([[0,2,1],[0,1,3],[0,3,2],[1,2,3]])]
    assert abs(winding_number(tri,[.1,.1,.1]))==pytest.approx(1)
    assert abs(winding_number(tri,[1,1,1]))<1e-10
    assert abs(winding_number(tri[:,::-1],[.1,.1,.1]))==pytest.approx(1)


def test_repeated_ray_hit_is_unknown_not_outside():
    class Grazing:
        def ray_cast(self,p,d,limit):return p,None,0,0
    assert outside(Grazing(),V(0,0,0),V(1,0,0)) is None


def test_below_hem_blend_never_queries_nonexistent_torso_surface():
    for height in np.linspace(.95,1.145,200):
        weight,probe=seam_profile(height)
        assert 0<=weight<=1
        if weight:assert probe>=1.095>1.075
        if height<=1.00:assert weight==0
    assert seam_profile(1.02)[0]>0 and seam_profile(1.02)[1]==1.095
    assert seam_profile(1.145)==(1,1.145)
