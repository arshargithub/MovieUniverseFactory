import importlib.util
from pathlib import Path
import pytest
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('sikh320',ROOT/'scripts/sikh320.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def test_scope_isolated():
    assert m.START==252 and m.END==441
    assert 276-m.START==24 and m.END-417==24
    assert m.source('build',1)==m.SOURCE
    assert m.source('motion',1)!=m.SOURCE
    assert m.source('attention',8)==m.BASE/'build-04/sequence.blend'
    assert m.source('motion',8)==m.BASE/'build-08/sequence.blend'
def test_rejects_unstructured_jobs():
    valid={'operation':'look','version':1,'frames':[283]}
    assert m.validate(valid)
    for change in ({'operation':'exec'},{'frames':[1]},{'frames':[True]},{'version':0},{'frames':list(range(252,259))}):
        with pytest.raises(AssertionError):m.validate(valid|change)
    with pytest.raises(AssertionError):m.validate(valid|{'code':'not accepted'})

def test_audio_motion_share_retime_formula():
    import ast
    import numpy as np
    def get(filename):
        tree=ast.parse((ROOT/'scripts'/filename).read_text())
        function=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='retime')
        ns={'np':np};exec(compile(ast.Module(body=[function],type_ignores=[]),filename,'exec'),ns)
        return ns['retime']
    a=get('sikh320_performance.py');b=get('edit320.py')
    values=np.linspace(0,34,3401)
    assert all(a(t)==b(t) for t in values)
    assert all(a(y)>a(x) for x,y in zip(values,values[1:]))
    assert a(17.1)==17.1 and a(14.28)==14.28
    assert a(15.61)==15.29
