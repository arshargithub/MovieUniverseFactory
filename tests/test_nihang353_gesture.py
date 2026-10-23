from movie_factory.adapters.blender.nihang_gesture353 import lift,ground_gap,accelerating_strike

def test_visible_cue_then_strike_before_drive():
    assert lift(285,.18)==0
    assert lift(293,.18)==.18
    assert lift(297,.18)>lift(299,.18)>0
    assert lift(300,.18)==lift(327,.18)==0
    assert ground_gap(300)==0
    assert ground_gap(299)>0 and ground_gap(301)>0

def test_downstroke_accelerates_into_contact_not_smoothstep():
    v=[24*(lift(f,.15)-lift(f-1,.15)) for f in range(296,301)]
    assert accelerating_strike(v)
    assert not accelerating_strike([-.7439,-.9379,-.928,-.7138,-.2952])

def test_lift_has_no_negative_overshoot():
    for frame in range(252,442):
        assert 0<=lift(frame,.18)<=.18
