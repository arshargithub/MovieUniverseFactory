import sys
from pathlib import Path
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from finish237_clock import clocks
from finish237_native import validate
def test_duration_and_turn():
    assert 198+306==21*24
    for i in range(18,306):assert clocks('route',i)[0]==361+i-18
    assert clocks('route',48)==(391,391,391)
def test_opening_speed():
    for i in range(197):assert clocks('opening',i+1)[2]-clocks('opening',i)[2]==1
    assert clocks('opening',114)[1]==313
    assert clocks('opening',197)[1]<=360
def test_closed():
    validate({'operation':'opening01'})
    for job in ({'operation':'arbitrary'}, {'operation':'opening01','code':'x'}):
        with pytest.raises(ValueError):validate(job)
