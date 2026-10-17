"""Fixed, hash-bound synthetic GLB inspection, not production asset execution."""
import hashlib,json,os,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'.runtime/trellis294/retrieved/evidence/probe'
OUT=ROOT/'.runtime/trellis294/blender'
RECORD=ROOT/'results/trellis294'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def validate(job):
    if set(job)!={'operation','fixture'} or job['operation'] not in {'inspect','reopen'} or job['fixture'] not in {'uv-control','cube'}:raise ValueError('Unknown structured operation')
def snapshot(fixture):
    import bpy
    meshes=[o for o in bpy.context.scene.objects if o.type=='MESH'];assert len(meshes)==1
    obj=meshes[0];coords=sorted([[round(v,6) for v in obj.matrix_world@p.co] for p in obj.data.vertices])
    if fixture=='uv-control':assert coords==sorted([[0,0,.2],[1,0,.5],[1,1,.6],[0,1,.3]])
    else:
        for axis in range(3):
            assert abs(min(p[axis] for p in coords)+.25)<.01 and abs(max(p[axis] for p in coords)-.25)<.01
    mat=obj.active_material;assert mat and mat.use_nodes
    bs=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
    assert all(bs.inputs[k].is_linked for k in ('Base Color','Metallic','Roughness'))
    assert obj.data.uv_layers.active and len(obj.data.uv_layers.active.data)==len(obj.data.loops)
    return {'vertices':coords,'faces':len(obj.data.polygons),'uv':[[round(v,6) for v in d.uv] for d in obj.data.uv_layers.active.data],
        'images':sorted([{'name':i.name,'size':list(i.size),'colorspace':i.colorspace_settings.name} for i in bpy.data.images if i.source=='FILE'],key=lambda x:x['name']),
        'pbr_links':True}
def worker(job):
    import bpy
    validate(job);name=job['fixture'];op=job['operation'];source=SOURCE/(name+'.glb')
    receipt=json.loads((SOURCE/'receipt.json').read_text());assert sha(source)==receipt['outputs'][source.name]
    if op=='reopen':
        bpy.ops.wm.open_mainfile(filepath=str(OUT/(name+'.blend')))
        actual=snapshot(name);assert actual==json.loads((OUT/(name+'-inspect.json')).read_text())
        (OUT/(name+'-reopen.json')).write_text(json.dumps({'matches':True,'snapshot':actual},indent=2));return
    bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
    bpy.ops.import_scene.gltf(filepath=str(source));actual=snapshot(name)
    (OUT/(name+'-inspect.json')).write_text(json.dumps(actual,indent=2));bpy.ops.file.pack_all()
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT/(name+'.blend')))
    if name!='uv-control':return
    obj=next(o for o in bpy.context.scene.objects if o.type=='MESH');mat=obj.active_material
    bs=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED');source=bs.inputs['Base Color'].links[0].from_socket
    output=next(n for n in mat.node_tree.nodes if n.type=='OUTPUT_MATERIAL');em=mat.node_tree.nodes.new('ShaderNodeEmission')
    mat.node_tree.links.new(source,em.inputs['Color']);mat.node_tree.links.new(em.outputs[0],output.inputs['Surface'])
    cam=bpy.data.objects.new('UV proof',bpy.data.cameras.new('UV proof'));bpy.context.collection.objects.link(cam)
    cam.location=(.5,.5,4);cam.data.type='ORTHO';cam.data.ortho_scale=1.2
    scene=bpy.context.scene;scene.camera=cam;scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=1
    scene.render.resolution_x=384;scene.render.resolution_y=384;scene.render.resolution_percentage=100
    scene.view_settings.view_transform='Standard';scene.view_settings.look='None';scene.view_settings.exposure=0;scene.view_settings.gamma=1
    scene.render.image_settings.file_format='PNG';scene.render.filepath=str(OUT/'uv-diagnostic.png');bpy.ops.render.render(write_still=True)
def main():
    OUT.mkdir(parents=True,exist_ok=True)
    import trellis294_cloud as c
    c.configure();packet=c.packet()
    task=json.loads((RECORD/'task.json').read_text());task['inputs'][str(Path(__file__).relative_to(ROOT))]=sha(Path(__file__))
    for p in SOURCE.glob('*'):
        if p.is_file():task['inputs'][str(p.relative_to(ROOT))]=sha(p)
    from movie_factory import production_knowledge as pk
    packet=pk.task_packet(ROOT,task);assert packet['dispatch_ready']
    (RECORD/'blender-packet.json').write_text(json.dumps(packet,indent=2))
    env={k:os.environ[k] for k in ('PATH','HOME','TMPDIR','LANG','LC_ALL') if k in os.environ}
    timings=[]
    for name in ('uv-control','cube'):
        for op in ('inspect','reopen'):
            start=time.monotonic()
            with (OUT/(name+'-'+op+'.log')).open('w') as log:
                result=subprocess.run(['/Applications/Blender.app/Contents/MacOS/Blender','--background','--offline-mode','--factory-startup','--disable-autoexec','--python-exit-code','7','--python',str(Path(__file__).resolve()),'--',json.dumps({'operation':op,'fixture':name})],env=env,stdout=log,stderr=subprocess.STDOUT)
            timings.append({'fixture':name,'operation':op,'seconds':time.monotonic()-start,'returncode':result.returncode});assert result.returncode==0
    from PIL import Image
    im=Image.open(OUT/'uv-diagnostic.png');expected={(112,112):(0,255,51),(272,112):(255,255,51),(112,272):(0,0,51),(272,272):(255,0,51)}
    observed={str(p):im.getpixel(p)[:3] for p in expected}
    assert all(max(abs(a-b) for a,b in zip(observed[str(p)],rgb))<=1 for p,rgb in expected.items())
    (RECORD/'blender-verification.json').write_text(json.dumps({'jobs':timings,'uv_expected':{str(k):v for k,v in expected.items()},'uv_observed':observed,'scope':'Synthetic geometry, UV orientation, PBR links and fresh-process reopen only','artifacts':{str(p.relative_to(ROOT)):sha(p) for p in OUT.glob('*') if p.is_file()}},indent=2))
if __name__=='__main__':
    if '--' in sys.argv:
        args=sys.argv[sys.argv.index('--')+1:];assert len(args)==1;worker(json.loads(args[0]))
    else:main()
