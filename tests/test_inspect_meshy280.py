import importlib.util
from pathlib import Path
import pytest

spec = importlib.util.spec_from_file_location('inspect_meshy280', Path(__file__).parents[1]/'scripts/inspect_meshy280.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

def test_bound_source():
    assert m.inspector.sha(m.inspector.RAW) == m.inspector.EXPECTED
    assert m.inspector.glb_json(m.inspector.RAW.read_bytes())['asset']['version'] == '2.0'
    assert m.inspector.VIEW_YAW == 0.0
    assert m.inspector.WORKER.name == 'inspect_meshy280.py'
    assert str(m.inspector.TASK).endswith('sikh280/task-native.json')

@pytest.mark.parametrize('operation', ['inspect', 'reopen'])
def test_operations(operation):
    assert m.inspector.validate({'operation': operation}) == operation

@pytest.mark.parametrize('job', [{'operation': 'exec'}, {'operation': 'inspect', 'path': '/tmp/other'}, None])
def test_no_arbitrary_dispatch(job):
    with pytest.raises(ValueError):
        m.inspector.validate(job)
