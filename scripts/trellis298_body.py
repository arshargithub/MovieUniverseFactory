"""Fixed read-only body/rig inventory before choosing an actor integration."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / '.runtime/art-direction/series01-sikh270/candidate-17/character.blend'
SOURCE_SHA = 'd32a2152b7bee216cfb2e727291c8f2d147a8987401985ac75c24bec12e3fa5b'
OUT = ROOT / 'results/trellis298/body-inventory.json'


def worker(job):
    if job != {'operation': 'inventory'}:
        raise ValueError('Only read-only body inventory allowed')
    import bpy
    from mathutils import Vector
    assert not bpy.app.online_access
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == SOURCE_SHA
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE), load_ui=False, use_scripts=False)
    body = bpy.data.objects['Sikh269 coherent editable anatomy']
    rig = next(m.object for m in body.modifiers if m.type == 'ARMATURE')
    points = [body.matrix_world @ v.co for v in body.data.vertices]
    data = {'source_sha256': SOURCE_SHA, 'source_visual_status': 'REJECTED_HEAD_NOT_REUSED',
            'body_name': body.name, 'vertices': len(points), 'faces': len(body.data.polygons),
            'bounds': [[min(v[k] for v in points) for k in range(3)], [max(v[k] for v in points) for k in range(3)]],
            'groups': [g.name for g in body.vertex_groups],
            'bones': {b.name: {'head': list(rig.matrix_world @ b.head_local), 'tail': list(rig.matrix_world @ b.tail_local),
                               'parent': b.parent.name if b.parent else None, 'deform': b.use_deform} for b in rig.data.bones},
            'modifiers': [{'name': m.name, 'type': m.type} for m in body.modifiers],
            'shape_keys': [k.name for k in body.data.shape_keys.key_blocks] if body.data.shape_keys else [],
            'scope': 'Engineering substrate inventory only; no anatomy, new head, rig performance or visual acceptance'}
    OUT.write_text(json.dumps(data, indent=2))


def main():
    from movie_factory import production_knowledge as pk
    task = json.loads((ROOT / 'results/trellis298/task.json').read_text())
    task.update(id='trellis298-body-inventory', phase='execution')
    for p in (SOURCE, Path(__file__)):
        task['inputs'][str(p.relative_to(ROOT))] = hashlib.sha256(p.read_bytes()).hexdigest()
    packet = pk.task_packet(ROOT, task)
    (OUT.parent / 'body-packet.json').write_text(json.dumps(packet, indent=2))
    assert packet['dispatch_ready'], packet['blockers']
    env = {k: os.environ[k] for k in ('PATH', 'HOME', 'TMPDIR', 'LANG', 'LC_ALL') if k in os.environ}
    with (OUT.parent / 'body-inventory.log').open('w') as log:
        subprocess.run(['/Applications/Blender.app/Contents/MacOS/Blender', '--background', '--offline-mode',
            '--factory-startup', '--disable-autoexec', '--python-exit-code', '7', '--python', str(Path(__file__).resolve()),
            '--', json.dumps({'operation': 'inventory'})], env=env, stdout=log, stderr=subprocess.STDOUT, check=True)
    print('Read-only body and rig inventory saved; no source changes')


if __name__ == '__main__':
    worker(json.loads(sys.argv[sys.argv.index('--')+1])) if '--' in sys.argv else main()
