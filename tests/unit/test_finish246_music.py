import sys
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'scripts'))
from finish246_music import START,TURN,SOURCE_TURN,replace_music

def test_director_landmark_alignment():
    assert START==39.25 and START+TURN==SOURCE_TURN==51
    assert 52-START==12.75

def test_only_music_changes():
    r=np.random.default_rng(246);a=r.normal(0,.1,(50,2));am=r.normal(0,.03,(50,2));bm=r.normal(0,.03,(50,2))
    b,c=replace_music(a,am,bm,.73)
    np.testing.assert_allclose(b-a,.73*(bm-am),atol=1e-16)
    np.testing.assert_allclose(b-.73*bm,c,atol=1e-16)
