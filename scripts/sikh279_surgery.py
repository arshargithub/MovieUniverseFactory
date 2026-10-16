"""Localized editable eye surgery and groom on the generic sculpt; no full rig claim."""
import math
import random
import json
import hashlib
from collections import Counter,defaultdict

def sample_scene():
    import bpy
    import numpy as np
    scene=bpy.context.scene;rows={}
    for f in (1,20,21,26,42,54,66,90,96):
        scene.frame_set(f);dep=bpy.context.evaluated_depsgraph_get();row={}
        for ob in sorted(bpy.data.objects,key=lambda o:o.name):
            if ob.type not in {'MESH','CURVE'}:continue
            ev=ob.evaluated_get(dep)
            if ob.type=='MESH':
                coords=np.empty(len(ev.data.vertices)*3,dtype=np.float32);ev.data.vertices.foreach_get('co',coords)
                row[ob.name]=dict(vertices=len(ev.data.vertices),coordinates=hashlib.sha256(coords.tobytes()).hexdigest(),matrix=[list(r) for r in ev.matrix_world])
            else:row[ob.name]=dict(splines=len(ob.data.splines),matrix=[list(r) for r in ev.matrix_world])
        rows[str(f)]=row
    scene.frame_set(1)
    return rows

def construct(job,out,points,tris,surface):
    import bpy
    from mathutils import Vector,Matrix
    from sikh257_native import mesh,material,sphere,camera_at
    from sikh261_character import strands
    from inspect_meshy278 import geometry_record,sha
    scene=bpy.context.scene
    for ob in list(bpy.data.objects):
        if ob.type not in {'LIGHT','CAMERA'}:bpy.data.objects.remove(ob,do_unlink=True)
    eyes=[(-.031,1.6685),(.025,1.6685)]
    vertices=[p.copy() for p in points];faces=[];removed=[set(),set()]
    def eye_region(p,i):
        x,z=eyes[i]
        return p.y<-.08 and ((p.x-x)/.025)**2+((p.z-z)/.019)**2<1
    def beard_region(p):
        top=1.611+.035*min(1,abs(p.x)/.076)**1.5
        mouth=abs(p.x+.002)<.018 and 1.608<p.z<1.619
        front=p.y<-.069 and abs(p.x)<.086 and 1.516<p.z<top
        side=.047<abs(p.x)<.12 and -.07<=p.y<.045 and 1.535<p.z<1.627
        moustache=abs(p.x)<.042 and p.y<-.10 and 1.612<p.z<1.626
        return (front or side or moustache) and not mouth
    for f in tris:
        center=sum((points[i] for i in f),Vector())/len(f)
        region=next((i for i in range(2) if eye_region(center,i)),None)
        if region is not None:
            removed[region].update(f);continue
        faces.append(tuple(f))
    # Reconstruct a hidden jaw support from the beard envelope, smoothing away
    # sculpted locks. Surface remains skin, not a second visible solid beard.
    neighbors=defaultdict(set)
    for f in faces:
        for k,i in enumerate(f):neighbors[i].update((f[(k+1)%len(f)],f[k-1]))
    beardids={i for i,p in enumerate(vertices) if beard_region(p)}
    for _ in range(18):
        updates={i:vertices[i].lerp(sum((vertices[n] for n in neighbors[i]),Vector())/len(neighbors[i]),.65) for i in beardids if neighbors[i]}
        for i,p in updates.items():vertices[i]=p
    for i in beardids:vertices[i].y+=.009
    edges=Counter(tuple(sorted((f[k],f[(k+1)%len(f)]))) for f in faces for k in range(len(f)))
    lid_records=[]
    centers=[]
    for ei,(cx,cz) in enumerate(eyes):
        boundary=[e for e,n in edges.items() if n==1 and all(i in removed[ei] for i in e)]
        adj=defaultdict(list)
        for a,b in boundary:adj[a].append(b);adj[b].append(a)
        if not adj or any(len(v)!=2 for v in adj.values()):raise ValueError('Eye boundary is not a simple loop')
        start=min(adj);loop=[start];prev=None;cur=start
        while True:
            nxt=next(v for v in adj[cur] if v!=prev)
            if nxt==start:break
            loop.append(nxt);prev,cur=cur,nxt
            if len(loop)>len(adj):raise ValueError('Broken eye loop')
        if len(loop)!=len(adj):raise ValueError('Multiple eye holes')
        hit=surface.ray_cast(Vector((cx,-.5,cz)),Vector((0,1,0)),1)[0]
        cy=hit.y+.012;centers.append((cx,cy,cz))
        # Parameterize by cumulative perimeter, not noisy individual radial
        # angles; the raw triangulated cut otherwise folds annulus sectors.
        angles=[math.atan2((vertices[i].z-cz)/.019,(vertices[i].x-cx)/.025) for i in loop]
        winding=sum(math.atan2(math.sin(b-a),math.cos(b-a)) for a,b in zip(angles,angles[1:]+angles[:1]))
        sign=1 if winding>0 else -1
        # Preserve exact original outer edge. Moving it independently folds the
        # adjacent fine source triangles. Only interior rings are regularized.
        unwrapped=[0.]
        for a,b in zip(angles,angles[1:]):unwrapped.append(unwrapped[-1]+sign*math.atan2(math.sin(b-a),math.cos(b-a)))
        for k in range(1,len(unwrapped)):unwrapped[k]=max(unwrapped[k],unwrapped[k-1]+.00001)
        scale=min(1,(math.tau-.00001)/max(unwrapped[-1],.00001))
        parameter=[angles[0]+sign*u*scale for u in unwrapped]
        rings=[loop]
        for ri in range(1,6):
            t=ri/5;ring=[]
            for outerid,angle in zip(loop,parameter):
                outer=vertices[outerid]
                dx=.0122*math.cos(angle);dz=.0035*math.sin(angle)-.0007
                inner=Vector((cx+dx,cy-math.sqrt(max(.000002,.0131**2-dx*dx-dz*dz))-.00055,cz+dz))
                p=outer.lerp(inner,t)
                # Broad convex lid surface, not a flat cutout pasted on the face.
                p.y-=.0003*math.sin(math.pi*t)
                idx=len(vertices);vertices.append(p);ring.append(idx)
                lid_records.append((idx,t,angle,ei))
            rings.append(ring)
        for a,b in zip(rings,rings[1:]):
            for k in range(len(a)):n=(k+1)%len(a);faces.append((a[k],a[n],b[n],b[k]))
    # Smooth the transition as one neighborhood, rather than displacing a seam
    # independently from its adjacent triangles. Preserve the inner wet rim.
    adjacent=defaultdict(set)
    for f in faces:
        for k,i in enumerate(f):adjacent[i].update((f[k-1],f[(k+1)%len(f)]))
    inner={i for i,t,_,_ in lid_records if t>=.8}
    smoothids={i for i,p in enumerate(vertices) if i not in inner and p.y<-.08 and any(((p.x-x)/.029)**2+((p.z-z)/.023)**2<1 for x,z in eyes)}
    for _ in range(8):
        updates={i:vertices[i].lerp(sum((vertices[n] for n in adjacent[i]),Vector())/len(adjacent[i]),.4) for i in smoothids if adjacent[i]}
        for i,p in updates.items():vertices[i]=p
    skin=material('279 warm neutral skin',(.28,.28,.28))
    body=mesh('279 sculpt with welded eyelid loops',vertices,faces,skin)
    # Recalculate annulus winding together with the source surface.
    import bmesh
    bm=bmesh.new();bm.from_mesh(body.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(body.data);bm.free()
    body.shape_key_add(name='Basis');blink=body.shape_key_add(name='Bilateral blink - local topology control')
    for idx,t,angle,ei in lid_records:
        cx,cy,cz=centers[ei];p=blink.data[idx].co;dx=p.x-cx
        finalz=cz-.0014+(-.0004 if math.sin(angle)>0 else .0004)
        # Only the inner rim fully closes; progressively support outer lid.
        p.z=p.z*(1-t*t)+finalz*t*t
        spherey=cy-math.sqrt(max(.000002,.0131**2-dx*dx-(p.z-cz)**2))-.0007
        p.y=min(p.y,spherey)
    for f,value in [(1,0),(18,0),(21,1),(22,1),(26,0),(96,0)]:
        blink.value=value;blink.keyframe_insert('value',frame=f)
    # Source crown is separately editable without opening a new gap at its boundary.
    def crown_point(p):
        front=max(0,min(1,(-p.y-.04)/.075))
        return p.z>1.620+front*(.091-.064*min(1,abs(p.x)/.075))
    crown_faces=[f for f in tris if all(crown_point(points[i]) for i in f)]
    ids=sorted({i for f in crown_faces for i in f});remap={i:k for k,i in enumerate(ids)}
    crown=mesh('279 separated crown component', [points[i] for i in ids],[tuple(remap[i] for i in f) for f in crown_faces],skin)
    # Hide coincident donor crown faces in the editable actor using exact IDs.
    # Duplicated boundary coordinates preserve the original surface appearance.
    crownset={tuple(sorted(f)) for f in crown_faces}
    bm=bmesh.new();bm.from_mesh(body.data);bm.verts.ensure_lookup_table();bm.faces.ensure_lookup_table()
    bmesh.ops.delete(bm,geom=[f for f in bm.faces if tuple(sorted(v.index for v in f.verts)) in crownset],context='FACES_ONLY')
    bm.to_mesh(body.data);bm.free()
    rigdata=bpy.data.armatures.new('279 local performance rig');rig=bpy.data.objects.new('279 local performance rig',rigdata);scene.collection.objects.link(rig)
    bpy.context.view_layer.objects.active=rig;rig.select_set(True);bpy.ops.object.mode_set(mode='EDIT')
    for name,head,tail,parent in [('root',(0,0,1.42),(0,0,1.55),None),('neck',(0,0,1.55),(0,-.03,1.62),'root'),('head',(0,-.03,1.62),(0,-.03,1.82),'neck')]:
        b=rigdata.edit_bones.new(name);b.head=head;b.tail=tail
        if parent:b.parent=rigdata.edit_bones[parent]
    bpy.ops.object.mode_set(mode='OBJECT')
    groups={n:body.vertex_groups.new(name=n) for n in ('root','neck','head')}
    for v in body.data.vertices:
        z=v.co.z;head=max(0,min(1,(z-1.58)/.055))
        if v.co.y<-.065 and z>1.516:head=1
        if .047<abs(v.co.x) and -.07<v.co.y<.045 and z>1.535:head=1
        neck=(1-head)*max(0,min(1,(z-1.50)/.075));root=1-head-neck
        for name,w in [('head',head),('neck',neck),('root',root)]:
            if w:groups[name].add([v.index],w,'REPLACE')
    mod=body.modifiers.new('Weighted skull neck and fixed torso','ARMATURE');mod.object=rig
    def attach(ob):
        bpy.context.view_layer.update();world=ob.matrix_world.copy();ob.parent=rig;ob.parent_type='BONE';ob.parent_bone='head';ob.matrix_world=world
    attach(crown)
    for ei,(cx,cy,cz) in enumerate(centers):
        scl=sphere('279 independent eye '+str(ei),(cx,cy,cz),(.013,.013,.013),material('279 sclera '+str(ei),(.48,.45,.40)))
        iris=sphere('279 brown iris '+str(ei),(cx,cy-.0126,cz),(.0046,.0010,.0046),material('279 iris '+str(ei),(.045,.026,.013)))
        pupil=sphere('279 pupil '+str(ei),(cx,cy-.0133,cz),(.0020,.0005,.0020),material('279 pupil '+str(ei),(.004,.003,.002)))
        for ob in (scl,iris,pupil):attach(ob)
    # Rooted replacement hairs. No old sculpted beard is retained beneath them.
    rng=random.Random(279);paths=[[],[],[]]
    for side in (-1,1):
        for k in range(9000):
            ax=rng.uniform(0,.074);x=side*ax
            top=1.611+.035*(ax/.076)**1.5
            z=rng.uniform(1.532,top+.004)
            if rng.random()>max(0,min(1,(top+.004-z)/.010)):continue
            if ax<.020:z=min(z,1.608)
            root=surface.ray_cast(Vector((x,-.5,z)),Vector((0,1,0)),1)[0]
            if root is None:continue
            # Source sculpt is an envelope guide, not retained solid hair.
            root.y+=.0025
            length=rng.uniform(.008,.038)
            end=root+Vector((-side*ax*.12,rng.uniform(-.006,.002),-length))
            end.z=max(1.514+.027*(ax/.076)**2+rng.uniform(-.006,.006),end.z)
            if end.z>z-.003:continue
            phase=round(ax/.011)*1.55+rng.uniform(-.22,.22)
            path=[]
            for q in range(20):
                t=q/19;p=root.lerp(end,t)
                p.x+=side*(.002*math.sin(math.pi*t)+.0025*math.sin(t*9+phase)*math.sin(math.pi*t))*min(1,ax/.025)
                p.y-=.003*math.sin(math.pi*t)+.002*math.sin(t*8+phase)*math.sin(math.pi*t)
                path.append(tuple(p))
            paths[rng.choices(range(3),[.67,.26,.07])[0]].append(path)
        for k in range(950):
            x=side*rng.uniform(.002,.034);z=1.625-.007*(abs(x)/.034)+rng.uniform(-.002,.002)
            root=surface.ray_cast(Vector((x,-.5,z)),Vector((0,1,0)),1)[0]
            if root is None:continue
            end=root+Vector((side*rng.uniform(.003,.011),-.002,-rng.uniform(.006,.014)))
            paths[0].append([tuple(root.lerp(end,t)+Vector((0,-.003*math.sin(math.pi*t),0))) for t in [q/12 for q in range(13)]])
    # Side roots are sampled on the actual 3D surface, not a front-only ray map.
    candidates=[]
    for f in tris:
        p=sum((points[i] for i in f),Vector())/3
        if .045<abs(p.x)<.115 and -.085<p.y<-.025 and 1.535<p.z<1.627:
            a,b,c=[points[i] for i in f];area=(b-a).cross(c-a).length/2
            if area>1e-10:candidates.append((f,area))
    if candidates:
        for f in rng.choices([p[0] for p in candidates],weights=[p[1] for p in candidates],k=6500):
            a,b,c=[points[i] for i in f];u=math.sqrt(rng.random());v=rng.random();root=a*(1-u)+b*u*(1-v)+c*u*v
            side=1 if root.x>0 else -1;end=root+Vector((side*.001,-.002,-rng.uniform(.008,.026)))
            ps=[]
            for k in range(13):
                t=k/12;p=root.lerp(end,t);p.x+=side*.002*math.sin(math.pi*t);p.y-=.002*math.sin(t*8)*math.sin(math.pi*t);ps.append(tuple(p))
            paths[rng.choices(range(3),[.67,.26,.07])[0]].append(ps)
    for i,ps in enumerate(paths):
        ob=strands('279 replacement beard '+str(i),ps,material('279 hair tone '+str(i),[(.016,.011,.008),(.034,.025,.018),(.070,.054,.041)][i]),.00018);attach(ob)
    for f,a in [(1,0),(30,0),(54,15),(66,15),(90,0),(96,0)]:
        for n,fraction in [('head',.72),('neck',.28)]:
            b=rig.pose.bones[n];b.rotation_mode='XYZ';b.rotation_euler=(0,math.radians(a)*fraction,0);b.keyframe_insert('rotation_euler',frame=f)
    scene.frame_start=1;scene.frame_end=96;scene.render.fps=24;scene.frame_set(1)
    scene.cycles.samples=16;scene.render.resolution_x=600;scene.render.resolution_y=720
    bpy.data.objects['key'].data.size=2;bpy.data.objects['fill'].data.energy=70
    cam=scene.camera;cam.data.ortho_scale=.47;target=(0,-.03,1.655)
    for name,pos in [('front',(0,-3,1.67)),('left-quarter',(-1.7,-3,1.67)),('right-quarter',(1.7,-3,1.67)),('profile',(3,0,1.67)),('rear',(0,3,1.68))]:
        camera_at(cam,pos,target);scene.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True)
    camera_at(cam,(0,-3,1.67),target)
    for f in (20,21,54):
        scene.frame_set(f);scene.render.filepath=str(out/f'pose-{f:03d}.png');bpy.ops.render.render(write_still=True)
    scene.frame_set(1)
    hidden={o.name:o.hide_render for o in bpy.data.objects}
    for o in bpy.data.objects:
        if o.type in {'MESH','CURVE'}:o.hide_render=o!=crown
    for name,pos in [('crown-component-front',(0,-3,1.72)),('crown-component-rear',(0,3,1.72))]:
        camera_at(cam,pos,(0,0,1.71));scene.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True)
    for o in bpy.data.objects:o.hide_render=hidden[o.name]
    camera_at(cam,(0,-3,1.67),target)
    samples=sample_scene();bpy.ops.wm.save_as_mainfile(filepath=str(out/'conversion.blend'))
    (out/'build.json').write_text(json.dumps(dict(native_sha256=sha(out/'conversion.blend'),eye_centers=centers,eyelid_vertices=len(lid_records),beard_curves=sum(map(len,paths)),crown_triangles=len(crown_faces),objects=geometry_record(bpy.data.objects),samples=samples,status='INTERNAL_LOCAL_SURGERY_CONTROL_NOT_FULL_RETOPOLOGY'),indent=2))
