"""Hash-bound structured Blender source assessment, never an actor PASS."""
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / '.runtime/art-direction/series01-trellis298'
SOURCE = ROOT / '.runtime/trellis298c/retrieved/evidence'


def source_path(candidate):
    if candidate == 'head512-remeshed':
        return ROOT / '.runtime/trellis298d/retrieved/evidence/candidate.glb'
    return SOURCE / candidate / 'candidate.glb'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(job):
    if set(job) != {'operation', 'candidate'} or job['operation'] not in ('inspect', 'reopen') or job['candidate'] not in ('head512', 'head1024', 'head512-remeshed'):
        raise ValueError('Unknown structured operation')


def dump(path, data):
    path.write_text(json.dumps(data, indent=2))


def snapshot():
    import bpy
    import numpy as np
    result = {}
    for obj in bpy.data.objects:
        if obj.type != 'MESH':
            continue
        values = np.empty(len(obj.data.vertices)*3, dtype=np.float32)
        obj.data.vertices.foreach_get('co', values)
        assert np.isfinite(values).all()
        result[obj.name] = {'vertices': len(obj.data.vertices), 'faces': len(obj.data.polygons),
            'geometry_sha256': hashlib.sha256(values.tobytes()).hexdigest(), 'matrix': [list(r) for r in obj.matrix_world],
            'uv_layers': len(obj.data.uv_layers), 'materials': [m.name for m in obj.data.materials],
            'shape_keys': len(obj.data.shape_keys.key_blocks) if obj.data.shape_keys else 0}
    return result


def aim(obj, position, target):
    from mathutils import Vector
    obj.location = position
    obj.rotation_euler = (Vector(target)-obj.location).to_track_quat('-Z', 'Y').to_euler()


def worker(job):
    import bpy
    from mathutils import Vector
    validate(job)
    assert not bpy.app.online_access
    folder = OUT / job['candidate']
    folder.mkdir(parents=True, exist_ok=True)
    source = source_path(job['candidate'])
    receipt = json.loads((source.parent / 'receipt.json').read_text())
    assert sha(source) == receipt['glb_sha256']
    if job['operation'] == 'reopen':
        bpy.ops.wm.open_mainfile(filepath=str(folder / 'source.blend'))
        expected = json.loads((folder / 'inspection.json').read_text())['geometry']
        actual = snapshot()
        dump(folder / 'reopen.json', {'exact_geometry_material_binding': expected == actual, 'production_ready': False})
        assert expected == actual
        return
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    bpy.ops.import_scene.gltf(filepath=str(source))
    objects = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    assert objects
    bounds = [o.matrix_world @ Vector(v) for o in objects for v in o.bound_box]
    low = Vector([min(v[k] for v in bounds) for k in range(3)])
    high = Vector([max(v[k] for v in bounds) for k in range(3)])
    center = (low + high)*.5
    factor = .62 / (high.z-low.z)
    root = bpy.data.objects.new('Source normalization', None)
    bpy.context.collection.objects.link(root)
    for obj in objects:
        matrix = obj.matrix_world.copy()
        obj.parent = root
        obj.matrix_world = matrix
        for polygon in obj.data.polygons:
            polygon.use_smooth = True
    root.scale = (factor,)*3
    root.location = -center*factor
    bpy.context.view_layer.update()
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'CPU'
    scene.cycles.samples = 12
    scene.cycles.use_denoising = True
    scene.render.resolution_x = 480
    scene.render.resolution_y = 600
    scene.render.resolution_percentage = 100
    scene.view_settings.view_transform = 'AgX'
    scene.world.use_nodes = True
    scene.world.node_tree.nodes['Background'].inputs[0].default_value = (.18,.18,.18,1)
    scene.world.node_tree.nodes['Background'].inputs[1].default_value = .5
    cam = bpy.data.objects.new('Neutral assessment camera', bpy.data.cameras.new('Assessment'))
    bpy.context.collection.objects.link(cam)
    cam.data.type = 'ORTHO'
    cam.data.ortho_scale = .78
    scene.camera = cam
    for name, pos, energy, size in [('Key',(-1,-2,2),130,2),('Fill',(2,-1,.5),70,2),('Rim',(0,2,1.5),100,1.5)]:
        light = bpy.data.objects.new(name, bpy.data.lights.new(name,'AREA'))
        bpy.context.collection.objects.link(light)
        light.data.energy = energy
        light.data.shape = 'DISK'
        light.data.size = size
        aim(light,pos,(0,0,0))
    views = [('front',0),('left-quarter',45),('left-profile',90),('rear-left',135),
             ('back',180),('rear-right',225),('right-profile',270),('right-quarter',315)]
    for name, degrees in views:
        a = math.radians(degrees)
        aim(cam,(2.5*math.sin(a),-2.5*math.cos(a),.04),(0,0,0))
        scene.render.filepath = str(folder / (name+'.png'))
        result = bpy.ops.render.render(write_still=True)
        assert 'FINISHED' in result and Path(scene.render.filepath).is_file()
    clay = bpy.data.materials.new('Shape diagnostic only')
    clay.use_nodes=True
    clay.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.36,.36,.36,1)
    clay.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.8
    bpy.context.view_layer.material_override=clay
    for name,degrees in (views[0],views[1],views[-1]):
        a=math.radians(degrees)
        aim(cam,(2.5*math.sin(a),-2.5*math.cos(a),.04),(0,0,0))
        scene.render.filepath=str(folder/(name+'-clay.png'))
        assert 'FINISHED' in bpy.ops.render.render(write_still=True)
    bpy.context.view_layer.material_override=None
    aim(cam,(0,-2.5,.04),(0,0,0))
    bpy.ops.file.pack_all()
    dump(folder/'inspection.json', {'source_sha256':sha(source),'source_bounds':[list(low),list(high)],
         'normalized_height_m':.62,'geometry':snapshot(),'production_ready':False,
         'scope':'Static inferred source; no eye separation, rig, garment topology or motion is implied'})
    bpy.ops.wm.save_as_mainfile(filepath=str(folder/'source.blend'))


def main(candidate, packet_only=False):
    from movie_factory import production_knowledge as pk
    task=json.loads((ROOT/'results/trellis298/task.json').read_text())
    task.update(id='trellis298-inspect-'+candidate,phase='execution')
    # Current strategy was reread after the export-only representation reassessment.
    for path in (Path(__file__),ROOT/'results/trellis298/STRATEGY.md',source_path(candidate),source_path(candidate).parent/'receipt.json',
                 ROOT/'.runtime/art-direction/series01-sikh257/sikh-uncovered-concept-v03.png',
                 ROOT/'.runtime/art-direction/series01-entrances-v04/C-illustrated-landscape.png',
                 ROOT/'.runtime/art-direction/series01-facebuilder-trial-01/natural152-preview-16/front.png',
                 ROOT/'.runtime/art-direction/series01-sikh271-audit/accepted-pashtun-7s5.png'):
        task['inputs'][str(path.relative_to(ROOT))]=sha(path)
    packet=pk.task_packet(ROOT,task)
    dump(ROOT/'results/trellis298'/('blender-'+candidate+'-packet.json'),packet)
    assert packet['dispatch_ready'],packet['blockers']
    if packet_only:
        print(pk.packet_markdown(packet))
        return
    folder=OUT/candidate
    folder.mkdir(parents=True,exist_ok=True)
    env={k:os.environ[k] for k in ('PATH','HOME','TMPDIR','LANG','LC_ALL') if k in os.environ}
    for op in ('inspect','reopen'):
        job={'operation':op,'candidate':candidate}
        validate(job)
        start=time.monotonic()
        with (folder/(op+'.log')).open('w') as log:
            result=subprocess.run(['/Applications/Blender.app/Contents/MacOS/Blender','--background','--offline-mode',
                 '--factory-startup','--disable-autoexec','--python-exit-code','7','--python',str(Path(__file__).resolve()),
                 '--',json.dumps(job)],env=env,stdout=log,stderr=subprocess.STDOUT)
        dump(folder/(op+'-job.json'),{'returncode':result.returncode,'seconds':time.monotonic()-start})
        assert result.returncode==0


if __name__=='__main__':
    if '--' in sys.argv:
        worker(json.loads(sys.argv[sys.argv.index('--')+1]))
    else:
        import argparse
        parser=argparse.ArgumentParser()
        parser.add_argument('candidate',choices=['head512','head1024','head512-remeshed'])
        parser.add_argument('--packet-only',action='store_true')
        args=parser.parse_args()
        main(args.candidate,args.packet_only)
