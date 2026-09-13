def offset(phase, trajectory_callable, support_start, support_end, speed,
           period=10, fps=24, blend=1):
    if min(period, fps, blend) <= 0: raise ValueError("Invalid units/range")
    span = support_end - support_start
    if span < 0: span += period
    if not (0 < span and span + 2 * blend <= period):
        raise ValueError("Invalid support or overlapping blend margins")
    a = support_start % period
    m = a + span / 2
    u = m + ((phase - m + period / 2) % period) - period / 2
    gap = max(a - u, u - a - span, 0.0)
    if gap >= blend: return (0.0, 0.0, 0.0)
    q = 1 - gap / blend; w = q * q * (3 - 2 * q)
    times = [a + span*j/63 for j in range(64)]
    samples = [tuple(trajectory_callable(t % period)[i] + speed[i]*(t-m)/fps for i in range(3)) for t in times]
    center = tuple((min(p[i] for p in samples)+max(p[i] for p in samples))*.5 for i in range(3))
    c = trajectory_callable(u % period)
    d = tuple(w * (center[i] - c[i] + speed[i] * (m - u) / fps) if i<2 else 0.0 for i in range(3))
    if sum(x * x for x in d) > 0.30 ** 2:
        raise ValueError("Correction exceeds 0.30 m; refusing, not clamping")
    return d

def control_delta(rig, pb, delta, apply=False):
    from mathutils import Vector
    M = pb.matrix.copy()
    A = rig.convert_space(pose_bone=pb, matrix=M, from_space='POSE', to_space='LOCAL')
    M.translation += rig.matrix_world.inverted().to_3x3() @ Vector(delta)
    B = rig.convert_space(pose_bone=pb, matrix=M, from_space='POSE', to_space='LOCAL')
    d = B.translation - A.translation
    if apply: pb.location += d
    return tuple(d)

def probe(rig, pb, sole_world, eps=1e-3, tol=1e-5):
    import bpy
    from mathutils import Vector
    saved = pb.location.copy()
    base = Vector(sole_world()); errors = []
    try:
        for axis, sign in ((i, s) for i in range(3) for s in (-1, 1)):
            pb.location = saved; bpy.context.view_layer.update()
            d = Vector((0, 0, 0)); d[axis] = sign * eps
            control_delta(rig, pb, d, apply=True)
            bpy.context.view_layer.update()
            errors.append((Vector(sole_world()) - base - d).length)
    finally:
        pb.location = saved; bpy.context.view_layer.update()
    if max(errors) > tol: raise RuntimeError(f"Sole probe failed: {errors} m")
    return max(errors)

def bake_overlay(rig, records):
    import bpy
    records = list(records)
    ad = rig.animation_data_create()
    if ad.action is not None or ad.use_tweak_mode:
        raise RuntimeError("Requires source in NLA, no active Action/tweak mode")
    names = sorted({n for _, n, _ in records})
    if len(names) != 4: raise ValueError("Exactly four controls required")
    action = bpy.data.actions.new("HoofContactOverlay")
    slot = action.slots.new(id_type='OBJECT', name=rig.name)
    layer = action.layers.new("Contact")
    bag = layer.strips.new(type='KEYFRAME').channelbag(slot, ensure=True)
    for name in names:
        path = rig.pose.bones[name].path_from_id("location")
        rows = sorted((f, d) for f, n, d in records if n == name)
        for axis in range(3):
            fc = bag.fcurves.new(path, index=axis)
            for f, d in rows:
                k = fc.keyframe_points.insert(f, d[axis])
                k.interpolation = 'BEZIER'
                k.handle_left_type = k.handle_right_type = 'AUTO_CLAMPED'
    track = ad.nla_tracks.new(); track.name = action.name
    start = min(f for f, _, _ in records)
    st = track.strips.new(action.name, int(start), action)
    st.action_slot = slot; st.frame_start = start
    st.blend_type = 'ADD'; st.extrapolation = 'NOTHING'
    return action
