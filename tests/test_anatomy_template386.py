"""Geometric/deformation controls, not artistic anatomy tests."""
import importlib.util
from pathlib import Path
import numpy as np
spec=importlib.util.spec_from_file_location('template183',Path(__file__).resolve().parents[1]/'scripts/anatomy386_template183.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)


def test_closest_surface_interior_edge_and_corner():
    v=np.array([[0.,0,0],[1.,0,0],[0.,1,0]]);f=np.array([[0,1,2]])
    p=np.array([[.2,.2,1],[.6,.6,0],[-1,-1,0]])
    q,d=m.closest(p,v,f)
    assert np.allclose(q,[[.2,.2,0],[.5,.5,0],[0,0,0]])
    assert np.allclose(d,[1,np.sqrt(.02),np.sqrt(2)])


def test_one_ring_transfer_preserves_a_known_rigid_rotation():
    p=np.array([[0.,0,0],[1.,0,0],[0.,1,0],[0.,0,1]])
    e=np.array([[0,1],[0,2],[0,3],[1,2],[1,3],[2,3]])
    Q=np.array([[0.,-1,0],[1.,0,0],[0,0,1]])
    R=m.rotations(p,p@Q.T+np.array([2,3,4]),e,np.arange(4),4)
    assert np.allclose(R,Q,atol=1e-8)
    assert np.allclose(m.rotations(p,p,e,np.arange(4),4),np.eye(3))
