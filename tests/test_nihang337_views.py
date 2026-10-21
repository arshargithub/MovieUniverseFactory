"""Synthetic admission faults; never a perceptual/camera-framing qualification."""
import json
from pathlib import Path
import pytest
from test_production_workflow import setup
from test_native_handler333 import prepare,run
from test_task_router332 import step_review
from movie_factory.adapters.blender import runner


@pytest.mark.parametrize('fault',[None,'view','missing','nonfinite','shape'])
def test_diagnostic_manifest_cannot_mislabel_view(setup,monkeypatch,fault):
    root,c,bridge,calls=prepare(setup,monkeypatch,frame_set=True,view='leader_front')
    saved=run(root,bridge);step_review(bridge,saved)
    worker=runner.run_blender
    def candidate(job,**kwargs):
        result=worker(job,**kwargs);path=Path(job['output_dir'])/'frames.json'
        rows=json.loads(path.read_text())
        if fault=='view':rows[0]['view']='production'
        if fault=='missing':rows[0].pop('camera_matrix')
        if fault=='nonfinite':rows[0]['camera_matrix'][0][0]=float('nan')
        if fault=='shape':rows[0]['camera_matrix']=[[1]]
        path.write_text(json.dumps(rows))
        return result
    monkeypatch.setattr(runner,'run_blender',candidate)
    result=run(root,bridge,'build',saved['artifacts']['native'])
    assert result['status']==('FAILED' if fault else 'RETURNED')
