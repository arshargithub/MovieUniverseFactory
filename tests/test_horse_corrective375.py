import numpy as np
import pytest
from movie_factory.adapters.blender import nihang_corrective375 as m,nihang_patch


def test_closed_phases_and_no_code_or_parameters():
 for phase in ('body','coat'):
  good=dict(kind='mounted_horse_corrective375',target='horse',phase=phase);m.validate(good);nihang_patch.validate(dict(operation='nihang_patch',frame=367,width=432,height=432,samples=8,edits=[good]))
  for bad in ({**good,'target':'leader'},{**good,'phase':'x'},{**good,'code':'x'},{**good,'iterations':500}):
   with pytest.raises(ValueError):m.validate(bad)


def test_support_excludes_back_legs_high_neck_and_has_smooth_boundary():
 pts=np.array([[0,-.8,1.4],[0,0,1.4],[0,-.8,.7],[0,-.8,2.1],[0,-.28,1.4],[0,-.28001,1.4]])
 w=m.support(pts);assert w[0]==1 and np.all(w[1:5]==0) and 0<w[5]<1e-7
 with pytest.raises(ValueError):m.support([[np.nan,0,0]])
