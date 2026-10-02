"""Pinned Blender Studio body inspection and accepted-bust fitting operations."""
import json
from pathlib import Path
import sys
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parent))
from character_assembly import BASE, SOURCE, SOURCE_SHA, digest, inventory, protected as visible_protected

ROOT = Path(__file__).resolve().parents[4]
ASSETS = ROOT / '.runtime/assets/series01-body-blender-studio'
ARCHIVE = ASSETS / 'human-base-meshes-bundle-v1.4.1.zip'
ARCHIVE_SHA = '811f43accbb31a88266d932f8f5563b2d13586fca0ba2693aad1f5fe582b3515'
MEMBER = 'human-base-meshes-bundle-v1.4.1/human_base_meshes_bundle.blend'


def protected():
    """Keep hashing the accepted control source even when a derivative renders."""
    import bpy
    ob=bpy.data.objects.get('MF_continuous_head_neck')
    hidden=ob.hide_render if ob else False
    try:
        if ob:ob.hide_render=False
        return visible_protected()
    finally:
        if ob:ob.hide_render=hidden


def validate(job):
    if job not in tuple({'operation': name} for name in ('inspect01','fit01','fit02','fit03','fit04','review05','fit06','fit07','fit08','fit09','fit10','fit11','fit12','fit13','fit14','fit15','fit16','fit17','fit18','fit19','fit20','fit21','fit22','fit23','fit24','fit25','fit26','fit27','fit28','fit29','fit30','fit31','fit32','fit33')):
        raise ValueError('Only fixed operations admitted')
    for path, sha in ((ARCHIVE, ARCHIVE_SHA), (SOURCE, SOURCE_SHA)):
        if path.is_symlink() or digest(path) != sha:
            raise ValueError('Pinned input mismatch')
    out = BASE / (('body158-' if job['operation'] in ('fit17','fit18','fit19','fit20','fit21','fit22','fit23','fit24','fit25','fit26','fit27') else 'body157-' if job['operation'] in ('fit06','fit07','fit08','fit09','fit10','fit11','fit12','fit13','fit14','fit15','fit16') else 'body156-') + job['operation'])
    if job['operation'] in ('fit28','fit29','fit30','fit31','fit32','fit33'):out=BASE/('body159-'+job['operation'])
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
    if variant>=30:
        # Refine donor topology before cutting, so the join does not terminate
        # in a sparse, faceted shoulder ring. This edits only the derivative.
        refine=body.modifiers.new('Donor topology for shoulder connection','SUBSURF');refine.levels=1
        bpy.context.view_layer.update()
        evaluated=body.evaluated_get(bpy.context.evaluated_depsgraph_get())
        refined=bpy.data.meshes.new_from_object(evaluated)
        body.modifiers.clear();body.data=refined
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
    if 9<=variant<28:
        bust=bpy.data.objects['MF_continuous_head_neck']
        group=bust.vertex_groups.new(name='MF_body157_visible_neck')
        kept=[v.index for v in bust.data.vertices if (bust.matrix_world@v.co).z>=(-1.05 if variant>=18 else -1.36)]
        group.add(kept,1.,'REPLACE')
        mask=bust.modifiers.new('Reversible lower bust replacement','MASK');mask.vertex_group=group.name
        if variant>=22:
            # Interpolate the cut on edges instead of retaining a jagged stair.
            for v in bust.data.vertices:
                z=(bust.matrix_world@v.co).z
                group.add([v.index],max(0.,min(1.,(z+1.10)/.10)),'REPLACE')
            mask.use_smooth=True;mask.threshold=.5
        if variant>=21:
            bust.hide_set(False);bust.hide_viewport=False
            bpy.context.view_layer.update()
            ev=bust.evaluated_get(bpy.context.evaluated_depsgraph_get())
            print('NECK_DIAGNOSTIC',json.dumps({'mask':mask.vertex_group,'kept':len(kept),'source_vertices':len(bust.data.vertices),'evaluated_vertices':len(ev.data.vertices),'matrix':[list(r) for r in bust.matrix_world],'zrange':[min((bust.matrix_world@v.co).z for v in ev.data.vertices),max((bust.matrix_world@v.co).z for v in ev.data.vertices)]}))
        cutoff=min((bust.matrix_world@bust.data.vertices[i].co).z for i in kept)+.06
        if variant>=15:cutoff=-1.65
        if variant>=18:cutoff=-1.30
    if variant>=28:cutoff=-2.40
    # Diagnostic interface: preserve source/local data, clip donor only.
    bm = bmesh.new(); bm.from_mesh(body.data)
    bmesh.ops.bisect_plane(bm, geom=list(bm.verts)+list(bm.edges)+list(bm.faces),
        plane_co=(0,0,cutoff), plane_no=(0,0,1), clear_outer=True, dist=.00001)
    bm.to_mesh(body.data); bm.free()
    if variant>=19:
        blend_neck_surface(body,bpy.data.objects['MF_continuous_head_neck'],cutoff,pin=variant>=20,ordered=variant>=22,tangent=variant>=23)
    elif variant>=15:
        bridge_donor(body,bpy.data.objects['MF_continuous_head_neck'],cutoff=cutoff,high=variant>=18)
    elif variant >= 2:
        join_donor(body, bpy.data.objects['MF_continuous_head_neck'], short=variant>=6, neck=variant>=9, cutoff=cutoff, boundary=variant>=11)
    if 26<=variant<28:
        import math
        for v in body.data.vertices:
            x,y,z=v.co;ax=abs(x)
            if y<.05 and .05<ax<1.50 and z< -1.4:
                ridge=-1.89-.12*ax+.06*math.sin(ax*2.)
                weight=math.sin(math.pi*(ax-.05)/1.45)**2
                v.co.y-=.075*weight*math.exp(-((z-ridge)/.14)**2)
    for p in body.data.polygons: p.use_smooth=True
    sub=body.modifiers.new('Body display subdivision','SUBSURF');sub.levels=1
    if 3<=variant<13 or 15<=variant<=16 or 20<=variant<23:
        group=body.vertex_groups.new(name='MF_interface_normals')
        for v in body.data.vertices:
            w=max(0.,min(1.,(v.co.z+1.30)/.26)) if variant>=20 else max(0.,min(1.,(v.co.z+1.65)/.28)) if variant>=15 else max(0.,min(1.,(v.co.z-(cutoff-.38))/.32))
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
    integration=None
    if variant>=24:
        integration=unify_surface(body,bpy.data.objects['MF_continuous_head_neck'])
    if variant>=30:
        group=body.vertex_groups.new(name='MF_lower_shoulder_connection')
        for v in body.data.vertices:
            z=v.co.z
            upper=-1.84
            if variant>=32:upper+=.22*max(0.,min(1.,(abs(v.co.x)-1.05)/.40))
            w=max(0.,min(1.,(z+3.05)/.30,(upper-z)/.12))
            if w:group.add([v.index],w,'REPLACE')
        smooth=body.modifiers.new('Lower connection fairing only','SMOOTH')
        smooth.vertex_group=group.name;smooth.factor=.65;smooth.iterations=40 if variant>=32 else 18
    if 25<=variant<28:
        group=body.vertex_groups.new(name='MF_neck_surface_fairing')
        for v in body.data.vertices:
            z=v.co.z
            w=max(0.,min(1.,(z+1.85)/.35,(-.80-z)/.25))
            if variant>=26:w*=max(0.,min(1.,(1.4-abs(v.co.x))/.45))
            if w:group.add([v.index],w,'REPLACE')
        smooth=body.modifiers.new('Continuous neck fairing','SMOOTH')
        smooth.vertex_group=group.name;smooth.factor=1.;smooth.iterations=35
    if variant>=26:
        crease=body.data.attributes.get('crease_edge') or body.data.attributes.new('crease_edge','FLOAT','EDGE')
        for e in body.data.edges:
            if all(body.data.vertices[i].co.z>(-1.899 if variant>=28 else -.80) for i in e.vertices):crease.data[e.index].value=1.
        sub=body.modifiers.new('Donor body continuity with protected face edges','SUBSURF');sub.levels=1;sub.render_levels=1
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
    if variant>=28:
        # Match the accepted source and derivative, not only the failed prior fit.
        render('neck-front',0,(0,0,-1.2),4.7)
        render('neck-other-side',35,(0,0,-1.2),4.7)
        hair=[ob for ob in scene.objects if ob.type=='CURVES' and not ob.hide_render]
        for ob in hair:ob.hide_render=True
        render('neck-back',180,(0,0,-1.2),4.7)
        for ob in hair:ob.hide_render=False
        bust=bpy.data.objects['MF_continuous_head_neck'];bust.hide_render=False;body.hide_render=True
        render('accepted-neck-front',0,(0,0,-1.2),4.7)
        render('accepted-interface',-35,(0,0,-1.65),6)
        bust.hide_render=True;body.hide_render=False
    pose_result = None
    if variant >= 2:
        pose_result = pose_screen(body, before, render, sharpen=variant>=6, neck=variant>=9,hinge=variant>=20,shoulder=variant>=32)
    face_control=check_face_control(body) if variant>=26 else None
    assert all(protected()[k]==v for k,v in before.items())
    sealed = None
    if variant in (3,4,7,10,12,14,16,27,29,31,33):
        bpy.context.preferences.filepaths.save_version=0
        render('front',0,write=False)
        bpy.ops.wm.save_as_mainfile(filepath=str(out/'adult-body-fit.blend'),check_existing=False)
        sealed=verify_saved(out/'adult-body-fit.blend',before,pose_result['pose_matrices'])
        body=bpy.data.objects['MF_studio_adult_body']
    result={'status':'INTERNAL_FIT_NOT_ACCEPTED','asset_metadata':metadata,'scale':scale,'zoffset':zoffset,'upper_assembly_scale':.88 if variant>=6 else 1.,'lower_bust_display_mask':9<=variant<28,
        'body_vertices':len(body.data.vertices),'source_sha256':digest(native),'protected':before,'complete_accepted_bust_retained':variant>=28,
        'lower_connection_fairing':variant>=30,'lateral_shoulder_deforms':variant>=32,
        'bounds':next(r['bounds'] for r in inventory() if r['name']==body.name),
        'pose_screen':pose_result,'saved_verification':sealed,'surface_integration':integration,'face_control':face_control,
        'rigged':variant>=2,'limits':['Body interface requires visual acceptance','Static pose is not animation qualification','Clay material override is diagnostic only']}
    (out/'result.json').write_text(json.dumps(result,indent=2)+'\n')


def unify_surface(body,bust):
    """Continuous derivative with original face UVs and linked facial keys.

    The pinned head remains the control source, not destructively applied data.
    Join evaluated geometry at exact matching neck vertices, preserving a map
    to all source head vertices for expression deltas and verification.
    """
    import bpy,bmesh
    from mathutils.kdtree import KDTree
    bpy.context.view_layer.update()
    ev=bust.evaluated_get(bpy.context.evaluated_depsgraph_get())
    head=ev.to_mesh()
    vertices=[bust.matrix_world@v.co for v in head.vertices]
    faces=[tuple(p.vertices) for p in head.polygons]
    head_count=len(vertices);head_faces=len(faces)
    slots=list(bust.data.materials)+list(body.data.materials)
    registry={tuple(round(c,5) for c in p):i for i,p in enumerate(vertices)}
    remap={};welded=0
    for v in body.data.vertices:
        key=tuple(round(c,5) for c in v.co)
        if key in registry:remap[v.index]=registry[key];welded+=1
        else:
            remap[v.index]=len(vertices);vertices.append(v.co.copy())
    faces.extend(tuple(remap[i] for i in p.vertices) for p in body.data.polygons)
    mesh=bpy.data.meshes.new('MF_continuous_character_surface');mesh.from_pydata(vertices,[],faces);mesh.update()
    for m in slots:mesh.materials.append(m)
    for i,p in enumerate(mesh.polygons):
        p.material_index=head.polygons[i].material_index if i<head_faces else len(bust.data.materials)
        p.use_smooth=True
    for layer in head.uv_layers:
        dest=mesh.uv_layers.new(name=layer.name)
        for i,item in enumerate(layer.data):dest.data[i].uv=item.uv
    body.data=mesh
    # The head is already dense. Subdividing it again needlessly changes likeness.
    for mod in list(body.modifiers):body.modifiers.remove(mod)
    tree=KDTree(len(bust.data.vertices))
    for v in bust.data.vertices:tree.insert(bust.matrix_world@v.co,v.index)
    tree.balance()
    mapping=[tree.find(p)[1] for p in vertices[:head_count]]
    body.shape_key_add(name='Basis')
    keys=bust.data.shape_keys.key_blocks;basis=keys[0]
    matrix=bust.matrix_world.to_3x3()
    for key in list(keys)[1:]:
        target=body.shape_key_add(name=key.name);target.slider_min=-1.;target.slider_max=1.
        for i,j in enumerate(mapping):target.data[i].co+=matrix@(key.data[j].co-basis.data[j].co)
        driver=target.driver_add('value').driver;driver.type='SCRIPTED'
        variable=driver.variables.new();variable.name='source';variable.type='SINGLE_PROP'
        variable.targets[0].id_type='KEY';variable.targets[0].id=bust.data.shape_keys
        variable.targets[0].data_path=key.path_from_id('value')
        driver.expression=f'source - {key.value!r}'
    # Validate face correspondence separately from source hashes.
    error=max((body.data.vertices[i].co-vertices[i]).length for i in range(head_count))
    assert welded>100 and error<1e-5
    bm=bmesh.new();bm.from_mesh(mesh)
    seam_z=min(v.z for v in vertices[:head_count])
    seam_edges=[e for e in bm.edges if all(abs(v.co.z-seam_z)<.001 for v in e.verts)]
    assert seam_edges and all(len(e.link_faces)==2 for e in seam_edges), 'Unwelded neck edge'
    bm.free();ev.to_mesh_clear()
    bust.hide_render=True
    body['accepted_head_vertex_count']=head_count
    return {'welded_vertices':welded,'head_vertex_count':head_count,'head_position_max_error':error,'linked_shape_keys':len(keys)-1,'source_retained_as_control':True,'continuous_neck_edges':len(seam_edges)}


def check_face_control(body):
    """Verify source-driven blink and exact rollback on evaluated derivative."""
    import bpy
    from mathutils import Vector
    source=bpy.data.objects['MF_continuous_head_neck']
    key=source.data.shape_keys.key_blocks['eyeBlinkLeft'];old=key.value
    def coords():
        source.data.update();bpy.context.view_layer.update()
        ev=body.evaluated_get(bpy.context.evaluated_depsgraph_get())
        return [tuple(v.co) for v in ev.data.vertices]
    neutral=coords()
    key.value=.35
    moved=coords()
    linked=body.data.shape_keys.key_blocks[key.name].value
    count=sum((Vector(a)-Vector(b)).length>1e-5 for a,b in zip(neutral,moved))
    key.value=old
    returned=coords();error=max((Vector(a)-Vector(b)).length for a,b in zip(neutral,returned))
    assert abs(linked-(.35-old))<1e-5 and count>10 and error<1e-5
    return {'source_blink_drives_derivative':True,'evaluated_vertices_moved':count,'neutral_return_max_error':error,'limits':'One linked blink checked; full expression and speech qualification not rerun'}


def blend_neck_surface(body,bust,cutoff,pin=False,ordered=False,tangent=False):
    """Resample the donor neck to the accepted boundary before connecting it.

    Equal-density quad strips avoid long fans between unrelated ring densities.
    Only the new body derivative changes; the accepted bust stays independent.
    """
    import bpy,bmesh,math,bisect
    from collections import Counter
    bpy.context.view_layer.update()
    ev=bust.evaluated_get(bpy.context.evaluated_depsgraph_get())
    counts=Counter(edge for p in ev.data.polygons for edge in p.edge_keys)
    indices={i for edge,n in counts.items() if n==1 for i in edge}
    points=[bust.matrix_world@ev.data.vertices[i].co for i in indices]
    points=[p for p in points if p.z<-.85]
    cy=(min(p.y for p in points)+max(p.y for p in points))/2
    angle=lambda p:math.atan2(p.y-cy,p.x)
    points.sort(key=angle)
    if ordered:
        adjacency={}
        for edge,n in counts.items():
            if n==1 and all((bust.matrix_world@ev.data.vertices[i].co).z<-.85 for i in edge):
                a,b=edge;adjacency.setdefault(a,[]).append(b);adjacency.setdefault(b,[]).append(a)
        assert all(len(v)==2 for v in adjacency.values()), 'Neck boundary must be closed loops'
        unused=set(adjacency);loops=[]
        while unused:
            start=min(unused);loop=[start];previous=None;current=start
            while True:
                candidates=[i for i in adjacency[current] if i!=previous]
                nxt=candidates[0]
                if nxt==start:break
                assert nxt not in loop
                loop.append(nxt);previous,current=current,nxt
            unused.difference_update(loop);loops.append(loop)
        print('NECK_LOOPS',list(map(len,loops)),flush=True)
        loop=max(loops,key=len)
        points=[bust.matrix_world@ev.data.vertices[i].co for i in loop]
        area=sum(a.x*b.y-b.x*a.y for a,b in zip(points,points[1:]+points[:1]))
        if area<0:points.reverse()
        start=min(range(len(points)),key=lambda i:angle(points[i]))
        points=points[start:]+points[:start]
    bm=bmesh.new();bm.from_mesh(body.data);bm.normal_update()
    lower=sorted({v for e in bm.edges if e.is_boundary for v in e.verts if v.co.z>cutoff-.001},key=lambda v:angle(v.co))
    assert len(lower)>8 and len(points)>12
    angles=[angle(v.co) for v in lower]
    def sample(a,normal=False):
        j=bisect.bisect_left(angles,a)%len(lower);k=(j-1)%len(lower)
        lo=angles[k];hi=angles[j]
        if hi<=lo:hi+=2*math.pi
        if a<lo:a+=2*math.pi
        if normal:return lower[k].normal.lerp(lower[j].normal,(a-lo)/(hi-lo)).normalized()
        return lower[k].co.lerp(lower[j].co,(a-lo)/(hi-lo))
    if tangent:
        from mathutils.kdtree import KDTree
        from mathutils import Vector
        tree=KDTree(len(ev.data.vertices))
        for v in ev.data.vertices:tree.insert(bust.matrix_world@v.co,v.index)
        tree.balance()
        def derivative(n,dz):
            den=max(.08,n.x*n.x+n.y*n.y)
            return Vector((max(-1.5,min(1.5,-n.z*n.x/den))*dz,max(-1.5,min(1.5,-n.z*n.y/den))*dz,dz))
    # Interpolate several densely matched rings instead of a single triangle fan.
    rows=[]
    for t in (0.,.2,.4,.6,.8,.97):
        row=[]
        for p in points:
            q=sample(angle(p));w=t*t*(3-2*t)
            r=p.lerp(q,w);r.z=p.z*(1-t)+q.z*t
            if tangent:
                n0=ev.data.vertices[tree.find(p)[1]].normal
                n1=sample(angle(p),normal=True);dz=q.z-p.z
                m0=derivative(n0,dz);m1=derivative(n1,dz)
                r=p*(2*t**3-3*t*t+1)+m0*(t**3-2*t*t+t)+q*(-2*t**3+3*t*t)+m1*(t**3-t*t)
            row.append(bm.verts.new(r))
        rows.append(row)
    for a,b in zip(rows,rows[1:]):
        for i in range(len(a)):
            j=(i+1)%len(a);bm.faces.new((a[i],a[j],b[j],b[i]))
    upper=rows[-1];i=j=0
    while i<len(upper) or j<len(lower):
        ai=angle(upper[(i+1)%len(upper)].co)+(2*math.pi if i+1>=len(upper) else 0) if i<len(upper) else float('inf')
        aj=angle(lower[(j+1)%len(lower)].co)+(2*math.pi if j+1>=len(lower) else 0) if j<len(lower) else float('inf')
        if ai<=aj:
            bm.faces.new((upper[i%len(upper)],upper[(i+1)%len(upper)],lower[j%len(lower)]));i+=1
        else:
            bm.faces.new((upper[i%len(upper)],lower[(j+1)%len(lower)],lower[j%len(lower)]));j+=1
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
    if pin:
        crease=bm.edges.layers.float.get('crease_edge') or bm.edges.layers.float.new('crease_edge')
        top=set(rows[0])
        for e in bm.edges:
            if all(v in top for v in e.verts):e[crease]=1.
    bm.to_mesh(body.data);bm.free();body.data.update()


def bridge_donor(body,bust,cutoff=-1.65,high=False):
    """Connect actual evaluated neck boundary to the donor's open neck loop."""
    import bpy,bmesh,math
    from collections import Counter
    bpy.context.view_layer.update()
    ev=bust.evaluated_get(bpy.context.evaluated_depsgraph_get())
    counts=Counter(edge for p in ev.data.polygons for edge in p.edge_keys)
    indices={i for edge,count in counts.items() if count==1 for i in edge}
    points=[bust.matrix_world@ev.data.vertices[i].co for i in indices]
    points=[p for p in points if p.z<(-.85 if high else -1.15)]
    assert len(points)>12
    cy=(min(p.y for p in points)+max(p.y for p in points))/2
    angle=lambda p:math.atan2(p.y-cy,p.x)
    points.sort(key=angle)
    bm=bmesh.new();bm.from_mesh(body.data)
    lower=sorted({v for e in bm.edges if e.is_boundary for v in e.verts if v.co.z>cutoff-.001},key=lambda v:angle(v.co))
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


def shoulder_chest_weight(x,z):
    """Continuous chest protection without a hard lateral source/donor cutoff."""
    w=max(0.,min(1.,(z+2.4)/.90))
    central=max(0.,min(1.,(.95-abs(x))/.30))*max(0.,min(1.,(z+2.4)/.30))
    return max(w,central)


def sharpen_weights(weights, power=3.):
    transformed={key:value**power for key,value in weights.items()}
    total=sum(transformed.values())
    return {key:value/total for key,value in transformed.items()} if total else weights


def pose_screen(body, before, render, sharpen=False, neck=False,hinge=False,shoulder=False):
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
        if v.index<body.get('accepted_head_vertex_count',0) and not shoulder:w=1.
        if shoulder:
            # Preserve neck identity; do not pin the lateral shoulder to the
            # chest while the immediately adjacent donor follows the arm.
            w=shoulder_chest_weight(v.co.x,v.co.z)
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
    if hinge:
        # A local elbow band, not hand edits or a new rig; same authored pose.
        mod.use_deform_preserve_volume=False
        for side,s in [('L',1),('R',-1)]:
            elbow=Vector(definitions['forearm.'+side][0])
            axis=(Vector(definitions['forearm.'+side][1])-elbow).normalized()
            for v in body.data.vertices:
                d=(v.co-elbow).dot(axis)
                if s*v.co.x>2.05 and -.7<d<.7:
                    t=max(0.,min(1.,(d+.20)/.4));w=t*t*(3-2*t)
                    for g in list(v.groups):
                        if g.group in bone_groups:bone_groups[g.group].remove([v.index])
                    body.vertex_groups['upperarm.'+side].add([v.index],1-w,'REPLACE')
                    body.vertex_groups['forearm.'+side].add([v.index],w,'REPLACE')
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
    if shoulder:
        render('seated-interface',-35,(0,-.2,-1.65),6)
        render('seated-neck-front',0,(0,-.2,-1.65),6)
    recipe={b.name:[list(row) for row in b.matrix_basis] for b in rig.pose.bones}
    for b in rig.pose.bones:b.matrix_basis=Matrix.Identity(4)
    attach();returned=evaluated()
    error=max((Vector(a)-Vector(b)).length for a,b in zip(neutral,returned))
    assert error<1e-5
    return {'bones':len(arm.bones),'unweighted':len(unweighted),'neutral_return_max_error':error,
            'neutral_attachment_matrix_error':attachment_error,
            'pose_matrices':recipe,'limits':['Coarse body weights with boundary correction; not final performance rig','No finger articulation or actual tack contacts','Lateral lower bust participates in shoulder deformation; central neck follows chest' if shoulder else 'Preserved upper bust moves rigidly with chest; assembly-only lower-neck/shoulder replacement when enabled']}


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
    face_control=check_face_control(body) if body.data.shape_keys else None
    return {'native_sha256':digest(native),'reopened':True,'local_protected_data_exact':True,
            'posed_body_vertices_moved':moved,'bust_matrix_change':bust_moved,'body_neutral_return_max_error':err,
            'source_unchanged':digest(SOURCE)==SOURCE_SHA,'face_control':face_control}


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
