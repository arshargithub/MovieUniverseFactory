"""Fixed offline generic donor conversion controls; never executes asset code."""
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'));sys.path.insert(0,str(ROOT/'src'))
BASE=ROOT/'.runtime/art-direction/series01-sikh269/candidate-24/character.blend'
BASE_SHA='13353e4e11cc1c31ae45341ede0e38d9dc6d5f8f157d4578dff35f4ccb5b81d7'
RAW=ROOT/'.runtime/assets/series01-sikh278-meshy/original.glb'
RAW_SHA='58131039f2b34d17c6c5c97a1bf52d7a405ef13ef41ca9cd9404e0d5fde14d97'
OUT=ROOT/'.runtime/art-direction/series01-sikh279'
EYE=1.665999174118042

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def validate(j):
    if not isinstance(j,dict) or set(j)!={'operation','attempt'} or j['operation'] not in {'inventory','build','reopen','motion'} or type(j['attempt']) is not int or not 1<=j['attempt']<=30:
        raise ValueError('Fixed operation and integer attempt1..30 only')
    return OUT/f"control-{j['attempt']:02d}"

def packet(j):
    from movie_factory import production_knowledge as pk
    if sha(BASE)!=BASE_SHA or sha(RAW)!=RAW_SHA:raise ValueError('Protected input changed')
    files=[BASE,RAW,Path(__file__),ROOT/'scripts/sikh279_surgery.py',ROOT/'scripts/sikh261_character.py',ROOT/'scripts/sikh257_native.py',ROOT/'tests/test_sikh279_convert.py',ROOT/'docs/planning/SERIES_01_SIKH_ASSET_STRATEGY_262.md',
        ROOT/'docs/knowledge/SIKH_FOUNDATION_REJECTION_271.md',ROOT/'results/sikh278/NATIVE_ASSESSMENT.md',
        ROOT/'.runtime/art-direction/series01-sikh278/generic-study.png',
        ROOT/'.runtime/art-direction/series01-sikh257/sikh-uncovered-concept-v03.png',
        ROOT/'.runtime/art-direction/series01-entrances-v04/C-illustrated-landscape.png',
        ROOT/'.runtime/art-direction/series01-facebuilder-trial-01/natural152-preview-16/front.png',
        ROOT/'.runtime/art-direction/series01-sikh271-audit/accepted-pashtun-7s5.png']
    if j['operation'] in {'reopen','motion'}:files.append(validate(j)/'conversion.blend')
    task=dict(id=f"sikh279-{j['operation']}-{j['attempt']}",operation='modeling',entities=['sikh'],phase='execution',
        query='Generic donor conversion topology facial anatomy blink head motion groom crown cloth contact component proof',
        intent='Director279 local disposable conversion. No hero identity adoption or provider calls. Native utility and motion separate from character acceptance.',
        execution_authority=dict(source='docs/planning/SERIES_01_SIKH_ASSET_STRATEGY_262.md',scope='Exchange279 local generic conversion and motion proof'),
        inputs={str(p.relative_to(ROOT)):sha(p) for p in files},open_decisions=[],max_context_characters=42000)
    p=pk.task_packet(ROOT,task);dest=ROOT/'results/sikh279';dest.mkdir(parents=True,exist_ok=True)
    stem=dest/task['id'];stem.with_suffix('.json').write_text(json.dumps(p,indent=2));stem.with_suffix('.md').write_text(pk.packet_markdown(p))
    if not p['dispatch_ready']:raise ValueError(p['blockers'])
    return p,stem

def run(j):
    import bpy
    from mathutils import Vector,Matrix
    out=validate(j)
    if bpy.app.online_access:raise ValueError('Offline required')
    if sha(BASE)!=BASE_SHA or sha(RAW)!=RAW_SHA:raise ValueError('Input mismatch')
    if j['operation'] in {'reopen','motion'}:
        from sikh279_surgery import sample_scene
        report=json.loads((out/'build.json').read_text())
        if sha(out/'conversion.blend')!=report['native_sha256']:raise ValueError('Native changed')
        bpy.ops.wm.open_mainfile(filepath=str(out/'conversion.blend'))
        actual=sample_scene()
        passed=actual==report['samples']
        (out/'reopen.json').write_text(json.dumps(dict(exact_sample_match=passed,native_sha256=report['native_sha256'],samples=actual),indent=2))
        if not passed:raise ValueError('Fresh reopen samples differ')
        if j['operation']=='motion':
            scene=bpy.context.scene;scene.cycles.samples=8;scene.render.resolution_x=480;scene.render.resolution_y=576
            frames=out/'motion';frames.mkdir(exist_ok=True)
            for f in range(1,97):
                scene.frame_set(f);scene.render.filepath=str(frames/f'{f:04d}.png');bpy.ops.render.render(write_still=True)
        return
    bpy.ops.wm.open_mainfile(filepath=str(BASE));bpy.context.scene.frame_set(1)
    body=bpy.data.objects['Sikh269 coherent editable anatomy'];rig=body.parent
    info=dict(objects=[dict(name=o.name,type=o.type,parent=o.parent.name if o.parent else None) for o in bpy.data.objects],
        modifiers=[dict(name=m.name,type=m.type) for m in body.modifiers],
        shape_keys=[dict(name=k.name,value=k.value) for k in body.data.shape_keys.key_blocks],
        bones={b.name:dict(head=list(rig.matrix_world@b.head_local),tail=list(rig.matrix_world@b.tail_local)) for b in rig.data.bones if any(s in b.name for s in ('head','neck','eye'))})
    for m in body.modifiers:m.show_viewport=False
    bpy.context.view_layer.update();dep=bpy.context.evaluated_depsgraph_get()
    evalob=body.evaluated_get(dep);me=evalob.to_mesh()
    info['face_vertices']=[dict(i=v.index,co=list(body.matrix_world@v.co),groups=[body.vertex_groups[g.group].name for g in body.data.vertices[v.index].groups if g.weight>.5]) for v in me.vertices if v.co.z>1.52]
    evalob.to_mesh_clear()
    (out/'inventory.json').write_text(json.dumps(info,indent=2))
    if j['operation']=='inventory':return
    build(j,body,rig)

def build(j,body,rig):
    import bpy
    import numpy as np
    from mathutils import Vector,Matrix
    from mathutils.bvhtree import BVHTree
    from sikh257_native import material,mesh,camera_at
    from inspect_meshy278 import glb_json,geometry_record
    out=validate(j);scene=bpy.context.scene
    # Bake morph mix, not armature/subdivision. Preserve authored topology and weights.
    dep=bpy.context.evaluated_depsgraph_get();ev=body.evaluated_get(dep)
    coords=[v.co.copy() for v in ev.data.vertices]
    body.shape_key_clear()
    for v,p in zip(body.data.vertices,coords):
        if p.z>EYE-.14:
            # Landmark registration: generated eye-to-mouth interval is shorter
            # than this substrate. Blend back into unchanged neck below the jaw.
            t=max(0,min(1,(p.z-(EYE-.14))/.04))
            if p.z<EYE:p.z=EYE+(p.z-EYE)*(1-.25*t)
        v.co=p
    for m in body.modifiers:m.show_viewport=True
    rig.animation_data_clear()
    for b in rig.pose.bones:b.matrix_basis=Matrix.Identity(4)
    for ob in list(bpy.data.objects):
        if ob.name.startswith(('Rooted beard','Moustache','Natural brow','Harsh Sikh','Turban free')):bpy.data.objects.remove(ob,do_unlink=True)
    glb_json(RAW.read_bytes());before=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(RAW))
    donor=next(o for o in set(bpy.data.objects)-before if o.type=='MESH')
    info=json.loads((ROOT/'.runtime/art-direction/series01-sikh278/native-inspection02/inspection.json').read_text())
    lo,hi=map(Vector,info['input_bounds']);center=(lo+hi)/2
    xform=Matrix.Translation(Vector((-.005,-.020,1.600)))@Matrix.Scale(.42,4)@Matrix.Rotation(-math.atan2(2,3),4,'Z')@Matrix.Scale(info['presentation_scale'],4)@Matrix.Translation(-center)
    points=[xform@donor.matrix_world@v.co for v in donor.data.vertices]
    align=Matrix.Translation(Vector((.013,-.020,0)))@Matrix.Translation(Vector((0,-.10,EYE)))@Matrix.Rotation(-.30,4,'Z')@Matrix.Translation(Vector((0,.10,-EYE)))
    points=[align@p for p in points]
    tris=[tuple(p.vertices) for p in donor.data.polygons]
    surface=BVHTree.FromPolygons(points,tris,all_triangles=True)
    diagnostic=mesh('279 registered source diagnostic',points,tris,material('279 source clay',(.25,.25,.25)))
    oldhide={o.name:o.hide_render for o in bpy.data.objects}
    for o in bpy.data.objects:
        if o.type in {'MESH','CURVE'}:o.hide_render=o!=diagnostic
    scene.cycles.samples=12;scene.render.resolution_x=600;scene.render.resolution_y=720
    cam=scene.camera;cam.data.ortho_scale=.45;camera_at(cam,(0,-3,EYE),(0,-.03,EYE-.005))
    scene.render.filepath=str(out/'registered-source.png');bpy.ops.render.render(write_still=True)
    for o in bpy.data.objects:o.hide_render=oldhide.get(o.name,False)
    bpy.data.objects.remove(diagnostic,do_unlink=True)
    (out/'registration.json').write_text(json.dumps({'rays':[[x,z,list(hit) if (hit:=surface.ray_cast(Vector((x,-.5,z)),Vector((0,1,0)),1)[0]) else None] for z in (1.61,1.63,1.65,1.665,1.68,1.70,1.72,1.74) for x in (-.04,0,.04)]},indent=2))
    if j['attempt']>=6:
        from sikh279_surgery import construct
        construct(j,out,points,tris,surface)
        return
    skin=material('279 neutral anatomy',(.27,.27,.27));body.data.materials.clear();body.data.materials.append(skin)
    # Keep mask and true eye/lip loops; projected fields exclude fused facial hair.
    moved=[]
    for v in body.data.vertices:
        p=v.co.copy();x,y,z=p
        if not (1.612<z<1.80 and abs(x)<.090 and y<-.055):continue
        crownline=1.711-.064*min(1,abs(x)/.075)
        hit=surface.ray_cast(Vector((x,-.5,z)),Vector((0,1,0)),1)[0]
        if z>crownline-.004:
            if hit is not None:v.co.y=max(y,hit.y+.012)
            continue
        if z>1.704:continue
        eyeprotect=max(math.exp(-(((x-s*.02985)/.016)**2+((z-EYE)/.010)**2)*2) for s in (-1,1))
        lower=max(0,min(1,(z-1.612)/.022));edge=max(0,min(1,(.070-abs(x))/.012))
        if hit is None:continue
        w=lower*edge*(1-eyeprotect)
        delta=max(-.05,min(.05,hit.y-y))*w+.009*eyeprotect
        v.co.y+=delta;moved.append(abs(delta))
    body.data.update()
    # Segment crown using the known fabric/face frontier, varying with azimuth.
    # This is a component extraction, not reconstructed continuous cloth.
    def crown_vertex(p):
        x,y,z=p;front=max(0,min(1,(-y-.04)/.075))
        edge=1.620+front*(.091-.064*min(1,abs(x)/.075))
        return z>edge
    keep=[i for i,p in enumerate(points) if crown_vertex(p)];ids=set(keep);remap={i:k for k,i in enumerate(keep)}
    crown=mesh('279 separated sculpt crown',[points[i] for i in keep],[tuple(remap[i] for i in f) for f in tris if all(i in ids for i in f)],material('279 clay crown',(.12,.12,.12)))
    bpy.data.objects.remove(donor,do_unlink=True)
    # Explicit skull attachment; retain world transform when parenting.
    def attach(ob):
        world=ob.matrix_world.copy();ob.parent=rig;ob.parent_type='BONE';ob.parent_bone='head';ob.matrix_world=world
    bpy.context.view_layer.update();attach(crown)
    for side in ('L','R'):
        for prefix in ('Eye sclera ','Brown iris ','Pupil '):
            ob=bpy.data.objects[prefix+side];world=ob.matrix_world.copy();world.translation+=Vector((0,.013,-.001));ob.matrix_world=world
    scene.cycles.samples=12;scene.render.resolution_x=600;scene.render.resolution_y=720
    bpy.data.objects['key'].data.size=2;bpy.data.objects['fill'].data.energy=70
    cam=scene.camera;cam.data.ortho_scale=.45;target=(0,-.03,EYE-.005)
    views=[('front',(0,-3,EYE)),('left-quarter',(-1.7,-3,EYE)),('right-quarter',(1.7,-3,EYE)),('profile',(3,0,EYE)),('rear',(0,3,EYE+.04))]
    for name,pos in views:
        camera_at(cam,pos,target);scene.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True)
    camera_at(cam,(0,-3,EYE),target)
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'conversion.blend'))
    (out/'build.json').write_text(json.dumps(dict(native_sha256=sha(out/'conversion.blend'),projected_vertices=len(moved),maximum_projection=max(moved),objects=geometry_record(bpy.data.objects),status='INTERNAL_SHAPE_CONTROL'),indent=2))

def launch(j,prepare=False):
    out=validate(j);p,stem=packet(j)
    if prepare:print(stem.with_suffix('.md'));return
    out.mkdir(parents=True,exist_ok=True);log=out/(j['operation']+'.log')
    if log.exists():raise ValueError('Preserve prior attempt')
    (out/(j['operation']+'-source.py')).write_bytes(Path(__file__).read_bytes())
    (out/(j['operation']+'-surgery-source.py')).write_bytes((ROOT/'scripts/sikh279_surgery.py').read_bytes())
    env={k:os.environ[k] for k in ('PATH','HOME','TMPDIR','LANG','LC_ALL') if k in os.environ}
    start=time.monotonic()
    with log.open('w') as f:
        r=subprocess.run(['/Applications/Blender.app/Contents/MacOS/Blender','--background','--offline-mode','--factory-startup','--disable-autoexec','--python-exit-code','7','--python',str(Path(__file__).resolve()),'--',json.dumps(j)],env=env,stdout=f,stderr=subprocess.STDOUT)
    (out/(j['operation']+'-receipt.json')).write_text(json.dumps(dict(returncode=r.returncode,seconds=time.monotonic()-start,packet_digest=p['packet_digest']),indent=2))
    if r.returncode:raise RuntimeError(str(log))
    print(out)

if __name__=='__main__':
    if '--' in sys.argv:
        args=sys.argv[sys.argv.index('--')+1:]
        if len(args)!=1:raise ValueError('One structured job')
        j=json.loads(args[0]);validate(j);run(j)
    else:
        if len(sys.argv) not in (3,4) or (len(sys.argv)==4 and sys.argv[3]!='--prepare'):raise ValueError('operation attempt [--prepare]')
        launch(dict(operation=sys.argv[1],attempt=int(sys.argv[2])),len(sys.argv)==4)
