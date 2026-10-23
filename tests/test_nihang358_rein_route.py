"""Deterministic path controls; not artistic or Blender mesh qualification."""
import math
import pytest
from movie_factory.adapters.blender.nihang_rein358 import surface_route, visible


class V:
    def __init__(self,x,y,z):self.x,self.y,self.z=x,y,z
    def __add__(self,b):return V(self.x+b.x,self.y+b.y,self.z+b.z)
    def __sub__(self,b):return V(self.x-b.x,self.y-b.y,self.z-b.z)
    def __mul__(self,s):return V(self.x*s,self.y*s,self.z*s)
    __rmul__=__mul__
    @property
    def length_squared(self):return self.dot(self)
    @property
    def length(self):return math.sqrt(self.length_squared)
    def dot(self,b):return self.x*b.x+self.y*b.y+self.z*b.z
    def normalized(self):return self*(1/self.length)
    def lerp(self,b,t):return self*(1-t)+b*t
    def copy(self):return V(self.x,self.y,self.z)


class Box:
    """Closed half-metre cube exposing the two BVH methods used by routing."""
    def find_nearest(self,p):
        coords=[p.x,p.y,p.z];inside=all(abs(x)<=.5 for x in coords)
        q=[max(-.5,min(.5,x)) for x in coords]
        if inside:
            axis=max(range(3),key=lambda i:abs(coords[i]));q[axis]=.5 if coords[axis]>=0 else -.5
        else:
            axis=max(range(3),key=lambda i:abs(coords[i])-abs(q[i]))
        normal=[0.,0.,0.];normal[axis]=1 if q[axis]>=0 else -1
        hit=V(*q);return hit,V(*normal),0,(p-hit).length
    def ray_cast(self,a,d,length):
        lo,hi=0.,length
        for x,v in zip((a.x,a.y,a.z),(d.x,d.y,d.z)):
            if abs(v)<1e-10:
                if abs(x)>.5:return None,None,None,None
                continue
            q=sorted(((-.5-x)/v,(.5-x)/v));lo=max(lo,q[0]);hi=min(hi,q[1])
            if lo>hi:return None,None,None,None
        if lo<=length:return a+d*lo,None,0,lo
        return None,None,None,None


def cube():
    verts=[V(x,y,z) for x in (-.5,.5) for y in (-.5,.5) for z in (-.5,.5)]
    edges=[(i,j) for i,a in enumerate(verts) for j,b in enumerate(verts) if i<j and sum(x!=y for x,y in zip((a.x,a.y,a.z),(b.x,b.y,b.z)))==1]
    return verts,[v.normalized() for v in verts],edges


def test_straight_chord_through_closed_surface_is_rejected():
    assert not visible(Box(),V(-1,0,0),V(1,0,0))


def test_exterior_route_retains_contacts_and_does_not_cut_corners():
    a,b=V(-1.2,0,.1),V(1.2,0,.1);vertices,normals,edges=cube()
    p=surface_route(a,b,Box(),vertices,normals,edges,{})
    assert len(p)==129
    assert (p[0]-a).length==0 and (p[-1]-b).length==0
    assert all(visible(Box(),x,y,.006) for x,y in zip(p,p[1:]))


def test_same_frame_cache_does_not_reuse_other_rein_endpoints():
    vertices,normals,edges=cube();cache={}
    surface_route(V(-1.2,0,.1),V(1.2,0,.1),Box(),vertices,normals,edges,cache)
    a,b=V(-1.2,.08,.1),V(1.2,.1,.1)
    p=surface_route(a,b,Box(),vertices,normals,edges,cache)
    assert (p[0]-a).length==0 and (p[-1]-b).length==0
    assert all(visible(Box(),x,y,.006) for x,y in zip(p,p[1:]))


def test_sparse_quarter_samples_cannot_certify_a_narrow_near_miss():
    class NarrowObstacle:
        center=.375
        def ray_cast(self,*args):return None,None,None,None
        def find_nearest(self,p):
            # Cross-section of a small sphere close to, but not intersecting,
            # the centreline. The7mm radius clearance fails between probes.
            center=V(self.center,.010,0);d=p-center;n=d.normalized()
            hit=center+n*.004
            return hit,n,0,(p-hit).length
    surface=NarrowObstacle();a,b=V(0,0,0),V(1,0,0)
    assert all((a.lerp(b,u)-surface.find_nearest(a.lerp(b,u))[0]).dot(surface.find_nearest(a.lerp(b,u))[1])>.007 for u in (.25,.5,.75))
    assert not visible(surface,a,b,.007)
