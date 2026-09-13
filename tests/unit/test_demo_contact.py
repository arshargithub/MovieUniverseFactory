"""Physics-unit and boundary regressions for the admitted contact overlay math."""
import pytest
from movie_factory.adapters.blender.demo_contact import offset


def test_supported_world_patch_is_stationary_and_vertical_is_preserved():
    trajectory = lambda f: (.01*f*f, -.06*f, .2*f)
    points=[]
    for i in range(81):
        f=2+i/40
        c=trajectory(f)
        d=offset(f,trajectory,2,4,(0,-1,0),blend=.5)
        assert d[2]==0
        points.append(tuple(c[j]+d[j]+(0,-1,0)[j]*f/24 for j in range(2)))
    for j in range(2):
        assert max(x[j] for x in points)-min(x[j] for x in points)<1e-12


def test_periodic_wrapped_support():
    import math
    curve=lambda f:(.02*math.sin(f*math.tau/10),.01*math.cos(f*math.tau/10),.1)
    for f in (-1,.125,1.9,9.5,10.125):
        assert offset(f,curve,9.5,2,(0,-1,0),blend=.5)==pytest.approx(offset(f+10,curve,9.5,2,(0,-1,0),blend=.5))


def test_blend_ends_have_zero_value_and_derivative():
    curve=lambda f:(0,.02*f,0)
    for boundary,direction in ((1.5,1),(4.5,-1)):
        assert offset(boundary,curve,2,4,(0,-1,0),blend=.5)==(0,0,0)
        eps=1e-5
        assert max(abs(v)/eps for v in offset(boundary+direction*eps,curve,2,4,(0,-1,0),blend=.5))<1e-4
    assert offset(7,curve,2,4,(0,-1,0),blend=.5)==(0,0,0)


def test_excessive_correction_refused_instead_of_clamped():
    with pytest.raises(ValueError,match='exceeds'):
        offset(2,lambda f:(f,0,0),2,4,(0,0,0),blend=.5)


@pytest.mark.parametrize('changes',[{'mode':'execute_python'},{'profile':{'python':'x'}},{'python':'x'},{'output_dir':'/tmp/escape'}])
def test_fixed_riding_dispatch_rejects_unstructured_input(monkeypatch,changes):
    import importlib.util
    import sys
    from types import SimpleNamespace
    from pathlib import Path
    monkeypatch.setitem(sys.modules,'bpy',SimpleNamespace())
    monkeypatch.setitem(sys.modules,'mathutils',SimpleNamespace(Matrix=None,Vector=None))
    spec=importlib.util.spec_from_file_location('fixed_riding_boundary',Path('src/movie_factory/adapters/blender/demo_riding.py'))
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    job={'mode':'demo_free_verify','profile':{},'output_dir':'runs/demonstrator-01/never-created'}
    job.update(changes)
    with pytest.raises(ValueError):module._output(job)
