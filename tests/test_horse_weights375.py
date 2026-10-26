import numpy as np
import pytest
from movie_factory.adapters.blender import nihang_weights375 as m,nihang_patch as p

NAMES=['DEF-breast.L','DEF-breast.R','DEF-upper_arm.L.001','DEF-upper_arm.R.001','DEF-forearm.L','DEF-forearm.R','DEF-upper_arm.L','body','DEF-upper_arm.R']

def fixture():
 points=np.array([[.1,-.85,1.3],[-.1,-.85,1.3],[.1,-.8,2.0],[.1,.2,1.3]])
 raw=points.copy();raw[:,1]-=.1;w=np.array([[.4,0,.3,0,.1,0,.2,1,0],[0,.4,0,.3,0,.1,.2,1,0],[.4,0,.3,0,.1,0,.2,1,0],[.4,0,.3,0,.1,0,.2,1,0]])
 return points,raw,w,NAMES,np.array([[0,1],[1,2],[2,3]])

def test_calibrated_zero_and_mass_preserved_local_transfer():
 args=fixture();old=args[2];z,_,_=m.remap(*args,0);assert np.array_equal(z,old)
 new,mask,mass=m.remap(*args,1);assert mass[0]>.1 and mass[1]>.1
 assert np.allclose(new.sum(1),old.sum(1));assert np.array_equal(new[:,7],old[:,7]);assert np.array_equal(new[2:],old[2:]);assert new[0,6]>old[0,6] and new[0,2]<old[0,2] and new[0,0]<old[0,0]

def test_no_legacy_shape_shift_no_speculative_transfer():
 args=list(fixture());args[1]=args[0].copy();new,_,mass=m.remap(*args,1);assert np.array_equal(new,args[2]);assert np.allclose(mass,0)

def test_payload_closed_and_bounded():
 good=dict(kind='mounted_horse_deform375_weights',target='horse',strength=1);m.validate(good);p.validate(dict(operation='nihang_patch',frame=367,width=432,height=432,samples=8,edits=[good]))
 for e in [{**good,'code':'x'},{**good,'strength':1.1},{**good,'strength':True},{**good,'target':'leader'}]:
  with pytest.raises(ValueError):m.validate(e)
