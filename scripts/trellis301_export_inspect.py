"""Fixed-camera, fixed-scale export controls; no actor admission or network in Blender."""
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / '.runtime/trellis301/export/retrieved/evidence'
OUT = ROOT / '.runtime/trellis301/export-review'
BASE = ROOT / '.runtime/art-direction/series01-trellis298/head512-remeshed/source.blend'
VARIANTS = ('300000-2048', '1000000-2048', '1000000-4096')
VIEWS = (('front', 0), ('left-quarter', 45), ('left-profile', 90), ('back', 180),
         ('right-profile', 270), ('right-quarter', 315))


def validate(job):
    if set(job) != {'operation', 'variant'} or job['operation'] not in ('render', 'reopen') or job['variant'] not in VARIANTS:
        raise ValueError('Unadmitted export-review operation')


def worker(job):
    validate(job)
    import bpy
    from mathutils import Matrix
    sys.path.insert(0, str(ROOT / 'scripts'))
    from trellis301_prepare import sha, dump
    from trellis298_inspect import aim, snapshot
    assert not bpy.app.online_access
    variant = job['variant']
    folder = OUT / variant
    folder.mkdir(parents=True, exist_ok=True)
    source = SOURCE / f'head-{variant}.glb'
    receipt = json.loads((SOURCE / f'head-{variant}.json').read_text())
    assert sha(source) == receipt['glb_sha256']
    if job['operation'] == 'reopen':
        bpy.ops.wm.open_mainfile(filepath=str(folder / 'source.blend'))
        expected = json.loads((folder / 'inspection.json').read_text())['geometry']
        actual = snapshot()
        dump(folder / 'reopen.json', {'geometry_binding_exact': expected == actual, 'actor_ready': False})
        assert expected == actual
        return
    bpy.ops.wm.open_mainfile(filepath=str(BASE))
    normalization = bpy.data.objects['Source normalization'].matrix_world.copy()
    # Keep the baseline camera, lights and world, remove only the old asset.
    for obj in list(bpy.context.scene.objects):
        if obj.type in ('MESH', 'EMPTY'):
            bpy.data.objects.remove(obj, do_unlink=True)
    before = set(bpy.context.scene.objects)
    bpy.ops.import_scene.gltf(filepath=str(source))
    imported = set(bpy.context.scene.objects) - before
    meshes = [obj for obj in imported if obj.type == 'MESH']
    assert meshes
    # Apply identical source normalization to every root, not independent fit-to-frame.
    for obj in imported:
        if obj.parent not in imported:
            obj.matrix_world = normalization @ obj.matrix_world
    for obj in meshes:
        for polygon in obj.data.polygons:
            polygon.use_smooth = True
        for material in obj.data.materials:
            bsdf = next(n for n in material.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
            # Opacity is held constant; the prior separate alpha experiment failed.
            for link in list(bsdf.inputs['Alpha'].links):
                material.node_tree.links.remove(link)
            bsdf.inputs['Alpha'].default_value = 1
    scene = bpy.context.scene
    scene.cycles.device = 'CPU'
    scene.cycles.seed = 301
    scene.render.threads_mode = 'FIXED'
    scene.render.threads = 4
    bpy.context.view_layer.update()
    original = snapshot()
    for name, degrees in VIEWS:
        angle = math.radians(degrees)
        aim(scene.camera, (2.5*math.sin(angle), -2.5*math.cos(angle), .04), (0,0,0))
        scene.render.filepath = str(folder / f'{name}.png')
        assert 'FINISHED' in bpy.ops.render.render(write_still=True)
    clay = bpy.data.materials.new('Export geometry diagnostic')
    clay.use_nodes = True
    clay.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value = (.36,.36,.36,1)
    clay.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value = .8
    bpy.context.view_layer.material_override = clay
    for name, degrees in (VIEWS[0], VIEWS[1], VIEWS[-1]):
        angle = math.radians(degrees)
        aim(scene.camera, (2.5*math.sin(angle), -2.5*math.cos(angle), .04), (0,0,0))
        scene.render.filepath = str(folder / f'{name}-clay.png')
        assert 'FINISHED' in bpy.ops.render.render(write_still=True)
    bpy.context.view_layer.material_override = None
    assert snapshot() == original
    aim(scene.camera, (0,-2.5,.04), (0,0,0))
    bpy.ops.file.pack_all()
    dump(folder / 'inspection.json', {'source_sha256': sha(source), 'geometry': original,
         'normalization_matrix': [list(row) for row in normalization],
         'matched_to_baseline': str(BASE.relative_to(ROOT)), 'opacity_held': 1,
         'source_quality': 'NOT_RUN', 'actor_ready': False})
    bpy.ops.wm.save_as_mainfile(filepath=str(folder / 'source.blend'))


def main():
    from movie_factory import production_knowledge as pk
    from trellis301_prepare import sha, dump
    task = json.loads((ROOT / 'results/trellis301/task.json').read_text())
    task.update(id='trellis301-export-visual-control', phase='execution')
    paths = [Path(__file__), BASE, ROOT / 'scripts/trellis298_inspect.py', SOURCE / 'comparison-receipt.json']
    paths += [SOURCE / f'head-{v}{ext}' for v in VARIANTS for ext in ('.json','.glb')]
    task['inputs'].update({str(p.relative_to(ROOT)): sha(p) for p in paths})
    packet = pk.task_packet(ROOT, task)
    OUT.mkdir(parents=True, exist_ok=True)
    dump(OUT / 'packet.json', packet)
    if not packet['dispatch_ready']:
        raise RuntimeError(packet['blockers'])
    if subprocess.run(['pgrep','-fl','/Applications/Blender.app/Contents/MacOS/Blender'],capture_output=True).returncode == 0:
        raise RuntimeError('Blender slot occupied')
    env = {k: os.environ[k] for k in ('PATH','HOME','TMPDIR','LANG','LC_ALL') if k in os.environ}
    for variant in VARIANTS:
        for op in ('render','reopen'):
            job = {'operation':op,'variant':variant}
            validate(job)
            start = time.monotonic()
            with (OUT / f'{variant}-{op}.log').open('w') as log:
                result = subprocess.run(['/Applications/Blender.app/Contents/MacOS/Blender','--background',
                    '--offline-mode','--factory-startup','--disable-autoexec','--python-exit-code','7',
                    '--python',str(Path(__file__).resolve()),'--',json.dumps(job)],
                    env=env,stdout=log,stderr=subprocess.STDOUT)
            dump(OUT / f'{variant}-{op}-job.json', {'returncode':result.returncode,'process_seconds':time.monotonic()-start})
            if result.returncode:
                raise RuntimeError(f'{variant} {op} failed')


if __name__ == '__main__':
    worker(json.loads(sys.argv[sys.argv.index('--')+1])) if '--' in sys.argv else main()
