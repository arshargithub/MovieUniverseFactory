"""Fixed saved37 mounted-leader correction; no external paths or runtime code."""
import math
import numpy as np


def frame_map(across, longitudinal, shaft, forward):
    """Proper orthonormal rotation: index-to-little axis follows the shaft."""
    def basis(a,b):
        a=np.asarray(a,dtype=float);a=a/np.linalg.norm(a)
        b=np.asarray(b,dtype=float);b=b-a*np.dot(a,b)
        if np.linalg.norm(b)<1e-6:raise ValueError('HAND_FRAME_DEGENERATE')
        b/=np.linalg.norm(b)
        return np.column_stack((a,b,np.cross(a,b)))
    return basis(shaft,forward)@basis(across,longitudinal).T


def skirt_point(root,u,angle):
    """Gathered waist releases into weighted vertical folds, not a rigid rim."""
    root=np.asarray(root,dtype=float)
    axis=np.array([math.sin(angle),-.77*math.cos(angle),0.])
    release=math.sin(u*math.pi*.5)
    fold=(.010*math.sin(11*angle+.3)+.005*math.sin(17*angle-1.1))*release
    p=root+axis*(.105*u+fold)
    p[2]=1.145-.53*u+.012*u*math.sin(3*angle+.5)
    return p


def layer_weights(row,bones,waist=False):
    """Mask groups are not bone influences; waist support is not thigh skin."""
    if waist:
        if 'spine05' not in bones:raise ValueError('CLOTH345_WAIST_BONE')
        return {'spine05':1.0}
    valid={name:value for name,value in row.items() if name in bones and
           not name.startswith(('upperarm','lowerarm','wrist','finger'))}
    total=sum(valid.values())
    if total<.5:raise ValueError('CLOTH345_WEIGHT_OWNER')
    return {name:value/total for name,value in valid.items()}


def transported_frame(rest_frame,hand_rotation,axis):
    """Keep this bone's rest roll; swing its transported Y onto the limb axis.

    A wrist's local X is not a forearm bone's local X. Copying it constructs an
    unrelated roll frame and can twist the skin despite perfect endpoint tests.
    """
    target=np.asarray(hand_rotation,dtype=float)@np.asarray(rest_frame,dtype=float)
    a=target[:,1];a=a/np.linalg.norm(a)
    b=np.asarray(axis,dtype=float);b=b/np.linalg.norm(b)
    v=np.cross(a,b);c=float(np.clip(a@b,-1,1))
    if c<-.999999:raise ValueError('FOREARM_TRANSPORT_ANTIPARALLEL')
    k=np.array([[0,-v[2],v[1]],[v[2],0,-v[0]],[-v[1],v[0],0]])
    swing=np.eye(3)+k+k@k/(1+c)
    return swing@target


def neutral_elbow(shoulder,wrist,upper,lower,palm_direction):
    """On the two-bone elbow circle, minimize forearm-to-palm bending.

    This chooses a physically reachable elbow, not a free joint displacement.
    Skin, torso clearance and the animated elbow path still need visual review.
    """
    a=np.asarray(shoulder,dtype=float);b=np.asarray(wrist,dtype=float)
    axis=b-a;distance=np.linalg.norm(axis);axis/=distance
    if not abs(upper-lower)+1e-5<distance<upper+lower-1e-5:
        raise ValueError('NEUTRAL_ELBOW_UNREACHABLE')
    along=(upper*upper-lower*lower+distance*distance)/(2*distance)
    center=a+axis*along;radius=math.sqrt(max(0,upper*upper-along*along))
    direction=np.asarray(palm_direction,dtype=float);direction/=np.linalg.norm(direction)
    projected=b-direction*lower-center
    projected-=axis*np.dot(projected,axis)
    if np.linalg.norm(projected)<1e-6:raise ValueError('NEUTRAL_ELBOW_AMBIGUOUS')
    return center+radius*projected/np.linalg.norm(projected)


def restore_beard(bpy,rig):
    """Restore omitted fitted base cards from the already-inspected donor."""
    from pathlib import Path
    from mathutils import Matrix
    donor=Path(__file__).resolve().parents[4]/'.runtime/art-direction/series01-sikh265/candidate-04/character.blend'
    names=['Sikh265 coherent MPFB male.rehmanpolanski_'+n+'_viking' for n in ('beard','moustache')]
    original_objects=set(bpy.data.objects)
    with bpy.data.libraries.load(str(donor),link=False) as (available,loaded):
        if not all(n in available.objects for n in names):raise ValueError('FINISH345_BEARD_DONOR')
        loaded.objects=names
    fibers=bpy.data.objects['beard donor-guided fiber detail'];restored=[]
    for obj in loaded.objects:
        bpy.context.scene.collection.objects.link(obj)
        world=obj.matrix_world.copy();obj.data=obj.data.copy();obj.data.transform(world)
        for mod in list(obj.modifiers):obj.modifiers.remove(mod)
        obj.parent=rig;obj.matrix_parent_inverse=Matrix.Identity(4);obj.matrix_basis=fibers.matrix_basis.copy()
        obj.rotation_mode='QUATERNION'
        obj.animation_data_clear();obj.animation_data_create();obj.animation_data.action=fibers.animation_data.action.copy()
        # Single-slot transform actions require the copied source slot too.
        if obj.animation_data.action.slots:obj.animation_data.action_slot=obj.animation_data.action.slots[0]
        obj.hide_render=False;obj.hide_viewport=False
        restored.append(obj.name)
    # Library append also loads the source rig. Once both cards are reparented
    # it is a new unused dependency, dropped by save/reopen. Remove only such
    # newly appended orphans before the immutable snapshot is measured.
    for obj in set(bpy.data.objects)-original_objects:
        if obj.users==0:bpy.data.objects.remove(obj)
    for obj in bpy.data.objects:
        if obj.name.startswith('iris.') and obj.parent==rig:
            for v in obj.data.vertices:v.co.x*=1.17;v.co.z*=1.17
            obj.data.update()
    return restored


def cloth(bpy,out):
    """Reconstruct torso-owned layers; never bind a waist ribbon to sleeve skin."""
    import json
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    from mathutils.kdtree import KDTree
    scene=bpy.context.scene;scene.frame_set(283)
    rig=bpy.data.objects['MF coherent Nihang rig'];coat=bpy.data.objects['MF coherent coat']
    if not rig.get('layer_refit_proof') or rig.get('cloth345'):raise ValueError('CLOTH345_PARENT')
    rig.data.pose_position='REST';bpy.context.view_layer.update()
    # Local compression and elbow folds preserve the fitted outer silhouette.
    for v in coat.data.vertices:
        x,y,z=v.co;waist=math.exp(-((z-1.24)/.12)**2)
        amp=.004*waist*math.sin(78*z+14*x+2*math.sin(9*x))
        for side in ('L','R'):
            elbow=rig.data.bones['lowerarm01.'+side].head_local
            wrist=rig.data.bones['wrist.'+side].head_local;axis=(wrist-elbow).normalized()
            d=v.co-elbow;t=d.dot(axis);rad=(d-axis*t).length
            if rad<.105 and abs(t)<.12:
                amp+=.005*math.exp(-(t/.075)**2)*math.sin(t*145+.8*math.sin(x*19))
        v.co+=v.normal*amp
    coat.data.update()
    allowed=lambda name:name in rig.data.bones and not name.startswith(('upperarm','lowerarm','wrist','finger'))
    w=[]
    for v in coat.data.vertices:
        row={coat.vertex_groups[g.group].name:g.weight for g in v.groups}
        w.append(row)
    faces=[tuple(p.vertices) for p in coat.data.polygons if all(
        abs(coat.data.vertices[i].co.x)<.30 and
        sum(val for name,val in w[i].items() if name in rig.data.bones and not allowed(name))<.07 for i in p.vertices)]
    (out/'torso-support345.json').write_text(json.dumps(dict(total_faces=len(coat.data.polygons),torso_faces=len(faces),
        groups=[g.name for g in coat.vertex_groups],bounds=[[min(v.co[i] for v in coat.data.vertices),max(v.co[i] for v in coat.data.vertices)] for i in range(3)]),indent=2)+'\n')
    if len(faces)<100:raise ValueError('CLOTH345_TORSO_TOPOLOGY')
    tree=BVHTree.FromPolygons([v.co for v in coat.data.vertices],faces)
    # Shoulder cloth is supported by the actual outer shoulder, not the waist
    # mask. Keep geometric support distinct from the permitted deform owners.
    shoulder_faces=[tuple(p.vertices) for p in coat.data.polygons if all(
        abs(coat.data.vertices[i].co.x)<.36 for i in p.vertices)]
    shoulder_tree=BVHTree.FromPolygons([v.co for v in coat.data.vertices],shoulder_faces)
    kd=KDTree(len(coat.data.vertices))
    for v in coat.data.vertices:kd.insert(v.co,v.index)
    kd.balance();rows=[]
    def bind(obj,coords,surface,surface_faces):
        if len(coords)!=len(obj.data.vertices):raise ValueError('CLOTH345_LAYER_TOPOLOGY')
        for mod in list(obj.modifiers):obj.modifiers.remove(mod)
        obj.vertex_groups.clear()
        for v,p in zip(obj.data.vertices,coords):
            v.co=p;_,_,face,_=surface.find_nearest(p)
            if face is None:raise ValueError('CLOTH345_NO_TORSO')
            ids=surface_faces[face];inv=[1/max(.003,(coat.data.vertices[i].co-p).length) for i in ids];total=sum(inv)
            weights={}
            for i,weight in zip(ids,inv):
                for name,value in w[i].items():
                    if allowed(name):weights[name]=weights.get(name,0)+value*weight/total
            # Removed arm influence is redistributed to valid torso bones;
            # do not confuse that with coverage of a missing geometric surface.
            total_weight=sum(weights.values())
            if total_weight<.01:raise ValueError('CLOTH345_SHOULDER_OWNER')
            weights={n:v/total_weight for n,v in weights.items()}
            weights=layer_weights(weights,set(rig.data.bones.keys()),waist=obj.name=='MF coherent waist wrap')
            for name,value in weights.items():
                g=obj.vertex_groups.get(name) or obj.vertex_groups.new(name=name);g.add([v.index],value,'REPLACE')
        obj.data.update()
        arm=obj.modifiers.new('Torso-owned garment deformation','ARMATURE');arm.object=rig;arm.use_deform_preserve_volume=True
        sub=obj.modifiers.new('Soft woven continuity','SUBSURF');sub.levels=1;sub.render_levels=1
        solid=obj.modifiers.new('Woven layer thickness','SOLIDIFY');solid.thickness=.002
        rows.append(dict(name=obj.name,vertices=len(coords),weights=[g.name for g in obj.vertex_groups]))
    belt=bpy.data.objects['MF coherent waist wrap'];coords=[]
    for j in range(9):
        u=j/8
        for k in range(97):
            a=math.tau*k/96;axis=Vector((math.sin(a),-math.cos(a),0));z=1.111025+.085*u+.004*math.sin(a)
            hit=tree.ray_cast(Vector((0,-.02,z))+axis*.5,-axis)[0]
            if hit is None:raise ValueError(f'CLOTH345_BELT_RAY:{j}:{k}:{z}')
            coords.append(hit+axis*(.010+.002*math.sin(u*math.pi*4+a)))
    belt_coords=coords
    sash=bpy.data.objects['MF coherent shoulder sash'];panels=[]
    for side in (-1,1):
        pts=[]
        for j in range(41):
            t=j/40;x=.12-.25*t;z=1.145*(1-t)+1.55*t
            for k in range(7):
                off=(k/6-.5)*.065;xx=x+off*.84;zz=z+off*.54
                hit=shoulder_tree.ray_cast(Vector((xx,side*.7,zz)),Vector((0,-side,0)))[0]
                if hit is None:raise ValueError(f'CLOTH345_SASH_RAY:{side}:{j}:{k}:{xx}:{zz}')
                pts.append(hit+Vector((0,side*.010,0)))
        panels.append(np.array(pts).reshape(41,7,3))
    front,back=panels;bridge=[]
    for j in range(1,9):
        u=j/9;p=front[-1]*(1-u)+back[-1]*u
        for k in range(7):
            hit=shoulder_tree.ray_cast(Vector((p[k,0],p[k,1],1.9)),Vector((0,0,-1)))[0]
            if hit is None:raise ValueError('CLOTH345_SHOULDER_RAY')
            p[k,2]=max(p[k,2],hit.z+.010)
        bridge.append(p)
    sash_coords=[Vector(p) for p in np.concatenate((front,np.array(bridge),back[::-1])).reshape(-1,3)]
    # All rays completed before either dependent layer is changed; this handler
    # runs before the expensive190-frame contact solve in346.
    (out/'cloth-preflight346.json').write_text(json.dumps(dict(
        belt_samples=len(belt_coords),sash_samples=len(sash_coords),
        waist_faces=len(faces),shoulder_faces=len(shoulder_faces),
        geometry_complete=True,scope='support samples, not visual qualification'),indent=2)+'\n')
    bind(belt,belt_coords,tree,faces)
    bind(sash,sash_coords,shoulder_tree,shoulder_faces)
    # Follow the actual deformed coat at the loaded waist without allowing a
    # nearest-surface query to jump onto an arm or knee. This is a restricted
    # support copy with identical source bone weights, not a visible substitute.
    waist_faces=[tuple(p.vertices) for p in coat.data.polygons if all(
        .99<coat.data.vertices[i].co.z<1.36 and abs(coat.data.vertices[i].co.x)<.30
        for i in p.vertices)]
    ids=sorted({i for f in waist_faces for i in f});mapping={i:n for n,i in enumerate(ids)}
    mesh=bpy.data.meshes.new('346 waist support geometry')
    mesh.from_pydata([coat.data.vertices[i].co for i in ids],[],[[mapping[i] for i in f] for f in waist_faces]);mesh.update()
    proxy=bpy.data.objects.new('MF346 waist-only coat support',mesh);scene.collection.objects.link(proxy)
    proxy.parent=coat.parent;proxy.matrix_parent_inverse=coat.matrix_parent_inverse.copy();proxy.matrix_basis=coat.matrix_basis.copy();proxy.hide_render=True
    for n,i in enumerate(ids):
        for name,value in w[i].items():
            if name not in rig.data.bones:continue
            group=proxy.vertex_groups.get(name) or proxy.vertex_groups.new(name=name);group.add([n],value,'REPLACE')
    arm=proxy.modifiers.new('Same coat deformation','ARMATURE');arm.object=rig;arm.use_deform_preserve_volume=True
    smooth=proxy.modifiers.new('Coat outer continuity','SUBSURF');smooth.levels=1;smooth.render_levels=1
    weld=belt.modifiers.new('Closed woven waist seam','WELD');weld.merge_threshold=.0002
    bpy.context.view_layer.objects.active=belt
    bpy.ops.object.modifier_move_up(modifier=weld.name);bpy.ops.object.modifier_move_up(modifier=weld.name)
    contact=belt.modifiers.new('Actual waist cloth support','SHRINKWRAP');contact.target=proxy
    contact.wrap_method='NEAREST_SURFACEPOINT';contact.wrap_mode='ABOVE_SURFACE';contact.offset=.007
    bpy.ops.object.modifier_move_up(modifier=contact.name)
    rig.data.pose_position='POSE';rig['cloth345']=1;scene.frame_set(283);bpy.context.view_layer.update()
    result=dict(scope='Actual torso-owned layer repair; all poses require image inspection',layers=rows,contact_retained=True)
    (out/'leader-cloth345.json').write_text(json.dumps(result,indent=2)+'\n')
    return result


def run(bpy,out):
    import json
    from mathutils import Matrix,Vector,Quaternion
    from mathutils.bvhtree import BVHTree
    import importlib.util
    from pathlib import Path
    spec=importlib.util.spec_from_file_location('mf_finish345_support',Path(__file__).with_name('nihang_support.py'))
    support=importlib.util.module_from_spec(spec);spec.loader.exec_module(support)
    scene=support.select_production_scene(bpy);scene.frame_set(283)
    rig=bpy.data.objects['MF coherent Nihang rig'];coat=bpy.data.objects['MF coherent coat']
    if not rig.get('layer_refit_proof') or rig.get('finish345'):raise ValueError('FINISH345_PARENT')
    # Sample the actual rest coat boundary; retain its existing layer bindings.
    tree=BVHTree.FromPolygons([v.co for v in coat.data.vertices],[tuple(p.vertices) for p in coat.data.polygons])
    skirts=sorted([o for o in bpy.data.objects if o.name.startswith('MF coherent split chola')],key=lambda o:o.name)
    if len(skirts)!=2:raise ValueError('FINISH345_SKIRT_COUNT')
    for obj in skirts:
        if len(obj.data.vertices)!=20*49:raise ValueError('FINISH345_SKIRT_TOPOLOGY')
        side=1 if sum(v.co.x for v in obj.data.vertices)>0 else -1
        for k in range(49):
            angle=(.035+(math.pi-.07)*k/48)*side
            axis=Vector((math.sin(angle),-math.cos(angle),0))
            origin=Vector((0,-.02,1.145));hit=tree.ray_cast(origin+axis*.5,-axis)[0]
            if hit is None:raise ValueError('FINISH345_WAIST_SUPPORT')
            root=hit+axis*.004
            for j in range(20):obj.data.vertices[j*49+k].co=skirt_point(root,j/19,angle)
        obj.data.update()
    restored=restore_beard(bpy,rig)
    # Shaft is the actual planted/animated owner, not a substituted hand proxy.
    shaft=bpy.data.objects['LEADER spear world contact owner']
    proxy=bpy.data.objects['leader palm.001']
    suffix='.L';rest=rig.data.bones
    wrist_rest=rest['wrist'+suffix].head_local.copy()
    across=rest['finger2-1'+suffix].head_local-rest['finger5-1'+suffix].head_local
    mcp=sum((rest[f'finger{i}-1'+suffix].head_local for i in range(2,6)),Vector())/4
    longitudinal=mcp-wrist_rest;palm_rest=wrist_rest+longitudinal*.70
    records=[]
    def set_bone(pb,a,b,rotation=None):
        base=pb.bone.matrix_local.to_3x3()
        if rotation is None:rotation=base.col[1].normalized().rotation_difference((b-a).normalized()).to_matrix()@base
        mat=rotation.to_4x4();mat.translation=a
        pb.rotation_mode='QUATERNION';pb.matrix=mat
        for prop in ('location','rotation_quaternion','scale'):pb.keyframe_insert(prop,frame=f)
        bpy.context.view_layer.update()
    def chain(names,a,b,hand_rotation=None):
        axis=(b-a).normalized();p=a.copy()
        for index,name in enumerate(names):
            pb=rig.pose.bones[name];q=p+axis*pb.bone.length;rot=None
            if hand_rotation is not None:
                base=pb.bone.matrix_local.to_3x3();natural=base.col[1].normalized().rotation_difference(axis).to_matrix()@base
                target=Matrix(transported_frame(base,hand_rotation,axis).tolist())
                rot=natural.to_quaternion().slerp(target.to_quaternion(),(index+1)/len(names)).to_matrix()
            set_bone(pb,p,q,rot);p=q
        if (p-b).length>.0001:raise ValueError('FINISH345_ARM_LENGTH')
    for f in range(252,442):
        scene.frame_set(f);bpy.context.view_layer.update();inv=rig.matrix_world.inverted()
        origin=inv@shaft.matrix_world.translation
        up=(inv.to_3x3()@shaft.matrix_world.to_3x3()@Vector((0,0,1))).normalized()
        hint=inv@proxy.matrix_world.translation;center=origin+up*(hint-origin).dot(up)
        start=rig.pose.bones['upperarm01.L'].head.copy()
        # The grip may rotate around a cylindrical shaft. Use that freedom to
        # face the hand away from the shoulder, rather than global scene forward.
        forward=center-start;forward-=up*forward.dot(up)
        if forward.length<.02:raise ValueError('FINISH345_PALM_DIRECTION')
        rotation=Matrix(frame_map(across,longitudinal,up,forward).tolist())
        dorsal=(rotation@across.normalized()).cross((rotation@longitudinal).normalized()).normalized()
        palm=center+dorsal*.031
        wrist=palm-rotation@(palm_rest-wrist_rest)
        upper=sum(rest[n+'.L'].length for n in ('upperarm01','upperarm02'))
        lower=sum(rest[n+'.L'].length for n in ('lowerarm01','lowerarm02'))
        d=(wrist-start).length
        if not abs(upper-lower)+.001<d<upper+lower-.001:raise ValueError('FINISH345_ARM_REACH')
        palm_axis=(rotation@longitudinal).normalized()
        elbow=Vector(neutral_elbow(start,wrist,upper,lower,palm_axis))
        chain(['upperarm01.L','upperarm02.L'],start,elbow)
        chain(['lowerarm01.L','lowerarm02.L'],elbow,wrist,rotation)
        pb=rig.pose.bones['wrist.L'];set_bone(pb,wrist,wrist+rotation@(pb.bone.tail_local-pb.bone.head_local),rotation@pb.bone.matrix_local.to_3x3())
        hand=Matrix.Translation(wrist)@rotation.to_4x4()@Matrix.Translation(-wrist_rest)
        for digit in range(2,6):
            previous=None;total=0
            for j,angle in enumerate((1.10,1.20,.72),1):
                pb=rig.pose.bones[f'finger{digit}-{j}.L'];total-=angle
                rot=Quaternion(up,total).to_matrix()@rotation@pb.bone.matrix_local.to_3x3()
                a=hand@pb.bone.head_local if previous is None else previous
                previous=a+rot.col[1].normalized()*pb.bone.length;set_bone(pb,a,previous,rot)
        # Thumb metacarpal opposes, distal pair rests over the index finger.
        thumbs=[rig.pose.bones[f'finger1-{j}.L'] for j in (1,2,3)]
        index=rig.pose.bones['finger2-2.L'];base=hand@thumbs[0].bone.head_local
        first=base+(index.head-base).normalized()*thumbs[0].bone.length
        target=(index.head+index.tail)*.5+dorsal*.010
        lens=[p.bone.length for p in thumbs[1:]];distance=(target-first).length
        if not abs(lens[0]-lens[1])+.0001<distance<sum(lens)-.002:raise ValueError('FINISH345_THUMB_REACH')
        joint=Vector(support.bend_joint(first,target,*lens,tuple(dorsal)))
        ends=[base,first,joint,target]
        for pb,a,b in zip(thumbs,ends,ends[1:]):
            rot=rotation@pb.bone.matrix_local.to_3x3()
            rot=rot.col[1].normalized().rotation_difference((b-a).normalized()).to_matrix()@rot
            set_bone(pb,a,b,rot)
        bend=math.degrees((wrist-elbow).normalized().angle(palm_axis))
        records.append(dict(frame=f,shaft=list(center),wrist=list(wrist),elbow=list(elbow),palm=list(palm),wrist_bend_degrees=bend,thumb_error=(thumbs[-1].tail-target).length))
    scene.frame_set(283);bpy.context.view_layer.update();rig['finish345']=1
    (out/'leader-contact345.json').write_text(json.dumps(records,indent=2)+'\n')
    scene.frame_set(327);bpy.context.view_layer.update();visible=[]
    for obj in bpy.data.objects:
        if obj.hide_render or obj.type not in {'MESH','CURVE'}:continue
        if 'sash' not in obj.name.lower() and 'wrap' not in obj.name.lower():continue
        row=dict(name=obj.name,parent=obj.parent.name if obj.parent else None,materials=[m.name if m else None for m in obj.data.materials])
        if obj.type=='MESH':
            ev=obj.evaluated_get(bpy.context.evaluated_depsgraph_get());pts=[obj.matrix_world@v.co for v in ev.data.vertices]
            row['bounds']=[[min(p[i] for p in pts),max(p[i] for p in pts)] for i in range(3)]
            row['modifiers']=[dict(name=m.name,type=m.type) for m in obj.modifiers]
        visible.append(row)
    (out/'leader-layer-ownership345.json').write_text(json.dumps(visible,indent=2)+'\n')
    scene.frame_set(283);bpy.context.view_layer.update()
    return dict(scope='Shaft-relative anatomical grasp and supported skirt origin; image review required',frames=len(records),maximum_thumb_error=max(x['thumb_error'] for x in records),skirt_root=1.145,restored_beard=restored)
