import sys
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'scripts'))
from finish245_audio import music_gain,shorten_voice,RATE
from finish245_edit import manuscript,SRT
def test_music_build_does_not_pump():
    x=music_gain(np.linspace(0,11.3,2000))
    assert x[0]==0 and x[-1]==.66 and (np.diff(x)>=0).all()
    assert music_gain(np.array([6.6838]))[0]<.081
def test_silence_removal_preserves_spoken_samples():
    x=np.zeros(7*RATE);x[100:200]=.2;x[6*RATE:6*RATE+100]=.4
    y,p=shorten_voice(x)
    assert (y==.2).sum()==100 and (y==.4).sum()==100
    assert max(p)==0
def test_quote_and_short_subtitles():
    assert 'Sir Winston Churchill' in manuscript()
    assert 'pos(216,22)' in manuscript()
    assert 'pos(216,-' not in manuscript()
    assert 'Churchill' not in SRT and 'Pathans' not in SRT
    assert 'impeccable.' in SRT
