import importlib.util
import sys
from pathlib import Path

import numpy as np

SCRIPTS = Path(__file__).resolve().parents[2] / 'scripts'
sys.path.insert(0, str(SCRIPTS))
spec = importlib.util.spec_from_file_location('finish242_audition', SCRIPTS/'finish242_audition.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def test_boundaries_and_inverse():
    native = np.array([0, 3, 4.75, 5.75, 8.25, 10.25, 13.625, 21])
    edit = np.array([0, 4, 5.75, 7.25, 9.75, 11.75, 15.125, 22.5])
    np.testing.assert_allclose(mod.time_map(native), edit)
    np.testing.assert_allclose(mod.inverse_time(edit), native)


def test_turn_and_ending_every_frame_original_rate():
    frames = np.floor(mod.inverse_time(np.arange(540)/24)*24+1e-6).astype(int)
    np.testing.assert_array_equal(frames[282:], np.arange(246, 504))
    assert frames[-1] == 503
    assert np.all(np.diff(frames) >= 0)
    repeats = np.where(np.diff(frames) == 0)[0]/24
    assert np.all((repeats < 4) | ((repeats >= 5.75) & (repeats < 7.25)))


def test_source_arrival_and_speech_clearance():
    assert 88-mod.MUSIC_START == 11.75
    assert 11.0262916667 < 11.75
    assert 22.5-15.125 == 21-13.625


def test_quote_integrity_and_proxy_label():
    ass = mod.manuscript()
    for text in ('The Pathans:', 'a hardy and', 'martial people', 'Sir Winston Churchill', 'provisional pre-turn timing'):
        assert text in ass
    assert '0:00:09.70' in ass  # clear before9.75 geography
    assert '0:00:06.65' in ass  # no opening book
