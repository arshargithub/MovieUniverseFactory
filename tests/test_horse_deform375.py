import pytest
from movie_factory.adapters.blender import nihang_deform375 as d,nihang_patch as p

def test_closed_readonly_skin_ownership_inspection():
 e={'kind':'mounted_horse_deform375_inspect','target':'horse'};assert d.validate(e)==e
 p.validate(dict(operation='nihang_patch',frame=367,width=432,height=432,samples=8,edits=[e]))
 for bad in [{**e,'path':'other'},{**e,'target':'rider'},{**e,'code':'run'}]:
  with pytest.raises(ValueError):d.validate(bad)
