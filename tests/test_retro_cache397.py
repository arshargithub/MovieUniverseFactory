import json,sqlite3
import pytest
from movie_factory import retrospective as r,production_knowledge as pk
from movie_factory.production_workflow import Blocked


def test_incremental_supersession_and_corruption():
 c=sqlite3.connect(':memory:');r.install(c)
 r.append(c,'t','init','initialize',dict(version=r.VERSION,engine=r.engine()))
 r.append(c,'t','plan','plan',dict(requirements={'a':'fixed'},proof_uses=[],proof_bindings={}))
 base=dict(attempt='one',role='candidate',origin='test',evidence={},observations=[dict(requirement='a',status='FAIL',observation='bad')])
 r.append(c,'t','bad','outcome',base)
 assert r.snapshot(c,'t')==r.snapshot(c,'t',full=True)
 fixed=dict(base,supersedes='bad',observations=[dict(requirement='a',status='PASS',observation='corrected')])
 r.append(c,'t','fixed','outcome',fixed)
 assert r.snapshot(c,'t')==r.snapshot(c,'t',full=True)
 c.execute("UPDATE retrospective_cache397 SET state='{}'")
 with pytest.raises(Blocked):r.snapshot(c,'t')
 assert r.snapshot(c,'t',full=True)['outcomes'][-1]['event']=='fixed'
