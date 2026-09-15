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

def multistage():
 j=valid();p=j['profile'];p['offset_start']=[0,12,20];p['offset_end']=[-3,-10,1.8]
 p['camera_path']=[{'at':0,'offset':p['offset_start']},{'at':.35,'offset':[-10,0,2.2]},{'at':.52,'offset':[-10,0,2.2]},{'at':.84,'offset':p['offset_end']},{'at':1,'offset':p['offset_end']}]
 return j

def test_multistage_holds_and_boundaries():
 from movie_factory.adapters.blender.demo_reuse import camera_offset
 p=validate(multistage())[1]
 assert camera_offset(p,0)==p['offset_start']
 assert camera_offset(p,1)==p['offset_end']
 assert camera_offset(p,.4)==[-10,0,2.2]
 assert camera_offset(p,.9)==p['offset_end']
 for at in [.35,.52,.84]:
  lo=camera_offset(p,at-1e-6);mid=camera_offset(p,at);hi=camera_offset(p,at+1e-6)
  assert max(abs(x-y) for x,y in zip(lo,mid))<1e-8
  assert max(abs(x-y) for x,y in zip(hi,mid))<1e-8

@pytest.mark.parametrize('change',['unknown_key','nan','repeated_time','too_high','endpoint','too_many'])
def test_bad_path(change):
 j=multistage();p=j['profile'];knots=p['camera_path']
 if change=='unknown_key':knots[1]['python']='x'
 if change=='nan':knots[1]['at']=float('nan')
 if change=='repeated_time':knots[1]['at']=0
 if change=='too_high':knots[1]['offset'][2]=100
 if change=='endpoint':knots[-1]['at']=.99
 if change=='too_many':p['camera_path']=knots*2
 with pytest.raises(ValueError):validate(j)

def continuous():
 j=multistage();p=j['profile'];p['path_interpolation']='continuous'
 p['camera_path']=[{'at':0,'offset':p['offset_start']},{'at':.55,'offset':[-11,1,4.5]},{'at':.7,'offset':[-9,-2,2.5]},{'at':1,'offset':p['offset_end']}]
 return j

def test_continuous_path_moves_through_interior_knots():
 from movie_factory.adapters.blender.demo_reuse import camera_offset
 p=validate(continuous())[1]
 for t in [.55,.7]:
  eps=1e-6;left=camera_offset(p,t-eps);mid=camera_offset(p,t);right=camera_offset(p,t+eps)
  vl=[(m-l)/eps for l,m in zip(left,mid)];vr=[(r-m)/eps for m,r in zip(mid,right)]
  assert sum(v*v for v in vl)>1
  assert max(abs(x-y) for x,y in zip(vl,vr))<.01
 for i in range(1001):
  t=i/1000;v=camera_offset(p,t)
  assert sum(x*x for x in v)>=9
  for a,b in zip(p['camera_path'],p['camera_path'][1:]):
   if a['at']<=t<=b['at']:
    assert all(min(x,y)-1e-9<=z<=max(x,y)+1e-9 for x,y,z in zip(a['offset'],b['offset'],v))

def test_unknown_interpolator_rejected():
 j=continuous();j['profile']['path_interpolation']='python'
 with pytest.raises(ValueError):validate(j)
