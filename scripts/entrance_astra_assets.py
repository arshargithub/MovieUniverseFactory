"""Fixed read-only inventory of the original admitted horse asset."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import wardrobe_motion178 as base


def validate(job):
    if job != {'operation': 'original-horse-datablocks'}:
        raise ValueError('Fixed inventory operation required')
    source = ROOT / '.runtime/assets/demonstrator-01/horse.blend'
    if source.is_symlink() or base.digest(source) != 'b848037332fe62064989f250a94faa04c75e3fb21ae93f6a100f19079c1b21aa':
        raise ValueError('Original horse source mismatch')
    out = base.BASE / 'entrance-astra-horse-datablocks'
    if out.exists():
        raise ValueError('Preserve previous inventory')
    return source, out


def main():
    import bpy
    args = sys.argv[sys.argv.index('--') + 1:]
    if len(args) != 1:
        raise ValueError('One structured job required')
    source, out = validate(json.loads(Path(args[0]).read_text()))
    out.mkdir()
    # Read data without activating the legacy rig/dependency graph. The first
    # full-open inventory failed on an invalid legacy shape-key pointer.
    with bpy.data.libraries.load(str(source), link=False) as (available, loaded):
        loaded.meshes = available.meshes
        loaded.materials = available.materials
        loaded.images = available.images
    data = {'objects': [], 'materials': [], 'images': []}
    for mesh in loaded.meshes:
        if mesh:
            data['objects'].append({'name': mesh.name, 'vertices': len(mesh.vertices),
                'polygons': len(mesh.polygons), 'uv_layers': list(mesh.uv_layers.keys()),
                'materials': [m.name if m else None for m in mesh.materials]})
    for m in bpy.data.materials:
        data['materials'].append({'name': m.name, 'nodes': [
            {'type': n.bl_idname, 'name': n.name, 'image': getattr(getattr(n, 'image', None), 'name', None)}
            for n in m.node_tree.nodes] if m.use_nodes else [], 'color': list(m.diffuse_color)})
    for im in bpy.data.images:
        data['images'].append({'name': im.name, 'filepath': im.filepath, 'packed': bool(im.packed_file), 'size': list(im.size)})
    data['source_sha256'] = base.digest(source)
    (out / 'inventory.json').write_text(json.dumps(data, indent=2) + '\n')
    print(json.dumps(data), flush=True)


if __name__ == '__main__':
    main()
