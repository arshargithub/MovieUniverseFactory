import importlib.util
from pathlib import Path
import pytest

spec = importlib.util.spec_from_file_location('render210_probe', Path(__file__).parents[1] / 'scripts/render210_probe.py')
probe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(probe)

def test_fixed_sources_and_operations():
    for op in probe.OPS:
        source, device, rt, frames = probe.validate({'operation': op})
        assert source in probe.SOURCES and device in ('CPU', 'GPU')
        assert all(217 <= f <= 648 for f in frames)
        assert rt in (None, 'ON', 'OFF')

@pytest.mark.parametrize('job', [{}, {'operation':'unknown'}, {'operation':'inspect','code':'x'}, {'operation':[]}, None])
def test_rejects_unstructured_or_expanded_jobs(job):
    with pytest.raises(ValueError):
        probe.validate(job)
