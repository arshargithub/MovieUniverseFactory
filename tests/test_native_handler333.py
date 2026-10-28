"""Offline controls only. Fake Blender output is explicitly synthetic."""
import copy
import json
import pytest
from pathlib import Path
from PIL import Image
from movie_factory import native_admission as na, task_router as tr, production_workflow as wf
from movie_factory.adapters.blender import runner
from movie_factory.adapters.blender.nihang_control import validate
from test_production_workflow import setup, bind, direction
from test_task_router332 import request, step_review
import planning_fixtures as pf


def recipe(op='nihang_save'):
    return {'operation': op, 'frame': 327, 'width': 64, 'height': 64, 'samples': 1}


@pytest.mark.parametrize('bad', [None, {}, recipe() | {'code': 'print(1)'}, recipe() | {'frame': True},
    recipe() | {'frame': 1000}, recipe() | {'width': float('nan')}, recipe() | {'samples': 100},
    recipe('nihang_edit'), recipe() | {'camera': 'other'}])
def test_recipe_rejects_unbounded_or_edit_inputs(bad):
    with pytest.raises(ValueError): validate(bad)


def prepare(setup, monkeypatch, *, render_route=True, authoring=False, edit_route=True, inspection=False,frame_set=False,view=None):
    root, _, brief, _ = setup
    c = wf.Controller(root, tr.DATABASE)
    (root / 'parent.blend').write_bytes(b'SYNTHETIC BLEND')
    (root / 'texture.png').write_bytes(b'SYNTHETIC INPUT')
    for name, op in [('save.json', 'nihang_save'), ('render.json', 'nihang_render')]:
        value = recipe(op)
        if frame_set and op=='nihang_render':value.update(operation='nihang_frames',frames=[300,327,350])
        if view is not None and frame_set and op=='nihang_render':value['view']=view
        if inspection and op == 'nihang_save': value['operation'] = 'nihang_rig_inspect'
        if authoring and op == 'nihang_save':
            value.update(operation='nihang_patch', edits=[{'kind':'bone_pose', 'target':'horse.rig',
                'bone':'head', 'frame':327, 'quaternion':[1,0,0,0]}])
        (root / name).write_text(json.dumps(value))
        brief['source_bindings'][name] = bind(root, name)
    brief['source_bindings']['native'] = bind(root, 'parent.blend')
    from reference_fixtures378 import attach_transport
    attach_transport(root, brief)
    brief['offline_only'] = False
    req = request(root, ['native_inspect', 'render'] if render_route else ['native_inspect'])
    if authoring and edit_route: req['operations'].append('edit')
    c.route_request('request', req)
    c.create('t', 'production', req['authority'], 'create', direction=direction(brief),
             mode='local_native', admission='request')
    from governance_fixtures397 import attach
    attach(root,c,brief,recipes={'proof':bind(root,'save.json'),'build':bind(root,'render.json')})
    for stage in range(4):
        packet = c.packet('t'); response = pf.result(packet, brief)
        if packet['planning_step'] == 'STRATEGIZING':
            for step, name in zip(response['artifact']['steps'], ['save.json', 'render.json']):
                step['native_recipe'] = bind(root, name)
        c.submit('t', packet['actor'], packet['ticket'], response, 'plan' + str(stage))
    calls = []
    def worker(job, *, _admission, **kwargs):
        na.check_capability(_admission, job); calls.append(copy.deepcopy(job))
        out = Path(job['output_dir']); out.mkdir(parents=True)
        (out / 'snapshot.json').write_text('{"synthetic":true}')
        (out / 'script-diagnostics.json').write_text('{"synthetic":true}')
        (out / 'dependencies.json').write_text(json.dumps({'bindings': {'texture': bind(root, 'texture.png')}}))
        if job['recipe']['operation'] == 'nihang_rig_inspect':
            (out / 'rig.json').write_text('{"synthetic":true,"bones":{}}')
        elif job['recipe']['operation'] in {'nihang_save', 'nihang_patch'}:
            (out / 'scene.blend').write_bytes(b'SYNTHETIC DERIVATIVE')
            if authoring: (out / 'patch-evidence.json').write_text('{"synthetic":true}')
        else:
            Image.new('RGB', (64, 64), (40, 50, 60)).save(out / 'frame.png')
            if job['recipe']['operation']=='nihang_frames':
                from movie_factory.production_knowledge import file_hash
                manifest=[]
                for frame in job['recipe']['frames']:
                    name='frame.png' if frame==job['recipe']['frame'] else f'frame-{frame:04d}.png'
                    Image.new('RGB',(64,64),(40,50,60)).save(out/name)
                    manifest.append({'frame':frame,'file':name,'sha256':file_hash(out/name)})
                    if view is not None:manifest[-1].update(view=view,camera_matrix=[[int(i==j) for j in range(4)] for i in range(4)])
                (out/'frames.json').write_text(json.dumps(manifest))
        return {'ok': True}
    monkeypatch.setattr(runner, 'run_blender', worker)
    return root, c, na.Bridge(c), calls


def test_read_only_inventory_has_no_native_or_image_artifact(setup, monkeypatch):
    root, c, bridge, calls = prepare(setup, monkeypatch, inspection=True)
    inspected = run(root, bridge)
    assert inspected['status'] == 'RETURNED'
    assert 'rig' in inspected['artifacts']
    assert not {'native', 'frame'} & set(inspected['artifacts'])
    assert (root / 'parent.blend').read_bytes() == b'SYNTHETIC BLEND'


def run(root, bridge, step='proof', parent=None, **kw):
    return bridge.dispatch('t', step, step + '-run', parent=parent or bind(root, 'parent.blend'),
        blender_bin=na.BLENDER_BIN, recipe=bind(root, 'save.json' if step == 'proof' else 'render.json'), **kw)


def test_actual_native_dependency_and_fresh_render(setup, monkeypatch):
    root, c, bridge, calls = prepare(setup, monkeypatch)
    saved = run(root, bridge); assert saved['status'] == 'RETURNED'
    with pytest.raises(wf.Blocked, match='REVIEW_NOT_RUN'):
        run(root, bridge, 'build', saved['artifacts']['native'])
    step_review(bridge, saved)
    rendered = run(root, bridge, 'build', saved['artifacts']['native'])
    assert rendered['status'] == 'RETURNED' and len(calls) == 2
    step_review(bridge, rendered, 'FAIL')
    with pytest.raises(wf.Blocked, match='DEPENDENCY_REVIEW_FAILED'): bridge.qualified(rendered)
    assert (root / 'parent.blend').read_bytes() == b'SYNTHETIC BLEND'


def test_bound_recipe_cannot_be_omitted_or_substituted(setup, monkeypatch):
    root, c, bridge, calls = prepare(setup, monkeypatch)
    with pytest.raises(wf.Blocked, match='RECIPE_REQUIRED'):
        bridge.dispatch('t', 'proof', 'x', parent=bind(root, 'parent.blend'), blender_bin=na.BLENDER_BIN)
    with pytest.raises(wf.Blocked, match='UNPLANNED_NATIVE_RECIPE'):
        bridge.dispatch('t', 'proof', 'x', parent=bind(root, 'parent.blend'), blender_bin=na.BLENDER_BIN,
                        recipe=bind(root, 'render.json'))
    assert not calls


def test_changed_external_dependency_blocks_launch(setup, monkeypatch):
    root, c, bridge, calls = prepare(setup, monkeypatch)
    saved = run(root, bridge); step_review(bridge, saved)
    (root / 'texture.png').write_text('CHANGED')
    with pytest.raises(ValueError): run(root, bridge, 'build', saved['artifacts']['native'])
    assert len(calls) == 1


def test_render_must_use_reviewed_derivative_not_original(setup, monkeypatch):
    root, c, bridge, calls = prepare(setup, monkeypatch)
    saved = run(root, bridge); step_review(bridge, saved)
    with pytest.raises(wf.Blocked, match='REVIEWED_NATIVE'): run(root, bridge, 'build')
    assert len(calls) == 1


def test_render_route_required(setup, monkeypatch):
    root, c, bridge, calls = prepare(setup, monkeypatch, render_route=False)
    saved = run(root, bridge); step_review(bridge, saved)
    with pytest.raises(wf.Blocked, match='UNROUTED_RENDER'):
        run(root, bridge, 'build', saved['artifacts']['native'])
    assert len(calls) == 1


@pytest.mark.parametrize('fault', ['missing', 'corrupt_png', 'profile', 'state', 'dependencies'])
def test_worker_success_cannot_override_bad_artifacts(setup, monkeypatch, fault):
    root, c, bridge, calls = prepare(setup, monkeypatch)
    saved = run(root, bridge); step_review(bridge, saved)
    worker = runner.run_blender
    def broken(job, **kwargs):
        result = worker(job, **kwargs); out = Path(job['output_dir'])
        if fault == 'missing': (out / 'frame.png').unlink()
        if fault == 'corrupt_png': (out / 'frame.png').write_bytes(b'not an image')
        if fault == 'profile': Image.new('RGB', (80, 80)).save(out / 'frame.png')
        if fault == 'state': (out / 'snapshot.json').write_text('{"changed":true}')
        if fault == 'dependencies': (out / 'dependencies.json').write_text('{"bindings":{}}')
        return result
    monkeypatch.setattr(runner, 'run_blender', broken)
    bad = run(root, bridge, 'build', saved['artifacts']['native'])
    assert bad['status'] == 'FAILED'
    with pytest.raises(wf.Blocked): bridge.qualified(bad)
