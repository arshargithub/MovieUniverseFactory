import sys
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from anatomy386_surface_review import crossing,pairs_for

def test_proper_crossing_and_disjoint_triangles():
 a=np.array([[[0.,0,0],[1,0,0],[0,1,0]]]);b=np.array([[[.2,.2,-1],[.2,.2,1],[.7,.2,.2]]])
 assert crossing(a,b).tolist()==[True]
 assert crossing(a,b+np.array([4,0,0])).tolist()==[False]

def test_rigid_normal_rotation_is_not_a_surface_crossing():
 p=np.array([[0.,0,0],[1,0,0],[0,1,0],[0,0,1]]);f=np.array([[0,2,1],[0,1,3],[0,3,2],[1,2,3]])
 R=np.diag([1.,-1,-1]);new=p@R.T
 oldnormal=np.cross(p[1]-p[0],p[2]-p[0]);newnormal=np.cross(new[1]-new[0],new[2]-new[0]);assert oldnormal@newnormal<0
 assert len(pairs_for(new,f,np.ones(4,dtype=bool)))==0
