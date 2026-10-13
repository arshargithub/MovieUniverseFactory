import importlib.util
from pathlib import Path
import numpy as np
import pytest
spec=importlib.util.spec_from_file_location('delivery248',Path(__file__).resolve().parents[2]/'scripts/finish248_delivery.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def test_cut_preserves_accepted_sound_and_unfaded_join():
    x=np.ones((22*m.RATE,2))*.2;raw,review=m.cut_audio(x,m.RATE)
    assert len(raw)==len(review)==20*m.RATE
    assert np.array_equal(raw,x[:20*m.RATE])
    assert np.array_equal(review[:int(19.75*m.RATE)],raw[:int(19.75*m.RATE)])
    assert np.all(review[-1]==0)
    assert np.all(np.diff(review[-12000:,0])<=0)
    assert np.all(x==.2)
def test_rejects_wrong_audio_format():
    with pytest.raises(ValueError):m.cut_audio(np.zeros((100,2)),48000)
    with pytest.raises(ValueError):m.cut_audio(np.zeros((22*48000,2)),44100)
