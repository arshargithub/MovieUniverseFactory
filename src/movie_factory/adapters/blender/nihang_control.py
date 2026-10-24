"""Trusted no-edit native control. Not an animation builder or art evaluator.

Imports bpy only inside the worker. Recipes never contain code, paths, camera
changes or pose edits. A future authoring vocabulary needs separate qualification.
"""
import hashlib
import json
from pathlib import Path

OBJECTS = ('horse.rig', 'HORSE hind support pivot', 'mounted leader',
           '320 articulated upper body mounted leader')
# Exact diagnosed legacy320 defect, permitted ONLY for this unchanged negative
# control. It is not a working-rig certificate or a general invalid-driver waiver.
LEGACY_DRIVER_DEFECT = '054bf94aeb90448916005e7c0e8c5dbe163e7fbbea52cde230adf8c32ee0e21c'
ANATOMY_VIEWS = {f'anatomy_{pose}_{view}' for pose in ('rest','bend','custom','linear') for view in ('front','back')}
ANATOMY_VIEWS |= {'anatomy_custom_side','anatomy_linear_side'}


def validate(recipe):
    fields={'operation', 'frame', 'width', 'height', 'samples'}
    if isinstance(recipe,dict) and recipe.get('operation')=='nihang_frames':
        fields.add('frames')
        if 'view' in recipe:fields.add('view')
    if not isinstance(recipe, dict) or set(recipe) != fields:
        raise ValueError('NIHANG_RECIPE_FIELDS')
    if recipe['operation'] not in {'nihang_save', 'nihang_render', 'nihang_rig_inspect','nihang_cast_inspect','nihang_frames'}:
        raise ValueError('NIHANG_OPERATION')
    for key, lo, hi in [('frame', 252, 441), ('width', 64, 1080), ('height', 64, 1920), ('samples', 1, 32)]:
        if type(recipe[key]) is not int or not lo <= recipe[key] <= hi:
            raise ValueError('NIHANG_RECIPE_BOUND:' + key)
    if recipe['operation']=='nihang_frames':
        if not isinstance(recipe.get('view','production'),str) or recipe.get('view','production') not in ({'flag363','flag363_reverse','production','horse_chest','horse_chest_side','horse_chest_no_corrective','horse_chest_side_no_corrective','leader_right_contact','leader_left_contact','horse_head','horse_head_reverse','leader_front','leader_reverse','leader_contact','leader_anatomy','leader_face','leader_face_left','leader_face_right','leader_face_profile','crowd_front','crowd_reverse','neutral_front','neutral_back','neutral_side'} | ANATOMY_VIEWS):
            raise ValueError('NIHANG_DIAGNOSTIC_VIEW')
        frames=recipe['frames']
        if (not isinstance(frames,list) or not 1<=len(frames)<=16 or
                any(type(f) is not int or not 252<=f<=441 for f in frames) or
                len(set(frames))!=len(frames) or recipe['frame'] not in frames):
            raise ValueError('NIHANG_FRAME_SET')
    return recipe


def diagnostic_camera(bpy,view):
    """Temporary evidence camera only. No production-camera key edits or save."""
    from mathutils import Vector
    if view in {'flag363','flag363_reverse'}:
        flag=bpy.data.objects['MF363 physically solved tied pennant'];ev=flag.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=ev.to_mesh();target=sum((ev.matrix_world@v.co for v in mesh.vertices),Vector())/len(mesh.vertices);ev.to_mesh_clear();shaft=bpy.data.objects['LEADER spear world contact owner']
        data=bpy.data.cameras.new('363 cloth diagnostic');data.type='ORTHO';data.ortho_scale=1.2;camera=bpy.data.objects.new(data.name,data);bpy.context.scene.collection.objects.link(camera);camera.location=target+shaft.matrix_world.to_quaternion()@Vector(((-1 if view.endswith('reverse') else 1)*1.2,-.7,.1));camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler();return camera
    if view.endswith('_no_corrective'):
        for key in list(bpy.data.objects['horse'].data.shape_keys.key_blocks)[1:]:key.mute=True
        bpy.context.view_layer.update();view=view.removesuffix('_no_corrective')
    if view in {'horse_chest','horse_chest_side'}:
        rig=bpy.data.objects['horse.rig'];target=rig.matrix_world@(rig.pose.bones['neck'].head+Vector((0,.03,-.35)))
        head=rig.matrix_world@rig.pose.bones['head'].head;forward=head-target;forward.z=0;forward.normalize();side=Vector((-forward.y,forward.x,0))
        data=bpy.data.cameras.new('363 chest diagnostic');data.type='ORTHO';data.ortho_scale=1.65
        camera=bpy.data.objects.new(data.name,data);bpy.context.scene.collection.objects.link(camera)
        camera.location=target+(side*2.5 if view.endswith('_side') else forward*2+side*.7)+Vector((0,0,.12));camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler();return camera
    if view in {'leader_right_contact','leader_left_contact'}:
        rig=bpy.data.objects['MF coherent Nihang rig'];root=bpy.data.objects['mounted leader'];side='R' if view=='leader_right_contact' else 'L'
        target=rig.matrix_world@rig.pose.bones['finger3-1.'+side].head
        data=bpy.data.cameras.new('363 hand diagnostic');data.type='ORTHO';data.ortho_scale=.32
        camera=bpy.data.objects.new(data.name,data);bpy.context.scene.collection.objects.link(camera)
        camera.location=target+root.matrix_world.to_quaternion()@Vector((-.8 if side=='R' else .8,-1.4,.2));camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler();return camera
    if view in {'horse_head','horse_head_reverse'}:
        rig=bpy.data.objects['horse.rig'];bone=rig.pose.bones['head']
        target=rig.matrix_world@((bone.head+bone.tail)*.5)
        data=bpy.data.cameras.new('MF diagnostic camera temporary');data.type='ORTHO';data.ortho_scale=1.25
        camera=bpy.data.objects.new(data.name,data);bpy.context.scene.collection.objects.link(camera)
        camera.location=target+rig.matrix_world.to_quaternion()@Vector((-1.4 if view.endswith('_reverse') else 1.4,-1.8,.35));camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler()
        return camera
    if view.startswith('leader_face'):
        rig=bpy.data.objects['MF coherent Nihang rig'];root=bpy.data.objects['mounted leader']
        target=rig.matrix_world@((rig.pose.bones['eye.L'].head+rig.pose.bones['eye.R'].head)*.5)+Vector((0,0,.015))
        data=bpy.data.cameras.new('MF diagnostic camera temporary');data.type='ORTHO';data.ortho_scale=.48
        camera=bpy.data.objects.new('MF diagnostic camera temporary',data);bpy.context.scene.collection.objects.link(camera)
        offset={'leader_face':(.08,-1,.05),'leader_face_left':(.70,-1,.02),'leader_face_right':(-.70,-1,.02),'leader_face_profile':(1,-.08,.02)}[view]
        camera.location=target+root.matrix_world.to_quaternion()@Vector(offset);camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler()
        light=bpy.data.lights.new('353 face diagnostic fill','AREA');light.energy=35;light.shape='DISK';light.size=1.0
        obj=bpy.data.objects.new('353 face diagnostic fill',light);bpy.context.scene.collection.objects.link(obj)
        obj.location=camera.location+Vector((0,0,.2));obj.rotation_euler=(target-obj.location).to_track_quat('-Z','Y').to_euler()
        return camera
    if view in ANATOMY_VIEWS:
        return anatomy_control(bpy,view)
    if view=='leader_anatomy':
        for ob in bpy.data.objects:
            if ob.name.startswith(('MF coherent coat','MF coherent pants','MF coherent boots','MF coherent split chola','MF coherent waist wrap','MF coherent shoulder sash','MF347 chola')):
                ob.hide_render=True
        view='leader_reverse'
    if view=='leader_contact':
        rig=bpy.data.objects['MF coherent Nihang rig'];root=bpy.data.objects['mounted leader']
        target=rig.matrix_world@rig.pose.bones['finger3-1.L'].head
        data=bpy.data.cameras.new('MF diagnostic camera temporary');data.type='ORTHO';data.ortho_scale=.40
        camera=bpy.data.objects.new('MF diagnostic camera temporary',data);bpy.context.scene.collection.objects.link(camera)
        camera.location=target+root.matrix_world.to_quaternion()@Vector((.8,-1.4,.20))
        camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler()
        return camera
    if view.startswith('neutral_'):
        if bpy.context.scene.name!='MF neutral garment studio':raise ValueError('NEUTRAL_VIEW_SCENE')
        target=Vector((0,0,1.19))
        offset=Vector({'neutral_front':(0,-3,.07),'neutral_back':(0,3,.07),'neutral_side':(3,-.15,.07)}[view])
        data=bpy.data.cameras.new('MF diagnostic camera temporary')
        camera=bpy.data.objects.new('MF diagnostic camera temporary',data)
        bpy.context.scene.collection.objects.link(camera)
        camera.location=target+offset
        camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler()
        data.type='ORTHO';data.ortho_scale=1.22
        return camera
    leader=view.startswith('leader_')
    root=bpy.data.objects['mounted leader' if leader else 'FOOT WARRIOR 0']
    if not leader:
        # Diagnostic only: neighbours occluded the target's face and entire torso.
        # Production frames retain the complete ensemble unchanged.
        for other in bpy.data.objects:
            if other.name.startswith('FOOT WARRIOR ') and other!=root:
                for child in other.children_recursive:child.hide_render=True
    upper=next(o for o in root.children if o.name.startswith('320 articulated upper body'))
    head=next(o for o in upper.children if o.name.startswith('secondary adult head'))
    target=head.matrix_world.translation+Vector((0,0,-.22 if leader else -.35))
    facing=-1 if leader else 1
    if view.endswith('_reverse'):facing*=-1
    offset=root.matrix_world.to_quaternion()@Vector((.6,facing*1.9,.12))
    data=bpy.data.cameras.new('MF diagnostic camera temporary')
    camera=bpy.data.objects.new('MF diagnostic camera temporary',data)
    bpy.context.scene.collection.objects.link(camera)
    camera.location=target+offset
    camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler()
    data.lens=55
    return camera


def anatomy_control(bpy,view):
    """Temporary matched body-only controls. Never saved or a pose repair."""
    from mathutils import Vector, Matrix
    import math
    rig=bpy.data.objects['MF coherent Nihang rig']
    body=bpy.data.objects['MF coherent Nihang body']
    for ob in bpy.data.objects:
        if ob.type in {'MESH','CURVE','CURVES','LIGHT'}: ob.hide_render=ob!=body
    pose=view.split('_')[1]
    if pose=='linear':
        for mod in body.modifiers:
            if mod.type=='ARMATURE':mod.use_deform_preserve_volume=False
    if pose=='rest':rig.data.pose_position='REST'
    elif pose=='bend':
        rig.animation_data_clear()
        for pb in rig.pose.bones:pb.matrix_basis=Matrix.Identity(4)
        pb=rig.pose.bones['lowerarm01.L'];pb.rotation_mode='XYZ';pb.rotation_euler.x=math.radians(90)
    # Camera and illumination co-move with the rig, not with the tested arm.
    matrix=rig.matrix_world.copy();q=matrix.to_quaternion()
    target=matrix@Vector((0,0,1.37))
    for name,offset,power,size in [('key',(-1.4,-1.8,2.1),450,2.0),('fill',(1.2,1.2,1.6),350,2.0)]:
        light=bpy.data.lights.new('351 anatomy '+name,'AREA');light.energy=power;light.shape='DISK';light.size=size
        ob=bpy.data.objects.new(light.name,light);bpy.context.scene.collection.objects.link(ob)
        ob.location=target+q@Vector(offset);ob.rotation_euler=(target-ob.location).to_track_quat('-Z','Y').to_euler()
    data=bpy.data.cameras.new('MF diagnostic camera temporary');data.type='ORTHO';data.ortho_scale=1.40
    camera=bpy.data.objects.new(data.name,data);bpy.context.scene.collection.objects.link(camera)
    offset=(3,0,.12) if view.endswith('side') else (.12,-3 if view.endswith('front') else 3,.12)
    camera.location=target+q@Vector(offset)
    camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler()
    return camera


def anatomy_inventory(bpy):
    """Actual joint frames and ownership, not a pose-quality assertion."""
    rig=bpy.data.objects['MF coherent Nihang rig'];body=bpy.data.objects['MF coherent Nihang body']
    names=[n for n in rig.data.bones.keys() if n.startswith(('upperarm','lowerarm','clavicle','shoulder','wrist'))]
    bones={n:dict(parent=rig.data.bones[n].parent.name if rig.data.bones[n].parent else None,
        rest_head=list(rig.data.bones[n].head_local),rest_tail=list(rig.data.bones[n].tail_local),
        rest_matrix=[list(r) for r in rig.data.bones[n].matrix_local],
        pose_matrix=[list(r) for r in rig.pose.bones[n].matrix],
        basis=[list(r) for r in rig.pose.bones[n].matrix_basis],
        deform=rig.data.bones[n].use_deform) for n in names}
    weights={n:[] for n in names}
    for v in body.data.vertices:
        for g in v.groups:
            name=body.vertex_groups[g.group].name
            if name in weights and g.weight>.05: weights[name].append([*v.co,g.weight])
    return dict(bones=bones,weighted_vertices=weights,
        body_matrix=[list(r) for r in body.matrix_world],rig_matrix=[list(r) for r in rig.matrix_world],
        modifiers=[dict(name=m.name,type=m.type,render=m.show_render,
          preserve_volume=getattr(m,'use_deform_preserve_volume',None)) for m in body.modifiers])


def cast_inventory(bpy):
    """Read-only first supporting actors; inspect real owners before adapting."""
    from mathutils import Vector
    roots=[bpy.data.objects['mounted leader']]
    crowd=sorted([o for o in bpy.data.objects if o.name.startswith('FOOT WARRIOR ')],key=lambda o:o.name)
    if not crowd:raise ValueError('CAST_CROWD_MISSING')
    roots.append(crowd[0]);objects={};materials={}
    for root in roots:
        for obj in [root,*root.children_recursive]:
            row={'type':obj.type,'parent':obj.parent.name if obj.parent else None,'hidden':obj.hide_render,
                 'world':[[float(v) for v in r] for r in obj.matrix_world],
                 'local':[[float(v) for v in r] for r in obj.matrix_local]}
            if obj.type=='MESH':
                row.update(vertices=len(obj.data.vertices),polygons=len(obj.data.polygons),
                           smooth_polygons=sum(p.use_smooth for p in obj.data.polygons),
                           uv_layers=[u.name for u in obj.data.uv_layers],
                           shape_keys=len(obj.data.shape_keys.key_blocks) if obj.data.shape_keys else 0,
                           modifiers=[{'name':m.name,'type':m.type,'render':m.show_render} for m in obj.modifiers])
                points=[Vector(v) for v in obj.bound_box]
                row['local_bounds']={k:[fun(p[i] for p in points) for i in range(3)] for k,fun in [('min',min),('max',max)]}
            if obj.type=='CURVE':row.update(splines=len(obj.data.splines),bevel_depth=obj.data.bevel_depth)
            if obj.data and hasattr(obj.data,'materials'):
                row['materials']=[m.name if m else None for m in obj.data.materials]
                for mat in obj.data.materials:
                    if mat is None or mat.name in materials:continue
                    nodes={}
                    for n in mat.node_tree.nodes if mat.use_nodes else []:
                        inputs={}
                        for socket in n.inputs:
                            if not hasattr(socket,'default_value'):continue
                            value=socket.default_value
                            if isinstance(value,(str,bool,int,float)):inputs[socket.name]={'value':value,'linked':socket.is_linked}
                            elif hasattr(value,'__iter__'):inputs[socket.name]={'value':list(value),'linked':socket.is_linked}
                        nodes[n.name]={'type':n.bl_idname,'inputs':inputs}
                        if hasattr(n,'color_ramp'):nodes[n.name]['ramp']=[{'position':e.position,'color':list(e.color)} for e in n.color_ramp.elements]
                    materials[mat.name]={'nodes':nodes}
            objects[obj.name]=row
    return {'frame':bpy.context.scene.frame_current,'actors':[r.name for r in roots],
            'objects':objects,'materials':materials,'scope':'Actual supporting-actor ownership, topology counts, UVs, cached poses and material parameters; no mutation or appearance pass.'}


def rig_inventory(bpy):
    """Read-only ownership evidence. Never execute asset scripts or repair by inference."""
    rig = bpy.data.objects.get('horse.rig')
    if rig is None or rig.type != 'ARMATURE':
        raise ValueError('NIHANG_HORSE_RIG_MISSING')
    def vector(v): return [float(x) for x in v]
    def matrix(m): return [vector(row) for row in m]
    bones = {}
    for b in rig.pose.bones:
        constraints = []
        for c in b.constraints:
            row = {'name': c.name, 'type': c.type, 'influence': c.influence,
                   'mute': c.mute, 'valid': c.is_valid}
            for key in ('target', 'pole_target'):
                target = getattr(c, key, None)
                row[key] = target.name if target else None
            for key in ('subtarget', 'pole_subtarget', 'chain_count', 'pole_angle',
                        'use_stretch', 'owner_space', 'target_space', 'mix_mode'):
                if hasattr(c, key): row[key] = getattr(c, key)
            constraints.append(row)
        bones[b.name] = {'parent': b.parent.name if b.parent else None,
            'deform': b.bone.use_deform, 'head_rest': vector(b.bone.head_local),
            'tail_rest': vector(b.bone.tail_local), 'rest': matrix(b.bone.matrix_local),
            'head': vector(b.head), 'tail': vector(b.tail), 'matrix': matrix(b.matrix),
            'basis': matrix(b.matrix_basis), 'constraints': constraints,
            'properties': {k: v for k, v in b.items() if isinstance(v, (int, float, str, bool))}}
    drivers = []
    for owner in (rig, rig.data):
        ad = owner.animation_data
        for fc in ad.drivers if ad else []:
            d = fc.driver
            drivers.append({'owner': owner.name, 'owner_type': type(owner).__name__,
                'path': fc.data_path, 'index': fc.array_index, 'type': d.type,
                'valid': d.is_valid, 'expression': d.expression,
                'variables': [{'name': v.name, 'type': v.type,
                    'targets': [{'id': t.id.name if t.id else None, 'id_type': t.id_type,
                                 'data_path': t.data_path, 'bone_target': t.bone_target}
                                for t in v.targets]} for v in d.variables]})
    meshes = []
    for obj in bpy.data.objects:
        if obj.type != 'MESH': continue
        mods = [m for m in obj.modifiers if m.type == 'ARMATURE' and m.object == rig]
        if not mods: continue
        meshes.append({'name': obj.name, 'vertices': len(obj.data.vertices),
            'groups': [g.name for g in obj.vertex_groups],
            'modifiers': [{'name': m.name, 'type': m.type, 'viewport': m.show_viewport,
                           'render': m.show_render} for m in obj.modifiers]})
    # Bounded rest-space surface evidence for headstall placement. Bone tails
    # are control landmarks, not anatomical muzzle/eye locations.
    head_surface = {}
    horse = bpy.data.objects.get('horse')
    if horse is not None and horse.type == 'MESH':
        transform = rig.matrix_world.inverted() @ horse.matrix_world
        groups = {g.index:g.name for g in horse.vertex_groups}
        verts = [(v.index, transform @ v.co) for v in horse.data.vertices
                 if sum(g.weight for g in v.groups if groups.get(g.group) in
                        {'DEF-head','DEF-jaw'}) > .5]
        if verts:
            head_surface['bounds'] = [[min(p[k] for _,p in verts),max(p[k] for _,p in verts)] for k in range(3)]
            head_surface['vertex_count'] = len(verts)
            head_surface['sections'] = []
            lo,hi=head_surface['bounds'][1]
            for i in range(16):
                y=lo+(hi-lo)*(i+.5)/16
                points=[p for _,p in verts if abs(p.y-y)<(hi-lo)/32]
                if points:head_surface['sections'].append({'y':y,'count':len(points),
                    'x':[min(p.x for p in points),max(p.x for p in points)],
                    'z':[min(p.z for p in points),max(p.z for p in points)]})
            head_surface['materials']={}
            for index,mat in enumerate(horse.data.materials):
                ids={v for poly in horse.data.polygons if poly.material_index==index for v in poly.vertices}
                points=[p for v,p in verts if v in ids]
                if points:head_surface['materials'][str(index)]={'name':mat.name if mat else None,'count':len(points),
                    'bounds':[[min(p[k] for p in points),max(p[k] for p in points)] for k in range(3)]}
    head_center=rig.matrix_world@rig.pose.bones['DEF-head'].head
    nearby=[]
    for obj in bpy.context.scene.objects:
        if obj.type not in {'MESH','CURVE'} or obj.hide_render:continue
        from mathutils import Vector
        world=[obj.matrix_world@Vector(v) for v in obj.bound_box]
        lo=[min(v[k] for v in world) for k in range(3)];hi=[max(v[k] for v in world) for k in range(3)]
        distance=sum(max(lo[k]-head_center[k],0,head_center[k]-hi[k])**2 for k in range(3))**.5
        if distance>.65 and 'rein' not in obj.name.lower():continue
        row={'name':obj.name,'type':obj.type,'data':obj.data.name,'parent':obj.parent.name if obj.parent else None,
             'bbox_distance':distance,'materials':[{'name':slot.material.name if slot.material else None,'link':slot.link} for slot in obj.material_slots],
             'modifiers':[{'name':m.name,'type':m.type} for m in obj.modifiers]}
        if obj.type=='CURVE':
            row['splines']=[{'type':sp.type,'material_index':sp.material_index,'points':[vector(obj.matrix_world@Vector(p.co[:3])) for p in sp.points]} for sp in obj.data.splines if len(sp.points)<=20]
            row['shape_keys']=obj.data.shape_keys.name if obj.data.shape_keys else None
        nearby.append(row)
    return {'rig': rig.name, 'world': matrix(rig.matrix_world), 'bones': bones,
            'drivers': drivers, 'deformed_meshes': meshes,
            'head_surface_rest':head_surface,
            'near_head_visible_objects':nearby,
            'scope': 'Read-only horse controls, rest/evaluated joints, constraint ownership and driver target paths.'}


def digest_file(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def selected_state(bpy, frame):
    scene = bpy.context.scene
    scene.frame_set(frame)
    bpy.context.view_layer.update()
    def matrix(m):
        return [[round(float(v), 6) for v in row] for row in m]
    result = {'frame': frame, 'objects': {}, 'camera': scene.camera.name if scene.camera else None,
              'object_count': len(bpy.data.objects)}
    # In the isolated neutral proof, production objects belong to another scene.
    # A fresh open leaves their unevaluated matrices at identity. Evaluate their
    # owning scene explicitly; never compare cached old matrices with identities.
    if scene.name=='MF neutral garment studio':
        owners=[s for s in bpy.data.scenes if s!=scene and all(n in s.objects for n in OBJECTS)]
        if len(owners)!=1:raise ValueError('NEUTRAL_SOURCE_SCENE_AMBIGUOUS')
        bpy.context.window.scene=owners[0];owners[0].frame_set(frame);bpy.context.view_layer.update()
    for name in OBJECTS:
        obj = bpy.data.objects.get(name)
        if obj is None:
            raise ValueError('NIHANG_REQUIRED_OBJECT_MISSING:' + name)
        result['objects'][name] = {'type': obj.type, 'world': matrix(obj.matrix_world),
            'parent': obj.parent.name if obj.parent else None}
        if obj.pose:
            result['objects'][name]['bones'] = {bone.name: {
                'matrix': matrix(bone.matrix), 'basis': matrix(bone.matrix_basis)}
                for bone in sorted(obj.pose.bones, key=lambda b: b.name)}
    if bpy.context.window.scene!=scene:
        bpy.context.window.scene=scene;scene.frame_set(frame);bpy.context.view_layer.update()
    if not scene.camera:
        raise ValueError('NIHANG_CAMERA_MISSING')
    result['camera_matrix'] = matrix(scene.camera.matrix_world)
    result['camera_lens'] = scene.camera.data.lens
    result['authored_meshes'] = {}
    for obj in bpy.data.objects:
        if obj.type == 'MESH' and (obj.name.startswith('MF Nihang ') or obj.get('mf_supporting_appearance')):
            geometry = {'vertices': [[round(float(x), 6) for x in v.co] for v in obj.data.vertices],
                        'faces': [list(p.vertices) for p in obj.data.polygons]}
            mats = []
            for mat in obj.data.materials:
                node = mat.node_tree.nodes.get('Principled BSDF') if mat and mat.use_nodes else None
                if node:
                    mats.append({'color': list(node.inputs['Base Color'].default_value),
                                 'roughness': node.inputs['Roughness'].default_value})
            result['authored_meshes'][obj.name] = {'geometry_hash': hashlib.sha256(
                json.dumps(geometry, sort_keys=True).encode()).hexdigest(),
                'vertices': len(obj.data.vertices), 'faces': len(obj.data.polygons), 'materials': mats}
    return result


def script_diagnostics(bpy):
    """Inspect untrusted embedded code as DATA; never execute or register it.

    Autoexec warning alone is not a failed dependency. Only Blender's simple
    expression evaluator is admitted; Python namespace drivers stay blocked.
    """
    texts = []
    for item in bpy.data.texts:
        body = item.as_string()
        if len(body.encode()) > 256000:
            raise ValueError('NIHANG_EMBEDDED_TEXT_TOO_LARGE')
        texts.append({'name': item.name, 'use_module': bool(item.use_module),
                      'sha256': hashlib.sha256(body.encode()).hexdigest(), 'body': body})
    drivers = []
    # All animation-capable IDs, including shape keys and material node trees.
    visited = set()
    def inspect(item):
        if item.as_pointer() in visited:
            return
        visited.add(item.as_pointer())
        data = getattr(item, 'animation_data', None)
        for curve in data.drivers if data else []:
            d = curve.driver
            drivers.append({'owner': item.name, 'owner_type': type(item).__name__, 'users': item.users,
                'path': curve.data_path, 'index': curve.array_index,
                'type': d.type, 'expression': d.expression, 'valid': bool(d.is_valid),
                'simple': bool(d.is_simple_expression),
                'targets': [{'name': v.name, 'type': v.type, 'ids': [t.id.name if t.id else None for t in v.targets]}
                            for v in d.variables]})
        tree = getattr(item, 'node_tree', None)
        if tree: inspect(tree)
    for prop in bpy.data.bl_rna.properties:
        if prop.type == 'COLLECTION':
            for item in getattr(bpy.data, prop.identifier):
                if isinstance(item, bpy.types.ID): inspect(item)
    blocked = [d for d in drivers if d['users'] > 0 and
               (not d['valid'] or (d['type'] == 'SCRIPTED' and not d['simple']))]
    legacy = hashlib.sha256(json.dumps(blocked, sort_keys=True).encode()).hexdigest() == LEGACY_DRIVER_DEFECT
    return {'autoexec_warning': bool(bpy.app.autoexec_fail),
            'message': bpy.app.autoexec_fail_message, 'embedded_texts': texts, 'drivers': drivers,
            'blocked_drivers': [] if legacy else blocked,
            'known_source_defects': blocked if legacy else [],
            'rig_qualified': not blocked,
            'orphan_driver_count': sum(d['users'] == 0 for d in drivers)}


def dependency_relevant(collection, item, linked_ids=None):
    """A fully appended, unused library is input provenance, not a live link.

    Blender drops that orphan ID on save/reopen. Keep input provenance in the
    admitted source bindings; retain every actually used/fake-user library here.
    Other dependency collections are unchanged.
    """
    if collection!='libraries':return True
    if linked_ids is not None:
        return any(getattr(block,'library',None)==item for block in linked_ids)
    return item.users!=0 or item.use_fake_user


def dependencies(bpy, root):
    """Scoped external-file inventory; not complete simulation portability."""
    found = {}
    # Appending can leave nonzero weak provenance users on a library ID, even
    # though no data remains externally linked. Inventory actual linked IDs;
    # the admitted donor hash remains immutable input provenance separately.
    all_ids=list(bpy.data.user_map())
    for collection in ('images', 'libraries', 'cache_files', 'movieclips', 'sounds', 'fonts', 'volumes'):
        for item in getattr(bpy.data, collection):
            if not dependency_relevant(collection,item,all_ids):continue
            filename = getattr(item, 'filepath', '')
            if not filename or filename == '<builtin>' or getattr(item, 'packed_file', None):
                continue
            if collection == 'images' and item.source in {'GENERATED', 'VIEWER'}:
                continue
            resolved = Path(bpy.path.abspath(filename, library=getattr(item, 'library', None))).resolve()
            if not resolved.is_relative_to(root):
                raise ValueError('NIHANG_EXTERNAL_DEPENDENCY_OUTSIDE_ROOT:' + item.name)
            if resolved.suffix.lower() not in {'.png', '.jpg', '.jpeg', '.exr', '.hdr', '.tif', '.tiff', '.webp',
                    '.blend', '.abc', '.vdb', '.usd', '.usdc', '.ogg', '.wav', '.mp3', '.mp4', '.mov', '.bphys'}:
                raise ValueError('NIHANG_UNSUPPORTED_DEPENDENCY:' + item.name)
            if not resolved.is_file():
                raise ValueError('NIHANG_MISSING_DEPENDENCY:' + item.name)
            rel = str(resolved.relative_to(root))
            found[rel] = {'path': rel, 'sha256': digest_file(resolved)}
    return {'bindings': found, 'scope': 'Images, libraries, cache_files, clips, sounds, fonts, volumes; '
            'not arbitrary node paths or complete simulation-cache closure'}


def run(out, job):
    import bpy
    recipe = validate(job['recipe'])
    parent = Path(job['parent_native']).resolve(strict=True)
    root = Path(job['repository_root']).resolve(strict=True)
    if parent == (out / 'scene.blend').resolve() or not parent.is_relative_to(root):
        raise ValueError('NIHANG_PARENT_BOUNDARY')
    bpy.ops.wm.open_mainfile(filepath=str(parent), load_ui=False, use_scripts=False)
    state = selected_state(bpy, recipe['frame'])
    diagnostics = script_diagnostics(bpy)
    (out / 'script-diagnostics.json').write_text(json.dumps(diagnostics, indent=2) + '\n')
    if diagnostics['blocked_drivers']:
        raise ValueError('NIHANG_UNSAFE_OR_INVALID_DRIVER')
    deps = dependencies(bpy, root)
    (out / 'snapshot.json').write_text(json.dumps(state, sort_keys=True, indent=2) + '\n')
    (out / 'dependencies.json').write_text(json.dumps(deps, sort_keys=True, indent=2) + '\n')
    artifacts = ['snapshot.json', 'dependencies.json']
    if recipe['operation']=='nihang_cast_inspect':
        (out/'cast.json').write_text(json.dumps(cast_inventory(bpy),indent=2)+'\n')
        artifacts.append('cast.json')
    elif recipe['operation'] == 'nihang_rig_inspect':
        (out / 'rig.json').write_text(json.dumps(rig_inventory(bpy), indent=2) + '\n')
        artifacts.append('rig.json')
    elif recipe['operation'] == 'nihang_save':
        bpy.context.preferences.filepaths.save_version = 0
        # Remap relative external paths so relocation does not change their target.
        bpy.ops.wm.save_as_mainfile(filepath=str(out / 'scene.blend'), check_existing=False,
                                  compress=True, relative_remap=True)
        artifacts.append('scene.blend')
    else:
        scene = bpy.context.scene
        scene.render.engine = 'CYCLES'
        scene.cycles.device = 'CPU'
        scene.cycles.samples = recipe['samples']
        scene.cycles.seed = 333
        # Reuse static render data within this serial chunk. This is not a new
        # render style; repeated327 image controls must still match exactly.
        scene.render.use_persistent_data = True
        scene.render.resolution_x = recipe['width']
        scene.render.resolution_y = recipe['height']
        scene.render.resolution_percentage = 100
        scene.render.image_settings.file_format = 'PNG'
        frames=recipe.get('frames',[recipe['frame']]);manifest=[]
        for frame in frames:
            scene.frame_set(frame);bpy.context.view_layer.update()
            view=recipe.get('view','production');original_camera=scene.camera
            temp=diagnostic_camera(bpy,view) if view!='production' else None
            if temp:scene.camera=temp
            bpy.context.view_layer.update()
            filename='frame.png' if frame==recipe['frame'] else f'frame-{frame:04d}.png'
            scene.render.filepath = str(out / filename)
            camera_matrix=[[float(v) for v in row] for row in scene.camera.matrix_world]
            try:bpy.ops.render.render(write_still=True)
            finally:
                scene.camera=original_camera
                if temp:
                    data=temp.data;bpy.data.objects.remove(temp,do_unlink=True);bpy.data.cameras.remove(data)
                if view.startswith('leader_face'):
                    for ob in list(bpy.data.objects):
                        if ob.name.startswith('353 face diagnostic fill'):
                            data=ob.data;bpy.data.objects.remove(ob,do_unlink=True);bpy.data.lights.remove(data)
            manifest.append({'frame':frame,'file':filename,'sha256':digest_file(out/filename),
                             'view':view,'camera_matrix':camera_matrix})
            if view in ANATOMY_VIEWS:
                manifest[-1]['anatomy']=anatomy_inventory(bpy)
                for ob in list(bpy.data.objects):
                    if ob.name.startswith('351 anatomy '):bpy.data.objects.remove(ob,do_unlink=True)
        if recipe['operation']=='nihang_frames':
            (out/'frames.json').write_text(json.dumps(manifest,indent=2)+'\n')
            artifacts.append('frames.json')
        artifacts.append('frame.png')
    return artifacts
