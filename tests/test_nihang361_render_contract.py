"""Prepared render contract only; not an admitted production plan."""
import json
from pathlib import Path


def test_continuous_template_keeps_exact_frames_and_source_snapshot_pose():
    root=Path(__file__).resolve().parents[1]
    data=json.loads((root/'results/sikh361/CONTINUOUS_RENDER_TEMPLATE.json').read_text())
    assert data['status']=='PREPARED_NOT_ADMITTED_NOT_RENDERED'
    canonical=data['steps'][0]['recipe']['frame'];frames=set()
    for step in data['steps'][1:]:
        recipe=step['recipe']
        assert recipe['frame']==canonical and canonical in recipe['frames']
        assert len(recipe['frames'])<=16 and len(set(recipe['frames']))==len(recipe['frames'])
        frames.update(recipe['frames'])
    assert frames==set(range(252,377)) and data['fps']==24
