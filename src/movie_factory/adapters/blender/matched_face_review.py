"""Render-only, camera-relative lighting comparison of the pinned current head."""
import hashlib
import json
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / '.runtime/art-direction/series01-facebuilder-trial-01'
SOURCE = BASE / 'bilateral-04/head-bilateral.blend'
SHA = 'c263b6b715548e8fee58661eadd6f26f8b37c81295ae0fcc2c830a3786561322'


def rotate_z(point, degrees):
    a = math.radians(degrees)
    x, y, z = point
    return (x*math.cos(a)-y*math.sin(a), x*math.sin(a)+y*math.cos(a), z)


def validate(job):
    if job != {'operation': 'matched_lighting', 'output_name': 'matched-light-01'}:
        raise ValueError('Only the fixed render-only comparison is admitted')
    if SOURCE.is_symlink() or hashlib.sha256(SOURCE.read_bytes()).hexdigest() != SHA:
        raise ValueError('Source changed')
    out = BASE / job['output_name']
    if out.exists():
        raise ValueError('No overwrite')
    return out


def run(job):
    out = validate(job)
    import bpy
    from mathutils import Vector
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from likeness_cleanup import geometry_digest
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE), load_ui=False, use_scripts=False)
    head = bpy.data.objects['FBHead']
    before = geometry_digest(head)
    scene = bpy.context.scene
    camera = scene.camera
    target = Vector((0, 0, -.16))
    for obj in scene.objects:
        if obj.type == 'LIGHT':
            obj.hide_render = True
    lights = []
    # Symmetric broad lights avoid assigning the nearer cheek a different key/fill.
    for side in (-1, 1):
        data = bpy.data.lights.new('MF_matched_light', 'AREA')
        data.energy, data.shape, data.size = 300, 'DISK', 5
        light = bpy.data.objects.new(data.name, data)
        scene.collection.objects.link(light)
        lights.append((light, (side*3, -4, 3)))
    scene.world = bpy.data.worlds.new('MF_matched_uniform_world')
    scene.world.use_nodes = True
    scene.world.node_tree.nodes['Background'].inputs[0].default_value = (.12, .12, .12, 1)
    scene.world.node_tree.nodes['Background'].inputs[1].default_value = 1
    scene.render.resolution_x, scene.render.resolution_y = 768, 960
    scene.render.resolution_percentage = 100
    scene.cycles.samples = 32
    scene.cycles.seed = 0
    scene.cycles.use_animated_seed = False
    out.mkdir()
    views = {}
    for label, angle in [('left', -30), ('right', 30)]:
        camera.location = target + Vector(rotate_z((0, -6, 0), angle))
        camera.rotation_euler = (target-camera.location).to_track_quat('-Z', 'Y').to_euler()
        for light, offset in lights:
            light.location = target + Vector(rotate_z(offset, angle))
            light.rotation_euler = (target-light.location).to_track_quat('-Z', 'Y').to_euler()
        views[label] = {'camera': list(camera.location), 'lights': [list(l.location) for l, _ in lights]}
        scene.render.filepath = str(out / (label+'.png'))
        bpy.ops.render.render(write_still=True)
    assert geometry_digest(head) == before
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == SHA
    (out/'result.json').write_text(json.dumps({
        'source_sha256': SHA, 'geometry_digest': before, 'views': views,
        'light_power_each': 300, 'light_size_each': 5,
        'material_changes': False, 'source_scene_saved': False,
        'limitation': 'Baked texture shading and geometry/garment occlusion remain; not an unlit albedo view.'
    }, indent=2))


if __name__ == '__main__':
    args = sys.argv[sys.argv.index('--')+1:]
    if len(args) != 1:
        raise ValueError('One structured job file required')
    run(json.loads(Path(args[0]).read_text()))
