import importlib.util
import json
from pathlib import Path
import pytest
spec=importlib.util.spec_from_file_location('frontfit',Path('src/movie_factory/adapters/blender/hair_front_fit.py'))
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)

@pytest.mark.parametrize('job',[None,{}, {'operation':'exec','candidate':1},{'operation':'preview','candidate':True},{'operation':'preview','candidate':4},{'operation':'preview','candidate':1,'path':'x'}])
def test_invalid(job):
    with pytest.raises(ValueError): m.validate(job)

def test_pins_outputs_preview(tmp_path,monkeypatch):
    p=tmp_path/'source'; p.write_bytes(b'fixed')
    monkeypatch.setattr(m,'SOURCE',p); monkeypatch.setattr(m,'SOURCE_SHA',m.digest(p))
    monkeypatch.setattr(m,'BASE',tmp_path); monkeypatch.setattr(m,'REFERENCES',{})
    out=m.validate({'operation':'preview','candidate':1}); out.mkdir()
    with pytest.raises(ValueError,match='exists'): m.validate({'operation':'preview','candidate':1})
    with pytest.raises(ValueError,match='Preview'): m.validate({'operation':'package','candidate':1})
    result={'handler_sha256':m.digest(Path(m.__file__)),'protected_exact':True,'rear_geometry_exact':False}
    (out/'result.json').write_text(json.dumps(result))
    with pytest.raises(ValueError,match='Stale'): m.validate({'operation':'package','candidate':1})
    result['rear_geometry_exact']=True; (out/'result.json').write_text(json.dumps(result))
    assert m.validate({'operation':'package','candidate':1}).name=='frontfit-package-01'
    p.write_bytes(b'changed')
    with pytest.raises(ValueError,match='Pinned'): m.validate({'operation':'preview','candidate':2})

@pytest.mark.parametrize('candidate',[1,2,3])
def test_local_bounded_fit(candidate):
    for x in (-1,-.5,0,.5,1):
        assert m.weights(x,.2,1,candidate)==(0.,0.)
        assert m.weights(x,-1,1.6,candidate)==(0.,0.)
        for z in (0,.3,.7,1.,1.3):
            a,b=m.weights(x,-.8,z,candidate)
            assert -.086<=a<=.221 and 0<=b<=.69

def test_taper_not_global_lift():
    assert m.weights(0,-.8,.9,3)[0]>.10
    assert m.weights(.5,-.8,.6,3)[0]<-.07
