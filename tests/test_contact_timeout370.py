from copy import deepcopy
import pytest
from movie_factory import native_admission as na, production_workflow as wf
from test_production_workflow import setup, bind
from test_native_handler333 import prepare


def test_only_exact_contact_cache_gets_longer_bound():
    exact=dict(operation='nihang_patch', edits=[dict(kind='mounted_padcontact369', target='fitted saddle blanket292', mode='envelope')])
    assert na.timeout_limit(exact)==1200
    for mode in ('inspect','fit','bind','refine','diagnose'):
        other=deepcopy(exact);other['edits'][0]['mode']=mode
        assert na.timeout_limit(other)==600
    other=deepcopy(exact);other['edits'].append(dict(kind='bone_pose'))
    assert na.timeout_limit(other)==600
    other=deepcopy(exact);other['edits'][0]['target']='horse'
    assert na.timeout_limit(other)==600
    assert na.timeout_limit(None)==600
    assert na.timeout_limit(dict(operation='nihang_frames'))==600


def test_standard_native_step_still_rejects_longer_timeout(setup,monkeypatch):
    root,c,bridge,calls=prepare(setup,monkeypatch)
    with pytest.raises(wf.Blocked, match='NATIVE_TIMEOUT_BOUND'):
        bridge.dispatch('t','proof','too-long',parent=bind(root,'parent.blend'),
                        blender_bin=na.BLENDER_BIN,timeout=900,recipe=bind(root,'save.json'))
    assert not calls
