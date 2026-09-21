"""Fixed local shape-first crown/temple study; source portraits are authority.

Closed, tapered volumes and a scalp support replace the failed open strips.
Preview has neutral materials only. No face, skin, rig or wardrobe edits.
"""
import hashlib
import json
import math
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / '.runtime/art-direction/series01-facebuilder-trial-01'
SOURCE = BASE / 'hair-anatomy-build-10/character-hair-anatomy.blend'
SOURCE_SHA = '3158f62b8eba1ce3c8244e8ba00773efceb3fc2892e8d4902f529a82dc8db8b0'
REFBASE = ROOT / '.runtime/art-direction/series01-pashtun-baseline-v01'
REFERENCES = {
    'frontal-v02-individualized.png': '7f959fed6ca4f57cb1b7fdaa20aa4a0fdd64208595a8b5debd8d060c79068c75',
    'portrait-v07-individualized.png': 'e6afc72b56fa57642b521fd7a922894d81a900b8cab0103f7c3f2cfb39a795f1',
}


def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def validate(job):
    if not isinstance(job, dict) or set(job) != {'operation', 'candidate'}:
        raise ValueError('Exact structured job required')
    if job['operation'] not in ('preview', 'repair', 'package') or type(job['candidate']) is not int or job['candidate'] not in (1, 2, 3):
        raise ValueError('Unsupported operation')
    if job['operation']=='repair' and job['candidate']!=3:
        raise ValueError('Only the identified candidate3 projection defect may be repaired')
    for p, h in [(SOURCE, SOURCE_SHA), *[(REFBASE / n, h) for n, h in REFERENCES.items()]]:
        if p.is_symlink() or digest(p) != h:
            raise ValueError('Pinned input changed')
    out = BASE / f'hair-sculpt-{job["operation"]}-{job["candidate"]:02}'
    if out.exists() or out.is_symlink() or out.resolve().parent != BASE.resolve():
        raise ValueError('Output exists or escapes fixed directory')
    if shutil.disk_usage(BASE).free < 5_000_000_000:
        raise ValueError('Disk low')
    if job['operation'] == 'package':
        stage='repair' if job['candidate']==3 else 'preview'
        p = BASE / f'hair-sculpt-{stage}-{job["candidate"]:02}/result.json'
        if p.is_symlink() or not p.is_file():
            raise ValueError('Preview required')
        data = json.loads(p.read_text())
        if data['handler_sha256'] != digest(Path(__file__)) or not data['protected_exact']:
            raise ValueError('Stale preview or failed protection')
    return out


def smooth(t):
    t = max(0., min(1., t))
    return t * t * (3 - 2 * t)


def spline(points, t):
    n = len(points) - 1
    f = max(0., min(n - 1e-9, t * n)); i = int(f); u = f - i
    a, b, c, d = [points[max(0, min(n, j))] for j in (i - 1, i, i + 1, i + 2)]
    return tuple(.5 * (2*b[k] + (-a[k]+c[k])*u + (2*a[k]-5*b[k]+4*c[k]-d[k])*u*u + (-a[k]+3*b[k]-3*c[k]+d[k])*u*u*u) for k in range(3))


def guides(candidate):
    # Reference-led center-part lift, broad temporal sweep and tucked ends.
    # The portrait does not specify hidden rear shape; these terminate behind
    # the ear, not in a newly invented full-length haircut.
    return [
        ([(.014,-1.00,.87),(.20,-1.035,1.04),(.49,-.94,1.00),(.78,-.73,.73),(.965,-.32,.41),(.94,.14,.20),(.82,.52,-.03)], .165, .073),
        ([(.018,-.78,1.13),(.23,-.84,1.30),(.56,-.70,1.20),(.84,-.38,.94),(.97,.03,.63),(.85,.58,.26)], .19, .090),
        ([(.017,-.44,1.31),(.22,-.49,1.46),(.56,-.32,1.36),(.85,.01,1.14),(.90,.43,.76),(.71,.75,.29)], .20, .080),
        ([(.02,-.08,1.33),(.20,-.10,1.46),(.53,.06,1.38),(.79,.35,1.08),(.73,.69,.66),(.51,.81,.23)], .19, .070),
        ([(.60,-.86,.84),(.78,-.64,.61),(.92,-.29,.34),(.91,.07,.19),(.84,.34,.04),(.76,.55,-.10)], .102, .047),
    ]


def profile(t, theta, width, depth):
    taper = math.sin(math.pi * max(0., min(1., t))) ** .48
    # Closed asymmetric lens: broad outer face with shallow buried underside.
    x = width * math.cos(theta) * taper
    s = math.sin(theta)
    y = (depth if s >= 0 else depth * .48) * s * taper
    if s > 0:
        # Two subtle flow divisions, not a repeated field of thin cylinders.
        y += .008 * s * (math.cos(theta * 6 + t * 3) - .25) * taper
    return x, y


def material(name, value):
    import bpy
    m = bpy.data.materials.new(name); m.use_nodes = True
    p = m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value = (value, value, value, 1)
    p.inputs['Roughness'].default_value = .78
    p.inputs['Specular IOR Level'].default_value = .15
    return m


def skull_surface(source):
    """Smooth convex scalp proxy excludes ear contours from hair fitting."""
    import bmesh
    from mathutils.bvhtree import BVHTree
    bm=bmesh.new()
    for v in source.data.vertices:
        x,y,z=v.co
        if abs(x)>.77 and z<.37 and y>-.30:
            continue
        bm.verts.new(v.co)
    hull=bmesh.ops.convex_hull(bm,input=list(bm.verts),use_existing_faces=False)
    bm.verts.index_update()
    faces=[f for f in hull['geom'] if isinstance(f,bmesh.types.BMFace)]
    tree=BVHTree.FromPolygons([tuple(v.co) for v in bm.verts],[[v.index for v in f.verts] for f in faces])
    bm.free()
    return tree


def volume_mesh(points, width, depth, side, idx, mat, tree=None, candidate=1):
    import bpy
    import bmesh
    from mathutils import Vector
    fitted = None
    if candidate >= 3 and tree is not None:
        fitted=[]
        origin=Vector((0,0,.3))
        for k, point in enumerate(points):
            co=Vector(point)
            hit,normal,_,_=tree.ray_cast(origin,(co-origin).normalized())
            if hit is None: raise ValueError('Control projection failed')
            fitted.append(tuple(hit+normal*(.001 if k in (0,len(points)-1) else .017)))
    ns, nr = 80, 24
    verts, faces = [], []
    for i in range(1, ns):
        t = i / ns
        def center(at):
            if fitted is not None:
                return Vector(spline(fitted,at))
            co = Vector(spline(points, at))
            if tree is None:
                return co
            origin = Vector((0,0,.3)); direction = (co-origin).normalized()
            hit, normal, _, _ = tree.ray_cast(origin,direction)
            if hit is None:
                raise ValueError('Scalp radial projection missed')
            return hit + normal * (.004 + .028 * math.sin(math.pi*at)**1.2)
        c = center(t)
        tangent = center(min(1,t+.001)) - center(max(0,t-.001))
        tangent.normalize()
        outward = Vector((c.x / .86**2, (c.y + .05) / 1.0**2, (c.z - .1) / 1.25**2))
        outward = (outward - tangent * outward.dot(tangent)).normalized()
        across = tangent.cross(outward).normalized()
        for j in range(nr):
            variable_width=width*(.94+.13*math.sin(t*7+idx*.7)) if candidate>=3 else width
            x, y = profile(t, 2*math.pi*j/nr, variable_width, depth*(.68 if candidate>=3 else 1))
            verts.append(tuple(c + across*x + outward*y))
    for i in range(ns-2):
        for j in range(nr):
            a = i*nr+j; b = i*nr+(j+1)%nr
            faces.append((a, b, b+nr, a+nr))
    start, end = len(verts), len(verts)+1
    verts.extend((tuple(center(0)), tuple(center(1))))
    for j in range(nr):
        faces.append((start, (j+1)%nr, j))
        a = (ns-2)*nr+j; b = (ns-2)*nr+(j+1)%nr
        faces.append((end, a, b))
    mesh = bpy.data.meshes.new(f'MF_sculpt_hair_lock_{side}_{idx}')
    mesh.from_pydata(verts, [], faces); mesh.update()
    bm = bmesh.new(); bm.from_mesh(mesh)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    assert all(e.is_manifold for e in bm.edges), 'Open lock surface'
    bm.to_mesh(mesh); bm.free()
    for p in mesh.polygons:
        p.use_smooth = True
    ob = bpy.data.objects.new(mesh.name, mesh)
    bpy.context.scene.collection.objects.link(ob); mesh.materials.append(mat)
    return ob


def sculpt(candidate):
    import bpy
    import bmesh
    from mathutils.bvhtree import BVHTree
    from hair_anatomy_refinement import is_hair
    for o in bpy.context.scene.objects:
        if is_hair(o):
            o.hide_render = True
    mat = material('MF_sculpt_hair_neutral', .27)
    old = bpy.data.objects['MF_reference_crown_hair']
    base = old.copy(); base.data = old.data.copy(); base.name = 'MF_sculpt_hair_support'
    bpy.context.scene.collection.objects.link(base); base.hide_render = False
    base.data.materials.clear(); base.data.materials.append(mat)
    for p in base.data.polygons:
        p.material_index = 0; p.use_smooth = True
    for v in base.data.vertices:
        v.co += v.normal * .022
    base.data.update()
    tree = None
    if candidate >= 2:
        body = bpy.data.objects['MF_continuous_head_neck']
        tree = skull_surface(old) if candidate>=3 else BVHTree.FromObject(body,bpy.context.evaluated_depsgraph_get())
        # Smooth only the new support's crop boundary, never the face.
        bm = bmesh.new(); bm.from_mesh(base.data)
        boundary = [v for v in bm.verts if any(e.is_boundary for e in v.link_edges)]
        for _ in range(8):
            adjusted = {}
            for v in boundary:
                neighbors = [e.other_vert(v) for e in v.link_edges if e.is_boundary]
                if len(neighbors)==2:
                    adjusted[v] = v.co*.4 + (neighbors[0].co+neighbors[1].co)*.3
            for v,co in adjusted.items(): v.co=co
        for v in bm.verts:
            hit,normal,_,distance=tree.find_nearest(v.co)
            if hit is None or distance>.2: raise ValueError('Support projection failed')
            v.co=hit+normal*(.006 if v in boundary else .016)
        bm.to_mesh(base.data); bm.free(); base.data.update()
    objects = []
    for side in (-1, 1):
        for idx, (points, width, depth) in enumerate(guides(candidate)):
            # Small unequal wave offsets follow the images' living asymmetry;
            # do not mirror a rigid repeating comb, nor alter the face.
            pts = [(side*x, y + (.018*math.sin(k*1.3) if side == 1 else 0), z + (.016*math.sin(k+idx) if side == 1 else 0)) for k, (x,y,z) in enumerate(points)]
            objects.append(volume_mesh(pts, width, depth, side, idx, mat, tree, candidate))
    closed_vertices=sum(len(o.data.vertices) for o in objects)
    if candidate >= 2:
        # Close the support and union only the newly authored hair objects.
        for o in list(bpy.context.selected_objects): o.select_set(False)
        base.hide_set(False); base.select_set(True); bpy.context.view_layer.objects.active=base
        solid=base.modifiers.new('Closed hair support','SOLIDIFY'); solid.thickness=.025; solid.offset=-1
        bpy.ops.object.modifier_apply(modifier=solid.name)
        for o in objects: o.select_set(True)
        bpy.ops.object.join()
        remesh=base.modifiers.new('Blend hair volumes','REMESH')
        remesh.mode='VOXEL'; remesh.voxel_size=.012; remesh.use_smooth_shade=True
        bpy.ops.object.modifier_apply(modifier=remesh.name)
        soft=base.modifiers.new('Soften intersections','SMOOTH'); soft.factor=.6; soft.iterations=3
        bpy.ops.object.modifier_apply(modifier=soft.name)
        if candidate>=3:
            # A narrow, low center-part valley. This moves new hair only and
            # prevents the two root groups merging into a solid central knot.
            for v in base.data.vertices:
                x,y,z=v.co
                weight=(1-smooth(abs(x)/.065))*smooth((z-.69)/.18)*(1-smooth((y-.28)/.3))
                if weight:
                    hit,normal,_,_=tree.find_nearest(v.co)
                    v.co=v.co.lerp(hit+normal*.007,weight)
            base.data.update()
        for p in base.data.polygons: p.use_smooth=True
    return {'closed_locks':len(objects), 'vertices_before_union':closed_vertices,
            'support_vertices':len(base.data.vertices), 'texture_detail_added':False,
            'volumes_unioned':candidate>=2,
            'ear_excluded_skull_proxy':candidate>=3,
            'scope':'crown to temple/ear; support behind head not finished rear hairstyle'}


def run(job):
    out = validate(job); out.mkdir()
    import bpy
    from illustrated_hair_section import protection
    from hair_anatomy_refinement import visibility
    from hijab_donor import review
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE), load_ui=False, use_scripts=False)
    before = protection()
    changes = sculpt(job['candidate'])
    assert protection() == before, 'Non-hair mutation'
    visibility()
    # Neutral override only for the temporary review; restore exactly afterward.
    old = {}; clay = material('MF_hair_shape_review_clay', .40)
    for o in bpy.context.scene.objects:
        if o.type == 'MESH' and (o.name == 'MF_continuous_head_neck' or o.name.startswith('MF_aimable_eye_')):
            old[o.name] = list(o.data.materials)
            for i in range(len(o.data.materials)):
                o.data.materials[i] = clay
    review(bpy.context.scene, out, (0,-.05,.12), 3.7, (('front',0),('left',-45),('right',45),('back',180)))
    for name, mats in old.items():
        for i, m in enumerate(mats):
            bpy.data.objects[name].data.materials[i] = m
    result = {'candidate':job['candidate'], 'source_sha256':SOURCE_SHA, 'reference_authority':REFERENCES,
              'handler_sha256':digest(Path(__file__)), 'protected_exact':protection()==before,
              'geometry':changes, 'director_acceptance':'PENDING', 'whole_hair_qualified':False}
    assert result['protected_exact']
    if job['operation'] == 'package':
        native = out/'hair-shape-study.blend'
        bpy.ops.wm.save_as_mainfile(filepath=str(native))
        bpy.ops.wm.open_mainfile(filepath=str(native), load_ui=False, use_scripts=False)
        result['fresh_reopen_protected_exact'] = protection()==before
        assert result['fresh_reopen_protected_exact']
        result['native_sha256'] = digest(native)
    assert digest(SOURCE) == SOURCE_SHA
    (out/'result.json').write_text(json.dumps(result, indent=2))


if __name__ == '__main__':
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    args = sys.argv[sys.argv.index('--')+1:]
    if len(args) != 1:
        raise ValueError('One fixed job required')
    run(json.loads(Path(args[0]).read_text()))
