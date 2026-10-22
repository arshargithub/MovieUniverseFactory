"""Fixed private body/wardrobe binding screen; not production qualification."""
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
from character_assembly import BASE, digest, protected
ASSEMBLY=BASE/'body154-assembly07/character-prototype.blend'
ASSEMBLY_SHA='4eed7eb8ddad8a9a0e8320cfdf9e6b78e3d1d8dd779b95e7df3a28b91b45c120'
CORE=BASE/'body154-core01/core-body-rig.blend'
CORE_SHA='28e81a5d39d53049e1fc241467d8b9c8c31c334dd7592189b0051ae8ebfffd88'
BOUND03_SHA='ce016f3a820c626219c81ba89e259fd0237bbacfc9d09cd10fd1bfc288d5a3a2'


def validate(job):
    if job not in ({'operation':'bind01'},{'operation':'bind02'},{'operation':'bind03'},{'operation':'review03'},{'operation':'review04'}):raise ValueError('Fixed bind screen only')
    if job['operation']=='review04' and len(BOUND03_SHA)!=64:raise ValueError('Review source not pinned')
    for p,sha in [(ASSEMBLY,ASSEMBLY_SHA),(CORE,CORE_SHA)]:
        if p.is_symlink() or digest(p)!=sha:raise ValueError('Pinned source mismatch')
    out=BASE/('body154-'+job['operation'])
    if out.exists():raise ValueError('No overwrite')
    return out


def allowed_bones(name,names):
    """Spatial proximity alone must never bind trousers to nearby fingers."""
    if 'trouser' in name or 'boot' in name:
        side='.R' if name.endswith('_-1') else '.L'
        return {n for n in names if n=='root' or n=='spine05' or (n.endswith(side) and n.startswith(('pelvis','upperleg','lowerleg','foot','toe')))}
    if 'tunic_sleeve' in name:
        side='.R' if name.endswith('_-1') else '.L'
        return {n for n in names if n.endswith(side) and n.startswith(('clavicle','shoulder','upperarm','lowerarm','wrist'))}
    if any(s in name for s in ('palm','finger','thumb')):
        side='.R' if '_-1' in name else '.L'
        return {'wrist'+side}
    if 'long_tunic' in name:
        return {n for n in names if n=='root' or n.startswith(('spine','pelvis','upperleg'))}
    return {n for n in names if n=='root' or n.startswith(('spine','pelvis','neck','head','clavicle','shoulder'))}


def main():
    import bpy,bmesh,math
    from mathutils import Vector,Matrix
    from mathutils.kdtree import KDTree
    job=json.loads(Path(sys.argv[sys.argv.index('--')+1]).read_text())
    out=validate(job);out.mkdir()
    if job['operation'].startswith('review'):
        review_pose(out,job['operation'])
        return
    bpy.ops.wm.open_mainfile(filepath=str(ASSEMBLY),load_ui=False,use_scripts=False)
    accepted=json.loads((BASE/'body154-assembly07/result.json').read_text())['protected']
    assert all(protected()[n]==v for n,v in accepted.items())
    with bpy.data.libraries.load(str(CORE),link=False) as (a,b):b.objects=['MF_mpfb_core_body','MF_mpfb_core_rig']
    body,rig=b.objects
    for ob in (body,rig):
        if ob.name not in bpy.context.scene.objects:bpy.context.scene.collection.objects.link(ob)
    rig.scale=(7,7,7);rig.location=(0,.18,-5.60)
    bpy.context.view_layer.update()
    # Put the source arms in a relaxed near-down bind pose before fitting clothes.
    def aim_chain(first,last,target):
        bone=rig.pose.bones[first];end=rig.pose.bones[last]
        old=(end.head-bone.head).normalized();new=Vector(target).normalized()
        rotation=old.rotation_difference(new).to_matrix().to_4x4()
        matrix=rotation@bone.matrix;matrix.translation=bone.head
        bone.matrix=matrix;bpy.context.view_layer.update()
    for side,sign in (('L',1),('R',-1)):
        aim_chain('upperarm01.'+side,'lowerarm01.'+side,(sign*.19,0,-1))
        aim_chain('lowerarm01.'+side,'wrist.'+side,(sign*.01,0,-1))
    bpy.ops.object.select_all(action='DESELECT');body.select_set(True);bpy.context.view_layer.objects.active=body
    bpy.ops.object.modifier_apply(modifier='Core authored weights')
    body.select_set(False);rig.select_set(True);bpy.context.view_layer.objects.active=rig
    bpy.ops.object.mode_set(mode='POSE');bpy.ops.pose.armature_apply(selected=False);bpy.ops.object.mode_set(mode='OBJECT')
    mod=body.modifiers.new('Rest-fit core weights','ARMATURE');mod.object=rig
    # Source face is not used. Keep the accepted bust untouched, with a covered
    # attachment corridor. Remove donor faces above that corridor on donor only.
    bm=bmesh.new();bm.from_mesh(body.data)
    bmesh.ops.delete(bm,geom=[f for f in bm.faces if max((body.matrix_world@v.co).z for v in f.verts)>-1.91],context='FACES')
    bm.to_mesh(body.data);bm.free()
    from character_assembly import material
    body.data.materials.clear();body.data.materials.append(material('MF_body154_base_skin',(.38,.19,.105)))
    for ob in bpy.context.scene.objects:
        if any(k in ob.name for k in ('MF_body154_palm','MF_body154_finger','MF_body154_thumb')):ob.hide_render=job['operation']=='bind01'
    if job['operation'] in ('bind02','bind03'):
        # Clothed proxy uses the source mesh as an invisible weight scaffold.
        # Do not pass off mismatched underlying anatomy as a fitted final body.
        body.hide_render=True
        # The first material control proved hair penetrates the rear hood.
        # Fit CLOTH outside a conservative hull of evaluated native hair only.
        from mathutils.bvhtree import BVHTree
        points=[]
        for name in ('MF_natural147_hair_long hair main','MF_natural147_hair_long hair strands'):
            ob=bpy.data.objects[name];ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get())
            stride=max(1,len(ev.data.points)//1800)
            points.extend(ob.matrix_world@p.position for p in list(ev.data.points)[::stride])
        hull=bmesh.new()
        for p in points:hull.verts.new(p)
        bmesh.ops.convex_hull(hull,input=list(hull.verts),use_existing_faces=False)
        hull.verts.ensure_lookup_table();hull.verts.index_update()
        tree_hair=BVHTree.FromPolygons([v.co for v in hull.verts],[tuple(v.index for v in f.verts) for f in hull.faces])
        hood=bpy.data.objects['MF_adapted_donor_hood'];changed=0
        for v in hood.data.vertices:
            p=hood.matrix_world@v.co
            if p.y<.12 or p.z<-.75:continue
            center=Vector((0,.15,0));direction=(p-center).normalized()
            hit,normal,_,_=tree_hair.ray_cast(center+direction*8,-direction,10)
            if hit is not None and (p-center).length<(hit-center).length+.14:
                v.co=hood.matrix_world.inverted()@(hit+direction*.14);changed+=1
        hull.free();hood.data.update()
        bpy.context.scene['body154_hood_clearance_vertices']=changed
    bpy.context.view_layer.update()
    # Transfer nearby authored body weights to clothes. This is a first bind,
    # not a declaration that automatic transfer yields production deformation.
    used={i for p in body.data.polygons for i in p.vertices}
    tree=KDTree(len(used))
    for i in used:tree.insert(body.matrix_world@body.data.vertices[i].co,i)
    tree.balance()
    filtered_trees={}
    def nearest_weights(point,allowed=None):
        selected=tree
        if allowed is not None:
            key=tuple(sorted(allowed))
            if key not in filtered_trees:
                indices=[i for i in used if sum(g.weight for g in body.data.vertices[i].groups if body.vertex_groups[g.group].name in allowed)>.50]
                selected=KDTree(len(indices))
                for i in indices:selected.insert(body.matrix_world@body.data.vertices[i].co,i)
                selected.balance();filtered_trees[key]=selected
            selected=filtered_trees[key]
        entries=selected.find_n(point,4);weights={};denom=0
        for _,i,d in entries:
            factor=1/max(d,.015)**2;denom+=factor
            for g in body.data.vertices[i].groups:
                name=body.vertex_groups[g.group].name
                if name in rig.data.bones and (allowed is None or name in allowed):weights[name]=weights.get(name,0)+g.weight*factor
        total=sum(weights.values())
        return {n:w/total for n,w in weights.items() if w/total>.0001}
    bind_counts={}
    head=bpy.data.objects['MF_continuous_head_neck']
    targets=[o for o in bpy.context.scene.objects if o.type=='MESH' and not o.hide_render and o!=body and not o.name.startswith('MF_aimable_eye')]
    for ob in targets:
        allowed=allowed_bones(ob.name,rig.data.bones.keys()) if job['operation']=='bind03' else None
        groups={n:ob.vertex_groups.get(n) or ob.vertex_groups.new(name=n) for n in rig.data.bones.keys()}
        for v in ob.data.vertices:
            p=ob.matrix_world@v.co
            if ob==head and p.z>-.98:weights={'head':1.}
            elif ob==head:
                w=max(0.,min(1.,(p.z+1.85)/.87));weights={n:a*(1-w) for n,a in nearest_weights(p,allowed).items()};weights['head']=weights.get('head',0)+w
            elif ob.name=='MF_adapted_donor_hood':
                # Head-cover upper fabric follows head; lower drape blends to torso.
                w=max(0.,min(1.,(p.z+2.5)/1.4));weights={n:a*(1-w) for n,a in nearest_weights(p,allowed).items()};weights['head']=weights.get('head',0)+w
            else:weights=nearest_weights(p,allowed)
            for n,w in weights.items():groups[n].add([v.index],w,'REPLACE')
        modifier=ob.modifiers.new('MF_body154_first_bind','ARMATURE');modifier.object=rig
        bind_counts[ob.name]=len(ob.data.vertices)
    def parent_head(ob):
        world=ob.matrix_world.copy();ob.parent=rig;ob.parent_type='BONE';ob.parent_bone='head';ob.matrix_world=world
    for name in ('MF_natural147_hair_retarget','MF_natural147_hair_temples','MF_aimable_eye_Left','MF_aimable_eye_Right'):
        parent_head(bpy.data.objects[name])
    bpy.context.view_layer.update()
    assert all(protected()[n]==v for n,v in accepted.items())
    scene=bpy.context.scene;camera=scene.camera
    def render(label,angle):
        target=Vector((0,0,-4.9));rot=Matrix.Rotation(math.radians(angle),3,'Z')
        camera.data.ortho_scale=14.4;camera.location=target+rot@Vector((0,-24,1))
        camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler()
        scene.render.filepath=str(out/(label+'.png'));bpy.ops.render.render(write_still=True)
    render('neutral-front',0);render('neutral-side',-65)
    if job['operation'] in ('bind02','bind03'):render('neutral-back',180)
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'bound-prototype.blend'),check_existing=False)
    # Coordinated low-amplitude articulation screen, not a gallop or riding pose.
    for name,angle in [('spine03',.12),('spine02',.12),('neck01',-.12),('neck02',-.12),('upperarm01.L',.20),('upperarm01.R',.20)]:
        b=rig.pose.bones[name];b.rotation_mode='XYZ';b.rotation_euler.x=angle
    bpy.context.view_layer.update();render('lean-screen',-65)
    for b in rig.pose.bones:
        if b.rotation_mode=='XYZ':b.rotation_euler=(0,0,0)
    bpy.context.view_layer.update()
    bpy.ops.wm.open_mainfile(filepath=str(out/'bound-prototype.blend'),load_ui=False,use_scripts=False)
    assert all(protected()[n]==v for n,v in accepted.items())
    (out/'result.json').write_text(json.dumps({'status':'INTERNAL_BIND_SCREEN_NOT_ACCEPTED',
        'protected_local_geometry_and_materials_preserved':True,'source_hashes':{'assembly':ASSEMBLY_SHA,'core':CORE_SHA},
        'bound_vertex_counts':bind_counts,'bones':len(bpy.data.objects['MF_mpfb_core_rig'].data.bones),
        'fresh_open':True,'body_scaffold_hidden':job['operation'] in ('bind02','bind03'),
        'limits':['Body scaffold is not fitted production anatomy','Prototype hands retained','Body fit and weights require visual review','Not welded to bust','No gallop or garment qualification']},indent=2)+'\n')


def review_pose(out,operation):
    import bpy, math
    from mathutils import Vector,Matrix
    source=BASE/'body154-bind02/bound-prototype.blend'
    expected='54283c68aaf44f85b7749aed3b42c99bbcdfa6cf852dd8166bba45bf7919d1a5'
    if operation=='review04':
        source=BASE/'body154-bind03/bound-prototype.blend'
        expected=BOUND03_SHA
    if source.is_symlink() or digest(source)!=expected:raise ValueError('Bound source changed')
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False)
    scene=bpy.context.scene;rig=bpy.data.objects['MF_mpfb_core_rig'];camera=scene.camera
    accepted=json.loads((BASE/'body154-assembly07/result.json').read_text())['protected']
    def render(label,angle,center=(0,0,-4.8),scale=13.4):
        target=Vector(center);rot=Matrix.Rotation(math.radians(angle),3,'Z')
        camera.data.ortho_scale=scale;camera.location=target+rot@Vector((0,-24,1))
        camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler()
        for ob in scene.objects:
            if ob.type=='LIGHT' and not ob.hide_render:
                x=-6 if ob.data.energy>1500 else 6
                ob.location=target+rot@Vector((x,-7,6))
                ob.rotation_euler=(target-ob.location).to_track_quat('-Z','Y').to_euler()
        scene.render.filepath=str(out/(label+'.png'));bpy.ops.render.render(write_still=True)
    for label,a in [('front',0),('left',-45),('right',45),('back',180)]:render(label,a)
    render('medium',-15,(0,0,-1.7),7.0)
    def aim(first,last,target):
        bone=rig.pose.bones[first];end=rig.pose.bones[last]
        q=(end.head-bone.head).normalized().rotation_difference(Vector(target).normalized())
        matrix=q.to_matrix().to_4x4()@bone.matrix;matrix.translation=bone.head
        bone.matrix=matrix;bpy.context.view_layer.update()
    for name,angle in [('spine03',.18),('spine02',.18),('neck01',-.18),('neck02',-.18)]:
        bone=rig.pose.bones[name];bone.rotation_mode='XYZ';bone.rotation_euler.x=angle
    bpy.context.view_layer.update()
    for side,sign in [('L',1),('R',-1)]:
        aim('upperleg01.'+side,'lowerleg01.'+side,(sign*.45,-.8,-.9))
        aim('lowerleg01.'+side,'foot.'+side,(-sign*.05,.50,-1))
        aim('upperarm01.'+side,'lowerarm01.'+side,(sign*.08,-.5,-1))
        aim('lowerarm01.'+side,'wrist.'+side,(-sign*.42,-1,-.20))
    from character_assembly import material
    mat=material('MF_body154_saddle_proxy',(.11,.105,.10))
    bpy.ops.mesh.primitive_uv_sphere_add(segments=32,ring_count=16,location=(0,.10,-6.0))
    saddle=bpy.context.object;saddle.name='MF_body154_saddle_proxy';saddle.scale=(1.28,2.4,.88);saddle.data.materials.append(mat)
    render('riding-left',-65,(0,-.6,-4.1),11.8);render('riding-front',0,(0,-.6,-4.1),11.8)
    assert all(protected()[n]==v for n,v in accepted.items())
    (out/'result.json').write_text(json.dumps({'status':'STATIC_POSE_SCREEN_NOT_QUALIFIED',
        'source_sha256':expected,'accepted_local_data_preserved':True,
        'pose_bones':{b.name:[list(row) for row in b.matrix_basis] for b in rig.pose.bones},
        'limits':['Not animated','Proxy saddle only','No production acceptance']},indent=2)+'\n')


if __name__=='__main__':main()
