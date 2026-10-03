"""Fixed private costume/actual-tack fit on Director-accepted body66.

Only reviewed operation names are admitted; no paths/code from a model job.
"""
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from character_assembly import BASE, ROOT, digest, inventory

BODY = BASE / 'body168-hip66/adult-body-fit.blend'
BODY_SHA = '1ed613b16dc5b618ae601b9645f6042927e036f60f74314a31fc07e3c5e5c327'
HORSE = ROOT / 'runs/demonstrator-01/cut-world-v4/scene.blend'
HORSE_SHA = '7248f9dfecef3e9ece309c08055ab53ee6d802abe0a0e01307c7f9d8b93fd73e'


def validate(job):
    if not isinstance(job, dict) or set(job) != {'operation'} or job['operation'] not in ('inspect01', 'preview01', 'preview02', 'seal01'):
        raise ValueError('Only fixed reviewed operations admitted')
    for path, sha in ((BODY, BODY_SHA), (HORSE, HORSE_SHA)):
        if path.is_symlink() or not path.is_file() or digest(path) != sha:
            raise ValueError('Pinned fit input mismatch')
    out = BASE / ('wardrobe169-' + job['operation'])
    if out.exists():
        raise ValueError('Never overwrite fit evidence')
    return out


def inspect(out):
    import bpy
    from mathutils import Matrix
    bpy.ops.wm.open_mainfile(filepath=str(BODY), load_ui=False, use_scripts=False)
    body = bpy.data.objects['MF_studio_adult_body']
    rig = bpy.data.objects['MF_body156_fit_rig']
    result = {'body_source': BODY_SHA, 'horse_source': HORSE_SHA,
              'body_inventory': inventory(),
              'body_bones': {b.name: {'head': list(b.head_local), 'tail': list(b.tail_local)} for b in rig.data.bones},
              'body_materials': [m.name for m in body.data.materials]}
    recipe = json.loads((BODY.parent / 'result.json').read_text())['pose_screen']['pose_matrices']
    for n, m in recipe.items():
        rig.pose.bones[n].matrix_basis = Matrix(m)
    bpy.context.view_layer.update()
    result['seated_bones'] = {b.name: {'head': list(b.head), 'tail': list(b.tail)} for b in rig.pose.bones}
    bpy.ops.wm.open_mainfile(filepath=str(HORSE), load_ui=False, use_scripts=False)
    bpy.context.scene.frame_set(0)
    result['horse_inventory'] = [r for r in inventory() if any(s in r['name'].lower() for s in ('horse', 'saddle', 'rein', 'bridle', 'stirrup', 'torus'))]
    result['horse_bones'] = {b.name: {'head': list(b.head), 'tail': list(b.tail)} for b in bpy.data.objects['horse.rig'].pose.bones if any(k in b.name for k in ('torso', 'head', 'neck'))}
    result['source_unchanged'] = digest(BODY) == BODY_SHA and digest(HORSE) == HORSE_SHA
    (out / 'inventory.json').write_text(json.dumps(result, indent=2) + '\n')


def main():
    job = json.loads(Path(sys.argv[sys.argv.index('--') + 1]).read_text())
    out = validate(job)
    out.mkdir()
    if job['operation'] == 'inspect01':
        inspect(out)
    else:
        build(out, job['operation'])


def aim(rig, name, direction):
    from mathutils import Vector
    bone = rig.pose.bones[name]
    q = (bone.tail - bone.head).normalized().rotation_difference(Vector(direction).normalized())
    matrix = q.to_matrix().to_4x4() @ bone.matrix
    matrix.translation = bone.head
    bone.matrix = matrix
    import bpy
    bpy.context.view_layer.update()


def riding_pose(rig, strength=1.):
    import bpy
    from mathutils import Matrix
    for b in rig.pose.bones:
        b.matrix_basis = Matrix.Identity(4)
    for name, angle in (('spine', 24), ('chest', 10)):
        b = rig.pose.bones[name]
        b.rotation_mode = 'XYZ'; b.rotation_euler.x = math.radians(angle) * strength
    bpy.context.view_layer.update()
    for side, sign in (('L', 1), ('R', -1)):
        aim(rig, 'thigh.' + side, (sign * 1.8 * strength, -1.7 * strength, -3.08 + 1.05 * strength))
        aim(rig, 'shin.' + side, (-sign * .25 * strength, .65 * strength, -3.2))
        aim(rig, 'foot.' + side, (0, -1.08, -.25))
        aim(rig, 'upperarm.' + side, (-sign * .15, -1.8 * strength, -2.6 + 1.15 * strength))
        aim(rig, 'forearm.' + side, (-sign * .8 * strength, -1.4 * strength, -1.55 + 1.05 * strength))
        aim(rig, 'hand.' + side, (0, -1, -.15))


def shell(body, name, region, mat, rig):
    """Reuse the coherent body topology/weights, never edit the accepted body."""
    import bpy
    from mathutils import Vector
    from character_assembly import mesh
    selected = []
    def keep(v):
        p = v.co
        arm = sum(g.weight for g in v.groups if body.vertex_groups[g.group].name.startswith(('upperarm.', 'forearm.', 'hand.')))
        if region == 'tunic':
            neckline = -2.25 + .70 * min(1., abs(p.x) / 1.25)
            return -6.2 < p.z < neckline and (arm < .4 or p.z > -5.45)
        if region == 'trousers':
            return -11.45 < p.z < -5.72 and arm < .01
        return p.z < -10.95 and arm < .01
    for p in body.data.polygons:
        if all(keep(body.data.vertices[i]) for i in p.vertices):
            selected.append(p)
    indices = sorted({i for p in selected for i in p.vertices})
    lookup = {i: j for j, i in enumerate(indices)}
    points = []
    for i in indices:
        v = body.data.vertices[i]; p = v.co.copy()
        arm = sum(g.weight for g in v.groups if body.vertex_groups[g.group].name.startswith(('upperarm.', 'forearm.', 'hand.')))
        if region == 'tunic' and arm < .3:
            radial = Vector((p.x, p.y - .18, 0))
            if radial.length:
                radial.normalize(); p += radial * .18
            p.y = min(p.y, -.75) if p.y < -.35 and p.z < -2.9 else p.y
        else:
            p += v.normal * (.18 if region == 'trousers' else .075)
        points.append(tuple(p))
    ob = mesh(name, points, [tuple(lookup[i] for i in p.vertices) for p in selected], mat)
    names = rig.data.bones.keys()
    groups = {n: ob.vertex_groups.new(name=n) for n in names}
    for i in indices:
        weights = {body.vertex_groups[g.group].name: g.weight for g in body.data.vertices[i].groups if body.vertex_groups[g.group].name in names}
        total = sum(weights.values())
        assert total > .99
        for n, w in weights.items():
            if w: groups[n].add([lookup[i]], w / total, 'REPLACE')
    mod = ob.modifiers.new('Reviewed anatomical weight transfer', 'ARMATURE')
    mod.object = rig; mod.use_deform_preserve_volume = True
    sub = ob.modifiers.new('Cloth surface', 'SUBSURF'); sub.levels = 2
    shrink = ob.modifiers.new('Pose clearance to protected body', 'SHRINKWRAP')
    shrink.target = body; shrink.wrap_method = 'NEAREST_SURFACEPOINT'; shrink.wrap_mode = 'OUTSIDE'
    shrink.offset = .12 if region != 'boots' else .055
    thickness = ob.modifiers.new('Garment thickness', 'SOLIDIFY'); thickness.thickness = .025
    return ob


def actual_horse():
    """Bake a fixed actual source pose for private fitting, not gait reuse proof."""
    import bpy
    from mathutils import Matrix, Vector
    wanted = ['horse', 'horse.rig', 'saddle', 'saddle.pad', 'saddle.stirrup', 'saddle.stirrup.strap', 'bridle', 'bridle.body', 'bit', 'Torus.002', 'Full Bushy Flowing Horse Tail']
    with bpy.data.libraries.load(str(HORSE), link=False) as (a, b):
        b.objects = [n for n in wanted if n in a.objects]
    imported = list(b.objects)
    for ob in imported:
        if ob.name not in bpy.context.scene.objects: bpy.context.scene.collection.objects.link(ob)
        parent = ob.parent
        while parent:
            if parent.name not in bpy.context.scene.objects: bpy.context.scene.collection.objects.link(parent)
            parent = parent.parent
    bpy.context.scene.frame_set(0); bpy.context.view_layer.update()
    # Scene-unit conversion based on body height; seat position is deliberately
    # authored against the measured source saddle, not a saddle proxy.
    transform = Matrix.Translation((0, .20, -6.85)) @ Matrix.Scale(8.3, 4) @ Matrix.Translation((0, -2.52, -1.57))
    baked = []
    deps = bpy.context.evaluated_depsgraph_get()
    for ob in imported:
        if ob.type not in ('MESH', 'CURVE'): continue
        ev = ob.evaluated_get(deps)
        data = bpy.data.meshes.new_from_object(ev, preserve_all_data_layers=True, depsgraph=deps)
        copy = bpy.data.objects.new('MF_fit_' + ob.name, data)
        bpy.context.scene.collection.objects.link(copy)
        copy.matrix_world = transform @ ev.matrix_world
        copy['source_object'] = ob.name; copy['fit_scope'] = 'Fixed frame0 evaluated geometry; no motion qualification'
        baked.append(copy)
    for ob in imported:
        ob.hide_render = True; ob.hide_set(True)
    return baked


def ribbon(name, points, width, mat):
    from mathutils import Vector
    from character_assembly import mesh
    vertices = []
    for i, p in enumerate(points):
        p = Vector(p)
        tangent = Vector(points[(i+1) % len(points)]) - Vector(points[i-1])
        outward = Vector((p.x, p.y - .18, 0)).normalized()
        across = tangent.cross(outward).normalized() * width / 2
        vertices.extend((tuple(p-across), tuple(p+across)))
    faces = [(2*i, 2*((i+1)%len(points)), 2*((i+1)%len(points))+1, 2*i+1) for i in range(len(points))]
    ob = mesh(name, vertices, faces, mat)
    mod = ob.modifiers.new('Leather thickness', 'SOLIDIFY'); mod.thickness = .04
    return ob


def build(out, operation):
    import bpy
    from mathutils import Matrix, Vector
    from character_assembly import material
    from body_studio_fit import protected, coordinates_digest
    bpy.ops.wm.open_mainfile(filepath=str(BODY), load_ui=False, use_scripts=False)
    before = protected()
    body = bpy.data.objects['MF_studio_adult_body']; rig = bpy.data.objects['MF_body156_fit_rig']
    body_hash = coordinates_digest(tuple(v.co) for v in body.data.vertices)
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'; scene.cycles.samples = 16
    scene.render.resolution_x = 540; scene.render.resolution_y = 900; scene.render.resolution_percentage = 100
    scene.view_layers[0].material_override = None
    cloth = material('MF_fit_indigo_tunic', (.021, .045, .095))
    pants = material('MF_fit_dark_indigo_trousers', (.016, .027, .053))
    leather = material('MF_fit_brown_harness_boots', (.11, .052, .025))
    clothes = [shell(body, 'MF_fit_tunic', 'tunic', cloth, rig), shell(body, 'MF_fit_trousers', 'trousers', pants, rig), shell(body, 'MF_fit_boots', 'boots', leather, rig)]
    # Adapt the actual reusable scarf only; keep accepted hair/skin unchanged.
    hood = bpy.data.objects['MF_adapted_donor_hood'].copy()
    hood.data = hood.data.copy(); scene.collection.objects.link(hood)
    hood.name = 'MF_fit_indigo_headscarf'; hood.hide_render = False; hood.hide_set(False)
    hood.constraints.clear(); hood.modifiers.clear()
    hood.matrix_world = Matrix.Translation((0,0,-.228)) @ Matrix.Scale(.88,4) @ hood.matrix_world
    hood.data.materials.clear(); hood.data.materials.append(cloth)
    rest = rig.matrix_world @ rig.data.bones['chest'].matrix_local
    c = hood.constraints.new('CHILD_OF'); c.target = rig; c.subtarget = 'chest'; c.inverse_matrix = rest.inverted()
    clothes.append(hood)
    # Cloth below the waist needs separate astride panels, not a closed skirt.
    # First fit uses the inherited contour/weights; folds are deferred until
    # the complete seat and tack clearances have been visually established.
    camera = scene.camera
    lights = sorted((o for o in scene.objects if o.name.startswith('MF_body156_softbox')), key=lambda o:o.name)
    def render(label, angle, center=(0,.1,-5.8), size=15.8):
        target=Vector(center); rot=Matrix.Rotation(math.radians(angle),3,'Z')
        camera.data.ortho_scale=size; camera.location=target+rot@Vector((0,-36,.6))
        camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler()
        for light,x in zip(lights,(-7,7)):
            light.location=target+rot@Vector((x,-9,7));light.rotation_euler=(target-light.location).to_track_quat('-Z','Y').to_euler()
        scene.render.filepath=str(out/(label+'.png'));bpy.ops.render.render(write_still=True)
    for b in rig.pose.bones:b.matrix_basis=Matrix.Identity(4)
    bpy.context.view_layer.update()
    for label, angle in [('front',0), ('side',90), ('rear',180)]: render('standing-'+label,angle)
    horse=actual_horse()
    riding_pose(rig)
    bpy.context.view_layer.update()
    for label,angle in [('side',90), ('front-quarter',-40), ('rear-quarter',140)]: render('mounted-'+label,angle,(0,-1,-8.5),25)
    result = {'source_body_sha256':BODY_SHA,'source_horse_sha256':HORSE_SHA,'operation':operation,
              'body_local_geometry_exact':coordinates_digest(tuple(v.co) for v in body.data.vertices)==body_hash,
              'protected_data_exact':all(protected()[n]==v for n,v in before.items()),
              'garments':[o.name for o in clothes], 'actual_horse_objects':[o.name for o in horse],
              'pose_matrices':{b.name:[list(r) for r in b.matrix_basis] for b in rig.pose.bones},
              'structural_visual_gate':'NOT_RUN_PENDING_INTERNAL_REVIEW', 'Director_acceptance':'PENDING',
              'limits':['Private static fit only', 'Harness/reins/stirrup adaptation incomplete in first diagnostic', 'No simulation, gait or final outfit acceptance'],
              'source_unchanged':digest(BODY)==BODY_SHA and digest(HORSE)==HORSE_SHA}
    assert result['body_local_geometry_exact'] and result['protected_data_exact'] and result['source_unchanged']
    if operation=='seal01':
        scene.render.image_settings.file_format='PNG'
        bpy.ops.wm.save_as_mainfile(filepath=str(out/'dressed-fit.blend'),compress=True)
        result['native_sha256']=digest(out/'dressed-fit.blend')
    (out/'result.json').write_text(json.dumps(result,indent=2)+'\n')


if __name__ == '__main__':
    main()
