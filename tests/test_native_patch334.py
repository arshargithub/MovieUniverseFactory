import copy
import json
import math
import pytest
from movie_factory.adapters.blender.nihang_patch import validate
from movie_factory import production_workflow as wf, production_knowledge as pk
from test_production_workflow import setup
from test_native_handler333 import prepare, run, recipe


def patch():
    return recipe('nihang_patch') | {'edits': [{'kind':'bone_pose', 'target':'horse.rig',
        'bone':'head', 'frame':327, 'quaternion':[1,0,0,0]}]}


def test_valid_numeric_pose_and_mesh():
    p = patch(); assert validate(p) == p
    p['edits'].append({'kind':'mesh', 'target':'MF Nihang test', 'vertices':[[0,0,0],[1,0,0],[0,1,0]],
                       'faces':[[0,1,2]], 'color':[.1,.2,.3,1], 'roughness':.7})
    assert validate(p) == p


@pytest.mark.parametrize('fault', ['code', 'nan', 'quaternion', 'wrong_target', 'frame', 'empty', 'unknown', 'path', 'bool'])
def test_patch_rejects_invalid_or_executable_input(fault):
    p=patch(); e=p['edits'][0]
    if fault=='code': p['code']='print(1)'
    if fault=='nan': e['quaternion']=[float('nan'),0,0,0]
    if fault=='quaternion': e['quaternion']=[.5,0,0,0]
    if fault=='wrong_target': e['target']='accepted principal'
    if fault=='frame': e['frame']=1
    if fault=='empty': p['edits']=[]
    if fault=='unknown': e['kind']='exec'
    if fault=='path': e['target']='../source'
    if fault=='bool': e['quaternion']=[True,0,0,0]
    with pytest.raises(ValueError): validate(p)


def test_negative_control_known_defects_cannot_pass(setup,monkeypatch):
    from test_task_router332 import step_review
    from movie_factory.adapters.blender import runner
    root,c,bridge,calls=prepare(setup,monkeypatch)
    worker=runner.run_blender
    def faulty(job,**kwargs):
        result=worker(job,**kwargs)
        from pathlib import Path
        (Path(job['output_dir'])/'script-diagnostics.json').write_text('{"known_source_defects":["legacy"]}')
        return result
    monkeypatch.setattr(runner,'run_blender',faulty)
    saved=run(root,bridge); step_review(bridge,saved)
    rendered=run(root,bridge,'build',saved['artifacts']['native'])
    assert rendered['status']=='RETURNED'
    with pytest.raises(wf.Blocked,match='KNOWN_NATIVE_DEFECT'): step_review(bridge,rendered)
    step_review(bridge,rendered,'FAIL')


def test_authoring_requires_routed_edit(setup,monkeypatch):
    root,c,bridge,calls=prepare(setup,monkeypatch,authoring=True,edit_route=False)
    with pytest.raises(wf.Blocked,match='UNROUTED_NATIVE_EDIT'): run(root,bridge)
    assert not calls


def test_authoring_output_requires_review_before_render(setup,monkeypatch):
    from test_task_router332 import step_review
    root,c,bridge,calls=prepare(setup,monkeypatch,authoring=True)
    saved=run(root,bridge)
    assert saved['status']=='RETURNED' and 'patch' in saved['artifacts']
    assert calls[0]['mode']=='nihang_patch'
    with pytest.raises(wf.Blocked,match='REVIEW_NOT_RUN'):
        run(root,bridge,'build',saved['artifacts']['native'])
    step_review(bridge,saved)
    assert run(root,bridge,'build',saved['artifacts']['native'])['status']=='RETURNED'
