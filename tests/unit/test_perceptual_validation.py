import json

import numpy as np
from PIL import Image

from movie_factory.validators import compare_renders


def write_stage(path, damage=False, hidden=False, corrupt=False):
    (path / "renders").mkdir(parents=True)
    (path / "masks").mkdir()
    rng = np.random.default_rng(10)
    beauty = rng.integers(40, 200, (120, 200, 3), dtype=np.uint8)
    mask = np.zeros_like(beauty)
    mask[20:40, 80:100] = [255,0,0]
    mask[60:90, 70:130] = [0,255,0]
    if damage:
        beauty[20:40, 80:100] = [0,0,0]
    if hidden:
        mask[20:40, 80:100] = 0
    Image.fromarray(beauty).save(path / "renders/shot_A.png")
    Image.fromarray(mask).save(path / "masks/shot_A.png")
    (path / "mask-legend.json").write_text(json.dumps({"schema_version": "1.0", "encoding": "rgb8", "entities": {"helmet_01": [255,0,0], "coffee_table_01": [0,255,0]}}))
    if corrupt:
        (path / "renders/shot_A.png").write_bytes(b"not a PNG")


def test_identical_reference_passes_with_visible_crops(tmp_path):
    write_stage(tmp_path / "actual")
    write_stage(tmp_path / "expected")
    result = compare_renders(tmp_path / "actual", tmp_path / "expected")
    assert result["passed"], result
    assert result["shots"]["shot_A"]["regions"]["helmet"]["ssim"] == 1.0


def test_small_object_damage_not_hidden_by_full_frame_average(tmp_path):
    write_stage(tmp_path / "actual", damage=True)
    write_stage(tmp_path / "expected")
    result = compare_renders(tmp_path / "actual", tmp_path / "expected")
    assert result["color"] == "RED"
    assert result["shots"]["shot_A"]["regions"]["helmet"]["color"] == "RED"


def test_identical_beauty_does_not_override_missing_helmet_mask(tmp_path):
    write_stage(tmp_path / "actual", hidden=True)
    write_stage(tmp_path / "expected")
    result = compare_renders(tmp_path / "actual", tmp_path / "expected")
    assert not result["passed"]
    assert any("visibility" in error for error in result["errors"])


def test_corrupt_png_fails(tmp_path):
    write_stage(tmp_path / "actual", corrupt=True)
    write_stage(tmp_path / "expected")
    assert not compare_renders(tmp_path / "actual", tmp_path / "expected")["passed"]


def test_changed_legend_fails(tmp_path):
    write_stage(tmp_path / "actual")
    write_stage(tmp_path / "expected")
    (tmp_path / "actual/mask-legend.json").write_text(json.dumps({"encoding": "rgb8", "entities": {"helmet_01": [0,255,0], "coffee_table_01": [255,0,0]}}))
    assert not compare_renders(tmp_path / "actual", tmp_path / "expected")["passed"]
