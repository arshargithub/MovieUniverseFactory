"""Pinned Blender Studio body inspection and accepted-bust fitting operations."""
import json
from pathlib import Path
import sys
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parent))
from character_assembly import BASE, SOURCE, SOURCE_SHA, digest, inventory, protected

ROOT = Path(__file__).resolve().parents[4]
ASSETS = ROOT / '.runtime/assets/series01-body-blender-studio'
ARCHIVE = ASSETS / 'human-base-meshes-bundle-v1.4.1.zip'
ARCHIVE_SHA = '811f43accbb31a88266d932f8f5563b2d13586fca0ba2693aad1f5fe582b3515'
MEMBER = 'human-base-meshes-bundle-v1.4.1/human_base_meshes_bundle.blend'


def validate(job):
    if job not in tuple({'operation': name} for name in ('inspect01','fit01','fit02','fit03','fit04','review05','fit06','fit07','fit08','fit09','fit10','fit11','fit12','fit13','fit14','fit15','fit16')):
        raise ValueError('Only fixed operations admitted')
    for path, sha in ((ARCHIVE, ARCHIVE_SHA), (SOURCE, SOURCE_SHA)):
        if path.is_symlink() or digest(path) != sha:
            raise ValueError('Pinned input mismatch')
    out = BASE / (('body157-' if job['operation'] in ('fit06','fit07','fit08','fit09','fit10','fit11','fit12','fit13','fit14','fit15','fit16') else 'body156-') + job['operation'])
    if out.exists():
        raise ValueError('Never overwrite evidence')
    return out


def native_source():
    native = ASSETS / MEMBER
    with zipfile.ZipFile(ARCHIVE) as archive:
        payload = archive.read(MEMBER)
    if native.exists():
        if native.is_symlink() or native.read_bytes() != payload:
            raise ValueError('Extracted source differs')
    else:
        native.parent.mkdir(parents=True, exist_ok=True)
        native.write_bytes(payload)
    return native


def main():
    import bpy
    job = json.loads(Path(sys.argv[sys.argv.index('--') + 1]).read_text())
    out = validate(job)
    out.mkdir()
    if job['operation']=='review05':
        review(out)
        return
    native = native_source()
    if job['operation'].startswith('fit'):
        fit(out, native, int(job['operation'][-2:]))
        return
    bpy.ops.wm.open_mainfile(filepath=str(native), load_ui=False, use_scripts=False)
    result = {'source_sha256': digest(native), 'objects': inventory(),
              'collections': list(bpy.data.collections.keys()),
              'texts': {t.name: t.as_string() for t in bpy.data.texts if any(k in t.name.lower() for k in ('readme', 'license', 'credit'))}}
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE), load_ui=False, use_scripts=False)
    result['accepted_objects'] = inventory()
    result['protected'] = protected()
    (out / 'inventory.json').write_text(json.dumps(result, indent=2) + '\n')


def fit(out, native, variant):
    import bpy
    import bmesh
    from mathutils import Matrix, Vector
    from character_assembly import material
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE), load_ui=False, use_scripts=False)
    before = protected()
    if variant>=6:
        # Coherent reversible assembly scale: no accepted local data is edited.
        transform=Matrix.Translation((0,0,-1.9))@Matrix.Scale(.88,4)@Matrix.Translation((0,0,1.9))
        for name in [n for n in before if n not in ('MF_natural147_hair_long hair main','MF_natural147_hair_long hair strands')]+['MF_natural147_hair_retarget']:
            ob=bpy.data.objects[name];ob.matrix_world=transform@ob.matrix_world
        bpy.context.view_layer.update()
    with bpy.data.libraries.load(str(native), link=False) as (a, b):
        b.objects = ['GEO-body_female_realistic']
    body = b.objects[0]
    bpy.context.scene.collection.objects.link(body)
    metadata = {key: getattr(body.asset_data, key, None) for key in ('author','description','license','copyright')} if body.asset_data else {}
    body.animation_data_clear()
    # Keep authored base topology. The source multires sculpt remains in library.
    for mod in list(body.modifiers):
        body.modifiers.remove(mod)
    world = body.matrix_world.copy()
    original = [world @ v.co for v in body.data.vertices]
    xcenter = (max(v.x for v in original) + min(v.x for v in original)) / 2
    scale = 8.6
    top = max(v.z for v in original)
    zoffset = 1.3302977085 - top * scale
    if variant>=9:zoffset-=.55
    for v, p in zip(body.data.vertices, original):
        v.co = ((p.x-xcenter)*scale, p.y*scale + .15, p.z*scale+zoffset)
    body.matrix_world = Matrix.Identity(4)
    body.name = 'MF_studio_adult_body'
    if variant==8:
        samples={}
        for ob in (body,bpy.data.objects['MF_continuous_head_neck']):
            points=[ob.matrix_world@v.co for v in ob.data.vertices]
            rows=[]
            for z in (.2,0,-.2,-.4,-.6,-.8,-1.,-1.2,-1.4,-1.6,-1.8,-2.,-2.4,-3.,-3.5,-4.,-4.5):
                band=[v for v in points if abs(v.z-z)<.08]
                if band:rows.append({'z':z,'xmin':min(p.x for p in band),'xmax':max(p.x for p in band),'ymin':min(p.y for p in band),'ymax':max(p.y for p in band)})
            samples[ob.name]=rows
        (out/'sections.json').write_text(json.dumps(samples,indent=2)+'\n')
        return
    cutoff=-1.84
    if variant>=9:
        bust=bpy.data.objects['MF_continuous_head_neck']
        group=bust.vertex_groups.new(name='MF_body157_visible_neck')
        kept=[v.index for v in bust.data.vertices if (bust.matrix_world@v.co).z>=-1.36]
        group.add(kept,1.,'REPLACE')
        mask=bust.modifiers.new('Reversible lower bust replacement','MASK');mask.vertex_group=group.name
        cutoff=min((bust.matrix_world@bust.data.vertices[i].co).z for i in kept)+.06
        if variant>=15:cutoff=-1.65
    # Diagnostic interface: preserve source/local data, clip donor only.
    bm = bmesh.new(); bm.from_mesh(body.data)
    bmesh.ops.bisect_plane(bm, geom=list(bm.verts)+list(bm.edges)+list(bm.faces),
        plane_co=(0,0,cutoff), plane_no=(0,0,1), clear_outer=True, dist=.00001)
    bm.to_mesh(body.data); bm.free()
    if variant>=15:
        bridge_donor(body,bpy.data.objects['MF_continuous_head_neck'])
    elif variant >= 2:
        join_donor(body, bpy.data.objects['MF_continuous_head_neck'], short=variant>=6, neck=variant>=9, cutoff=cutoff, boundary=variant>=11)
    for p in body.data.polygons: p.use_smooth=True
    sub=body.modifiers.new('Body display subdivision','SUBSURF');sub.levels=1
    if 3<=variant<13 or variant>=15:
        group=body.vertex_groups.new(name='MF_interface_normals')
        for v in body.data.vertices:
            w=max(0.,min(1.,(v.co.z+1.65)/.28)) if variant>=15 else max(0.,min(1.,(v.co.z-(cutoff-.38))/.32))
            if w:group.add([v.index],w,'REPLACE')
        transfer=body.modifiers.new('Boundary normal continuity','DATA_TRANSFER')
        transfer.object=bpy.data.objects['MF_continuous_head_neck']
        transfer.use_loop_data=True;transfer.data_types_loops={'CUSTOM_NORMAL'}
        transfer.loop_mapping='POLYINTERP_NEAREST';transfer.vertex_group=group.name
    if 13<=variant<15:
        bust=bpy.data.objects['MF_continuous_head_neck']
        blend=bust.vertex_groups.new(name='MF_body157_neck_interface')
        for v in bust.data.vertices:
            z=(bust.matrix_world@v.co).z
            w=max(0.,min(1.,(-1.05-z)/.20))
            if w:blend.add([v.index],w,'REPLACE')
        shrink=bust.modifiers.new('Reversible neck boundary fit','SHRINKWRAP')
        shrink.target=body;shrink.vertex_group=blend.name;shrink.wrap_method='NEAREST_SURFACEPOINT';shrink.offset=.002
        normal=bust.modifiers.new('Neck boundary normals','DATA_TRANSFER')
        normal.object=body;normal.use_loop_data=True;normal.data_types_loops={'CUSTOM_NORMAL'}
        normal.loop_mapping='POLYINTERP_NEAREST';normal.vertex_group=blend.name
    clay=material('MF_body156_clay',(.34,.31,.28))
    body.data.materials.clear();body.data.materials.append(clay)
    body.hide_render=False;body.hide_set(False)
    scene=bpy.context.scene
    scene.render.engine='CYCLES';scene.cycles.samples=12;scene.cycles.use_denoising=True;scene.cycles.seed=0
    scene.render.resolution_x=480;scene.render.resolution_y=800;scene.render.resolution_percentage=100
    scene.view_layers[0].material_override=clay
    for ob in scene.objects:
        if ob.type=='LIGHT':ob.hide_render=True
    camera=bpy.data.objects.new('MF_body156_camera',bpy.data.cameras.new('MF_body156_camera'))
    scene.collection.objects.link(camera);scene.camera=camera;camera.data.type='ORTHO'
    lights=[]
    for x,power in ((-7,2200),(7,1400)):
        light=bpy.data.objects.new('MF_body156_softbox',bpy.data.lights.new('MF_body156_softbox','AREA'))
        scene.collection.objects.link(light);light.data.energy=power;light.data.shape='DISK';light.data.size=9
        lights.append((light,Vector((x,-9,7))))
    def render(label,angle,center=(0,0,-5.8),size=16.5,write=True):
        target=Vector(center);rot=Matrix.Rotation(__import__('math').radians(angle),3,'Z')
        camera.data.ortho_scale=size;camera.location=target+rot@Vector((0,-25,.5))
        camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler()
        for light,offset in lights:
            light.location=target+rot@offset;light.rotation_euler=(target-light.location).to_track_quat('-Z','Y').to_euler()
        if write:
            scene.render.filepath=str(out/(label+'.png'));bpy.ops.render.render(write_still=True)
    for label,angle in [('front',0),('side',90),('three-quarter',-40),('other-three-quarter',40),('back',180)]:render(label,angle)
    render('interface',-35,(0,0,-1.65),6)
    pose_result = None
    if variant >= 2:
        pose_result = pose_screen(body, before, render, sharpen=variant>=6, neck=variant>=9)
    assert all(protected()[k]==v for k,v in before.items())
    sealed = None
    if variant in (3,4,7,10,12,14,16):
        bpy.context.preferences.filepaths.save_version=0
        render('front',0,write=False)
        bpy.ops.wm.save_as_mainfile(filepath=str(out/'adult-body-fit.blend'),check_existing=False)
        sealed=verify_saved(out/'adult-body-fit.blend',before,pose_result['pose_matrices'])
        body=bpy.data.objects['MF_studio_adult_body']
    result={'status':'INTERNAL_FIT_NOT_ACCEPTED','asset_metadata':metadata,'scale':scale,'zoffset':zoffset,'upper_assembly_scale':.88 if variant>=6 else 1.,'lower_bust_display_mask':variant>=9,
        'body_vertices':len(body.data.vertices),'source_sha256':digest(native),'protected':before,
        'bounds':next(r['bounds'] for r in inventory() if r['name']==body.name),
        'pose_screen':pose_result,'saved_verification':sealed,
        'rigged':variant>=2,'limits':['Body interface requires visual acceptance','Static pose is not animation qualification','Clay material override is diagnostic only']}
    (out/'result.json').write_text(json.dumps(result,indent=2)+'\n')


def bridge_donor(body,bust):
    """Connect actual evaluated neck boundary to the donor's open neck loop."""
    import bpy,bmesh,math
    from collections import Counter
    bpy.context.view_layer.update()
    ev=bust.evaluated_get(bpy.context.evaluated_depsgraph_get())
    counts=Counter(edge for p in ev.data.polygons for edge in p.edge_keys)
    indices={i for edge,count in counts.items() if count==1 for i in edge}
    points=[bust.matrix_world@ev.data.vertices[i].co for i in indices]
    points=[p for p in points if p.z<-1.15]
    assert len(points)>12
    cy=(min(p.y for p in points)+max(p.y for p in points))/2
    angle=lambda p:math.atan2(p.y-cy,p.x)
    points.sort(key=angle)
    bm=bmesh.new();bm.from_mesh(body.data)
    lower=sorted({v for e in bm.edges if e.is_boundary for v in e.verts if v.co.z>-1.651},key=lambda v:angle(v.co))
    assert len(lower)>8
    upper=[bm.verts.new(p) for p in points]
    i=j=0
    while i<len(upper) or j<len(lower):
        ai=angle(upper[(i+1)%len(upper)].co)+(2*math.pi if i+1>=len(upper) else 0) if i<len(upper) else float('inf')
        aj=angle(lower[(j+1)%len(lower)].co)+(2*math.pi if j+1>=len(lower) else 0) if j<len(lower) else float('inf')
        if ai<=aj:
            bm.faces.new((upper[i%len(upper)],upper[(i+1)%len(upper)],lower[j%len(lower)]));i+=1
        else:
            bm.faces.new((upper[i%len(upper)],lower[(j+1)%len(lower)],lower[j%len(lower)]));j+=1
    crease=bm.edges.layers.float.get('crease_edge') or bm.edges.layers.float.new('crease_edge')
    upper_set=set(upper)
    for e in bm.edges:
        if all(v in upper_set for v in e.verts):e[crease]=1.
    assert all(len(e.link_faces)<=2 for e in bm.edges), 'Nonmanifold bridge'
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
    bm.to_mesh(body.data);bm.free();body.data.update()


def join_donor(body, bust, short=False, neck=False, cutoff=-1.84, boundary=False):
    """Fit donor-only terminal ring to fixed accepted bust boundary."""
    import math
    from mathutils import Vector
    points=[bust.matrix_world@v.co for v in bust.data.vertices]
    if neck:points=[p for p in points if p.z>=-1.36]
    bottom=min(p.z for p in points)
    ring=[p for p in points if p.z<bottom+(.035 if neck else .0002)]
    if boundary:
        import bpy
        from collections import Counter
        bpy.context.view_layer.update()
        evaluated=bust.evaluated_get(bpy.context.evaluated_depsgraph_get())
        counts=Counter(edge for p in evaluated.data.polygons for edge in p.edge_keys)
        indices={i for edge,count in counts.items() if count==1 for i in edge}
        ring=[bust.matrix_world@evaluated.data.vertices[i].co for i in indices]
        ring=[p for p in ring if p.z<-1.15]
        assert len(ring)>12
    assert len(ring)>12
    cy=(min(p.y for p in ring)+max(p.y for p in ring))/2
    ring.sort(key=lambda p:math.atan2(p.y-cy,p.x))
    angles=[math.atan2(p.y-cy,p.x) for p in ring]
    import bisect
    for v in body.data.vertices:
        t=max(0.,min(1.,(v.co.z-(cutoff-.5))/.5)) if neck else max(0.,min(1.,(v.co.z+2.49)/.65)) if short else max(0.,min(1.,(v.co.z+2.85)/1.01))
        if t==0:continue
        a=math.atan2(v.co.y-cy,v.co.x)
        j=bisect.bisect_left(angles,a)%len(ring);k=(j-1)%len(ring)
        lo=angles[k];hi=angles[j]
        if hi<=lo:hi+=2*math.pi
        aa=a if a>=lo else a+2*math.pi
        u=max(0.,min(1.,(aa-lo)/(hi-lo))) if hi>lo else 0
        target=ring[k].lerp(ring[j],u)
        w=t*t*(3-2*t)
        v.co.x=(1-w)*v.co.x+w*target.x
        v.co.y=(1-w)*v.co.y+w*target.y
        v.co.z=(1-w)*v.co.z+w*(target.z+.035) if boundary else v.co.z-.06*t
    body.data.update()


def chest_blend(z):
    t=max(0.,min(1.,(z+3.05)/1.15))
    return t*t*(3-2*t)


def sharpen_weights(weights, power=3.):
    transformed={key:value**power for key,value in weights.items()}
    total=sum(transformed.values())
    return {key:value/total for key,value in transformed.items()} if total else weights


def pose_screen(body, before, render, sharpen=False, neck=False):
    import bpy
    import math
    from mathutils import Matrix, Vector
    arm=bpy.data.armatures.new('MF_body156_fit_rig')
    rig=bpy.data.objects.new(arm.name,arm);bpy.context.scene.collection.objects.link(rig)
    bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);bpy.context.view_layer.objects.active=rig
    bpy.ops.object.mode_set(mode='EDIT')
    definitions={
        'pelvis':((0,.2,-6.1),(0,.2,-4.9),None),
        'spine':((0,.2,-4.9),(0,.17,-3.55),'pelvis'),
        'chest':((0,.17,-3.55),(0,.15,-1.7),'spine'),
    }
    for side,s in [('L',1),('R',-1)]:
        definitions.update({
            'thigh.'+side:((s*.79,.16,-6.05),(s*.85,-.03,-9.22),'pelvis'),
            'shin.'+side:((s*.85,-.03,-9.22),(s*.85,.16,-12.18),'thigh.'+side),
            'foot.'+side:((s*.85,.16,-12.18),(s*.85,-.92,-12.62),'shin.'+side),
            'upperarm.'+side:((s*1.65,.12,-2.25),(s*2.48,-.10,-4.16),'chest'),
            'forearm.'+side:((s*2.48,-.10,-4.16),(s*3.14,-.33,-5.52),'upperarm.'+side),
            'hand.'+side:((s*3.14,-.33,-5.52),(s*3.52,-.46,-6.40),'forearm.'+side),
        })
    if neck:
        for side,s in [('L',1),('R',-1)]:
            definitions['upperarm.'+side]=((s*1.55,.12,-1.65),(s*2.48,-.10,-4.05),'chest')
            definitions['forearm.'+side]=((s*2.48,-.10,-4.05),(s*3.14,-.33,-5.52),'upperarm.'+side)
        definitions={n:((h[0],h[1],h[2]-.55),(t[0],t[1],t[2]-.55),p) for n,(h,t,p) in definitions.items()}
    for name,(head,tail,parent) in definitions.items():
        bone=arm.edit_bones.new(name);bone.head=head;bone.tail=tail
        if parent:bone.parent=arm.edit_bones[parent]
    bpy.ops.object.mode_set(mode='OBJECT')
    body.select_set(True);bpy.context.view_layer.objects.active=rig
    bpy.ops.object.parent_set(type='ARMATURE_AUTO')
    mod=next(m for m in body.modifiers if m.type=='ARMATURE')
    # Armature before subdivision; fit ring stays with the protected bust/chest.
    bpy.context.view_layer.objects.active=body
    while body.modifiers.find(mod.name)>0:
        bpy.ops.object.modifier_move_up(modifier=mod.name)
    mod.use_deform_preserve_volume=True
    bone_groups={g.index:g for g in body.vertex_groups if g.name in arm.bones}
    for v in body.data.vertices:
        w=max(0.,min(1.,(v.co.z+2.)/.64)) if neck else chest_blend(v.co.z)
        if w:
            old_chest=next((g.weight for g in v.groups if g.group==body.vertex_groups['chest'].index),0.)
            for g in list(v.groups):
                if g.group in bone_groups:bone_groups[g.group].add([v.index],g.weight*(1-w),'REPLACE')
            body.vertex_groups['chest'].add([v.index],old_chest*(1-w)+w,'REPLACE')
    unweighted=[v.index for v in body.data.vertices if sum(g.weight for g in v.groups if g.group in bone_groups)<.001]
    if sharpen:
        for v in body.data.vertices:
            if abs(v.co.x)>2.05 and v.co.z<-3.1:
                weights={g.group:g.weight for g in v.groups if g.group in bone_groups}
                for index,weight in sharpen_weights(weights).items():bone_groups[index].add([v.index],weight,'REPLACE')
    assert not unweighted, ('Unweighted body',len(unweighted))
    protected_roots=[bpy.data.objects[n] for n in before if n not in ('MF_natural147_hair_long hair main','MF_natural147_hair_long hair strands')]
    protected_roots.append(bpy.data.objects['MF_natural147_hair_retarget'])
    original_world={ob.name:ob.matrix_world.copy() for ob in protected_roots}
    rest=rig.pose.bones['chest'].matrix.copy()
    for ob in protected_roots:
        c=ob.constraints.new('CHILD_OF');c.name='MF body fit chest attachment'
        c.target=rig;c.subtarget='chest';c.inverse_matrix=rest.inverted()
    bpy.context.view_layer.update()
    attachment_error=max(abs(ob.matrix_world[i][j]-original_world[ob.name][i][j]) for ob in protected_roots for i in range(4) for j in range(4))
    assert attachment_error<1e-4, attachment_error
    def attach():
        bpy.context.view_layer.update()
    def evaluated():
        bpy.context.view_layer.update();ev=body.evaluated_get(bpy.context.evaluated_depsgraph_get())
        return [tuple(v.co) for v in ev.data.vertices]
    neutral=evaluated()
    def aim(name,target):
        bone=rig.pose.bones[name]
        q=(bone.tail-bone.head).normalized().rotation_difference(Vector(target).normalized())
        mat=q.to_matrix().to_4x4()@bone.matrix;mat.translation=bone.head;bone.matrix=mat
        bpy.context.view_layer.update()
    rig.pose.bones['spine'].rotation_mode='XYZ';rig.pose.bones['spine'].rotation_euler.x=.12
    for side,s in [('L',1),('R',-1)]:
        aim('thigh.'+side,(s*.22,-1,-.35));aim('shin.'+side,(0,.20,-1))
        aim('upperarm.'+side,(s*.15,-.38,-1));aim('forearm.'+side,(-s*.18,-1,-.10))
    attach()
    posed=evaluated();assert all(math.isfinite(v) for p in posed for v in p)
    render('seated-three-quarter',-45,(0,-.8,-4.9),14.5)
    render('seated-side',90,(0,-.8,-4.9),14.5)
    recipe={b.name:[list(row) for row in b.matrix_basis] for b in rig.pose.bones}
    for b in rig.pose.bones:b.matrix_basis=Matrix.Identity(4)
    attach();returned=evaluated()
    error=max((Vector(a)-Vector(b)).length for a,b in zip(neutral,returned))
    assert error<1e-5
    return {'bones':len(arm.bones),'unweighted':len(unweighted),'neutral_return_max_error':error,
            'neutral_attachment_matrix_error':attachment_error,
            'pose_matrices':recipe,'limits':['Coarse body weights with boundary correction; not final performance rig','No finger articulation or actual tack contacts','Preserved upper bust moves rigidly with chest; assembly-only lower-neck/shoulder replacement when enabled']}


def verify_saved(native,before,recipe):
    import bpy
    from mathutils import Matrix,Vector
    bpy.ops.wm.open_mainfile(filepath=str(native),load_ui=False,use_scripts=False)
    assert all(protected()[n]==v for n,v in before.items())
    rig=bpy.data.objects['MF_body156_fit_rig'];body=bpy.data.objects['MF_studio_adult_body']
    bust=bpy.data.objects['MF_continuous_head_neck']
    neutral=bust.matrix_world.copy()
    def coords():
        bpy.context.view_layer.update()
        ev=body.evaluated_get(bpy.context.evaluated_depsgraph_get())
        return [tuple(v.co) for v in ev.data.vertices]
    neutral_body=coords()
    for n,m in recipe.items():rig.pose.bones[n].matrix_basis=Matrix(m)
    posed=coords()
    bust_moved=max(abs(bust.matrix_world[i][j]-neutral[i][j]) for i in range(4) for j in range(4))
    assert bust_moved>.01
    moved=sum((Vector(a)-Vector(b)).length>.001 for a,b in zip(neutral_body,posed));assert moved>100
    for bone in rig.pose.bones:bone.matrix_basis=Matrix.Identity(4)
    returned=coords();err=max((Vector(a)-Vector(b)).length for a,b in zip(neutral_body,returned));assert err<1e-5
    assert all(protected()[n]==v for n,v in before.items())
    return {'native_sha256':digest(native),'reopened':True,'local_protected_data_exact':True,
            'posed_body_vertices_moved':moved,'bust_matrix_change':bust_moved,'body_neutral_return_max_error':err,
            'source_unchanged':digest(SOURCE)==SOURCE_SHA}


def review(out):
    import bpy
    import math
    from mathutils import Matrix,Vector
    parent=BASE/'body156-fit04'
    native=parent/'adult-body-fit.blend'
    expected='644d7109c379f78092bc5a897aa1e81628b17f5f877cea48a3ec492598dc278c'
    assert not native.is_symlink() and digest(native)==expected
    data=json.loads((parent/'result.json').read_text())
    bpy.ops.wm.open_mainfile(filepath=str(native),load_ui=False,use_scripts=False)
    scene=bpy.context.scene;camera=scene.camera
    lights=sorted([o for o in scene.objects if o.type=='LIGHT' and o.name.startswith('MF_body156_softbox')],key=lambda o:o.name)
    def render(label,angle,posed=False,close=False):
        center=(0,0,-1.65) if close else (0,-.8,-4.9) if posed else (0,0,-5.5)
        target=Vector(center);rot=Matrix.Rotation(math.radians(angle),3,'Z')
        camera.data.ortho_scale=6 if close else 14.5 if posed else 15.7
        camera.location=target+rot@Vector((0,-25,.5))
        camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler()
        for light,x in zip(lights,(-7,7)):
            light.location=target+rot@Vector((x,-9,7))
            light.rotation_euler=(target-light.location).to_track_quat('-Z','Y').to_euler()
        scene.render.filepath=str(out/(label+'.png'));bpy.ops.render.render(write_still=True)
    for label,angle in [('front',0),('left',-40),('right',40),('back',180),('side',90)]:render(label,angle)
    render('interface',-35,close=True)
    rig=bpy.data.objects['MF_body156_fit_rig']
    for n,m in data['pose_screen']['pose_matrices'].items():rig.pose.bones[n].matrix_basis=Matrix(m)
    bpy.context.view_layer.update()
    render('seated-three-quarter',-45,posed=True);render('seated-side',90,posed=True)
    assert all(protected()[n]==v for n,v in data['protected'].items())
    assert digest(native)==expected
    (out/'result.json').write_text(json.dumps({'parent_native_sha256':expected,'protected_local_data_exact':True,'native_unchanged':True,'purpose':'Adult proportions and static seated reach; not finished skin or animation'},indent=2)+'\n')


if __name__ == '__main__':
    main()
