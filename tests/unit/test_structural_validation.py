import copy
import json
from pathlib import Path

import pytest

from movie_factory.validators import canonical_revision, srgb_hex_to_linear, validate_baseline, validate_plan, validate_revision
from movie_factory.validators.structural import compare_replay_snapshots

ROOT = Path(__file__).resolve().parents[2]


def matrix(position):
    return [[1, 0, 0, position[0]], [0, 1, 0, position[1]], [0, 0, 1, position[2]], [0, 0, 0, 1]]


def object_state(oid, entity, position, bounds=None, material_ids=None):
    geometry = {"vertices": [[0, 0, 0], [1, 0, 0], [0, 1, 0]], "faces": [[0, 1, 2]], "normals": [[0, 0, 1]]*3, "uv_layers": {}, "attributes": {}, "hash": "original-geometry"}
    return {"id": oid, "entity_id": entity, "parent_id": None if oid == entity else entity,
            "type": "MESH" if bounds else "EMPTY", "location": position.copy(), "rotation_euler": [0, 0, 0], "scale": [1, 1, 1], "matrix_local": matrix(position), "matrix_world": matrix(position), "bounds_world": bounds,
            "visible_render": True, "material_ids": material_ids or [], "collection_ids": ["scene"],
            "modifiers": [], "constraints": [], "animation": None, "drivers": [], "custom_properties": {"creation_id": "original"},
            "source_geometry": geometry if bounds else None, "evaluated_geometry": copy.deepcopy(geometry) if bounds else None}


@pytest.fixture
def plan():
    return json.loads((ROOT / "feasibility/3d/3d-01/fixtures/plan.json").read_text())


@pytest.fixture
def baseline(plan):
    s = {"schema_version": "1.0", "scene_id": plan["scene_id"], "entities": {}, "objects": {}, "materials": {}, "cameras": {"camera_A": {"lens_mm": 43}}, "lights": {"key": {"energy_w": 650}}, "world": {"strength": 0.12}, "render": {"engine": "CYCLES"}, "external_files": [], "unsupported": []}
    for item in plan["entities"]:
        oid = item["id"]
        x, y, z = item["position"]
        w, d, h = item["dimensions"]
        bounds = {"min": [x-w/2, y-d/2, z], "max": [x+w/2, y+d/2, z+h]}
        part = oid + "_body"
        root = object_state(oid, oid, item["position"])
        body = object_state(part, oid, [0, 0, 0], bounds, ["helmet_shell_01"] if oid == "helmet_01" else [])
        body["matrix_world"] = matrix(item["position"])
        s["objects"].update({oid: root, part: body})
        s["entities"][oid] = {"id": oid, "root_id": oid, "kind": item["kind"], "position": item["position"].copy(), "rotation_euler": [0,0,0], "scale": [1,1,1], "object_ids": [oid, part], "bounds_world": bounds}
    seat = object_state("sofa_seat", "sofa_01", [0,0,0], {"min": [-1.1, 0.5, 0.48], "max": [1.1, 1.4, 0.648]})
    s["objects"]["sofa_seat"] = seat
    s["entities"]["sofa_01"]["object_ids"].append("sofa_seat")
    s["objects"]["room_floor"] = object_state("room_floor", "room_01", [0,0,0], {"min": [-2.5,-2,-0.1], "max": [2.5,2,0]})
    color = srgb_hex_to_linear("#C62828")
    s["materials"]["helmet_shell_01"] = {"base_color_linear": color, "roughness": 0.22, "nodes": {"Principled BSDF": {"inputs": {"Base Color": color, "Roughness": 0.22}}}}
    return s


def independently_revise(baseline, distance=0.4):
    """Simple +Y fixture oracle, intentionally independent of validator math."""
    after = copy.deepcopy(baseline)
    entity = after["entities"]["coffee_table_01"]
    entity["position"][1] += distance
    entity["bounds_world"] = copy.deepcopy(entity["bounds_world"])
    for edge in ("min", "max"):
        entity["bounds_world"][edge][1] += distance
    for oid in entity["object_ids"]:
        obj = after["objects"][oid]
        obj["matrix_world"][1][3] += distance
        if obj["bounds_world"]:
            obj["bounds_world"] = copy.deepcopy(obj["bounds_world"])
            for edge in ("min", "max"):
                obj["bounds_world"][edge][1] += distance
        if oid == entity["root_id"]:
            obj["location"][1] += distance
            obj["matrix_local"][1][3] += distance
    color = srgb_hex_to_linear("#163D2A")
    after["materials"]["helmet_shell_01"]["base_color_linear"] = color
    after["materials"]["helmet_shell_01"]["nodes"]["Principled BSDF"]["inputs"]["Base Color"] = color
    return after


def test_fixture_and_exact_revision_pass(baseline, plan):
    assert not validate_plan(plan)
    assert validate_baseline(baseline, plan)["passed"]
    result = validate_revision(baseline, independently_revise(baseline), canonical_revision())
    assert result["passed"], result


@pytest.mark.parametrize("distance", [-0.4, 0.004, 0.8, 0.0, 0.4002])
def test_wrong_translation_rejected(baseline, distance):
    assert not validate_revision(baseline, independently_revise(baseline, distance), canonical_revision())["passed"]


def test_documented_translation_tolerance(baseline):
    assert validate_revision(baseline, independently_revise(baseline, 0.40001), canonical_revision())["passed"]


@pytest.mark.parametrize("mutation", [
    lambda s: s["cameras"]["camera_A"].update(lens_mm=44),
    lambda s: s["lights"]["key"].update(energy_w=651),
    lambda s: s["objects"]["sofa_01_body"].update(visible_render=False),
    lambda s: s["objects"]["coffee_table_01_body"]["source_geometry"]["vertices"][0].__setitem__(0, 0.02),
    lambda s: s["objects"]["helmet_01_body"]["evaluated_geometry"]["normals"][0].__setitem__(0, 0.1),
    lambda s: s["materials"]["helmet_shell_01"].update(roughness=0.25),
    lambda s: s["materials"]["helmet_shell_01"]["base_color_linear"].__setitem__(3, 0.5),
    lambda s: s["objects"]["coffee_table_01_body"]["custom_properties"].update(creation_id="recreated"),
    lambda s: s["objects"]["coffee_table_01_body"].update(parent_id="sofa_01"),
    lambda s: s["render"].update(unknown_protected_field="surprise"),
    lambda s: s["world"].update(strength=float("nan")),
])
def test_negative_mutations_fail_independent_state_diff(baseline, mutation):
    after = independently_revise(baseline)
    mutation(after)
    assert not validate_revision(baseline, after, canonical_revision())["passed"]


def test_shared_shell_material_rejected_at_baseline(baseline, plan):
    baseline["objects"]["sofa_01_body"]["material_ids"].append("helmet_shell_01")
    result = validate_baseline(baseline, plan)
    assert "helmet.private_shell_material" in result["errors"]


def test_missing_coverage_is_not_a_pass(baseline):
    del baseline["objects"]["helmet_01_body"]["source_geometry"]
    assert not validate_revision(baseline, independently_revise(baseline), canonical_revision())["passed"]


def test_helmet_floating_rejected(baseline, plan):
    baseline["entities"]["helmet_01"]["bounds_world"]["min"][2] += 0.01
    assert not validate_baseline(baseline, plan)["passed"]


def test_unknown_operation_field_rejected(baseline):
    operations = canonical_revision()
    operations["operations"][0]["script"] = "untrusted"
    assert not validate_revision(baseline, independently_revise(baseline), operations)["passed"]


def test_baseline_cannot_intersect_target(plan):
    plan["entities"][1]["position"][1] = 0.1
    assert any("intersects" in message for message in validate_plan(plan))


def test_qualification_camera_and_neutral_lighting_are_frozen(plan):
    plan["cameras"][1]["lens_mm"] = 50
    plan["lights"][0]["color_hex"] = "#163D2A"
    errors = validate_plan(plan)
    assert any("camera rig" in message for message in errors)
    assert any("light rig" in message for message in errors)


def test_palette_conversion_is_linear():
    assert srgb_hex_to_linear("#FFFFFF") == [1.0]*4
    assert srgb_hex_to_linear("#000000") == [0,0,0,1]
    assert srgb_hex_to_linear("#808080")[0] == pytest.approx(0.2158605)
    assert srgb_hex_to_linear("#163D2A")[1] == pytest.approx(0.0466650863)


def test_replay_comparison_ignores_mesh_index_permutation(baseline):
    after = copy.deepcopy(baseline)
    obj = after["objects"]["coffee_table_01_body"]
    for field in ("source_geometry", "evaluated_geometry"):
        geometry = obj[field]
        geometry["vertices"] = [geometry["vertices"][2], geometry["vertices"][0], geometry["vertices"][1]]
        geometry["normals"] = [geometry["normals"][2], geometry["normals"][0], geometry["normals"][1]]
        geometry["faces"] = [[1, 2, 0]]
        geometry["hash"] = "different-index-order"
    assert compare_replay_snapshots(baseline, after)["passed"]


def test_replay_comparison_rejects_geometry_change(baseline):
    after = copy.deepcopy(baseline)
    after["objects"]["coffee_table_01_body"]["source_geometry"]["vertices"][0][0] = 0.1
    assert not compare_replay_snapshots(baseline, after)["passed"]
