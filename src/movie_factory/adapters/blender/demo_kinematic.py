# kinematic_repair.py -- Blender 5.x, authored kinematics only.
from dataclasses import dataclass
from mathutils import Matrix, Vector

_EPS = 1.0e-8


def prepare_diagnostic(scene, tail_systems):
    """Use only in a disposable diagnostic scene; tail systems are explicit."""
    report = {"tail_dynamics_disabled": [], "collisions_disabled": 0,
              "subdivision_normalized": 0}
    for psys in tail_systems:
        settings = psys.settings
        if psys.use_hair_dynamics:
            psys.use_hair_dynamics = False  # Hair remains; baked dynamics are ignored.
        report["tail_dynamics_disabled"].append(psys.name)

    for obj in scene.objects:
        for mod in obj.modifiers:
            if mod.type == 'COLLISION':
                mod.show_viewport = mod.show_render = False
                report["collisions_disabled"] += 1
            elif mod.type == 'SUBSURF':
                # Measure the same surface in viewport and render without lowering quality.
                level = max(mod.levels, mod.render_levels)
                mod.levels = mod.render_levels = level
                mod.show_viewport = mod.show_render = True
                report["subdivision_normalized"] += 1
    return report


def torso_frame(rig, bone_name, depsgraph):
    """Current evaluated torso-bone frame in world space; never changes scene time."""
    erig = rig.evaluated_get(depsgraph)
    return erig.matrix_world @ erig.pose.bones[bone_name].matrix


def _descendants(roots):
    found, stack = set(roots), list(roots)
    while stack:
        for child in stack.pop().children:
            if child not in found:
                found.add(child)
                stack.append(child)
    return found


def _key_object(obj, frame):
    obj.keyframe_insert("location", frame=frame)
    path = "rotation_quaternion" if obj.rotation_mode == 'QUATERNION' else \
           ("rotation_axis_angle" if obj.rotation_mode == 'AXIS_ANGLE' else
            "rotation_euler")
    obj.keyframe_insert(path, frame=frame)
    obj.keyframe_insert("scale", frame=frame)


@dataclass
class TackState:
    rig: object
    torso_bone: str
    objects: tuple
    roots: tuple
    offsets: dict
    depsgraph: object

    def update_tack(self, frame, key=True):
        """Call after the caller establishes the source torso pose for this frame."""
        frame_world = torso_frame(self.rig, self.torso_bone, self.depsgraph)
        for obj in self.roots:
            obj.matrix_world = frame_world @ self.offsets[obj]
        self.depsgraph.update()
        if key:
            # Explicit object keys prevent a later bake from recreating deform outputs.
            for obj in self.objects:
                _key_object(obj, frame)
        return frame_world


def capture_tack(rig, torso_bone, tack_objects, depsgraph,
                 dependency_modifiers=(), dependency_constraints=()):
    """Capture frame-0 rigid offsets and disable only explicitly supplied dependencies."""
    objects = tuple(tack_objects)
    object_set = set(objects)
    roots = tuple(o for o in objects if o.parent not in object_set)
    preserved = {o: o.matrix_world.copy() for o in _descendants(roots)}

    for mod in dependency_modifiers:
        mod.show_viewport = mod.show_render = False
    for con in dependency_constraints:
        con.mute = True

    # Remove only external parenting of tack roots; internal hierarchy is retained.
    for obj in roots:
        if obj.parent is not None:
            world = obj.matrix_world.copy()
            obj.parent = None
            obj.matrix_world = world
    for obj, world in preserved.items():
        obj.matrix_world = world
    depsgraph.update()

    base = torso_frame(rig, torso_bone, depsgraph)
    offsets = {obj: base.inverted_safe() @ obj.matrix_world for obj in roots}
    return TackState(rig, torso_bone, objects, roots, offsets, depsgraph)


@dataclass(frozen=True)
class SeatFrame:
    tack: TackState
    local_matrix: Matrix

    def matrix_world(self):
        return torso_frame(self.tack.rig, self.tack.torso_bone,
                           self.tack.depsgraph) @ self.local_matrix


def capture_seat_frame(tack, saddle, depsgraph):
    """Sample saddle geometry once; subsequent seat frames use only the torso offset."""
    evaluated = saddle.evaluated_get(depsgraph)
    mesh = evaluated.to_mesh()
    try:
        if not mesh.vertices:
            raise ValueError("saddle has no evaluated vertices")
        points = [v.co for v in mesh.vertices]
        local_point = Vector((
            sum(p.x for p in points) / len(points),
            sum(p.y for p in points) / len(points),
            max(p.z for p in points)))
        world_point = evaluated.matrix_world @ local_point
        seat_world = evaluated.matrix_world.normalized()
        seat_world.translation = world_point
    finally:
        evaluated.to_mesh_clear()
    base = torso_frame(tack.rig, tack.torso_bone, depsgraph)
    return SeatFrame(tack, base.inverted_safe() @ seat_world)


def _orthogonal(v):
    axis = min((Vector((1, 0, 0)), Vector((0, 1, 0)), Vector((0, 0, 1))),
               key=lambda a: abs(a.dot(v)))
    return v.cross(axis).normalized()


def _bone_matrix(head, direction, plane_normal):
    """Construct a +Y bone frame directly, including a -Y antiparallel aim."""
    y = direction.normalized()
    x = plane_normal - y * plane_normal.dot(y)
    x = x.normalized() if x.length_squared > _EPS else _orthogonal(y)
    z = x.cross(y).normalized()
    matrix = Matrix((x, y, z)).transposed().to_4x4()
    matrix.translation = head
    return matrix


def _key_control(pb, frame):
    pb.keyframe_insert("location", frame=frame)
    path = "rotation_quaternion" if pb.rotation_mode == 'QUATERNION' else \
           ("rotation_axis_angle" if pb.rotation_mode == 'AXIS_ANGLE' else
            "rotation_euler")
    pb.keyframe_insert(path, frame=frame)


def aim_two_bone_fk(rig, upper_name, lower_name, root_world, goal_world,
                    outward_world, upper_length, lower_length, depsgraph,
                    frame=None):
    """Analytic, non-stretching FK solve; lengths are fixed armature-space units."""
    inv = rig.matrix_world.inverted_safe()
    root = inv @ Vector(root_world)
    goal = inv @ Vector(goal_world)
    outward = inv.to_3x3() @ Vector(outward_world)
    delta = goal - root
    requested = delta.length
    aim = delta.normalized() if requested > _EPS else Vector((0, 1, 0))

    lo = abs(upper_length - lower_length) + _EPS
    hi = upper_length + lower_length - _EPS
    used = min(max(requested, lo), hi)
    bend = outward - aim * outward.dot(aim)
    bend = bend.normalized() if bend.length_squared > _EPS else _orthogonal(aim)
    x = (upper_length ** 2 - lower_length ** 2 + used ** 2) / (2.0 * used)
    h = max(0.0, upper_length ** 2 - x ** 2) ** 0.5
    joint = root + aim * x + bend * h
    endpoint = root + aim * used
    normal = aim.cross(bend).normalized()

    upper = rig.pose.bones[upper_name]
    lower = rig.pose.bones[lower_name]
    _aim_preserving_roll(upper, joint)
    depsgraph.update()                 # Parent/control evaluation is intentionally sequential.
    _aim_preserving_roll(lower, endpoint)
    depsgraph.update()
    if frame is not None:
        _key_control(upper, frame)
        _key_control(lower, frame)

    endpoint_world = rig.matrix_world @ lower.tail
    return {"requested_distance": requested, "used_distance": used,
            "clamped": abs(used - requested) > _EPS,
            "endpoint_gap_world": (Vector(goal_world) - endpoint_world).length}


def _aim_preserving_roll(pb,target):
    head=pb.head.copy();current=pb.tail-head;desired=target-head
    if current.length < _EPS or desired.length < _EPS: raise ValueError("Degenerate bone aim")
    q=current.normalized().rotation_difference(desired.normalized())
    pb.matrix=Matrix.Translation(head) @ q.to_matrix().to_4x4() @ Matrix.Translation(-head) @ pb.matrix
