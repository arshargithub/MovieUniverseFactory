"""Volumetric solver controls; not equine anatomy or visual acceptance."""
import importlib.util
from pathlib import Path
import numpy as np
s=importlib.util.spec_from_file_location('volume185',Path(__file__).resolve().parents[1]/'scripts/anatomy386_volume185.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)


def test_closed_cube_parity_inside_outside():
    v=np.array([[0,0,0],[1,0,0],[1,1,0],[0,1,0],[0,0,1],[1,0,1],[1,1,1],[0,1,1]],dtype=float)
    f=np.array([[0,2,1],[0,3,2],[4,5,6],[4,6,7],[0,1,5],[0,5,4],[1,2,6],[1,6,5],[2,3,7],[2,7,6],[3,0,4],[3,4,7]])
    assert m.inside(np.array([[.4,.2,.3],[1.4,.2,.3],[-.4,.2,.3],[.2,1.2,.3]]),v[f]).tolist()==[True,False,False,False]


def test_volumetric_identity_and_rigid_boundary_preserve_volume():
    p=np.array([[0.,0,0],[1,0,0],[0,1,0],[0,0,1],[.25,.25,.25]])
    t=np.array([[0,1,2,4],[0,1,4,3],[0,4,2,3],[4,1,2,3]])
    fixed=np.arange(4);S=m.system(p,t,fixed)
    x,d=m.solve(p,t,S,p[fixed]);assert np.allclose(x,p) and abs(d['volume_ratio']-1)<1e-8
    R=np.array([[0.,-1,0],[1,0,0],[0,0,1]]);expected=p@R.T+[2,3,4]
    x,d=m.solve(p,t,S,expected[fixed],initial=expected)
    assert np.allclose(x,expected,atol=1e-8) and d['constraint_error']==0
    assert abs(d['min_jacobian']-1)<1e-8 and abs(d['max_jacobian']-1)<1e-8
