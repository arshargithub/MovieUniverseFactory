"""Independent checks for the frozen 3D-02 external-asset experiment."""
from __future__ import annotations

import copy
import math
from typing import Any

from .structural import compare_snapshots


EXPECTED_ENTITIES = {"courtyard_01", "motorcycle_01", "sword_01"}


def _check(checks: list[dict[str, Any]], name: str, passed: bool, details: Any = None) -> None:
    checks.append({"name": name, "passed": bool(passed), "details": details})


def _result(checks: list[dict[str, Any]]) -> dict[str, Any]:
    return {"passed": all(item["passed"] for item in checks), "checks": checks,
            "errors": [item["name"] for item in checks if not item["passed"]]}


def _dimensions(bounds: dict[str, list[float]]) -> list[float]:
    return [bounds["max"][i] - bounds["min"][i] for i in range(3)]


def _entity_topology(snapshot: dict, entity_id: str) -> tuple[int, int]:
    objects = [snapshot["objects"][oid] for oid in snapshot["entities"][entity_id]["object_ids"]]
    vertices = sum(len((obj.get("source_geometry") or {}).get("vertices", [])) for obj in objects)
    polygons = sum(len((obj.get("source_geometry") or {}).get("faces", [])) for obj in objects)
    return vertices, polygons


def validate_external_baseline(snapshot: dict, plan: dict) -> dict:
    checks: list[dict[str, Any]] = []
    _check(checks, "identity.scene", snapshot.get("scene_id") == plan.get("scene_id"))
    _check(checks, "identity.entity_set", set(snapshot.get("entities", {})) == EXPECTED_ENTITIES,
           sorted(snapshot.get("entities", {})))
    _check(checks, "snapshot.supported", snapshot.get("unsupported") == [], snapshot.get("unsupported"))
    external = snapshot.get("external_files", [])
    _check(checks, "assets.images_packed", bool(external) and all(
        item.get("type") == "image" and item.get("packed") is True for item in external
    ), external)
    image_hashes={item.get("packed_sha256") for item in snapshot.get("images", {}).values()}
    required_hashes=set(plan.get("required_packed_image_sha256", []))
    _check(checks, "assets.packed_image_identity", bool(required_hashes) and required_hashes <= image_hashes,
           {"required":sorted(required_hashes),"observed":sorted(value for value in image_hashes if value)})
    try:
        planned = {entity["id"]: entity for entity in plan["entities"]}
        for entity_id in EXPECTED_ENTITIES:
            entity = snapshot["entities"][entity_id]
            _check(checks, f"identity.{entity_id}.root", entity["root_id"] in snapshot["objects"])
            _check(checks, f"identity.{entity_id}.parts", bool(entity["object_ids"]) and all(
                snapshot["objects"][oid]["entity_id"] == entity_id for oid in entity["object_ids"]
            ))
        for entity_id, target, minimum_vertices in (("motorcycle_01", 2.4, 10_000), ("sword_01", 1.0, 100)):
            bounds = snapshot["entities"][entity_id]["bounds_world"]
            longest = max(_dimensions(bounds))
            vertices, polygons = _entity_topology(snapshot, entity_id)
            _check(checks, f"normalization.{entity_id}.longest_dimension", abs(longest-target) <= 1e-4,
                   {"actual_m": longest, "target_m": target})
            _check(checks, f"normalization.{entity_id}.ground_contact", abs(bounds["min"][2]) <= 1e-4,
                   {"bottom_z_m": bounds["min"][2]})
            _check(checks, f"topology.{entity_id}.minimum", vertices >= minimum_vertices and polygons > 0,
                   {"vertices": vertices, "polygons": polygons})
            root = snapshot["objects"][entity_id]
            _check(checks, f"provenance.{entity_id}.source_hash",
                   root["custom_properties"].get("mf_source_sha256") == planned[entity_id]["source_sha256"])
        vertices, polygons = _entity_topology(snapshot, "courtyard_01")
        _check(checks, "topology.courtyard_01.minimum", vertices >= 1_000 and polygons >= 500,
               {"vertices": vertices, "polygons": polygons})
        bike_materials = [material for material in snapshot["materials"].values()
                          if material["custom_properties"].get("mf_repair")]
        _check(checks, "materials.motorcycle_explicit_repair", len(bike_materials) == 1 and
               bike_materials[0]["custom_properties"]["mf_repair"] == "explicit_unreal_pbr_relink_v1")
    except (KeyError, TypeError, ValueError) as exc:
        _check(checks, "snapshot.malformed", False, f"{type(exc).__name__}: {exc}")
    return _result(checks)


def _protected_object(obj: dict, *, root_transform: bool, rotated_child: bool = False) -> dict:
    result = copy.deepcopy(obj)
    if root_transform:
        for field in ("location", "rotation_euler", "matrix_local", "matrix_world"):
            result.pop(field, None)
    else:
        for field in ("matrix_world", "bounds_world"):
            result.pop(field, None)
        if rotated_child:
            result.pop("dimensions", None)
    return result


def validate_external_revision(before: dict, after: dict, operations: list[dict]) -> dict:
    checks: list[dict[str, Any]] = []
    expected_operations = [
        {"op":"translate_entity","entity_id":"motorcycle_01","delta_m":[0.6,0,0]},
        {"op":"rotate_entity_z","entity_id":"sword_01","degrees":25},
    ]
    _check(checks, "revision.operations_frozen", operations == expected_operations)
    for section in ("scene_id", "materials", "cameras", "lights", "world", "render", "images", "external_files", "unsupported"):
        _check(checks, f"protected.{section}", compare_snapshots(before.get(section), after.get(section))["passed"])
    _check(checks, "identity.object_set", set(before.get("objects", {})) == set(after.get("objects", {})))
    _check(checks, "identity.entity_set", set(before.get("entities", {})) == set(after.get("entities", {})))
    try:
        for entity_id in EXPECTED_ENTITIES:
            before_entity, after_entity = before["entities"][entity_id], after["entities"][entity_id]
            if entity_id == "courtyard_01":
                _check(checks, "protected.courtyard_entity", compare_snapshots(before_entity, after_entity)["passed"])
            else:
                left, right = copy.deepcopy(before_entity), copy.deepcopy(after_entity)
                for item in (left, right):
                    for field in ("position", "rotation_euler", "bounds_world"):
                        item.pop(field, None)
                _check(checks, f"protected.{entity_id}.semantic", compare_snapshots(left, right)["passed"])
            for oid in before_entity["object_ids"]:
                if entity_id == "courtyard_01":
                    passed = compare_snapshots(before["objects"][oid], after["objects"][oid])["passed"]
                else:
                    passed = compare_snapshots(
                        _protected_object(before["objects"][oid], root_transform=oid == entity_id, rotated_child=entity_id == "sword_01"),
                        _protected_object(after["objects"][oid], root_transform=oid == entity_id, rotated_child=entity_id == "sword_01"),
                    )["passed"]
                _check(checks, f"protected.object.{oid}", passed)
        bike_before = before["objects"]["motorcycle_01"]["location"]
        bike_after = after["objects"]["motorcycle_01"]["location"]
        _check(checks, "revision.motorcycle_delta", all(abs((bike_after[i]-bike_before[i])-[.6,0,0][i]) <= 1e-6 for i in range(3)),
               {"before": bike_before, "after": bike_after})
        sword_before = before["objects"]["sword_01"]["rotation_euler"]
        sword_after = after["objects"]["sword_01"]["rotation_euler"]
        _check(checks, "revision.sword_rotation", abs((sword_after[2]-sword_before[2])-math.radians(25)) <= 1e-6,
               {"before": sword_before[2], "after": sword_after[2]})
    except (KeyError, TypeError, ValueError) as exc:
        _check(checks, "snapshot.malformed", False, f"{type(exc).__name__}: {exc}")
    return _result(checks)
