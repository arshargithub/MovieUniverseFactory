"""Authoritative read-only native state extraction, executed by Blender Python.

Stable IDs, raw geometry arrays and comprehensive node values support a
deny-by-default comparison. UI selection, active render camera and file output
paths are deliberately omitted: their frozen mappings live in the work package.
"""
import hashlib
import json
import math

import bpy
from mathutils import Euler, Matrix, Quaternion, Vector


def value(item):
    if item is None or isinstance(item, (str, bool, int)):
        return item
    if isinstance(item, float):
        if not math.isfinite(item):
            raise ValueError("Non-finite native state")
        return round(item, 9)
    if isinstance(item, Matrix):
        return [[value(component) for component in row] for row in item]
    if isinstance(item, (Vector, Euler, Quaternion)):
        return [value(component) for component in item]
    if isinstance(item, bpy.types.ID):
        return item.get("mf_id", item.name)
    if hasattr(item, "to_list"):
        return value(item.to_list())
    if hasattr(item, "to_dict"):
        return value(item.to_dict())
    if isinstance(item, dict):
        return {str(k): value(v) for k, v in sorted(item.items())}
    if hasattr(item, "__iter__"):
        return [value(v) for v in item]
    return str(item)


def digest(data):
    return hashlib.sha256(json.dumps(data, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def properties(item, fields):
    return {name: value(getattr(item, name)) for name in fields if hasattr(item, name)}


def custom(item):
    return {key: value(item[key]) for key in sorted(item.keys()) if key != "_RNA_UI"}


def rna_values(item):
    """All scalar RNA properties; collection structure is handled explicitly."""
    result = {}
    for prop in item.bl_rna.properties:
        name = prop.identifier
        # session_uid is allocated afresh when a .blend is reopened and is not
        # persistent scene state. Everything else remains deny-by-default.
        if name in {"rna_type", "session_uid"} or prop.type in {"COLLECTION", "POINTER"}:
            continue
        try:
            result[name] = value(getattr(item, name))
        except (AttributeError, TypeError):
            continue
    return result


def nodes(tree):
    if not tree:
        return {"nodes": {}, "links": []}
    graph = {}
    for node in sorted(tree.nodes, key=lambda n: n.name):
        graph[node.name] = {
            "type": node.bl_idname,
            "image": value(getattr(node, "image", None)),
            "inputs": {s.identifier: value(s.default_value) for s in node.inputs if hasattr(s, "default_value")},
            "outputs": {s.identifier: value(s.default_value) for s in node.outputs if hasattr(s, "default_value")},
            "properties": properties(node, ("mute", "is_active_output", "distribution", "subsurface_method",
                                            "operation", "blend_type", "clamp_factor", "clamp_result",
                                            "interpolation", "extension", "projection")),
        }
    links = [{"from_node": l.from_node.name, "from_socket": l.from_socket.identifier,
              "to_node": l.to_node.name, "to_socket": l.to_socket.identifier} for l in tree.links]
    return {"nodes": graph, "links": sorted(links, key=lambda x: json.dumps(x, sort_keys=True))}


def geometry(mesh):
    result = {
        "vertices": [value(v.co) for v in mesh.vertices],
        "faces": [list(p.vertices) for p in mesh.polygons],
        "edges": [list(e.vertices) for e in mesh.edges],
        "normals": [value(v.normal) for v in mesh.vertices],
        "polygon_normals": [value(p.normal) for p in mesh.polygons],
        "polygon_material_indices": [p.material_index for p in mesh.polygons],
        "polygon_smooth": [p.use_smooth for p in mesh.polygons],
        "uv_layers": {uv.name: [value(d.uv) for d in uv.data] for uv in mesh.uv_layers},
        "attributes": {},
    }
    for attr in sorted(mesh.attributes, key=lambda a: a.name):
        key = next((k for k in ("value", "vector", "color") if len(attr.data) and hasattr(attr.data[0], k)), None)
        result["attributes"][attr.name] = {
            "domain": attr.domain, "data_type": attr.data_type,
            "data": [value(getattr(d, key)) for d in attr.data] if key else [],
        }
    result["hash"] = digest(result)
    return result


def bounds(obj):
    pts = [obj.matrix_world @ Vector(p) for p in obj.bound_box]
    return {"min": [round(min(p[i] for p in pts), 9) for i in range(3)],
            "max": [round(max(p[i] for p in pts), 9) for i in range(3)]}


def animation(item):
    data = getattr(item, "animation_data", None)
    if data is None:
        return None
    # No animation/drivers are accepted in this static experiment. Their presence
    # is preserved and is independently a hard unsupported-state failure.
    return {"action": data.action.name if data.action else None,
            "drivers": [d.data_path for d in data.drivers], "nla_tracks": len(data.nla_tracks)}


def snapshot():
    scene = bpy.context.scene
    bpy.context.view_layer.update()
    deps = bpy.context.evaluated_depsgraph_get()
    result = {"schema_version": "1.0", "scene_id": scene.get("mf_scene_id"),
              "objects": {}, "entities": {}, "materials": {}, "cameras": {}, "lights": {},
              "world": {}, "render": {}, "images": {}, "external_files": [], "unsupported": []}
    seen_ids = set()
    for obj in sorted(scene.objects, key=lambda o: o.get("mf_id", o.name)):
        oid = obj.get("mf_id")
        if not oid or oid in seen_ids:
            result["unsupported"].append("missing_or_duplicate_object_id:" + obj.name)
            oid = oid or obj.name
        seen_ids.add(oid)
        geom = geometry(obj.data) if obj.type == "MESH" else None
        evaluated = None
        if obj.type == "MESH":
            evaluated_obj = obj.evaluated_get(deps)
            evaluated_mesh = evaluated_obj.to_mesh(preserve_all_data_layers=True, depsgraph=deps)
            evaluated = geometry(evaluated_mesh)
            evaluated_obj.to_mesh_clear()
        item = {
            "id": oid, "name": obj.name, "entity_id": obj.get("mf_entity"),
            "kind": obj.get("mf_kind"), "type": obj.type,
            "parent_id": obj.parent.get("mf_id", obj.parent.name) if obj.parent else None,
            "location": value(obj.location), "rotation_euler": value(obj.rotation_euler),
            "rotation_mode": obj.rotation_mode, "scale": value(obj.scale),
            "matrix_local": value(obj.matrix_local), "matrix_world": value(obj.matrix_world),
            "matrix_parent_inverse": value(obj.matrix_parent_inverse),
            "dimensions": value(obj.dimensions),
            "bounds_world": bounds(obj) if obj.type == "MESH" else None,
            "visible_render": not obj.hide_render,
            "visibility": properties(obj, ("hide_render", "hide_viewport", "visible_camera", "visible_diffuse",
                                           "visible_glossy", "visible_shadow", "visible_transmission", "visible_volume_scatter")),
            "collection_ids": sorted(c.get("mf_id", c.name) for c in obj.users_collection),
            "material_ids": [m.get("mf_id", m.name) if m else None for m in obj.data.materials] if hasattr(obj.data, "materials") else [],
            "geometry_hash": geom["hash"] if geom else None,
            "source_geometry": geom, "evaluated_geometry": evaluated,
            "modifiers": [rna_values(m) for m in obj.modifiers],
            "constraints": [rna_values(c) for c in obj.constraints],
            "animation": animation(obj), "drivers": [d.data_path for d in obj.animation_data.drivers] if obj.animation_data else [],
            "custom_properties": custom(obj), "provenance": obj.get("mf_creation_id"),
        }
        if obj.modifiers or obj.constraints or obj.animation_data:
            result["unsupported"].append("object_procedural_or_animated_state:" + oid)
        if obj.type not in {"EMPTY", "MESH", "CAMERA", "LIGHT"}:
            result["unsupported"].append("object_type:" + oid)
        result["objects"][oid] = item
        if obj.get("mf_is_entity"):
            result["entities"][oid] = {
                "id": oid, "root_id": oid, "kind": obj.get("mf_kind"), "position": value(obj.location),
                "rotation_euler": value(obj.rotation_euler), "scale": value(obj.scale),
                "object_ids": sorted(o.get("mf_id", o.name) for o in scene.objects if o.get("mf_entity") == oid),
                "bounds_world": None,
            }
        if obj.type == "CAMERA":
            result["cameras"][oid] = {"object_id": oid, "shot_id": obj.get("mf_shot_id"),
                "data": rna_values(obj.data), "dof": rna_values(obj.data.dof),
                "focus_object": value(obj.data.dof.focus_object), "animation": animation(obj.data),
                "custom_properties": custom(obj.data)}
        elif obj.type == "LIGHT":
            result["lights"][oid] = {"object_id": oid, "data": rna_values(obj.data),
                **nodes(obj.data.node_tree if getattr(obj.data, "use_nodes", False) else None),
                "animation": animation(obj.data), "custom_properties": custom(obj.data)}
    for entity in result["entities"].values():
        boxes = [result["objects"][oid]["bounds_world"] for oid in entity["object_ids"]
                 if result["objects"][oid]["bounds_world"]]
        if boxes:
            entity["bounds_world"] = {"min": [min(b["min"][i] for b in boxes) for i in range(3)],
                                      "max": [max(b["max"][i] for b in boxes) for i in range(3)]}
    for mat in sorted(bpy.data.materials, key=lambda m: m.get("mf_id", m.name)):
        if not mat.users:
            continue
        mid = mat.get("mf_id", mat.name)
        principled = mat.node_tree.nodes.get("Principled BSDF") if mat.use_nodes else None
        result["materials"][mid] = {"id": mid, "name": mat.name, "users": mat.users,
            "object_ids": sorted(o.get("mf_id", o.name) for o in scene.objects if hasattr(o.data, "materials") and mat.name in o.data.materials),
            "base_color_linear": value(principled.inputs["Base Color"].default_value) if principled else None,
            "roughness": value(principled.inputs["Roughness"].default_value) if principled else None,
            "properties": properties(mat, ("use_nodes", "diffuse_color", "surface_render_method", "use_backface_culling")),
            **nodes(mat.node_tree), "animation": animation(mat), "custom_properties": custom(mat)}
        allowed_material_nodes = {"ShaderNodeBsdfPrincipled", "ShaderNodeOutputMaterial"}
        if scene.get("mf_builder_version") == "external-v1":
            allowed_material_nodes |= {
                "ShaderNodeTexImage", "ShaderNodeNormalMap", "ShaderNodeSeparateColor",
                "ShaderNodeMapping", "ShaderNodeUVMap", "ShaderNodeTexCoord",
            }
        if not mat.use_nodes or any(n.bl_idname not in allowed_material_nodes for n in mat.node_tree.nodes):
            result["unsupported"].append("material_node_type:" + mid)
        if animation(mat) or (mat.node_tree and animation(mat.node_tree)):
            result["unsupported"].append("material_animation:" + mid)
    world = scene.world
    result["world"] = {"name": world.name, "color": value(world.color), "use_nodes": world.use_nodes,
                       **nodes(world.node_tree), "animation": animation(world), "custom_properties": custom(world)} if world else None
    if world and any(n.bl_idname not in {"ShaderNodeBackground", "ShaderNodeOutputWorld"} for n in world.node_tree.nodes):
        result["unsupported"].append("world_node_type")
    result["render"] = {
        "engine": scene.render.engine, "blender_version": bpy.app.version_string,
        "blender_build_hash": bpy.app.build_hash.decode(), "frame": scene.frame_current,
        "settings": properties(scene.render, ("resolution_x", "resolution_y", "resolution_percentage", "pixel_aspect_x", "pixel_aspect_y", "film_transparent", "use_border", "use_crop_to_border", "fps", "fps_base", "film_transparent_glass", "use_freestyle")),
        "image_settings": properties(scene.render.image_settings, ("file_format", "color_mode", "color_depth", "compression")),
        "cycles": properties(scene.cycles, ("device", "samples", "seed", "use_animated_seed", "use_denoising", "use_adaptive_sampling", "adaptive_threshold", "max_bounces", "diffuse_bounces", "glossy_bounces", "transmission_bounces", "transparent_max_bounces", "volume_bounces", "sample_clamp_direct", "sample_clamp_indirect", "use_light_tree")),
        "view_settings": properties(scene.view_settings, ("view_transform", "look", "exposure", "gamma", "use_curve_mapping", "use_white_balance", "temperature", "tint")),
        "display_settings": properties(scene.display_settings, ("display_device",)),
        "sequencer_colorspace": properties(scene.sequencer_colorspace_settings, ("name",)),
        "compositor": {"use_nodes": getattr(scene, "use_nodes", False), "nodes": nodes(getattr(scene, "node_tree", None))},
        "shot_bindings": {o.get("mf_shot_id"): o.get("mf_id") for o in scene.objects if o.type == "CAMERA"},
        "scene_custom_properties": custom(scene), "unit_settings": rna_values(scene.unit_settings),
        "collections": {c.get("mf_id", c.name): {"name": c.name, "hide_render": c.hide_render, "hide_viewport": c.hide_viewport} for c in bpy.data.collections},
    }
    compositor_tree = getattr(scene, "node_tree", None)
    if compositor_tree and (len(compositor_tree.nodes) or len(compositor_tree.links)):
        result["unsupported"].append("compositor_nodes")
    if scene.animation_data:
        result["unsupported"].append("scene_animation")
    for library in bpy.data.libraries:
        result["external_files"].append({"type": "library", "path": library.filepath})
    for img in bpy.data.images:
        if img.source == "FILE":
            result["external_files"].append({"type": "image", "path": img.filepath, "packed": bool(img.packed_file)})
        if img.users:
            packed = bytes(img.packed_file.data) if img.packed_file else None
            result["images"][img.name] = {
                "name": img.name, "source": img.source, "filepath": img.filepath,
                "packed": bool(img.packed_file), "packed_sha256": hashlib.sha256(packed).hexdigest() if packed is not None else None,
                "size": value(img.size), "channels": img.channels,
                "colorspace": img.colorspace_settings.name, "custom_properties": custom(img),
            }
    # Packed images remain self-contained inside the native file. Preserve their
    # original acquisition paths as evidence, but reject libraries and unpacked images.
    if any(item["type"] == "library" or not item.get("packed", False) for item in result["external_files"]):
        result["unsupported"].append("external_files")
    result["unsupported"] = sorted(set(result["unsupported"]))
    return result
