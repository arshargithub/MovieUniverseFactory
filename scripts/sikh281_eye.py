"""Reviewed fixed local single-eye construction and blink proof; offline only."""
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT/'.runtime/art-direction/series01-sikh280/native-inspection01/study.blend'
SOURCE_SHA = 'd707a63a314ae0d7f989db6a0fb03a664043f4acdfc3d9ca077ffa32aaff722c'
OUT = ROOT/'.runtime/art-direction/series01-sikh281'
CX, CZ = -.097, .175
RX, RZ = .070, .052
RADIUS = .045

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def validate(job):
    if not isinstance(job, dict) or set(job) != {'operation', 'attempt'}:
        raise ValueError('Fixed structured operation required')
    if job['operation'] not in {'build', 'reopen', 'motion', 'verify'} or type(job['attempt']) is not int or not 1 <= job['attempt'] <= 8:
        raise ValueError('Invalid operation or control')
    return OUT/f"control-{job['attempt']:02d}"

def packet(job):
    sys.path.insert(0, str(ROOT/'src'))
    from movie_factory import production_knowledge as pk
    paths = [SOURCE, Path(__file__), ROOT/'tests/test_sikh281_eye.py', ROOT/'results/sikh281/STRATEGY.md',
        ROOT/'results/sikh280/NATIVE_ASSESSMENT.md', ROOT/'docs/knowledge/SIKH_FOUNDATION_REJECTION_271.md',
        ROOT/'docs/planning/MOTION_DESIGN_TEMPLATE.md']
    if job['operation'] != 'build':
        paths.append(validate(job)/'eye.blend')
    task = dict(id=f"sikh281-{job['operation']}-{job['attempt']}", operation='modeling', entities=['sikh'],
        phase='execution', query='Single eye landmark registration eyelid topology blink anatomy correspondence',
        intent='Director confirms approved local working-eye proof. Generic donor only; no hero identity change or external calls.',
        execution_authority=dict(source='results/sikh281/STRATEGY.md',scope='Clarified approval for local landmark and working-eye proof'),
        inputs={str(p.relative_to(ROOT)):sha(p) for p in paths}, open_decisions=[], max_context_characters=42000)
    p = pk.task_packet(ROOT, task)
    folder = ROOT/'results/sikh281'; folder.mkdir(parents=True, exist_ok=True)
    (folder/(task['id']+'.json')).write_text(json.dumps(p, indent=2))
    (folder/(task['id']+'.md')).write_text(pk.packet_markdown(p))
    if not p['dispatch_ready']:
        raise ValueError(p['blockers'])
    return p

def aim(ob, pos, target):
    from mathutils import Vector
    ob.location=pos; ob.rotation_euler=(Vector(target)-ob.location).to_track_quat('-Z','Y').to_euler()

def sample():
    import bpy
    import numpy as np
    rows={}
    for f in (1,13,14,15,16,18,21,36):
        bpy.context.scene.frame_set(f); deps=bpy.context.evaluated_depsgraph_get(); row={}
        for ob in bpy.data.objects:
            if ob.type!='MESH':continue
            ev=ob.evaluated_get(deps); me=ev.to_mesh()
            co=np.empty(len(me.vertices)*3,dtype=np.float32);me.vertices.foreach_get('co',co)
            row[ob.name]=dict(vertices=len(me.vertices),sha256=hashlib.sha256(co.tobytes()).hexdigest(),matrix=[list(r) for r in ob.matrix_world])
            ev.to_mesh_clear()
        rows[str(f)]=row
    bpy.context.scene.frame_set(1)
    return rows

def run(job):
    import bpy
    import bmesh
    from mathutils import Vector, Matrix
    from mathutils.bvhtree import BVHTree
    from collections import Counter, defaultdict
    out=validate(job)
    if bpy.app.online_access or sha(SOURCE)!=SOURCE_SHA:
        raise ValueError('Offline source-bound execution required')
    if job['operation']!='build':
        info=json.loads((out/'build.json').read_text())
        if sha(out/'eye.blend')!=info['native_sha256']:raise ValueError('Native changed')
        bpy.ops.wm.open_mainfile(filepath=str(out/'eye.blend'))
        actual=sample();passed=actual==info['samples']
        (out/'reopen.json').write_text(json.dumps(dict(passed=passed,samples=actual),indent=2))
        if not passed:raise ValueError('Reopen differs')
        if job['operation']=='verify':
            import numpy as np
            body=bpy.data.objects['Generic source with one reconstructed eye'];center=Vector(info['eye_center'])
            rows=[]
            for f in range(1,37):
                bpy.context.scene.frame_set(f);deps=bpy.context.evaluated_depsgraph_get()
                ev=body.evaluated_get(deps);me=ev.to_mesh()
                distances=[(v.co-center).length-RADIUS for v in me.vertices[info['original_vertices']:]]
                rows.append(dict(frame=f,minimum_lid_vertex_globe_clearance=min(distances),
                    finite=all(math.isfinite(x) for v in me.vertices for x in v.co)))
                ev.to_mesh_clear()
            report=dict(samples_exact=passed,rest_return_exact=actual['1']==actual['36'],all_frames=rows,
                limits='Vertex clearance is not triangle intersection or anatomical validation. Rendered front/oblique partial and full closure remain required.')
            (out/'verification.json').write_text(json.dumps(report,indent=2))
            if not report['rest_return_exact'] or not all(r['finite'] for r in rows):raise ValueError('Invalid motion')
        if job['operation']=='motion':
            scene=bpy.context.scene;scene.cycles.samples=12
            scene.render.resolution_x=640;scene.render.resolution_y=640
            scene.camera.data.ortho_scale=.25
            aim(scene.camera,(CX,-3,CZ+.015),(CX,-.2,CZ))
            frames=out/'motion';frames.mkdir(exist_ok=True)
            for f in range(1,37):
                scene.frame_set(f);scene.render.filepath=str(frames/f'{f:04d}.png')
                if 'FINISHED' not in bpy.ops.render.render(write_still=True):raise ValueError('Render incomplete')
        return
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
    body=next(o for o in bpy.data.objects if o.type=='MESH')
    points=[body.matrix_world@v.co for v in body.data.vertices]
    faces=[tuple(p.vertices) for p in body.data.polygons]
    surf=BVHTree.FromPolygons(points,faces,all_triangles=True)
    def hit(x,z):
        p=surf.ray_cast(Vector((x,-2,z)),Vector((0,1,0)),4)[0]
        if p is None:raise ValueError('No facial surface')
        return p
    landmarks={'eye_outer':(-.139,.177),'eye_inner':(-.056,.174), 'other_eye_outer':(.139,.177),
        'other_eye_inner':(.056,.174),'nose_tip':(0,.073),'nose_wing_left':(-.035,.065),
        'nose_wing_right':(.035,.065),'mouth_left':(-.059,-.032),'mouth_right':(.059,-.032),'chin':(0,-.155)}
    registered={n:list(hit(x,z)) for n,(x,z) in landmarks.items()}
    (out/'landmarks.json').write_text(json.dumps(dict(method='Manually annotated normalized front landmarks with source surface ray registration; not automatic anatomy recognition',landmarks=registered),indent=2))
    scene=bpy.context.scene;cam=scene.camera
    aim(cam,(0,-3,.05),(0,0,0));cam.data.ortho_scale=1.28
    for lname,pos,power in [('Key',(-1.1,-1.2,.9),50),('Fill',(1,-1.2,-.15),14)]:
        light=bpy.data.objects[lname];light.data.energy=power;aim(light,pos,(0,0,0))
    scene.render.filepath=str(out/'source-front.png');bpy.ops.render.render(write_still=True)
    markers=[]
    marker_mat=bpy.data.materials.new('Landmark annotation');marker_mat.diffuse_color=(1,.15,.02,1)
    for name,p in registered.items():
        bpy.ops.mesh.primitive_uv_sphere_add(segments=12,ring_count=8,radius=.0035,location=Vector(p)+Vector((0,-.004,0)))
        marker=bpy.context.object;marker.name='Landmark '+name;marker.data.materials.append(marker_mat);markers.append(marker)
    scene.render.filepath=str(out/'landmarks-front.png');bpy.ops.render.render(write_still=True)
    for marker in markers:bpy.data.objects.remove(marker,do_unlink=True)
    # Remove one complete fused-eye patch while retaining unrelated source vertices.
    kept=[];removed=set()
    for f in faces:
        p=sum((points[i] for i in f),Vector())/3
        if p.y<-.12 and ((p.x-CX)/RX)**2+((p.z-CZ)/RZ)**2<1:
            removed.update(f)
        else:kept.append(f)
    edges=Counter(tuple(sorted((f[k],f[(k+1)%3]))) for f in kept for k in range(3))
    adj=defaultdict(list)
    for (a,b),count in edges.items():
        if count==1 and a in removed and b in removed:adj[a].append(b);adj[b].append(a)
    if not adj or any(len(v)!=2 for v in adj.values()):raise ValueError('Cut is not one simple boundary')
    start=min(adj);loop=[start];prev=None;cur=start
    while True:
        nxt=next(v for v in adj[cur] if v!=prev)
        if nxt==start:break
        loop.append(nxt);prev,cur=cur,nxt
        if len(loop)>len(adj):raise ValueError('Boundary traversal failed')
    if len(loop)!=len(adj):raise ValueError('Multiple boundaries')
    angles=[math.atan2((points[i].z-CZ)/RZ,(points[i].x-CX)/RX) for i in loop]
    winding=sum(math.atan2(math.sin(b-a),math.cos(b-a)) for a,b in zip(angles,angles[1:]+angles[:1]))
    if winding<0:loop.reverse();angles.reverse()
    # The retained boundary is subsequently blended with adjacent source skin;
    # uniform inner sectors avoid propagating cut-edge angular irregularity.
    # Uniform sectors prevent collapsed radial columns from a jagged triangular
    # cut. Blend the boundary neighbourhood as a surface, not independent spikes.
    theta=[angles[0]+math.tau*k/len(loop) for k in range(len(loop))]
    cy=hit(CX+.018,CZ).y+math.sqrt(RADIUS**2-.018**2)
    verts=[p.copy() for p in points];rings=[loop];records=[]
    for ri in range(1,13):
        t=ri/12;ring=[]
        for k,(outer,angle) in enumerate(zip(loop,theta)):
            a=.041;dz=(.0145 if math.sin(angle)>0 else .0105)*math.sin(angle)-.001+.0015*math.cos(angle)
            dx=a*math.cos(angle)
            inner=Vector((CX+dx,cy-math.sqrt(max(.000001,RADIUS**2-dx*dx-dz*dz))-.002,CZ+dz))
            p=points[outer].lerp(inner,t)
            # Interpolate from the unchanged outer boundary, not through the old
            # fused eye relief and pupil pits that this patch is replacing.
            d2=(p.x-CX)**2+(p.z-CZ)**2
            if d2<RADIUS**2:
                p.y=min(p.y,cy-math.sqrt(RADIUS**2-d2)-.002)
            ring.append(len(verts));records.append((len(verts),t,angle));verts.append(p)
        rings.append(ring)
    for a,b in zip(rings,rings[1:]):
        for k in range(len(a)):
            n=(k+1)%len(a);kept.append((a[k],a[n],b[n],b[k]))
    # A short posterior rim supplies visible thickness, not a zero-thickness hole.
    rim=[]
    for idx,angle in zip(rings[-1],theta):
        p=verts[idx]+Vector((0,.001,0));rim.append(len(verts));records.append((len(verts),1,angle));verts.append(p)
    for k in range(len(rim)):
        n=(k+1)%len(rim);kept.append((rings[-1][k],rings[-1][n],rim[n],rim[k]))
    neighbours=defaultdict(set)
    for face in kept:
        for k,i in enumerate(face):neighbours[i].update((face[k-1],face[(k+1)%len(face)]))
    protected_inner=set(rings[-1]+rings[-2]+rim)
    movable={i for i,p in enumerate(verts) if i not in protected_inner and p.y<-.12 and
        ((p.x-CX)/(RX+.014))**2+((p.z-CZ)/(RZ+.012))**2<1 and neighbours[i]}
    for iteration in range(24):
        updates={}
        for i in movable:
            p=verts[i];r2=((p.x-CX)/(RX+.014))**2+((p.z-CZ)/(RZ+.012))**2
            weight=.45*min(1,max(0,(1-r2)*6))
            q=p.lerp(sum((verts[n] for n in neighbours[i]),Vector())/len(neighbours[i]),weight)
            d2=(q.x-CX)**2+(q.z-CZ)**2
            if d2<RADIUS**2:q.y=min(q.y,cy-math.sqrt(RADIUS**2-d2)-.002)
            updates[i]=q
        for i,p in updates.items():verts[i]=p
    me=bpy.data.meshes.new('Single eye editable topology');me.from_pydata(verts,[],kept);me.update()
    old=body.data;body.data=me;body.matrix_world=Matrix.Identity(4)
    me.materials.append(old.materials[0])
    bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(me);bm.free()
    for p in me.polygons:p.use_smooth=True
    body.name='Generic source with one reconstructed eye'
    body.shape_key_add(name='Basis',from_mix=False);blink=body.shape_key_add(name='Blink local eye',from_mix=False)
    for idx,t,angle in records:
        p=blink.data[idx].co;dx=p.x-CX
        # Corners remain fixed; eyelid rows slide over the globe and meet at one seam.
        w=t*t*(3-2*t)
        seam=CZ-.003 + .0015*dx/.041
        p.z=p.z*(1-w)+seam*w
        if t>.25:
            d2=dx*dx+(p.z-CZ)**2
            if d2<RADIUS**2:
                target=cy-math.sqrt(RADIUS**2-d2)-.002
                p.y=min(p.y,target)
    for f,v in [(1,0),(12,0),(15,1),(16,1),(21,0),(36,0)]:
        blink.value=v;blink.keyframe_insert('value',frame=f)
    # A linear blend between spherical endpoint poses cuts through the globe.
    # Add a scalar mid-closure corrective; validate all intermediate states.
    corrective=body.shape_key_add(name='Lid spherical travel corrective',from_mix=False)
    for idx,t,angle in records:
        if t<=.25:continue
        a=body.data.shape_keys.key_blocks['Basis'].data[idx].co;b=blink.data[idx].co
        mid=a.lerp(b,.5);d2=(mid.x-CX)**2+(mid.z-CZ)**2
        if d2<RADIUS**2:
            needed=cy-math.sqrt(RADIUS**2-d2)-.0022
            corrective.data[idx].co.y+=min(0,needed-mid.y)
    curve=corrective.driver_add('value');driver=curve.driver;var=driver.variables.new();var.name='b';var.type='SINGLE_PROP'
    var.targets[0].id_type='KEY';var.targets[0].id=body.data.shape_keys
    var.targets[0].data_path='key_blocks["Blink local eye"].value';driver.expression='4*b*(1-b)'
    def material(name,color):
        m=bpy.data.materials.new(name);m.use_nodes=True
        node=m.node_tree.nodes.get('Principled BSDF');node.inputs['Base Color'].default_value=(*color,1);node.inputs['Roughness'].default_value=.4
        return m
    bpy.ops.mesh.primitive_uv_sphere_add(segments=64,ring_count=32,radius=RADIUS,location=(CX,cy,CZ))
    eye=bpy.context.object;eye.name='Separate eye globe';eye.data.materials.append(material('Neutral sclera',(.36,.34,.31)))
    for p in eye.data.polygons:p.use_smooth=True
    # Flush spherical iris and pupil patches, not protruding flat discs.
    for name,radius,color in [('Iris',.014,(.07,.045,.023)),('Pupil',.006,(.006,.005,.004))]:
        offset=.0008 if name=='Pupil' else .0004
        vs=[(CX,cy-RADIUS-offset,CZ)];fs=[]
        for ri in range(1,9):
            for k in range(64):
                a=math.tau*k/64;x=radius*ri/8*math.cos(a);z=radius*ri/8*math.sin(a)
                vs.append((CX+x,cy-math.sqrt(RADIUS**2-x*x-z*z)-offset,CZ+z))
        for k in range(64):fs.append((0,k+1,(k+1)%64+1))
        for ri in range(7):
            for k in range(64):
                n=(k+1)%64; a=1+ri*64; b=a+64
                fs.append((a+k,b+k,b+n,a+n))
        mesh=bpy.data.meshes.new(name);mesh.from_pydata(vs,[],fs);mesh.materials.append(material(name,color))
        ob=bpy.data.objects.new(name,mesh);bpy.context.collection.objects.link(ob)
    scene=bpy.context.scene;scene.frame_start=1;scene.frame_end=36;scene.render.fps=24;scene.cycles.samples=24
    cam=scene.camera
    def render(name,pos,target,scale,frame=1):
        scene.frame_set(frame);aim(cam,pos,target);cam.data.ortho_scale=scale
        q=cam.rotation_euler.to_quaternion()
        for lname,offset,power in [('Key',(-1.1,.9,0),50),('Fill',(1,-.15,0),14)]:
            light=bpy.data.objects[lname];light.data.energy=power
            aim(light,Vector(target)+Vector((0,-1,0))+q@Vector(offset),target)
        scene.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True)
    scene.render.resolution_x=640;scene.render.resolution_y=760
    render('whole-front',(0,-3,.05),(0,0,0),1.28)
    render('whole-oblique',(-1.5,-3,.1),(0,0,0),1.28)
    scene.render.resolution_x=760;scene.render.resolution_y=640
    for label,frame in [('open',1),('half',14),('closed',15)]:
        render(label+'-front',(CX,-3,CZ),(CX,-.2,CZ),.24,frame)
        render(label+'-oblique',(-1.1,-3,CZ+.15),(CX,-.2,CZ),.24,frame)
    scene.frame_set(1)
    samples=sample();bpy.ops.wm.save_as_mainfile(filepath=str(out/'eye.blend'))
    (out/'build.json').write_text(json.dumps(dict(native_sha256=sha(out/'eye.blend'),source_sha256=SOURCE_SHA,
        original_vertices=len(points),boundary_vertices=len(loop),new_lid_vertices=len(records),eye_center=[CX,cy,CZ],
        unrelated_vertices_unchanged=all((body.data.vertices[i].co-p).length<1e-7 for i,p in enumerate(points) if i not in movable),
        source_vertices_in_local_blend=sum(i<len(points) for i in movable),
        samples=samples,status='INTERNAL_CONTROL_NOT_HERO_ADMISSION'),indent=2))

def launch(job,prepare=False):
    out=validate(job);p=packet(job)
    if prepare:print(p['packet_digest']);return
    out.mkdir(parents=True,exist_ok=True)
    log=out/(job['operation']+'.log')
    if log.exists():raise ValueError('Preserve prior attempt')
    # Snapshot the exact executed handler; cumulative attempts retain source provenance.
    import shutil
    shutil.copy2(__file__,out/(job['operation']+'-handler.py'))
    env={k:os.environ[k] for k in ('PATH','HOME','TMPDIR','LANG','LC_ALL') if k in os.environ}
    start=time.monotonic()
    with log.open('w') as h:
        r=subprocess.run(['/Applications/Blender.app/Contents/MacOS/Blender','--background','--offline-mode','--factory-startup','--disable-autoexec','--python-exit-code','7','--python',str(Path(__file__).resolve()),'--',json.dumps(job)],env=env,stdout=h,stderr=subprocess.STDOUT)
    (out/(job['operation']+'-receipt.json')).write_text(json.dumps(dict(seconds=time.monotonic()-start,returncode=r.returncode,packet_digest=p['packet_digest']),indent=2))
    if r.returncode:raise RuntimeError(str(log))
    print(out)

if __name__=='__main__':
    if '--' in sys.argv:
        args=sys.argv[sys.argv.index('--')+1:]
        if len(args)!=1:raise ValueError('One operation')
        run(json.loads(args[0]))
    else:
        if len(sys.argv) not in (3,4):raise ValueError('operation attempt [prepare]')
        launch({'operation':sys.argv[1],'attempt':int(sys.argv[2])},len(sys.argv)==4 and sys.argv[3]=='prepare')
