import sys
from pathlib import Path
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'scripts'))
from finish245_render import validate,OPS
def test_closed_operations():
    for x in ({'operation':'shell'},{'operation':'opening-final','path':'/tmp/x'},{},None):
        with pytest.raises((ValueError,TypeError)):validate(x)
def test_complete_native_coverage():
    frames=OPS['opening-final'][1]+OPS['route-final'][1]
    assert frames==tuple(range(217,757))
    assert len(set(frames))==540
