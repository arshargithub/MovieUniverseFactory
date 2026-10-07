"""Deterministic geometry controls; these never substitute for visual review."""
import importlib.util
from pathlib import Path
import numpy as np
import pytest

PATH=Path(__file__).resolve().parents[2]/'scripts/entrance188_groom.py'
spec=importlib.util.spec_from_file_location('groom188',PATH)
groom=importlib.util.module_from_spec(spec);spec.loader.exec_module(groom)


def fixture():
    a=np.zeros((144,1047,6,3))
    a[:,:,:,1]=np.linspace(-8,-2,1047)[None,:,None]
    a[:,:,:,2]=np.linspace(-2,-5,1047)[None,:,None]
    a[:,:,:,0]=np.arange(144)[:,None,None]*.01
    return a


def test_roots_and_stability():
    a=fixture();p,r=groom.guides(a,1)
    assert p.shape==(144,1047,12,3)
    assert np.isfinite(p).all()
    assert r['source_root_error']<1e-6
    assert np.max(abs(p[:,:,0]-a[:,:,0]))<1e-6
    assert np.array_equal(p,groom.guides(a,1)[0])


def test_tube_topology():
    p,_=groom.guides(fixture(),1)
    v,f=groom.tube_frames(p[:2,:5])
    assert v.shape==(2,180,3)
    assert len(f)==165
    assert max(max(face) for face in f)<180
    assert np.isfinite(v).all()


def test_reject_invalid_source():
    with pytest.raises(ValueError):groom.guides(np.zeros((1,2,3)))
    a=fixture();a[0,0,0,0]=np.nan
    with pytest.raises(ValueError):groom.guides(a)


@pytest.mark.parametrize('job',[None,{}, {'operation':'execute'}, {'operation':'horse01','code':'no'}, {'operation':'integrated01','path':'/tmp/no'}])
def test_job_rejects_unstructured_inputs(job):
    path=PATH.parent/'entrance188.py'
    spec=importlib.util.spec_from_file_location('entry188',path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    with pytest.raises(ValueError):module.validate(job)
