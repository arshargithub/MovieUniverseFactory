"""Reviewed coordinated controls for the short wardrobe proof.

No payload expressions or external inputs. Not a certified riding performance.
"""
import math
from contextlib import contextmanager


@contextmanager
def render_geometry_paused():
    """Suspend costly render evaluation, never the rig or solver supports.

    Local data/modifiers remain unchanged; restore exact visibility even on
    error. Motion solving uses independently bound MF178 collision geometry.
    """
    import bpy
    states=[(o,o.hide_viewport) for o in bpy.context.scene.objects
            if o.type in ('MESH','CURVE','CURVES') and not o.name.startswith(('MF178_support','MF178_live_solver'))]
    try:
        for ob,_ in states:ob.hide_viewport=True
        bpy.context.view_layer.update()
        yield
    finally:
        for ob,hidden in states:ob.hide_viewport=hidden
        bpy.context.view_layer.update()


def smooth(x):
    x = max(0., min(1., x))
    return x*x*(3-2*x)


def phase(frame,neutral_entry=False):
    t = (frame-97)/24
    lean = smooth(t/2) if neutral_entry else smooth((frame-49)/96)
    riding = smooth(t/2) * (1-smooth((t-6)/2))
    return {'lean': lean, 'bob': .065*riding*math.sin(2*math.pi*1.7*t),
            'chest_yaw': .025*riding*math.sin(2*math.pi*.25*t),
            'wind': 4*smooth((t-1)/2)*(1-smooth((t-6)/2))}


def animate(rig,neutral_entry=False):
    with render_geometry_paused():
        _animate(rig,neutral_entry)


def _animate(rig,neutral_entry=False):
    import bpy
    from wardrobe_riding_fit import riding_pose
    roots = [bpy.data.objects[n] for n in ('MF_continuous_head_neck',
             'MF_aimable_eye_Left','MF_aimable_eye_Right',
             'MF_natural147_hair_temples','MF_natural147_hair_retarget')]
    # Accepted roots already carry CHILD_OF chest attachments. Keying another
    # chest delta doubled that movement and detached eyes/groom from the skin.
    for ob in roots:
        if not any(c.type=='CHILD_OF' and c.target==rig and c.subtarget=='chest'
                   for c in ob.constraints):
            raise ValueError('Expected accepted chest attachment: '+ob.name)
    rig.animation_data_clear()
    for frame in range(1,290,4):
        bpy.context.scene.frame_set(frame)
        p = phase(frame,neutral_entry)
        riding_pose(rig, p['lean'])
        rig.pose.bones['pelvis'].location.z = p['bob']
        chest = rig.pose.bones['chest']
        chest.rotation_euler.z += p['chest_yaw']
        bpy.context.view_layer.update()
        for bone in rig.pose.bones:
            location, rotation, scale = bone.matrix_basis.decompose()
            bone.rotation_mode = 'QUATERNION'
            bone.location = location;bone.rotation_quaternion = rotation;bone.scale = scale
            for prop in ('location','rotation_quaternion','scale'):
                bone.keyframe_insert(data_path=prop, frame=frame)
        if frame%24==1:print('178 coordinated rig keys',frame,flush=True)
    # Native keyframe interpolation supplies continuous poses; clothed motion
    # must still be visually reviewed and contact-qualified before handoff.
    bpy.context.scene.frame_set(1)
    bpy.context.view_layer.update()


def canonical_rig(rig, scale):
    import bpy
    from mathutils import Matrix
    proxy = rig.copy()
    proxy.data = rig.data
    proxy.name = 'MF178_metres_rig'
    bpy.context.scene.collection.objects.link(proxy)
    proxy.matrix_world = Matrix.Scale(scale, 4)@rig.matrix_world
    proxy.hide_render = True
    return proxy


def body_weight_sampler():
    import bpy
    from mathutils.kdtree import KDTree
    body = bpy.data.objects['MF_studio_adult_body']
    tree = KDTree(len(body.data.vertices))
    for vertex in body.data.vertices:tree.insert(body.matrix_world@vertex.co, vertex.index)
    tree.balance()
    names = {g.index:g.name for g in body.vertex_groups}
    rig = bpy.data.objects['MF_body156_fit_rig']
    def sample(point):
        _, index, _ = tree.find(point)
        weights = {names[g.group]:g.weight for g in body.data.vertices[index].groups
                   if names[g.group] in rig.data.bones and g.weight>.005}
        total = sum(weights.values())
        if not total:raise ValueError('Missing anatomical skinning support')
        return {n:w/total for n,w in weights.items()}
    return sample


def admitted_weights(weights, bones, allow_fingers=False):
    allowed={bone.name for bone in bones}
    result={n:w for n,w in weights.items() if n in allowed and (allow_fingers or 'finger' not in n)
            and math.isfinite(w) and w>0}
    total=sum(result.values())
    if not total:raise ValueError('No admitted named bone weights')
    return {n:w/total for n,w in result.items()}


def render_surface_target():
    """Copy evaluated-body controls, not anatomy, for fitted garment following.

    The accepted object's data stays shared read-only. No subdivision changes
    its topology during the bind; all anatomical pose correctives are retained.
    """
    import bpy
    original=bpy.data.objects['MF_studio_adult_body']
    target=original.copy();target.name='MF178_render_deform_target'
    bpy.context.scene.collection.objects.link(target)
    target.hide_render=True;target.hide_viewport=False
    for mod in target.modifiers:
        if mod.type=='SUBSURF':mod.show_viewport=False;mod.show_render=False
    bpy.context.view_layer.update()
    return target


def bind_render_surface(ob,target):
    import bpy
    for mod in list(ob.modifiers):
        if mod.name.startswith('MF178 support follows'):ob.modifiers.remove(mod)
    mod=ob.modifiers.new('MF178 fitted surface follows accepted body','SURFACE_DEFORM')
    mod.target=target;mod.falloff=4.
    bpy.context.view_layer.objects.active=ob;ob.select_set(True)
    while list(ob.modifiers).index(mod)>0:bpy.ops.object.modifier_move_up(modifier=mod.name)
    bpy.context.view_layer.update()
    bpy.ops.object.surfacedeform_bind(modifier=mod.name)
    if not mod.is_bound:raise ValueError('Fitted garment has no surface bind: '+ob.name)
    return mod


def bind(ob, rig, sample=None, scale=1., chest_only=False, allow_fingers=False):
    """Transfer actual neutral-body bone weights; never bind to fingers nearby."""
    import bpy
    import bmesh
    # Evaluated meshes can retain deform indices without their old object's
    # group-name table. Never reinterpret those indices as new bone names.
    ob.vertex_groups.clear()
    bm=bmesh.new();bm.from_mesh(ob.data)
    deform=bm.verts.layers.deform.active
    if deform:
        for vertex in bm.verts:vertex[deform].clear()
    bm.to_mesh(ob.data);bm.free()
    # RNA collection iteration yields Bone objects, not their string names.
    for vertex in ob.data.vertices:
        point = (ob.matrix_world@vertex.co)/scale
        weights = {'chest':1.} if chest_only else sample(point)
        weights=admitted_weights(weights,rig.data.bones,allow_fingers)
        for name,w in weights.items():
            group = ob.vertex_groups.get(name) or ob.vertex_groups.new(name=name)
            group.add([vertex.index], w, 'REPLACE')
    mod = ob.modifiers.new('MF178 support follows coordinated body', 'ARMATURE')
    mod.object = rig;mod.use_deform_preserve_volume=True
    bpy.context.view_layer.objects.active = ob
    while list(ob.modifiers).index(mod)>0:bpy.ops.object.modifier_move_up(modifier=mod.name)
    return mod


def wind(gain=1.):
    import bpy
    scene=bpy.context.scene
    if scene.rigidbody_world and not any(o.rigid_body or o.rigid_body_constraint for o in scene.objects):
        # Retired empty world from inherited scene is not a cloth dependency.
        bpy.ops.rigidbody.world_remove()
    # Fixed authored direction, not inferred from a still. Modest back/side
    # airflow must not turn the shawl into an exaggerated flag.
    bpy.ops.object.effector_add(type='WIND', location=(4,-3,0))
    ob = bpy.context.object;ob.name = 'MF178_controlled_wind'
    ob.rotation_euler = (math.radians(72),0,math.radians(-25))
    for frame in range(1,290,4):
        ob.field.strength = phase(frame)['wind']*gain
        ob.keyframe_insert(data_path='field.strength', frame=frame)
    return ob
