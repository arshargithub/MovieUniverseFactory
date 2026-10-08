"""Closed-operation safety and numerical controls for entrance193."""
import importlib.util
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('entrance193_inspect', ROOT/'scripts/entrance193_inspect.py')
inspect = importlib.util.module_from_spec(spec); spec.loader.exec_module(inspect)


@pytest.mark.parametrize('job', [{}, {'operation':'inspect02'}, {'operation':'inspect01','code':'bad'}])
def test_closed_inspection(job):
    with pytest.raises(ValueError): inspect.validate(job)


def test_chain_root_and_lengths():
    import numpy as np
    import entrance193_motion as motion
    p=np.column_stack((np.zeros(18),np.linspace(0,9,18),-np.linspace(0,4,18)**1.1))
    roots=np.zeros((48,3));roots[:,2]=.5*np.sin(np.arange(48)*.5)
    q=motion.tail_chain(p,roots)
    assert np.max(abs(q[:,0]-roots))<1e-9
    lengths=np.linalg.norm(np.diff(p,axis=0),axis=1)
    assert np.max(abs(np.linalg.norm(np.diff(q,axis=1),axis=2)/lengths-1))<.035
    assert np.ptp(q[:,-1,2]-roots[:,2])>.15


def test_phase_finite_and_bounded():
    import numpy as np
    import entrance193_motion as motion
    s=np.repeat(np.eye(4)[None],144,axis=0);s[:,2,3]=np.sin(np.arange(144)*.5)
    q=motion.phase_signal(s)
    assert q.shape==(144,) and abs(q).max()<=1


@pytest.mark.parametrize('job', [{}, {'operation':'custom'}, {'operation':'lookA10','source':'elsewhere'}])
def test_render_rejects_unreviewed_operation(job):
    import entrance193_render as render
    with pytest.raises(ValueError):render.validate(job)
