import math
import pytest
from movie_factory.adapters.blender.nihang_motion import validate,sample,FIELDS
from movie_factory.adapters.blender.nihang_control import validate as control
from test_production_workflow import setup
from test_native_handler333 import prepare,run
from test_task_router332 import step_review

def anchors():
    return [dict(zip(('frame',*FIELDS),row)) for row in [
        (252,0,0,.03,0,0,0),(302,0,0,.03,0,0,0),(327,-.8,.12,.18,-.18,.1,1),
        (331,-.79,.12,.18,-.18,.1,1),(342,-.45,.06,.08,0,.1,.5),
        (350,0,0,.03,0,0,0),(441,0,0,.03,0,0,0)]]

def test_motion_validation():
    edit={'kind':'supported_motion','target':'horse.rig','anchors':anchors()}
    assert validate(edit)==edit
    for row in ({'pitch':float('nan')},{'fold':2},{'frame':False},{'script':'bad'}):
        rows=anchors();rows[2].update(row)
        with pytest.raises(ValueError):validate(edit|{'anchors':rows})

def test_no_overshoot_and_no_descending_anchor_pause():
    rows=anchors()
    for f in range(252,442):
        result=sample(rows,f)
        for key in FIELDS:
            assert min(r[key] for r in rows)-1e-9<=result[key]<=max(r[key] for r in rows)+1e-9
    left=sample(rows,341.99)['pitch'];mid=sample(rows,342)['pitch'];right=sample(rows,342.01)['pitch']
    assert .02<(mid-left)/.01<.08
    assert (mid-left)/.01==pytest.approx((right-mid)/.01,rel=.01)

def test_frame_set_strict_limits():
    r={'operation':'nihang_frames','frame':327,'width':540,'height':960,'samples':8,'frames':[302,327,350]}
    assert control(r)==r
    for fs in ([327,327],[True,327],[1,327],list(range(320,340)),[302]):
        with pytest.raises(ValueError):control(r|{'frames':fs})

def test_cast_inspection_has_no_target_or_code():
    r={'operation':'nihang_cast_inspect','frame':283,'width':64,'height':64,'samples':1}
    assert control(r)==r
    with pytest.raises(ValueError):control(r|{'target':'accepted principal'})
    with pytest.raises(ValueError):control(r|{'code':'anything'})

def test_supporting_look_is_fixed_scope():
    from movie_factory.adapters.blender.nihang_patch import validate as patch
    r={'operation':'nihang_patch','frame':283,'width':432,'height':768,'samples':8,
       'edits':[{'kind':'supporting_look','target':'mounted leader'}]}
    assert patch(r)==r
    with pytest.raises(ValueError):patch(r|{'edits':[{'kind':'supporting_look','target':'accepted principal'}]})
    with pytest.raises(ValueError):patch(r|{'edits':[{'kind':'supporting_look','target':'mounted leader','code':'bad'}]})

def test_foreleg_preparation_and_distinct_contact():
    from movie_factory.adapters.blender.nihang_motion import foreleg_phases
    rows=anchors()
    assert foreleg_phases(rows,294)['L']['lift']>0
    assert foreleg_phases(rows,294)['R']['lift']==0
    assert foreleg_phases(rows,301)['R']['lift']>0
    assert foreleg_phases(rows,298)['L']['back']==pytest.approx(.03)
    assert foreleg_phases(rows,327)['L']['back']==0
    assert foreleg_phases(rows,350)['L']['fold']==0
    assert foreleg_phases(rows,350)['R']['fold']>0
    assert foreleg_phases(rows,351)['R']['fold']==0

@pytest.mark.parametrize('fault',[None,'path','hash','order','profile','missing'])
def test_frame_manifest_cannot_fake_success(setup,monkeypatch,fault):
    import json
    from pathlib import Path
    from PIL import Image
    from movie_factory.adapters.blender import runner
    from movie_factory.production_knowledge import file_hash
    root,c,bridge,calls=prepare(setup,monkeypatch,frame_set=True)
    saved=run(root,bridge);step_review(bridge,saved)
    worker=runner.run_blender
    def candidate(job,**kw):
        result=worker(job,**kw);out=Path(job['output_dir'])
        rows=json.loads((out/'frames.json').read_text())
        if fault=='path':rows[0]['file']='../frame.png'
        if fault=='hash':rows[0]['sha256']='bad'
        if fault=='order':rows.reverse()
        if fault=='profile':
            Image.new('RGB',(80,80)).save(out/rows[0]['file'])
            rows[0]['sha256']=file_hash(out/rows[0]['file'])
        if fault=='missing':(out/rows[0]['file']).unlink()
        (out/'frames.json').write_text(json.dumps(rows))
        return result
    monkeypatch.setattr(runner,'run_blender',candidate)
    result=run(root,bridge,'build',saved['artifacts']['native'])
    assert result['status']==('FAILED' if fault else 'RETURNED')
    if not fault:assert {'frame_300','frame_327','frame_350','frames'}<=set(result['artifacts'])
