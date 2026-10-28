import copy
import json
import pytest
from movie_factory import context_projection397 as cp,review_control as rc


@pytest.fixture
def bound(tmp_path):
    p=tmp_path/cp.PATH;p.parent.mkdir(parents=True)
    p.write_text(json.dumps(dict(substantive_exchange_count=397,updated_date='today',authority='unchanged',budgets={'a':2})))
    return tmp_path,p,cp.bind(tmp_path)


def test_only_cosmetic_status_fields_can_change(bound):
    root,p,b=bound;d=json.loads(p.read_text());d.update(substantive_exchange_count=398,updated_date='tomorrow');p.write_text(json.dumps(d))
    rc.binding(root,b)


@pytest.mark.parametrize('field',['authority','budgets','unknown_new_permission'])
def test_changed_or_added_substantive_fact_blocks(bound,field):
    root,p,b=bound;d=json.loads(p.read_text());d[field]='changed';p.write_text(json.dumps(d))
    with pytest.raises(rc.Blocked,match='AUTHORITY_OR_FACTS_CHANGED'):rc.binding(root,b)


def test_deleting_fact_or_expanding_exclusion_blocks(bound):
    root,p,b=bound;d=json.loads(p.read_text());d.pop('authority');p.write_text(json.dumps(d))
    with pytest.raises(rc.Blocked):rc.binding(root,b)
    b=copy.deepcopy(b);b['projection397']['excluded'].append('authority')
    with pytest.raises(rc.Blocked,match='FIELDS'):rc.binding(root,b)


def test_old_whole_binding_remains_strict(bound):
    from movie_factory.production_knowledge import file_hash
    root,p,_=bound;b={'path':cp.PATH,'sha256':file_hash(p)}
    p.write_text(p.read_text()+' ')
    with pytest.raises(rc.Blocked,match='STALE_BINDING'):rc.binding(root,b)


def test_frozen_snapshot_tampering_cannot_repin_status(bound):
    root,p,b=bound;(root/b['projection397']['snapshot']['path']).write_text('{}')
    with pytest.raises(rc.Blocked,match='STALE_STATUS_SNAPSHOT'):rc.binding(root,b)
