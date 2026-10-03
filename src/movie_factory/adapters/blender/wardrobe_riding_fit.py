"""Fixed private costume/actual-tack fit on Director-accepted body66.

Only reviewed operation names are admitted; no paths/code from a model job.
"""
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from character_assembly import BASE, ROOT, digest, inventory

BODY = BASE / 'body168-hip66/adult-body-fit.blend'
BODY_SHA = '1ed613b16dc5b618ae601b9645f6042927e036f60f74314a31fc07e3c5e5c327'
HORSE = ROOT / 'runs/demonstrator-01/cut-world-v4/scene.blend'
HORSE_SHA = '7248f9dfecef3e9ece309c08055ab53ee6d802abe0a0e01307c7f9d8b93fd73e'


def validate(job):
    if not isinstance(job, dict) or set(job) != {'operation'} or job['operation'] not in ('inspect01', 'inspect02', 'inspect03', 'inspect04', 'preview01', 'preview02', 'preview03', 'preview04', 'preview05', 'preview06', 'preview07', 'preview08', 'preview09', 'preview10', 'preview11', 'preview12', 'preview13', 'finger14', 'finger16', 'finger17', 'finger18', 'preview15', 'preview19', 'preview20', 'preview21', 'preview22', 'preview23', 'cloth24', 'preview25', 'preview26', 'pose27', 'preview28', 'seal01', 'verify01'):
        raise ValueError('Only fixed reviewed operations admitted')
    for path, sha in ((BODY, BODY_SHA), (HORSE, HORSE_SHA)):
        if path.is_symlink() or not path.is_file() or digest(path) != sha:
            raise ValueError('Pinned fit input mismatch')
    if job['operation']=='verify01':
        result=json.loads((BASE/'wardrobe169-seal01/result.json').read_text())
        native=BASE/'wardrobe169-seal01/dressed-fit.blend'
        if native.is_symlink() or digest(native)!=result['native_sha256']:
            raise ValueError('Selected native mismatch')
    out = BASE / ('wardrobe169-' + job['operation'])
    if out.exists():
        raise ValueError('Never overwrite fit evidence')
    return out


def inspect(out):
    import bpy
    from mathutils import Matrix
    bpy.ops.wm.open_mainfile(filepath=str(BODY), load_ui=False, use_scripts=False)
    body = bpy.data.objects['MF_studio_adult_body']
    rig = bpy.data.objects['MF_body156_fit_rig']
    result = {'body_source': BODY_SHA, 'horse_source': HORSE_SHA,
              'body_inventory': inventory(),
              'body_bones': {b.name: {'head': list(b.head_local), 'tail': list(b.tail_local)} for b in rig.data.bones},
              'body_materials': [m.name for m in body.data.materials]}
    recipe = json.loads((BODY.parent / 'result.json').read_text())['pose_screen']['pose_matrices']
    for n, m in recipe.items():
        rig.pose.bones[n].matrix_basis = Matrix(m)
    bpy.context.view_layer.update()
    result['seated_bones'] = {b.name: {'head': list(b.head), 'tail': list(b.tail)} for b in rig.pose.bones}
    bpy.ops.wm.open_mainfile(filepath=str(HORSE), load_ui=False, use_scripts=False)
    bpy.context.scene.frame_set(0)
    result['horse_inventory'] = [r for r in inventory() if any(s in r['name'].lower() for s in ('horse', 'saddle', 'rein', 'bridle', 'stirrup', 'torus'))]
    result['horse_bones'] = {b.name: {'head': list(b.head), 'tail': list(b.tail)} for b in bpy.data.objects['horse.rig'].pose.bones if any(k in b.name for k in ('torso', 'head', 'neck'))}
    result['source_unchanged'] = digest(BODY) == BODY_SHA and digest(HORSE) == HORSE_SHA
    (out / 'inventory.json').write_text(json.dumps(result, indent=2) + '\n')


def main():
    job = json.loads(Path(sys.argv[sys.argv.index('--') + 1]).read_text())
    out = validate(job)
    out.mkdir()
    if job['operation'] == 'inspect01':
        inspect(out)
    elif job['operation']=='inspect02':
        inspect_hands(out)
    elif job['operation']=='inspect03':
        inspect_grip_evaluation(out)
    elif job['operation']=='inspect04':
        inspect_finger_weights(out)
    elif job['operation']=='verify01':
        verify(out)
    else:
        build(out, job['operation'])


def aim(rig, name, direction):
    from mathutils import Vector
    bone = rig.pose.bones[name]
    q = (bone.tail - bone.head).normalized().rotation_difference(Vector(direction).normalized())
    matrix = q.to_matrix().to_4x4() @ bone.matrix
    matrix.translation = bone.head
    bone.matrix = matrix
    import bpy
    bpy.context.view_layer.update()


def inspect_finger_weights(out):
    import bpy
    bpy.ops.wm.open_mainfile(filepath=str(BODY),load_ui=False,use_scripts=False)
    body=bpy.data.objects['MF_studio_adult_body'];rig=bpy.data.objects['MF_body156_fit_rig']
    names=install_fingers(body,rig);riding_pose(rig)
    rows={}
    for n in names:
        group=body.vertex_groups[n]
        weights=[(v.index,g.weight) for v in body.data.vertices for g in v.groups if g.group==group.index]
        b=rig.pose.bones[n]
        rows[n]={'count':len(weights),'weight_sum':sum(w for _,w in weights),'deform':b.bone.use_deform,'head':list(b.head),'tail':list(b.tail),'samples':weights[:3]}
    (out/'finger-weights.json').write_text(json.dumps(rows,indent=2)+'\n')


def inspect_hands(out):
    import bpy
    bpy.ops.wm.open_mainfile(filepath=str(BODY),load_ui=False,use_scripts=False)
    body=bpy.data.objects['MF_studio_adult_body'];rig=bpy.data.objects['MF_body156_fit_rig'];rows={}
    for side in ('L','R'):
        bone=rig.data.bones['hand.'+side];group=body.vertex_groups['hand.'+side].index
        axis=(bone.tail_local-bone.head_local).normalized()
        points=[]
        for v in body.data.vertices:
            w=next((g.weight for g in v.groups if g.group==group),0.)
            if w>.1:points.append({'i':v.index,'p':list(v.co),'w':w,'t':(v.co-bone.head_local).dot(axis)})
        rows[side]={'head':list(bone.head_local),'tail':list(bone.tail_local),'points':points}
    (out/'hands.json').write_text(json.dumps(rows)+'\n')


def inspect_grip_evaluation(out):
    import bpy,numpy as np
    bpy.ops.wm.open_mainfile(filepath=str(BODY),load_ui=False,use_scripts=False)
    body=bpy.data.objects['MF_studio_adult_body'];rig=bpy.data.objects['MF_body156_fit_rig']
    for mod in body.modifiers:
        if mod.type=='SUBSURF':mod.show_viewport=False
    grip=authored_grip(body,rig);riding_pose(rig)
    names=['MF_studio_adult_body'];grip.value=0.;bpy.context.view_layer.update();zero=evaluated_surfaces(names)[body.name]
    grip.value=1.;bpy.context.view_layer.update();one=evaluated_surfaces(names)[body.name]
    basis=body.data.shape_keys.key_blocks['Basis']
    ids=[v.index for v in body.data.vertices if any(body.vertex_groups[g.group].name=='hand.L' and g.weight>.5 for g in v.groups)]
    raw=np.array([grip.data[i].co[:] for i in ids])-np.array([basis.data[i].co[:] for i in ids])
    mesh_basis=np.array([body.data.vertices[i].co[:] for i in ids])-np.array([basis.data[i].co[:] for i in ids])
    result={'value':grip.value,'relative_key':grip.relative_key.name,'raw_max_delta':float(np.max(np.abs(raw))),
            'evaluated_max_delta':float(np.max(np.abs(one[ids]-zero[ids]))),
            'mesh_vs_basis_max_delta':float(np.max(np.abs(mesh_basis))),
            'modifiers':[(m.name,m.type,m.vertex_group if hasattr(m,'vertex_group') else None) for m in body.modifiers]}
    (out/'evaluation.json').write_text(json.dumps(result,indent=2)+'\n')


def riding_pose(rig, strength=1.):
    import bpy
    from mathutils import Matrix
    for b in rig.pose.bones:
        b.matrix_basis = Matrix.Identity(4)
    for name, angle in (('spine', 24), ('chest', 10)):
        b = rig.pose.bones[name]
        b.rotation_mode = 'XYZ'; b.rotation_euler.x = math.radians(angle) * strength
    bpy.context.view_layer.update()
    for side, sign in (('L', 1), ('R', -1)):
        aim(rig, 'thigh.' + side, (sign * 2.2, -1.7, -2.03))
        aim(rig, 'shin.' + side, (-sign * .25, .65, -3.2))
        aim(rig, 'foot.' + side, (0, -1.08, -.25))
        aim(rig, 'upperarm.' + side, (-sign * .15, -1.8 * strength, -2.6 + 1.15 * strength))
        aim(rig, 'forearm.' + side, (sign * .08 * strength, -1.30 * strength, -.35))
        aim(rig, 'hand.' + side, (0, -1, -.15))
        # Aim alone preserves arbitrary inherited roll. Register the measured
        # palm plane so the palms face each other around the reins/neck.
        from mathutils import Vector,Quaternion
        hand=rig.pose.bones['hand.'+side]
        axis=(hand.tail-hand.head).normalized()
        source=Vector((-sign*.7604,.0723,-.6455))
        current=hand.matrix.to_3x3()@hand.bone.matrix_local.inverted().to_3x3()@source
        current-=axis*current.dot(axis);current.normalize()
        desired=Vector((-sign,0,0));desired-=axis*desired.dot(axis);desired.normalize()
        angle=math.atan2(axis.dot(current.cross(desired)),current.dot(desired))
        matrix=Quaternion(axis,angle).to_matrix().to_4x4()@hand.matrix
        matrix.translation=hand.head;hand.matrix=matrix
        for digit in range(5):
            for joint,angle in enumerate((45,90,55) if digit<4 else (0,30,15)):
                finger=rig.pose.bones.get(f'MF_fit_finger_{digit}_{joint}.{side}')
                if finger:
                    finger.rotation_mode='XYZ';finger.rotation_euler.x=math.radians(angle)
        bpy.context.view_layer.update()
        thumb=rig.pose.bones.get('MF_fit_finger_4_0.'+side)
        if thumb:
            # Oppose the whole thumb toward the index/middle grip corridor;
            # simply reversing its flexion plane created an upward hook.
            aim(rig,thumb.name,(-sign*.12,-.47,-.23))


def neutral_surface(body):
    """Sample accepted neutral fairing, keeping vertex correspondence/weights."""
    import bpy
    subs=[m for m in body.modifiers if m.type=='SUBSURF']
    flags=[m.show_viewport for m in subs]
    try:
        for m in subs:m.show_viewport=False
        bpy.context.view_layer.update()
        ev=body.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh()
        assert len(me.vertices)==len(body.data.vertices)
        result=[(v.co.copy(),v.normal.copy()) for v in me.vertices]
        ev.to_mesh_clear()
        return result
    finally:
        for m,flag in zip(subs,flags):m.show_viewport=flag
        bpy.context.view_layer.update()


def shell(body, name, region, mat, rig, surface):
    """Reuse the coherent body topology/weights, never edit the accepted body."""
    import bpy
    from mathutils import Vector
    from character_assembly import mesh
    selected = []
    def keep(v):
        p = surface[v.index][0]
        arm = sum(g.weight for g in v.groups if body.vertex_groups[g.group].name.startswith(('upperarm.', 'forearm.', 'hand.')))
        if region == 'tunic':
            return arm>.10 and -5.45<p.z<-1.50
        if region == 'trousers':
            return -11.45 < p.z < -5.72 and arm < .01
        return -12.28 < p.z < -10.95 and arm < .01
    for p in body.data.polygons:
        if all(keep(body.data.vertices[i]) for i in p.vertices):
            selected.append(p)
    indices = sorted({i for p in selected for i in p.vertices})
    lookup = {i: j for j, i in enumerate(indices)}
    points = []
    for i in indices:
        v = body.data.vertices[i]; p = surface[i][0].copy()
        arm = sum(g.weight for g in v.groups if body.vertex_groups[g.group].name.startswith(('upperarm.', 'forearm.', 'hand.')))
        if region == 'tunic' and arm < .3:
            radial = Vector((p.x, p.y - .18, 0))
            if radial.length:
                radial.normalize(); p += radial * .18
            if p.y < -.35:
                p.y = min(p.y, -1.16 + .04 * math.sin(p.x * 3 + p.z))
            if p.y > .5 and p.z < -3.:
                p.y = max(p.y, .97)
        else:
            p += surface[i][1] * (.18 if region == 'trousers' else .22 if region=='tunic' else .075)
        points.append(tuple(p))
    ob = mesh(name, points, [tuple(lookup[i] for i in p.vertices) for p in selected], mat)
    names = rig.data.bones.keys()
    groups = {n: ob.vertex_groups.new(name=n) for n in names}
    for i in indices:
        weights = {body.vertex_groups[g.group].name: g.weight for g in body.data.vertices[i].groups if body.vertex_groups[g.group].name in names}
        total = sum(weights.values())
        assert total > .99
        for n, w in weights.items():
            if w: groups[n].add([lookup[i]], w / total, 'REPLACE')
    mod = ob.modifiers.new('Reviewed anatomical weight transfer', 'ARMATURE')
    mod.object = rig; mod.use_deform_preserve_volume = True
    sub = ob.modifiers.new('Cloth surface', 'SUBSURF'); sub.levels = 2
    thickness = ob.modifiers.new('Garment thickness', 'SOLIDIFY'); thickness.thickness = .025
    return ob


def patterned_torso(cloth,rig):
    """Clean coarse tailoring surface, not a cut from bust integration edges."""
    from character_assembly import mesh
    rings=[(-2.18,1.63,1.02),(-2.75,1.79,1.46),(-3.5,1.65,1.34),(-4.3,1.43,1.16),(-5.15,1.34,1.13),(-5.9,1.52,1.21),(-6.45,1.61,1.24),(-6.85,1.65,1.25),(-7.25,1.69,1.28)]
    points=[];faces=[];n=96
    for j,(z,rx,ry) in enumerate(rings):
        for i in range(n):
            a=math.tau*i/n;fold=.028*math.sin(7*a+j*.6)
            top=.40*math.cos(a)**2 if j==0 else 0.
            points.append(((rx+fold)*math.cos(a),.18+(ry+fold)*math.sin(a),z+top))
    for j in range(len(rings)-1):
        for i in range(n):
            a=math.tau*(i+.5)/n
            if j>=5 and abs(math.sin(a))<.17:continue
            k=j*n+i;l=j*n+(i+1)%n
            faces.append((k,l,l+n,k+n))
    ob=mesh('MF_fit_tunic',points,faces,cloth);bind_torso(ob,rig)
    ob.modifiers.new('Tailored continuous surface','SUBSURF').levels=2
    ob.modifiers.new('Fabric thickness','SOLIDIFY').thickness=.035
    return ob


def expand_torso_clearance(ob,body,surface):
    """Expand the tailoring to actual neutral anatomy without copying its cuts."""
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    points=[p for p,_ in surface]
    faces=[tuple(f.vertices) for f in body.data.polygons if all(abs(points[i].x)<1.88 for i in f.vertices)]
    tree=BVHTree.FromPolygons(points,faces)
    for v in ob.data.vertices:
        center=Vector((0,.18,v.co.z));direction=v.co-center;direction.z=0
        direction.normalize();hit,_,_,_=tree.ray_cast(center+direction*5,-direction,8)
        if hit is not None and (hit-center).dot(direction)>0:
            radius=(hit-center).dot(direction)+(.32 if v.co.z<-5.2 else .20)
            if (v.co-center).length<radius:v.co=center+direction*radius
    ob.data.update()


def continuous_tunic(parts,body,surface,rig,cloth):
    """Union overlapping pattern/sleeves, then bind the coherent garment."""
    import bpy,bmesh
    from mathutils.kdtree import KDTree
    from character_assembly import mesh
    points=[];faces=[];volumes=[]
    for ob in parts:
        # Close each outer envelope before volumetric union. Thin walls were
        # undersampled and produced lace-like holes; they are rejected evidence.
        ob.modifiers.remove(ob.modifiers[-1])
        bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get()
        ev=ob.evaluated_get(deps);me=ev.to_mesh();offset=len(points)
        bm=bmesh.new();bm.from_mesh(me)
        bmesh.ops.holes_fill(bm,edges=[e for e in bm.edges if e.is_boundary],sides=0)
        bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
        volumes.append(abs(bm.calc_volume(signed=True)))
        assert not any(e.is_boundary for e in bm.edges), 'Outer envelope must be closed before union'
        bm.verts.ensure_lookup_table();bm.verts.index_update()
        points.extend(tuple(ob.matrix_world@v.co) for v in bm.verts)
        faces.extend(tuple(offset+v.index for v in f.verts) for f in bm.faces)
        bm.free()
        ev.to_mesh_clear();ob.hide_render=True;ob.hide_set(True)
        ob.name=ob.name+'_pattern_source'
    ob=mesh('MF_fit_tunic',points,faces,cloth)
    ob['fit_envelope_volumes']=volumes
    merge=ob.modifiers.new('Continuous stitched coarse garment','REMESH')
    merge.mode='VOXEL';merge.voxel_size=.045;merge.use_smooth_shade=True
    bpy.context.view_layer.update();ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get())
    data=bpy.data.meshes.new_from_object(ev);ob.modifiers.clear();ob.data=data
    bm=bmesh.new();bm.from_mesh(data)
    # Open only the central neck aperture, not upward-facing shoulder skin.
    # The broad normal-only cut passed neutral but tore open on arm reach.
    caps=[f for f in bm.faces if (f.calc_center_median().z>-2.40 and f.normal.z>.45
          and (f.calc_center_median().x/1.30)**2+((f.calc_center_median().y-.18)/1.00)**2<1.)
          or (f.calc_center_median().z<-6.80 and f.normal.z<-.65)]
    bmesh.ops.delete(bm,geom=caps,context='FACES')
    bm.to_mesh(data);bm.free()
    kd=KDTree(len(surface))
    for i,(p,_) in enumerate(surface):kd.insert(p,i)
    kd.balance()
    groups={n:ob.vertex_groups.new(name=n) for n in rig.data.bones.keys()}
    for v in ob.data.vertices:
        _,i,_=kd.find(v.co)
        weights={body.vertex_groups[g.group].name:g.weight for g in body.data.vertices[i].groups if body.vertex_groups[g.group].name in groups}
        total=sum(weights.values());assert total>.99
        for n,w in weights.items():
            if w:groups[n].add([v.index],w/total,'REPLACE')
    arm=ob.modifiers.new('Accepted-body garment weight transfer','ARMATURE');arm.object=rig;arm.use_deform_preserve_volume=True
    contact=ob.modifiers.new('Explicit static posed body clearance','SHRINKWRAP')
    contact.target=body;contact.wrap_method='NEAREST_SURFACEPOINT';contact.wrap_mode='OUTSIDE_SURFACE';contact.offset=.30
    return ob


def fair_boundary(ob):
    """Fair an actual cloth edge along its edge neighbours, not the torso."""
    import bmesh
    bm=bmesh.new();bm.from_mesh(ob.data)
    boundary=[v for v in bm.verts if v.is_boundary]
    for _ in range(8):
        moves=[]
        for v in boundary:
            neighbors=[e.other_vert(v) for e in v.link_edges if e.is_boundary]
            if len(neighbors)==2:moves.append((v,(neighbors[0].co+neighbors[1].co)*.5))
        for v,target in moves:v.co=v.co.lerp(target,.5)
    bm.to_mesh(ob.data);bm.free()


def hair_clearance(hood):
    import bpy,bmesh
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    hull=bmesh.new()
    for name in ('MF_natural147_hair_long hair main','MF_natural147_hair_long hair strands'):
        ob=bpy.data.objects[name];ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get())
        stride=max(1,len(ev.data.points)//1800)
        for p in list(ev.data.points)[::stride]:hull.verts.new(ob.matrix_world@p.position)
    bmesh.ops.convex_hull(hull,input=list(hull.verts),use_existing_faces=False)
    hull.verts.ensure_lookup_table();hull.verts.index_update()
    tree=BVHTree.FromPolygons([v.co for v in hull.verts],[tuple(v.index for v in f.verts) for f in hull.faces])
    changed=0;center=Vector((0,.25,-.40))
    for v in hood.data.vertices:
        p=hood.matrix_world@v.co
        if p.z < -2.2 or (p.y<.05 and p.z<.55):continue
        direction=(p-center).normalized()
        hit,_,_,_=tree.ray_cast(center+direction*8,-direction,10)
        if hit is not None and (p-center).length<(hit-center).length+.30:
            v.co=hood.matrix_world.inverted()@(hit+direction*.30);changed+=1
    hull.free();hood.data.update()
    return changed


def fit_straps(straps, targets):
    import bpy
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    verts=[];faces=[];deps=bpy.context.evaluated_depsgraph_get()
    for ob in targets:
        ev=ob.evaluated_get(deps);me=ev.to_mesh();offset=len(verts)
        verts.extend(ob.matrix_world@v.co for v in me.vertices)
        # Radial casts must not land on sleeves/forearms: that created belt
        # wings. Only the torso corridor can be a harness fitting surface.
        faces.extend(tuple(offset+i for i in p.vertices) for p in me.polygons
                     if all(abs(verts[offset+i].x)<1.88 for i in p.vertices))
        ev.to_mesh_clear()
    tree=BVHTree.FromPolygons(verts,faces)
    for ob in straps:
        for v in ob.data.vertices:
            p=v.co;center=Vector((0,.18,p.z));direction=p-center
            direction.z=0
            if direction.length<.01:continue
            direction.normalize();hit,_,_,_=tree.ray_cast(center+direction*5,-direction,8)
            # An open neckline ray can hit the opposite/back side, folding the
            # front scarf into a black hole. Never cross the torso centre.
            if hit is not None and (hit-center).dot(direction)>0:
                v.co=hit+direction*.06
        ob.data.update()


def restore_skin_interface(body):
    """Carry source shader inputs, not only UVs, onto the continuous derivative."""
    import bpy
    from mathutils import Vector
    source = bpy.data.objects['MF_continuous_head_neck']
    ev = source.evaluated_get(bpy.context.evaluated_depsgraph_get())
    count = body['accepted_head_vertex_count']
    assert len(ev.data.vertices) == count
    copied = []
    for attr in ev.data.attributes:
        if attr.domain != 'POINT' or attr.data_type != 'FLOAT' or not attr.name.startswith('MF_'):
            continue
        dest = body.data.attributes.get(attr.name) or body.data.attributes.new(attr.name, 'FLOAT', 'POINT')
        for i, item in enumerate(attr.data): dest.data[i].value = item.value
        copied.append(attr.name)
    coords = body.data.attributes.new('MF_fit_source_skin_coordinates', 'FLOAT_VECTOR', 'POINT')
    inv = source.matrix_world.inverted()
    for v, item in zip(body.data.vertices, coords.data):
        item.vector = ev.data.vertices[v.index].co if v.index<count else inv @ v.co
    old = body.data.materials[0]
    mat = old.copy(); mat.name = 'MF_fit_preserved_skin_coordinates'; body.data.materials[0] = mat
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    origin = nodes.new('ShaderNodeAttribute'); origin.attribute_name = coords.name
    for node in list(nodes):
        if node.type == 'TEX_COORD':
            for link in list(node.outputs['Object'].links): links.new(origin.outputs['Vector'], link.to_socket)
    from character_assembly import material
    body.data.materials[3] = material('MF_fit_visible_hand_skin', (.37,.205,.125))
    chest=material('MF_fit_neckline_skin_transition',(.54,.225,.105))
    body.data.materials.append(chest)
    chest_index=len(body.data.materials)-1
    for poly in body.data.polygons:
        if poly.material_index==3 and all(body.data.vertices[i].co.z>-3.8 and abs(body.data.vertices[i].co.x)<1.75 for i in poly.vertices):
            poly.material_index=chest_index
    return {'copied_point_attributes':copied, 'source_local_coordinate_restoration':True,
            'source_material_unchanged':True, 'scope':'Source-face shader interface restoration; donor hands/neckline base tones are provisional, not final body atlas'}


def bind_torso(ob, rig):
    groups = {n: ob.vertex_groups.new(name=n) for n in ('chest','spine','pelvis')}
    for v in ob.data.vertices:
        z = v.co.z
        chest = min(1., max(0., (z+4.8)/1.6))
        pelvis = min(1., max(0., (-z-4.8)/1.2))
        for n,w in [('chest',chest),('pelvis',pelvis),('spine',1-chest-pelvis)]:
            if w>0:groups[n].add([v.index],w,'REPLACE')
    m=ob.modifiers.new('Continuous torso support','ARMATURE');m.object=rig;m.use_deform_preserve_volume=True


def drape_and_harness(cloth, leather, rig, body):
    import bpy
    from mathutils import Vector
    from character_assembly import mesh
    from mathutils.bvhtree import BVHTree
    points=[];faces=[];nu=64;nv=18
    for i in range(nu):
        # Front drape continues the hood sides. A second rigid rear shoulder
        # cape floated around the hair; the existing hood already covers rear.
        a=math.pi+math.pi*i/(nu-1)
        for j in range(nv):
            v=j/(nv-1)
            fold=.075*math.sin(9*a+7*v)*math.sin(math.pi*v)
            x=(1.72+.12*v+fold)*math.cos(a)
            y=.18+(1.65+.18*v+.18*max(0,math.sin(a)))*math.sin(a)
            top=-2.16+.45*math.cos(a)**2
            bottom=-3.80+1.20*math.cos(a)**2+.40*math.sin(a)
            z=top*(1-v)+bottom*v+fold*.5
            points.append((x,y,z))
    for i in range(nu-1):
        for j in range(nv-1):
            a=i*nv+j;b=(i+1)*nv+j;faces.append((a,b,b+1,a+1))
    shawl=mesh('MF_fit_diagonal_scarf',points,faces,cloth);bind_torso(shawl,rig)
    shawl.modifiers.new('Broad cloth drape','SUBSURF').levels=2
    shawl.modifiers.new('Cloth thickness','SOLIDIFY').thickness=.03
    straps=[]
    for sign in (-1,1):
        anchors=[Vector((sign*x,y,z)) for x,y,z in [(1.48,-.38,-1.82),(1.20,-1.43,-2.4),(.4,-1.46,-3.4),(-.55,-1.36,-4.4),(-1.26,-.80,-5.35),(-1.40,.35,-5.35),(-.9,1.27,-4.7),(.2,1.3,-3.5),(1.4,.9,-2.2),(1.5,.4,-1.82)]]
        curve=[]
        for i in range(len(anchors)):
            p0,p1,p2,p3=[anchors[k%len(anchors)] for k in (i-1,i,i+1,i+2)]
            for j in range(10):
                t=j/10
                curve.append(tuple(.5*((2*p1)+(-p0+p2)*t+(2*p0-5*p1+4*p2-p3)*t*t+(-p0+3*p1-3*p2+p3)*t*t*t)))
        ob=ribbon('MF_fit_shoulder_harness_'+str(sign),curve,.22,leather);bind_torso(ob,rig);straps.append(ob)
    belt=ribbon('MF_fit_waist_belt',[(1.48*math.cos(math.tau*i/96),.18+1.19*math.sin(math.tau*i/96),-5.62) for i in range(96)],.24,leather);bind_torso(belt,rig)
    # Keep detached panels out of the realization. The visible shoulder wrap
    # has a shaped U opening and broad diagonal fall, not a flat ring plate.
    collar=ribbon('MF_fit_bound_neckline',[(1.72*math.cos(math.tau*i/96),.18+1.42*math.sin(math.tau*i/96),-2.30+.55*math.cos(math.tau*i/96)**2) for i in range(96)],.28,cloth)
    bind_torso(collar,rig)
    collar.modifiers.new('Rounded neckline binding','SUBSURF').levels=2
    return [shawl,collar,*straps,belt]


def fit_static_contacts(horse, rig, leather):
    import bpy
    from mathutils import Matrix,Vector
    # Actual stirrup halves, translated separately to the boot support point.
    stirrup=next(o for o in horse if o['source_object']=='saddle.stirrup')
    old_world=stirrup.matrix_world.copy()
    points=[old_world@v.co for v in stirrup.data.vertices]
    stirrup.matrix_world=Matrix.Identity(4)
    contacts={}
    for side,sign in [('L',1),('R',-1)]:
        foot=rig.pose.bones['foot.'+side]
        boot=bpy.data.objects['MF_fit_closed_boot_'+side]
        ev=boot.evaluated_get(bpy.context.evaluated_depsgraph_get())
        sole=[boot.matrix_world@v.co for v in ev.data.vertices]
        # Support is registered to the actual closed boot sole, not an assumed
        # offset from an anatomical ankle pivot.
        target=Vector((foot.head.x,foot.head.y-.25,min(p.z for p in sole)+.025))
        ids=[i for i,p in enumerate(points) if sign*p.x>0]
        center=Vector(tuple((min(points[i][k] for i in ids)+max(points[i][k] for i in ids))/2 for k in range(3)))
        # Bottom plate, rather than ring centre, supports the sole.
        center.z=min(points[i].z for i in ids)+.10
        delta=target-center
        for i in ids:stirrup.data.vertices[i].co=points[i]+delta
        contacts[side]={'stirrup_support_authored':list(target),'foot_bone':list(foot.head)}
    for o in horse:
        if o['source_object']=='saddle.stirrup.strap':o.hide_render=True
    def rope(name,locations,depth):
        existing=bpy.data.objects.get(name)
        if existing:
            for p,location in zip(existing.data.splines[0].points,locations):p.co=(*location,1)
            return
        data=bpy.data.curves.new(name,'CURVE');data.dimensions='3D';data.bevel_depth=depth;data.bevel_resolution=2
        spline=data.splines.new('POLY');spline.points.add(len(locations)-1)
        for p,location in zip(spline.points,locations):p.co=(*location,1)
        ob=bpy.data.objects.new(name,data);bpy.context.scene.collection.objects.link(ob);data.materials.append(leather)
    bridle=next(o for o in horse if o['source_object']=='bit')
    bridle_points=[bridle.matrix_world@v.co for v in bridle.data.vertices]
    for side,sign in [('L',1),('R',-1)]:
        hand=rig.pose.bones['hand.'+side]
        grip=hand.head+(hand.tail-hand.head).normalized()*.9+Vector((-sign*.25,0,0))
        a=rig.pose.bones.get('MF_fit_finger_0_1.'+side)
        b=rig.pose.bones.get('MF_fit_finger_1_1.'+side)
        if a and b:grip=(a.head+a.tail+b.head+b.tail)/4
        # Nearest anterior-lower part of actual bridle is a private fit anchor,
        # not a certified bit attachment or physical force model.
        bit=min((p for p in bridle_points if sign*p.x>0),key=lambda p:p.y+p.z*.35)
        midpoint=bit.lerp(grip,.5);midpoint.z-=.22;midpoint.x=sign*1.60
        rope('MF_fit_rein_'+side,[bit,midpoint,grip],.050)
        foot=Vector(contacts[side]['stirrup_support_authored'])
        rope('MF_fit_stirrup_leather_'+side,[(sign*2.0,.3,-7.0),foot+Vector((0,.1,0))],.055)
        contacts[side]['rein_endpoint']=list(grip)
    return contacts


def actual_horse():
    """Bake a fixed actual source pose for private fitting, not gait reuse proof."""
    import bpy
    from mathutils import Matrix, Vector
    wanted = ['horse', 'horse.rig', 'saddle', 'saddle.pad', 'saddle.stirrup', 'saddle.stirrup.strap', 'bridle', 'bridle.body', 'bit', 'Torus.002', 'Full Bushy Flowing Horse Tail']
    target_scene=bpy.context.scene
    # The complete source evaluation graph includes rig helper/constraint
    # targets. Loading only named visible meshes left disconnected leg parts.
    with bpy.data.libraries.load(str(HORSE), link=False) as (a, b):
        b.scenes=[a.scenes[0]]
    source_scene=b.scenes[0];bpy.context.window.scene=source_scene
    imported=[o for o in source_scene.objects if o.name in wanted]
    source_scene.frame_set(0)
    # Static saddle fit uses neutral horse geometry, not an unqualified gait
    # instant with open distal joints. Gait is a later complete-motion test.
    source_rig=next(o for o in imported if o.name=='horse.rig')
    source_rig.animation_data_clear()
    for bone in source_rig.pose.bones:
        for constraint in list(bone.constraints):bone.constraints.remove(constraint)
        bone.matrix_basis=Matrix.Identity(4)
    bpy.context.view_layer.update()
    # Scene-unit conversion based on body height; seat position is deliberately
    # authored against the measured source saddle, not a saddle proxy.
    transform = Matrix.Translation((0, .20, -6.85)) @ Matrix.Scale(8.3, 4) @ Matrix.Translation((0, -2.52, -1.57))
    baked = []
    deps = bpy.context.evaluated_depsgraph_get()
    for ob in imported:
        if ob.type not in ('MESH', 'CURVE'): continue
        ev = ob.evaluated_get(deps)
        data = bpy.data.meshes.new_from_object(ev, preserve_all_data_layers=True, depsgraph=deps)
        copy = bpy.data.objects.new('MF_fit_' + ob.name, data)
        target_scene.collection.objects.link(copy)
        copy.matrix_world = transform @ ev.matrix_world
        copy['source_object'] = ob.name; copy['fit_scope'] = 'Neutral derivative evaluated geometry; source untouched, no motion qualification'
        baked.append(copy)
    bpy.context.window.scene=target_scene;bpy.context.view_layer.update()
    return baked


def ribbon(name, points, width, mat):
    from mathutils import Vector
    from character_assembly import mesh
    vertices = []
    for i, p in enumerate(points):
        p = Vector(p)
        tangent = Vector(points[(i+1) % len(points)]) - Vector(points[i-1])
        outward = Vector((p.x, p.y - .18, 0)).normalized()
        across = tangent.cross(outward).normalized() * width / 2
        vertices.extend((tuple(p-across), tuple(p+across)))
    faces = [(2*i, 2*((i+1)%len(points)), 2*((i+1)%len(points))+1, 2*i+1) for i in range(len(points))]
    ob = mesh(name, vertices, faces, mat)
    mod = ob.modifiers.new('Leather thickness', 'SOLIDIFY'); mod.thickness = .04
    return ob


def accepted_signature(names):
    """Hash accepted data once, excluding newly admitted horse/costume geometry.

    Earlier diagnostics accidentally rehashed every visible scene object six
    times per check; both the protection scope and that overhead were wrong.
    Visibility is restored immediately, even if the shared hasher fails.
    """
    import bpy
    from body_studio_fit import protected
    state={ob.name:ob.hide_render for ob in bpy.context.scene.objects}
    try:
        for ob in bpy.context.scene.objects:ob.hide_render=ob.name not in names
        result=protected()
        return {n:result[n] for n in names}
    finally:
        for name,hidden in state.items():bpy.data.objects[name].hide_render=hidden


def closed_boot(body, side, sign, leather, rig):
    import bpy,bmesh
    # A closed convex last contains every foot point and bridges individual
    # toes. It replaces both the bare-toe shell and failed egg-shaped proxies.
    points=[v.co for v in body.data.vertices if sign*v.co.x>0 and v.co.z<-12.15 and abs(v.co.x)<1.6]
    bm=bmesh.new()
    for p in points:bm.verts.new(p)
    hull=bmesh.ops.convex_hull(bm,input=list(bm.verts),use_existing_faces=False)
    unused=[v for v in hull['geom_unused']+hull['geom_interior'] if isinstance(v,bmesh.types.BMVert)]
    if unused:bmesh.ops.delete(bm,geom=list(set(unused)),context='VERTS')
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.normal_update()
    for v in bm.verts:v.co+=v.normal*.16
    # Do not bevel the acute hull edges: unconstrained miters exploded in05.
    data=bpy.data.meshes.new('MF_closed_last_'+side);bm.to_mesh(data);bm.free()
    boot=bpy.data.objects.new('MF_fit_closed_boot_'+side,data);bpy.context.scene.collection.objects.link(boot)
    data.materials.append(leather)
    for p in data.polygons:p.use_smooth=True
    group=boot.vertex_groups.new(name='foot.'+side);group.add(list(range(len(data.vertices))),1,'REPLACE')
    mod=boot.modifiers.new('Foot support','ARMATURE');mod.object=rig
    return boot


def authored_grip(body, rig):
    """Reversible static hand closure, not a finger rig or animation claim."""
    from mathutils import Vector,Quaternion
    # Four separate distal components were measured from inspect02's pinned
    # donor points (t>.9, distance connectivity .035); roots extend .14 inward.
    fingers=[
        ((3.443960,-.475900,-6.695024),(.228215,-.394335,-.890179),.695763),
        ((3.456708,-.276842,-6.753022),(.138602,-.324769,-.935582),.624770),
        ((3.402358,-.713464,-6.640621),(.202822,-.496609,-.843945),.560728),
        ((3.384742,-.047760,-6.839653),(.241573,-.091246,-.966083),.418581),
        ((3.14,-.52,-6.25),(-.10,-.80,-.59),.58),
    ]
    key=body.shape_key_add(name='MF_fit_static_rein_grip',from_mix=False)
    for side,sign in (('L',1),('R',-1)):
        bone=rig.data.bones['hand.'+side]
        axis=(bone.tail_local-bone.head_local).normalized()
        paths=[]
        for i,(root,direction,length) in enumerate(fingers):
            root=Vector((sign*root[0],root[1],root[2]));direction=Vector((sign*direction[0],direction[1],direction[2])).normalized()
            normal=Vector((sign if i==4 else -sign,0,0));normal-=direction*normal.dot(direction);normal.normalize()
            paths.append((root,direction,length,normal,1.65 if i==4 else 2.65))
        group=body.vertex_groups['hand.'+side].index
        for v in body.data.vertices:
            weight=next((g.weight for g in v.groups if g.group==group),0.)
            if weight<.01:continue
            t=(v.co-bone.head_local).dot(axis)
            if t<.25:continue
            def distance(path):
                root,direction,length,_,_=path;u=(v.co-root).dot(direction)
                return (v.co-root-direction*min(length,max(0.,u))).length
            root,direction,length,normal,angle=min(paths,key=distance)
            delta=v.co-root;u=delta.dot(direction)
            if u<=0:continue
            theta=min(angle+ .15,u/length*angle);radius=length/angle
            across=delta-direction*u
            q=Quaternion(direction.cross(normal).normalized(),theta)
            target=root+direction*(radius*math.sin(theta))+normal*(radius*(1-math.cos(theta)))+q@across
            key.data[v.index].co=key.data[v.index].co.lerp(target,weight)
    key.value=0.
    return key


def evaluated_surfaces(names):
    import bpy,numpy as np
    result={};deps=bpy.context.evaluated_depsgraph_get()
    for name in names:
        ob=bpy.data.objects[name];ev=ob.evaluated_get(deps)
        if ob.type!='MESH':continue
        me=ev.to_mesh()
        coords=np.empty(len(me.vertices)*3,dtype=np.float32)
        me.vertices.foreach_get('co',coords)
        result[name]=coords.reshape(-1,3)
        ev.to_mesh_clear()
    return result


def install_fingers(body,rig):
    """Narrow articulated derivative; accepted neutral basis stays unchanged."""
    import bpy
    from mathutils import Vector
    definitions=[
        ((3.443960,-.475900,-6.695024),(.228215,-.394335,-.890179),.695763),
        ((3.456708,-.276842,-6.753022),(.138602,-.324769,-.935582),.624770),
        ((3.402358,-.713464,-6.640621),(.202822,-.496609,-.843945),.560728),
        ((3.384742,-.047760,-6.839653),(.241573,-.091246,-.966083),.418581),
        # Thumb measured separately (x<3.25, anterior edge), not inferred
        # from the four-finger fan. The earlier approximation tore its web.
        ((2.966360,-.664022,-6.236777),(.166636,-.807428,-.565944),.479723)]
    bpy.context.view_layer.objects.active=rig;rig.hide_set(False);rig.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT');paths=[]
    for side,sign in [('L',1),('R',-1)]:
        for digit,(root,direction,length) in enumerate(definitions):
            root=Vector((sign*root[0],root[1],root[2]));axis=Vector((sign*direction[0],direction[1],direction[2])).normalized()
            normal=Vector((sign*.7604,-.0723,.6455) if digit==4 else (-sign*.7604,.0723,-.6455));normal-=axis*normal.dot(axis);normal.normalize()
            names=[]
            for joint,(a,b) in enumerate(((0,.40),(.40,.75),(.75,1.0))):
                name=f'MF_fit_finger_{digit}_{joint}.{side}';bone=rig.data.edit_bones.new(name)
                bone.head=root+axis*length*a;bone.tail=root+axis*length*b
                bone.parent=rig.data.edit_bones[names[-1] if names else 'hand.'+side]
                bone.use_connect=bool(names);bone.align_roll(normal);names.append(name)
            paths.append((side,root,axis,length,names))
    bpy.ops.object.mode_set(mode='OBJECT')
    groups={n:body.vertex_groups.new(name=n) for *_,names in paths for n in names}
    for side in ('L','R'):
        hand=body.vertex_groups['hand.'+side];options=[p for p in paths if p[0]==side]
        for v in body.data.vertices:
            w=next((g.weight for g in v.groups if g.group==hand.index),0.)
            if w<.01:continue
            def distance(p):
                _,root,axis,length,_=p;u=(v.co-root).dot(axis)
                return (v.co-root-axis*max(0,min(length,u))).length
            chosen=min(options,key=distance)
            _,root,axis,length,names=chosen;u=(v.co-root).dot(axis)
            support=min(1,max(0,(u+.04)/.12))*min(1,max(0,(.20-distance(chosen))/.08))
            if support==0:continue
            hand.add([v.index],w*(1-support),'REPLACE')
            t=u/length
            if t<.34:weights=(1,0,0)
            elif t<.46:
                blend=(t-.34)/.12;weights=(1-blend,blend,0)
            elif t<.69:weights=(0,1,0)
            elif t<.81:
                blend=(t-.69)/.12;weights=(0,1-blend,blend)
            else:weights=(0,0,1)
            for name,fraction in zip(names,weights):
                if fraction:groups[name].add([v.index],w*support*fraction,'REPLACE')
    return list(groups)


def fit_render(out, label, angle, center=(0,.1,-5.8), size=15.8, resolution=(540,900)):
    import bpy
    from mathutils import Matrix,Vector
    scene=bpy.context.scene;camera=scene.camera
    scene.render.resolution_x,scene.render.resolution_y=resolution
    target=Vector(center);rot=Matrix.Rotation(math.radians(angle),3,'Z')
    camera.data.ortho_scale=size;camera.location=target+rot@Vector((0,-36,.6))
    camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler()
    lights=sorted((o for o in scene.objects if o.name.startswith('MF_body156_softbox')),key=lambda o:o.name)
    for light,x in zip(lights,(-7,7)):
        light.location=target+rot@Vector((x,-9,7));light.rotation_euler=(target-light.location).to_track_quat('-Z','Y').to_euler()
    scene.render.filepath=str(out/(label+'.png'));bpy.ops.render.render(write_still=True)


def verify(out):
    import bpy,numpy as np
    from mathutils import Matrix
    from body_studio_fit import coordinates_digest
    sealed=BASE/'wardrobe169-seal01'
    result=json.loads((sealed/'result.json').read_text())
    bpy.ops.wm.open_mainfile(filepath=str(sealed/'dressed-fit.blend'),load_ui=False,use_scripts=False)
    body=bpy.data.objects['MF_studio_adult_body'];rig=bpy.data.objects['MF_body156_fit_rig']
    source_equal=accepted_signature(result['protected_signatures'])==result['protected_signatures']
    basis_equal=coordinates_digest(tuple(v.co) for v in body.data.vertices)==result['body_basis_digest']
    reference=np.load(sealed/'evaluated-surfaces.npz',allow_pickle=False)
    actual=evaluated_surfaces(reference.files)
    errors={n:float(np.max(np.abs(actual[n]-reference[n]))) if actual[n].shape==reference[n].shape else None for n in reference.files}
    assert source_equal and basis_equal and all(v is not None and v<2e-5 for v in errors.values())
    fit_render(out,'reopened-mounted-side',90,(0,-1,-10),29,(1000,700))
    for bone in rig.pose.bones:bone.matrix_basis=Matrix.Identity(4)
    for ob in bpy.context.scene.objects:
        if ob.name.startswith(('MF_fit_horse','MF_fit_saddle','MF_fit_bridle','MF_fit_bit','MF_fit_Torus','MF_fit_Full','MF_fit_rein_','MF_fit_stirrup_leather_')):ob.hide_render=True
    bpy.context.view_layer.update()
    fit_render(out,'reopened-standing-front',0)
    verification={'reopened':True,'protected_signatures_exact':source_equal,'body_basis_exact':basis_equal,
                  'evaluated_local_surface_max_errors':errors,'surface_tolerance':2e-5,
                  'neutral_rollback_and_grip_release':True,'source_unchanged':digest(BODY)==BODY_SHA and digest(HORSE)==HORSE_SHA,
                  'limits':['Evaluated local mesh positions checked; not topology, gait, constraint-force or facial-expression qualification']}
    (out/'result.json').write_text(json.dumps(verification,indent=2)+'\n')


def build(out, operation):
    import bpy
    from mathutils import Matrix, Vector
    from character_assembly import material
    from body_studio_fit import protected, coordinates_digest
    bpy.ops.wm.open_mainfile(filepath=str(BODY), load_ui=False, use_scripts=False)
    # Only original accepted identity/control names are immutable material
    # targets. The continuous body's diagnostic clay/material interface is
    # explicitly restored in this wardrobe derivative; its geometry stays exact.
    authority = json.loads((BODY.parent/'result.json').read_text())['protected']
    before = accepted_signature(authority)
    body = bpy.data.objects['MF_studio_adult_body']; rig = bpy.data.objects['MF_body156_fit_rig']
    body_hash = coordinates_digest(tuple(v.co) for v in body.data.vertices)
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'; scene.cycles.samples = 16
    scene.render.resolution_x = 540; scene.render.resolution_y = 900; scene.render.resolution_percentage = 100
    scene.view_layers[0].material_override = None
    skin_interface = restore_skin_interface(body)
    for bone in rig.pose.bones:bone.matrix_basis=Matrix.Identity(4)
    bpy.context.view_layer.update()
    surface=neutral_surface(body)
    cloth = material('MF_fit_indigo_tunic', (.021, .045, .095))
    pants = material('MF_fit_dark_indigo_trousers', (.016, .027, .053))
    leather = material('MF_fit_brown_harness_boots', (.11, .052, .025))
    clothes = [patterned_torso(cloth,rig),shell(body, 'MF_fit_sleeves', 'tunic', cloth, rig, surface), shell(body, 'MF_fit_trousers', 'trousers', pants, rig, surface), shell(body, 'MF_fit_boots', 'boots', leather, rig, surface)]
    expand_torso_clearance(clothes[0],body,surface)
    clothes=[continuous_tunic(clothes[:2],body,surface,rig,cloth),*clothes[2:]]
    # Adapt the actual reusable scarf only; keep accepted hair/skin unchanged.
    hood = bpy.data.objects['MF_adapted_donor_hood'].copy()
    hood.data = hood.data.copy(); scene.collection.objects.link(hood)
    hood.name = 'MF_fit_indigo_headscarf'; hood.hide_render = False; hood.hide_set(False)
    hood.constraints.clear(); hood.modifiers.clear()
    hood.matrix_world = Matrix.Translation((0,0,-.228)) @ Matrix.Scale(.88,4) @ hood.matrix_world
    hood.data.materials.clear(); hood.data.materials.append(cloth)
    scarf_clearance_vertices=hair_clearance(hood)
    for v in hood.data.vertices:
        p=hood.matrix_world@v.co
        if p.z<-1.2:
            t=min(1.,max(0.,(-p.z-1.2)/1.2))
            p.z-=.65*t
            if p.y>.8:p.y=p.y*(1-t*.55)+1.18*t*.55
            p.x*=1+.10*t
            v.co=hood.matrix_world.inverted()@p
    sub=hood.modifiers.new('Continuous scarf surface','SUBSURF');sub.levels=2
    rest = rig.matrix_world @ rig.data.bones['chest'].matrix_local
    c = hood.constraints.new('CHILD_OF'); c.target = rig; c.subtarget = 'chest'; c.inverse_matrix = rest.inverted()
    clothes.append(hood)
    clothes.extend(drape_and_harness(cloth,leather,rig,body))
    shawl=next(o for o in clothes if o.name=='MF_fit_diagonal_scarf')
    collar=next(o for o in clothes if o.name=='MF_fit_bound_neckline')
    fit_straps([shawl,collar],[clothes[0]])
    for ob in (clothes[0],shawl):fair_boundary(ob)
    fit_straps([o for o in clothes if 'harness' in o.name or 'belt' in o.name],[o for o in clothes if 'harness' not in o.name and 'belt' not in o.name and 'boot' not in o.name and 'trouser' not in o.name])
    # Closed overshoe volumes remove bare-toe silhouettes without changing feet.
    for side,sign in [('L',1),('R',-1)]:
        clothes.append(closed_boot(body,side,sign,leather,rig))
    finger_controls=install_fingers(body,rig)
    # Tailoring/control surfaces are derivatives; folds and dynamic cloth
    # remain separate from this authored static pose/clearance screen.
    for b in rig.pose.bones:b.matrix_basis=Matrix.Identity(4)
    bpy.context.view_layer.update()
    if not operation.startswith(('finger','pose')):
        for label, angle in [('front',0), ('side',90), ('rear',180)]:fit_render(out,'standing-'+label,angle)
    if operation=='cloth24':
        result={'operation':operation,'protected_data_exact':accepted_signature(authority)==before,
                'body_local_geometry_exact':coordinates_digest(tuple(v.co) for v in body.data.vertices)==body_hash,
                'closed_envelope_volumes':list(clothes[0]['fit_envelope_volumes']),
                'scope':'Standing cloth diagnostic only; no mounted or selected gate',
                'handler_sha256':digest(Path(__file__))}
        assert result['protected_data_exact'] and result['body_local_geometry_exact']
        (out/'result.json').write_text(json.dumps(result,indent=2)+'\n');return
    horse=actual_horse()
    riding_pose(rig)
    bpy.context.view_layer.update()
    contacts=fit_static_contacts(horse,rig,leather)
    if operation=='pose27':
        for ob in clothes+horse:ob.hide_render=True
        for ob in scene.objects:
            if ob.name.startswith(('MF_fit_rein_','MF_fit_stirrup_leather_')):ob.hide_render=True
        scene.view_layers[0].material_override=material('MF_fit_pose_clay',(.35,.35,.35))
        for label,angle in [('side',90),('rear-quarter',140)]:fit_render(out,'body-'+label,angle,(0,-1,-5.8),15.8)
        result={'operation':operation,'scope':'Underlying current body pose, without garment concealment',
                'protected_data_exact':accepted_signature(authority)==before,
                'body_local_geometry_exact':coordinates_digest(tuple(v.co) for v in body.data.vertices)==body_hash,
                'handler_sha256':digest(Path(__file__))}
        assert result['protected_data_exact'] and result['body_local_geometry_exact']
        (out/'result.json').write_text(json.dumps(result,indent=2)+'\n');return
    if not operation.startswith('finger'):
        for label,angle in [('side',90),('opposite-side',-90),('front-quarter',-40),('rear-quarter',140)]:
            fit_render(out,'mounted-'+label,angle,(0,-1,-10.0),29,(1000,700) if 'side' in label else (540,900))
    hand_center=(rig.pose.bones['hand.L'].head+rig.pose.bones['hand.R'].head)/2
    hand_center+=(rig.pose.bones['hand.L'].tail-rig.pose.bones['hand.L'].head)*.5
    fit_render(out,'mounted-hands',-35,tuple(hand_center),3.5,(800,650))
    if operation.startswith('finger'):fit_render(out,'mounted-other-hands',35,tuple(hand_center),3.5,(800,650))
    else:fit_render(out,'mounted-boot-stirrup',90,(2.7,-1,-11.8),4.8,(800,650))
    riding_pose(rig,.75);bpy.context.view_layer.update();fit_static_contacts(horse,rig,leather)
    if not operation.startswith('finger'):fit_render(out,'mounted-partial-lean',90,(0,-1,-10),29,(1000,700))
    riding_pose(rig);bpy.context.view_layer.update();contacts=fit_static_contacts(horse,rig,leather)
    after=accepted_signature(authority)
    result = {'source_body_sha256':BODY_SHA,'source_horse_sha256':HORSE_SHA,'operation':operation,
              'body_local_geometry_exact':coordinates_digest(tuple(v.co) for v in body.data.vertices)==body_hash,
              'skin_interface':skin_interface,'static_contacts':contacts,'scarf_clearance_vertices':scarf_clearance_vertices,
              'protected_data_exact':after==before,
              'garments':[o.name for o in clothes], 'actual_horse_objects':[o.name for o in horse],
              'pose_matrices':{b.name:[list(r) for r in b.matrix_basis] for b in rig.pose.bones},
              'structural_visual_gate':'NOT_RUN_PENDING_INTERNAL_REVIEW', 'Director_acceptance':'PENDING',
              'limits':['Private static fit only', 'Authored rein endpoints do not establish finger grasp or dynamic contact', 'No simulation, gait or final outfit acceptance'],
              'source_unchanged':digest(BODY)==BODY_SHA and digest(HORSE)==HORSE_SHA}
    result['protected_differences']=[n for n,v in before.items() if after[n]!=v]
    result['handler_sha256']=digest(Path(__file__))
    result['protected_signatures']=before
    result['body_basis_digest']=body_hash
    result['finger_controls']=finger_controls
    result['garment_envelope_volumes']=list(clothes[0]['fit_envelope_volumes'])
    result['horse_pose_scope']='Neutral private derivative; source gait snapshot not qualified for reuse'
    result['garment_fit_scope']='Pose-evaluated outside-surface clearance, not cloth simulation or dynamic qualification'
    result['static_grip_corrective']='Articulated derivative finger controls; native animation and force/contact qualification remain open'
    (out/'result.json').write_text(json.dumps(result,indent=2)+'\n')
    assert result['body_local_geometry_exact'] and result['protected_data_exact'] and result['source_unchanged'], {k:result[k] for k in ('body_local_geometry_exact','protected_differences','source_unchanged')}
    if operation=='seal01':
        import numpy as np
        names=[body.name,*[o.name for o in clothes],*[o.name for o in horse]]
        np.savez_compressed(out/'evaluated-surfaces.npz',**evaluated_surfaces(names))
        for block in bpy.data.texts:block.use_module=False
        bpy.ops.file.pack_all()
        result['embedded_text_auto_registration_disabled']=all(not t.use_module for t in bpy.data.texts)
        scene.render.image_settings.file_format='PNG'
        bpy.ops.wm.save_as_mainfile(filepath=str(out/'dressed-fit.blend'),compress=True)
        result['native_sha256']=digest(out/'dressed-fit.blend')
    (out/'result.json').write_text(json.dumps(result,indent=2)+'\n')


if __name__ == '__main__':
    main()
