"""Fixed, reviewed costume174 operations; no executable job payload.

Retain173 source/binding unchanged. All imports and input/output locations are
repository-fixed; asset scripts disabled. Static authoring, not dynamics.
"""
import json
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src/movie_factory/adapters/blender'))
sys.path.insert(0, str(ROOT / 'scripts'))
import wardrobe_studio as studio
from wardrobe_riding_fit import digest

BASE = studio.BASE
SOURCE = BASE / 'wardrobe173-seal01/dressed-fit.blend'
SOURCE_SHA = '60c3380f765f3d278b008ddaf862e9fcfae0cb9fdd6140910a09a2813825fc01'
OPERATIONS = ('probe01', 'probe02') + tuple('preview%02d' % i for i in range(1, 25)) + ('seal01', 'verify01')
PHYSICS_INPUT = BASE/'wardrobe174-preview09/neutral-before-cleanup.npz'
PHYSICS_INPUT_SHA = '9e88da31d2af59ad670cf7b6fcd5f23f17c448bef4eb262981af7d6e1da49e25'
ORIGINAL_SCULPT = studio.sculpt_fabric
ORIGINAL_CONSTRUCT = studio.construct_scarf
ORIGINAL_LEATHER = studio.leather_paths
from wardrobe_tension import press_visible_scarf as ORIGINAL_PRESS


def hem_fold(x, y, z):
    """Sparse descending folds released from waist support, not uniform noise."""
    release = studio.smoothstep((-z - 5.42) / 1.28)
    angle = math.atan2(x, -(y - .14))
    ridges = ((-.85 + .06 * (z + 6), .14, .065),
              (.35 - .04 * (z + 6), .19, .045), (2.55, .22, .040))
    return release * sum(a * math.exp(-((angle - c) / width) ** 2) for c, width, a in ridges)


def sculpt(mats):
    import bpy
    from mathutils import Vector
    from wardrobe_refinement import tree_for
    ORIGINAL_SCULPT(mats)
    skin = tree_for(bpy.data.objects['MF_studio_adult_body'])
    measurements = {}
    for side in ('L', 'R'):
        ob = bpy.data.objects['MF_171_fitted_sleeve_' + side + '_173_visible']
        before = []; after = []
        for v in ob.data.vertices:
            p = ob.matrix_world @ v.co
            hit, normal, _, distance = skin.find_nearest(p)
            if hit is None or distance > .40: continue
            before.append(distance)
            # Keep a mobile garment silhouette, not a copy of naked muscles.
            signed = (p - hit).dot(normal)
            if signed > .055:
                p -= normal * (signed - .055) * .70
            if signed < .025: p = hit + normal * .025
            v.co = ob.matrix_world.inverted() @ p
            after.append(skin.find_nearest(p)[3])
        ob.data.update(); studio.border_seams(ob, mats['seam'])
        measurements[side] = {'mean_nearest_distance_before': sum(before) / len(before),
                              'mean_nearest_distance_after': sum(after) / len(after),
                              'sample_count': len(before), 'not_calibrated_anthropometry': True}
    tunic = bpy.data.objects['MF_fit_tunic_173_visible']
    rest = tunic.data.attributes['MF_173_material_coords'].data
    upper_before = []; upper_after = []
    for v in tunic.data.vertices:
        rp = rest[v.index].vector
        if rp.z > -5.30:
            p = tunic.matrix_world @ v.co
            hit, normal, _, distance = skin.find_nearest(p)
            if hit is not None and distance < .5:
                upper_before.append(distance)
                signed = (p - hit).dot(normal)
                blend = studio.smoothstep((rp.z + 5.30) / .35)
                if signed > .065: p -= normal * (signed - .065) * .78 * blend
                if signed < .030: p = p.lerp(hit + normal * .030, blend)
                v.co = tunic.matrix_world.inverted() @ p
                upper_after.append(skin.find_nearest(p)[3])
        if rp.z > -5.40: continue
        local = studio.torso_matrix(rp.z).inverted() @ v.co
        outward = Vector((local.x, local.y - .14, 0)).normalized()
        # Descending folds and slight unequal hem length, released from belt.
        local += outward * hem_fold(rp.x, rp.y, rp.z)
        local.z += .025 * studio.smoothstep((-rp.z - 6.2) / .5) * math.sin(2.4 * rp.x + .6)
        v.co = studio.torso_matrix(rp.z) @ local
    # Recess the redundant short-sleeve layer beneath the full fitted sleeve.
    # Cutting its faces instead produced angular armhole flaps (preview03).
    sleeves = {sign: tree_for(bpy.data.objects['MF_171_fitted_sleeve_'+side+'_173_visible'])
               for sign, side in ((1,'L'),(-1,'R'))}
    for v in tunic.data.vertices:
        rp = rest[v.index].vector
        if not (-3.15 < rp.z < -1.35): continue
        blend = studio.smoothstep((abs(rp.x)-1.35)/.32)
        if not blend: continue
        p = tunic.matrix_world @ v.co
        hit, normal, _, distance = sleeves[1 if rp.x>0 else -1].find_nearest(p)
        if hit is not None and distance < .7:
            v.co = tunic.matrix_world.inverted() @ p.lerp(hit-normal*.045,blend)
    tunic.data.update()
    for old in list(bpy.data.objects):
        if old.name.startswith('MF_fit_tunic_173_visible_seam_'):
            bpy.data.objects.remove(old, do_unlink=True)
    studio.border_seams(tunic, mats['seam'])
    measurements['upper_tunic'] = {'mean_nearest_distance_before': sum(upper_before) / len(upper_before),
                                  'mean_nearest_distance_after': sum(upper_after) / len(upper_after),
                                  'sample_count': len(upper_before), 'flare_not_reduced': True}
    bpy.context.scene['MF_174_sleeve_measurements'] = json.dumps(measurements)
    bpy.context.view_layer.update()


def settle_chest(ob):
    """One neutral construction settle with pinned shoulder ends; no motion claim."""
    import bpy
    supports = [bpy.data.objects['MF_fit_tunic_173_visible']]
    temporary = []
    for source in supports:
        data = studio.single_surface_mesh(source)
        collider = bpy.data.objects.new('MF_174_chest_settle_support', data)
        bpy.context.collection.objects.link(collider)
        collider.matrix_world = source.matrix_world.copy(); collider.hide_render = True
        collider.modifiers.new('Construction contact', 'COLLISION')
        collider.collision.thickness_outer = .016
        temporary.append(collider)
    group = ob.vertex_groups.new(name='Shoulder attachment')
    for i in range(81):
        for j in range(33):
            if (i < 3 or i > 77) and j > 19:
                group.add([i * 33 + j], 1., 'REPLACE')
    cloth = ob.modifiers.new('Neutral chest cloth settle', 'CLOTH')
    settings = cloth.settings
    settings.quality = 8; settings.mass = .13
    settings.tension_stiffness = 16; settings.compression_stiffness = 16
    settings.shear_stiffness = 8; settings.bending_stiffness = .045
    settings.vertex_group_mass = group.name; settings.pin_stiffness = 1.
    cloth.collision_settings.use_collision = True
    cloth.collision_settings.distance_min = .018
    cloth.collision_settings.use_self_collision = True
    cloth.collision_settings.self_distance_min = .012
    cloth.point_cache.frame_start = 1; cloth.point_cache.frame_end = 72
    # Cloth before final shell/subdivision; evaluate the single surface only.
    states = [(m, m.show_viewport) for m in ob.modifiers if m.type in ('SOLIDIFY', 'SUBSURF')]
    for m, _ in states: m.show_viewport = False
    scene = bpy.context.scene; scene.gravity = (0, 0, -9.81)
    for frame in range(1, 73): scene.frame_set(frame); bpy.context.view_layer.update()
    evaluated = ob.evaluated_get(bpy.context.evaluated_depsgraph_get())
    data = bpy.data.meshes.new_from_object(evaluated, preserve_all_data_layers=True,
                                          depsgraph=bpy.context.evaluated_depsgraph_get())
    ob.modifiers.remove(cloth)
    for m, state in states: m.show_viewport = state
    studio.set_surface(ob.name, data, .012)
    for collider in temporary:
        data = collider.data; bpy.data.objects.remove(collider, do_unlink=True)
        if not data.users: bpy.data.meshes.remove(data)
    scene.frame_set(1); bpy.context.view_layer.update()


def settle_connected(ob):
    """Freeze a neutral whole-sheet settle, with crown/rear-tuck holds only."""
    import bpy
    scene = bpy.context.scene
    original_frame = scene.frame_current; gravity = scene.gravity.copy()
    supports = ('MF_fit_tunic_173_visible', 'MF_171_fitted_sleeve_L_173_visible',
                'MF_171_fitted_sleeve_R_173_visible', 'MF_studio_adult_body',
                'MF_173_static_groom_clearance')
    temporary = []; states = []
    try:
        for name in supports:
            source = bpy.data.objects[name]
            if any(m.type=='SOLIDIFY' for m in source.modifiers):
                data = studio.single_surface_mesh(source)
            else:
                data = bpy.data.meshes.new_from_object(
                    source.evaluated_get(bpy.context.evaluated_depsgraph_get()),
                    depsgraph=bpy.context.evaluated_depsgraph_get())
            collider = bpy.data.objects.new('MF_174_whole_sheet_support', data)
            bpy.context.collection.objects.link(collider)
            collider.matrix_world = source.matrix_world.copy(); collider.hide_render = True
            if len(data.polygons)>15000:
                simplify = collider.modifiers.new('Construction-only support simplification', 'DECIMATE')
                simplify.ratio = .22
            collider.modifiers.new('Construction-only collision', 'COLLISION')
            collider.collision.thickness_outer = .018
            temporary.append(collider)
        group = ob.vertex_groups.new(name='Crown and rear tucks, no shoulder clips')
        columns = len(ob.data.vertices)//41
        core_start = columns-33-20
        for i in range(columns):
            for j in range(41):
                if (core_start<=i<core_start+33 and j<=23) or i<2 or i>=columns-2:
                    group.add([i*41+j],1.,'REPLACE')
        for mod in ob.modifiers:
            if mod.type in ('SOLIDIFY','SUBSURF'):
                states.append((mod,mod.show_viewport)); mod.show_viewport = False
        cloth = ob.modifiers.new('Whole neutral shawl construction settle', 'CLOTH')
        settings = cloth.settings
        settings.quality = 6; settings.mass = .14
        settings.tension_stiffness = 28; settings.compression_stiffness = 20
        settings.shear_stiffness = 12; settings.bending_stiffness = .055
        settings.vertex_group_mass = group.name; settings.pin_stiffness = 1.
        cloth.collision_settings.use_collision = True
        cloth.collision_settings.distance_min = .016
        cloth.collision_settings.use_self_collision = True
        cloth.collision_settings.self_distance_min = .014
        cloth.point_cache.frame_start = 1; cloth.point_cache.frame_end = 32
        scene.gravity = (0,0,-9.81)
        for frame in range(1,33):
            scene.frame_set(frame); bpy.context.view_layer.update()
            # Force cache evaluation at EACH frame, not only the last frame.
            evaluated = ob.evaluated_get(bpy.context.evaluated_depsgraph_get())
            data = evaluated.to_mesh(); evaluated.to_mesh_clear()
        evaluated = ob.evaluated_get(bpy.context.evaluated_depsgraph_get())
        data = bpy.data.meshes.new_from_object(evaluated, preserve_all_data_layers=True,
                                              depsgraph=bpy.context.evaluated_depsgraph_get())
        ob.modifiers.remove(cloth)
        studio.set_surface(ob.name, data, .012)
    finally:
        for mod, state in states: mod.show_viewport = state
        for collider in temporary:
            data = collider.data; bpy.data.objects.remove(collider, do_unlink=True)
            if not data.users: bpy.data.meshes.remove(data)
        scene.gravity = gravity; scene.frame_set(original_frame)
        bpy.context.view_layer.update()


def construct(mats):
    """One connected static sheet: crown, two offset shoulder wraps and tail.

    Authored dressing with contact support, NOT a physically simulated winding
    or an animated cloth solution. Never alter the protected groom underneath.
    """
    import bpy
    from mathutils import Vector
    from wardrobe_refinement import tree_for
    frame = ORIGINAL_CONSTRUCT(mats)
    for old in list(bpy.data.objects):
        if old.name.startswith(('MF_173_open_scarf_seam_', 'MF_173_diagonal_scarf_fall_seam_')):
            bpy.data.objects.remove(old, do_unlink=True)
    cache = bpy.data.objects.get('MF_174_connected_pattern')
    if cache is not None:
        rest = [v.co.copy() for v in cache.data.vertices]
    else:
        import numpy as np
        if PHYSICS_INPUT.is_symlink() or digest(PHYSICS_INPUT)!=PHYSICS_INPUT_SHA:
            raise ValueError('Frozen discovery cloth input changed')
        with np.load(PHYSICS_INPUT,allow_pickle=False) as record:
            if record.files!=['points']: raise ValueError('Unexpected frozen cloth fields')
            array = record['points']
            if array.shape!=(243*41,3) or not np.isfinite(array).all() or np.abs(array).max()>25:
                raise ValueError('Invalid bounded frozen cloth coordinates')
            rest = [Vector(p) for p in array]
        # The frozen short return still wandered down the outer shoulder and
        # emerged through the rear strap. Route that free end beneath the
        # existing rear overlap, rather than hiding a protrusion with clothes.
        for i,p in enumerate(rest):
            column,j = divmod(i,41)
            if column<=216:continue
            v = j/40
            t = max(studio.smoothstep((column-222)/20),
                    studio.smoothstep((column-216)/8)*studio.smoothstep((v-.35)/.45))
            target = Vector((.45+.30*v,1.55+.05*v,-1.70-.15*v))
            rest[i] = p.lerp(target,t)
        rest = fair_shoulder_turns(rest, sheet_faces(len(rest)//41))
        data = bpy.data.meshes.new('MF_174_connected_pattern')
        faces = sheet_faces(len(rest)//41)
        data.from_pydata(rest, [], faces); data.update()
        cache = bpy.data.objects.new(data.name, data)
        bpy.context.collection.objects.link(cache)
        cache.hide_render = True; cache.hide_set(True)
        cache['qualification'] = 'Authored connected static cloth; no motion or cloth simulation claim'
    points = [tuple(studio.torso_point(p)) for p in rest]
    faces = sheet_faces(len(points)//41)
    ob = studio.panel('MF_173_open_scarf', points, faces, mats['scarf'], .012, 1)
    for v, item in zip(rest, ob.data.attributes['MF_173_material_coords'].data): item.vector = v
    layering = ob.data.attributes.get('MF_174_wrap_under_harness') or ob.data.attributes.new(
        'MF_174_wrap_under_harness','FLOAT','POINT')
    for i,item in enumerate(layering.data):
        item.value = 1. if i//41<189 else 0.
    # Pressure/exclusion must act on the ACTUAL smoothed render surface. The
    # legacy tuck operation did this bake; disabling its mapping also removed
    # the bake, allowing later subdivision to undo the new layer fit.
    data = studio.single_surface_mesh(ob)
    for mod in list(ob.modifiers):
        if mod.type=='SUBSURF': ob.modifiers.remove(mod)
    studio.set_surface(ob.name,data,.012)
    # Support proxy is a hidden identical sheet, not a second visible garment.
    support = studio.panel('MF_173_diagonal_scarf_fall', points, faces, mats['scarf'], .012, 0)
    for v, item in zip(rest, support.data.attributes['MF_173_material_coords'].data): item.vector = v
    support.hide_render = True
    return frame


def shoulder_cleanup_weight(x,z):
    return (studio.smoothstep((abs(x)-.88)/.52)
            *studio.smoothstep((z+3.85)/1.10)
            *studio.smoothstep((-1.12-z)/.40))


def fair_shoulder_turns(points,faces):
    """Local static cloth cleanup; not a change to anatomy or a dynamics claim."""
    import bpy
    from mathutils import Vector
    from wardrobe_refinement import tree_for
    neighbors = [set() for _ in points]
    for face in faces:
        for a,b in zip(face,face[1:]+face[:1]):
            neighbors[a].add(b); neighbors[b].add(a)
    weights = [shoulder_cleanup_weight(p.x,p.z) for p in points]
    points = [p.copy() for p in points]
    for _ in range(32):
        prior = points
        points = [p.lerp(sum((prior[j] for j in neighbors[i]),Vector())/len(neighbors[i]),.44*weights[i])
                  if weights[i] and neighbors[i] else p.copy() for i,p in enumerate(prior)]
    # Exclude the actual skin/tunic after fairing without projecting folds to
    # the upper-arm radial section that caused the collar/cup failure.
    supports = [tree_for(bpy.data.objects[name]) for name in
                ('MF_studio_adult_body','MF_fit_tunic_173_visible')]
    for i,p in enumerate(points):
        # Free lateral folds must fall around the shoulder, not stick out as
        # unsupported epaulettes. Gather the outer width while preserving the
        # inner shoulder opening and the two differently slanted chest passes.
        lateral = studio.smoothstep((abs(p.x)-1.48)/.42)
        if weights[i] and lateral:
            p.x *= 1-.14*lateral*weights[i]
            p.z -= .13*lateral*weights[i]
        if not weights[i] or p.z < -2.30: continue
        hits = []
        for tree in supports:
            hit,_,_,_ = tree.ray_cast(p+Vector((0,0,1.)),Vector((0,0,-1)),2.)
            if hit is not None: hits.append(hit.z)
        if hits and p.z<max(hits)+.035: p.z = max(hits)+.035
    return points


def sheet_faces(columns):
    return [(i*41+j, (i+1)*41+j, (i+1)*41+j+1, i*41+j+1)
            for i in range(columns-1) for j in range(40)]


def connected_pattern():
    import bpy
    from mathutils import Vector
    from wardrobe_refinement import tree_for
    from wardrobe_tension import open_curve
    source = bpy.data.objects['MF_173_neutral_scarf_pattern']
    raw = [v.co.copy() for v in source.data.vertices]
    shirt = tree_for(bpy.data.objects['MF_fit_tunic_173_visible'])
    skin = tree_for(bpy.data.objects['MF_studio_adult_body'])
    groom = tree_for(bpy.data.objects['MF_173_static_groom_clearance'])

    def exclude(p, margin=.045):
        # Bounded torso rays avoid snapping onto the adjacent arm or another
        # fold; rear hair support is additional, not an anatomy modification.
        center = Vector((0, .14, p.z))
        radial = Vector((p.x, p.y-.14, 0))
        if radial.length < 1e-5: return p
        direction = radial.normalized(); radius = radial.length
        for tree in (shirt, skin, groom):
            hit, _, _, distance = tree.ray_cast(center, direction, 3.2)
            if hit is not None and distance+margin > radius:
                radius = distance+margin
        return center+direction*radius

    core = []
    for i in range(24, 57):
        row = []
        for j in range(41):
            p = raw[i*41+j].copy()
            back = studio.smoothstep((j/40-.56)/.44)
            p.z -= 2.15*back
            if back:
                p.y += .24*back
                p = exclude(p, .040)
                # Three broad unequal gravity falls; no evenly spaced ripples.
                p.y += back*(.06*math.exp(-((p.x+.58)/.23)**2)
                              + .09*math.exp(-((p.x-.25)/.32)**2))
            row.append(p)
        core.append(row)

    root = sum(core[0], Vector())/41
    anchors = [root, Vector((-1.28,.95,-1.30)), Vector((-1.43,.80,-2.10)),
               Vector((-1.43,-.28,-1.85)), Vector((-1.30,-1.0,-2.70)),
               Vector((-.40,-1.50,-3.05)), Vector((.65,-1.42,-2.62)),
               Vector((1.55,-.62,-1.78)), Vector((1.62,.35,-1.75)),
               Vector((.80,1.26,-1.54)), Vector((-.15,1.36,-1.85)),
               Vector((-.95,1.16,-1.43)), Vector((-1.65,.35,-1.70)),
               Vector((-1.55,-.55,-1.88)), Vector((-.65,-1.48,-2.70)),
               Vector((.35,-1.51,-2.40)), Vector((1.42,-.85,-1.87)),
               Vector((1.62,.12,-1.73)), Vector((1.35,.98,-2.12)),
               Vector((.35,1.08,-1.98))]
    path = open_curve(anchors, 10)
    long = []; previous = (core[0][-1]-core[0][0]).normalized()
    for i, center in enumerate(path):
        tangent = (path[min(i+1,len(path)-1)]-path[max(0,i-1)]).normalized()
        outward = Vector((center.x,center.y-.14,0)).normalized()
        cap = studio.smoothstep((abs(center.x)-1.2)/.30)*studio.smoothstep((center.z+2.3)/.4)
        support_normal = outward.lerp(Vector((0,0,1)), cap).normalized()
        width = tangent.cross(support_normal).normalized()
        if width.dot(previous)<0: width = -width
        previous = width
        start = studio.smoothstep(i/12)
        end = studio.smoothstep((i-(len(path)-16))/15)
        row = []
        for j in range(41):
            v = j/40
            root_offset = core[0][j]-root
            offset = root_offset.lerp(width*((v-.5)*(1.00-.28*end-.38*cap)),start)
            p = center+offset
            # Creases vary with support and cloth width; keep valleys broad.
            relief = (.035*math.exp(-((v-.22-.04*math.sin(i*.035))/.13)**2)
                      + .065*math.exp(-((v-.65+.05*math.sin(i*.026))/.19)**2))
            p += outward*relief*start
            p = p.lerp(exclude(p, .055), (1-cap)*start)
            if cap:
                hits = []
                for tree in (shirt, skin):
                    hit, normal, _, _ = tree.ray_cast(p+Vector((0,0,1.5)), Vector((0,0,-1)), 3.)
                    if hit is not None: hits.append(hit.z)
                if hits:
                    supported = p.copy(); supported.z = max(hits)+.045+relief*.4
                    p = p.lerp(supported, cap*start)
            # Second winding sits above the first at crossings, not coincident.
            if i>105: p += outward*.050*(1-end)
            if end: p -= outward*.025*end
            row.append(p)
        long.append(row)
    # A shorter opposite end falls beneath the rear wrap, not around the arm.
    short = []
    for k in range(1, 21):
        t = k/20; row = []
        for j in range(41):
            p = core[-1][j].copy(); p.z = p.z*(1-t)+(-2.70-.40*j/40)*t
            p.y = p.y*(1-t)+(1.00+.08*(j/40))*t
            p.x *= 1-.22*t
            row.append(exclude(p,.040))
        short.append(row)
    return [tuple(p) for row in list(reversed(long[1:]))+core+short for p in row]


def no_legacy_mapping(*args):
    """The connected pattern already includes its ends; don't remap them."""
    return None


def end_approach_z(distance_from_end):
    """Monotone downward entry from upper waist into the belt, no return loop."""
    return -5.12+.45*max(0.,min(24.,distance_from_end))/24


def leather(frame, mats):
    import bpy
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    from wardrobe_refinement import tree_for
    ORIGINAL_LEATHER(frame, mats)
    original_centers = {sign:[(bpy.data.objects['MF_173_tension_harness_'+str(sign)].data.vertices[2*i].co
                            +bpy.data.objects['MF_173_tension_harness_'+str(sign)].data.vertices[2*i+1].co)/2
                             for i in range(len(bpy.data.objects['MF_173_tension_harness_'+str(sign)].data.vertices)//2)]
                        for sign in (-1,1)}
    skin = tree_for(bpy.data.objects['MF_studio_adult_body'])
    shirt = bpy.data.objects['MF_fit_tunic_173_visible']
    data = studio.single_surface_mesh(shirt)
    cloth = BVHTree.FromPolygons([shirt.matrix_world @ v.co for v in data.vertices],
                                [tuple(f.vertices) for f in data.polygons])
    bpy.data.meshes.remove(data)
    belt = bpy.data.objects['MF_173_waist_belt']
    shell = next(m for m in belt.modifiers if m.type == 'SOLIDIFY')
    shell.offset = 1.; shell.thickness = .040
    belt_tree = tree_for(belt)
    # A leather band bridges folds as a continuous strip. At the superior
    # shoulder use an upward-facing clearance envelope, not independent
    # per-vertex normal snaps onto competing fold faces (preview08 failure).
    scarf = bpy.data.objects['MF_173_open_scarf']
    scarf_data = studio.single_surface_mesh(scarf)
    layer = scarf_data.attributes['MF_174_wrap_under_harness'].data
    scarf_tree = BVHTree.FromPolygons([scarf.matrix_world@v.co for v in scarf_data.vertices],
        [tuple(f.vertices) for f in scarf_data.polygons
         if sum(layer[i].value for i in f.vertices)/len(f.vertices)>.65])
    bpy.data.meshes.remove(scarf_data)
    for sign in (-1, 1):
        ob = bpy.data.objects['MF_173_tension_harness_' + str(sign)]
        nrows = len(ob.data.vertices) // 2
        shell = next(m for m in ob.modifiers if m.type == 'SOLIDIFY')
        shell.offset = 0.; shell.thickness = .016
        for v in ob.data.vertices:
            p = ob.matrix_world @ v.co
            row = v.index // 2; end_weight = 1 - studio.smoothstep(min(row, nrows - 1 - row) / 8)
            if end_weight:
                local = studio.torso_matrix(-5.2).inverted() @ p
                local.z = local.z * (1 - end_weight) - 5.28 * end_weight
                p = studio.torso_matrix(-5.2) @ local
            for _ in range(2):
                for tree, margin in ((skin, .040), (cloth, .045)):
                    hit, normal, _, distance = tree.find_nearest(p)
                    if hit is None: continue
                    local = studio.torso_matrix(-2.8).inverted() @ hit
                    root = studio.torso_matrix(-2.8) @ Vector((0,.14,local.z))
                    if normal.dot(hit-root)<0: normal = -normal
                    if distance < .55 and (p - hit).dot(normal) < margin:
                        p = hit + normal * margin
            if end_weight:
                hit, normal, _, distance = belt_tree.find_nearest(p)
                if hit is not None and distance < .5:
                    # Seat beneath the outer belt face, not a dangling lap.
                    p = p.lerp(hit - normal * .035, end_weight)
            v.co = ob.matrix_world.inverted() @ p
        frame = studio.torso_matrix(-2.8); inverse = frame.inverted()
        up = (frame.to_3x3()@Vector((0,0,1))).normalized()
        # Rebuild the shoulder portion on the superior garment/skin support.
        # The free head fall is not a load-bearing support for the band.
        from wardrobe_tension import open_curve
        authored = [(-1.15,-1.,-5.62),(-.65,-1.42,-4.55),(.35,-1.52,-3.45),
                    (1.2,-1.12,-2.55),(1.55,-.42,-1.65),(1.62,.35,-1.65),
                    (1.2,1.05,-2.65),(.35,1.28,-3.65),(-.65,1.2,-4.65),(-1.15,.92,-5.62)]
        path = open_curve([Vector((sign*x,y,z)) for x,y,z in authored])
        assert len(path)==nrows
        centers = [(ob.data.vertices[2*i].co+ob.data.vertices[2*i+1].co)/2 for i in range(nrows)]
        weights = [studio.smoothstep((q.z+2.65)/.65) for q in path]
        for i,q in enumerate(path):
            if not weights[i]:continue
            target = studio.torso_point(q);hits = []
            for tree in (skin,cloth):
                hit,_,_,_ = tree.ray_cast(target+up*1.5,-up,3.)
                if hit is not None:hits.append(hit)
            if hits:
                hit = max(hits,key=lambda p:p.dot(up))
                target += up*((hit-target).dot(up)+.085)
            centers[i] = centers[i].lerp(ob.matrix_world.inverted()@target,weights[i])
        for _ in range(8):
            previous = centers
            centers = [p.lerp((previous[max(0,i-1)]+previous[min(nrows-1,i+1)])/2,
                       .40*weights[i])
                       for i,p in enumerate(previous)]
        for i,center in enumerate(centers):
            world = ob.matrix_world@center
            weight = weights[i]
            if not weight: continue
            tangent = (ob.matrix_world.to_3x3()@(centers[min(nrows-1,i+1)]-centers[max(0,i-1)])).normalized()
            old = ob.matrix_world.to_3x3()@(ob.data.vertices[2*i+1].co-ob.data.vertices[2*i].co)/2
            new = tangent.cross(up).normalized()*.125
            if new.dot(old)<0:new = -new
            width = old.lerp(new,weight)
            ob.data.vertices[2*i].co = ob.matrix_world.inverted()@(world-width)
            ob.data.vertices[2*i+1].co = ob.matrix_world.inverted()@(world+width)
        # Replace the piecemeal edge fit with one coherent band. Preserve the
        # fair inherited route, but discard its independently snapped edges.
        from wardrobe_tension import fair
        centers = fair(original_centers[sign],40)
        normals = []
        for q in path:
            lateral = Vector((q.x,q.y-.14,0)).normalized()
            normal = (studio.torso_matrix(q.z).to_3x3()@lateral).normalized()
            normals.append(normal.lerp(up,studio.smoothstep((q.z+2.6)/.55)).normalized())
        normals = [n.normalized() for n in fair(normals,100)]
        previous_width = None
        for i,center in enumerate(centers):
            p = ob.matrix_world@center
            tangent = (ob.matrix_world.to_3x3()@(centers[min(nrows-1,i+1)]-centers[max(0,i-1)])).normalized()
            width = tangent.cross(normals[i]).normalized()*.125
            if previous_width is not None and width.dot(previous_width)<0:width = -width
            previous_width = width
            # Move both edges together to preserve strip framing/width.
            push = 0.
            for edge in (p-width,p+width):
                for tree in (skin,cloth):
                    hit,_,_,distance = tree.find_nearest(edge)
                    if hit is not None and distance<.45:
                        clearance = .035+.045*studio.smoothstep((path[i].z+2.6)/.55)
                        push = max(push,clearance-(edge-hit).dot(normals[i]))
            p += normals[i]*max(0.,push)
            end_weight = 1-studio.smoothstep(min(i,nrows-1-i)/8)
            if end_weight:
                local = studio.torso_matrix(-5.2).inverted()@p
                local.z = local.z*(1-end_weight)-5.18*end_weight
                p = studio.torso_matrix(-5.2)@local
                hit,n,_,distance = belt_tree.find_nearest(p)
                if hit is not None and distance<.5:
                    waist = studio.torso_matrix(-5.18)
                    local_hit = waist.inverted()@hit
                    root = waist@Vector((0,.14,local_hit.z))
                    if n.dot(hit-root)<0:n = -n
                    p = p.lerp(hit-n*.012,end_weight)
            ob.data.vertices[2*i].co = ob.matrix_world.inverted()@(p-width)
            ob.data.vertices[2*i+1].co = ob.matrix_world.inverted()@(p+width)
        # Entire terminal rows, including both corners, sit below the inner
        # belt face. Nearest edge normals can point up/down at belt borders;
        # a waist-local radial ray gives an unambiguous under-belt side.
        waist = studio.torso_matrix(-5.18);waist_inverse = waist.inverted()
        for v in ob.data.vertices:
            row = v.index//2;distance_from_end = min(row,nrows-1-row)
            weight = 1-studio.smoothstep(max(0,distance_from_end-9)/7)
            approach = 1-studio.smoothstep(max(0,distance_from_end-16)/8)
            if not approach:continue
            p = ob.matrix_world@v.co;local = waist_inverse@p
            local.z = max(local.z,end_approach_z(distance_from_end))
            p = waist@local
            root = waist@Vector((0,.14,local.z))
            direction = (waist.to_3x3()@Vector((local.x,local.y-.14,0))).normalized()
            hit,_,_,_ = belt_tree.ray_cast(root,direction,3.)
            if hit is not None:p = p.lerp(hit-direction*.012,weight)
            v.co = ob.matrix_world.inverted()@p
        ob.data.update()
        for edge in (0, 1):
            studio.line('MF_173_harness_welt_' + str(sign) + '_' + str(edge),
                        [tuple(ob.matrix_world @ ob.data.vertices[2 * i + edge].co) for i in range(nrows)],
                        mats['thread'], .005)
    bpy.context.view_layer.update()


def install():
    """Explicit replacement of fixed trusted functions, never code from job."""
    studio.sculpt_fabric = sculpt
    studio.construct_scarf = construct
    studio.leather_paths = leather
    studio.compress_cloth = no_legacy_mapping
    studio.tuck_scarf_ends = no_legacy_mapping
    import wardrobe_tension
    wardrobe_tension.press_visible_scarf = layered_pressure


def layered_pressure():
    """Only chest windings load beneath leather; the free head fall is over it."""
    import bpy
    ob = bpy.data.objects['MF_173_open_scarf']
    layer = ob.data.attributes['MF_174_wrap_under_harness'].data
    upper = {v.index:v.co.copy() for v in ob.data.vertices if layer[v.index].value<1.}
    ORIGINAL_PRESS()
    for index,p in upper.items():
        ob.data.vertices[index].co = p.lerp(ob.data.vertices[index].co,layer[index].value)
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    from wardrobe_refinement import tree_for
    frame = studio.torso_matrix(-2.8);inverse = frame.inverted()
    up = (frame.to_3x3()@Vector((0,0,1))).normalized()
    bands = []
    for sign in (-1,1):
        strap = bpy.data.objects['MF_173_tension_harness_'+str(sign)]
        data = studio.single_surface_mesh(strap)
        bands.append(BVHTree.FromPolygons([strap.matrix_world@v.co for v in data.vertices],
                                         [tuple(f.vertices) for f in data.polygons]))
        bpy.data.meshes.remove(data)
    shirt = tree_for(bpy.data.objects['MF_fit_tunic_173_visible'])
    for v in ob.data.vertices:
        p = ob.matrix_world@v.co;local = inverse@p
        if abs(local.x)<1.1 or not -2.65<local.z<-1.25:continue
        for tree in bands:
            hit,n,_,distance = tree.find_nearest(p)
            if hit is None or distance>.40:continue
            offset = p-hit;vertical = offset.dot(up)
            lateral = (offset-up*vertical).length
            weight = studio.smoothstep((.20-lateral)/.15)
            if vertical>-.045 and vertical<.40 and weight:
                p -= up*(vertical+.045)*weight
                floor,_,_,_ = shirt.ray_cast(p+up*.8,-up,1.6)
                if floor is not None and (p-floor).dot(up)<.018:
                    p += up*(.018-(p-floor).dot(up))
        v.co = ob.matrix_world.inverted()@p
    # Remove pressure-boundary frills on the shoulder turns, not wrinkles in
    # the chest or protected anatomical features. Smooth actual topology.
    weights = [shoulder_cleanup_weight((inverse@(ob.matrix_world@v.co)).x,
                                        (inverse@(ob.matrix_world@v.co)).z)
               for v in ob.data.vertices]
    neighbors = {}
    for face in ob.data.polygons:
        ids = list(face.vertices)
        for a,b in zip(ids,ids[1:]+ids[:1]):
            if weights[a]:neighbors.setdefault(a,set()).add(b)
            if weights[b]:neighbors.setdefault(b,set()).add(a)
    points = [v.co.copy() for v in ob.data.vertices]
    for _ in range(24):
        prior = points
        points = list(prior)
        for i,adjacent in neighbors.items():
            points[i] = prior[i].lerp(sum((prior[j] for j in adjacent),Vector())/len(adjacent),.42*weights[i])
    for i,p in enumerate(points):ob.data.vertices[i].co = p
    ob.data.update(); bpy.context.view_layer.update()


def cheap_construction_review(out):
    """Failure-seeking local screen before another complete mounted set."""
    import bpy
    from wardrobe_riding_fit import fit_render
    studio.neutral(bpy.data.objects['MF_body156_fit_rig'])
    mats = studio.make_materials(); studio.pose_wardrobe(mats)
    for ob in bpy.context.scene.objects:
        if ob.name.startswith(('MF_fit_horse','MF_fit_saddle','MF_fit_bridle','MF_fit_bit',
                               'MF_fit_Torus','MF_fit_Full','MF_fit_rein_',
                               'MF_fit_stirrup_leather_','MF_170_tail_')): ob.hide_render = True
    bpy.context.scene.cycles.samples = 24
    for label,angle in (('front',0),('right',40),('rear',180),('profile',90)):
        fit_render(out,'upper-'+label,angle,(0,.15,-1.7),7.,(800,850))
    for label,angle in (('left',-40),('right',40)):
        fit_render(out,'chest-'+label,angle,(0,-.3,-3.2),4.,(750,750))
    if out.name.endswith('preview08'):
        ob = bpy.data.objects['MF_173_open_scarf']
        saved = [v.co.copy() for v in ob.data.vertices]
        ORIGINAL_PRESS(); studio.border_seams(ob,mats['seam'])
        maximum = max((v.co-p).length for v,p in zip(ob.data.vertices,saved))
        fit_render(out,'legacy-pressure-front',0,(0,.15,-1.7),7.,(800,850))
        fit_render(out,'legacy-pressure-right',40,(0,.15,-1.7),7.,(800,850))
        for v,p in zip(ob.data.vertices,saved): v.co = p
        ob.data.update(); studio.border_seams(ob,mats['seam'])
        bpy.context.scene['MF_174_legacy_pressure_max_delta'] = maximum


def belt_review(out):
    import bpy
    from wardrobe_riding_fit import fit_render,riding_pose
    from mathutils import Vector
    rig = bpy.data.objects['MF_body156_fit_rig']
    studio.neutral(rig);mats = studio.make_materials();studio.pose_wardrobe(mats)
    for ob in bpy.context.scene.objects:
        if ob.name.startswith(('MF_fit_horse','MF_fit_saddle','MF_fit_bridle','MF_fit_bit','MF_fit_Torus',
                              'MF_fit_Full','MF_fit_rein_','MF_fit_stirrup_leather_','MF_170_tail_')):ob.hide_render = True
    bpy.context.scene.cycles.samples = 24
    for pose in ('neutral','mounted'):
        if pose=='mounted':riding_pose(rig);bpy.context.view_layer.update();studio.pose_wardrobe(mats)
        belt = bpy.data.objects['MF_173_waist_belt']
        center = sum((belt.matrix_world@v.co for v in belt.data.vertices),Vector())/len(belt.data.vertices)
        for label,angle in (('front',0),('rear',180)):
            fit_render(out,pose+'-belt-'+label,angle,tuple(center),4.,(750,650))


def belt_diagnose(out):
    import bpy
    from mathutils import Vector
    from wardrobe_refinement import tree_for
    studio.neutral(bpy.data.objects['MF_body156_fit_rig'])
    studio.pose_wardrobe(studio.make_materials())
    belt = bpy.data.objects['MF_173_waist_belt'];tree = tree_for(belt)
    frame = studio.torso_matrix(-5.18);inv = frame.inverted()
    ev = belt.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh = ev.to_mesh()
    points = [inv@(belt.matrix_world@v.co) for v in mesh.vertices];ev.to_mesh_clear()
    rows = {}
    for sign in (-1,1):
        ob = bpy.data.objects['MF_173_tension_harness_'+str(sign)]
        record = []
        for index in (0,1,2,3,len(ob.data.vertices)-2,len(ob.data.vertices)-1):
            p = ob.matrix_world@ob.data.vertices[index].co;local = inv@p
            root = frame@Vector((0,.14,local.z))
            direction = (frame.to_3x3()@Vector((local.x,local.y-.14,0))).normalized()
            hit,n,_,distance = tree.ray_cast(root,direction,3.)
            near,nn,_,nd = tree.find_nearest(p)
            record.append({'index':index,'local':tuple(local),'ray_hit':tuple(inv@hit) if hit is not None else None,
                           'ray_signed':(p-hit).dot(direction) if hit is not None else None,
                           'nearest':tuple(inv@near),'nearest_normal':tuple(nn),'nearest_distance':nd})
        rows[str(sign)] = record
    mods = [{'name':m.name,'type':m.type,'levels':getattr(m,'levels',None),
             'render_levels':getattr(m,'render_levels',None),'offset':getattr(m,'offset',None),
             'thickness':getattr(m,'thickness',None)} for m in belt.modifiers]
    visible = [o.name for o in bpy.context.scene.objects if not o.hide_render and ('belt' in o.name.lower() or 'harness' in o.name.lower())]
    (out/'result.json').write_text(json.dumps({'belt_local_bounds':[(min(p[i] for p in points),max(p[i] for p in points)) for i in range(3)],
        'modifiers':mods,'endpoints':rows,'visible_belts_harnesses':visible},indent=2)+'\n')


def validate(job):
    if not isinstance(job, dict) or set(job) != {'operation'} or job['operation'] not in OPERATIONS:
        raise ValueError('Only fixed reviewed operation enum admitted')
    if SOURCE.is_symlink() or not SOURCE.is_file() or digest(SOURCE) != SOURCE_SHA:
        raise ValueError('Pinned source mismatch')
    out = BASE / ('wardrobe174-' + job['operation'])
    if out.exists():
        raise ValueError('Never overwrite evidence')
    if job['operation'] in ('seal01','verify01'):source_binding()
    if job['operation']=='verify01':
        native = BASE/'wardrobe174-seal01/dressed-fit.blend'
        result = json.loads((native.parent/'result.json').read_text())
        if native.is_symlink() or digest(native)!=result['native_sha256']:
            raise ValueError('Selected native mismatch')
    return out


def source_binding():
    """Read only fixed admitted source/input paths; no paths from job input."""
    binding_path = BASE/'wardrobe174-operating/source-binding.json'
    if binding_path.is_symlink() or not binding_path.is_file():
        raise ValueError('Freeze selected source binding before dispatch')
    binding = json.loads(binding_path.read_text())
    expected = {str(p.relative_to(ROOT)) for p in (ROOT/'src/movie_factory/adapters/blender').glob('*.py')}
    expected.update({'scripts/wardrobe_construction174.py','scripts/wardrobe_construction174_verify.py',
        'scripts/package_wardrobe_construction174.py','scripts/package_wardrobe_studio.py',
        'scripts/package_wardrobe_fit_review.py','tests/unit/test_wardrobe_construction174.py',
        'tests/unit/test_wardrobe_construction174_package.py'})
    rows = binding['source_files']
    if len(rows)!=len(expected) or {r['path'] for r in rows}!=expected:
        raise ValueError('Unexpected source manifest paths')
    inputs = {str(SOURCE.relative_to(ROOT)),str(PHYSICS_INPUT.relative_to(ROOT)),
        '.runtime/assets/series01-dressing-source/scarf-original.glb',
        '.runtime/art-direction/series01-pashtun-baseline-v01/frontal-v02-individualized.png',
        '.runtime/art-direction/series01-pashtun-baseline-v01/portrait-v07-individualized.png'}
    if len(binding['inputs'])!=len(inputs) or {r['path'] for r in binding['inputs']}!=inputs:
        raise ValueError('Unexpected input manifest paths')
    for row in rows+binding['inputs']:
        path = ROOT/row['path']
        if path.is_symlink() or digest(path)!=row['sha256']:
            raise ValueError('Frozen source or input changed')
    return binding


def seal(out):
    import bpy
    import numpy as np
    from wardrobe_riding_fit import accepted_signature,evaluated_surfaces
    from body_studio_fit import coordinates_digest
    from static_tail_dock import data_signature
    binding = source_binding(); binding_hash = digest(BASE/'wardrobe174-operating/source-binding.json')
    prior = json.loads((SOURCE.parent/'result.json').read_text())
    protected = accepted_signature(prior['protected_signatures'])
    basis = coordinates_digest(tuple(v.co for v in bpy.data.objects['MF_studio_adult_body'].data.vertices))
    assert protected==prior['protected_signatures'] and basis==prior['body_basis_digest']
    studio.render_set(out,full=True)
    assert accepted_signature(protected)==protected
    assert coordinates_digest(tuple(v.co for v in bpy.data.objects['MF_studio_adult_body'].data.vertices))==basis
    tail = data_signature(bpy.data.objects['MF_170_tail_fibers']);assert tail==prior['static_tail_curve_digest']
    scene = bpy.context.scene
    scene['MF_174_source_commit'] = binding['source_commit']
    scene['MF_174_source_binding_sha256'] = binding_hash
    scene['MF_174_asset_status'] = 'Static appearance pending; motion and upstream rights not qualified'
    names = [o.name for o in scene.objects if not o.hide_render and o.type=='MESH']
    np.savez_compressed(out/'evaluated-surfaces.npz',**evaluated_surfaces(names))
    for text in bpy.data.texts:text.use_module = False
    bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(out/'dressed-fit.blend'),compress=True)
    result = {'source_sha256':SOURCE_SHA,'source_commit':binding['source_commit'],
        'source_git_tree':binding['source_git_tree'],'source_binding_sha256':binding_hash,
        'native_sha256':digest(out/'dressed-fit.blend'),'protected_signatures':protected,
        'body_basis_digest':basis,'static_tail_curve_digest':tail,'head_scale_changed':False,
        'visual_gate':'NOT_RUN','Director_acceptance':'PENDING','blender_version':bpy.app.version_string,
        'blender_build_hash':str(bpy.app.build_hash),
        'sleeve_measurements':json.loads(scene['MF_174_sleeve_measurements']),
        'limits':['Frozen neutral discovery geometry and prescribed static transport; not dynamics',
                  'Source-bound transformation does not reconstruct uncommitted discovery source',
                  'Not motion, cultural, rights or release qualification']}
    (out/'result.json').write_text(json.dumps(result,indent=2)+'\n')


def probe(out):
    import bpy
    from wardrobe_riding_fit import fit_render
    studio.neutral(bpy.data.objects['MF_body156_fit_rig'])
    mats = studio.make_materials()
    studio.pose_wardrobe(mats)
    garments = [ob for ob in bpy.context.scene.objects if not ob.hide_render and
                (ob.name.startswith(('MF_fit_', 'MF_171_', 'MF_173_', 'MF_170_')))]
    state = {ob.name: ob.hide_render for ob in garments}
    groups = [('tunic', ('MF_fit_tunic_173_visible',)),
              ('sleeves', ('MF_171_fitted_sleeve_L_173_visible', 'MF_171_fitted_sleeve_R_173_visible')),
              ('covering', ('MF_173_open_scarf',))]
    bpy.context.scene.cycles.samples = 16
    rows = {}
    for label, names in groups:
        for ob in garments: ob.hide_render = ob.name not in names
        for angle, view in ((180, 'rear'), (40, 'front')):
            fit_render(out, label + '-' + view, angle, (0, .15, -1.7), 7., (500, 550))
        rows[label] = {name: {'vertices': len(bpy.data.objects[name].data.vertices),
                             'bounds': [[min(v.co[k] for v in bpy.data.objects[name].data.vertices),
                                         max(v.co[k] for v in bpy.data.objects[name].data.vertices)] for k in range(3)]}
                       for name in names}
    for ob in garments: ob.hide_render = state[ob.name]
    (out / 'result.json').write_text(json.dumps(rows, indent=2) + '\n')


def main():
    import bpy
    job = json.loads(Path(sys.argv[sys.argv.index('--') + 1]).read_text())
    out = validate(job)
    out.mkdir()
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE), load_ui=False, use_scripts=False)
    bpy.context.scene['MF_174_output'] = str(out)
    if job['operation'] == 'probe01':
        probe(out)
    elif job['operation'] == 'probe02':
        studio.neutral(bpy.data.objects['MF_body156_fit_rig'])
        cache = bpy.data.objects['MF_173_neutral_scarf_pattern']
        rows = {str(i): [tuple(cache.data.vertices[i*41+j].co) for j in (0, 10, 20, 30, 40)]
                for i in (20, 24, 28, 32, 40, 48, 52, 56, 60)}
        (out / 'result.json').write_text(json.dumps(rows, indent=2) + '\n')
    elif job['operation'].startswith('preview'):
        install()
        if job['operation']=='preview23':
            belt_diagnose(out);return
        elif job['operation'] in ('preview21','preview22','preview24'):
            belt_review(out)
        elif job['operation'] in tuple('preview%02d'%i for i in range(8,20)):
            cheap_construction_review(out)
        else:
            studio.render_set(out, full=job['operation']=='preview20')
        from wardrobe_riding_fit import accepted_signature
        from body_studio_fit import coordinates_digest
        prior = json.loads((SOURCE.parent / 'result.json').read_text())
        assert accepted_signature(prior['protected_signatures']) == prior['protected_signatures']
        assert coordinates_digest(tuple(v.co for v in bpy.data.objects['MF_studio_adult_body'].data.vertices)) == prior['body_basis_digest']
        (out / 'result.json').write_text(json.dumps({'source_unchanged': digest(SOURCE) == SOURCE_SHA,
            'protected_exact': True, 'body_basis_exact': True, 'visual_gate': 'NOT_RUN',
            'sleeve_measurements': json.loads(bpy.context.scene['MF_174_sleeve_measurements']),
            'legacy_pressure_comparison_max_delta': bpy.context.scene.get('MF_174_legacy_pressure_max_delta'),
            'limits': ['Static construction settle, not riding dynamics', 'Appearance pending']}, indent=2) + '\n')
    elif job['operation']=='seal01':
        install();seal(out)
    elif job['operation']=='verify01':
        install()
        from wardrobe_construction174_verify import verify
        verify(out,BASE,SOURCE,SOURCE_SHA,source_binding())


if __name__ == '__main__':
    main()
