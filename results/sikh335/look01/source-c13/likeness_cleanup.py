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
    if job['operation'] not in {'inspect', 'neck_material_preview', 'jaw_diagnostic', 'jaw_projection_preview', 'portable_cleanup'}:
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


def jaw_mask(x, z):
    """Local lower-side face blend; preserves central mouth and upper face."""
    side = max(0., min(1., (abs(x) - .22) / .22))
    lower = max(0., min(1., (z - .27) / .05))
    upper = max(0., min(1., (.49 - z) / .08))
    return .85 * side * lower * upper


def skin_projection_confidence(rgb):
    """Conservative local color gate, not a general skin/ethnicity classifier."""
    r, g, b = rgb
    if not all(math.isfinite(c) for c in rgb):
        return 0.
    return max(0., min(1., (r - .25) / .15)) * max(0., min(1., (r - g) / .08)) * max(0., min(1., (g - b) / .05))


def gap_region(x, y, z):
    return (max(0., min(1., (x-.25)/.2)) * max(0., min(1., (z-.27)/.05))
            * max(0., min(1., (.62-z)/.08)) * max(0., min(1., (.5-y)/.3)))


def fill_jaw_gap(obj, low, high, nodes, links, color_socket):
    """Material-only approximate infill of the known viewer-right black gap."""
    from mathutils.kdtree import KDTree
    original = next(n for n in nodes if n.type == 'TEX_IMAGE' and n.image and n.image.name == 'FBHead_baked_tex')
    image = original.image
    pixels, (w, h) = list(image.pixels), tuple(image.size)
    samples = []
    for loop in obj.data.loops:
        v = obj.data.vertices[loop.vertex_index].co
        z = (v.z-low[2])/(high[2]-low[2])
        if not (.28 < z < .56 and v.y < -.2):
            continue
        uv = obj.data.uv_layers.active.data[loop.index].uv
        x, y = max(0,min(w-1,int(uv.x*w))), max(0,min(h-1,int(uv.y*h)))
        rgb = pixels[4*(y*w+x):4*(y*w+x)+3]
        if skin_projection_confidence(rgb) > .9:
            samples.append((v.copy(), tuple(linear_channel(c) for c in rgb)+(1,)))
    if len(samples) < 10:
        raise ValueError('Insufficient local skin for gap fill')
    tree = KDTree(len(samples))
    for index, (p, _) in enumerate(samples):
        tree.insert(p, index)
    tree.balance()
    colors = obj.data.color_attributes.new(name='MF_gap_skin', type='FLOAT_COLOR', domain='POINT')
    region = obj.data.attributes.new(name='MF_gap_region', type='FLOAT', domain='POINT')
    side = obj.data.attributes.new(name='MF_gap_side_blend', type='FLOAT', domain='POINT')
    for v in obj.data.vertices:
        near = tree.find_n(v.co, min(32,len(samples)))
        weights = [(i, 1.0 / (.04 + distance)**2) for _,i,distance in near]
        total = sum(weight for _,weight in weights)
        colors.data[v.index].color = tuple(sum(samples[i][1][c]*weight for i,weight in weights)/total for c in range(4))
        region.data[v.index].value = gap_region(v.co.x,v.co.y,(v.co.z-low[2])/(high[2]-low[2]))
        # Feather from the front cheek into the side; cover the baked portrait
        # silhouette rather than retaining it as a false crease below the ear.
        t = max(0., min(1., (v.co.y + 1.25)/.6))
        side.data[v.index].value = t*t*(3-2*t)
    luminance = nodes.new('ShaderNodeRGBToBW'); links.new(original.outputs['Color'],luminance.inputs[0])
    dark = nodes.new('ShaderNodeMapRange'); dark.clamp=True
    dark.inputs['From Min'].default_value=.015; dark.inputs['From Max'].default_value=.09
    dark.inputs['To Min'].default_value=1; dark.inputs['To Max'].default_value=0
    links.new(luminance.outputs[0],dark.inputs['Value'])
    region_node=nodes.new('ShaderNodeAttribute'); region_node.attribute_name=region.name
    side_node=nodes.new('ShaderNodeAttribute'); side_node.attribute_name=side.name
    coverage=nodes.new('ShaderNodeMath'); coverage.operation='MAXIMUM'
    links.new(dark.outputs['Result'],coverage.inputs[0]); links.new(side_node.outputs['Fac'],coverage.inputs[1])
    color_node=nodes.new('ShaderNodeAttribute'); color_node.attribute_name=colors.name
    weight=nodes.new('ShaderNodeMath'); weight.operation='MULTIPLY'
    links.new(coverage.outputs[0],weight.inputs[0]); links.new(region_node.outputs['Fac'],weight.inputs[1])
    mix=nodes.new('ShaderNodeMixRGB')
    links.new(weight.outputs[0],mix.inputs[0]); links.new(color_socket,mix.inputs[1]); links.new(color_node.outputs['Color'],mix.inputs[2])
    return mix.outputs[0]


def ear_region(x, y, z):
    def smooth(t):
        t = max(0., min(1., t))
        return t*t*(3-2*t)
    return smooth((x-.4)/.3)*smooth((y+1.1)/.55)*smooth((z-.30)/.10)*smooth((.68-z)/.08)


def transfer_ear_material(obj, low, high, nodes, links, color_socket):
    """Mirror only material coordinates from the better-covered side, not shape."""
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    from mathutils.geometry import barycentric_transform
    mesh = obj.data
    mesh.calc_loop_triangles()
    triangles = list(mesh.loop_triangles)
    tree = BVHTree.FromPolygons([v.co for v in mesh.vertices],
                               [tuple(t.vertices) for t in triangles], all_triangles=True)
    primary = mesh.uv_layers.active
    active_index = mesh.uv_layers.active_index
    uv = mesh.uv_layers.new(name='MF_opposite_ear_material')
    weight = mesh.attributes.new(name='MF_ear_transfer', type='FLOAT', domain='POINT')
    for v in mesh.vertices:
        weight.data[v.index].value = ear_region(v.co.x, v.co.y, (v.co.z-low[2])/(high[2]-low[2]))
    for loop in mesh.loops:
        v = mesh.vertices[loop.vertex_index].co
        hit, _, index, _ = tree.find_nearest(Vector((-v.x,v.y,v.z)))
        tri = triangles[index]
        points = [mesh.vertices[i].co for i in tri.vertices]
        coords = [Vector((*primary.data[i].uv,0)) for i in tri.loops]
        mapped = barycentric_transform(hit, *points, *coords)
        uv.data[loop.index].uv = mapped.xy
    mesh.uv_layers.active_index = active_index
    original = next(n for n in nodes if n.type == 'TEX_IMAGE' and n.image and n.image.name == 'FBHead_baked_tex')
    tex = nodes.new('ShaderNodeTexImage'); tex.image = original.image
    uvnode = nodes.new('ShaderNodeUVMap'); uvnode.uv_map = uv.name
    links.new(uvnode.outputs['UV'],tex.inputs['Vector'])
    attr = nodes.new('ShaderNodeAttribute'); attr.attribute_name = weight.name
    mix = nodes.new('ShaderNodeMixRGB')
    links.new(attr.outputs['Fac'],mix.inputs[0])
    links.new(color_socket,mix.inputs[1]); links.new(tex.outputs['Color'],mix.inputs[2])
    return mix.outputs[0]


def project_frontal_jaw(obj, low, high):
    import bpy
    from bpy_extras.object_utils import world_to_camera_view
    scene = bpy.context.scene
    camera = bpy.data.objects['fbCamera.001']
    image = bpy.data.images['frontal-v02-individualized.png.001']
    old = (scene.render.resolution_x, scene.render.resolution_y)
    scene.render.resolution_x, scene.render.resolution_y = tuple(image.size)
    active_index = obj.data.uv_layers.active_index
    uv = obj.data.uv_layers.new(name='MF_frontal_jaw_projection')
    attr = obj.data.attributes.new('MF_jaw_weight', 'FLOAT', 'POINT')
    pixels = list(image.pixels)
    w, h = image.size
    for v in obj.data.vertices:
        p = world_to_camera_view(scene, camera, obj.matrix_world @ v.co)
        weight = jaw_mask(v.co.x, (v.co.z - low[2]) / (high[2] - low[2]))
        # Only directly visible front-facing skin, never underside/back-face projection.
        if p.z <= 0 or not (0 <= p.x <= 1 and 0 <= p.y <= 1) or v.co.y > -.2 or v.normal.y > -.25:
            weight = 0
        else:
            x, y = min(w-1, int(p.x*w)), min(h-1, int(p.y*h))
            weight *= skin_projection_confidence(pixels[4*(y*w+x):4*(y*w+x)+3])
        attr.data[v.index].value = weight
    for loop in obj.data.loops:
        p = world_to_camera_view(scene, camera, obj.matrix_world @ obj.data.vertices[loop.vertex_index].co)
        uv.data[loop.index].uv = (p.x, p.y)
    obj.data.uv_layers.active_index = active_index
    scene.render.resolution_x, scene.render.resolution_y = old
    nodes, links = obj.data.materials[0].node_tree.nodes, obj.data.materials[0].node_tree.links
    neck_mix = next(n for n in nodes if n.type == 'MIX_RGB')
    original_color = neck_mix.inputs[1].links[0].from_socket
    uvnode = nodes.new('ShaderNodeUVMap'); uvnode.uv_map = uv.name
    tex = nodes.new('ShaderNodeTexImage'); tex.image = image; tex.extension = 'EXTEND'
    links.new(uvnode.outputs[0], tex.inputs['Vector'])
    attribute = nodes.new('ShaderNodeAttribute'); attribute.attribute_name = attr.name
    mix = nodes.new('ShaderNodeMixRGB')
    # Fragment-level gate prevents dark/blue pixels leaking between admitted vertices.
    separate = nodes.new('ShaderNodeSeparateColor')
    links.new(tex.outputs['Color'], separate.inputs['Color'])
    def difference(a, b):
        n = nodes.new('ShaderNodeMath'); n.operation = 'SUBTRACT'
        links.new(a, n.inputs[0]); links.new(b, n.inputs[1])
        gate = nodes.new('ShaderNodeMapRange'); gate.clamp = True
        gate.inputs['From Min'].default_value = 0
        gate.inputs['From Max'].default_value = .02
        links.new(n.outputs[0], gate.inputs['Value'])
        return gate.outputs['Result']
    factor = attribute.outputs['Fac']
    for gate in [difference(separate.outputs['Red'], separate.outputs['Green']),
                 difference(separate.outputs['Green'], separate.outputs['Blue'])]:
        multiply = nodes.new('ShaderNodeMath'); multiply.operation = 'MULTIPLY'
        links.new(factor, multiply.inputs[0]); links.new(gate, multiply.inputs[1])
        factor = multiply.outputs[0]
    luminance = nodes.new('ShaderNodeMapRange'); luminance.clamp = True
    luminance.inputs['From Min'].default_value = .05
    luminance.inputs['From Max'].default_value = .12
    links.new(separate.outputs['Red'], luminance.inputs['Value'])
    multiply = nodes.new('ShaderNodeMath'); multiply.operation = 'MULTIPLY'
    links.new(factor, multiply.inputs[0]); links.new(luminance.outputs['Result'], multiply.inputs[1])
    links.new(multiply.outputs[0], mix.inputs[0])
    links.new(original_color, mix.inputs[1])
    links.new(tex.outputs['Color'], mix.inputs[2])
    filled = fill_jaw_gap(obj, low, high, nodes, links, mix.outputs[0])
    links.new(transfer_ear_material(obj, low, high, nodes, links, filled), neck_mix.inputs[1])
    return {'method': 'Skin-gated frontal projection, localized nearest-skin infill and mirrored opposite-side ear material; inferred color, not recovered anatomy',
            'geometry_edit': False, 'source_image_edit': False,
            'additional_uv_layer': uv.name, 'additional_weight_attribute': attr.name}


def jaw_diagnostic(obj, low, high, out, report, correction=False):
    """Separate geometry, baked color, and real light without modifying the mesh."""
    import bpy
    repair_material(obj, low, high)
    material = obj.data.materials[0]
    scene, camera = setup_review(obj)
    # Equal mirrored large lights; no asymmetric key/fill difference.
    for name, x in [('MF_key', -3), ('MF_fill', 3)]:
        from mathutils import Vector
        light = bpy.data.objects[name]
        light.location = (x, -4, 3)
        light.rotation_euler = (Vector((0, 0, -.1)) - light.location).to_track_quat('-Z', 'Y').to_euler()
        light.data.energy = 300
        light.data.size = 5
    scene.cycles.samples = 32
    render_views(scene, camera, out, 'balanced-texture')
    unlit = material.copy()
    unlit.name = 'MF_diagnostic_unlit_color'
    nodes, links = unlit.node_tree.nodes, unlit.node_tree.links
    bsdf = next(n for n in nodes if n.type == 'BSDF_PRINCIPLED')
    color_socket = bsdf.inputs['Base Color'].links[0].from_socket
    emission = nodes.new('ShaderNodeEmission')
    links.new(color_socket, emission.inputs['Color'])
    output = next(n for n in nodes if n.type == 'OUTPUT_MATERIAL')
    links.new(emission.outputs[0], output.inputs['Surface'])
    obj.data.materials[0] = unlit
    render_views(scene, camera, out, 'unlit-texture')
    clay = bpy.data.materials.new('MF_diagnostic_clay')
    clay.use_nodes = True
    shader = clay.node_tree.nodes.get('Principled BSDF')
    shader.inputs['Base Color'].default_value = (.35, .35, .35, 1)
    shader.inputs['Roughness'].default_value = .8
    obj.data.materials[0] = clay
    render_views(scene, camera, out, 'balanced-clay')
    report['geometry_after'] = geometry_digest(obj)
    if report['geometry_before'] != report['geometry_after']:
        raise ValueError('Diagnostic changed geometry')
    report['diagnostic'] = 'Equal mirrored lights / emission texture / neutral clay; no shape correction'
    obj.data.materials[0] = material
    if correction:
        report['jaw_correction'] = project_frontal_jaw(obj, low, high)
        if geometry_digest(obj) != report['geometry_before']:
            raise ValueError('Correction changed protected geometry or primary UV')
        render_views(scene, camera, out, 'corrected')
    bpy.ops.wm.save_as_mainfile(filepath=str(out / 'jaw-review.blend'))
    report['source_preserved'] = hashlib.sha256(SOURCE.read_bytes()).hexdigest() == DIGEST
    if not report['source_preserved']:
        raise ValueError('Source mutated')
    (out / 'result.json').write_text(json.dumps(report, indent=2))


def portable_cleanup(obj, low, high, out, report):
    """Bake base color only; check clean-scene import with explicit material defaults."""
    import bpy
    repair_material(obj, low, high)
    report['correction'] = project_frontal_jaw(obj, low, high)
    scene, camera = setup_review(obj)
    scene.cycles.samples = 32
    render_views(scene, camera, out, 'procedural')
    bpy.ops.wm.save_as_mainfile(filepath=str(out / 'head-procedural.blend'))
    mat = obj.data.materials[0]
    defaults = shader_defaults(mat)
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    bsdf = next(n for n in nodes if n.type == 'BSDF_PRINCIPLED')
    output = next(n for n in nodes if n.type == 'OUTPUT_MATERIAL')
    color = bsdf.inputs['Base Color'].links[0].from_socket
    emission = nodes.new('ShaderNodeEmission')
    links.new(color, emission.inputs['Color'])
    links.new(emission.outputs[0], output.inputs['Surface'])
    atlas = bpy.data.images.new('MF_cleaned_base_color', width=2048, height=2048, alpha=False)
    atlas.colorspace_settings.name = 'sRGB'
    target = nodes.new('ShaderNodeTexImage'); target.image = atlas
    nodes.active = target
    for n in nodes:
        n.select = n == target
    bpy.ops.object.select_all(action='DESELECT')
    obj.hide_set(False); obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    # Primary UV is the portable atlas; projection layers are shader inputs only.
    obj.data.uv_layers.active.active_render = True
    scene.render.bake.margin = 16
    bpy.ops.object.bake(type='EMIT')
    atlas.filepath_raw = str(out / 'cleaned-base-color.png')
    atlas.file_format = 'PNG'; atlas.save(); atlas.pack()
    links.new(bsdf.outputs[0], output.inputs['Surface'])
    # A minimal portable material avoids accidental export of procedural nodes.
    baked = bpy.data.materials.new('MF_cleaned_portable'); baked.use_nodes = True
    shader = baked.node_tree.nodes.get('Principled BSDF')
    for name, value in defaults.items():
        socket = shader.inputs.get(name)
        if socket is not None:
            socket.default_value = value
    texture = baked.node_tree.nodes.new('ShaderNodeTexImage'); texture.image = atlas
    uv = baked.node_tree.nodes.new('ShaderNodeUVMap'); uv.uv_map = obj.data.uv_layers.active.name
    baked.node_tree.links.new(uv.outputs['UV'],texture.inputs['Vector'])
    baked.node_tree.links.new(texture.outputs['Color'],shader.inputs['Base Color'])
    obj.data.materials[0] = baked
    report['geometry_after'] = geometry_digest(obj)
    if report['geometry_after'] != report['geometry_before']:
        raise ValueError('Bake changed protected geometry')
    render_views(scene, camera, out, 'baked')
    bpy.ops.wm.save_as_mainfile(filepath=str(out / 'head-baked.blend'))
    bpy.ops.export_scene.gltf(filepath=str(out / 'head-cleaned.glb'), export_format='GLB', use_selection=True)
    (out / 'material-sidecar.json').write_text(json.dumps(defaults, indent=2))
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(out / 'head-cleaned.glb'), import_pack_images=True)
    meshes = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    if len(meshes) != 1:
        raise ValueError('Expected one imported head')
    imported = meshes[0]
    shader = next(n for n in imported.data.materials[0].node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    for name, value in defaults.items():
        socket = shader.inputs.get(name)
        if socket is not None and not socket.is_linked:
            socket.default_value = value
    scene, camera = setup_review(imported); scene.cycles.samples = 32
    render_views(scene, camera, out, 'roundtrip')
    bpy.ops.wm.save_as_mainfile(filepath=str(out / 'head-roundtrip.blend'))
    report['roundtrip'] = {'meshes': len(meshes), 'vertices': len(imported.data.vertices),
                           'faces': len(imported.data.polygons), 'policy': 'GLB plus Principled defaults sidecar; no add-on'}
    report['source_preserved'] = hashlib.sha256(SOURCE.read_bytes()).hexdigest() == DIGEST
    if not report['source_preserved']:
        raise ValueError('Source mutated')
    (out / 'result.json').write_text(json.dumps(report, indent=2))


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
    if job['operation'] == 'portable_cleanup':
        portable_cleanup(obj, low, high, out, report)
        return
    if job['operation'] in {'jaw_diagnostic', 'jaw_projection_preview'}:
        jaw_diagnostic(obj, low, high, out, report, job['operation'] == 'jaw_projection_preview')
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
