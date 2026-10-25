import importlib.util
from pathlib import Path
import numpy as np
import pytest

from movie_factory.adapters.blender import nihang_sculpt374 as m,nihang_patch

def test_closed_payload():
 good={'kind':'mounted_horseform374_sculpt','target':'horse','strength':1.}
 assert m.validate(good)==good
 nihang_patch.validate(dict(operation='nihang_patch',frame=367,width=432,height=432,samples=8,edits=[good]))
 for bad in [{**good,'code':'x'},{**good,'target':'leader'},{**good,'strength':float('nan')},{**good,'strength':True},{**good,'strength':1.26}]:
  with pytest.raises(ValueError):m.validate(bad)

def test_bounded_positive_form_not_laplacian():
 x=np.linspace(-.4,.4,21);z=np.linspace(.9,1.9,24);p=np.array([(a,-.85,c) for a in x for c in z]);b=np.ones(len(p));l=np.zeros(len(p));d=m.form_delta(p,b,l,1)
 assert np.isfinite(d).all() and .02<np.linalg.norm(d,axis=1).max()<.06
 assert d[:,1].min()<-.03
 assert np.allclose(d[:,2],0)
 assert np.allclose(d[p[:,2]<1.06],0)
 assert np.allclose(d[p[:,2]>1.76],0)
 assert np.allclose(d,m.form_delta(p,b,l,1))
 assert np.allclose(d,m.form_delta(p*np.array([-1,1,1]),b,l,1)*np.array([-1,1,1]))

def test_limb_and_back_anchors():
 p=np.array([[.14,-.8,1.4],[.14,0,1.4],[.14,-.8,1.4]])
 d=m.form_delta(p,np.ones(3),[0,0,.9],1)
 assert d[0,1]<-.025
 assert np.allclose(d[1:],0)

def test_strength_linear_inside_guard():
 p=np.array([[.14,-.8,1.4]])
 a=m.form_delta(p,[1],[0],.5);b=m.form_delta(p,[1],[0],1)
 assert np.allclose(a*2,b)


def test_contact_guard_uses_local_not_global_sculpt_influence():
 d=np.zeros((7,3));d[0,1]=.04;edges=np.array([[i,i+1] for i in range(6)])
 b=m.influence_bound(d,edges)
 assert np.allclose(b[:3],.04)
 assert np.allclose(b[3:],0)
 # An unchanged distant cache neighbour with3mm clearance is not required
 # to meet a nonsensical global25mm gap; changed surface still needs80mm.
 required=np.maximum(.002,2*b)
 assert required[0]==.08 and required[6]==.002


def test_actual_surface_contact_closed_frame_batches():
 e={'kind':'mounted_horseform374_contact','target':'horse','frames':[276,283,333,367]}
 assert m.validate(e)==e
 nihang_patch.validate(dict(operation='nihang_patch',frame=367,width=432,height=432,samples=8,edits=[e]))
 for fs in [[],[275],[368],[True],list(range(276,293)),[283,283]]:
  with pytest.raises(ValueError):m.validate({**e,'frames':fs})
