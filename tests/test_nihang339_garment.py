import numpy as np
import pytest
from movie_factory.adapters.blender.nihang_garment import barycentric,pattern,transport

def test_barycentric_reconstructs_triangle_and_rejects_collapse():
    tri=np.array([[0.,0,0],[1.,0,0],[0.,1,0]])
    p=np.array([.2,.3,0]);w=barycentric(p,*tri)
    assert np.allclose(w@tri,p) and np.isclose(w.sum(),1)
    with pytest.raises(ValueError):barycentric(p,*np.zeros((3,3)))

def test_complete_pattern_has_sleeves_seams_and_finite_pins():
    source=np.array([(x,y,z) for z in np.linspace(.03,.52,70)
                     for x in np.linspace(-.17,.17,20) for y in (-.12,.10)])
    cuffs={'-1':[-.44,-.15,.18],'1':[.44,-.15,.18]}
    elbows={'-1':[-.32,-.04,.29],'1':[.32,-.04,.29]}
    p,faces,pins=pattern(source,cuffs,elbows,True)
    assert len(p)>3000 and np.isfinite(p).all()
    assert pins.min()>=0 and pins.max()<=1.000000001
    edges={}
    for face in faces:
        assert len(set(face))==4
        for a,b in zip(face,face[1:]+face[:1]):
            edge=tuple(sorted((a,b)));edges[edge]=edges.get(edge,0)+1
    assert max(edges.values())==2
    # An open neckline, waist and two cuffs are intended; no disconnected panels.
    adjacency={i:set() for i in range(len(p))}
    for a,b in edges:adjacency[a].add(b);adjacency[b].add(a)
    visited=set();todo=[0]
    while todo:
        i=todo.pop()
        if i in visited:continue
        visited.add(i);todo.extend(adjacency[i]-visited)
    assert len(visited)==len(p)

def test_bent_arm_accepts_short_wrist_to_shoulder_distance():
    source=np.array([(x,y,z) for z in np.linspace(.03,.52,70)
                     for x in np.linspace(-.17,.17,20) for y in (-.12,.10)])
    cuffs={'-1':[-.27,-.02,.32],'1':[.27,-.02,.32]}
    elbows={'-1':[-.4,-.04,.19],'1':[.4,-.04,.19]}
    p,faces,pins=pattern(source,cuffs,elbows,True)
    assert np.isfinite(p).all() and pins.max()<=1

def test_parallel_transport_remains_orthogonal_through_bend():
    a=np.array([1.,0,0]);v=np.array([0.,0,1])
    for theta in np.linspace(0,2.6,30):
        b=np.array([np.cos(theta),0,np.sin(theta)])
        v=transport(v,a,b);a=b
        assert np.isclose(np.dot(v,b),0,atol=1e-9)
        assert np.isclose(np.linalg.norm(v),1)
