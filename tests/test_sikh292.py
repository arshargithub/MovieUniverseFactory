import pytest
from movie_factory import sikh292_motion as m
from movie_factory import sikh291_motion as old
def test_stop_and_launch():
    assert m.travel(10)==pytest.approx(old.travel(10)+6)
    assert m.travel(21.5)==pytest.approx(old.travel(21.5))
    assert -18.4-(m.travel(8)-.9)<-13
def test_continuous_motion():
    for t in (4.5,7.5,18.5,20,21.5,23):
        assert abs(m.travel(t-1e-6)-m.travel(t+1e-6))<.0001
        vl=(m.travel(t)-m.travel(t-1e-5))/1e-5;vr=(m.travel(t+1e-5)-m.travel(t))/1e-5
        assert abs(vl-vr)<.001
def test_debris_ground():
    for a in (0,.1,.3,1,3):assert m.debris_position((0,0,.02),(1,3,2),a)[2]>=.012
    assert m.debris_position((0,0,.02),(1,3,2),1)==m.debris_position((0,0,.02),(1,3,2),3)
def test_exact_job():
    assert m.validate_job({'operation':'controls','version':1})
    for j in ({'operation':'exec','version':1},{'operation':'movie','version':True},{'operation':'movie','version':1,'code':'x'}):
        with pytest.raises(ValueError):m.validate_job(j)
def test_slip():
    assert m.slip(6.4) and m.slip(21.8)
    assert not m.slip(10)
