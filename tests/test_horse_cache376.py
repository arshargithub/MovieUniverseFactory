import numpy as np
import pytest
from movie_factory.adapters.blender import nihang_cache376 as m,nihang_patch


def test_closed_cache_and_continuous_amount():
 e=dict(kind='mounted_horse_cache376',target='horse');m.validate(e);nihang_patch.validate(dict(operation='nihang_patch',frame=367,width=432,height=432,samples=8,edits=[e]))
 for bad in ({**e,'target':'leader'},{**e,'frames':[1]},{**e,'code':'x'}):
  with pytest.raises(ValueError):m.validate(bad)
 assert m.amplitude(276)==m.amplitude(293)==m.amplitude(367)==0
 assert m.amplitude(333)==m.amplitude(339)==1
 for f in np.linspace(276,367,183):assert 0<=m.amplitude(f)<=1


def test_regularized_displacement_keeps_outside_support_exact():
 p=np.array([[0,-.8,.5],[0,-.8,1.4],[0,-.8,2.1]],dtype=float);edges=np.array([[0,1],[1,2]]);d,mask=m.target(p,p,edges,np.ones(3),339);assert not d[[0,2]].any() and np.isfinite(d).all()
 d,_=m.target(p,p,edges,np.ones(3),283);assert not d.any()
