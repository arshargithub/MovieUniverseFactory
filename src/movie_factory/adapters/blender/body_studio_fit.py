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
    if job in tuple({'operation':name} for name in ('hip58','hip59','hip61','hip62','hip63','hip64','hip66')):
        for path,sha in ((SOURCE,SOURCE_SHA),(BASE/'body164-legs57/adult-body-fit.blend','cedce781c0980ce387b925d4b1cab6b510a8dcdd42453d6da243131440924f2f')):
            if path.is_symlink() or digest(path)!=sha:raise ValueError('Pinned hip-correction input mismatch')
        out=BASE/(('body168-' if job['operation'] in ('hip63','hip64','hip66') else 'body166-')+job['operation'])
        if out.exists():raise ValueError('Never overwrite evidence')
        return out
    if job in tuple({'operation':name} for name in ('legs55','legs56','legs57')):
        for path,sha in ((SOURCE,SOURCE_SHA),(BASE/'body162-fit52/adult-body-fit.blend','8e9db951953034113e51c0be55f8acb39b96486826d0fa404a28631c5d08ce81')):
            if path.is_symlink() or digest(path)!=sha:raise ValueError('Pinned leg-repair input mismatch')
        out=BASE/('body164-'+job['operation'])
        if out.exists():raise ValueError('Never overwrite evidence')
        return out
    if job not in tuple({'operation': name} for name in ('inspect01','fit01','fit02','fit03','fit04','review05','fit06','fit07','fit08','fit09','fit10','fit11','fit12','fit13','fit14','fit15','fit16','fit17','fit18','fit19','fit20','fit21','fit22','fit23','fit24','fit25','fit26','fit27','fit28','fit29','fit30','fit31','fit32','fit33','fit34','fit35','fit36','fit37','fit38','fit39','fit40','fit41','fit42','fit43','fit44','fit45','fit46','fit47','verify48','inspect49','fit50','fit52','inspect53','inspect54')):
        raise ValueError('Only fixed operations admitted')
    for path, sha in ((ARCHIVE, ARCHIVE_SHA), (SOURCE, SOURCE_SHA)):
        if path.is_symlink() or digest(path) != sha:
            raise ValueError('Pinned input mismatch')
    out = BASE / (('body158-' if job['operation'] in ('fit17','fit18','fit19','fit20','fit21','fit22','fit23','fit24','fit25','fit26','fit27') else 'body157-' if job['operation'] in ('fit06','fit07','fit08','fit09','fit10','fit11','fit12','fit13','fit14','fit15','fit16') else 'body156-') + job['operation'])
    if job['operation'] in ('fit28','fit29','fit30','fit31','fit32','fit33'):out=BASE/('body159-'+job['operation'])
    if job['operation'] in ('fit34','fit35','fit36','fit37','fit38','fit39'):out=BASE/('body160-'+job['operation'])
    if job['operation'] in ('fit40','fit41','fit42','fit43','fit44','fit45','fit46','fit47','verify48'):out=BASE/('body161-'+job['operation'])
    if job['operation'] in ('inspect49','fit50','fit52'):out=BASE/('body162-'+job['operation'])
    if job['operation'] in ('inspect53','inspect54'):
        native=BASE/'body162-fit52/adult-body-fit.blend'
        if native.is_symlink() or digest(native)!='8e9db951953034113e51c0be55f8acb39b96486826d0fa404a28631c5d08ce81':
            raise ValueError('Pinned seated diagnosis input mismatch')
        out=BASE/('body163-'+job['operation'])
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
    if job['operation'] in ('hip58','hip59','hip61','hip62','hip63','hip64','hip66'):
        repair_hip_transition(out,job['operation'])
        return
    if job['operation'] in ('legs55','legs56','legs57'):
        repair_seated_legs(out,job['operation'])
        return
    if job['operation'] in ('inspect53','inspect54'):
        inspect_seated_proportions(out)
        return
    if job['operation']=='inspect49':
        inspect_shoulders(out)
        return
    if job['operation']=='verify48':
        diagnostic_reopen(out)
        return
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


def fit(out, native, variant,render_images=True,write_result=True,retain_points=False):
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
    donor_surface=None
    if variant>=30:
        # Refine donor topology before cutting, so the join does not terminate
        # in a sparse, faceted shoulder ring. This edits only the derivative.
        refine=body.modifiers.new('Donor topology for shoulder connection','SUBSURF');refine.levels=2 if variant>=34 else 1
        bpy.context.view_layer.update()
        evaluated=body.evaluated_get(bpy.context.evaluated_depsgraph_get())
        refined=bpy.data.meshes.new_from_object(evaluated)
        body.modifiers.clear();body.data=refined
    if variant>=50:
        from mathutils.bvhtree import BVHTree
        donor_surface=BVHTree.FromPolygons([v.co.copy() for v in body.data.vertices],[tuple(p.vertices) for p in body.data.polygons])
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
    anatomy_transfer=None
    if 34<=variant<40:
        anatomy_transfer=transfer_bust_anatomy(body,bpy.data.objects['MF_continuous_head_neck'],normal_support=variant>=36,detail_only=variant>=38,relief_gain=.8 if variant==39 else 2.)
        bust=bpy.data.objects['MF_continuous_head_neck']
        group=bust.vertex_groups.new(name='MF_body160_retained_head_neck')
        for v in bust.data.vertices:
            z=(bust.matrix_world@v.co).z
            group.add([v.index],max(0.,min(1.,(z+1.20)/.10)),'REPLACE')
        mask=bust.modifiers.new('Reversible neck-only control surface','MASK')
        mask.vertex_group=group.name;mask.use_smooth=True;mask.threshold=.5
    if variant>=40:
        bust=bpy.data.objects['MF_continuous_head_neck']
        group=bust.vertex_groups.new(name='MF_body161_anatomical_patch')
        for v in bust.data.vertices:
            p=bust.matrix_world@v.co
            group.add([v.index],max(0.,min(1.,.5+(p.z-anatomical_boundary(p.x))/.06)),'REPLACE')
        mask=bust.modifiers.new('Reversible curved boundary below landmarks','MASK')
        mask.vertex_group=group.name;mask.use_smooth=True;mask.threshold=.5
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
    if variant>=34:cutoff=-1.42
    if variant>=40:cutoff=-2.265
    if variant>=41:cutoff=-3.065
    # Diagnostic interface: preserve source/local data, clip donor only.
    if variant>=40:
        group=body.vertex_groups.new(name='MF_body161_curved_donor_boundary')
        for v in body.data.vertices:
            lower=anatomical_boundary(v.co.x)-.38
            if variant>=41:lower-=.8*smooth_transition((.25-v.co.y)/.50)*(1-smooth_transition((abs(v.co.x)-1.1)/.55))
            group.add([v.index],max(0.,min(1.,.5+(lower-v.co.z)/.06)),'REPLACE')
        mask=body.modifiers.new('Retain continuous lateral donor shoulders','MASK')
        mask.vertex_group=group.name;mask.use_smooth=True;mask.threshold=.5
        bpy.context.view_layer.update()
        clipped=bpy.data.meshes.new_from_object(body.evaluated_get(bpy.context.evaluated_depsgraph_get()))
        body.modifiers.clear();body.data=clipped
    else:
        bm = bmesh.new(); bm.from_mesh(body.data)
        bmesh.ops.bisect_plane(bm, geom=list(bm.verts)+list(bm.edges)+list(bm.faces),
            plane_co=(0,0,cutoff), plane_no=(0,0,1), clear_outer=True, dist=.00001)
        bm.to_mesh(body.data); bm.free()
    if variant>=19:
        blend_neck_surface(body,bpy.data.objects['MF_continuous_head_neck'],cutoff,pin=variant>=20,ordered=variant>=22,tangent=variant>=23,dense=variant>=41,topological=variant>=42)
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
    shoulder_restoration=None
    if variant>=50:shoulder_restoration=restore_donor_shoulders(body,donor_surface)
    if variant>=30:
        group=body.vertex_groups.new(name='MF_lower_shoulder_connection')
        for v in body.data.vertices:
            z=v.co.z
            upper=-1.84
            if variant>=32:upper+=.22*max(0.,min(1.,(abs(v.co.x)-1.05)/.40))
            w=max(0.,min(1.,(z+3.05)/.30,(upper-z)/.12))
            if variant>=34:w=max(0.,min(1.,(z+1.72)/.18,(-1.03-z)/.12))
            if variant>=36:w=max(0.,min(1.,(z+1.65)/.15,(-.91-z)/.12))
            if variant>=40:
                boundary=anatomical_boundary(v.co.x)
                w=smooth_transition((boundary-z)/.10)*smooth_transition((z-boundary+.65)/.25)
            if variant>=45:w=smooth_transition((-1.74-z)/.18)*smooth_transition((z+3.38)/.35)
            if variant>=46:w=connection_fairing_weight(v.co.x,z)
            if variant>=50:w*=1-shoulder_restore_weight(tuple(v.co))
            if w:group.add([v.index],w,'REPLACE')
        smooth=body.modifiers.new('Lower connection fairing only','SMOOTH')
        smooth.vertex_group=group.name;smooth.factor=.65;smooth.iterations=40 if variant>=32 else 18
        if variant>=45:smooth.iterations=90
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
            keep=all(body.data.vertices[i].co.z>anatomical_boundary(body.data.vertices[i].co.x)+.025 for i in e.vertices) if variant>=40 else all(body.data.vertices[i].co.z>(-.95 if variant>=36 else -1.149 if variant>=34 else -1.899 if variant>=28 else -.80) for i in e.vertices)
            if variant>=50:keep=keep and all(shoulder_restore_weight(tuple(body.data.vertices[i].co))==0 for i in e.vertices)
            if keep:crease.data[e.index].value=1.
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
        if write and render_images:
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
        masks=[m for m in bust.modifiers if m.type=='MASK'] if variant>=40 else []
        for m in masks:m.show_viewport=False;m.show_render=False
        bpy.context.view_layer.update()
        render('accepted-neck-front',0,(0,0,-1.2),4.7)
        render('accepted-interface',-35,(0,0,-1.65),6)
        for m in masks:m.show_viewport=True;m.show_render=True
        bust.hide_render=True;body.hide_render=False
    pose_result = None
    if variant >= 2:
        pose_result = pose_screen(body, before, render, sharpen=variant>=6, neck=variant>=9,hinge=20<=variant<40,shoulder=variant>=32,semantic=variant>=40,corrective=variant>=42,knee_fairing=variant>=45,retain_points=retain_points or variant==52,topological_arms=variant>=50)
    face_control=check_face_control(body) if variant>=26 else None
    assert all(protected()[k]==v for k,v in before.items())
    sealed = None
    if variant in (3,4,7,10,12,14,16,27,29,31,33,35,37,39,47,52):
        bpy.context.preferences.filepaths.save_version=0
        render('front',0,write=False)
        bpy.ops.wm.save_as_mainfile(filepath=str(out/'adult-body-fit.blend'),check_existing=False)
        sealed=verify_saved(out/'adult-body-fit.blend',before,pose_result['pose_matrices'],pose_result)
        body=bpy.data.objects['MF_studio_adult_body']
        if variant==52:
            del pose_result['_posed_surface_points']
            saved_review_frames(out,pose_result['pose_matrices'])
            assert digest(out/'adult-body-fit.blend')==sealed['native_sha256']
    result={'status':'INTERNAL_FIT_NOT_ACCEPTED','asset_metadata':metadata,'scale':scale,'zoffset':zoffset,'upper_assembly_scale':.88 if variant>=6 else 1.,'lower_bust_display_mask':9<=variant<28 or variant>=34,
        'body_vertices':len(body.data.vertices),'source_sha256':digest(native),'protected':before,'complete_accepted_bust_retained':28<=variant<34,
        'anatomy_transfer':anatomy_transfer,
        'shoulder_restoration':shoulder_restoration,
        'lower_connection_fairing':variant>=30,'lateral_shoulder_deforms':variant>=32,
        'bounds':next(r['bounds'] for r in inventory() if r['name']==body.name),
        'pose_screen':pose_result,'saved_verification':sealed,'surface_integration':integration,'face_control':face_control,
        'rigged':variant>=2,'limits':['Body interface requires visual acceptance','Static pose is not animation qualification','Clay material override is diagnostic only']}
    if write_result:(out/'result.json').write_text(json.dumps(result,indent=2)+'\n')
    return result


def smooth_transition(value):
    t=max(0.,min(1.,value))
    return t*t*t*(t*(t*6-15)+10)


def connection_fairing_weight(x,z):
    """Round only outer shoulder joins, protecting central throat/clavicles."""
    upper=-1.74+.42*smooth_transition((abs(x)-1.35)/.35)
    return smooth_transition((upper-z)/.18)*smooth_transition((z+3.38)/.35)


def coordinates_digest(points):
    """Bind reopened evaluated surfaces, not merely unchanged control data."""
    import hashlib,struct
    digestor=hashlib.sha256()
    for point in points:digestor.update(struct.pack('<ddd',*point))
    return digestor.hexdigest()


def anatomical_boundary(x):
    """A lower neck/clavicle patch, not the portrait's flat shoulder cutoff."""
    return -1.885+.48*smooth_transition((abs(x)-1.10)/.55)


def boundary_loops(edges):
    """Walk actual adjacency; a coordinate cutoff must not truncate a curve."""
    adjacency={}
    for a,b in edges:
        adjacency.setdefault(a,[]).append(b);adjacency.setdefault(b,[]).append(a)
    if not adjacency or any(len(v)!=2 for v in adjacency.values()):
        raise ValueError('Boundary is not closed two-neighbour loops')
    unused=set(adjacency);loops=[]
    while unused:
        start=next(iter(unused));walk=[start];previous=None;current=start
        while True:
            nxt=next(v for v in adjacency[current] if v!=previous)
            if nxt==start:break
            if nxt in walk:raise ValueError('Boundary crosses itself topologically')
            walk.append(nxt);previous,current=current,nxt
        unused.difference_update(walk);loops.append(walk)
    return loops


def anchored_ring_parameters(sequence):
    """Match front/right/back/left anchors despite unequal 3D perimeter lengths."""
    import math
    cy=(min(p[1] for p in sequence)+max(p[1] for p in sequence))/2
    front=min(range(len(sequence)),key=lambda i:abs(sequence[i][0])+10*max(0.,sequence[i][1]-cy))
    order=list(range(front,len(sequence)))+list(range(front))
    seq=[sequence[i] for i in order]
    right=max(range(len(seq)),key=lambda i:seq[i][0])
    back=min(range(len(seq)),key=lambda i:abs(seq[i][0])+10*max(0.,cy-seq[i][1]))
    left=min(range(len(seq)),key=lambda i:seq[i][0])
    anchors=[0,right,back,left,len(seq)]
    assert all(b>a for a,b in zip(anchors,anchors[1:])), 'Anatomical anchors must follow boundary orientation'
    fractions=[0.]*len(seq)
    for quarter,(start,end) in enumerate(zip(anchors,anchors[1:])):
        lengths=[math.dist(seq[i],seq[(i+1)%len(seq)]) for i in range(start,end)]
        total=sum(lengths);distance=0.
        for i,length in zip(range(start,end),lengths):
            fractions[i]=quarter/4+distance/(4*total);distance+=length
    return order,fractions


def regional_weights(point,definitions,arm_support=None,hip_transition=None):
    """Normalized anatomical support; no heat diffusion into unrelated limbs."""
    import math
    x,y,z=point;side='L' if x>=0 else 'R';ax=abs(x)
    def signed_projection(joint,upper,lower):
        h=definitions[upper][0];j=definitions[joint][0];t=definitions[lower][1]
        a=[j[i]-h[i] for i in range(3)];b=[t[i]-j[i] for i in range(3)]
        la=math.sqrt(sum(v*v for v in a));lb=math.sqrt(sum(v*v for v in b))
        direction=[a[i]/la+b[i]/lb for i in range(3)]
        norm=math.sqrt(sum(v*v for v in direction))
        return sum((point[i]-j[i])*direction[i]/norm for i in range(3))
    pelvis_spine=smooth_transition((z+5.7)/1.0)
    spine_chest=smooth_transition((z+4.3)/1.1)
    weights={'pelvis':1-pelvis_spine,'spine':pelvis_spine*(1-spine_chest),'chest':pelvis_spine*spine_chest}
    hip_start,hip_width=(6.0,1.20) if hip_transition is None else hip_transition
    if z< (-5.85 if hip_transition is None else -hip_start):
        hip=smooth_transition((-z-hip_start)/hip_width)
        weights={k:v*(1-hip) for k,v in weights.items()}
        left=smooth_transition((x+.30)/.60)
        for leg,fraction in [('L',left),('R',1-left)]:
            if not fraction:continue
            knee=smooth_transition((signed_projection('shin.'+leg,'thigh.'+leg,'shin.'+leg)+.35)/.70)
            ankle=smooth_transition((signed_projection('foot.'+leg,'shin.'+leg,'foot.'+leg)+.17)/.34)
            weights.update({'thigh.'+leg:hip*fraction*(1-knee),'shin.'+leg:hip*fraction*knee*(1-ankle),'foot.'+leg:hip*fraction*knee*ankle})
    if z>-8.3:
        threshold=1.20+.20*max(0.,-z-2.2)
        arm=smooth_transition((ax-threshold)/.35) if arm_support is None else arm_support
        if arm:
            elbow=smooth_transition((signed_projection('forearm.'+side,'upperarm.'+side,'forearm.'+side)+.32)/.64)
            wrist=smooth_transition((signed_projection('hand.'+side,'forearm.'+side,'hand.'+side)+.15)/.30)
            weights={k:v*(1-arm) for k,v in weights.items()}
            weights.update({'upperarm.'+side:arm*(1-elbow),'forearm.'+side:arm*elbow*(1-wrist),'hand.'+side:arm*elbow*wrist})
    return {k:v for k,v in weights.items() if v>1e-8}


def shoulder_restore_weight(point):
    """Adapt lateral assembly shoulders only; central accepted relief is fixed."""
    x,y,z=point
    return smooth_transition((abs(x)-1.05)/.50)*smooth_transition((-1.0-z)/.35)*smooth_transition((z+3.3)/.40)


def restore_donor_shoulders(body,tree):
    """Replace the outer graft corner with the donor's continuous shoulder cap."""
    maximum=0.;count=0
    for v in body.data.vertices:
        w=shoulder_restore_weight(tuple(v.co))
        if not w:continue
        hit=tree.find_nearest(v.co)
        assert hit[0] is not None and hit[3]<1.,'Shoulder donor correspondence outside local scope'
        delta=(hit[0]-v.co)*w
        if delta.length<1e-8:continue
        target=v.co+delta
        if body.data.shape_keys:
            for key in body.data.shape_keys.key_blocks:key.data[v.index].co+=delta
        v.co=target;maximum=max(maximum,delta.length);count+=1
    body.data.update()
    return {'vertices':count,'maximum_delta':maximum,'central_landmarks_unchanged':True,'method':'Local nearest donor shoulder cap, faded before central neck/clavicles; original source unedited'}


def connected_arm_support(points,edges):
    """Classify disconnected lower arms, then blend along surface paths.

    A world-X threshold cuts through the triceps and attaches it to the spine.
    Below the armpits the actual mesh separates into torso and two arm regions.
    Use that connectivity, not proximity across the armpit gap, as the seeds.
    """
    import heapq,math
    adjacency=[[] for _ in points]
    for a,b in edges:
        length=math.dist(points[a],points[b])
        adjacency[a].append((b,length));adjacency[b].append((a,length))
    lower={i for i,p in enumerate(points) if p[2]<-3.25}
    components=[]
    while lower:
        stack=[lower.pop()];component=[]
        while stack:
            i=stack.pop();component.append(i)
            for j,_ in adjacency[i]:
                if j in lower:lower.remove(j);stack.append(j)
        components.append(component)
    major=[c for c in components if len(c)>100]
    assert len(major)==3,('Expected torso and two disconnected lower arms',list(map(len,major)))
    torso=max(major,key=len)
    arms=[c for c in major if c is not torso]
    assert all(abs(sum(points[i][0] for i in c)/len(c))>1.5 for c in arms)
    fixed={i:0. for i in torso}
    for c in arms:
        for i in c:fixed[i]=1.
    for i,p in enumerate(points):
        if p[2]>=-1.35 or abs(p[0])<=1.05:fixed[i]=0.
    def distances(value):
        dist=[float('inf')]*len(points);queue=[]
        for i,v in fixed.items():
            if v==value:
                dist[i]=0.;heapq.heappush(queue,(0.,i))
        while queue:
            d,i=heapq.heappop(queue)
            if d!=dist[i]:continue
            for j,length in adjacency[i]:
                if j in fixed:continue
                candidate=d+length
                if candidate<dist[j]:dist[j]=candidate;heapq.heappush(queue,(candidate,j))
        return dist
    chest=distances(0.);arm=distances(1.)
    support=[]
    for i in range(len(points)):
        if i in fixed:support.append(fixed[i]);continue
        assert math.isfinite(chest[i]) and math.isfinite(arm[i]),'Unseeded shoulder island'
        support.append(smooth_transition(chest[i]/(chest[i]+arm[i])))
    return support,{'major_lower_components':list(map(len,major)),'lower_arm_vertices':sum(map(len,arms)),'transition_vertices':len(points)-len(fixed),'method':'Lower-arm connectivity labels; upper-shoulder geodesic blend'}


def transfer_bust_anatomy(body,bust,normal_support=False,detail_only=False,relief_gain=2.):
    """Transfer the approved surface to a continuous donor torso by depth rays.

    The donor's lateral shoulders, vertex heights and topology remain intact.
    The source supplies central neck/clavicle relief. Smooth support fades below
    and beside that region instead of grafting its horizontal shoulder cutoff.
    """
    import bpy,bmesh
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    bpy.context.view_layer.update()
    ev=bust.evaluated_get(bpy.context.evaluated_depsgraph_get())
    verts=[bust.matrix_world@v.co for v in ev.data.vertices]
    tree=BVHTree.FromPolygons(verts,[tuple(p.vertices) for p in ev.data.polygons])
    smooth_tree=None
    if detail_only:
        # Separate local anatomical relief from the portrait bust's broad,
        # flat lower shape. Copy-only smoothing creates a reference field;
        # it never edits accepted geometry or the donor shoulder silhouette.
        bm=bmesh.new();bm.from_mesh(ev.data)
        for v,p in zip(bm.verts,verts):v.co=p
        selected=[v for v in bm.verts if v.co.z<-.85]
        for _ in range(180):
            bmesh.ops.smooth_vert(bm,verts=selected,factor=.65,use_axis_x=False,use_axis_y=True,use_axis_z=False)
        bm.verts.ensure_lookup_table();bm.verts.index_update()
        smooth_tree=BVHTree.FromPolygons([v.co.copy() for v in bm.verts],[tuple(v.index for v in p.verts) for p in bm.faces])
        bm.free()
    hits=0;max_delta=0.
    normals=[v.normal.copy() for v in body.data.vertices]
    for v,n in zip(body.data.vertices,normals):
        x,y,z=v.co
        if not -2.45<z<-.95:continue
        w=smooth_transition((z+2.45)/.60)*(1-smooth_transition((abs(x)-.85)/.60))
        if normal_support:w*=smooth_transition((abs(n.y)-.20)/.60)
        if not w:continue
        front=n.y<0 if normal_support else y<.15
        start=Vector((x,-3 if front else 3,max(z,-1.885)))
        hit,normal,index,distance=tree.ray_cast(start,Vector((0,1 if front else -1,0)),6.)
        if hit is None:continue
        delta=(hit.y-y)*w
        if detail_only:
            soft,_,_,_=smooth_tree.ray_cast(start,Vector((0,1 if front else -1,0)),6.)
            if soft is None:continue
            absolute=smooth_transition((z+1.75)/.30)
            relief=(hit.y-soft.y)*relief_gain
            delta=((hit.y-y)*absolute+relief*(1-absolute))*w
        assert abs(delta)<1.5, 'Anatomical transfer exceeds bounded donor depth'
        v.co.y+=delta;hits+=1;max_delta=max(max_delta,abs(delta))
    body.data.update()
    assert hits>100,'Source neck/clavicle transfer did not cover donor'
    return {'depth_ray_vertices':hits,'max_depth_change':max_delta,'donor_xz_preserved':True,'clavicle_relief_without_bust_base':detail_only,'relief_gain':relief_gain if detail_only else None,
            'limits':'Central surface adaptation only; not exact reuse of every source clavicle vertex'}


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


def blend_neck_surface(body,bust,cutoff,pin=False,ordered=False,tangent=False,dense=False,topological=False):
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
    if topological:
        loops=boundary_loops([tuple(e.verts) for e in bm.edges if e.is_boundary])
        print('DONOR_BOUNDARY_LOOPS',[(len(loop),min(v.co.z for v in loop),max(v.co.z for v in loop)) for loop in loops],flush=True)
        eligible=[loop for loop in loops if max(v.co.z for v in loop)>-2.5]
        assert len(eligible)==1,'Multiple upper donor loops require separate treatment'
        lower=eligible[0]
        start=min(range(len(lower)),key=lambda i:angle(lower[i].co))
        lower=lower[start:]+lower[:start]
        if sum(a.co.x*b.co.y-b.co.x*a.co.y for a,b in zip(lower,lower[1:]+lower[:1]))<0:
            lower=[lower[0]]+list(reversed(lower[1:]))
        upper_order,upper_fractions=anchored_ring_parameters([tuple(p) for p in points])
        lower_order,lower_fractions=anchored_ring_parameters([tuple(v.co) for v in lower])
        points=[points[i] for i in upper_order];lower=[lower[i] for i in lower_order]
        point_fraction={id(p):f for p,f in zip(points,upper_fractions)}
    angles=[angle(v.co) for v in lower]
    def sample(a,normal=False):
        if topological:
            j=bisect.bisect_right(lower_fractions,a)%len(lower);k=(j-1)%len(lower)
            lo=lower_fractions[k];hi=lower_fractions[j] if j else 1.
            t=(a-lo)/(hi-lo)
            return lower[k].normal.lerp(lower[j].normal,t).normalized() if normal else lower[k].co.lerp(lower[j].co,t)
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
    for t in ([i/16 for i in range(16)]+[.995] if dense else (0.,.2,.4,.6,.8,.97)):
        row=[]
        for p in points:
            location=point_fraction[id(p)] if topological else angle(p)
            q=sample(location);w=t*t*(3-2*t)
            r=p.lerp(q,w);r.z=p.z*(1-t)+q.z*t
            if tangent:
                n0=ev.data.vertices[tree.find(p)[1]].normal
                n1=sample(location,normal=True);dz=q.z-p.z
                m0=derivative(n0,dz);m1=derivative(n1,dz)
                r=p*(2*t**3-3*t*t+1)+m0*(t**3-2*t*t+t)+q*(-2*t**3+3*t*t)+m1*(t**3-t*t)
            row.append(bm.verts.new(r))
        rows.append(row)
    for a,b in zip(rows,rows[1:]):
        for i in range(len(a)):
            j=(i+1)%len(a);bm.faces.new((a[i],a[j],b[j],b[i]))
    upper=rows[-1];i=j=0
    while i<len(upper) or j<len(lower):
        if topological:
            ai=(upper_fractions[i+1] if i+1<len(upper) else 1.) if i<len(upper) else float('inf')
            aj=(lower_fractions[j+1] if j+1<len(lower) else 1.) if j<len(lower) else float('inf')
        else:
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


def pose_screen(body, before, render, sharpen=False, neck=False,hinge=False,shoulder=False,semantic=False,corrective=False,knee_fairing=False,retain_points=False,topological_arms=False):
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
    if semantic:
        # Rest-space pivots at the donor's visible joints, not the old proxy.
        for side,s in [('L',1),('R',-1)]:
            definitions['thigh.'+side]=((s*.79,.16,-6.60),(s*.90,.04,-9.03),'pelvis')
            definitions['shin.'+side]=((s*.90,.04,-9.03),(s*.95,.16,-12.23),'thigh.'+side)
            definitions['foot.'+side]=((s*.95,.16,-12.23),(s*.95,-.92,-12.85),'shin.'+side)
    arm_support=None;arm_support_result=None
    if topological_arms:
        # Centre the elbow/wrist pivots on actual donor cross-sections.
        for side,s in [('L',1),('R',-1)]:
            joints=[]
            for z in (-4.6,-6.07):
                band=[v.co for v in body.data.vertices if abs(v.co.z-z)<.04 and s*v.co.x>1.7]
                assert len(band)>10
                joints.append((sum(p.x for p in band)/len(band),sum(p.y for p in band)/len(band),z))
            elbow,wrist=joints
            definitions['upperarm.'+side]=((s*1.57,.30,-2.05),elbow,'chest')
            definitions['forearm.'+side]=(elbow,wrist,'upperarm.'+side)
            definitions['hand.'+side]=(wrist,definitions['hand.'+side][1],'forearm.'+side)
        arm_support,arm_support_result=connected_arm_support([tuple(v.co) for v in body.data.vertices],[tuple(e.vertices) for e in body.data.edges])
    for name,(head,tail,parent) in definitions.items():
        bone=arm.edit_bones.new(name);bone.head=head;bone.tail=tail
        if parent:bone.parent=arm.edit_bones[parent]
    bpy.ops.object.mode_set(mode='OBJECT')
    body.select_set(True);bpy.context.view_layer.objects.active=rig
    if semantic:
        for group in list(body.vertex_groups):
            if group.name in arm.bones:body.vertex_groups.remove(group)
        for name in definitions:body.vertex_groups.new(name=name)
        for v in body.data.vertices:
            weights=regional_weights(tuple(v.co),definitions,None if arm_support is None else arm_support[v.index])
            assert abs(sum(weights.values())-1)<1e-6
            for name,weight in weights.items():body.vertex_groups[name].add([v.index],weight,'REPLACE')
        body.parent=rig
        mod=body.modifiers.new('Anatomical isolated skinning','ARMATURE');mod.object=rig
    else:bpy.ops.object.parent_set(type='ARMATURE_AUTO')
    mod=next(m for m in body.modifiers if m.type=='ARMATURE')
    # Armature before subdivision; fit ring stays with the protected bust/chest.
    bpy.context.view_layer.objects.active=body
    while body.modifiers.find(mod.name)>0:
        bpy.ops.object.modifier_move_up(modifier=mod.name)
    mod.use_deform_preserve_volume=True
    bone_groups={g.index:g for g in body.vertex_groups if g.name in arm.bones}
    for v in body.data.vertices:
        if semantic:continue
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
    if sharpen and not semantic:
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
    if corrective:
        group=body.vertex_groups.new(name='MF_body161_joint_relaxation')
        for v in body.data.vertices:
            p=v.co
            distances=[(p-Vector(definitions[n][0])).length for n in ('forearm.L','forearm.R','shin.L','shin.R')]
            w=1-smooth_transition((min(distances)-.22)/.75)
            if w:group.add([v.index],w,'REPLACE')
        relax=body.modifiers.new('Local joint corrective deformation','CORRECTIVE_SMOOTH')
        relax.vertex_group=group.name;relax.factor=.75;relax.iterations=12
        relax.smooth_type='LENGTH_WEIGHTED';relax.rest_source='BIND'
        while body.modifiers.find(relax.name)>1:
            bpy.ops.object.modifier_move_up(modifier=relax.name)
        bpy.context.view_layer.update()
        bpy.ops.object.correctivesmooth_bind(modifier=relax.name)
        assert relax.is_bind,'Joint correction must have an actual neutral bind'
    if knee_fairing:
        fairs=[]
        for side in ('L','R'):
            group=body.vertex_groups.new(name='MF_body161_pose_only_knee_'+side)
            for v in body.data.vertices:
                distance=(v.co-Vector(definitions['shin.'+side][0])).length
                w=1-smooth_transition((distance-.25)/.75)
                if w:group.add([v.index],w,'REPLACE')
            fair=body.modifiers.new('Knee-local pose-space crease correction '+side,'SMOOTH')
            fair.vertex_group=group.name;fair.iterations=120;fair.factor=0.
            while body.modifiers.find(fair.name)>2+len(fairs):bpy.ops.object.modifier_move_up(modifier=fair.name)
            driver=fair.driver_add('factor').driver;driver.type='SCRIPTED'
            variable=driver.variables.new();variable.name='bend';variable.type='TRANSFORMS'
            target=variable.targets[0];target.id=rig;target.bone_target='shin.'+side
            target.transform_type='ROT_X';target.transform_space='LOCAL_SPACE'
            driver.expression='0.8 * min(1.0, abs(bend) / 0.8)'
            fairs.append(fair)
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
    if topological_arms:
        render('neutral-shoulders',-35,(0,0,-2.9),6.8)
        render('neutral-other-shoulders',35,(0,0,-2.9),6.8)
        hair=[ob for ob in bpy.context.scene.objects if ob.type=='CURVES' and not ob.hide_render]
        for ob in hair:ob.hide_render=True
        render('neutral-shoulders-rear',145,(0,0,-2.9),6.8)
        for ob in hair:ob.hide_render=False
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
    if knee_fairing:
        assert all(f.factor>.1 for f in fairs),'Knee correction drivers must respond to this pose'
        print('KNEE_POSE_FACTORS',[f.factor for f in fairs],flush=True)
    posed=evaluated();assert all(math.isfinite(v) for p in posed for v in p)
    render('seated-three-quarter',-45,(0,-.8,-4.9),14.5)
    render('seated-side',90,(0,-.8,-4.9),14.5)
    if shoulder:
        render('seated-interface',-35,(0,-.2,-1.65),6)
        render('seated-neck-front',0,(0,-.2,-1.65),6)
    if semantic:
        render('seated-elbow',-80,tuple(rig.pose.bones['forearm.L'].head),3.5)
        render('seated-other-elbow',80,tuple(rig.pose.bones['forearm.R'].head),3.5)
        center=(rig.pose.bones['shin.L'].head+rig.pose.bones['shin.R'].head)/2
        render('seated-knees',-45,tuple(center),6.5)
        if knee_fairing:render('seated-other-knees',45,tuple(center),6.5)
        render('seated-abdomen',0,(0,-.5,-5.5),6.5)
        if knee_fairing:render('seated-front',0,(0,-.8,-4.9),14.5)
    if topological_arms:
        render('seated-other-three-quarter',45,(0,-.8,-4.9),14.5)
        render('seated-shoulders',-35,(0,0,-2.9),6.8)
        render('seated-other-shoulders',35,(0,0,-2.9),6.8)
        hair=[ob for ob in bpy.context.scene.objects if ob.type=='CURVES' and not ob.hide_render]
        for ob in hair:ob.hide_render=True
        render('seated-shoulders-rear',145,(0,0,-2.9),6.8)
        render('seated-other-shoulders-rear',-145,(0,0,-2.9),6.8)
        render('seated-shoulders-side',90,(0,0,-2.9),6.8)
        for ob in hair:ob.hide_render=False
    recipe={b.name:[list(row) for row in b.matrix_basis] for b in rig.pose.bones}
    for b in rig.pose.bones:b.matrix_basis=Matrix.Identity(4)
    attach();returned=evaluated()
    error=max((Vector(a)-Vector(b)).length for a,b in zip(neutral,returned))
    assert error<1e-5
    if knee_fairing:assert all(abs(f.factor)<1e-6 for f in fairs),'No knee correction in neutral'
    return {'bones':len(arm.bones),'unweighted':len(unweighted),'neutral_return_max_error':error,
            'arm_support':arm_support_result,'bone_definitions':definitions if topological_arms else None,
            **({'_posed_surface_points':posed} if retain_points else {}),
            'neutral_attachment_matrix_error':attachment_error,
            'neutral_surface_sha256':coordinates_digest(neutral),'posed_surface_sha256':coordinates_digest(posed),
            'pose_matrices':recipe,'limits':['Coarse body weights with boundary correction; not final performance rig','No finger articulation or actual tack contacts','Lateral lower bust participates in shoulder deformation; central neck follows chest' if shoulder else 'Preserved upper bust moves rigidly with chest; assembly-only lower-neck/shoulder replacement when enabled']}


def verify_saved(native,before,recipe,expected=None):
    import bpy
    from mathutils import Matrix,Vector
    bpy.ops.wm.open_mainfile(filepath=str(native),load_ui=False,use_scripts=False)
    reopened_protected=protected()
    assert all(reopened_protected[n]==v for n,v in before.items())
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
    pose_error=None;posed_bit_exact=False
    if expected:
        assert coordinates_digest(neutral_body)==expected['neutral_surface_sha256'],'Reopened neutral surface changed'
        posed_bit_exact=coordinates_digest(posed)==expected['posed_surface_sha256']
        if '_posed_surface_points' in expected:
            assert len(posed)==len(expected['_posed_surface_points'])
            pose_error=max((Vector(a)-Vector(b)).length for a,b in zip(posed,expected['_posed_surface_points']))
            print('REOPEN_POSE_MAX_ERROR',pose_error,flush=True)
            assert pose_error<1e-5,('Material reopened pose change',pose_error)
        else:assert posed_bit_exact,'Reopened posed surface changed'
    bust_moved=max(abs(bust.matrix_world[i][j]-neutral[i][j]) for i in range(4) for j in range(4))
    assert bust_moved>.01
    moved=sum((Vector(a)-Vector(b)).length>.001 for a,b in zip(neutral_body,posed));assert moved>100
    for bone in rig.pose.bones:bone.matrix_basis=Matrix.Identity(4)
    returned=coords();err=max((Vector(a)-Vector(b)).length for a,b in zip(neutral_body,returned));assert err<1e-5
    returned_protected=protected()
    assert all(returned_protected[n]==v for n,v in before.items())
    face_control=check_face_control(body) if body.data.shape_keys else None
    return {'native_sha256':digest(native),'reopened':True,'local_protected_data_exact':True,
            'evaluated_surfaces_match_pre_save':bool(expected),
            'posed_surface_bit_exact':posed_bit_exact,'posed_surface_max_error':pose_error,
            'posed_body_vertices_moved':moved,'bust_matrix_change':bust_moved,'body_neutral_return_max_error':err,
            'source_unchanged':digest(SOURCE)==SOURCE_SHA,'face_control':face_control}


def diagnostic_reopen(out):
    """Quantify failed bitwise pose check against a fixed, render-free rebuild.

    This never resaves or changes the selected native. Numerical tolerance is
    the existing neutral-return tolerance, not a visual or rig-quality waiver.
    """
    import bpy,math
    from mathutils import Matrix,Vector
    native=BASE/'body161-fit47/adult-body-fit.blend'
    pinned='ead27ef192fec5dad724a4a86706328121b4174266002627f780d4911e80a4ce'
    assert not native.is_symlink() and digest(native)==pinned
    rebuilt=fit(out,native_source(),46,render_images=False,write_result=False,retain_points=True)
    verified=verify_saved(native,rebuilt['protected'],rebuilt['pose_screen']['pose_matrices'],rebuilt['pose_screen'])
    verified['evaluated_surfaces_match_reconstruction']=verified.pop('evaluated_surfaces_match_pre_save')
    verified['posed_comparison_tolerance']=1e-5
    del rebuilt['pose_screen']['_posed_surface_points']
    rebuilt['saved_verification']=verified
    rebuilt['native_ref']='body161-fit47/adult-body-fit.blend'
    rebuilt['verification_method']='Fixed46 render-free post-run reconstruction; neutral bitwise and posed max-coordinate-error check against reopened47. Not a new shape variant.'
    (out/'result.json').write_text(json.dumps(rebuilt,indent=2)+'\n')
    scene=bpy.context.scene;camera=scene.camera
    lights=sorted((ob for ob in scene.objects if ob.name.startswith('MF_body156_softbox')),key=lambda ob:ob.name)
    assert len(lights)==2
    def render(label,angle,center,size):
        target=Vector(center);rot=Matrix.Rotation(math.radians(angle),3,'Z')
        camera.data.ortho_scale=size;camera.location=target+rot@Vector((0,-25,.5))
        camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler()
        for light,x in zip(lights,(-7,7)):
            light.location=target+rot@Vector((x,-9,7));light.rotation_euler=(target-light.location).to_track_quat('-Z','Y').to_euler()
        scene.render.filepath=str(out/(label+'.png'));bpy.ops.render.render(write_still=True)
    render('neck-front',0,(0,0,-1.2),4.7)
    rig=bpy.data.objects['MF_body156_fit_rig']
    for n,m in rebuilt['pose_screen']['pose_matrices'].items():rig.pose.bones[n].matrix_basis=Matrix(m)
    bpy.context.view_layer.update()
    render('seated-three-quarter',-45,(0,-.8,-4.9),14.5)
    render('seated-elbow',-80,tuple(rig.pose.bones['forearm.L'].head),3.5)
    center=(rig.pose.bones['shin.L'].head+rig.pose.bones['shin.R'].head)/2
    render('seated-knees',-45,tuple(center),6.5)
    render('seated-abdomen',0,(0,-.5,-5.5),6.5)
    assert digest(native)==pinned and digest(SOURCE)==SOURCE_SHA


def saved_review_frames(out,recipe):
    """Inspect the just-reopened scene, including posterior upper arms."""
    import bpy,math
    from mathutils import Matrix,Vector
    scene=bpy.context.scene;camera=scene.camera
    lights=sorted((ob for ob in scene.objects if ob.name.startswith('MF_body156_softbox')),key=lambda ob:ob.name)
    assert len(lights)==2
    def render(label,angle,center=(0,0,-2.9),size=6.8):
        target=Vector(center);rot=Matrix.Rotation(math.radians(angle),3,'Z')
        camera.data.ortho_scale=size;camera.location=target+rot@Vector((0,-25,.5))
        camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler()
        for light,x in zip(lights,(-7,7)):
            light.location=target+rot@Vector((x,-9,7));light.rotation_euler=(target-light.location).to_track_quat('-Z','Y').to_euler()
        scene.render.filepath=str(out/(label+'.png'));bpy.ops.render.render(write_still=True)
    render('reopened-neutral-shoulders',-35)
    render('reopened-neck-front',0,(0,0,-1.2),4.7)
    rig=bpy.data.objects['MF_body156_fit_rig']
    for n,m in recipe.items():rig.pose.bones[n].matrix_basis=Matrix(m)
    bpy.context.view_layer.update()
    render('reopened-seated-three-quarter',-45,(0,-.8,-4.9),14.5)
    hair=[ob for ob in scene.objects if ob.type=='CURVES' and not ob.hide_render]
    for ob in hair:ob.hide_render=True
    render('reopened-seated-shoulders-rear',145)
    render('reopened-seated-shoulders-side',90)
    for ob in hair:ob.hide_render=False
    for bone in rig.pose.bones:bone.matrix_basis=Matrix.Identity(4)
    bpy.context.view_layer.update()


def inspect_shoulders(out):
    """Read-only rest/posed shoulder diagnosis on the rejected pinned native."""
    import bpy,math
    from mathutils import Matrix,Vector
    native=BASE/'body161-fit47/adult-body-fit.blend'
    pinned='ead27ef192fec5dad724a4a86706328121b4174266002627f780d4911e80a4ce'
    assert not native.is_symlink() and digest(native)==pinned
    bpy.ops.wm.open_mainfile(filepath=str(native),load_ui=False,use_scripts=False)
    scene=bpy.context.scene;camera=scene.camera
    rig=bpy.data.objects['MF_body156_fit_rig'];body=bpy.data.objects['MF_studio_adult_body']
    lights=sorted((o for o in scene.objects if o.name.startswith('MF_body156_softbox')),key=lambda o:o.name)
    def render(label,angle):
        target=Vector((0,0,-2.9));rot=Matrix.Rotation(math.radians(angle),3,'Z')
        camera.data.ortho_scale=6.8;camera.location=target+rot@Vector((0,-25,.5))
        camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler()
        for light,x in zip(lights,(-7,7)):
            light.location=target+rot@Vector((x,-9,7));light.rotation_euler=(target-light.location).to_track_quat('-Z','Y').to_euler()
        scene.render.filepath=str(out/(label+'.png'));bpy.ops.render.render(write_still=True)
    for o in scene.objects:
        if o.type=='CURVES':o.hide_render=True
    render('neutral-shoulders',-35);render('neutral-shoulders-rear',145)
    rows=[]
    for z in (-1.6,-2.2,-2.8,-3.4,-4.0,-4.6):
        band=[v for v in body.data.vertices if abs(v.co.z-z)<.04 and 1.2<v.co.x<3]
        rows.append({'z':z,'points':[{'p':list(v.co),'weights':{body.vertex_groups[g.group].name:g.weight for g in v.groups if body.vertex_groups[g.group].name in rig.data.bones}} for v in sorted(band,key=lambda v:v.co.y)[::max(1,len(band)//12)]]})
    recipe=json.loads((BASE/'body161-verify48/result.json').read_text())['pose_screen']['pose_matrices']
    for n,m in recipe.items():rig.pose.bones[n].matrix_basis=Matrix(m)
    bpy.context.view_layer.update()
    render('seated-shoulders',-35);render('seated-shoulders-rear',145);render('seated-shoulders-side',90)
    bones={b.name:{'head':list(b.head_local),'tail':list(b.tail_local)} for b in rig.data.bones}
    # Unmodified donor at the exact assembly transform supplies a shape control.
    with bpy.data.libraries.load(str(native_source()),link=False) as (a,b):b.objects=['GEO-body_female_realistic']
    donor=b.objects[0];scene.collection.objects.link(donor)
    world=donor.matrix_world.copy();points=[world@v.co for v in donor.data.vertices]
    xc=(max(p.x for p in points)+min(p.x for p in points))/2
    zo=1.3302977085-max(p.z for p in points)*8.6-.55
    for v,p in zip(donor.data.vertices,points):v.co=((p.x-xc)*8.6,p.y*8.6+.15,p.z*8.6+zo)
    donor.matrix_world=Matrix.Identity(4);donor.modifiers.clear()
    sub=donor.modifiers.new('Donor inspection subdivision','SUBSURF');sub.levels=2
    donor.hide_render=False;body.hide_render=True
    for bone in rig.pose.bones:bone.matrix_basis=Matrix.Identity(4)
    render('donor-shoulders',-35);render('donor-shoulders-rear',145)
    (out/'result.json').write_text(json.dumps({'native_unchanged':digest(native)==pinned,'source_unchanged':digest(SOURCE)==SOURCE_SHA,'bones':bones,'rest_surface_weight_samples':rows,'purpose':'Internal shoulder/arm diagnosis; not acceptance'},indent=2)+'\n')


def repair_seated_legs(out,operation):
    """Fixed local leg-rig correction; keep all accepted rest geometry exact."""
    import bpy,math
    from mathutils import Matrix,Vector
    native=BASE/'body162-fit52/adult-body-fit.blend'
    pinned='8e9db951953034113e51c0be55f8acb39b96486826d0fa404a28631c5d08ce81'
    assert digest(native)==pinned and not native.is_symlink()
    parent=json.loads((native.parent/'result.json').read_text())
    bpy.ops.wm.open_mainfile(filepath=str(native),load_ui=False,use_scripts=False)
    scene=bpy.context.scene;camera=scene.camera
    rig=bpy.data.objects['MF_body156_fit_rig'];body=bpy.data.objects['MF_studio_adult_body']
    before=protected();assert all(before[n]==v for n,v in parent['protected'].items())
    def surface():
        bpy.context.view_layer.update()
        return [tuple(v.co) for v in body.evaluated_get(bpy.context.evaluated_depsgraph_get()).data.vertices]
    def apply(recipe):
        for bone in rig.pose.bones:bone.matrix_basis=Matrix(recipe[bone.name]) if recipe else Matrix.Identity(4)
        bpy.context.view_layer.update()
    neutral=surface();local_digest=coordinates_digest(tuple(v.co) for v in body.data.vertices)
    apply(parent['pose_screen']['pose_matrices']);previous_pose=surface();apply(None)
    # The old hip is almost at the groin, below the broad lateral pelvic mass.
    # Move only its rotation centre inside that mass; no limb mesh is stretched.
    hip_z=-5.95
    bpy.ops.object.select_all(action='DESELECT');rig.select_set(True);bpy.context.view_layer.objects.active=rig
    bpy.ops.object.mode_set(mode='EDIT')
    for side,s in [('L',1),('R',-1)]:rig.data.edit_bones['thigh.'+side].head=(s*.84,.20,hip_z)
    bpy.ops.object.mode_set(mode='OBJECT')
    definitions={b.name:(tuple(b.head_local),tuple(b.tail_local),b.parent.name if b.parent else None) for b in rig.data.bones}
    changed=0
    for v in body.data.vertices:
        if v.co.z>=-5.65:continue
        current={body.vertex_groups[g.group].name:g.weight for g in v.groups if body.vertex_groups[g.group].name in rig.data.bones}
        if any(n.startswith(('upperarm.','forearm.','hand.')) and w>1e-6 for n,w in current.items()):continue
        # First diagnostic varied central/lateral support; selected repair uses
        # one continuous bilateral transition to avoid an abdominal crease.
        lateral=smooth_transition((abs(v.co.x)-.30)/.45)
        hip_start=6.0*(1-lateral)+5.65*lateral if operation=='legs55' else 5.80
        width=1.20*(1-lateral)+1.10*lateral if operation=='legs55' else 1.30
        weights=regional_weights(tuple(v.co),definitions,arm_support=0.,hip_transition=(hip_start,width))
        for name in current:body.vertex_groups[name].remove([v.index])
        for name,w in weights.items():body.vertex_groups[name].add([v.index],w,'REPLACE')
        changed+=1
    assert coordinates_digest(tuple(v.co) for v in body.data.vertices)==local_digest
    after=surface();neutral_error=max((Vector(a)-Vector(b)).length for a,b in zip(neutral,after))
    assert neutral_error<1e-5,('Standing geometry changed',neutral_error)
    lights=sorted((o for o in scene.objects if o.name.startswith('MF_body156_softbox')),key=lambda o:o.name)
    def render(label,angle,center=(0,-.8,-4.9),size=14.5):
        target=Vector(center);rot=Matrix.Rotation(math.radians(angle),3,'Z')
        camera.data.ortho_scale=size;camera.location=target+rot@Vector((0,-25,.5))
        camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler()
        for light,x in zip(lights,(-7,7)):
            light.location=target+rot@Vector((x,-9,7));light.rotation_euler=(target-light.location).to_track_quat('-Z','Y').to_euler()
        scene.render.filepath=str(out/(label+'.png'));bpy.ops.render.render(write_still=True)
    render('standing-side',90,(0,0,-5.5),15.7)
    apply(parent['pose_screen']['pose_matrices'])
    def aim(name,target):
        bone=rig.pose.bones[name]
        q=(bone.tail-bone.head).normalized().rotation_difference(Vector(target).normalized())
        matrix=q.to_matrix().to_4x4()@bone.matrix;matrix.translation=bone.head;bone.matrix=matrix
        bpy.context.view_layer.update()
    for side,s in [('L',1),('R',-1)]:
        aim('thigh.'+side,(s*.22,-1,-.35));aim('shin.'+side,(0,.20,-1))
    posed=surface()
    unchanged_indices=[i for i,p in enumerate(neutral) if p[2]>-5.4 or (abs(p[0])>1.7 and p[2]>-8.3)]
    upper_error=max((Vector(posed[i])-Vector(previous_pose[i])).length for i in unchanged_indices)
    assert upper_error<1e-5,('Previously repaired upper-body pose changed',upper_error)
    for label,angle in [('seated-side',90),('seated-opposite-side',-90),('seated-front',0),('seated-three-quarter',-45),('seated-other-three-quarter',45)]:render(label,angle)
    knees=(rig.pose.bones['shin.L'].head+rig.pose.bones['shin.R'].head)/2
    render('seated-knees',-45,tuple(knees),6.5);render('seated-other-knees',45,tuple(knees),6.5)
    render('seated-abdomen',0,(0,-.5,-5.5),6.5)
    recipe={b.name:[list(row) for row in b.matrix_basis] for b in rig.pose.bones}
    lengths={s:{'hip_to_knee':rig.data.bones['thigh.'+s].length,'knee_to_ankle':rig.data.bones['shin.'+s].length} for s in ('L','R')}
    apply(None);returned=surface();return_error=max((Vector(a)-Vector(b)).length for a,b in zip(after,returned))
    protected_after=protected()
    assert return_error<1e-5 and all(protected_after[n]==v for n,v in parent['protected'].items())
    result={'status':'INTERNAL_VISUAL_REVIEW_PENDING','parent_native_sha256':pinned,'hip_z':hip_z,
        'leg_lengths':lengths,'vertices_reweighted':changed,'body_local_geometry_exact':True,
        'neutral_surface_max_error':neutral_error,'previous_upper_pose_max_error':upper_error,
        'neutral_return_max_error':return_error,'protected':parent['protected'],
        'pose_screen':{'pose_matrices':recipe,'neutral_surface_sha256':coordinates_digest(after),
            'posed_surface_sha256':coordinates_digest(posed),'_posed_surface_points':posed},
        'limits':['Static correction only; no true hip-centre reconstruction or universal ratio claim','Standing geometry preserved; selected save requires internal visual review']}
    if operation=='legs57':
        bpy.context.preferences.filepaths.save_version=0
        bpy.ops.wm.save_as_mainfile(filepath=str(out/'adult-body-fit.blend'),check_existing=False)
        result['saved_verification']=verify_saved(out/'adult-body-fit.blend',parent['protected'],recipe,result['pose_screen'])
        # Inspect representative actual saved/reopened images, not only previews.
        rig=bpy.data.objects['MF_body156_fit_rig'];body=bpy.data.objects['MF_studio_adult_body'];scene=bpy.context.scene;camera=scene.camera
        lights=sorted((o for o in scene.objects if o.name.startswith('MF_body156_softbox')),key=lambda o:o.name)
        render('reopened-standing-side',90,(0,0,-5.5),15.7)
        apply(recipe);render('reopened-seated-side',90);render('reopened-seated-front',0);apply(None)
    del result['pose_screen']['_posed_surface_points']
    assert digest(native)==pinned and digest(SOURCE)==SOURCE_SHA
    (out/'result.json').write_text(json.dumps(result,indent=2)+'\n')


def hip_linear_support(point):
    """Compact smooth mask: hip bend only, not abdomen, knees or upper body."""
    x,y,z=point
    return smooth_transition((-z-5.35)/.55)*(1-smooth_transition((-z-7.05)/.65))


def hip_fairing_support(point):
    """Broad lower-waist fade avoids a new ridge at a tight hip mask boundary."""
    x,y,z=point
    return smooth_transition((-z-4.65)/1.30)*(1-smooth_transition((-z-7.05)/.65))


def anatomical_hip_transition(point):
    """Front thigh and posterior gluteal tissue need different support fields."""
    x,y,z=point
    rear=smooth_transition((y-.05)/.65)
    return (5.35+.35*rear,1.70+.45*rear)


def repair_hip_transition(out,operation):
    """Pinned local dual-quaternion/linear blend; preserve neutral coordinates."""
    import bpy,math
    from mathutils import Matrix,Vector
    native=BASE/'body164-legs57/adult-body-fit.blend'
    pinned='cedce781c0980ce387b925d4b1cab6b510a8dcdd42453d6da243131440924f2f'
    parent=json.loads((native.parent/'result.json').read_text())
    bpy.ops.wm.open_mainfile(filepath=str(native),load_ui=False,use_scripts=False)
    scene=bpy.context.scene;camera=scene.camera
    rig=bpy.data.objects['MF_body156_fit_rig'];body=bpy.data.objects['MF_studio_adult_body']
    before=protected();assert all(before[n]==v for n,v in parent['protected'].items())
    local=coordinates_digest(tuple(v.co) for v in body.data.vertices)
    def apply(recipe):
        for bone in rig.pose.bones:bone.matrix_basis=Matrix(recipe[bone.name]) if recipe else Matrix.Identity(4)
        bpy.context.view_layer.update()
    def surface():
        bpy.context.view_layer.update()
        return [tuple(v.co) for v in body.evaluated_get(bpy.context.evaluated_depsgraph_get()).data.vertices]
    lights=sorted((o for o in scene.objects if o.name.startswith('MF_body156_softbox')),key=lambda o:o.name)
    def render(label,angle,center=(0,-.8,-4.9),size=14.5):
        target=Vector(center);rot=Matrix.Rotation(math.radians(angle),3,'Z')
        camera.data.ortho_scale=size;camera.location=target+rot@Vector((0,-25,.5))
        camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler()
        for light,x in zip(lights,(-7,7)):
            light.location=target+rot@Vector((x,-9,7));light.rotation_euler=(target-light.location).to_track_quat('-Z','Y').to_euler()
        scene.render.filepath=str(out/(label+'.png'));bpy.ops.render.render(write_still=True)
    apply(None);neutral=surface()
    recipe=parent['pose_screen']['pose_matrices']
    apply(recipe);old_pose=surface()
    for label,angle in [('side',90),('front',0),('rear-oblique',135)]:render('before-'+label,angle)
    apply(None)
    anatomical_support=operation in ('hip64','hip66')
    if anatomical_support:
        definitions={b.name:(tuple(b.head_local),tuple(b.tail_local),b.parent.name if b.parent else None) for b in rig.data.bones}
        for v in body.data.vertices:
            if v.co.z>=-5.25:continue
            current={body.vertex_groups[g.group].name:g.weight for g in v.groups if body.vertex_groups[g.group].name in rig.data.bones}
            if any(n.startswith(('upperarm.','forearm.','hand.')) and w>1e-6 for n,w in current.items()):continue
            weights=regional_weights(tuple(v.co),definitions,arm_support=0.,hip_transition=anatomical_hip_transition(tuple(v.co)))
            for name in current:body.vertex_groups[name].remove([v.index])
            for name,w in weights.items():body.vertex_groups[name].add([v.index],w,'REPLACE')
    main=next(m for m in body.modifiers if m.type=='ARMATURE')
    assert main.use_deform_preserve_volume
    blend=body.modifiers.new('Hip-local linear skinning blend','ARMATURE')
    assert hasattr(blend,'use_multi_modifier'),'Native version lacks multi-armature blend; do not silently alter whole-body skinning'
    group=body.vertex_groups.new(name='MF_body166_hip_linear_support')
    count=0
    for v in body.data.vertices:
        arm_weight=sum(g.weight for g in v.groups if body.vertex_groups[g.group].name.startswith(('upperarm.','forearm.','hand.')))
        w=hip_linear_support(tuple(v.co)) if arm_weight<1e-6 else 0.
        if w:group.add([v.index],w,'REPLACE');count+=1
    blend.object=rig;blend.use_deform_preserve_volume=False;blend.use_multi_modifier=True
    blend.vertex_group=group.name
    bpy.context.view_layer.objects.active=body
    while body.modifiers.find(blend.name)>body.modifiers.find(main.name)+1:bpy.ops.object.modifier_move_up(modifier=blend.name)
    shape_preserving=operation in ('hip63','hip64','hip66')
    if shape_preserving:
        # Delta-mush restores the neutral surface detail after smoothing the
        # deformation, unlike SMOOTH which erased the gluteal cleft in62.
        # Bind at the unchanged neutral surface; never smooth accepted rest.
        fair=body.modifiers.new('Hip-local rest-shape corrective deformation','CORRECTIVE_SMOOTH')
        fair_group=body.vertex_groups.new(name='MF_body168_hip_shape_preserving')
        for v in body.data.vertices:
            arm_weight=sum(g.weight for g in v.groups if body.vertex_groups[g.group].name.startswith(('upperarm.','forearm.','hand.')))
            w=hip_fairing_support(tuple(v.co)) if arm_weight<1e-6 else 0.
            if w:fair_group.add([v.index],w,'REPLACE')
        fair.vertex_group=fair_group.name;fair.factor=.8;fair.iterations=24
        fair.smooth_type='LENGTH_WEIGHTED';fair.rest_source='BIND';fair.use_only_smooth=False
        while body.modifiers.find(fair.name)>body.modifiers.find(blend.name)+1:bpy.ops.object.modifier_move_up(modifier=fair.name)
        bpy.context.view_layer.update();bpy.ops.object.correctivesmooth_bind(modifier=fair.name)
        assert fair.is_bind,'Hip correction needs an actual neutral rest bind'
    if operation in ('hip59','hip61','hip62'):
        # Local linear skinning removes DQ inflation, but the flexion crease
        # still needs a pose-only fairing. Never fair the accepted neutral.
        fair=body.modifiers.new('Hip-local pose-only flexion fairing','SMOOTH')
        fair_group=group
        if operation in ('hip61','hip62'):
            fair_group=body.vertex_groups.new(name='MF_body166_lower_waist_fairing')
            for v in body.data.vertices:
                arm_weight=sum(g.weight for g in v.groups if body.vertex_groups[g.group].name.startswith(('upperarm.','forearm.','hand.')))
                w=hip_fairing_support(tuple(v.co)) if arm_weight<1e-6 else 0.
                if w:fair_group.add([v.index],w,'REPLACE')
        fair.vertex_group=fair_group.name;fair.iterations=90 if operation in ('hip61','hip62') else 160;fair.factor=0.
        while body.modifiers.find(fair.name)>body.modifiers.find(blend.name)+1:bpy.ops.object.modifier_move_up(modifier=fair.name)
        driver=fair.driver_add('factor').driver;driver.type='SCRIPTED'
        for side in ('L','R'):
            variable=driver.variables.new();variable.name='bend'+side;variable.type='TRANSFORMS'
            target=variable.targets[0];target.id=rig;target.bone_target='thigh.'+side
            target.transform_type='ROT_X';target.transform_space='LOCAL_SPACE'
        driver.expression='min(0.85, 0.85 * (abs(bendL) + abs(bendR)) / 2.6)' if operation in ('hip61','hip62') else 'min(0.9, (abs(bendL) + abs(bendR)) / 2.0)'
    after=surface();neutral_error=max((Vector(a)-Vector(b)).length for a,b in zip(neutral,after))
    assert neutral_error<1e-5,('Standing surface changed',neutral_error)
    assert coordinates_digest(tuple(v.co) for v in body.data.vertices)==local
    render('standing-side',90,(0,0,-5.5),15.7)
    apply(recipe);posed=surface()
    upper=[i for i,p in enumerate(neutral) if p[2]>(-4.4 if operation in ('hip61','hip62') or shape_preserving else -5.1) or (abs(p[0])>1.7 and p[2]>-8.3)]
    upper_error=max((Vector(posed[i])-Vector(old_pose[i])).length for i in upper)
    assert upper_error<1e-5,('Upper-body pose changed',upper_error)
    angles=[('front',0),('front-left',-45),('left',-90),('rear-left',-135),('back',180),('rear-right',135),('right',90),('front-right',45)]
    for label,angle in angles:render('seated-'+label,angle)
    for label,angle in angles:render('hip-'+label,angle,(0,-.35,-6.0),5.5)
    half={}
    for bone in rig.pose.bones:
        loc,rot,scale=Matrix(recipe[bone.name]).decompose()
        if bone.name.startswith(('thigh.','shin.')):rot=rot.slerp(rot.__class__(),.5)
        half[bone.name]=[list(row) for row in Matrix.LocRotScale(loc,rot,scale)]
    apply(half);render('half-bend-side',90);render('half-bend-rear',135)
    if shape_preserving:
        # The failures appear already at partial flexion, so inspect that
        # actual transition from all angles, not only two flattering samples.
        for label,angle in angles:render('half-hip-'+label,angle,(0,-.35,-6.0),5.5)
        render('half-bend-front',0);render('half-bend-left',-90);render('half-bend-back',180)
    apply(None);returned=surface()
    return_error=max((Vector(a)-Vector(b)).length for a,b in zip(after,returned))
    final_protected=protected();assert all(final_protected[n]==v for n,v in parent['protected'].items())
    assert return_error<1e-5 and digest(native)==pinned and digest(SOURCE)==SOURCE_SHA
    result={'status':'INTERNAL_VISUAL_REVIEW_PENDING','method':'Hip-local linear/DQ multi-modifier blend'+(' plus neutral-bound rest-shape corrective deformation' if shape_preserving else ' plus pose-only flexion fairing' if operation!='hip58' else '')+'; no neutral sculpt',
        'parent_native_sha256':pinned,'protected':parent['protected'],'support_vertices':count,
        'body_local_geometry_exact':True,'neutral_surface_max_error':neutral_error,
        'previous_upper_pose_max_error':upper_error,'neutral_return_max_error':return_error,
        'pose_screen':{'pose_matrices':recipe,'neutral_surface_sha256':coordinates_digest(after),'posed_surface_sha256':coordinates_digest(posed)},
        'limits':['Static seated screen plus intermediate bend, not full riding performance','Original source native unmodified']}
    if operation in ('hip62','hip66'):
        result['pose_screen']['_posed_surface_points']=posed
        bpy.context.preferences.filepaths.save_version=0
        bpy.ops.wm.save_as_mainfile(filepath=str(out/'adult-body-fit.blend'),check_existing=False)
        result['saved_verification']=verify_saved(out/'adult-body-fit.blend',parent['protected'],recipe,result['pose_screen'])
        del result['pose_screen']['_posed_surface_points']
        rig=bpy.data.objects['MF_body156_fit_rig'];body=bpy.data.objects['MF_studio_adult_body'];scene=bpy.context.scene;camera=scene.camera
        lights=sorted((o for o in scene.objects if o.name.startswith('MF_body156_softbox')),key=lambda o:o.name)
        render('reopened-standing-side',90,(0,0,-5.5),15.7)
        apply(recipe)
        for label,angle in [('front',0),('right',90),('rear-right',135)]:render('reopened-seated-'+label,angle)
        render('reopened-hip-front',0,(0,-.35,-6.0),5.5)
        apply(None)
    (out/'result.json').write_text(json.dumps(result,indent=2)+'\n')


def inspect_seated_proportions(out):
    """Read-only current-native skeletal/support diagnosis; never save the scene."""
    import bpy, math
    from mathutils import Matrix, Vector
    from bpy_extras.object_utils import world_to_camera_view
    native=BASE/'body162-fit52/adult-body-fit.blend'
    pinned='8e9db951953034113e51c0be55f8acb39b96486826d0fa404a28631c5d08ce81'
    assert not native.is_symlink() and digest(native)==pinned
    data=json.loads((native.parent/'result.json').read_text())
    bpy.ops.wm.open_mainfile(filepath=str(native),load_ui=False,use_scripts=False)
    scene=bpy.context.scene;camera=scene.camera
    rig=bpy.data.objects['MF_body156_fit_rig'];body=bpy.data.objects['MF_studio_adult_body']
    current=protected()
    before={name:current[name] for name in data['protected']}
    assert before==data['protected']
    def surface():
        bpy.context.view_layer.update()
        ob=body.evaluated_get(bpy.context.evaluated_depsgraph_get())
        return [tuple(v.co) for v in ob.data.vertices]
    neutral=surface()
    def snapshot(posed):
        target=Vector((0,-.8,-4.9) if posed else (0,0,-5.5))
        rot=Matrix.Rotation(math.radians(90),3,'Z')
        camera.data.ortho_scale=14.5 if posed else 15.7
        camera.location=target+rot@Vector((0,-25,.5))
        camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler()
        bpy.context.view_layer.update()
        result={}
        for side in ('L','R'):
            thigh=rig.pose.bones['thigh.'+side];shin=rig.pose.bones['shin.'+side]
            points=[rig.matrix_world@p for p in (thigh.head,shin.head,shin.tail)]
            projection=[world_to_camera_view(scene,camera,p) for p in points]
            pixels=[(p.x*scene.render.resolution_x,(1-p.y)*scene.render.resolution_y) for p in projection]
            a,b=(points[1]-points[0]).length,(points[2]-points[1]).length
            pa,pb=math.dist(pixels[0],pixels[1]),math.dist(pixels[1],pixels[2])
            result[side]={'world_joints':[list(p) for p in points], 'image_pixels':pixels,
                'hip_to_knee':a,'knee_to_ankle':b,'upper_lower_ratio':a/b,
                'projected_upper_lower_ratio':pa/pb}
        return result
    rest=snapshot(False)
    bands=[]
    names={g.index:g.name for g in body.vertex_groups}
    for z in (-5.4,-5.7,-6.0,-6.3,-6.6,-6.9,-7.2,-7.5,-8.0,-8.5,-9.03,-9.5,-10.0,-11.0,-12.23):
        vertices=[v for v in body.data.vertices if abs(v.co.z-z)<.045 and .30<v.co.x<1.5]
        if not vertices:continue
        means={}
        for v in vertices:
            for g in v.groups:
                name=names[g.group]
                if name in rig.data.bones:means[name]=means.get(name,0)+g.weight/len(vertices)
        bands.append({'z':z,'vertex_count':len(vertices),'mean_weights':means,
            'mean_coordinate':[sum(v.co[i] for v in vertices)/len(vertices) for i in range(3)]})
    for n,m in data['pose_screen']['pose_matrices'].items():rig.pose.bones[n].matrix_basis=Matrix(m)
    bpy.context.view_layer.update()
    seated=snapshot(True);posed=surface()
    for bone in rig.pose.bones:bone.matrix_basis=Matrix.Identity(4)
    returned=surface()
    error=max((Vector(a)-Vector(b)).length for a,b in zip(neutral,returned))
    assert error<1e-5 and all(protected()[name]==value for name,value in before.items())
    assert digest(native)==pinned and digest(SOURCE)==SOURCE_SHA
    result={'native_sha256':pinned,'native_unchanged':True,'protected_local_data_exact':True,
        'standing':rest,'seated':seated,'rest_surface_weight_bands':bands,
        'neutral_surface_sha256':coordinates_digest(neutral),
        'posed_surface_sha256':coordinates_digest(posed),'neutral_return_max_error':error,
        'limits':['Joint ratios are test-rig measurements, not a universal anatomical standard',
            'No asset change, new design, render, pose revision or animation qualification',
            'Camera projection includes the actual side-view elevation and lateral leg splay']}
    (out/'result.json').write_text(json.dumps(result,indent=2)+'\n')


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
