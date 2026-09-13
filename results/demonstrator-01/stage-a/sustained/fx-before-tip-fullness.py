"""Deterministic authored tail and contact-driven dust for Blender 5.2.

Public API
----------
tail(scene, horse, helper, mf, frequency, frames=144)
dust(scene, events, helper, frames=144)

The module creates no hair, cloth, particle, smoke, or fluid simulation caches.
All animation is deterministic and directly keyframed.
"""

import math
import random
import bpy
from mathutils import Vector


FPS = 24.0
TAIL_SEED = 31415
DUST_SEED = 2718
TAIL_ROOT_BONE = "DEF-tail.001"


def _unique_collection(scene, base_name):
    collection = bpy.data.collections.new(base_name)
    scene.collection.children.link(collection)
    return collection


def _move_to_collection(obj, collection):
    for owner in tuple(obj.users_collection):
        owner.objects.unlink(obj)
    collection.objects.link(obj)


_pending = {}

def _linear_animation(id_block):
    rows = _pending.pop(id_block.name, None)
    if rows:
        action = bpy.data.actions.new(id_block.name+' deterministic FX')
        slot = action.slots.new(id_type='OBJECT',name=id_block.name)
        bag = action.layers.new('FX').strips.new(type='KEYFRAME').channelbag(slot,ensure=True)
        id_block.animation_data_create();id_block.animation_data.action=action;id_block.animation_data.action_slot=slot
        for prop,values in rows.items():
            for axis in range(len(values[0][1])):
                fc=bag.fcurves.new(prop,index=axis);fc.keyframe_points.add(len(values));fc.keyframe_points.foreach_set('co',[x for f,v in values for x in (f,v[axis])])
                for k in fc.keyframe_points:k.interpolation='LINEAR'
    else:
        animation=getattr(id_block,'animation_data',None);action=animation.action if animation else None
        if action:
            for curve in (fc for layer in action.layers for strip in layer.strips for bag in strip.channelbags for fc in bag.fcurves):
                for point in curve.keyframe_points:point.interpolation='LINEAR'

def _set_key(obj, data_path, frame):
    _pending.setdefault(obj.name,{}).setdefault(data_path,[]).append((frame,tuple(getattr(obj,data_path))))


def _frame_start(scene):
    return int(scene.frame_start)


def _duration(frames):
    return max(0, int(frames) - 1) / FPS


def _premotion_frames(mf):
    """Read optional pre-roll without imposing a required motion-helper API."""
    for name in (
        "PREMOTION_FRAMES",
        "PRE_ROLL_FRAMES",
        "premotion_frames",
        "pre_roll_frames",
    ):
        if hasattr(mf, name):
            try:
                return max(0, int(getattr(mf, name)))
            except (TypeError, ValueError):
                pass

    for name in (
        "PREMOTION_SECONDS",
        "PRE_ROLL_SECONDS",
        "premotion_seconds",
        "pre_roll_seconds",
    ):
        if hasattr(mf, name):
            try:
                return max(0, int(round(float(getattr(mf, name)) * FPS)))
            except (TypeError, ValueError):
                pass

    return 0


def _frequency_value(frequency):
    try:
        return max(0.01, float(frequency))
    except (TypeError, ValueError):
        for name in ("FREQUENCY", "frequency"):
            if hasattr(frequency, name):
                return max(0.01, float(getattr(frequency, name)))
    raise TypeError("frequency must be numeric or expose FREQUENCY/frequency")


def _disable_legacy_tail_particles(horse):
    disabled = []
    for modifier in getattr(horse, "modifiers", ()):
        if modifier.type != 'PARTICLE_SYSTEM':
            continue
        system = getattr(modifier, "particle_system", None)
        name = system.name.lower() if system else modifier.name.lower()
        if "tail" in name:
            modifier.show_viewport = False
            modifier.show_render = False
            disabled.append(modifier.name)
    return disabled


def tail(scene, horse, helper, mf, frequency, frames=144):
    """Create and animate a full, bushy, coherent curve groom.

    The fixed shot is assumed to travel toward world -Y, so the authored groom
    trails toward world +Y. The root follows DEF-tail.001 in world space while
    flow increases smoothly from root to tip. No dynamics or caches are used.
    """
    frames = max(1, int(frames))
    frequency = _frequency_value(frequency)
    start = _frame_start(scene)
    old_frame = int(scene.frame_current)
    pre_roll = _premotion_frames(mf)
    rng = random.Random(TAIL_SEED)

    bone = horse.pose.bones.get(TAIL_ROOT_BONE) if horse.pose else None
    if bone is None:
        raise KeyError("Horse rig has no pose bone %r" % TAIL_ROOT_BONE)

    collection = _unique_collection(scene, "FX Tail Groom")
    disabled_particles = _disable_legacy_tail_particles(bpy.data.objects["horse"])

    curve = bpy.data.curves.new("Full Bushy Flowing Horse Tail", 'CURVE')
    curve.dimensions = '3D'
    curve.resolution_u = 3
    curve.render_resolution_u = 3
    curve.bevel_depth = 0.00165
    curve.bevel_resolution = 1
    curve.resolution_u = 3

    groom = bpy.data.objects.new("Full Bushy Flowing Horse Tail", curve)
    collection.objects.link(groom)
    groom["fx_role"] = "horse_tail_groom"
    groom["deterministic_seed"] = TAIL_SEED
    groom["uses_simulation_cache"] = False

    material = helper._material(
        "tail dark chestnut",
        (0.055, 0.014, 0.005),
        0.72,
    )
    curve.materials.append(material)

    anchor = bpy.data.objects.new("Tail Root World Anchor", None)
    collection.objects.link(anchor)
    anchor.empty_display_type = 'PLAIN_AXES'
    anchor.empty_display_size = 0.06
    anchor["fx_role"] = "tail_root_anchor"
    anchor["source_bone"] = TAIL_ROOT_BONE
    groom.parent = anchor

    # Forty-eight coherent clumps, each containing eleven related strands.
    # Shared clump parameters prevent a spray of independent needle hairs.
    clump_count = 64
    strands_per_clump = 14
    control_points = 9
    point_basis = []
    point_u = []
    point_phase = []

    for clump_index in range(clump_count):
        clump_angle = rng.random() * math.tau
        clump_radius = math.sqrt(rng.random())
        clump_length = rng.uniform(0.92, 1.08)
        clump_phase = rng.uniform(-0.20, 0.20)
        clump_curl = rng.uniform(-1.0, 1.0)
        clump_side = rng.uniform(-0.012, 0.012)

        for strand_index in range(strands_per_clump):
            strand_angle = clump_angle + rng.gauss(0.0, 0.10)
            radial = min(1.0, max(0.0, clump_radius + rng.gauss(0.0, 0.055)))
            length = clump_length * rng.uniform(0.94, 1.055)
            phase = clump_phase + rng.uniform(-0.045, 0.045)
            fine_curl = clump_curl + rng.uniform(-0.18, 0.18)

            spline = curve.splines.new('NURBS')
            spline.points.add(control_points - 1)
            spline.order_u = 4
            spline.use_endpoint_u = True
            spline.resolution_u = 3

            for point_index, point in enumerate(spline.points):
                u = point_index / (control_points - 1)
                smooth_u = u * u * (3.0 - 2.0 * u)

                # Broad at the dock, increasingly full through the lower tail,
                # with coherent clump convergence rather than random frizz.
                spread = 0.026 + 0.145 * math.sin(math.pi * u) ** 0.72
                strand_offset = 0.0065 * (0.35 + 0.65 * u)
                curl = math.sin(u * math.pi * 1.55 + fine_curl) * 0.012 * u

                x = (
                    math.cos(strand_angle) * radial * spread
                    + math.cos(strand_angle + math.pi * 0.5) * strand_offset
                    + clump_side * smooth_u
                    + curl
                )
                y = length * (0.93 * u + 0.055 * u * u)
                z = (
                    -length * (0.10 * u + 0.35 * u * u)
                    + math.sin(strand_angle) * radial * spread * 0.72
                    - 0.018 * math.sin(math.pi * u)
                )

                point.co = (x, y, z, 1.0)
                point.radius = 0.035 + 0.965 * (1.0 - u) ** 0.74

                point_basis.append(Vector((x, y, z)))
                point_u.append(u)
                point_phase.append(phase)

    basis = groom.shape_key_add(name="Basis")
    flow_sine = groom.shape_key_add(name="Root to Tip Flow Sine")
    flow_cosine = groom.shape_key_add(name="Root to Tip Flow Cosine")
    flow_sine.slider_min = -1.0
    flow_sine.slider_max = 1.0
    flow_cosine.slider_min = -1.0
    flow_cosine.slider_max = 1.0

    for index, (position, u, phase) in enumerate(
        zip(point_basis, point_u, point_phase)
    ):
        # Amplitude is nearly zero at the root, bounded at the tip, and uses a
        # progressive phase delay so motion visibly travels root-to-tip.
        amplitude = 0.135 * u ** 1.65
        lag = 2.35 * u + phase
        vertical_lag = lag + 0.78

        sine_delta = Vector((
            amplitude * math.cos(lag),
            0.020 * u * u * math.cos(lag),
            0.090 * u ** 1.7 * math.cos(vertical_lag),
        ))
        cosine_delta = Vector((
            amplitude * math.sin(lag),
            0.020 * u * u * math.sin(lag),
            0.090 * u ** 1.7 * math.sin(vertical_lag),
        ))

        flow_sine.data[index].co = position + sine_delta
        flow_cosine.data[index].co = position + cosine_delta

    # Allow a supplied pre-roll to update stateful motion helpers before frame 0.
    for sample in range(-pre_roll, 0):
        helper._refresh(scene, mf, sample)

    for sample in range(frames):
        output_frame = start + sample
        helper._refresh(scene, mf, sample)

        root_world = horse.matrix_world @ horse.pose.bones[TAIL_ROOT_BONE].head
        anchor.location = root_world
        _set_key(anchor, "location", output_frame)

        theta = math.tau * frequency * (sample / FPS)
        flow_sine.value = math.sin(theta)
        flow_cosine.value = math.cos(theta)
        flow_sine.keyframe_insert("value", frame=output_frame)
        flow_cosine.keyframe_insert("value", frame=output_frame)

    _linear_animation(anchor)
    if curve.shape_keys:
        _linear_animation(curve.shape_keys)

    scene.frame_start = start
    scene.frame_end = start + frames - 1
    scene.frame_set(min(max(old_frame, scene.frame_start), scene.frame_end))

    return {
        "object": groom.name,
        "anchor": anchor.name,
        "collection": collection.name,
        "strands": clump_count * strands_per_clump,
        "clumps": clump_count,
        "control_points_per_strand": control_points,
        "root_bone": TAIL_ROOT_BONE,
        "frequency": frequency,
        "frames": frames,
        "fps": FPS,
        "premotion_frames": pre_roll,
        "seed": TAIL_SEED,
        "disabled_particle_modifiers": disabled_particles,
        "policy": (
            "Smooth tapered coherent NURBS clumps with bounded root-to-tip "
            "phase lag; deterministic shape-key animation; no hair dynamics "
            "or simulation cache. World +Y trailing is intentional for the "
            "fixed world -Y horse motion."
        ),
    }


def _dust_volume_material():
    material = bpy.data.materials.new("Soft Warm Contact Dust Volume")
    material.use_nodes = True
    material.diffuse_color = (0.28, 0.12, 0.045, 1.0)

    nodes = material.node_tree.nodes
    links = material.node_tree.links
    nodes.clear()

    output = nodes.new('ShaderNodeOutputMaterial')
    volume = nodes.new('ShaderNodeVolumePrincipled')
    volume.inputs["Color"].default_value = (0.62, 0.43, 0.22, 1.0)
    volume.inputs["Anisotropy"].default_value = 0.18

    texcoord = nodes.new('ShaderNodeTexCoord')
    object_info = nodes.new('ShaderNodeObjectInfo')

    noise_large = nodes.new('ShaderNodeTexNoise')
    noise_large.noise_dimensions = '4D'
    noise_large.inputs["Scale"].default_value = 2.6
    noise_large.inputs["Detail"].default_value = 2.2
    noise_large.inputs["Roughness"].default_value = 0.62

    noise_fine = nodes.new('ShaderNodeTexNoise')
    noise_fine.noise_dimensions = '4D'
    noise_fine.inputs["Scale"].default_value = 7.5
    noise_fine.inputs["Detail"].default_value = 1.3
    noise_fine.inputs["Roughness"].default_value = 0.55

    distance = nodes.new('ShaderNodeVectorMath')
    distance.operation = 'DISTANCE'
    distance.inputs[1].default_value = (0.5, 0.5, 0.5)

    radial = nodes.new('ShaderNodeMath')
    radial.operation = 'MULTIPLY_ADD'
    radial.inputs[1].default_value = -2.15
    radial.inputs[2].default_value = 1.03
    radial.use_clamp = True

    radial_power = nodes.new('ShaderNodeMath')
    radial_power.operation = 'POWER'
    radial_power.inputs[1].default_value = 1.75

    noise_mix = nodes.new('ShaderNodeMath')
    noise_mix.operation = 'MULTIPLY'

    erosion = nodes.new('ShaderNodeMath')
    erosion.operation = 'MULTIPLY_ADD'
    erosion.inputs[1].default_value = 2.15
    erosion.inputs[2].default_value = -0.15
    erosion.use_clamp = True

    shape_density = nodes.new('ShaderNodeMath')
    shape_density.operation = 'MULTIPLY'

    alpha_density = nodes.new('ShaderNodeMath')
    alpha_density.operation = 'MULTIPLY'

    density_gain = nodes.new('ShaderNodeMath')
    density_gain.operation = 'MULTIPLY'
    density_gain.inputs[1].default_value = 18.0

    links.new(texcoord.outputs["Generated"], noise_large.inputs["Vector"])
    links.new(texcoord.outputs["Generated"], noise_fine.inputs["Vector"])
    links.new(object_info.outputs["Random"], noise_large.inputs["W"])
    links.new(object_info.outputs["Random"], noise_fine.inputs["W"])
    links.new(noise_large.outputs["Fac"], noise_mix.inputs[0])
    links.new(noise_fine.outputs["Fac"], noise_mix.inputs[1])
    links.new(noise_mix.outputs[0], erosion.inputs[0])

    links.new(texcoord.outputs["Generated"], distance.inputs[0])
    links.new(distance.outputs["Value"], radial.inputs[0])
    links.new(radial.outputs[0], radial_power.inputs[0])
    links.new(radial_power.outputs[0], shape_density.inputs[0])
    links.new(erosion.outputs[0], shape_density.inputs[1])
    links.new(shape_density.outputs[0], alpha_density.inputs[0])
    links.new(object_info.outputs["Alpha"], alpha_density.inputs[1])
    links.new(alpha_density.outputs[0], density_gain.inputs[0])
    links.new(density_gain.outputs[0], volume.inputs["Density"])
    # Small density-shaped warm fill approximates ambient illumination in Eevee.
    emission=nodes.new('ShaderNodeMath');emission.operation='MULTIPLY';emission.inputs[1].default_value=.32
    links.new(density_gain.outputs[0],emission.inputs[0]);links.new(emission.outputs[0],volume.inputs['Emission Strength'])
    volume.inputs['Emission Color'].default_value=(.65,.46,.25,1)
    links.new(volume.outputs["Volume"], output.inputs["Volume"])

    return material


def _shared_icosphere_mesh(name, subdivisions):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=subdivisions, radius=1.0)
    temporary = bpy.context.object
    mesh = temporary.data
    mesh.name = name
    for polygon in mesh.polygons:
        polygon.use_smooth = True
    bpy.data.objects.remove(temporary, do_unlink=True)
    return mesh


def dust(scene, events, helper, frames=144):
    """Create layered contact dust and ballistic grit from supplied events.

    Each event must provide:
        {"time": seconds, "anchor": [world_x, world_y, 0], "leg": value}

    Negative event times are retained when their cloud or grit remains visible
    at frame zero, providing deterministic pre-motion dust without simulation.
    """
    frames = max(1, int(frames))
    start = _frame_start(scene)
    duration = _duration(frames)
    rng = random.Random(DUST_SEED)

    collection = _unique_collection(scene, "FX Contact Dust")
    collection["fx_role"] = "dust_free_view_collection"
    collection["hide_collection_for_dust_free_view"] = True

    volume_material = _dust_volume_material()
    earth_material = helper._material(
        "scattered dry soil",
        (0.14, 0.060, 0.022),
        0.96,
    )

    puff_mesh = _shared_icosphere_mesh("Soft Dust Billow Boundary", 2)
    grit_mesh = _shared_icosphere_mesh("Ballistic Grit Mesh", 1)
    puff_mesh.materials.append(volume_material)
    grit_mesh.materials.append(earth_material)

    objects = []
    accepted_events = []
    puff_count = 0
    grit_count = 0

    for event_index, source_event in enumerate(events):
        if "time" not in source_event or "anchor" not in source_event:
            raise ValueError("Dust event requires time and anchor: %r" % source_event)

        event_time = float(source_event["time"])
        anchor = Vector(source_event["anchor"])
        if len(anchor) != 3:
            raise ValueError("Dust anchor must be a world-space XYZ coordinate")
        anchor.z = max(0.0, anchor.z)

        lifetime = 2.85 + rng.uniform(-0.08, 0.16)
        if event_time > duration or event_time + lifetime < 0.0:
            continue

        leg = source_event.get("leg", "unknown")
        accepted_events.append({
            "time": event_time,
            "anchor": [anchor.x, anchor.y, anchor.z],
            "leg": leg,
        })

        # Three overlapping, differently timed ellipsoids form a layered cloud.
        # Their radial shader density reaches zero before the mesh boundary,
        # avoiding visible sphere/cube silhouettes and hard bubble edges.
        for layer in range(3):
            delay = (0.000, 0.045, 0.095)[layer]
            layer_time = event_time + delay
            layer_lifetime = lifetime * (1.0 - 0.09 * layer)
            lateral = rng.uniform(-0.065, 0.065)
            inherited_y = rng.uniform(-1.35, -0.60)
            drag = rng.uniform(3.0, 4.4)
            rise = rng.uniform(0.55, 0.80)

            obj = bpy.data.objects.new(
                "Dust Billow %03d L%d" % (event_index, layer),
                puff_mesh,
            )
            collection.objects.link(obj)
            obj.rotation_euler = (
                rng.uniform(-0.18, 0.18),
                rng.uniform(-0.18, 0.18),
                rng.uniform(-0.3, 0.3),
            )
            obj["fx_role"] = "dust_volume"
            obj["event_index"] = event_index
            obj["leg"] = str(leg)
            obj["uses_simulation_cache"] = False
            objects.append(obj)
            puff_count += 1

            for sample in range(frames):
                frame = start + sample
                time = sample / FPS
                age = time - layer_time

                if 0.0 <= age <= layer_lifetime:
                    normalized = age / layer_lifetime
                    drag_displacement = inherited_y * (
                        1.0 - math.exp(-drag * age)
                    ) / drag

                    obj.location = anchor + Vector((
                        lateral * (1.0 - math.exp(-2.2 * age)),
                        drag_displacement + 0.055 * age,
                        0.10 + .65 * math.sqrt(age) + rise * age * .3,
                    ))

                    obj.scale = (
                        0.15 + (1.0 + 0.15 * layer) * math.sqrt(age),
                        0.20 + (2.2 + 0.20 * layer) * math.sqrt(age),
                        0.10 + (.95 + 0.10 * layer) * math.sqrt(age),
                    )

                    attack = min(1.0, age / 0.075)
                    fade = max(0.0, 1.0 - normalized)
                    alpha = attack * fade ** 1.10 * (0.88 - 0.10 * layer)
                    if layer == 0:
                        # Denser, low contact kick beneath the diffuse suspended trail.
                        obj.location.z = .04 + .30 * math.sqrt(age)
                        obj.scale = (.10+.5*math.sqrt(age), .12+.85*math.sqrt(age), .07+.40*math.sqrt(age))
                        alpha *= 2.8
                    obj.color = (1.0, 0.80, 0.58, alpha)
                else:
                    obj.location = anchor
                    obj.scale = (0.001, 0.001, 0.001)
                    obj.color = (1.0, 0.80, 0.58, 0.0)

                _set_key(obj, "location", frame)
                _set_key(obj, "scale", frame)
                _set_key(obj, "color", frame)

            _linear_animation(obj)

        # Small ballistic fragments provide sharp contact detail. Their world-Y
        # velocity is negative, matching the supplied fixed horse travel.
        for particle_index in range(5):
            chip = bpy.data.objects.new(
                "Dust Grit %03d %02d" % (event_index, particle_index),
                grit_mesh,
            )
            collection.objects.link(chip)
            chip["fx_role"] = "ballistic_grit"
            chip["event_index"] = event_index
            chip["uses_simulation_cache"] = False
            objects.append(chip)
            grit_count += 1

            velocity = Vector((
                rng.uniform(-0.80, 0.80),
                rng.uniform(-3.50, -0.65),
                rng.uniform(0.80, 2.05),
            ))
            size = rng.uniform(0.0045, 0.0115)
            flight = min(0.62, 2.0 * velocity.z / 9.81)
            chip.rotation_euler = tuple(rng.uniform(-math.pi, math.pi) for _ in range(3))

            for sample in range(frames):
                frame = start + sample
                age = sample / FPS - event_time

                if 0.0 <= age <= flight:
                    chip.location = anchor + velocity * age + Vector((
                        0.0,
                        0.0,
                        0.010 - 4.905 * age * age,
                    ))
                    chip.scale = (size, size * 0.68, size * 0.45)
                    chip.rotation_euler.rotate_axis('Z', 0.31)
                else:
                    chip.location = anchor
                    chip.scale = (0.0, 0.0, 0.0)

                _set_key(chip, "location", frame)
                _set_key(chip, "scale", frame)
                _set_key(chip, "rotation_euler", frame)

            _linear_animation(chip)

    scene.frame_end = start + frames - 1

    metadata = {
        "collection": collection.name,
        "dust_free_view": {
            "collection": collection.name,
            "instruction": (
                "Disable this collection in the active view layer, or set its "
                "hide_viewport/hide_render flags, for a dust-free view."
            ),
            "object_names": [obj.name for obj in objects],
        },
        "events": accepted_events,
        "objects": len(objects),
        "volume_billows": puff_count,
        "ballistic_grit": grit_count,
        "frames": frames,
        "fps": FPS,
        "duration_seconds": duration,
        "seed": DUST_SEED,
        "velocity_policy": "Initial world-Y velocity is negative and rapidly drag-limited.",
        "policy": (
            "Ground-referenced contact anchors, three soft eroded ellipsoidal "
            "billows per event, and analytic ballistic grit. Negative-time "
            "events provide pre-motion dust. No fluid, particle, rigid-body, "
            "hair, or dynamics cache is created."
        ),
    }

    return objects, metadata
