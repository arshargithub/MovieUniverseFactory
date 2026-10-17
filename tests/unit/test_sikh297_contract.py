import math
import pytest
from movie_factory.sikh297_contract import validate, TORCHES, flicker, band_radius

def test_exact_job():
    assert validate({'operation':'controls','version':1})['version']==1
    for j in ({'operation':'exec','version':1},{'operation':'movie','version':True},{'operation':'movie','version':1,'code':'x'}):
        with pytest.raises(ValueError):validate(j)

def test_torches_outside_lane_and_leader_fixture():
    assert all(abs(x)>=2.75 for x,y,z in TORCHES if not z)
    assert sum(z>0 for x,y,z in TORCHES)==1
    assert len([y for x,y,z in TORCHES if y>0])>=3

def test_no_blackout_or_strobe_power():
    for i in range(8):
        values=[flicker(f/24,i) for f in range(528)]
        assert min(values)>.88 and max(values)<1.12
        assert max(abs(a-b) for a,b in zip(values,values[1:]))<.06

def test_crown_taper_not_cylinder():
    assert band_radius(.27)<band_radius(.13)
    assert all(math.isfinite(band_radius(z/100)) for z in range(4,30))
