"""Structured offline opacity diagnostic. Launch only when shared Blender slot is free."""
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / '.runtime/art-direction/series01-trellis298/head512-remeshed/source.blend'
OUT = ROOT / '.runtime/trellis301/opacity'


def validate(job):
    if job != {'operation': 'opacity-control'}:
        raise ValueError('Unsupported structured301 operation')


def worker(job):
    validate(job)
    import bpy
    sys.path.insert(0, str(ROOT / 'scripts'))
    import trellis298_inspect as old
    if bpy.app.online_access:
        raise RuntimeError('Offline Blender required')
    OUT.mkdir(parents=True, exist_ok=True)
    baseline_snapshot = None
    for variant in ('opaque', 'alpha'):
        bpy.ops.wm.open_mainfile(filepath=str(BASE))
        snap = old.snapshot()
        if baseline_snapshot is None:
            baseline_snapshot = snap
        if snap != baseline_snapshot:
            raise RuntimeError('Source reopen changed')
        materials = {m for obj in bpy.context.scene.objects if obj.type == 'MESH' for m in obj.data.materials}
        changes = []
        if variant == 'alpha':
            for material in materials:
                bsdf = next(n for n in material.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
                links = bsdf.inputs['Base Color'].links
                if len(links) != 1 or links[0].from_node.type != 'TEX_IMAGE':
                    raise RuntimeError('Unexpected source base-color routing')
                image_node = links[0].from_node
                if image_node.image.channels != 4:
                    raise RuntimeError('Missing alpha channel')
                for link in list(bsdf.inputs['Alpha'].links):
                    material.node_tree.links.remove(link)
                material.node_tree.links.new(image_node.outputs['Alpha'], bsdf.inputs['Alpha'])
                changes.append({'material': material.name, 'alpha_image': image_node.image.name})
        scene = bpy.context.scene
        scene.render.threads_mode = 'FIXED'
        scene.render.threads = 4
        scene.cycles.seed = 301
        for name, angle in [('front', 0), ('left-quarter', 45), ('right-quarter', 315), ('back', 180)]:
            radians = math.radians(angle)
            old.aim(scene.camera, (2.5 * math.sin(radians), -2.5 * math.cos(radians), .04), (0, 0, 0))
            scene.render.filepath = str(OUT / f'{variant}-{name}.png')
            if 'FINISHED' not in bpy.ops.render.render(write_still=True):
                raise RuntimeError('Render failed')
        if old.snapshot() != baseline_snapshot:
            raise RuntimeError('Opacity diagnostic modified geometry/material binding')
        (OUT / f'{variant}.json').write_text(json.dumps({'changes': changes,
            'geometry_material_binding_unchanged': True, 'artistic_verdict': 'NOT_RUN'}, indent=2))


def main():
    from movie_factory import production_knowledge as pk
    from trellis301_prepare import sha
    task = json.loads((ROOT / 'results/trellis301/task.json').read_text())
    task.update(id='trellis301-opacity-control', phase='execution')
    for path in (Path(__file__), BASE, ROOT / 'scripts/trellis298_inspect.py'):
        task['inputs'][str(path.relative_to(ROOT))] = sha(path)
    packet = pk.task_packet(ROOT, task)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / 'packet.json').write_text(json.dumps(packet, indent=2))
    if not packet['dispatch_ready']:
        raise RuntimeError(packet['blockers'])
    # Do not overlap any Blender native worker. No process is killed here.
    active = subprocess.run(['pgrep', '-fl', '/Applications/Blender.app/Contents/MacOS/Blender'], capture_output=True, text=True)
    if active.returncode == 0:
        raise RuntimeError('Blender slot occupied; coordinate rather than run in parallel')
    job = {'operation': 'opacity-control'}
    validate(job)
    env = {k: os.environ[k] for k in ('PATH', 'HOME', 'TMPDIR', 'LANG', 'LC_ALL') if k in os.environ}
    with (OUT / 'render.log').open('w') as log:
        result = subprocess.run(['/Applications/Blender.app/Contents/MacOS/Blender', '--background', '--offline-mode',
            '--factory-startup', '--disable-autoexec', '--python-exit-code', '7', '--python', str(Path(__file__).resolve()),
            '--', json.dumps(job)], env=env, stdout=log, stderr=subprocess.STDOUT)
    if result.returncode:
        raise RuntimeError(f'Opacity render failed: {result.returncode}')
    comparison_sheets()


def comparison_sheets():
    """Paired full-size evidence per angle, not a dense thumbnail grid."""
    from PIL import Image, ImageDraw, ImageFont
    font = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 20)
    references = []
    for angle in ('front', 'left-quarter', 'right-quarter', 'back'):
        sources = [OUT / f'{variant}-{angle}.png' for variant in ('opaque', 'alpha')]
        images = [Image.open(path).convert('RGB') for path in sources]
        if images[0].size != images[1].size:
            raise RuntimeError('Comparison dimensions differ')
        width, height = images[0].size
        board = Image.new('RGB', (width * 2, height + 40), '#eeeeee')
        draw = ImageDraw.Draw(board)
        for i, (label, image) in enumerate(zip(('Original opaque', 'Image alpha enabled'), images)):
            draw.text((i * width + 12, 9), label, fill='#161616', font=font)
            board.paste(image, (i * width, 40))
        target = OUT / f'comparison-{angle}.jpg'
        board.save(target, quality=95)
        references.append({'angle': angle, 'sources': list(map(str, sources)), 'comparison': str(target)})
    (OUT / 'comparisons.json').write_text(json.dumps({'pairs': references,
        'claim': 'Matched render comparison; alpha atlas statistics alone do not establish beard improvement'}, indent=2))


if __name__ == '__main__':
    if '--' in sys.argv:
        worker(json.loads(sys.argv[sys.argv.index('--') + 1]))
    else:
        main()
