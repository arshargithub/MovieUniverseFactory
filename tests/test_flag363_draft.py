"""Finite real handler geometry controls; no solver or artistic approval."""
import numpy as np
from movie_factory.adapters.blender.nihang_flag363 import topology
def test_actual_flag_nondegenerate_triangle_three_ties_and_pole_clearance():
 points,faces,pins=topology();a=np.array(points)
 assert len(pins)==3 and all(a[i,0]==.032 and a[i,1]==0 for i in pins)
 assert len(set(map(tuple,points)))==len(points)
 assert min(np.linalg.norm(a[:,:2],axis=1))>.018+.002+.001
 for f in faces:
  p,q,r=a[list(f)];assert np.linalg.norm(np.cross(q-p,r-p))>1e-6


def test_collider_faces_have_conditioned_aspect_and_outward_winding():
 from movie_factory.adapters.blender.nihang_flag363 import pole_topology
 p,f=pole_topology();a=np.asarray(p);assert len(p)==660 and len(f)==642
 for face in f[:-2]:
  q=a[list(face)];edges=np.linalg.norm(q-np.roll(q,1,axis=0),axis=1);assert max(edges)/min(edges)<4.2
  normal=np.cross(q[1]-q[0],q[2]-q[0]);center=q.mean(axis=0);assert np.dot(normal[:2],center[:2])>0
