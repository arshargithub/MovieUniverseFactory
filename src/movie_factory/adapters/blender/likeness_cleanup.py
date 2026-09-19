"""Trusted bounded material-only diagnostic for the approved Pashtun head.

No generated code is admitted. Input is pinned; outputs are new local folders.
Run with factory startup and auto-execution disabled. No add-on is required.
"""
import hashlib
import json
import math
import statistics
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / '.runtime/art-direction/series01-facebuilder-trial-01'
SOURCE = BASE / 'head-v02-two-view.blend'
DIGEST = 'c0e5201fa25490e528396132edff5f45b5f4b803d9487983bca2fde194255e4c'


def validate(job):
    if not isinstance(job, dict) or set(job) != {'operation', 'output_name'}:
        raise ValueError('Only operation and output_name admitted')
    if job['operation'] not in {'inspect', 'neck_material_preview'}:
        raise ValueError('Unsupported operation')
    name = job['output_name']
    if not isinstance(name, str) or not name.startswith('cleanup-') or len(name) > 64 or not all(c.isalnum() or c == '-' for c in name):
        raise ValueError('Invalid output name')
    if SOURCE.is_symlink() or hashlib.sha256(SOURCE.read_bytes()).hexdigest() != DIGEST:
        raise ValueError('Approved source changed')
    out = BASE / name
    if out.exists():
        raise ValueError('Refusing to overwrite evidence')
    return out


def geometry_digest(obj):
    payload = {
        'vertices': [list(v.co) for v in obj.data.vertices],
        'faces': [list(p.vertices) for p in obj.data.polygons],
        'matrix': [list(row) for row in obj.matrix_world],
        'uv': [list(v.uv) for v in obj.data.uv_layers.active.data],
        'shapes': {k.name: [list(v.co) for v in k.data] for k in obj.data.shape_keys.key_blocks} if obj.data.shape_keys else {},
    }
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()


def neck_weight(z):
    """Reference definition: fully protected above normalized height 0.30."""
    return max(0.0, min(1.0, (0.30 - z) / 0.09))


def linear_channel(c):
    return c / 12.92 if c <= .04045 else ((c + .055) / 1.055) ** 2.4


def shader_defaults(material):
    node = next(n for n in material.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    values = {}
    for socket in node.inputs:
        if socket.is_linked or not hasattr(socket, 'default_value'):
            continue
        value = socket.default_value
        if isinstance(value, (int, float, str, bool)):
            values[socket.name] = value
        else:
            try:
                values[socket.name] = list(value)
            except TypeError:
                pass
    return values


def repair_material(obj, low, high):
    import bpy
    mat = obj.data.materials[0].copy()
    obj.data.materials[0] = mat
    mat.name = 'MF_neck_cleanup_candidate'
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    tex = next(n for n in nodes if n.type == 'TEX_IMAGE' and n.image)
    bsdf = next(n for n in nodes if n.type == 'BSDF_PRINCIPLED')
    image = tex.image
    pixels = list(image.pixels)
    w, h = image.size
    samples = []
    uv = obj.data.uv_layers.active.data
    for loop in obj.data.loops:
        v = obj.data.vertices[loop.vertex_index].co
        z = (v.z - low[2]) / (high[2] - low[2])
        if .16 < z < .26 and abs(v.x) < .24 and v.y < -.3:
            u = uv[loop.index].uv
            x, y = int(max(0, min(w - 1, u.x * w))), int(max(0, min(h - 1, u.y * h)))
            rgb = pixels[4 * (y * w + x):4 * (y * w + x) + 3]
            if rgb[0] > rgb[1] > rgb[2] and rgb[0] > .06:
                samples.append(rgb)
    if len(samples) < 5:
        raise ValueError('Not enough admitted neck-skin samples')
    encoded = tuple(statistics.median(s[i] for s in samples) for i in range(3))
    skin = tuple(linear_channel(c) if image.colorspace_settings.name == 'sRGB' else c for c in encoded) + (1,)
    coords = nodes.new('ShaderNodeTexCoord')
    separate = nodes.new('ShaderNodeSeparateXYZ')
    links.new(coords.outputs['Generated'], separate.inputs[0])
    weight = nodes.new('ShaderNodeMapRange')
    weight.clamp = True
    weight.inputs['From Min'].default_value = .21
    weight.inputs['From Max'].default_value = .30
    weight.inputs['To Min'].default_value = 1
    weight.inputs['To Max'].default_value = 0
    links.new(separate.outputs['Z'], weight.inputs['Value'])
    mix = nodes.new('ShaderNodeMixRGB')
    mix.blend_type = 'MIX'
    links.new(weight.outputs['Result'], mix.inputs[0])
    links.new(tex.outputs['Color'], mix.inputs[1])
    mix.inputs[2].default_value = skin
    links.new(mix.outputs[0], bsdf.inputs['Base Color'])
    return {'sample_count': len(samples), 'skin_sample_encoded': encoded, 'image_colorspace': image.colorspace_settings.name, 'skin_linear_rgba': skin,
            'mask_full_below': .21, 'mask_zero_above': .30,
            'limitation': 'Neutral neck infill, not reconstructed skin detail; procedural mask requires baking for portable material export.'}


def setup_review(obj):
    import bpy
    from mathutils import Vector
    scene = bpy.context.scene
    for other in scene.objects:
        other.hide_render = other != obj
    obj.hide_set(False)
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'CPU'
    scene.cycles.samples = 12
    scene.cycles.use_denoising = True
    scene.render.resolution_x = 512
    scene.render.resolution_y = 640
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    scene.view_settings.view_transform = 'Standard'
    scene.view_settings.look = 'None'
    scene.view_settings.exposure = 0
    scene.view_settings.gamma = 1
    scene.world = bpy.data.worlds.new('MF_review_world')
    scene.world.use_nodes = True
    scene.world.node_tree.nodes['Background'].inputs[0].default_value = (.12, .12, .12, 1)
    for name, location, power, size in [('key', (-3, -4, 5), 450, 5), ('fill', (3, -2, 1), 180, 4)]:
        data = bpy.data.lights.new('MF_' + name, 'AREA')
        data.energy, data.shape, data.size = power, 'DISK', size
        light = bpy.data.objects.new('MF_' + name, data)
        scene.collection.objects.link(light)
        light.location = location
        light.rotation_euler = (Vector((0, 0, -.1)) - light.location).to_track_quat('-Z', 'Y').to_euler()
    camera = bpy.data.objects.new('MF_review_camera', bpy.data.cameras.new('MF_review_camera'))
    scene.collection.objects.link(camera)
    camera.data.type, camera.data.ortho_scale = 'ORTHO', 3.6
    scene.camera = camera
    return scene, camera


def render_views(scene, camera, out, prefix):
    import bpy
    from mathutils import Vector
    for label, degrees in [('front', 0), ('left', -30), ('right', 30)]:
        angle = math.radians(degrees)
        camera.location = (6 * math.sin(angle), -6 * math.cos(angle), -.16)
        camera.rotation_euler = (Vector((0, 0, -.16)) - camera.location).to_track_quat('-Z', 'Y').to_euler()
        scene.render.filepath = str(out / (prefix + '-' + label + '.png'))
        bpy.ops.render.render(write_still=True)


def run(job):
    out = validate(job)  # Must precede Blender operations and output creation.
    import bpy
    out.mkdir()
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE), load_ui=False, use_scripts=False)
    obj = bpy.data.objects['FBHead']
    if obj.type != 'MESH' or len(obj.data.vertices) > 100000 or obj.modifiers:
        raise ValueError('Unexpected head structure')
    before = geometry_digest(obj)
    low = [min(v.co[i] for v in obj.data.vertices) for i in range(3)]
    high = [max(v.co[i] for v in obj.data.vertices) for i in range(3)]
    mats = [m for m in obj.data.materials if m]
    source_defaults = shader_defaults(mats[0])
    report = {'source_sha256': DIGEST, 'geometry_before': before, 'bounds': [low, high],
              'vertices': len(obj.data.vertices), 'faces': len(obj.data.polygons), 'shader_defaults': source_defaults,
              'materials': [{ 'name': m.name, 'nodes': [
                  {'name': n.name, 'type': n.type, 'image': n.image.name if n.type == 'TEX_IMAGE' and n.image else None}
                  for n in m.node_tree.nodes], 'links': [
                      [l.from_node.name, l.from_socket.name, l.to_node.name, l.to_socket.name] for l in m.node_tree.links]}
                  for m in mats],
              'images': [{'name': i.name, 'size': list(i.size), 'packed': bool(i.packed_file)} for i in bpy.data.images]}
    (out / 'inspection.json').write_text(json.dumps(report, indent=2))
    if job['operation'] == 'inspect':
        return
    # Export the untouched approved material, before adding procedural nodes.
    bpy.ops.object.select_all(action='DESELECT')
    obj.hide_set(False)
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.export_scene.gltf(filepath=str(out / 'approved-base.glb'), export_format='GLB', use_selection=True)
    scene, camera = setup_review(obj)
    render_views(scene, camera, out, 'before')
    report['repair'] = repair_material(obj, low, high)
    report['geometry_after'] = geometry_digest(obj)
    if report['geometry_after'] != before:
        raise ValueError('Protected geometry changed')
    render_views(scene, camera, out, 'after')
    bpy.ops.wm.save_as_mainfile(filepath=str(out / 'neck-material-candidate.blend'))
    # Fresh add-on-free import. Native geometry may be split at UV seams.
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(out / 'approved-base.glb'), import_pack_images=True)
    meshes = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    if len(meshes) != 1:
        raise ValueError('Expected one imported mesh')
    imported = meshes[0]
    imported_defaults = shader_defaults(imported.data.materials[0])
    report['material_roundtrip_changes'] = {k: {'source': v, 'imported': imported_defaults.get(k)}
        for k, v in source_defaults.items() if imported_defaults.get(k) != v}
    # Explicit Blender material sidecar restores values the exchange format omits.
    (out / 'material-sidecar.json').write_text(json.dumps(source_defaults, indent=2))
    shader = next(n for n in imported.data.materials[0].node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    for name, value in source_defaults.items():
        socket = shader.inputs.get(name)
        if socket is not None and not socket.is_linked:
            socket.default_value = value
    report['roundtrip_material_policy'] = 'GLB plus explicit Blender Principled input sidecar; not bare-GLB material parity'
    report['roundtrip'] = {'objects': len(bpy.context.scene.objects), 'meshes': len(meshes),
        'vertices': len(imported.data.vertices), 'faces': len(imported.data.polygons),
        'images': [{'name': i.name, 'packed': bool(i.packed_file), 'size': list(i.size)} for i in bpy.data.images if i.type != 'RENDER_RESULT']}
    scene, camera = setup_review(imported)
    render_views(scene, camera, out, 'roundtrip')
    bpy.ops.wm.save_as_mainfile(filepath=str(out / 'approved-base-roundtrip.blend'))
    if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != DIGEST:
        raise ValueError('Source mutated')
    report['source_preserved'] = True
    (out / 'result.json').write_text(json.dumps(report, indent=2))


if __name__ == '__main__':
    args = sys.argv[sys.argv.index('--') + 1:]
    if len(args) != 1:
        raise ValueError('One JSON job path required')
    run(json.loads(Path(args[0]).read_text()))
