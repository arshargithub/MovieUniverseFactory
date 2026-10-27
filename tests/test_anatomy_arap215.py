import sys
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from anatomy386_arap215 import rotations,oriented_goal

def test_local_rotations_recover_rigid_motion_without_reflection():
    r=np.array([[0.,0,0],[1,0,0],[0,1,0],[0,0,1]])
    e=np.array([[0,1],[0,2],[0,3],[1,2],[1,3],[2,3]])
    R=np.array([[0.,-1,0],[1,0,0],[0,0,1]])
    current=r@R.T+np.array([3.,2,1])
    fit=rotations(r,current,e,np.arange(4))
    assert np.allclose(fit,R[None],atol=1e-8)
    assert np.allclose(np.linalg.det(fit),1)

def test_correspondence_rejects_closer_oppositely_facing_branch():
    v=np.array([[0.,0,0],[1,0,0],[0,1,0],[0,0,.1],[1,0,.1],[0,1,.1]])
    f=np.array([[0,1,2],[3,5,4]])
    goal,d,valid=oriented_goal(np.array([[.2,.2,.09]]),np.array([[0.,0,1]]),v,f)
    assert valid.tolist()==[True]
    assert abs(goal[0,2])<1e-9
    assert abs(d[0]-.09)<1e-9
