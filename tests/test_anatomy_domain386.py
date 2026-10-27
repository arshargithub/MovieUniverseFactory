"""Frozen ownership cannot be evaded with an arbitrary geometric edit mask."""
import numpy as np
import pytest
from movie_factory.adapters.blender.anatomy_domain386 import foreleg_ownership,preserve_forelegs

def test_forearm_and_downstream_are_protected_even_when_mask_would_include_them():
 names=['body','DEF-forearm.L','DEF-forearm.R','DEF-forearm.R.001','DEF-f_hoof.L'];w=np.array([[1,0,0,0,0],[1,.8,0,0,0],[1,0,.2,.3,0],[1,0,0,0,.9]])
 assert np.allclose(foreleg_ownership(w,names),[0,.8,.5,.9])
 a=np.zeros((3,4,3));b=a.copy();b[:,0,0]=.1
 assert preserve_forelegs(a,b,w,names)['protected_vertices']==3
 b[:,2,0]=.001
 with pytest.raises(ValueError,match='FROZEN_FORELEG_DRIFT'):preserve_forelegs(a,b,w,names)

def test_unknown_rig_ownership_fails_closed():
 with pytest.raises(ValueError,match='MISSING_FOREARM'):foreleg_ownership(np.zeros((2,1)),['body'])

def test_main_skin_excludes_disconnected_cards():
 from movie_factory.adapters.blender.anatomy_domain386 import main_skin
 assert main_skin(np.array([[0,1],[1,2],[2,3],[4,5]]),7).tolist()==[True,True,True,True,False,False,False]
