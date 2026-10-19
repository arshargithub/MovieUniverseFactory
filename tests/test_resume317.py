import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from scripts.resume317 import batches

def test_recovery_covers_missing_only_once():
    existing={1,2,3,14,280,281,450,696}
    jobs=batches(existing)
    flat=[f for a,b in jobs for f in range(a,b+1)]
    assert len(flat)==len(set(flat))
    assert set(flat)==set(range(1,697))-existing
    assert all(1<=b-a+1<=6 for a,b in jobs)
    assert jobs[0]==(275,279)
