import sys
from pathlib import Path
import numpy as np
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from entrance207_motion import flexion,expression,mane_step,tail_response
from entrance207_inspect import validate
from entrance207_build import validate as build_validate

def test_closed_inspection():
 validate({'operation':'inspect01'})
 for job in ({'operation':'exec'},{'operation':'inspect01','code':'x'},None):
  with pytest.raises(ValueError):validate(job)
 for op in ('opening01','route02'):build_validate({'operation':op})
 with pytest.raises(ValueError):build_validate({'operation':'opening01','source':'/tmp/no'})

def test_attention_bounded_and_visible_delta():
 for f in range(217,649):assert all(0<=v<=1 for v in expression(f).values())
 assert expression(329)['browInnerUp']-expression(315)['browInnerUp']>.4
 assert expression(345)['browDownLeft']>.6

def test_absorption_is_driven_not_unrelated_noise():
 x=flexion(np.full(144,.15));assert np.ptp(x[:,0])<1e-9
 x=flexion(.15+.03*np.sin(np.arange(144)*.7))
 assert 10<np.rad2deg(np.ptp(x[:,0]))<13
 assert np.max(abs(x[:,0]+x[:,1]))<np.deg2rad(3)

def test_root_pinned_mane_finite_and_responds():
 rest=np.zeros((4,12,3));rest[:,:,1]=np.linspace(0,3,12);rest[:,:,2]=np.linspace(0,-1,12)
 d=np.zeros_like(rest);v=d.copy()
 for i in range(24):d,v=mane_step(rest,d,v,np.zeros((4,3)),np.arange(4),i/24)
 assert np.array_equal(d[:,:2],np.zeros((4,2,3)))
 assert np.max(abs(d))>.04 and np.isfinite(d).all()
 lengths=np.linalg.norm(np.diff(rest+d,axis=1),axis=2);original=np.linalg.norm(np.diff(rest,axis=1),axis=2)
 assert np.max(abs(lengths-original))<.04

def test_tail_root_and_length():
 rest=np.column_stack((np.zeros(12),np.linspace(0,8,12),-np.linspace(0,2,12)))
 roots=np.column_stack((np.zeros(30),np.zeros(30),.2*np.sin(np.arange(30)*.6)))
 worlds=np.tile(np.eye(4),(30,1,1));p=tail_response(rest,roots,worlds)
 assert np.max(abs(p[:,0]-roots))<1e-9
 assert np.isfinite(p).all()
 assert np.max(abs(np.linalg.norm(np.diff(p,axis=1),axis=2)-np.linalg.norm(np.diff(rest,axis=0),axis=1)))<.025
