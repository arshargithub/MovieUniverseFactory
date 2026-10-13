import sys
from pathlib import Path
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'scripts'))
from finish248_fist import validate,OPS
from finish248_render import validate as render_validate,OPS as RENDER_OPS
def test_closed_operations():
    for op in OPS:assert validate({'operation':op})==op
    for job in ({'operation':'exec'},{'operation':'inspect01','code':'bad'},None,{'operation':'../bad'}):
        with pytest.raises(ValueError):validate(job)
def test_twenty_second_clock_and_closed_render():
    frames=[]
    for op in ('opening-final','route-final'):
        _,interval=render_validate({'operation':op});frames.extend(interval)
    assert frames==list(range(217,697))
    assert len(frames)/24==20
    with pytest.raises(ValueError):render_validate({'operation':'opening-final','script':'untrusted'})
