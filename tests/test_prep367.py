from copy import deepcopy
import pytest
from movie_factory.adapters.blender import nihang_prep367 as p, nihang_patch as patch, nihang_control as control


def edit():
    rows=[]
    for f,v in [(283,0),(291,.2),(298,.6),(307,.2),(314,0)]:
        row={k:0. for k in p.FIELDS};row.update(frame=f,left_fold=v,actor_time=283+(f-283)*23/31);rows.append(row)
    return dict(kind='mounted_prep367',target='mounted leader',anchors=rows)


def test_numeric_transport_and_fixed_audit():
    e=edit();p.validate(e)
    r=dict(operation='nihang_patch',frame=314,width=432,height=768,samples=8,edits=[e]);assert patch.validate(r)==r
    r['edits']=[dict(kind='mounted_prepaudit367',target='mounted leader')];patch.validate(r)
    control.validate(dict(operation='nihang_frames',frame=283,frames=[283,300],view='horse_phase367',width=640,height=640,samples=8))


@pytest.mark.parametrize('change',['unknown','nan','bad_time','backwards','mesh','count'])
def test_numeric_bounds(change):
    e=edit()
    if change=='unknown':e['anchors'][0]['code']='print(1)'
    if change=='nan':e['anchors'][1]['hip_drop']=float('nan')
    if change=='bad_time':e['anchors'][1]['frame']=900
    if change=='backwards':e['anchors'][2]['actor_time']=276
    if change=='mesh':e['anchors'][0]['hip_drop']=1
    if change=='count':e['anchors']=e['anchors'][:2]
    with pytest.raises(ValueError):p.validate(e)


def test_smooth_sample_stays_inside_keyed_range_and_clock():
    a=edit()['anchors'];rows=[p.sample(a,283+i/16) for i in range(32*16)]
    assert all(0<=r['left_fold']<=.6 for r in rows)
    assert all(rows[i]['actor_time']<=rows[i+1]['actor_time'] for i in range(len(rows)-1))
    assert p.sample(a,283)==a[0] and p.sample(a,314)==a[-1]
