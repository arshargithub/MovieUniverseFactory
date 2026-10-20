import importlib.util
from pathlib import Path
import pytest

spec=importlib.util.spec_from_file_location('sikh319',Path(__file__).parents[1]/'scripts/sikh319.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def test_jobs():
    assert m.validate({'operation':'inspect','version':1,'frames':[1]})
    for change in ({'operation':'exec'},{'version':0},{'frames':[0]},{'frames':list(range(1,9))},{'frames':[True]}):
        j={'operation':'inspect','version':1,'frames':[1]};j.update(change)
        with pytest.raises(ValueError):m.validate(j)
def test_preserved_input():
    assert m.source_for('build',1)==m.SOURCE
    assert m.source_for('look',1)!=m.SOURCE
    assert m.source_for('refine',17)==m.BASE/'build-16/sequence.blend'
    assert m.source_for('movie',17)==m.BASE/'refine-17/sequence.blend'

def test_resume_never_repeats_frames():
    import sys
    sys.path.insert(0,str(Path(__file__).parents[1]/'scripts'))
    from resume319 import batches
    old={1,2,3,10,80,283,333,695,696}
    jobs=batches(old);frames=[f for job in jobs for f in job]
    assert len(frames)==len(set(frames))
    assert set(frames)==set(range(1,697))-old
    assert all(1<=len(job)<=6 for job in jobs)
