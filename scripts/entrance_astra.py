"""Source-bound entrance art proof. Fixed reviewed operations only."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import entrance187 as prior
BASE = prior.actor.base.BASE
ASSETS = ROOT / '.runtime/assets/entrance-astra'


def validate(job):
    if not isinstance(job, dict) or set(job) != {'operation'} or job['operation'] not in ('audit01', 'proof01', 'proof02', 'hybrid03', 'hybrid04'):
        raise ValueError('Fixed art operation required')
    if prior.actor.base.digest(prior.SOURCE) != prior.SOURCE_SHA:
        raise ValueError('Actor source mismatch')
    out = BASE / ('entrance-astra-' + job['operation'])
    if out.exists() or out.is_symlink():
        raise ValueError('Preserve evidence')
    manifest = json.loads((ASSETS / 'manifest.json').read_text())
    for row in manifest['files']:
        path = ASSETS / row['path']
        if not path.resolve().is_relative_to(ASSETS.resolve()) or path.is_symlink() or prior.actor.base.digest(path) != row['sha256']:
            raise ValueError('Asset dependency mismatch')
    return out


def horse_restore():
    import bpy
    import numpy as np
    source = ROOT / '.runtime/assets/demonstrator-01/horse.blend'
    if prior.actor.base.digest(source) != 'b848037332fe62064989f250a94faa04c75e3fb21ae93f6a100f19079c1b21aa':
        raise ValueError('Horse source mismatch')
    with bpy.data.libraries.load(str(source), link=False) as (available, loaded):
        loaded.meshes = ['horseMesh.001']
        loaded.materials = [n for n in available.materials if n.startswith(('horse', 'saddle.', 'quilt.'))]
    original = loaded.meshes[0]
    horse = bpy.data.objects['MF185_gait_horse']
    horse.data = horse.data.copy()
    ratio = len(horse.data.polygons) / len(original.polygons)
    level = next((i for i in range(4) if 4 ** i == ratio), None)
    if level is None:
        raise ValueError('Unknown horse topology ratio ' + str(ratio))
    temp = bpy.data.objects.new('AS_original_horse_material_control', original)
    bpy.context.scene.collection.objects.link(temp)
    if level:
        sub = temp.modifiers.new('Original topology recovery', 'SUBSURF')
        sub.levels = sub.render_levels = level
    bpy.context.view_layer.update()
    ev = temp.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh = ev.to_mesh(preserve_all_data_layers=True, depsgraph=bpy.context.evaluated_depsgraph_get())
    if len(mesh.loops) != len(horse.data.loops):
        raise ValueError('Horse corner topology mismatch')
    a = np.empty(len(mesh.loops) * 2, dtype=np.float32)
    b = np.empty_like(a)
    mesh.uv_layers.active.data.foreach_get('uv', a)
    horse.data.uv_layers.active.data.foreach_get('uv', b)
    uv_error = float(np.max(abs(a-b)))
    if uv_error > 1e-5:
        raise ValueError('Horse UV order mismatch ' + str(uv_error))
    labels = np.array([p.material_index for p in mesh.polygons], dtype=np.int32)
    materials = list(original.materials)
    horse.data.materials.clear()
    for mat in materials:
        horse.data.materials.append(mat)
    horse.data.polygons.foreach_set('material_index', labels)
    ev.to_mesh_clear()
    bpy.data.objects.remove(temp, do_unlink=True)
    # Existing UVs + exact corner order recover eyes, hoof and coat ownership.
    # Reuse a native brown/black coat rather than random white spot options.
    brown = next(m for m in loaded.materials if m and m.name.startswith('horse_body.brown_black'))
    horse.data.materials[0] = brown
    result = {'uv_max_error': uv_error, 'subdivision_level': level,
              'target_polygons': len(labels), 'labels': {str(int(i)): int(np.sum(labels==i)) for i in np.unique(labels)},
              'material_names': [m.name for m in horse.data.materials]}
    for name in ('saddle', 'saddle.pad'):
        ob = bpy.data.objects['MF185_gait_' + name]
        ob.data = ob.data.copy()
        ob.data.materials.clear()
        matname = 'saddle.random' if name == 'saddle' else 'quilt.dark'
        ob.data.materials.append(next(m for m in loaded.materials if m and m.name.startswith(matname)))
        for face in ob.data.polygons:
            face.material_index = 0
    return result


def import_asset(name):
    import bpy
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=str(ASSETS / name / (name + '.gltf')))
    objects = [o for o in set(bpy.data.objects)-before if o.type == 'MESH']
    return objects


def main():
    import bpy
    args = sys.argv[sys.argv.index('--') + 1:]
    if len(args) != 1:
        raise ValueError('One structured job required')
    job = json.loads(Path(args[0]).read_text())
    out = validate(job)
    out.mkdir()
    (out / 'handler.py').write_bytes(Path(__file__).read_bytes())
    bpy.ops.wm.open_mainfile(filepath=str(prior.SOURCE), load_ui=False, use_scripts=False)
    prior.actor.base.check_protected()
    result = {'source_sha256': prior.SOURCE_SHA, 'horse': horse_restore(), 'assets': []}
    if job['operation'] == 'audit01':
        for asset in ('rock_face_01', 'namaqualand_boulder_03', 'pine_sapling_small', 'shrub_02'):
            objects = import_asset(asset)
            result['assets'].append({'asset': asset, 'objects': [
                {'name': o.name, 'vertices': len(o.data.vertices), 'dimensions': list(o.dimensions),
                 'position': list(o.location), 'materials': [m.name for m in o.data.materials]}
                for o in objects]})
        result['horse_nodes'] = {m.name:[{'name':n.name,'type':n.bl_idname,
            'inputs':{i.name:list(i.default_value) if hasattr(i.default_value,'__len__') else i.default_value
                      for i in n.inputs if hasattr(i,'default_value') and isinstance(i.default_value,(float,int))}}
            for n in m.node_tree.nodes] for m in bpy.data.objects['MF185_gait_horse'].data.materials if m.use_nodes}
    else:
        import entrance_astra_world as world
        (out / 'world-handler.py').write_bytes(Path(world.__file__).read_bytes())
        result.update(world.build_and_render(out))
    (out / 'result.json').write_text(json.dumps(result, indent=2) + '\n')
    prior.actor.base.check_protected()
    print('Completed', job['operation'], flush=True)


if __name__ == '__main__':
    main()
