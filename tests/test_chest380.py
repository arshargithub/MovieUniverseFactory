import numpy as np
import pytest
from movie_factory.adapters.blender import nihang_chest380 as h,nihang_patch

def test_central_and_lateral_ownership_have_no_stationary_pectoral_island():
 names=['DEF-breast.L','DEF-breast.R','DEF-upper_arm.L','DEF-upper_arm.R','body','DEF-forearm.L']
 w=np.array([[.5,.5,0,0,1,0],[.8,.1,.1,0,1,0],[0,0,0,0,1,1]])
 q=h.ownership(w,names)
 assert np.allclose(q.sum(1),w.sum(1))
 assert np.array_equal(q[:,4:],w[:,4:]) and np.array_equal(q[2],w[2])
 assert np.allclose(q[0,:4],[0,0,.5,.5])
 assert np.allclose(q[1,:4],[0,0,.9,.1])

def test_closed_handler_and_shared_registration():
 e={'kind':'mounted_horse_chest380','target':'horse','restoration':.5};h.validate(e)
 nihang_patch.validate(dict(operation='nihang_patch',frame=367,width=640,height=640,samples=8,edits=[e]))
 for bad in [dict(e,code='x'),dict(e,target='rider'),dict(e,strength=1),dict(e,restoration=float('nan'))]:
  with pytest.raises(ValueError):h.validate(bad)
 with pytest.raises(ValueError):h.ownership(np.array([[np.nan]]),['x'])
