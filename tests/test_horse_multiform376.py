import pytest
from movie_factory.adapters.blender import nihang_multiform376 as m,nihang_patch


def test_closed_original_source_multiform_contract():
 e=dict(kind='mounted_horse_multiform376',target='horse');m.validate(e);nihang_patch.validate(dict(operation='nihang_patch',frame=367,width=432,height=432,samples=8,edits=[e]))
 for bad in ({**e,'code':'x'},{**e,'target':'leader'},{**e,'frame':339}):
  with pytest.raises(ValueError):m.validate(bad)


def test_envelopes_have_distinct_pose_ownership_and_stance_zero():
 rows=m.envelopes();assert set(rows)=={333,339,346}
 for f,curve in rows.items():
  vals=dict(curve);assert vals[f]==1 and vals[276]==vals[367]==0 and all(0<=v<=1 for v in vals.values())
  for other in rows:
   if other!=f:assert vals[other]==0
