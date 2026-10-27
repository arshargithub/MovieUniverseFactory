"""Uniform cage controls; do not qualify anatomy."""
import sys
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import anatomy386_grid189 as m

def test_grid_is_complete_positive_volume_without_slivers():
 p,t=m.regular(np.zeros(3),np.ones(3),spacing=.25);D=np.transpose(p[t[:,1:]]-p[t[:,0,None]],(0,2,1));v=abs(np.linalg.det(D))/6
 assert abs(v.sum()-1)<1e-10 and v.min()>0 and np.linalg.cond(D).max()<5
 faces=np.sort(np.concatenate([t[:,[0,1,2]],t[:,[0,1,3]],t[:,[0,2,3]],t[:,[1,2,3]]]),axis=1);_,count=np.unique(faces,axis=0,return_counts=True)
 assert count.max()==2 and set(count)=={1,2}
