import copy
import pytest
from movie_factory.adapters.blender.demo_reuse import validate, BASE_SHA, OUTPUT

def valid():
 return {'mode':'demo_reuse','output_dir':str(OUTPUT/'smoke'),'profile':{'source_sha256':BASE_SHA,'start':144,'duration_frames':72,'offset_start':[10,0,2],'offset_end':[10,0,2],'target_offset':[0,0,0],'lens_mm':40,'operation':'smoke'}}

def test_normal():assert validate(valid())[1]['duration_frames']==72

@pytest.mark.parametrize('change',[
 {'start':True},{'duration_frames':121},{'start':550},{'source_sha256':'wrong'},
 {'lens_mm':float('nan')},{'offset_end':[0,0,0]}, {'python':'print(1)'},
 {'offset_start':[-10,0,0],'offset_end':[10,0,0]},
])
def test_bad_profile(change):
 j=valid();j['profile'].update(change)
 with pytest.raises(ValueError):validate(j)

def test_path_rejected():
 j=valid();j['output_dir']=str(OUTPUT/'../cut-world-v4')
 with pytest.raises(ValueError):validate(j)

def test_properties_use_values_not_addresses():
 from movie_factory.adapters.blender.demo_reuse import stable_property
 class Group:
  def to_dict(self):return {'b':[1,2],'a':3}
 class Text:
  name='rig_ui.py'
 assert stable_property(Group())==(('a',3),('b',(1,2)))
 assert stable_property(Text())==('Text','rig_ui.py')
