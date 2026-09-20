"""Pinned, data-only inspection and static fitting of the Director-supplied hijab.

No source changes, runtime code strings, external resources or provider calls.
"""
import hashlib
import json
import math
from pathlib import Path
import shutil
import struct
import sys

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / '.runtime/art-direction/series01-facebuilder-trial-01'
DONOR = ROOT / '.runtime/assets/series01-dressing-source/lam-m-zack-hijab/hijab.glb'
SHA = 'c209b25a85a8dad1def97880ee400af23d38ded876e578968004bee59203700a'
HEAD = BASE / 'bilateral-04/head-bilateral.blend'
HEAD_SHA = 'c263b6b715548e8fee58661eadd6f26f8b37c81295ae0fcc2c830a3786561322'


def inspect_glb(raw):
    if len(raw) < 20 or struct.unpack_from('<4sII', raw) != (b'glTF', 2, len(raw)):
        raise ValueError('Invalid GLB')
    size, kind = struct.unpack_from('<II', raw, 12)
    if kind != 0x4E4F534A or size > len(raw)-20:
        raise ValueError('Invalid JSON chunk')
    doc = json.loads(raw[20:20+size])
    if any('uri' in x for k in ('buffers', 'images') for x in doc.get(k, [])):
        raise ValueError('External resources prohibited')
    if doc.get('extensionsUsed') or len(doc.get('meshes', [])) != 1:
        raise ValueError('Unexpected donor structure')
    if sum(a.get('count', 0) for a in doc.get('accessors', [])) > 200000:
        raise ValueError('Excessive geometry')
    return doc


def validate(job):
    if not isinstance(job, dict) or set(job) != {'operation', 'stage'}:
        raise ValueError('Invalid keys')
    if job['operation'] != 'hijab_donor' or job['stage'] not in ('audit', 'fit01', 'fit02', 'verify02'):
        raise ValueError('Unsupported operation/stage')
    for path, digest in ((DONOR, SHA), (HEAD, HEAD_SHA)):
        if path.is_symlink() or hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            raise ValueError('Source changed')
    inspect_glb(DONOR.read_bytes())
    out = BASE / ('hijab-' + job['stage'])
    if out.exists() or shutil.disk_usage(BASE).free < 5_000_000_000:
        raise ValueError('Existing output or insufficient disk')
    return out


def bounds(obj):
    points = [obj.matrix_world @ v.co for v in obj.data.vertices]
    return [[min(p[i] for p in points) for i in range(3)],
            [max(p[i] for p in points) for i in range(3)]]


def fit_point(point, variant=1):
    x, y, z = point
    original_z = z
    lower = max(0., min(1., (.65-z)/1.1))
    front = max(0., min(1., (.7-y)/1.4))
    x = x * (1.25 + .10*lower)
    y = y * .85 - .40
    z = z * .90 - .70 - .60*lower*front
    if variant == 2:
        x *= .90 + .10*lower
        # Move only the lower front wrap down, preserving the crown and face.
        weight = max(0., min(1., (1.15-original_z)/1.15))
        z -= .65*weight*front
        y += .10*(1-lower)
    if z < -1.7:
        z = -1.7 + (z+1.7)*.55
    return (x, y, z)


def connected_groups(bm):
    seen = set(); groups = []
    for vertex in bm.verts:
        if vertex in seen:
            continue
        seen.add(vertex); todo = [vertex]; group = []
        while todo:
            current = todo.pop(); group.append(current)
            for edge in current.link_edges:
                other = edge.other_vert(current)
                if other not in seen:
                    seen.add(other); todo.append(other)
        groups.append(group)
    return sorted(groups, key=len, reverse=True)


def material_signature(mat):
    nodes = []
    for node in mat.node_tree.nodes:
        inputs = {}
        for socket in node.inputs:
            if hasattr(socket, 'default_value'):
                value = socket.default_value
                if isinstance(value, (str, bool, int, float)):
                    inputs[socket.identifier] = value
                else:
                    try: inputs[socket.identifier] = list(value)
                    except TypeError: pass
        nodes.append((node.name, node.bl_idname, inputs,
                      node.image.name if node.type == 'TEX_IMAGE' and node.image else None))
    links = [(l.from_node.name, l.from_socket.identifier, l.to_node.name, l.to_socket.identifier)
             for l in mat.node_tree.links]
    return hashlib.sha256(json.dumps([nodes, links], sort_keys=True).encode()).hexdigest()


def review(scene, out, target, scale, angles, *, portrait=False):
    import bpy
    from mathutils import Vector
    from matched_face_review import rotate_z
    for o in scene.objects:
        if o.type == 'LIGHT':
            o.hide_render = True
    data = bpy.data.cameras.new('MF_hijab_review')
    cam = bpy.data.objects.new(data.name, data)
    scene.collection.objects.link(cam)
    scene.camera = cam
    data.type = 'ORTHO'; data.ortho_scale = scale
    lights = []
    for sign in (-1, 1):
        ld = bpy.data.lights.new('MF_hijab_softbox', 'AREA')
        ld.energy = 300; ld.shape = 'DISK'; ld.size = 5
        ob = bpy.data.objects.new(ld.name, ld); scene.collection.objects.link(ob)
        lights.append((ob, (sign*3, -4, 3)))
    scene.world = bpy.data.worlds.new('MF_hijab_world'); scene.world.use_nodes = True
    bg = scene.world.node_tree.nodes['Background']; bg.inputs[0].default_value = (.12, .12, .12, 1)
    scene.render.engine = 'CYCLES'; scene.cycles.samples = 24; scene.cycles.seed = 0
    scene.render.resolution_x = 640; scene.render.resolution_y = 800
    scene.render.resolution_percentage = 100
    if portrait:
        scene.render.resolution_x = 955; scene.render.resolution_y = 1647
        scene.cycles.samples = 64
    target = Vector(target)
    for label, angle in angles:
        cam.location = target + Vector(rotate_z((0, -10, 0), angle))
        cam.rotation_euler = (target-cam.location).to_track_quat('-Z', 'Y').to_euler()
        for ob, offset in lights:
            ob.location = target + Vector(rotate_z(offset, angle))
            ob.rotation_euler = (target-ob.location).to_track_quat('-Z', 'Y').to_euler()
        scene.render.filepath = str(out / (label+'.png'))
        bpy.ops.render.render(write_still=True)
    # Leave the saved scene on the first reviewed view, including its lighting.
    angle = angles[0][1]
    cam.location = target + Vector(rotate_z((0, -10, 0), angle))
    cam.rotation_euler = (target-cam.location).to_track_quat('-Z', 'Y').to_euler()
    for ob, offset in lights:
        ob.location = target + Vector(rotate_z(offset, angle))
        ob.rotation_euler = (target-ob.location).to_track_quat('-Z', 'Y').to_euler()


def run(job):
    out = validate(job)
    import bpy
    import bmesh
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from likeness_cleanup import geometry_digest
    bpy.ops.wm.open_mainfile(filepath=str(HEAD), load_ui=False, use_scripts=False)
    head = bpy.data.objects['FBHead']; before = geometry_digest(head)
    material = head.data.materials[0]
    material_before = material_signature(material)
    shapes = {k.name: k.value for k in head.data.shape_keys.key_blocks}
    head_bounds = bounds(head)
    if job['stage'] == 'verify02':
        candidate = BASE/'hijab-fit02/donor.blend'
        record = json.loads((candidate.parent/'result.json').read_text())
        assert hashlib.sha256(candidate.read_bytes()).hexdigest() == record['native_sha256']
        bpy.ops.wm.open_mainfile(filepath=str(candidate), load_ui=False, use_scripts=False)
        reopened = bpy.data.objects['FBHead']
        assert geometry_digest(reopened) == before
        assert material_signature(reopened.data.materials[0]) == material_before
        assert shapes == {k.name:k.value for k in reopened.data.shape_keys.key_blocks}
        assert bpy.data.objects.get('MF_lam_m_zack_hijab') is not None
        out.mkdir()
        (out/'result.json').write_text(json.dumps({'native_sha256':record['native_sha256'],
            'reopened':True, 'protected_geometry_shapes_material_graph_unchanged':True,
            'head_source_sha256':HEAD_SHA}, indent=2))
        return
    if job['stage'] == 'audit':
        for obj in list(bpy.context.scene.objects):
            bpy.data.objects.remove(obj, do_unlink=True)
    else:
        for obj in list(bpy.context.scene.objects):
            if obj.type == 'MESH' and obj != head:
                obj.hide_render = True
    prior = set(bpy.context.scene.objects)
    bpy.ops.import_scene.gltf(filepath=str(DONOR), import_pack_images=True)
    imported = [o for o in bpy.context.scene.objects if o not in prior and o.type == 'MESH']
    if len(imported) != 1:
        raise ValueError('Expected one mesh')
    obj = imported[0]; original_bounds = bounds(obj)
    points = [obj.matrix_world @ v.co for v in obj.data.vertices]
    obj.parent = None; obj.matrix_world.identity()
    for v, p in zip(obj.data.vertices, points):
        v.co = p
    obj.name = 'MF_lam_m_zack_hijab'
    bm = bmesh.new(); bm.from_mesh(obj.data)
    original_vertices = len(bm.verts)
    bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=0.00001)
    stats = {'imported_vertices': original_vertices, 'welded_vertices': len(bm.verts),
             'faces': len(bm.faces), 'boundary_edges': sum(e.is_boundary for e in bm.edges)}
    groups = connected_groups(bm)
    stats['connected_component_sizes'] = [len(g) for g in groups]
    if job['stage'] in ('fit01', 'fit02'):
        if [len(g) for g in groups] != [2481, 412]:
            raise ValueError('Audited component structure changed')
        bmesh.ops.delete(bm, geom=groups[1], context='VERTS')
        for vertex in bm.verts:
            vertex.co = fit_point(vertex.co, 2 if job['stage'] == 'fit02' else 1)
        bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
        stats['retained_garment_vertices'] = len(bm.verts)
    bm.to_mesh(obj.data); bm.free()
    for p in obj.data.polygons:
        p.use_smooth = True
    out.mkdir()
    scene = bpy.context.scene
    if job['stage'] == 'audit':
        lo, hi = original_bounds
        review(scene, out, [(a+b)/2 for a,b in zip(lo, hi)], 7.5,
               [('front', 0), ('left', -60), ('right', 60), ('back', 180)])
    else:
        from dressing_renewal import cloth_material
        obj.data.materials.clear(); obj.data.materials.append(cloth_material())
        solid = obj.modifiers.new('Thin cloth edge', 'SOLIDIFY'); solid.thickness = .008
        review(scene, out, (0, -.1, -.60), 5.6,
               [('front', 0), ('left', -45), ('right', 45)])
        assert geometry_digest(head) == before
        assert head.data.materials[0] == material
        assert material_signature(material) == material_before
        assert shapes == {k.name: k.value for k in head.data.shape_keys.key_blocks}
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'donor.blend'))
    (out/'result.json').write_text(json.dumps({
        'donor_sha256': SHA, 'credit': inspect_glb(DONOR.read_bytes())['asset']['extras'],
        'source_bounds': original_bounds, 'head_bounds': head_bounds, 'mesh': stats,
        'head_source_sha256': HEAD_SHA, 'head_geometry_digest': before,
        'stage': job['stage'], 'protected_material_name': material.name,
        'native_sha256': hashlib.sha256((out/'donor.blend').read_bytes()).hexdigest(),
        'shape_values': shapes, 'scope': 'Static donor audit/fit; no aesthetic acceptance or animation qualification'
    }, indent=2))
    assert hashlib.sha256(HEAD.read_bytes()).hexdigest() == HEAD_SHA


if __name__ == '__main__':
    args = sys.argv[sys.argv.index('--')+1:]
    if len(args) != 1:
        raise ValueError('One structured job required')
    run(json.loads(Path(args[0]).read_text()))
