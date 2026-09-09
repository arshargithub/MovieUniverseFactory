"""Independent, fail-closed state checks for the bounded original fixture vocabulary.

Coordinates are metres; source and evaluated geometry are object-local. The native
inspector is responsible for complete extraction. This module never trusts the
worker's success flag or planner-provided expected targets.
"""
from __future__ import annotations

import copy
import math
from typing import Any

EPSILON = 1e-6
TRANSLATION_TOLERANCE_M = 1e-4
ENTITIES = {"sofa_01": "sofa", "coffee_table_01": "coffee_table", "floor_lamp_01": "floor_lamp", "helmet_01": "motorcycle_helmet"}
SHELL = "helmet_shell_01"
SEAT_HEIGHT_RATIO = 0.54
QUALIFICATION_CAMERAS = {
    "camera_A": {"shot_id": "shot_A", "position": [3.6, -5.4, 2.55], "target": [0.0, 0.55, 0.75], "lens_mm": 43.0},
    "camera_B": {"shot_id": "shot_B", "position": [-3.15, -3.1, 1.65], "target": [0.1, 0.6, 0.8], "lens_mm": 42.0},
    "camera_C": {"shot_id": "shot_C", "position": [1.65, -0.55, 1.35], "target": [0.68, 0.9, 0.85], "lens_mm": 62.0},
}
QUALIFICATION_LIGHTS = {
    "key_light_01": {"type": "AREA", "position": [-2.0, -1.5, 3.4], "target": [0.0, 0.7, 0.6], "color_hex": "#FFF0D9", "energy_w": 650.0, "size_m": 3.0},
    "fill_light_01": {"type": "AREA", "position": [2.8, -0.8, 2.8], "target": [0.0, 0.8, 0.8], "color_hex": "#D3E4FF", "energy_w": 250.0, "size_m": 2.5},
}


def srgb_hex_to_linear(value: str) -> list[float]:
    if not isinstance(value, str) or len(value) != 7 or value[0] != "#":
        raise ValueError("Expected #RRGGBB sRGB color")
    values = [int(value[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    return [v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in values] + [1.0]


def canonical_revision(before: dict | None = None) -> dict:
    return {"operations": [
        {"op": "translate_toward", "entity_id": "coffee_table_01", "target_entity_id": "sofa_01", "distance_m": 0.4},
        {"op": "set_base_color", "entity_id": "helmet_01", "material_id": SHELL, "color_hex": "#163D2A"},
    ]}


def _finite(value: Any) -> bool:
    if isinstance(value, float):
        return math.isfinite(value)
    if isinstance(value, dict):
        return all(_finite(v) for v in value.values())
    if isinstance(value, list):
        return all(_finite(v) for v in value)
    return True


def _near(a: Any, b: Any, tolerance: float = EPSILON) -> bool:
    return not _diff(a, b, tolerance=tolerance)


def _diff(before: Any, after: Any, path: str = "$", tolerance: float = EPSILON) -> list[dict]:
    """All unknown fields are protected. Numbers have an absolute-only tolerance."""
    differences = []
    if isinstance(before, bool) or isinstance(after, bool):
        if type(before) is not type(after) or before != after:
            differences.append({"path": path, "before": before, "after": after})
    elif isinstance(before, (float, int)) and isinstance(after, (float, int)):
        delta = abs(after - before)
        if not math.isfinite(delta) or delta > tolerance:
            differences.append({"path": path, "before": before, "after": after, "delta": delta if math.isfinite(delta) else None})
    elif type(before) is not type(after):
        differences.append({"path": path, "before_type": type(before).__name__, "after_type": type(after).__name__})
    elif isinstance(before, dict):
        for key in sorted(before.keys() | after.keys()):
            child = f"{path}.{key}"
            if key not in before or key not in after:
                differences.append({"path": child, "missing_in": "before" if key not in before else "after"})
            else:
                differences.extend(_diff(before[key], after[key], child, tolerance))
    elif isinstance(before, list):
        if len(before) != len(after):
            differences.append({"path": path, "before_length": len(before), "after_length": len(after)})
        else:
            for index, (a, b) in enumerate(zip(before, after)):
                differences.extend(_diff(a, b, f"{path}[{index}]", tolerance))
    elif before != after:
        differences.append({"path": path, "before": before, "after": after})
    return differences


def compare_snapshots(before: dict, after: dict) -> dict:
    differences = _diff(before, after)
    return {"passed": not differences, "differences": differences, "max_numeric_delta": max((d.get("delta") or 0 for d in differences), default=0)}


def _stable_geometry(geometry: dict | None) -> dict | None:
    """Represent mesh semantics without depending on Blender element indices.

    Blender can assign different vertex, edge, face, UV-loop, and built-in
    attribute indices when identical procedural primitives are rebuilt in separate
    processes. Replay still compares complete topology, coordinates, normals,
    material slots, and smoothing, but keys them by coordinates so an index
    permutation is harmless. UV values are omitted because this experiment
    forbids texture nodes and external images; layer presence and size remain
    protected.
    """
    if geometry is None:
        return None
    vertices = geometry.get("vertices", [])

    def coordinate(index: int) -> tuple:
        return tuple(vertices[index])

    sorted_vertex_records = sorted(
        (coordinate(index), tuple(normal))
        for index, normal in enumerate(geometry.get("normals", []))
    )
    sorted_edge_records = sorted(
        tuple(sorted((coordinate(edge[0]), coordinate(edge[1]))))
        for edge in geometry.get("edges", [])
    )
    sorted_polygon_records = []
    faces = geometry.get("faces", [])
    normals = geometry.get("polygon_normals", [])
    material_indices = geometry.get("polygon_material_indices", [])
    smooth = geometry.get("polygon_smooth", [])
    for index, face in enumerate(faces):
        sorted_polygon_records.append((
            tuple(sorted(coordinate(vertex) for vertex in face)),
            tuple(normals[index]) if index < len(normals) else None,
            material_indices[index] if index < len(material_indices) else None,
            smooth[index] if index < len(smooth) else None,
        ))
    return {
        "vertex_records": [[list(position), list(normal)] for position, normal in sorted_vertex_records],
        "edge_records": [[list(start), list(end)] for start, end in sorted_edge_records],
        "polygon_records": [
            {
                "vertices": [list(position) for position in positions],
                "normal": list(normal) if normal is not None else None,
                "material_index": material_index,
                "smooth": is_smooth,
            }
            for positions, normal, material_index, is_smooth in sorted(sorted_polygon_records)
        ],
        "uv_layers": {
            name: len(data)
            for name, data in sorted(geometry.get("uv_layers", {}).items())
        },
        "attributes": {
            name: {
                "domain": attr.get("domain"),
                "data_type": attr.get("data_type"),
                "count": len(attr.get("data", [])),
            }
            for name, attr in sorted(geometry.get("attributes", {}).items())
        },
    }


def canonical_replay_snapshot(snapshot: dict) -> dict:
    """Canonicalize only the index-unstable mesh fields used by offline replay."""
    result = copy.deepcopy(snapshot)
    for obj in result.get("objects", {}).values():
        obj.pop("geometry_hash", None)
        obj["source_geometry"] = _stable_geometry(obj.get("source_geometry"))
        obj["evaluated_geometry"] = _stable_geometry(obj.get("evaluated_geometry"))
    return result


def compare_replay_snapshots(before: dict, after: dict) -> dict:
    """Compare independently rebuilt scenes while preserving production meaning."""
    differences = _diff(
        canonical_replay_snapshot(before), canonical_replay_snapshot(after)
    )
    return {
        "passed": not differences,
        "differences": differences,
        "max_numeric_delta": max(
            (difference.get("delta") or 0 for difference in differences), default=0
        ),
    }


def _check(checks: list, name: str, passed: bool, details: Any = None) -> None:
    checks.append({"name": name, "passed": bool(passed), "details": details})


def _result(checks: list) -> dict:
    return {"passed": all(check["passed"] for check in checks), "checks": checks,
            "errors": [check["name"] for check in checks if not check["passed"]]}


def _bounds(entity: dict, delta: list | None = None) -> dict:
    result = copy.deepcopy(entity["bounds_world"])
    if delta:
        for key in ("min", "max"):
            result[key] = [a + b for a, b in zip(result[key], delta)]
    return result


def _overlap(a: dict, b: dict) -> bool:
    return all(min(a["max"][i], b["max"][i]) - max(a["min"][i], b["min"][i]) > EPSILON for i in range(3))


def _delta(table: list, sofa: list) -> list:
    dx, dy = sofa[0] - table[0], sofa[1] - table[1]
    length = math.hypot(dx, dy)
    if length < 1e-4:
        raise ValueError("Table and sofa anchors have no meaningful horizontal direction")
    return [0.4 * dx / length, 0.4 * dy / length, 0.0]


def _plan_bounds(entity: dict) -> dict:
    x, y, z = entity["position"]
    w, d, h = entity["dimensions"]
    angle = entity["rotation_z"]
    rx = (abs(math.cos(angle)) * w + abs(math.sin(angle)) * d) / 2
    ry = (abs(math.sin(angle)) * w + abs(math.cos(angle)) * d) / 2
    return {"min": [x-rx, y-ry, z], "max": [x+rx, y+ry, z+h]}


def validate_plan(plan: dict) -> list[str]:
    errors = []
    if not _finite(plan):
        return ["Plan has non-finite numbers"]
    try:
        by_id = {entity["id"]: entity for entity in plan["entities"]}
        if len(by_id) != 4 or len(plan["entities"]) != 4 or set(by_id) != set(ENTITIES):
            errors.append("Plan requires exactly the four distinct canonical entity IDs")
        if {e["id"]: e["kind"] for e in plan["entities"]} != ENTITIES:
            errors.append("Entity kinds must match the canonical identity map")
        cameras = plan["cameras"]
        if len(cameras) != 3 or {(c["id"], c["shot_id"]) for c in cameras} != {(f"camera_{s}", f"shot_{s}") for s in "ABC"}:
            errors.append("Exactly camera_A/B/C bound to shot_A/B/C are required")
        for camera in cameras:
            expected = QUALIFICATION_CAMERAS.get(camera["id"])
            if expected is None or not all(_near(camera.get(field), expected[field]) for field in expected):
                errors.append(f"{camera['id']} must use the frozen qualification camera rig")
        lights = plan["lights"]
        if {light["id"] for light in lights} != set(QUALIFICATION_LIGHTS) or len(lights) != 2:
            errors.append("Exactly the two frozen neutral qualification lights are required")
        else:
            for light in lights:
                expected = QUALIFICATION_LIGHTS[light["id"]]
                if not all(_near(light.get(field), expected[field]) for field in expected):
                    errors.append(f"{light['id']} must use the frozen neutral qualification light rig")
        if not _near(plan["world_strength"], 0.12) or not _near(plan["exposure"], 0.0):
            errors.append("World strength and exposure must use the frozen qualification values")
        all_ids = list(by_id) + [c["id"] for c in cameras] + [light["id"] for light in plan["lights"]]
        if len(set(all_ids)) != len(all_ids):
            errors.append("Entity, light, and camera IDs must be globally unique")
        for camera in cameras:
            if math.dist(camera["position"], camera["target"]) < 1e-4:
                errors.append(f"{camera['id']} has no viewing direction")
        sofa, table, helmet = (by_id[key] for key in ("sofa_01", "coffee_table_01", "helmet_01"))
        if helmet["color_hex"].upper() != "#C62828":
            errors.append("Initial helmet shell must be palette red #C62828")
        if not _near(helmet["position"][2], sofa["position"][2] + SEAT_HEIGHT_RATIO * sofa["dimensions"][2]):
            errors.append("Helmet base must contact the sofa seat at 0.54 times sofa height")
        for key in ("sofa_01", "coffee_table_01", "floor_lamp_01"):
            if abs(by_id[key]["position"][2]) > EPSILON:
                errors.append(f"{key} must have floor contact at z=0")
        delta = _delta(table["position"], sofa["position"])
        table_bounds, sofa_bounds = _plan_bounds(table), _plan_bounds(sofa)
        target_bounds = {k: [v + d for v, d in zip(table_bounds[k], delta)] for k in ("min", "max")}
        if _overlap(table_bounds, sofa_bounds) or _overlap(target_bounds, sofa_bounds):
            errors.append("Table baseline/target intersects sofa's conservative collision box")
        room = plan["room"]["size_m"]
        for name, bound in [(e["id"], _plan_bounds(e)) for e in plan["entities"]] + [("table target", target_bounds)]:
            if any(bound["min"][i] < -room[i]/2 - EPSILON or bound["max"][i] > room[i]/2 + EPSILON for i in (0, 1)) or bound["max"][2] > room[2] + EPSILON:
                errors.append(f"{name} exceeds the room interior bounds")
    except (KeyError, TypeError, ValueError, IndexError) as exc:
        errors.append(f"Incomplete or invalid semantic plan: {type(exc).__name__}")
    return errors


def _snapshot_coverage(snapshot: dict, checks: list) -> None:
    required = {"schema_version", "scene_id", "entities", "objects", "materials", "cameras", "lights", "world", "render", "external_files", "unsupported"}
    _check(checks, "snapshot.required_sections", not (required - snapshot.keys()), sorted(required - snapshot.keys()))
    _check(checks, "snapshot.finite", _finite(snapshot))
    _check(checks, "snapshot.supported_features", snapshot.get("unsupported") == [], snapshot.get("unsupported"))
    _check(checks, "snapshot.no_external_dependencies", snapshot.get("external_files") == [], snapshot.get("external_files"))
    for object_id, obj in snapshot.get("objects", {}).items():
        fields = {"id", "entity_id", "parent_id", "type", "location", "rotation_euler", "scale", "matrix_local", "matrix_world", "visible_render", "material_ids", "collection_ids", "modifiers", "constraints", "animation", "drivers", "custom_properties"}
        _check(checks, f"coverage.object.{object_id}", not (fields - obj.keys()), sorted(fields - obj.keys()))
        if obj.get("type") == "MESH":
            for geometry_name in ("source_geometry", "evaluated_geometry"):
                geometry = obj.get(geometry_name, {})
                _check(checks, f"coverage.{object_id}.{geometry_name}", all(key in geometry for key in ("vertices", "faces", "normals", "uv_layers", "attributes", "hash")))


def _physical_checks(snapshot: dict, checks: list, target_delta: list | None = None) -> None:
    entities = snapshot["entities"]
    table = _bounds(entities["coffee_table_01"], target_delta)
    sofa = _bounds(entities["sofa_01"])
    helmet = _bounds(entities["helmet_01"])
    label = "target" if target_delta else "current"
    _check(checks, f"physical.{label}.table_sofa_clearance", not _overlap(table, sofa), {"table_bounds": table, "sofa_bounds": sofa, "method": "disjoint evaluated-mesh AABBs prove no mesh intersection; ambiguous AABB overlap is conservatively rejected"})
    for entity_id in ("sofa_01", "coffee_table_01", "floor_lamp_01"):
        bound = table if entity_id == "coffee_table_01" else _bounds(entities[entity_id])
        _check(checks, f"physical.{label}.{entity_id}.floor_contact", abs(bound["min"][2]) <= TRANSLATION_TOLERANCE_M, {"bottom_z": bound["min"][2]})
    # The original procedural builder's seat is flat. Require contact and the full
    # helmet footprint inside its seat surface; a generic support claim is not made.
    seat_parts = [obj for obj in snapshot["objects"].values() if obj.get("entity_id") == "sofa_01" and "seat" in obj.get("id", "").lower() and "bounds_world" in obj]
    support = []
    for obj in seat_parts:
        seat = obj["bounds_world"]
        contact = abs(helmet["min"][2] - seat["max"][2]) <= TRANSLATION_TOLERANCE_M
        contained = all(helmet["min"][i] >= seat["min"][i] - EPSILON and helmet["max"][i] <= seat["max"][i] + EPSILON for i in (0, 1))
        support.append({"seat_id": obj["id"], "contact": contact, "footprint_contained": contained, "gap_m": helmet["min"][2]-seat["max"][2]})
    _check(checks, "physical.helmet_supported_by_stationary_seat", any(s["contact"] and s["footprint_contained"] for s in support), support)
    # Room parameters are saved on the root; use actual room floor bounds where available.
    floors = [obj for obj in snapshot["objects"].values() if obj.get("entity_id") == "room_01" and "floor" in obj.get("id", "").lower() and "bounds_world" in obj]
    if floors:
        room = floors[0]["bounds_world"]
        inside = all(table["min"][i] >= room["min"][i] - EPSILON and table["max"][i] <= room["max"][i] + EPSILON for i in (0, 1))
        _check(checks, f"physical.{label}.table_within_room", inside, {"room_floor": room, "table": table})
    else:
        _check(checks, f"physical.{label}.table_within_room", False, "Missing authoritative room floor geometry")


def validate_baseline(snapshot: dict, plan: dict) -> dict:
    checks = []
    _snapshot_coverage(snapshot, checks)
    _check(checks, "plan.semantic_constraints", not (errors := validate_plan(plan)), errors)
    try:
        entities = snapshot["entities"]
        _check(checks, "identity.required_entities", set(ENTITIES) <= set(entities), sorted(entities))
        _check(checks, "identity.scene", snapshot["scene_id"] == plan["scene_id"])
        for item in plan["entities"]:
            entity = entities[item["id"]]
            _check(checks, f"identity.{item['id']}.kind", entity["kind"] == item["kind"])
            _check(checks, f"transform.{item['id']}.position", _near(entity["position"], item["position"]), {"actual": entity["position"], "planned": item["position"]})
            _check(checks, f"identity.{item['id']}.assembly", entity["root_id"] in snapshot["objects"] and len(set(entity["object_ids"])) == len(entity["object_ids"]) and all(snapshot["objects"][part]["entity_id"] == item["id"] for part in entity["object_ids"]))
        shell = snapshot["materials"][SHELL]
        _check(checks, "helmet.initial_linear_red", _near(shell["base_color_linear"], srgb_hex_to_linear("#C62828")))
        users = [object_id for object_id, obj in snapshot["objects"].items() if SHELL in obj["material_ids"]]
        _check(checks, "helmet.private_shell_material", bool(users) and all(snapshot["objects"][user]["entity_id"] == "helmet_01" for user in users), users)
        for entity_id in ENTITIES:
            meshes = [snapshot["objects"][part] for part in entities[entity_id]["object_ids"] if snapshot["objects"][part]["type"] == "MESH"]
            _check(checks, f"visibility.{entity_id}.render_enabled", bool(meshes) and all(obj["visible_render"] for obj in meshes))
        _physical_checks(snapshot, checks)
        delta = _delta(entities["coffee_table_01"]["position"], entities["sofa_01"]["position"])
        _physical_checks(snapshot, checks, delta)
    except (KeyError, TypeError, ValueError, IndexError) as exc:
        _check(checks, "snapshot.malformed", False, f"{type(exc).__name__}: {exc}")
    return _result(checks)


def _translate_matrix(matrix: list, delta: list) -> list:
    output = copy.deepcopy(matrix)
    if len(output) == 4 and all(isinstance(row, list) and len(row) == 4 for row in output):
        for i in range(3):
            output[i][3] += delta[i]
        return output
    raise ValueError("Inspector matrix must be row-major 4x4")


def _expected_revision(before: dict, accepted_delta: list | None = None) -> tuple[dict, list]:
    expected = copy.deepcopy(before)
    table = expected["entities"]["coffee_table_01"]
    delta = accepted_delta if accepted_delta is not None else _delta(table["position"], expected["entities"]["sofa_01"]["position"])
    root_id = table["root_id"]
    for object_id in table["object_ids"]:
        obj = expected["objects"][object_id]
        obj["matrix_world"] = _translate_matrix(obj["matrix_world"], delta)
        if obj.get("bounds_world"):
            obj["bounds_world"] = _bounds(obj, delta)
        if object_id == root_id:
            if obj["parent_id"] is not None:
                raise ValueError("Table root must be unparented for world-space translation")
            obj["location"] = [a+b for a, b in zip(obj["location"], delta)]
            obj["matrix_local"] = _translate_matrix(obj["matrix_local"], delta)
    table["position"] = [a+b for a, b in zip(table["position"], delta)]
    table["bounds_world"] = _bounds(table, delta)
    material = expected["materials"][SHELL]
    color = srgb_hex_to_linear("#163D2A")
    material["base_color_linear"] = color
    material["nodes"]["Principled BSDF"]["inputs"]["Base Color"] = color
    # Bookkeeping fields must be individually agreed and explicit. No broad metadata exclusion.
    if "scene_version" in expected:
        expected["scene_version"] += 1
    return expected, delta


def validate_revision(before: dict, after: dict, operations: list | dict) -> dict:
    checks = []
    _snapshot_coverage(before, checks)
    _snapshot_coverage(after, checks)
    actual_operations = operations.get("operations") if isinstance(operations, dict) else operations
    canonical_operations = canonical_revision()["operations"]
    # Order does not change the semantics of these two independent operations.
    valid_ops = isinstance(actual_operations, list) and len(actual_operations) == 2 and all(op in canonical_operations for op in actual_operations) and len({op.get("op") for op in actual_operations if isinstance(op, dict)}) == 2
    _check(checks, "revision.canonical_operations", valid_ops, actual_operations)
    try:
        old_position = before["entities"]["coffee_table_01"]["position"]
        position = after["entities"]["coffee_table_01"]["position"]
        displacement = [a-b for a, b in zip(position, old_position)]
        delta = _delta(old_position, before["entities"]["sofa_01"]["position"])
        # Use the observed horizontal displacement for the rigid-body consistency
        # check; a separate target gate enforces the 1e-4 m target tolerance. Z,
        # rotation, scale and all source geometry remain protected at 1e-6.
        expected, _ = _expected_revision(before, [displacement[0], displacement[1], 0.0])
        differences = _diff(expected, after)
        _check(checks, "revision.deny_by_default_state_diff", not differences, {"differences": differences, "max_numeric_delta": max((d.get("delta") or 0 for d in differences), default=0), "protected_tolerance": EPSILON})
        _check(checks, "revision.translation_target", _near(displacement, delta, TRANSLATION_TOLERANCE_M), {"actual_delta_m": displacement, "expected_delta_m": delta, "max_delta_m": max(abs(a-b) for a, b in zip(displacement, delta))})
        distance = math.sqrt(sum(v*v for v in displacement))
        _check(checks, "revision.translation_magnitude", abs(distance-0.4) <= TRANSLATION_TOLERANCE_M, {"distance_m": distance})
        _check(checks, "revision.exact_linear_green", _near(after["materials"][SHELL]["base_color_linear"], srgb_hex_to_linear("#163D2A")), {"expected": srgb_hex_to_linear("#163D2A"), "actual": after["materials"][SHELL]["base_color_linear"]})
        _physical_checks(after, checks)
    except (KeyError, TypeError, ValueError, IndexError) as exc:
        _check(checks, "revision.malformed_snapshot", False, f"{type(exc).__name__}: {exc}")
    return _result(checks)
