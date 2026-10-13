import sys
from pathlib import Path
import numpy as np

sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'scripts'))
import finish243_remix as remix


def test_music_co_lead_and_pause():
    g=remix.music_envelope(np.array([.7,2.,5.8,6.5,7.,7.3,8.,11.70,12.]))
    np.testing.assert_allclose(g,[.66,.46,.46,.66,.66,.66,.46,.66,.66])
    assert 20*np.log10(.46/.66)>-3.2


def test_silent_insert_preserves_speech():
    source=np.zeros((21*48000,2));source[10000:20000]=.1;source[300000:310000]=.2
    out,peak=remix.narration(source)
    assert peak==0
    np.testing.assert_array_equal(out[out!=0],source[source!=0])
    assert len(out)==22.5*48000
    assert np.all(out[round((.95+5.395)*48000):round((.95+5.395+1.12)*48000)]==0)


def test_non_silent_splice_rejected():
    source=np.ones((21*48000,2))*.1
    try:remix.narration(source)
    except AssertionError:pass
    else:raise AssertionError('Must not insert silence in a phoneme')


def test_no_sudden_automation_steps():
    g=remix.music_envelope(np.arange(round(22.5*48000))/48000)
    assert np.max(np.abs(np.diff(g)))<.001
