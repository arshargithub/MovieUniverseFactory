import numpy as np
from movie_factory.adapters.blender.nihang_garment import sleeve_axis,outward_triangles,pattern

def test_straight_rest_sleeve_has_linear_arc_distance():
    a=np.array([0.,0,0]);b=np.array([.25,0,0]);c=np.array([.5,0,0])
    for t in np.linspace(0,1,101):
        p,n=sleeve_axis(a,b,c,t)
        assert np.allclose(p,[t*.5,0,0])
        assert np.allclose(n,[1,0,0])

def test_raised_elbow_cannot_overshoot_control_triangle():
    a=np.array([.205,0,.42]);b=np.array([.3968,-.0055,.2654]);c=np.array([.35,-.03,.5005])
    previous=None
    for t in np.linspace(0,1,501):
        p,n=sleeve_axis(a,b,c,t)
        assert p[0]<=max(a[0],b[0],c[0])+1e-9
        assert p[2]>=min(a[2],b[2],c[2])-1e-9
        assert np.isclose(np.linalg.norm(n),1)
        if previous is not None:assert np.linalg.norm(p-previous)<.002
        previous=p

def test_inward_collision_proxy_is_corrected_without_mutating_source():
    points=[];tri=[]
    for y in [-.15,.10]:
        for z in np.linspace(.15,.32,15):
            i=len(points);points.extend([[-.05,y,z],[.05,y,z],[0,y,z+.01]])
            tri.append([i,i+1,i+2] if y>.0 else [i+2,i+1,i])
    points=np.array(points);tri=np.array(tri);original=tri.copy()
    corrected,vote=outward_triangles(points,tri,True)
    assert vote<-.9 and np.array_equal(tri,original)
    corrected2,vote2=outward_triangles(points,corrected,True)
    assert vote2>.9 and np.array_equal(corrected2,corrected)

def test_standing_pattern_preserves_its_own_torso_height():
    source=np.array([(x,y,z) for z in np.linspace(.85,1.45,90)
                    for x in np.linspace(-.17,.17,20) for y in (-.1,.12)])
    points,faces,pins=pattern(source,{'-1':[-.275,.05,1.03],'1':[.295,0,.98]},
                             {'-1':[-.24,.02,1.165],'1':[.243,.012,1.157]},False)
    assert points[:2178,2].max()>1.395
    assert points[:2178,2].min()==.885
