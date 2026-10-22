"""Fixed, local-only accepted-bust inventory and whole-character prototype.

Jobs select reviewed operations, never paths or executable expressions.
"""
import hashlib
import json
import math
from pathlib import Path
import shutil
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / '.runtime/art-direction/series01-facebuilder-trial-01'
SOURCE = BASE / 'natural152-seal-16/natural-hair.blend'
SOURCE_SHA = '9a204ec2e3951274aeff52aeb554de6b8bc7fa169933e27bfea7073bb62f323f'
DONORS = {
    'dressing': (BASE / 'dressing-motion-build-04/character-dressed.blend',
                 '77fa1fad9da232a6af156f0f62b1a3fd994f4aa28e89011643ea74574e77526e'),
    'knight': (ROOT / '.runtime/assets/demonstrator-01/Knight_0.blend',
               'd7461ba21f3d5768e4f8a782ac4e5283eac73fdb991e44fddeb5cb487c045e0c'),
}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(job):
    if not isinstance(job, dict) or set(job) != {'operation'} or job['operation'] not in ('inventory', 'prototype01', 'prototype02', 'prototype03', 'prototype04', 'assembly05', 'assembly06', 'assembly07'):
        raise ValueError('Only fixed operations admitted')
    for path, expected in [(SOURCE, SOURCE_SHA), *DONORS.values()]:
        if path.is_symlink() or digest(path) != expected:
            raise ValueError('Pinned source mismatch')
    out = BASE / ('body154-' + job['operation'])
    if out.exists() or shutil.disk_usage(BASE).free < 5_000_000_000:
        raise ValueError('Existing output or low disk')
    return out


def inventory():
    import bpy
    from mathutils import Vector
    rows = []
    bpy.context.view_layer.update()
    for ob in bpy.context.scene.objects:
        bounds = [ob.matrix_world @ Vector(c) for c in ob.bound_box]
        rows.append({'name': ob.name, 'type': ob.type, 'hidden_render': ob.hide_render,
                     'parent': ob.parent.name if ob.parent else None,
                     'bounds': [[min(c[i] for c in bounds) for i in range(3)],
                                [max(c[i] for c in bounds) for i in range(3)]],
                     'materials': [m.name if m else None for m in getattr(ob.data, 'materials', [])],
                     'shape_keys': list(ob.data.shape_keys.key_blocks.keys()) if getattr(ob.data, 'shape_keys', None) else [],
                     'bones': list(ob.data.bones.keys()) if ob.type == 'ARMATURE' else [],
                     'modifiers': [(m.name, m.type) for m in ob.modifiers],
                     'vertices': len(ob.data.vertices) if ob.type == 'MESH' else None})
    return rows


def mesh(name, verts, faces, material):
    import bpy
    data = bpy.data.meshes.new(name)
    data.from_pydata(verts, [], faces)
    data.update()
    ob = bpy.data.objects.new(name, data)
    bpy.context.scene.collection.objects.link(ob)
    data.materials.append(material)
    for p in data.polygons:
        p.use_smooth = True
    return ob


def material(name, color):
    import bpy
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value = (*color, 1)
    bsdf.inputs['Roughness'].default_value = .78
    return m


def tube(name, rings, mat, detail=40, folds=0.):
    """Authored cross-sections: center xyz, width and depth; no runtime code."""
    verts = []
    for j, (x, y, z, width, depth) in enumerate(rings):
        for i in range(detail):
            t = 2*math.pi*i/detail
            f = folds*math.sin(t*7 + .35*j)*math.sin(math.pi*j/(len(rings)-1))
            verts.append((x+(width+f)*math.cos(t), y+(depth+f*.5)*math.sin(t), z))
    faces = []
    for j in range(len(rings)-1):
        for i in range(detail):
            a = j*detail+i; b = j*detail+(i+1)%detail
            faces.append((a, b, b+detail, a+detail))
    ob = mesh(name, verts, faces, mat)
    sub = ob.modifiers.new('Coarse cloth continuity', 'SUBSURF')
    sub.levels = 2
    return ob


def protected():
    """Capture accepted data without invoking historical mutation-based checks."""
    import bpy
    from hijab_donor import material_signature
    result = {}
    for ob in bpy.context.scene.objects:
        if ob.hide_render or ob.type not in ('MESH', 'CURVES'):
            continue
        if ob.type == 'MESH':
            coords = [tuple(v.co) for v in ob.data.vertices]
            extra = {k.name: [tuple(v.co) for v in k.data] for k in ob.data.shape_keys.key_blocks} if ob.data.shape_keys else {}
        else:
            coords = [tuple(v.position) for v in ob.data.points]
            extra = {'counts': [len(c.points) for c in ob.data.curves]}
        result[ob.name] = hashlib.sha256(json.dumps([coords, extra, [material_signature(m) for m in ob.data.materials if m]], sort_keys=True).encode()).hexdigest()
    return result


def prototype(out, variant):
    import bpy
    from mathutils import Vector
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE), load_ui=False, use_scripts=False)
    before = protected()
    keep = ['MF_upper_tunic', 'MF_loose_tunic_sleeve_-1', 'MF_loose_tunic_sleeve_1',
            'MF_reference_shoulder_harness_-1', 'MF_reference_shoulder_harness_1',
            'MF_tunic_shoulder_underlayer']
    for name in keep:
        ob = bpy.data.objects[name]; ob.hide_render = False; ob.hide_set(False)
    pants = material('MF_body154_dark_indigo', (.027, .045, .068))
    leather = material('MF_body154_boot_leather', (.055, .028, .017))
    cloth = bpy.data.materials['MF_indigo_tunic']
    skin = material('MF_body154_hand_proxy', (.38, .19, .105))
    # Existing torso ends at upper thigh; overlap lower divided panels.
    for side in (-1, 1):
        tube(f'MF_body154_trouser_{side}', [(side*.68,.20,-4.65,.71,.67),
             (side*.74,.22,-5.1,.74,.69), (side*.79,.19,-6.1,.72,.64),
             (side*.84,.14,-7.1,.65,.58), (side*.85,.10,-8.0,.52,.45),
             (side*.85,.09,-8.8,.34,.34), (side*.85,.08,-9.12,.32,.32)], pants, folds=.06)
        tube(f'MF_body154_boot_{side}', [(side*.85,.08,-8.45,.34,.34),
             (side*.85,.08,-8.55,.38,.37), (side*.85,.07,-9.25,.35,.36),
             (side*.85,.02,-9.95,.27,.28), (side*.85,-.14,-10.2,.33,.48),
             (side*.85,-.23,-10.5,.35,.63), (side*.85,-.23,-10.61,.35,.63)], leather)
        # Relaxed coarse hands with separate tapered digits, not a final grip rig.
        x = side*2.02
        tube(f'MF_body154_palm_{side}', [(x,.20,-5.13,.20,.17),
             (x,.18,-5.4,.24,.16), (x,.12,-5.72,.23,.13),
             (x,.10,-5.86,.18,.11)], skin, 24)
        for f in range(4):
            fx = x + (f-1.5)*.105
            length = [.35,.46,.43,.32][f]
            tube(f'MF_body154_finger_{side}_{f}', [(fx,.10,-5.76,.064,.095),
                 (fx,.06,-5.89,.061,.078), (fx,.02,-5.85-length,.045,.055),
                 (fx,.02,-5.88-length,.012,.017)], skin, 12)
        tube(f'MF_body154_thumb_{side}', [(x-side*.18,.08,-5.38,.095,.10),
             (x-side*.30,-.01,-5.58,.075,.08), (x-side*.31,-.08,-5.80,.025,.03)], skin, 16)
    # Shoulder-draped scarf: broad asymmetrical cloth, no analytical cowl rings.
    verts=[]; faces=[]; rows=38; cols=44
    for j in range(rows):
        t=j/(rows-1)
        for i in range(cols):
            u=i/(cols-1); a=-math.pi*.20+u*math.pi*1.40
            width=1.50+.55*t
            x=width*math.cos(a)
            y=.17+(1.00+.10*t)*math.sin(a)
            z=-1.45-3.35*t + .20*math.sin(a+.4)*t
            # Large supported vertical folds decay into the shoulder attachment.
            ripple=.08*math.sin(6*a+2*t)*math.sin(t*math.pi*.85)
            x+=math.cos(a)*ripple; y+=math.sin(a)*ripple
            verts.append((x,y,z))
    for j in range(rows-1):
        for i in range(cols-1):
            a=j*cols+i; faces.append((a,a+1,a+1+cols,a+cols))
    shawl=mesh('MF_body154_open_shoulder_shawl',verts,faces,cloth)
    shawl.modifiers.new('Cloth thickness','SOLIDIFY').thickness=.035
    sub=shawl.modifiers.new('Broad fold continuity','SUBSURF'); sub.levels=2
    # Waist belt gives a readable termination for the existing shoulder straps.
    tube('MF_body154_waist_belt',[(0,.20,-4.53,1.47,.83),
         (0,.20,-4.58,1.49,.85),(0,.20,-4.82,1.49,.85),(0,.20,-4.88,1.47,.83)],leather)
    if variant >= 3:
        shawl.hide_render=True
        for name in ('MF_upper_tunic','MF_tunic_shoulder_underlayer','MF_body154_waist_belt'):
            bpy.data.objects[name].hide_render=True
        body=tube('MF_body154_long_tunic',[(0,.18,-1.32,.64,.57),
             (0,.18,-1.51,1.18,.65),(0,.18,-1.76,1.69,.73),
             (0,.18,-2.45,1.58,.86),(0,.18,-3.35,1.36,.80),
             (0,.18,-4.20,1.20,.75),(0,.18,-5.05,1.49,.79),
             (0,.18,-5.8,1.60,.85),(0,.18,-6.45,1.68,.87),
             (0,.18,-6.65,1.67,.86)],cloth,folds=.05)
        body.modifiers.new('Tunic thickness','SOLIDIFY').thickness=.025
        # Open side slits below the hip: a long closed tube cannot straddle a saddle.
        import bmesh
        bm=bmesh.new(); bm.from_mesh(body.data)
        bmesh.ops.delete(bm,geom=[f for f in bm.faces if f.calc_center_median().z < -5.0 and abs(f.calc_center_median().x)>1.25],context='FACES')
        bm.to_mesh(body.data);bm.free()
        scarf=bpy.data.objects['MF_layered_upper_scarf'];scarf.hide_render=False;scarf.hide_set(False)
        hood=bpy.data.objects['MF_adapted_donor_hood'];hood.hide_render=False;hood.hide_set(False)
        # Cloth changes only: increase back/crown clearance around accepted hair.
        for modifier in list(hood.modifiers):
            if modifier.type=='SHRINKWRAP':hood.modifiers.remove(modifier)
        for v in hood.data.vertices:
            v.co.x*=1.10
            v.co.y=.2+(v.co.y-.2)*1.24
            v.co.z+=.17*max(0.,min(1.,(v.co.z+1.0)/2.3))
        hood.data.update()
        for side in (-1,1):
            ob=bpy.data.objects[f'MF_body154_trouser_{side}']
            for v in ob.data.vertices:
                w=max(0.,min(1.,(-v.co.z-7.65)/.65))
                v.co.x=side*.85+(v.co.x-side*.85)*(1-.23*w)
                v.co.y=.08+(v.co.y-.08)*(1-.23*w)
            ob.data.update()
            harness=bpy.data.objects[f'MF_reference_shoulder_harness_{side}']
            harness.data.materials.clear();harness.data.materials.append(leather)
    def continuous_garments():
        bpy.data.objects['MF_body154_diagonal_shawl'].hide_render=True
        for side in (-1,1):bpy.data.objects[f'MF_reference_shoulder_harness_{side}'].hide_render=True
        hood=bpy.data.objects['MF_adapted_donor_hood']
        for v in hood.data.vertices:
            rear=max(0.,min(1.,(v.co.y-.35)/.6))
            upper=max(0.,min(1.,(v.co.z+.5)/1.2))
            v.co.y+=.46*rear*upper;v.co.z+=.14*rear*upper
        hood.data.update()
        # One continuous shoulder wrap eliminates floating cut-off panel ends.
        vv=[];ff=[]; na=96; nw=18
        for i in range(na):
            a=2*math.pi*i/na
            for j in range(nw):
                t=j/(nw-1)
                z=-1.90+.42*math.cos(a)-.12*math.sin(a)-1.12*t
                rx=1.73+.09*math.sin(math.pi*t)
                ry=1.05+.075*math.sin(3*math.pi*t+.4*math.cos(a))
                vv.append((rx*math.cos(a),.18+ry*math.sin(a),z))
        for i in range(na):
            for j in range(nw-1):
                a=i*nw+j;b=((i+1)%na)*nw+j;ff.append((a,b,b+1,a+1))
        wrap=mesh('MF_body154_continuous_shawl',vv,ff,cloth)
        wrap.modifiers.new('Continuous drape','SUBSURF').levels=2
        wrap.modifiers.new('Fabric thickness','SOLIDIFY').thickness=.025
        # Smooth closed shoulder-to-opposite-hip harness loops, intentionally
        # simpler than old fitted strips whose local surface hits kinked.
        from mathutils import Vector
        for side in (-1,1):
            anchors=[(1.45,-.56,-1.72),(1.08,-1.18,-2.3),(.35,-1.20,-3.2),
                     (-.60,-1.08,-4.1),(-1.30,-.62,-4.8),(-1.34,.30,-4.84),
                     (-1.15,.99,-4.55),(-.20,1.13,-3.4),(1.15,1.02,-2.0),(1.48,.50,-1.69)]
            anchors=[Vector((side*x,y,z)) for x,y,z in anchors]
            points=[]
            for j in range(len(anchors)):
                p0,p1,p2,p3=[anchors[k%len(anchors)] for k in (j-1,j,j+1,j+2)]
                for k in range(12):
                    t=k/12
                    points.append(.5*((2*p1)+(-p0+p2)*t+(2*p0-5*p1+4*p2-p3)*t*t+(-p0+3*p1-3*p2+p3)*t*t*t))
            vertices=[];faces=[]
            for j,p in enumerate(points):
                tangent=(points[(j+1)%len(points)]-points[j-1]).normalized()
                outward=Vector((p.x,p.y-.18,0)).normalized()
                across=tangent.cross(outward).normalized()*.13
                vertices.extend([tuple(p-across),tuple(p+across)])
            for j in range(len(points)):
                a=2*j;b=2*((j+1)%len(points));faces.append((a,b,b+1,a+1))
            ob=mesh(f'MF_body154_harness_{side}',vertices,faces,leather)
            ob.modifiers.new('Leather thickness','SOLIDIFY').thickness=.028
            ob.modifiers.new('Rounded edges','BEVEL').width=.015
            harness=bpy.data.objects[f'MF_reference_shoulder_harness_{side}']
            harness.data.materials.clear();harness.data.materials.append(leather)
    if variant >= 4:
        bpy.data.objects['MF_layered_upper_scarf'].hide_render=True
        hood=bpy.data.objects['MF_adapted_donor_hood']
        for v in hood.data.vertices:
            top=max(0.,min(1.,(v.co.z+.5)/1.8))
            v.co.z+=.22*top
            v.co.y+=.22*top*max(0.,min(1.,(v.co.y+.1)/.9))
        hood.data.update()
        # Broad diagonal shoulder wrap, not a narrow horizontal neck ring.
        vertices=[];polygons=[]; nu=48; nv=18
        for i in range(nu):
            u=i/(nu-1);x=-1.65+3.30*u
            top=-2.70+1.13*u
            for j in range(nv):
                v=j/(nv-1)
                z=top-v*(.85+.25*math.sin(math.pi*u))
                y=-.76-.25*math.sin(math.pi*u)-.07*math.sin(v*math.pi*3+.6*u)
                vertices.append((x,y,z))
        for i in range(nu-1):
            for j in range(nv-1):
                a=i*nv+j;polygons.append((a,a+nv,a+nv+1,a+1))
        wrap=mesh('MF_body154_diagonal_shawl',vertices,polygons,cloth)
        wrap.modifiers.new('Soft fold continuity','SUBSURF').levels=2
        wrap.modifiers.new('Woven cloth thickness','SOLIDIFY').thickness=.026
        # Replace square legacy neckline with a low curved opening around the bust.
        for v in bpy.data.objects['MF_body154_long_tunic'].data.vertices:
            if v.co.z> -1.8:
                top=max(0.,min(1.,(v.co.z+1.8)/.48))
                v.co.z-=.22*top*max(0.,-(v.co.y-.18)/.57)
        belt=tube('MF_body154_fitted_waist_belt',[(0,.18,-4.66,1.40,.86),
             (0,.18,-4.7,1.42,.88),(0,.18,-4.95,1.46,.89),(0,.18,-4.99,1.44,.87)],leather)
        # Fit continuous old strap paths to the new visible assembly, not skin.
        from mathutils.bvhtree import BVHTree
        bpy.context.view_layer.update()
        dg=bpy.context.evaluated_depsgraph_get(); vv=[]; ff=[]
        for name in ['MF_body154_long_tunic','MF_body154_diagonal_shawl','MF_loose_tunic_sleeve_-1','MF_loose_tunic_sleeve_1']:
            ob=bpy.data.objects[name];ev=ob.evaluated_get(dg);me=ev.to_mesh();offset=len(vv)
            vv.extend(ob.matrix_world@v.co for v in me.vertices)
            ff.extend(tuple(offset+i for i in p.vertices) for p in me.polygons)
            ev.to_mesh_clear()
        tree=BVHTree.FromPolygons(vv,ff)
        for side in (-1,1):
            ob=bpy.data.objects[f'MF_reference_shoulder_harness_{side}']
            for v in ob.data.vertices:
                if v.co.z < -4.2:v.co.z=-4.2+(v.co.z+4.2)*.62
                pos=ob.matrix_world@v.co;center=Vector((0,.18,pos.z));direction=pos-center;direction.z=0
                if direction.length>.1:
                    direction.normalize();hit,n,_,_=tree.ray_cast(center+direction*5,-direction,7)
                    if hit is not None and pos.z < -1.9:
                        v.co=ob.matrix_world.inverted()@(hit+direction*.055)
            ob.data.update()
    if variant >= 5:
        continuous_garments()
    if variant >= 7:
        # Flat-material diagnostic: persistence of rear dark patches in07
        # establishes that those remaining marks are geometric intersections.
        hood=bpy.data.objects['MF_adapted_donor_hood']
        hood.data.materials.clear();hood.data.materials.append(cloth)
    # Native preview setup, ordinary-size whole character, not beauty lighting.
    scene=bpy.context.scene
    for ob in scene.objects:
        if ob.type=='LIGHT': ob.hide_render=True
    camera=bpy.data.objects.new('MF_body154_camera',bpy.data.cameras.new('MF_body154_camera'))
    scene.collection.objects.link(camera); scene.camera=camera; camera.data.type='ORTHO'
    scene.render.engine='CYCLES'; scene.cycles.samples=16; scene.cycles.seed=0
    scene.cycles.use_denoising=True
    scene.render.resolution_x=432; scene.render.resolution_y=768; scene.render.resolution_percentage=100
    lights=[]
    for x,power in ((-6,1800),(6,1200)):
        light=bpy.data.objects.new('MF_body154_softbox',bpy.data.lights.new('MF_body154_softbox','AREA'))
        scene.collection.objects.link(light); light.data.energy=power; light.data.shape='DISK'; light.data.size=8
        lights.append((light,Vector((x,-7,6))))
    def render(label,angle,center=(0,0,-4.4),scale=13.4):
        from mathutils import Matrix
        target=Vector(center); rot=Matrix.Rotation(math.radians(angle),3,'Z')
        camera.data.ortho_scale=scale
        camera.location=target+rot@Vector((0,-24,1))
        camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler()
        for light,offset in lights:
            light.location=target+rot@offset
            light.rotation_euler=(target-light.location).to_track_quat('-Z','Y').to_euler()
        scene.render.filepath=str(out/(label+'.png')); bpy.ops.render.render(write_still=True)
    for label, angle in [('front',0),('left',-45),('right',45),('back',180)]: render(label,angle)
    render('medium',-15,(0,0,-1.70),7.0)
    now=protected()
    assert all(now[k]==v for k,v in before.items()), 'Accepted geometry/material changed'
    bpy.context.preferences.filepaths.save_version=0
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'character-prototype.blend'),check_existing=False)
    if variant>=7:
        riding_pose()
        # A neutral saddle/body proxy is sufficient for clearance screening;
        # not the accepted horse or a proof of its proportions/contacts.
        proxy=material('MF_body154_saddle_proxy',(.11,.105,.10))
        bpy.ops.mesh.primitive_uv_sphere_add(segments=32,ring_count=16,location=(0,.10,-6.0))
        saddle=bpy.context.object;saddle.name='MF_body154_saddle_body_proxy';saddle.scale=(1.28,2.4,.88);saddle.data.materials.append(proxy)
        render('riding-left',-65,(0,-.9,-4.1),11.0)
        render('riding-front',0,(0,-.9,-4.1),11.0)
        after=protected();assert all(after[k]==v for k,v in before.items())
        bpy.ops.wm.save_as_mainfile(filepath=str(out/'riding-pose-proxy.blend'),check_existing=False)
    (out/'result.json').write_text(json.dumps({'status':'STATIC_DESIGN_PROTOTYPE_NOT_ACCEPTED',
       'protected':before,'protected_preserved':True,'source_sha256':SOURCE_SHA,
       'native_sha256':digest(out/'character-prototype.blend'),
       'rig':'NOT_IMPLEMENTED','riding_pose':'STATIC_PROXY_ONLY' if variant>=7 else 'NOT_RUN','paid_calls':0},indent=2)+'\n')


def riding_pose():
    """Piecewise static pose screen, explicitly not a rig/animation solution."""
    import bpy
    from mathutils import Vector, Matrix
    pivot=Vector((0,.18,-4.85))
    lean=Matrix.Translation(pivot)@Matrix.Rotation(math.radians(25),4,'X')@Matrix.Translation(-pivot)
    # Preserve all original local data. The accepted head/hair hierarchy moves
    # as a whole; no facial, neck or hair geometry edit is needed for this test.
    roots=[o for o in bpy.context.scene.objects if o.parent is None and o.type not in ('CAMERA','LIGHT')]
    for ob in roots:ob.matrix_world=lean@ob.matrix_world
    bpy.context.view_layer.update()
    for side in (-1,1):
        hip=Vector((side*.74,.2,-5.2));knee=Vector((side*.85,.1,-7.9))
        knee_new=Vector((side*1.52,-1.65,-6.85));ankle_new=Vector((side*1.45,-.72,-8.82))
        thigh_rot=Vector((0,0,-1)).rotation_difference((knee_new-hip).normalized())
        shin_rot=Vector((0,0,-1)).rotation_difference((ankle_new-knee_new).normalized())
        for name in (f'MF_body154_trouser_{side}',f'MF_body154_boot_{side}'):
            ob=bpy.data.objects[name];ob.matrix_world=Matrix.Identity(4)
            for v in ob.data.vertices:
                old=v.co.copy();w=max(0.,min(1.,(-old.z-7.65)/.50))
                upper=hip+thigh_rot@(old-hip);lower=knee_new+shin_rot@(old-knee)
                v.co=upper.lerp(lower,w)
            ob.data.update()
        shoulder=Vector((side*1.55,.2,-1.8));elbow=Vector((side*2.0,.2,-3.65))
        wrist=Vector((side*2.02,.15,-5.28));shoulder_new=lean@shoulder
        elbow_new=Vector((side*1.68,-1.90,-3.85));wrist_new=Vector((side*.86,-3.12,-4.36))
        upper_rot=(elbow-shoulder).normalized().rotation_difference((elbow_new-shoulder_new).normalized())
        lower_rot=(wrist-elbow).normalized().rotation_difference((wrist_new-elbow_new).normalized())
        names=[f'MF_loose_tunic_sleeve_{side}',f'MF_body154_palm_{side}',f'MF_body154_thumb_{side}']
        names += [f'MF_body154_finger_{side}_{f}' for f in range(4)]
        for name in names:
            ob=bpy.data.objects[name];ob.matrix_world=Matrix.Identity(4)
            for v in ob.data.vertices:
                old=v.co.copy();w=max(0.,min(1.,(-old.z-3.4)/.5))
                v.co=(shoulder_new+upper_rot@(old-shoulder)).lerp(elbow_new+lower_rot@(old-elbow),w)
            ob.data.update()
    # Lower tunic panels spread at the hips, rather than crossing the saddle.
    tunic=bpy.data.objects['MF_body154_long_tunic']
    for v in tunic.data.vertices:
        w=max(0.,min(1.,(-v.co.z-4.9)/1.5))
        v.co.x*=1+.25*w
        if v.co.y<.18:v.co.y-=.8*w
    tunic.data.update()


def main():
    import bpy
    job = json.loads(Path(sys.argv[sys.argv.index('--') + 1]).read_text())
    out = validate(job)
    out.mkdir()
    if job['operation'].startswith(('prototype','assembly')):
        prototype(out, int(job['operation'][-2:]))
        return
    result = {}
    for name, (path, sha) in {'accepted': (SOURCE, SOURCE_SHA), **DONORS}.items():
        bpy.ops.wm.open_mainfile(filepath=str(path), load_ui=False, use_scripts=False)
        result[name] = {'source_sha256': sha, 'objects': inventory()}
    (out / 'inventory.json').write_text(json.dumps(result, indent=2) + '\n')


if __name__ == '__main__':
    main()
