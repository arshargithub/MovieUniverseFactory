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


def restore_beard(bpy,rig):
    """Restore omitted fitted base cards from the already-inspected donor."""
    from pathlib import Path
    from mathutils import Matrix
    donor=Path(__file__).resolve().parents[4]/'.runtime/art-direction/series01-sikh265/candidate-04/character.blend'
    names=['Sikh265 coherent MPFB male.rehmanpolanski_'+n+'_viking' for n in ('beard','moustache')]
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
    if not rig.get('finish345') or rig.get('cloth345'):raise ValueError('CLOTH345_PARENT')
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
    kd=KDTree(len(coat.data.vertices))
    for v in coat.data.vertices:kd.insert(v.co,v.index)
    kd.balance();rows=[]
    def bind(obj,coords):
        if len(coords)!=len(obj.data.vertices):raise ValueError('CLOTH345_LAYER_TOPOLOGY')
        for mod in list(obj.modifiers):obj.modifiers.remove(mod)
        obj.vertex_groups.clear()
        for v,p in zip(obj.data.vertices,coords):
            v.co=p;_,_,face,_=tree.find_nearest(p)
            if face is None:raise ValueError('CLOTH345_NO_TORSO')
            ids=faces[face];inv=[1/max(.003,(coat.data.vertices[i].co-p).length) for i in ids];total=sum(inv)
            weights={}
            for i,weight in zip(ids,inv):
                for name,value in w[i].items():
                    if allowed(name):weights[name]=weights.get(name,0)+value*weight/total
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
    bind(belt,coords)
    sash=bpy.data.objects['MF coherent shoulder sash'];panels=[]
    for side in (-1,1):
        pts=[]
        for j in range(41):
            t=j/40;x=.12-.25*t;z=1.145*(1-t)+1.55*t
            for k in range(7):
                off=(k/6-.5)*.065;xx=x+off*.84;zz=z+off*.54
                hit=tree.ray_cast(Vector((xx,side*.7,zz)),Vector((0,-side,0)))[0]
                if hit is None:raise ValueError('CLOTH345_SASH_RAY')
                pts.append(hit+Vector((0,side*.010,0)))
        panels.append(np.array(pts).reshape(41,7,3))
    front,back=panels;bridge=[]
    for j in range(1,9):
        u=j/9;p=front[-1]*(1-u)+back[-1]*u
        for k in range(7):
            hit=tree.ray_cast(Vector((p[k,0],p[k,1],1.9)),Vector((0,0,-1)))[0]
            if hit is None:raise ValueError('CLOTH345_SHOULDER_RAY')
            p[k,2]=max(p[k,2],hit.z+.010)
        bridge.append(p)
    bind(sash,[Vector(p) for p in np.concatenate((front,np.array(bridge),back[::-1])).reshape(-1,3)])
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
    def chain(names,a,b,roll_axis=None):
        axis=(b-a).normalized();p=a.copy()
        for index,name in enumerate(names):
            pb=rig.pose.bones[name];q=p+axis*pb.bone.length;rot=None
            if roll_axis is not None:
                x=(roll_axis-axis*roll_axis.dot(axis)).normalized();z=x.cross(axis).normalized()
                target=Matrix((x,axis,z)).transposed()
                base=pb.bone.matrix_local.to_3x3();natural=base.col[1].normalized().rotation_difference(axis).to_matrix()@base
                rot=natural.to_quaternion().slerp(target.to_quaternion(),(index+1)/len(names)).to_matrix()
            set_bone(pb,p,q,rot);p=q
        if (p-b).length>.0001:raise ValueError('FINISH345_ARM_LENGTH')
    for f in range(252,442):
        scene.frame_set(f);bpy.context.view_layer.update();inv=rig.matrix_world.inverted()
        origin=inv@shaft.matrix_world.translation
        up=(inv.to_3x3()@shaft.matrix_world.to_3x3()@Vector((0,0,1))).normalized()
        hint=inv@proxy.matrix_world.translation;center=origin+up*(hint-origin).dot(up)
        rotation=Matrix(frame_map(across,longitudinal,up,Vector((0,-1,0))).tolist())
        dorsal=(rotation@across.normalized()).cross((rotation@longitudinal).normalized()).normalized()
        palm=center+dorsal*.031
        wrist=palm-rotation@(palm_rest-wrist_rest)
        start=rig.pose.bones['upperarm01.L'].head.copy()
        upper=sum(rest[n+'.L'].length for n in ('upperarm01','upperarm02'))
        lower=sum(rest[n+'.L'].length for n in ('lowerarm01','lowerarm02'))
        d=(wrist-start).length
        if not abs(upper-lower)+.001<d<upper+lower-.001:raise ValueError('FINISH345_ARM_REACH')
        elbow=Vector(support.bend_joint(start,wrist,upper,lower,(1,.35,-.2)))
        chain(['upperarm01.L','upperarm02.L'],start,elbow)
        roll_axis=rotation@rest['wrist.L'].matrix_local.to_3x3().col[0]
        chain(['lowerarm01.L','lowerarm02.L'],elbow,wrist,roll_axis)
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
        records.append(dict(frame=f,shaft=list(center),wrist=list(wrist),palm=list(palm),thumb_error=(thumbs[-1].tail-target).length))
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
