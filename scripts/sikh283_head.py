"""Fixed offline integrated-head construction. No external code or provider input."""
import hashlib
import json
import math
import os
from pathlib import Path
import random
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'.runtime/art-direction/series01-sikh281/control-04/eye.blend'
CROWN=ROOT/'.runtime/art-direction/series01-sikh279/control-11/conversion.blend'
OUT=ROOT/'.runtime/art-direction/series01-sikh283'
EXPECTED={BASE:'563e64aaffbf9ca39a5a8f507459ebccb003078e597fd43bdae7985293c0898f',CROWN:'362d1815ba468a8ce1e49d4ecaa162e7782afcfa8476bef746d30a2be9174eb6'}

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def validate(job):
    if not isinstance(job,dict) or set(job)!={'operation','attempt'}:raise ValueError('Structured operation required')
    if job['operation'] not in {'build','motion','verify','inspect'} or type(job['attempt']) is not int or not 1<=job['attempt']<=12:raise ValueError('Invalid operation')
    return OUT/f"control-{job['attempt']:02d}"

def packet(job):
    sys.path.insert(0,str(ROOT/'src'))
    from movie_factory import production_knowledge as pk
    paths=[BASE,CROWN,Path(__file__),ROOT/'tests/test_sikh283_head.py',ROOT/'results/sikh283/STRATEGY.md',ROOT/'docs/knowledge/SIKH_FOUNDATION_REJECTION_271.md',ROOT/'docs/planning/SERIES_01_SIKH_BASELINE_V01.md',ROOT/'.runtime/art-direction/series01-sikh257/sikh-uncovered-concept-v03.png',ROOT/'.runtime/art-direction/series01-facebuilder-trial-01/natural152-preview-16/front.png']
    if job['attempt']>=5:paths.append(OUT/'skin-color-study01.png')
    if job['attempt']>=12:paths.append(OUT/'skin-color-study02.png')
    if (ROOT/'results/sikh283/ASSESSMENT.md').exists():
        paths.extend([ROOT/'results/sikh283/ASSESSMENT.md',ROOT/'.runtime/art-direction/series01-entrances-v04/C-illustrated-landscape.png',ROOT/'.runtime/art-direction/series01-sikh271-audit/accepted-pashtun-7s5.png'])
    if job['operation']!='build':paths.append(validate(job)/'head.blend')
    task=dict(id=f"sikh283-{job['operation']}-{job['attempt']}",operation='modeling',entities=['sikh','sikh_beard','sikh_turban_cover'],phase='execution',query='integrated character eyes blink gaze beard turban skin neck performance same film',intent='Director283 authorizes scope282 integrated head and short performance, not whole entrance or paid calls.',execution_authority={'source':'results/sikh283/STRATEGY.md','scope':'Local integrated Sikh head and short performance'},inputs={str(p.relative_to(ROOT)):sha(p) for p in paths},open_decisions=[],max_context_characters=42000)
    p=pk.task_packet(ROOT,task);folder=ROOT/'results/sikh283';folder.mkdir(exist_ok=True)
    (folder/(task['id']+'.json')).write_text(json.dumps(p,indent=2));(folder/(task['id']+'.md')).write_text(pk.packet_markdown(p))
    if not p['dispatch_ready']:raise ValueError(p['blockers'])
    return p

def aim(ob,pos,target):
    from mathutils import Vector
    ob.location=pos;ob.rotation_euler=(Vector(target)-ob.location).to_track_quat('-Z','Y').to_euler()

def material(name,colors,scale=25,rough=.65,bump=.0005):
    import bpy
    m=bpy.data.materials.new(name);m.use_nodes=True;n=m.node_tree.nodes;l=m.node_tree.links
    bs=n.get('Principled BSDF');bs.inputs['Roughness'].default_value=rough
    bs.inputs['Specular IOR Level'].default_value=.08 if 'Hair' in name else .3
    tex=n.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=scale;tex.inputs['Detail'].default_value=3
    ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].position=.24;ramp.color_ramp.elements[1].position=.78
    for e,c in zip(ramp.color_ramp.elements,colors):e.color=(*c,1)
    l.new(tex.outputs['Fac'],ramp.inputs[0]);l.new(ramp.outputs[0],bs.inputs['Base Color'])
    fine=n.new('ShaderNodeTexNoise');fine.inputs['Scale'].default_value=550
    b=n.new('ShaderNodeBump');b.inputs['Strength'].default_value=.22;b.inputs['Distance'].default_value=bump
    l.new(fine.outputs['Fac'],b.inputs['Height']);l.new(b.outputs[0],bs.inputs['Normal'])
    return m

def mesh(name,vs,fs,mat):
    import bpy
    me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update()
    ob=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(ob)
    if mat:me.materials.append(mat)
    for p in me.polygons:p.use_smooth=True
    return ob

def beard_top(x):
    """Organic cheek-growth boundary; one shared definition for roots and fade."""
    a=min(1,abs(x)/.205)
    return -.004+.125*a**1.45+.006*math.sin(x*103)+.004*math.sin(x*237)

def curves(name,paths,mat,radius):
    import bpy
    cu=bpy.data.curves.new(name,'CURVE');cu.dimensions='3D';cu.resolution_u=2;cu.bevel_depth=radius;cu.bevel_resolution=1
    for pts in paths:
        s=cu.splines.new('POLY');s.points.add(len(pts)-1)
        for k,(p,q) in enumerate(zip(s.points,pts)):
            t=k/(len(pts)-1)
            p.co=(*q,1);p.radius=max(.035,(1-t)**.65)*min(1,.15+t*9)
    ob=bpy.data.objects.new(name,cu);bpy.context.collection.objects.link(ob);cu.materials.append(mat);return ob

def snapshot():
    import bpy
    import numpy as np
    rows={}
    for f in (1,25,45,63,66,70,90,108,130,144):
        bpy.context.scene.frame_set(f);dg=bpy.context.evaluated_depsgraph_get();row={}
        for ob in sorted(bpy.data.objects,key=lambda o:o.name):
            if ob.type!='MESH':continue
            ev=ob.evaluated_get(dg);me=ev.to_mesh();a=np.empty(len(me.vertices)*3,dtype=np.float32);me.vertices.foreach_get('co',a)
            row[ob.name]={'sha':hashlib.sha256(a.tobytes()).hexdigest(),'matrix':[list(r) for r in ob.matrix_world],'finite':bool(np.isfinite(a).all())};ev.to_mesh_clear()
        rows[str(f)]=row
    bpy.context.scene.frame_set(1);return rows

def run(job):
    import bpy
    import bmesh
    from mathutils import Vector,Matrix
    from mathutils.bvhtree import BVHTree
    out=validate(job);attempt=job['attempt']
    if bpy.app.online_access or any(sha(p)!=v for p,v in EXPECTED.items()):raise ValueError('Source or offline guard failed')
    if job['operation']!='build':
        info=json.loads((out/'build.json').read_text())
        if sha(out/'head.blend')!=info['native_sha256']:raise ValueError('Native changed')
        bpy.ops.wm.open_mainfile(filepath=str(out/'head.blend'));actual=snapshot()
        (out/'verify.json').write_text(json.dumps({'exact_reopen':actual==info['samples'],'samples':actual},indent=2))
        if job['operation'] in {'inspect','verify'}:
            rows={}
            for ob in bpy.data.objects:
                if ob.type=='MESH':
                    pts=[ob.matrix_world@v.co for v in ob.data.vertices]
                    rows[ob.name]={'location':list(ob.location),'matrix':[list(r) for r in ob.matrix_world],'bounds':[[min(p[i] for p in pts),max(p[i] for p in pts)] for i in range(3)],'materials':[m.name for m in ob.data.materials]}
            (out/'inspect.json').write_text(json.dumps(rows,indent=2))
            if job['operation']=='inspect':
                scene=bpy.context.scene;scene.frame_set(1);scene.camera.data.ortho_scale=.24
                aim(scene.camera,(-.097,-3,.175),(-.097,-.2,.175));scene.render.filepath=str(out/'eye-detail.png');bpy.ops.render.render(write_still=True)
        if actual!=info['samples']:raise ValueError('Reopen mismatch')
        if job['operation']=='motion':
            scene=bpy.context.scene;scene.cycles.samples=12;scene.render.resolution_x=576;scene.render.resolution_y=720
            frames=out/'motion';frames.mkdir(exist_ok=True)
            for f in range(1,145):
                scene.frame_set(f);scene.render.filepath=str(frames/f'{f:04d}.png');bpy.ops.render.render(write_still=True)
        return
    bpy.ops.wm.open_mainfile(filepath=str(BASE));old=bpy.data.objects['Generic source with one reconstructed eye'];oldkeys=old.data.shape_keys.key_blocks
    # Clip the proven left half exactly at the sagittal plane, carrying all key coordinates.
    # Reflect the complete eye/skin interface rather than performing a second inconsistent surgery.
    names=['Basis','Blink local eye','Lid spherical travel corrective'];values={n:[v.co.copy() for v in oldkeys[n].data] for n in names}
    vs=[];fs=[];maps={};keycoords={n:[] for n in names}
    def add(key,coords):
        if key not in maps:
            maps[key]=len(vs);vs.append(coords['Basis'])
            for n in names:keycoords[n].append(coords[n])
        return maps[key]
    for face in old.data.polygons:
        ids=list(face.vertices);poly=[]
        for a,b in zip(ids,ids[1:]+ids[:1]):
            pa,pb=values['Basis'][a],values['Basis'][b]
            if pa.x<=0:poly.append(add(('v',a),{n:values[n][a].copy() for n in names}))
            if (pa.x<0<pb.x) or (pb.x<0<pa.x):
                t=-pa.x/(pb.x-pa.x);poly.append(add(('e',min(a,b),max(a,b)),{n:values[n][a].lerp(values[n][b],t) for n in names}))
        if len(poly)>=3:fs.append(tuple(poly))
    mirror={}
    for i,p in list(enumerate(vs)):
        if abs(p.x)<1e-7:mirror[i]=i
        else:mirror[i]=len(vs);vs.append(Vector((-p.x,p.y,p.z)));[keycoords[n].append(Vector((-keycoords[n][i].x,keycoords[n][i].y,keycoords[n][i].z))) for n in names]
    fs+= [tuple(mirror[i] for i in reversed(f)) for f in list(fs)]
    skin=material('Warm varied skin',[(.22,.092,.039),(.28,.135,.066)],85,.64,.00022)
    skin.node_tree.nodes.get('Principled BSDF').inputs['Subsurface Weight'].default_value=.055
    body=mesh('Sikh face and neck',vs,fs,skin)
    if attempt>=5:
        # Fixed rest-space projection, feathered away from side silhouettes and
        # groom boundaries. It is surface color only, not geometry replacement.
        uv=body.data.uv_layers.new(name='Authored front color')
        mask=body.data.color_attributes.new(name='Front color weight',type='FLOAT_COLOR',domain='POINT')
        up=Vector((0,.05,3)).normalized();target=Vector((0,0,.07))
        for v in body.data.vertices:
            p=v.co;top=beard_top(p.x)
            w=max(0,min(1,(-p.y-.045)/.09))*max(0,min(1,(.21-abs(p.x))/.045))
            w*=max(0,min(1,(p.z-top-.004)/.025))*max(0,min(1,(.36-p.z)/.04))
            w*=1-math.exp(-((abs(p.x)-.10)/.080)**8-((p.z-.248)/.016)**8)
            mask.data[v.index].color=(w,w,w,1)
        for poly in body.data.polygons:
            for li in poly.loop_indices:
                p=body.data.vertices[body.data.loops[li].vertex_index].co
                uv.data[li].uv=(.5+p.x/1.056,.5+(p-target).dot(up)/1.32)
        n=skin.node_tree.nodes;l=skin.node_tree.links;bs=n.get('Principled BSDF')
        tex=n.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(OUT/('skin-color-study02.png' if attempt>=12 else 'skin-color-study01.png')));tex.image.pack();tex.extension='EXTEND'
        attr=n.new('ShaderNodeVertexColor');attr.layer_name=mask.name
        mix=n.new('ShaderNodeMixRGB');oldlink=bs.inputs['Base Color'].links[0];source=oldlink.from_socket;l.remove(oldlink)
        l.new(source,mix.inputs[1]);l.new(tex.outputs['Color'],mix.inputs[2]);l.new(attr.outputs['Color'],mix.inputs[0]);l.new(mix.outputs[0],bs.inputs['Base Color'])
    rim=body.data.color_attributes.new(name='Lid rim pigment',type='FLOAT_COLOR',domain='POINT')
    for v in rim.data:v.color=(0,0,0,1)
    for key,idx in maps.items():
        if key[0]!='v':continue
        sourceidx=key[1];weight=max(0,min(1,(sourceidx-(49256+94*10))/(94*2))) if sourceidx>=49256 else 0
        if weight:
            for vi in {idx,mirror[idx]}:rim.data[vi].color=(weight*.72,)*3+(1,)
    n=skin.node_tree.nodes;l=skin.node_tree.links;bs=n.get('Principled BSDF');attr=n.new('ShaderNodeVertexColor');attr.layer_name=rim.name
    mix=n.new('ShaderNodeMixRGB');link=bs.inputs['Base Color'].links[0];source=link.from_socket;l.remove(link)
    mix.inputs[2].default_value=(.075,.026,.014,1);l.new(source,mix.inputs[1]);l.new(attr.outputs['Color'],mix.inputs[0]);l.new(mix.outputs[0],bs.inputs['Base Color'])
    for n in names:
        key=body.shape_key_add(name=n)
        for v,p in zip(key.data,keycoords[n]):v.co=p
    # Sculpt a restrained upper-lid crease and stronger inner brow, applied to
    # all keys so blink does not erase the facial support form.
    for key in body.data.shape_keys.key_blocks:
        for v in key.data:
            p=v.co
            if p.y<-.12:
                crease=math.exp(-((abs(p.x)-.097)/.045)**4-((p.z-.203)/.0045)**2)
                brow=math.exp(-((abs(p.x)-.07)/.05)**2-((p.z-.237)/.025)**2)
                p.y+=.0025*crease-.004*brow;p.z-=.003*brow
    # Retain nose/brow planes; slightly lengthen lower face without widening jaw.
    for key in body.data.shape_keys.key_blocks:
        for v in key.data:
            p=v.co
            if -.19<p.z<.07 and p.y<-.07:p.z-=.010*math.sin(math.pi*(p.z+.19)/.26)
    blink=body.data.shape_keys.key_blocks[names[1]];correct=body.data.shape_keys.key_blocks[names[2]]
    drv=correct.driver_add('value').driver;var=drv.variables.new();var.name='b';var.type='SINGLE_PROP';var.targets[0].id_type='KEY';var.targets[0].id=body.data.shape_keys;var.targets[0].data_path='key_blocks["Blink local eye"].value';drv.expression='4*b*(1-b)'
    for f,v in [(1,0),(62,0),(65,1),(66,1),(70,0),(144,0)]:blink.value=v;blink.keyframe_insert('value',frame=f)
    expression=body.shape_key_add(name='Recognition softening')
    for v in expression.data:
        p=v.co
        if p.y<-.10:
            brow=math.exp(-((abs(p.x)-.095)/.065)**2-((p.z-.218)/.030)**2)
            p.z+=.006*brow
            mouth=math.exp(-((abs(p.x)-.052)/.024)**2-((p.z+.036)/.024)**2)
            p.z+=.004*mouth
    for f,v in [(1,0),(40,0),(70,1),(108,.8),(144,0)]:expression.value=v;expression.keyframe_insert('value',frame=f)
    # Remove old source body and retain eye materials and patch topology as independent components.
    bpy.data.objects.remove(old,do_unlink=True)
    for ob in list(bpy.data.objects):
        if ob.type=='MESH' and ob!=body and ob.name not in {'Separate eye globe','Iris','Pupil'}:bpy.data.objects.remove(ob,do_unlink=True)
    centers=[];eyes=[]
    base_eye=bpy.data.objects['Separate eye globe'];cx,cy,cz=base_eye.location
    for side in (-1,1):
        center=Vector((side*abs(cx),cy,cz));centers.append(center)
        root=bpy.data.objects.new('Gaze '+str(side),None);bpy.context.collection.objects.link(root);root.location=center
        for name in ('Separate eye globe','Iris','Pupil'):
            src=bpy.data.objects[name];ob=src.copy();ob.data=src.data.copy();bpy.context.collection.objects.link(ob);ob.name=name+' '+str(side)
            for v in ob.data.vertices:
                world=src.matrix_world@v.co
                if side==1:world.x=-world.x
                v.co=world-center
                if name in {'Iris','Pupil'}:
                    v.co.x*=1.40;v.co.z*=1.40
                    v.co.y=-math.sqrt(max(.00001,.045**2-v.co.x**2-v.co.z**2))-(.0008 if name=='Pupil' else .0004)
            ob.matrix_world=Matrix.Identity(4);ob.parent=root;ob.location=(0,0,0)
            # Reflection reverses winding. Recalculate consistently and smooth
            # the spherical patches, which the component proof left faceted.
            bm=bmesh.new();bm.from_mesh(ob.data)
            bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
            if name in {'Iris','Pupil'}:
                for face in bm.faces:
                    if face.normal.y>0:face.normal_flip()
            bm.to_mesh(ob.data);bm.free()
            for p in ob.data.polygons:p.use_smooth=True
            if name=='Separate eye globe':
                ob.data.materials.clear();ob.data.materials.append(material('Warm sclera '+str(side),[(.12,.105,.085),(.20,.18,.15)],80,.40,.00001))
            if name=='Iris':
                ob.data.materials.clear();ob.data.materials.append(material('Deep brown iris '+str(side),[(.025,.012,.005),(.075,.038,.013)],120,.33,.00001))
                # Rest-space radial pigment retains a dark limbal edge without
                # introducing a projecting disc or a painted eye on the skin.
                color=ob.data.color_attributes.new(name='Iris pigment',type='FLOAT_COLOR',domain='POINT')
                for v in ob.data.vertices:
                    r=math.hypot(v.co.x,v.co.z)/.0196;a=math.atan2(v.co.z,v.co.x)
                    ray=.65+.2*math.sin(a*73)+.15*math.sin(a*127+r*13)
                    edge=max(0,min(1,(.99-r)/.14));c=(.055*ray*edge+.008,.025*ray*edge+.005,.008*ray*edge+.003)
                    color.data[v.index].color=(*c,1)
                mat=ob.data.materials[0];node=mat.node_tree.nodes.new('ShaderNodeVertexColor');node.layer_name=color.name
                mat.node_tree.links.new(node.outputs['Color'],mat.node_tree.nodes.get('Principled BSDF').inputs['Base Color'])
            shader=ob.data.materials[0].node_tree.nodes.get('Principled BSDF')
            shader.inputs['Coat Weight'].default_value=0;shader.inputs['Specular IOR Level'].default_value=.025
            if name=='Pupil':shader.inputs['Roughness'].default_value=.32
        for f,yaw,pitch in [(1,0,0),(22,0,0),(32,7,-4),(60,5,-4),(85,0,0),(108,0,0),(144,0,0)]:
            root.rotation_euler=(math.radians(pitch),0,math.radians(yaw));root.keyframe_insert('rotation_euler',frame=f)
        eyes.append(root)
    for name in ('Separate eye globe','Iris','Pupil'):bpy.data.objects.remove(bpy.data.objects[name],do_unlink=True)
    points=[v.co.copy() for v in body.data.vertices];surface=BVHTree.FromPolygons(points,[list(p.vertices) for p in body.data.polygons])
    def hit(x,z):
        p=surface.ray_cast(Vector((x,-2,z)),Vector((0,1,0)),4)[0]
        return p
    rng=random.Random(283);hairm=[material('Hair '+str(i),[a,b],70,.57,.00004) for i,(a,b) in enumerate([((.008,.005,.003),(.020,.012,.007)),((.018,.011,.006),(.042,.027,.014)),((.040,.029,.018),(.080,.058,.035))])]
    paths=[[],[],[]]
    # Irregular guide families form layered locks; root cloud follows skin rather than a solid beard shell.
    for side in (-1,1):
        guides=[]
        for j in range(72):
            x=side*rng.uniform(.008,.205);top=beard_top(x);z=rng.uniform(-.14,top)
            if abs(x)<.055:z=min(z,-.075)
            root=hit(x,z)
            if root is None:continue
            bottom=-.39+.10*(abs(x)/.205)**2
            endz=z+(bottom-z)*rng.uniform(.55,1.02)
            guides.append((root,endz,rng.uniform(0,math.tau),rng.uniform(.020,.038)))
        for root,endz,phase,width in guides:
            for k in range(150):
                x=root.x+rng.gauss(0,width*.38);z=root.z+rng.gauss(0,.012);r=hit(x,z)
                if r is None:continue
                top=beard_top(x)
                if z>top or (abs(x)<.055 and z>-.065):continue
                if rng.random()>max(0,min(1,(top-z)/.048)):continue
                r.y-=.0006
                lengthblend=.18+.82*min(1,max(0,(top-z)/.075))
                end=Vector((x*(.96+rng.uniform(-.05,.05)),r.y-.020+rng.uniform(-.008,.008),z+(endz-z)*lengthblend+rng.uniform(-.014,.014)))
                ps=[]
                for q in range(17):
                    t=q/16;p=r.lerp(end,t);en=math.sin(math.pi*t)
                    p.x+=side*(.012*en+.021*lengthblend*math.sin(t*10+phase)*en);p.y-=.028*en+.017*lengthblend*math.sin(t*9+phase)*en
                    ps.append(tuple(p))
                paths[rng.choices(range(3),[.79,.19,.02])[0]].append(ps)
        # Upper-lip rooted moustache fans outward and down into cheek hair, not upward wings.
        for k in range(1700):
            x=side*rng.uniform(.001,.080);z=.012-.020*(abs(x)/.080)+rng.uniform(-.009,.009);r=hit(x,z)
            if r is None:continue
            end=r+Vector((side*rng.uniform(.008,.027),-.010,-rng.uniform(.028,.047)))
            paths[rng.choices(range(3),[.8,.18,.02])[0]].append([tuple(r.lerp(end,t)+Vector((0,-.009*math.sin(math.pi*t),.005*math.sin(math.pi*t)))) for t in [q/14 for q in range(15)]])
        for k in range(450):
            x=side*rng.uniform(.001,.029);z=rng.uniform(-.007,.017);r=hit(x,z)
            if r is None:continue
            end=r+Vector((side*rng.uniform(.004,.016),-.005,-rng.uniform(.017,.028)))
            paths[0].append([tuple(r.lerp(end,q/8)) for q in range(9)])
        # Close, irregular brow hair integrates with the brow plane.
        brow=[]
        for k in range(1000):
            x=side*rng.uniform(.036,.170);z=.211+.014*math.sin((abs(x)-.036)/.134*math.pi)+rng.gauss(0,.005);r=hit(x,z)
            if r is None:continue
            r.y-=.001;end=r+Vector((side*.012,-.002,rng.uniform(.002,.010)))
            brow.append([tuple(r.lerp(end,q/5)) for q in range(6)])
        curves('Brow '+str(side),brow,hairm[0],.00055)
        # Sparse short growth softens the cheek boundary without drawing a hard
        # painted stripe. It has an actual root and randomized finite length.
        for k in range(1800):
            x=side*rng.uniform(.012,.21);top=beard_top(x)
            z=top+rng.uniform(-.026,.014)
            if abs(x)<.065:continue
            r=hit(x,z)
            if r is None:continue
            r.y-=.0008;length=rng.uniform(.004,.025)
            paths[0].append([tuple(r+Vector((side*.003*t,-.003*math.sin(t*math.pi),-length*t))) for t in [q/5 for q in range(6)]])
    for i,p in enumerate(paths):curves('Layered beard '+str(i),p,hairm[i],.00065 if i<2 else .00043)
    # Root the sideburn/jaw transition on real side-facing triangles, not a
    # front projection that leaves an empty wedge immediately ahead of the ear.
    candidates=[]
    for face in body.data.polygons:
        if len(face.vertices)!=3:continue
        a,b,c=[points[i] for i in face.vertices];p=(a+b+c)/3
        if abs(p.x)>.185 and -.13<p.y<.06 and -.18<p.z<.15:
            area=(b-a).cross(c-a).length/2
            if area>1e-10:candidates.append((a,b,c,area))
    sidepaths=[]
    for a,b,c,area in rng.choices(candidates,weights=[q[3] for q in candidates],k=5000):
        u=math.sqrt(rng.random());v=rng.random();r=a*(1-u)+b*u*(1-v)+c*u*v;side=1 if r.x>0 else -1
        normal=(b-a).cross(c-a).normalized();r+=normal*.0008;length=rng.uniform(.025,.10)
        end=r+Vector((side*.004,-.009,-length));phase=rng.uniform(0,math.tau)
        sidepaths.append([tuple(r.lerp(end,t)+Vector((side*.006*math.sin(math.pi*t),.005*math.sin(t*8+phase)*math.sin(math.pi*t),0))) for t in [q/12 for q in range(13)]])
    curves('Sideburn and jaw roots',sidepaths,hairm[0],.00052)
    # Append only the useful crown component, never embedded source scene controls.
    with bpy.data.libraries.load(str(CROWN),link=False) as (src,dst):dst.objects=['279 separated crown component']
    crown=dst.objects[0];bpy.context.collection.objects.link(crown);crown.name='Sikh tied crown'
    crown.parent=None;crown.matrix_world=Matrix.Identity(4);crown.animation_data_clear()
    for v in crown.data.vertices:
        p=v.co;p.x=(p.x-.02)*3.0;p.y=(p.y+.025)*3.45;p.z=(p.z-1.6685)*3.0+.265
    # Smooth the extracted edge together with its immediate support, then give
    # the cloth a thin physical underside instead of a jagged paper cut.
    bm=bmesh.new();bm.from_mesh(crown.data)
    boundary={v for e in bm.edges if e.is_boundary for v in e.verts}
    for _ in range(25):
        updates={v:v.co.lerp(sum((e.other_vert(v).co for e in v.link_edges if e.is_boundary),Vector())/sum(e.is_boundary for e in v.link_edges),.45) for v in boundary if any(e.is_boundary for e in v.link_edges)}
        for v,p in updates.items():v.co=p
    bm.to_mesh(crown.data);bm.free()
    solid=crown.modifiers.new('Thin cloth underside','SOLIDIFY');solid.thickness=.004;solid.offset=-1
    crown.data.materials.clear();cloth=material('Worn indigo weave',[(.003,.005,.020),(.008,.012,.040)],170,.86,.00016);crown.data.materials.append(cloth)
    # A tucked continuation emerges behind the ear; actual release still requires motion proof.
    sv=[];sf=[]
    for j in range(33):
        t=j/32
        for k in range(9):
            u=k/8-.5;sv.append((-.22+.045*t+.09*u,.035+.055*t+.012*math.sin(u*13+t*3),.12-.55*t+.012*math.cos(u*12)))
    for j in range(32):
        for k in range(8):a=j*9+k;sf.append((a,a+1,a+10,a+9))
    tail=mesh('Tucked free end interface',sv,sf,cloth);solid=tail.modifiers.new('Fabric thickness','SOLIDIFY');solid.thickness=.002
    # Skull articulation with a continuous, spatially weighted neck blend.
    rigdata=bpy.data.armatures.new('Head study rig');rig=bpy.data.objects.new('Head study rig',rigdata);bpy.context.collection.objects.link(rig)
    bpy.context.view_layer.objects.active=rig;rig.select_set(True);bpy.ops.object.mode_set(mode='EDIT')
    for name,h,t,parent in [('root',(0,.02,-.5),(0,.02,-.3),None),('neck',(0,.02,-.3),(0,.015,-.12),'root'),('head',(0,.015,-.12),(0,.015,.42),'neck')]:
        b=rigdata.edit_bones.new(name);b.head=h;b.tail=t
        if parent:b.parent=rigdata.edit_bones[parent]
    bpy.ops.object.mode_set(mode='OBJECT');groups={n:body.vertex_groups.new(name=n) for n in ('root','neck','head')}
    for v in body.data.vertices:
        p=v.co;h=max(0,min(1,(p.z+.22)/.15))
        if p.y<-.10 and p.z>-.20:h=1
        w=(1-h)*max(0,min(1,(p.z+.47)/.16))
        for n,a in [('head',h),('neck',w),('root',1-h-w)]:
            if a:groups[n].add([v.index],a,'REPLACE')
    mod=body.modifiers.new('Distributed neck articulation','ARMATURE');mod.object=rig;mod.use_deform_preserve_volume=True
    master=bpy.data.objects.new('Skull attachment',None);bpy.context.collection.objects.link(master)
    for ob in list(bpy.context.scene.objects):
        if ob in {body,master} or ob.parent or ob.type not in {'MESH','CURVE','EMPTY'}:continue
        ob.parent=master
    for f,yaw,pitch in [(1,0,0),(24,0,0),(52,12,-4),(70,12,-4),(94,8,8),(108,7,9),(130,0,0),(144,0,0)]:
        for n,portion in [('neck',.3),('head',.7)]:
            b=rig.pose.bones[n];b.rotation_mode='XYZ';b.rotation_euler=(math.radians(pitch)*portion,math.radians(yaw)*portion,0);b.keyframe_insert('rotation_euler',frame=f)
    # Exact sampled skull transform avoids bone-tail parent offsets and keyed
    # gaze Euler channels overwriting the compensation rotation on an empty.
    master.rotation_mode='QUATERNION'
    for f in range(1,145):
        bpy.context.scene.frame_set(f);bpy.context.view_layer.update()
        master.matrix_world=rig.matrix_world@rig.pose.bones['head'].matrix@rig.data.bones['head'].matrix_local.inverted()
        for prop in ('location','rotation_quaternion','scale'):master.keyframe_insert(prop,frame=f)
    scene=bpy.context.scene;scene.frame_start=1;scene.frame_end=144;scene.render.fps=24;scene.frame_set(1)
    scene.cycles.samples=20;scene.render.resolution_x=640;scene.render.resolution_y=800
    scene.view_settings.view_transform='AgX';scene.world.color=(.13,.13,.13)
    cam=scene.camera;cam.data.ortho_scale=1.32;target=(0,0,.07)
    for lname,pos,power,size in [('Key',(-1,-1.6,1.3),90,1.2),('Fill',(1,-1,.4),42,1.5)]:
        ob=bpy.data.objects[lname];ob.data.energy=power;ob.data.size=size;aim(ob,pos,target)
    def render(name,pos,frame=1):
        scene.frame_set(frame);aim(cam,pos,target)
        direction=(Vector(pos)-Vector(target)).normalized();right=direction.cross(Vector((0,0,1))).normalized()
        for lname,x,z,power in [('Key',-.9,1.1,90),('Fill',1,.3,24)]:
            ob=bpy.data.objects[lname];ob.data.energy=power;ob.data.size=.5 if lname=='Key' else 1.5;aim(ob,Vector(target)+direction*1.5+right*x+Vector((0,0,z)),target)
        scene.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True)
    for name,pos in [('front',(0,-3,.12)),('left',(-1.65,-3,.15)),('right',(1.65,-3,.15)),('rear',(0,3,.18)),('profile',(3,-.15,.14))]:render(name,pos)
    render('recognition',(1,-3,.15),70);render('bow',(1,-3,.15),108)
    if attempt>=9:
        scene.frame_set(1);aim(cam,(1,-3,.15),target)
        key=bpy.data.objects['Key'];fill=bpy.data.objects['Fill'];key.data.color=(.62,.74,1);key.data.energy=100;fill.data.energy=12
        scene.render.filepath=str(out/'moonlight.png');bpy.ops.render.render(write_still=True)
        key.data.color=(1,1,1);key.data.energy=90;fill.data.energy=24
    scene.frame_set(1);aim(cam,(.65,-3,.15),target)
    samples=snapshot();bpy.ops.wm.save_as_mainfile(filepath=str(out/'head.blend'))
    (out/'build.json').write_text(json.dumps({'native_sha256':sha(out/'head.blend'),'samples':samples,'beard_strands':sum(map(len,paths)),'status':'INTERNAL_NOT_DIRECTOR_ADMITTED','source_hashes':{str(p.relative_to(ROOT)):v for p,v in EXPECTED.items()}},indent=2))

def launch(job,prepare=False):
    out=validate(job);p=packet(job)
    if prepare:print(p['packet_digest']);return
    out.mkdir(parents=True,exist_ok=True);log=out/(job['operation']+'.log')
    if log.exists():raise ValueError('Preserve prior run')
    import shutil
    shutil.copy2(__file__,out/(job['operation']+'-handler.py'))
    env={k:os.environ[k] for k in ('PATH','HOME','TMPDIR','LANG','LC_ALL') if k in os.environ};start=time.monotonic()
    with log.open('w') as h:r=subprocess.run(['/Applications/Blender.app/Contents/MacOS/Blender','--background','--offline-mode','--factory-startup','--disable-autoexec','--python-exit-code','7','--python',str(Path(__file__).resolve()),'--',json.dumps(job)],env=env,stdout=h,stderr=subprocess.STDOUT)
    (out/(job['operation']+'-receipt.json')).write_text(json.dumps({'seconds':time.monotonic()-start,'returncode':r.returncode,'packet_digest':p['packet_digest']},indent=2))
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
