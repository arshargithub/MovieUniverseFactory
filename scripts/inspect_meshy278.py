"""Fixed offline data-only GLB inspection. No provider code or arbitrary paths."""
import hashlib
import json
import math
import os
from pathlib import Path
import struct
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT/'.runtime/assets/series01-sikh278-meshy/original.glb'
EXPECTED = '58131039f2b34d17c6c5c97a1bf52d7a405ef13ef41ca9cd9404e0d5fde14d97'
OUT = ROOT/'.runtime/art-direction/series01-sikh278/native-inspection02'

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def validate(job):
    if not isinstance(job, dict) or set(job) != {'operation'} or job['operation'] not in ('inspect', 'reopen'):
        raise ValueError('Only fixed inspect/reopen operations permitted')
    return job['operation']

def glb_json(data):
    if len(data) < 20:
        raise ValueError('Truncated GLB')
    magic, version, total = struct.unpack_from('<4sII', data)
    size, kind = struct.unpack_from('<II', data, 12)
    if magic != b'glTF' or version != 2 or total != len(data) or kind != 0x4e4f534a or 20+size > len(data):
        raise ValueError('Invalid GLB envelope')
    doc = json.loads(data[20:20+size])
    for group in ('buffers', 'images'):
        for item in doc.get(group, []):
            if 'uri' in item:
                raise ValueError('External or URI resources prohibited in fixed inspection')
    return doc

def geometry_record(objects):
    import numpy as np
    records = []
    for ob in sorted(objects, key=lambda o:o.name):
        if ob.type != 'MESH':
            continue
        me=ob.data
        coords=np.empty(len(me.vertices)*3,dtype=np.float32);me.vertices.foreach_get('co',coords)
        loops=np.empty(len(me.loops),dtype=np.int32);me.loops.foreach_get('vertex_index',loops)
        parents=list(range(len(me.vertices)))
        def root(i):
            while parents[i]!=i:
                parents[i]=parents[parents[i]];i=parents[i]
            return i
        for edge in me.edges:
            a,b=map(int,edge.vertices);a=root(a);b=root(b)
            if a!=b:parents[b]=a
        counts={}
        for i in range(len(parents)):
            r=root(i);counts[r]=counts.get(r,0)+1
        records.append(dict(name=ob.name,vertices=len(me.vertices),faces=len(me.polygons),
            polygon_sizes=sorted(set(len(p.vertices) for p in me.polygons)),
            connected_component_vertex_counts=sorted(counts.values(),reverse=True),
            coordinate_sha256=hashlib.sha256(coords.tobytes()).hexdigest(),
            loop_sha256=hashlib.sha256(loops.tobytes()).hexdigest(),
            uv_layers=len(me.uv_layers),shape_keys=len(me.shape_keys.key_blocks) if me.shape_keys else 0,
            vertex_groups=len(ob.vertex_groups),modifiers=[m.type for m in ob.modifiers],
            materials=[m.name if m else None for m in me.materials],
            world_matrix=[list(row) for row in ob.matrix_world]))
    return records

def run(job):
    import bpy
    from mathutils import Vector
    op=validate(job)
    if sha(RAW)!=EXPECTED:raise ValueError('Downloaded source changed')
    doc=glb_json(RAW.read_bytes())
    if op=='reopen':
        saved=json.loads((OUT/'inspection.json').read_text())
        if sha(OUT/'study.blend')!=saved['native_sha256']:raise ValueError('Native changed')
        bpy.ops.wm.open_mainfile(filepath=str(OUT/'study.blend'))
        actual=geometry_record(bpy.data.objects)
        passed=actual==saved['normalized_geometry']
        (OUT/'reopen.json').write_text(json.dumps({'passed':passed,'native_sha256':saved['native_sha256'],
            'geometry_exact':passed,'autoexec_disabled':True},indent=2))
        if not passed:raise ValueError('Reopen geometry mismatch')
        return
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(RAW))
    raw_records=geometry_record(bpy.data.objects)
    meshes=[o for o in bpy.data.objects if o.type=='MESH']
    if not meshes:raise ValueError('No mesh')
    points=[o.matrix_world@Vector(c) for o in meshes for c in o.bound_box]
    lo=Vector(tuple(min(p[i] for p in points) for i in range(3)))
    hi=Vector(tuple(max(p[i] for p in points) for i in range(3)))
    scale=1/(hi.z-lo.z);center=(lo+hi)/2
    # Normalize only rigid presentation transforms, not the recovered vertices.
    from mathutils import Matrix
    transform=Matrix.Scale(scale,4)@Matrix.Translation(-center)
    for ob in meshes:
        ob.matrix_world=transform@ob.matrix_world
    clay=bpy.data.materials.new('Neutral diagnostic clay');clay.diffuse_color=(.25,.25,.25,1)
    clay.use_nodes=True;bs=clay.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value=(.25,.25,.25,1);bs.inputs['Roughness'].default_value=.78
    for ob in meshes:
        ob.data.materials.clear();ob.data.materials.append(clay)
    scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=20
    scene.cycles.use_denoising=True;scene.render.resolution_x=640;scene.render.resolution_y=760
    scene.render.resolution_percentage=100;scene.render.image_settings.file_format='PNG'
    scene.world=bpy.data.worlds.new('Diagnostic world');scene.world.use_nodes=True
    scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.22,.22,.22,1)
    scene.world.node_tree.nodes['Background'].inputs[1].default_value=.15
    def aim(ob,p,t=(0,0,0)):
        ob.location=p;ob.rotation_euler=(Vector(t)-ob.location).to_track_quat('-Z','Y').to_euler()
    camdata=bpy.data.cameras.new('Inspection camera');cam=bpy.data.objects.new('Inspection camera',camdata)
    scene.collection.objects.link(cam);scene.camera=cam;camdata.type='ORTHO';camdata.ortho_scale=1.28
    lights=[]
    for name,energy,size in [('Key',50,1.25),('Fill',8,2)]:
        data=bpy.data.lights.new(name,'AREA');data.energy=energy;data.shape='DISK';data.size=size
        light=bpy.data.objects.new(name,data);scene.collection.objects.link(light);lights.append(light)
    views=[('front',(0,-3,.05)),('right-quarter',(2,-3,.08)),('left-quarter',(-2,-3,.08)),
        ('profile',(3,0,.05)),('rear',(0,3,.08)),('crown',(1,-1,3))]
    # Source has a fixed head turn. Register views approximately to facial
    # forward direction, not torso forward. Never call torso-front face-front.
    yaw=math.atan2(2,3)
    for name,pos in views:
        pos=Vector((pos[0]*math.cos(yaw)-pos[1]*math.sin(yaw),
                    pos[0]*math.sin(yaw)+pos[1]*math.cos(yaw),pos[2]))
        aim(cam,pos)
        # Camera-relative lighting removes left/right light bias in comparisons.
        q=cam.rotation_euler.to_quaternion()
        aim(lights[0],Vector(pos)*.35+q@Vector((-1.1,.9,0)))
        aim(lights[1],Vector(pos)*.4+q@Vector((1,-.15,0)))
        scene.render.filepath=str(OUT/(name+'.png'));bpy.ops.render.render(write_still=True)
    aim(cam,(0,-3,.05))
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'study.blend'))
    report=dict(source_sha256=EXPECTED,source_bytes=RAW.stat().st_size,
        gltf_summary={k:len(doc.get(k,[])) for k in ('meshes','nodes','materials','images','skins','animations')},
        imported_geometry=raw_records,normalized_geometry=geometry_record(bpy.data.objects),
        input_bounds=[list(lo),list(hi)],presentation_scale=scale,native_sha256=sha(OUT/'study.blend'),
        views=[v[0] for v in views],limits=['Static data inspection only','No rig or performance qualification',
        'Generic disposable identity','No texture or sculpt edits; rigid normalization only'])
    (OUT/'inspection.json').write_text(json.dumps(report,indent=2))

def launch(job):
    op=validate(job);glb_json(RAW.read_bytes())
    if sha(RAW)!=EXPECTED:raise ValueError('Source hash mismatch')
    OUT.mkdir(parents=True,exist_ok=True)
    log=OUT/(op+'.log')
    if log.exists():raise ValueError('Preserve previous run')
    sys.path.insert(0,str(ROOT/'src'))
    from movie_factory import production_knowledge as pk
    task=json.loads((ROOT/'results/sikh278/task-native.json').read_text())
    packet=pk.task_packet(ROOT,task)
    if not packet['dispatch_ready']:raise ValueError(packet['blockers'])
    (OUT/(op+'-packet.json')).write_text(json.dumps(packet,indent=2))
    env={k:os.environ[k] for k in ('PATH','HOME','TMPDIR','LANG','LC_ALL') if k in os.environ}
    start=time.monotonic()
    with log.open('w') as handle:
        result=subprocess.run(['/Applications/Blender.app/Contents/MacOS/Blender','--background',
            '--offline-mode','--factory-startup','--disable-autoexec','--python-exit-code','7',
            '--python',str(Path(__file__).resolve()),'--',json.dumps(job)],env=env,stdout=handle,stderr=subprocess.STDOUT)
    (OUT/(op+'-receipt.json')).write_text(json.dumps({'seconds':time.monotonic()-start,
        'returncode':result.returncode,'packet_digest':packet['packet_digest']},indent=2))
    if result.returncode:raise RuntimeError(str(log))
    print(OUT)

if __name__=='__main__':
    if '--' in sys.argv:
        args=sys.argv[sys.argv.index('--')+1:]
        if len(args)!=1:raise ValueError('One structured operation')
        run(json.loads(args[0]))
    else:
        if len(sys.argv)!=2:raise ValueError('inspect or reopen required')
        launch({'operation':sys.argv[1]})
