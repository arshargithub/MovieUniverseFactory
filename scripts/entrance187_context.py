"""Reviewed native look construction for the entrance187 fixed operation."""
import math
import random

TRAVEL_NATIVE_PER_SECOND = 99.60000205  # Recorded185 source path: 593.45001221 / (143/24).


def road_center(y):
    return 5 * math.sin(y / 180)


def height(x, y, floor):
    edge = max(0., abs(x - road_center(y)) - 24.)
    rise = 1 - math.exp(-edge / 100.)
    return floor + rise * (18 + 22 * math.sin(y / 95. + x / 170.) ** 2) + rise * 3 * math.sin(x / 14.) * math.cos(y / 17.)


def material(name, dark, light, scale=.2, bump=.1):
    import bpy
    m = bpy.data.materials.new('MF187_' + name)
    m.use_nodes = True
    nodes, links = m.node_tree.nodes, m.node_tree.links
    bsdf = nodes.get('Principled BSDF')
    bsdf.inputs['Roughness'].default_value = .88
    coord = nodes.new('ShaderNodeTexCoord')
    noise = nodes.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value = scale
    noise.inputs['Detail'].default_value = 2
    ramp = nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].color = (*dark, 1)
    ramp.color_ramp.elements[1].color = (*light, 1)
    relief = nodes.new('ShaderNodeBump')
    relief.inputs['Strength'].default_value = .25
    relief.inputs['Distance'].default_value = bump
    links.new(coord.outputs['Object'], noise.inputs['Vector'])
    links.new(noise.outputs['Fac'], ramp.inputs['Fac'])
    links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])
    links.new(noise.outputs['Fac'], relief.inputs['Height'])
    links.new(relief.outputs['Normal'], bsdf.inputs['Normal'])
    return m


def own(ob, col, root):
    for old in list(ob.users_collection):
        old.objects.unlink(ob)
    col.objects.link(ob)
    ob.parent = root
    return ob


def construct(scene, floor):
    import bpy
    from mathutils import Vector
    col = bpy.data.collections.new('MF187_ENTRANCE_CONTEXT')
    scene.collection.children.link(col)
    root = bpy.data.objects.new('MF187_world_travel', None)
    col.objects.link(root)
    earth = material('ochre-earth', (.22, .115, .045), (.55, .36, .15), .12, .16)
    road = material('worn-road', (.36, .24, .12), (.64, .46, .24), .34, .065)
    slate = material('slate-rock', (.13, .16, .19), (.35, .34, .31), .4, .08)
    scrub = material('scrub', (.045, .065, .042), (.12, .15, .067), 1., .015)

    nx, ny = 72, 160
    points = []
    for j in range(ny + 1):
        y = -900 + 1800 * j / ny
        for i in range(nx + 1):
            x = -400 + 800 * i / nx
            points.append((x, y, height(x, y, floor)))
    faces = [(j * (nx + 1) + i, j * (nx + 1) + i + 1,
              (j + 1) * (nx + 1) + i + 1, (j + 1) * (nx + 1) + i)
             for j in range(ny) for i in range(nx)]
    mesh = bpy.data.meshes.new('MF187_terrain')
    mesh.from_pydata(points, [], faces)
    ob = bpy.data.objects.new('MF187_terrain', mesh)
    col.objects.link(ob)
    ob.parent = root
    mesh.materials.append(earth)
    for poly in mesh.polygons:
        poly.use_smooth = True

    # A broad actual surface, not a floating stripe. Ruts are shallow and avoid
    # altering actor foot support: diagnostic ground/contact proof is separate.
    p, f = [], []
    for j in range(321):
        y = -900 + j * 1800 / 320
        c = road_center(y)
        p.extend(((c - 23., y, floor + .006), (c + 23., y, floor + .006)))
        if j:
            f.append((2*j-2, 2*j, 2*j+1, 2*j-1))
    mesh = bpy.data.meshes.new('MF187_road')
    mesh.from_pydata(p, [], f)
    ob = bpy.data.objects.new('MF187_road', mesh)
    col.objects.link(ob)
    ob.parent = root
    mesh.materials.append(road)

    # Shared low-poly rock data is instanced with deterministic, unequal scale.
    rng = random.Random(187)
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=1)
    seed = own(bpy.context.object, col, root)
    seed.name = 'MF187_rock_000'
    seed.data.materials.append(slate)
    for n in range(260):
        rock = seed if n == 0 else bpy.data.objects.new('MF187_rock_%03d' % n, seed.data)
        if n:
            col.objects.link(rock)
            rock.parent = root
        y = rng.uniform(-550, 550)
        x = (1 if n % 2 else -1) * rng.uniform(29, 240) + road_center(y)
        radius = rng.uniform(1.3, 5.5)
        rock.location = (x, y, height(x, y, floor) + radius * .32)
        rock.scale = (radius * rng.uniform(.7, 1.4), radius, radius * rng.uniform(.45, .9))
        rock.rotation_euler = (rng.uniform(-.4, .4), rng.uniform(-.4, .4), rng.random() * math.tau)

    # Coarse clustered mountain scrub; no purchased tree or historical claim.
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=1)
    seed = own(bpy.context.object, col, root)
    seed.name = 'MF187_scrub_000'
    seed.data.materials.append(scrub)
    for n in range(350):
        bush = seed if n == 0 else bpy.data.objects.new('MF187_scrub_%03d' % n, seed.data)
        if n:
            col.objects.link(bush)
            bush.parent = root
        y = rng.uniform(-750, 750)
        x = (1 if n % 2 else -1) * rng.uniform(31, 330) + road_center(y)
        size = rng.uniform(.8, 2.8)
        bush.location = (x, y, height(x, y, floor) + size * .6)
        bush.scale = (size * 1.4, size, size * .9)

    root.location = (0, 0, 0)
    root.keyframe_insert(data_path='location', frame=217)
    root.location = (0, TRAVEL_NATIVE_PER_SECOND * 143 / 24, 0)
    root.keyframe_insert(data_path='location', frame=360)
    for layer in root.animation_data.action.layers:
        for strip in layer.strips:
            for bag in strip.channelbags:
                for fc in bag.fcurves:
                    for key in fc.keyframe_points:
                        key.interpolation = 'LINEAR'

    scene.world = scene.world.copy()
    bg = scene.world.node_tree.nodes.get('Background')
    bg.inputs['Color'].default_value = (.36, .45, .57, 1)
    bg.inputs['Strength'].default_value = .55
    sun_data = bpy.data.lights.new('MF187_warm-daylight', 'SUN')
    sun_data.energy = 1.5
    sun_data.angle = math.radians(18)
    sun_data.color = (1., .84, .65)
    sun = bpy.data.objects.new(sun_data.name, sun_data)
    scene.collection.objects.link(sun)
    sun.location = (-50, -80, 100)
    sun.rotation_euler = (Vector((0, 0, -10)) - sun.location).to_track_quat('-Z', 'Y').to_euler()
    return {'ground_z': floor, 'travel_native_per_second': TRAVEL_NATIVE_PER_SECOND, 'road_half_width': 23.,
            'terrain_vertices': len(points), 'rocks': 260, 'scrub': 350,
            'scope': 'Reversible look candidate. Not final painted-world art or new gait qualification.'}


def camera(scene, rig, frame):
    from mathutils import Vector
    from demo_reuse import camera_offset
    t = (frame - 217) / 143
    profile = {'path_interpolation': 'continuous', 'offset_start': [0., 100., 210.],
               'offset_end': [-7., -17., 2.6], 'camera_path': [
                   {'at': 0., 'offset': [0., 100., 210.]},
                   {'at': .34, 'offset': [-78., 40., 38.]},
                   {'at': .64, 'offset': [-120., 0., 5.]},
                   {'at': 1., 'offset': [-7., -17., 2.6]}]}
    focus = min(1., max(0., (t - .64) / .36))
    focus = focus * focus * (3 - 2 * focus)
    head = rig.matrix_world @ rig.pose.bones['MF185_head'].head
    target = Vector((0, -.5, -9.)).lerp(head + Vector((0, 0, -.65)), focus)
    cam = scene.camera
    cam.data.type = 'PERSP'
    cam.data.lens = 42
    cam.data.sensor_fit = 'VERTICAL'
    cam.data.sensor_height = 24
    cam.data.dof.use_dof = False
    cam.location = target + Vector(camera_offset(profile, t))
    cam.rotation_euler = (target - cam.location).to_track_quat('-Z', 'Y').to_euler()
    return {'frame': frame, 'position': list(cam.location), 'target': list(target)}
