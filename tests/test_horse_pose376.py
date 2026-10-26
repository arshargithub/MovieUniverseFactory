import numpy as np
import pytest
from movie_factory.adapters.blender import nihang_pose376 as m,nihang_patch


def test_closed_inspect():
 e=dict(kind='mounted_horse_pose376_inspect',target='horse');m.validate(e);nihang_patch.validate(dict(operation='nihang_patch',frame=367,width=432,height=432,samples=8,edits=[e]))
 for bad in ({**e,'target':'leader'},{**e,'code':'x'},{**e,'frame':338}):
  with pytest.raises(ValueError):m.validate(bad)


def test_posed_control_keeps_endpoints_and_zero_iterations():
 p=np.array([[0,-.8,.5],[0,-.8,1.4],[0,-.8,2.1]],dtype=float);edges=np.array([[0,1],[1,2]])
 delta,_=m.fair(p,p,edges,0);assert not delta.any()
 delta,mask=m.fair(p,p,edges,1);assert mask[0]==mask[2]==0 and mask[1]==1;assert not delta[[0,2]].any();assert np.isfinite(delta).all()


def test_corrective_target_is_finite_local_and_closed():
 e=dict(kind='mounted_horse_pose376_correct',target='horse');m.validate(e);nihang_patch.validate(dict(operation='nihang_patch',frame=367,width=432,height=432,samples=8,edits=[e]))
 p=np.array([[0,-.8,.5],[0,-.8,1.4],[0,-.8,2.1]],dtype=float);d,mask=m.posed_target(p,p,np.array([[0,1],[1,2]]),np.array([1.,1.,1.]));assert not d[[0,2]].any() and d[1,1]>0 and np.isfinite(d).all()
