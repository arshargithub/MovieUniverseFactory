import pytest
from movie_factory.adapters.blender import nihang_patch as p,nihang_control as c,nihang_form374 as f

def test_only_closed_readonly_export_shape():
 e={'kind':'mounted_horseform374_inspect','target':'horse'};f.validate(e)
 p.validate(dict(operation='nihang_patch',frame=367,width=576,height=576,samples=8,edits=[e]))
 for bad in [{**e,'code':'run'},{**e,'target':'other'},{**e,'path':'file'}]:
  with pytest.raises(ValueError):f.validate(bad)

def test_form_camera_frame_anchor_and_fixed_views():
 for view in ['horse_form_front374','horse_form_side374','horse_form_reverse374']:
  r=dict(operation='nihang_frames',frame=367,frames=[283,333,346,367],view=view,width=576,height=576,samples=8)
  c.validate(r)
  with pytest.raises(ValueError):c.validate({**r,'frames':[283,333,346]})
 with pytest.raises(ValueError):c.validate({**r,'view':'arbitrary'})
