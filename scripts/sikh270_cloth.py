"""Fixed gravity/contact control and portable packaging for Sikh270.

Not an actor-driven reveal. Source08 and failed cloth10 are immutable.
"""
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import time
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'));sys.path.insert(0,str(ROOT/'src'))
from sikh270_guides import sha,EYE
BASE=ROOT/'.runtime/art-direction/series01-sikh270'
FIT=12
ASSEMBLY=13

def validate(job):
    if not isinstance(job,dict) or set(job)!={'operation'} or job['operation'] not in {'fit','assemble','reopen'}:raise ValueError('Fixed fit/assemble/reopen only')
    return BASE/f"candidate-{FIT if job['operation']=='fit' else ASSEMBLY:02d}"

def packet(job):
    from movie_factory import production_knowledge as pk
    p=json.loads((ROOT/'.runtime/knowledge-pilot213/sikh270-look-08.json').read_text());task=p['task']
    task['id']=f'sikh270-cloth{FIT}-'+job['operation'];task['intent']='Recompute fixed-body face-end gravity/contact with compressed moustache and clean initial surface, then package native character candidate. No real hand reveal or full-sequence qualification.'
    files=list(task['inputs'])+['scripts/sikh270_cloth.py',str((BASE/'candidate-08/character.blend').relative_to(ROOT)),str((BASE/'candidate-08/build.json').relative_to(ROOT))]
    if job['operation'] in {'assemble','reopen'}:files.extend(str((BASE/f'candidate-{FIT:02d}'/f).relative_to(ROOT)) for f in ('cloth.json','cloth-motion.npz','groom-compression.json'))
    if job['operation']=='reopen':files.append(str((BASE/f'candidate-{ASSEMBLY:02d}/character.blend').relative_to(ROOT)))
    task['inputs']={f:sha(ROOT/f) for f in files};result=pk.task_packet(ROOT,task)
    dest=ROOT/'.runtime/knowledge-pilot213'/task['id'];dest.with_suffix('.json').write_text(json.dumps(result,indent=2));dest.with_suffix('.md').write_text(pk.packet_markdown(result))
    if not result['dispatch_ready']:raise ValueError(result['blockers'])
    return result,dest

def launch(job,prepare=False):
    out=validate(job);proof,p=packet(job)
    if prepare:print(p.with_suffix('.md'));return
    out.mkdir(parents=True,exist_ok=True);log=out/(job['operation']+'.log')
    if log.exists():raise ValueError('Preserve previous dispatch')
    (out/(job['operation']+'-source.py')).write_bytes(Path(__file__).read_bytes())
    env={k:os.environ[k] for k in ('PATH','HOME','TMPDIR','LANG','LC_ALL') if k in os.environ};env['CYCLES_METAL_DISABLE_BINARY_ARCHIVES']='1';start=time.time()
    with log.open('w') as f:
        p=subprocess.run(['/Applications/Blender.app/Contents/MacOS/Blender','--background','--offline-mode','--disable-autoexec','--python-exit-code','7','--python',str(Path(__file__).resolve()),'--',json.dumps(job)],env=env,stdout=f,stderr=subprocess.STDOUT)
    (out/(job['operation']+'-receipt.json')).write_text(json.dumps(dict(returncode=p.returncode,seconds=time.time()-start,packet_digest=proof['packet_digest'],inputs=proof['task']['inputs']),indent=2))
    if p.returncode:raise RuntimeError(str(log))
    print(out)

def native(job):
    import bpy
    from mathutils import Vector
    from sikh257_native import mesh,camera_at
    import sikh269_character as previous
    out=validate(job);source=BASE/'candidate-08';rec=json.loads((source/'build.json').read_text())
    if bpy.app.online_access or sha(source/'character.blend')!=rec['native_sha256']:raise ValueError('Source/offline check failed')
    if job['operation']=='reopen':
        import numpy as np
        record=json.loads((out/'build.json').read_text());nativepath=out/'character.blend'
        if sha(nativepath)!=record['native_sha256']:raise ValueError('Saved native changed')
        bpy.ops.wm.open_mainfile(filepath=str(nativepath));scene=bpy.context.scene
        ob=bpy.data.objects['Sikh270 own free end | embedded gravity control'];points=np.load(BASE/f'candidate-{FIT:02d}/cloth-motion.npz')['vertices'];errors={}
        for f in (1,16,34,54,72,96):
            scene.frame_set(f);bpy.context.view_layer.update();ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get())
            actual=np.asarray([list(v.co) for v in ev.data.vertices]);errors[str(f)]=float(np.max(np.abs(actual-points[f-1])))
            if errors[str(f)]>1e-6:raise ValueError('Embedded cache differs')
        scene.frame_set(16);scene.render.filepath=str(out/'reopen-covered.png');bpy.ops.render.render(write_still=True)
        scene.frame_set(96);ob.hide_render=True;scene.render.filepath=str(out/'reopen.png');bpy.ops.render.render(write_still=True)
        (out/'reopen.json').write_text(json.dumps(dict(native_sha256=sha(nativepath),inventory_matches=sorted(o.name for o in bpy.data.objects)==record['objects'],embedded_cloth_errors_m=errors,limits='Sampled geometry replay, not a new solver run or animation qualification'),indent=2));return
    bpy.ops.wm.open_mainfile(filepath=str(source/'character.blend'));scene=bpy.context.scene
    old=bpy.data.objects.get('Turban free end | evaluated gravity control')
    if old:bpy.data.objects.remove(old,do_unlink=True)
    if job['operation']=='fit':
        from mathutils.bvhtree import BVHTree
        import bmesh
        body=bpy.data.objects['Sikh269 coherent editable anatomy'];surface=BVHTree.FromObject(body,bpy.context.evaluated_depsgraph_get())
        compression={};hull=bmesh.new()
        for hair in bpy.data.objects:
            if not hair.name.startswith('Sikh270 regional beard'):continue
            compressed=[]
            for spline in hair.data.splines:
                root=Vector(spline.points[0].co[:3]);moustache=abs(root.x)<.034 and root.z>EYE-.067
                for i,p in enumerate(spline.points):
                    q=Vector(p.co[:3])
                    if moustache:
                        hit=surface.ray_cast(Vector((q.x,-.5,q.z)),Vector((0,1,0)),1)[0]
                        if hit is not None:q.y=max(q.y,hit.y-.003)
                        p.co=(*q,1)
                    compressed.append(list(q))
                    if i%4==0 or i==len(spline.points)-1:hull.verts.new(q)
            compression[hair.name]=compressed
        (out/'groom-compression.json').write_text(json.dumps(compression))
        bmesh.ops.convex_hull(hull,input=list(hull.verts),use_existing_faces=False)
        bmesh.ops.delete(hull,geom=[v for v in hull.verts if not v.link_faces],context='VERTS')
        bmesh.ops.recalc_face_normals(hull,faces=list(hull.faces));groom=BVHTree.FromBMesh(hull);hull.free()
        original=previous.cover_control
        def widened(eye):
            ob,info=original(eye);basis=ob.data.shape_keys.key_blocks[0]
            for row in range(101):
                u=row/100;center=basis.data[row*21+10].co.copy();spread=1+.38*math.sin(math.pi*u)
                for col in range(21):
                    v=basis.data[row*21+col];v.co.z=center.z+(v.co.z-center.z)*spread-.018*math.sin(math.pi*u)
                    if v.co.y<-.075:
                        for collision in (surface,groom):
                            hit=collision.ray_cast(Vector((v.co.x,-.5,v.co.z)),Vector((0,1,0)),1)[0]
                            if hit is not None:v.co.y=min(v.co.y,hit.y-.005)
            centers=[basis.data[i*21+10].co.copy() for i in range(101)]
            info['covered_centerline_length']=sum((b-a).length for a,b in zip(centers,centers[1:]));info['released_centerline_length']=None
            info['scope']='Widened dressed initial surface and actual270 groom contact; released authored key unused; no verified textile cutting pattern'
            return ob,info
        previous.cover_control=widened
        for ob in bpy.data.objects:
            if ob.name.startswith('Sikh270 regional beard'):ob.name='Rooted beard270 '+ob.name.rsplit(' ',1)[-1]
        scene.camera.data.ortho_scale=.56
        previous.cloth_study(out,EYE);return
    import numpy as np
    clothdir=BASE/f'candidate-{FIT:02d}';info=json.loads((clothdir/'cloth.json').read_text());points=np.load(clothdir/'cloth-motion.npz')['vertices']
    compressed=json.loads((clothdir/'groom-compression.json').read_text())
    for name,coords in compressed.items():
        hair=bpy.data.objects[name];hair.shape_key_add(name='Open groom');key=hair.shape_key_add(name='Compressed under face cloth',from_mix=False);key.value=0
        if len(key.data)!=len(coords):raise ValueError('Groom topology differs')
        for v,p in zip(key.data,coords):v.co=p
        for f,value in ((1,1),(16,1),(34,.2),(54,0),(96,0)):key.value=value;key.keyframe_insert('value',frame=f)
        key.value=0
    ob=mesh('Sikh270 own free end | embedded gravity control',points[0].tolist(),info['polygons'],previous.cloth_material())
    ob.shape_key_add(name='Basis')
    for frame,verts in enumerate(points,1):
        key=ob.shape_key_add(name=f'Gravity frame {frame:03d}',from_mix=False);key.value=0
        for v,p in zip(key.data,verts):v.co=p
        for f,value in ((max(0,frame-1),0),(frame,1),(frame+1,0)):key.value=value;key.keyframe_insert('value',frame=f)
        key.value=0
    if ob.data.shape_keys.animation_data:
        action=ob.data.shape_keys.animation_data.action
        for layer in action.layers:
            for strip in layer.strips:
                for bag in strip.channelbags:
                    for fc in bag.fcurves:
                        for k in fc.keyframe_points:k.interpolation='LINEAR'
    scene.frame_start=1;scene.frame_end=96;scene.cycles.samples=32;scene.render.resolution_x=720;scene.render.resolution_y=900
    cam=scene.camera;cam.data.ortho_scale=.54;target=Vector((0,-.025,EYE-.017));scene.frame_set(96);ob.hide_render=True
    for name,pos in [('front',(0,-3,EYE)),('three-quarter',(1.7,-3,EYE+.03)),('opposite',(-1.7,-3,EYE+.03)),('profile',(3,0,EYE)),('rear',(0,3,EYE+.10)),('crown',(1,-1,EYE+2))]:
        camera_at(cam,pos,target);scene.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True)
    ob.hide_render=False;scene.frame_set(16)
    for name,pos in [('covered-front',(0,-3,EYE)),('covered-quarter',(1.7,-3,EYE+.03))]:
        camera_at(cam,pos,target);scene.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True)
    scene.frame_set(96);camera_at(cam,(1.7,-3,EYE+.03),target);scene.render.filepath=str(out/'released-quarter.png');bpy.ops.render.render(write_still=True)
    ob.hide_render=True;rig=bpy.data.objects['Sikh269 coherent editable anatomy.rig'];head=rig.pose.bones['head'];head.rotation_mode='XYZ';head.rotation_euler=(.20944,0,-.20944);bpy.context.view_layer.update()
    scene.render.filepath=str(out/'head-attachment.png');bpy.ops.render.render(write_still=True)
    head.rotation_euler=(0,0,0);bpy.context.view_layer.update();camera_at(cam,(0,-3,EYE),target);scene.render.filepath=str(out/'reopen.png')
    bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(out/'character.blend'))
    (out/'build.json').write_text(json.dumps(dict(native_sha256=sha(out/'character.blend'),source_native_sha256=rec['native_sha256'],cloth_sha256=sha(clothdir/'cloth-motion.npz'),objects=sorted(o.name for o in bpy.data.objects),status='INTERNAL_UNREVIEWED',limits=['Static identity candidate','Fixed-body cloth control, no real crossed hand or bike','Head attachment control is not coordinated acting']),indent=2))

if __name__=='__main__':
    if '--' in sys.argv:
        args=sys.argv[sys.argv.index('--')+1:]
        if len(args)!=1:raise ValueError('One structured operation')
        job=json.loads(args[0]);validate(job);native(job)
    else:
        if len(sys.argv) not in (2,3) or (len(sys.argv)==3 and sys.argv[2]!='--prepare'):raise ValueError('operation [--prepare]')
        job={'operation':sys.argv[1]};validate(job)
        if len(sys.argv)==3:launch(job,True)
        else:
            import fcntl
            with (BASE/'worker.lock').open('a') as lock:
                fcntl.flock(lock,fcntl.LOCK_EX);launch(job)
