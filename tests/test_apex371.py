from copy import deepcopy
import json
from pathlib import Path
import pytest
from movie_factory.adapters.blender import nihang_apex371 as apex,nihang_patch as patch,nihang_control as control,nihang_prep367 as prep,nihang_padsolve370 as cloth,nihang_padcontact369 as transport


def candidate():
    p=Path(__file__).resolve().parents[1]/'results/sikh371/motion-c67-anchors.json'
    return json.loads(p.read_text())


def test_interval_guards_protect_accepted_prefix_and_land_scope():
    edit=candidate();apex.validate(edit)
    for frame in (313,315):
        bad=deepcopy(edit);bad['anchors'][0]['frame']=frame
        with pytest.raises(ValueError):apex.validate(bad)
    bad=deepcopy(edit);bad['anchors'][-1]['frame']=334
    with pytest.raises(ValueError):apex.validate(bad)
    for field,value in [('pitch',-1.5),('left_fold',1.2),('actor_time',320),('poll_pitch',float('nan'))]:
        bad=deepcopy(edit);bad['anchors'][2][field]=value
        with pytest.raises(ValueError):apex.validate(bad)
    bad=deepcopy(edit);bad['code']='arbitrary'
    with pytest.raises(ValueError):apex.validate(bad)


def test_declared_crest_is_high_and_active_with_exact_incoming_discrete_slope():
    edit=candidate();a=edit['anchors'];assert a[0]['frame']==314
    baseline=json.loads((Path(__file__).resolve().parents[1]/'results/sikh371/ACCEPTED_EXIT.json').read_text())['rows']
    rows={int(k):v for k,v in baseline.items()}
    for field in prep.FIELDS:
        if field=='actor_time':continue
        assert a[1][field]-a[0][field]==pytest.approx(rows[314][field]-rows[313][field])
    states=[prep.sample(a,f) for f in range(315,334)]
    assert min(x['pitch'] for x in states)<-.95
    held=[x for x in states if x['frame']>=323]
    assert len(held)==11 and max(x['pitch'] for x in held)<-1.
    assert len({x['left_fold'] for x in held})>3
    assert len({x['neck_pitch'] for x in held})>3


def test_apex_contact_cache_cannot_overwrite_preparation_or_expand_window():
    name,frames=cloth.phase_spec('apex');old,oldframes=cloth.phase_spec('preparation')
    assert name!=old and set(frames)==set(range(315,334))
    assert not set(frames)&set(oldframes)
    with pytest.raises(ValueError):cloth.phase_spec('arbitrary')
    transport.validate(dict(kind='mounted_padcontact369',target='fitted saddle blanket292',mode='apex_envelope'))
    with pytest.raises(ValueError):transport.validate(dict(kind='mounted_padcontact369',target='fitted saddle blanket292',mode='apex_envelope',frames=[1]))


def test_new_patch_and_reverse_view_are_typed_not_code_paths():
    patch.validate(dict(operation='nihang_patch',frame=333,width=432,height=432,samples=8,edits=[candidate()]))
    control.validate(dict(operation='nihang_frames',frame=333,frames=[323,333],view='horse_reverse371',width=432,height=432,samples=8))
    with pytest.raises(ValueError):control.validate(dict(operation='nihang_frames',frame=333,frames=[323,333],view='arbitrary',width=432,height=432,samples=8))


def test_visibility_extension_keeps_every_actual_accepted_state():
    before={f:(f%3==0) for f in range(276,315)}
    rows=apex.visibility_keys(before,{315:True,334:True});after=dict(rows)
    assert {f:after[f] for f in before}==before
    assert after[315] and after[334] and not any(f<276 for f in after)
    with pytest.raises(ValueError):apex.visibility_keys({314:False},{315:True})
    with pytest.raises(ValueError):apex.visibility_keys(before,{300:True})
