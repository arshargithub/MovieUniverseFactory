"""Fixed, reference-textured crown/temple proof; no face or body edits.

Only preview (three variants) and seal of an inspected preview are admitted.
Illustrated source UVs remain attached to a single displaced hair shell. This
does not qualify a whole hairstyle, rear groom, animation or Director acceptance.
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


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(job):
    if not isinstance(job, dict) or set(job) != {'operation', 'candidate'}:
        raise ValueError('Exact structured job required')
    if type(job['candidate']) is not int or job['candidate'] not in (1, 2, 3, 4) or job['operation'] not in ('preview', 'seal'):
        raise ValueError('Unsupported operation')
    for p, expected in [(SOURCE, SOURCE_SHA), *[(REFBASE / n, h) for n, h in REFERENCES.items()]]:
        if p.is_symlink() or digest(p) != expected:
            raise ValueError('Pinned input changed')
    out = BASE / f'illustrated-hair-{job["operation"]}-{job["candidate"]:02}'
    if out.exists() or out.is_symlink() or out.resolve().parent != BASE.resolve():
        raise ValueError('Output exists or escapes fixed directory')
    if shutil.disk_usage(BASE).free < 5_000_000_000:
        raise ValueError('Disk low')
    if job['operation'] == 'seal':
        report = BASE / f'illustrated-hair-preview-{job["candidate"]:02}/result.json'
        if report.is_symlink() or not report.is_file():
            raise ValueError('Preview required')
        data = json.loads(report.read_text())
        if data['handler_sha256'] != digest(Path(__file__)) or not data['protected_exact']:
            raise ValueError('Preview stale or protection failed')
    return out


def smooth(t):
    t = max(0., min(1., t))
    return t * t * (3 - 2 * t)


def relief(x, y, z, candidate):
    """Broad swept volumes, not comb-like repeated thin ridges."""
    if z < .12 or y > .38:
        return 0.
    ax = abs(x)
    # Unequal overlapping wave heights follow the approved frontal sweep.
    curves = ((1.00, .65, .045, .092), (1.22, .63, .073, .14),
              (1.40, .52, .048, .16))
    value = 0.
    for root, drop, height, width in curves:
        center = root - drop * (ax / .96) ** 1.6
        center += .025 * math.sin(ax * 6 + (0 if x < 0 else .8))
        value += height * math.exp(-((z - center) / width) ** 2)
    return value * smooth(ax / .12) * (1 - smooth((y + .12) / .5)) * smooth((z - .12) / .25)


def protection():
    import bpy
    from neck_anatomy_review import signature
    from hair_anatomy_refinement import is_hair
    from hijab_donor import material_signature
    result = {}
    for o in bpy.context.scene.objects:
        if o.type in ('MESH', 'CURVE') and not is_hair(o):
            s = signature(o)
            s.pop('hide_render')  # Review visibility may hide clothing only.
            result[o.name] = s
    body = bpy.data.objects['MF_continuous_head_neck']
    result['rest_attributes'] = {
        a.name: [list(v.vector) for v in a.data] for a in body.data.attributes
        if a.data_type == 'FLOAT_VECTOR' and a.domain == 'POINT'
    }
    result['body_materials'] = [material_signature(m) for m in body.data.materials]
    return hashlib.sha256(json.dumps(result, sort_keys=True).encode()).hexdigest()


def build(candidate):
    import bpy
    from hair_anatomy_refinement import is_hair
    from dressing_motion_fit import hairline
    original = bpy.data.objects['MF_reference_crown_hair']
    for o in bpy.context.scene.objects:
        if is_hair(o):
            o.hide_render = True
    ob = original.copy()
    ob.data = original.data.copy()
    ob.name = 'MF_illustrated_hair_section'
    bpy.context.scene.collection.objects.link(ob)
    ob.hide_render = False
    ob.data.materials.clear()
    for m in original.data.materials:
        ob.data.materials.append(m.copy())
    attr = ob.data.attributes['MF_crown_edge_blend']
    max_relief = 0.
    for v in ob.data.vertices:
        x, y, z = v.co
        attr.data[v.index].value = smooth((z - hairline(x, y) + .06) / .12) * (1 - smooth((y + .05) / .4))
        d = relief(x, y, z, candidate)
        v.co += v.normal * d
        max_relief = max(max_relief, d)
    ob.data.update()
    # Source painted color retained. No procedural strand pattern and no new
    # fiber layer. Modest emission avoids doubling the painted lighting.
    if candidate >= 2:
        # The historical cleaned scalp atlas has warped, crinkled highlights.
        # Project the actual approved illustration onto frozen pre-relief UVs
        # instead of treating that derivative atlas as appearance authority.
        mat = bpy.data.materials.new('MF_approved_illustration_hair_section')
        mat.use_nodes = True
        n, links = mat.node_tree.nodes, mat.node_tree.links
        p = n.get('Principled BSDF')
        tex = n.new('ShaderNodeTexImage')
        tex.image = bpy.data.images.load(str(REFBASE / 'frontal-v02-individualized.png'), check_existing=False)
        tex.image.pack()
        uv = ob.data.uv_layers.new(name='ApprovedFrontalProjection')
        for poly in ob.data.polygons:
            for li in poly.loop_indices:
                co = original.data.vertices[ob.data.loops[li].vertex_index].co
                uv.data[li].uv = (.238 * co.x + .5, .156 * co.z + .677)
        uvnode = n.new('ShaderNodeUVMap'); uvnode.uv_map = uv.name
        links.new(uvnode.outputs[0], tex.inputs['Vector'])
        links.new(tex.outputs['Color'], p.inputs['Base Color'])
        alpha = n.new('ShaderNodeAttribute'); alpha.attribute_name = attr.name
        rgb = n.new('ShaderNodeSeparateColor'); links.new(tex.outputs['Color'], rgb.inputs[0])
        brown = n.new('ShaderNodeMath'); brown.operation = 'GREATER_THAN'
        links.new(rgb.outputs['Red'], brown.inputs[0]); links.new(rgb.outputs['Blue'], brown.inputs[1])
        mask = n.new('ShaderNodeMath'); mask.operation = 'MULTIPLY'
        links.new(alpha.outputs['Fac'], mask.inputs[0]); links.new(brown.outputs[0], mask.inputs[1])
        links.new(mask.outputs[0], p.inputs['Alpha'])
        ob.data.materials.clear(); ob.data.materials.append(mat)
        for poly in ob.data.polygons:
            poly.material_index = 0
    images = []
    for m in ob.data.materials:
        n, links = m.node_tree.nodes, m.node_tree.links
        p = n.get('Principled BSDF')
        if p is None or not p.inputs['Base Color'].is_linked:
            raise ValueError('Expected original illustrated material')
        color = p.inputs['Base Color'].links[0].from_socket
        links.new(color, p.inputs['Emission Color'])
        p.inputs['Emission Strength'].default_value = .18
        p.inputs['Roughness'].default_value = .85
        p.inputs['Specular IOR Level'].default_value = .05
        images.extend({'name': q.image.name, 'size': list(q.image.size)} for q in n if q.type == 'TEX_IMAGE' and q.image)
    locks = sculpted_locks(ob.data.materials[0]) if candidate == 3 else 0
    if candidate == 4:
        locks = wrapped_locks(ob.data.materials[0])
        # A subdued foundation, not a second visible illustration competing
        # with the rounded locks. Retain hair-only mask and original geometry.
        for m in ob.data.materials:
            n, links = m.node_tree.nodes, m.node_tree.links
            p = n.get('Principled BSDF'); color = p.inputs['Base Color'].links[0].from_socket
            shade = n.new('ShaderNodeMixRGB'); shade.blend_type = 'MULTIPLY'
            shade.inputs[0].default_value = 1; shade.inputs[2].default_value = (.14, .14, .14, 1)
            links.new(color, shade.inputs[1]); links.new(shade.outputs[0], p.inputs['Base Color'])
            links.new(shade.outputs[0], p.inputs['Emission Color'])
    return {'vertices': len(ob.data.vertices), 'max_relief': max_relief, 'broad_locks': locks,
            'images': images, 'single_visible_hair_surface': candidate < 3,
            'scope': 'forehead crown and upper temples only; rear and lower lengths unfinished'}


def sculpted_locks(material):
    """Few rounded locks following actual broad sweeps in approved front image.

    Their UVs follow those same image curves. No generated bitmap, repeated
    generic hair tile, or unrelated fiber shader is introduced.
    """
    import bpy
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    from hair_anatomy_refinement import spline
    body = bpy.data.objects['MF_continuous_head_neck']
    tree = BVHTree.FromObject(body, bpy.context.evaluated_depsgraph_get())
    guides = [
        ([(476,310,0),(431,321,0),(383,375,0),(299,412,0),(239,410,0)], 14, .073),
        ([(478,289,0),(427,279,0),(354,307,0),(289,360,0),(233,389,0)], 20, .100),
        ([(482,266,0),(435,240,0),(366,251,0),(295,306,0),(241,342,0)], 18, .070),
        ([(356,361,0),(321,414,0),(284,453,0),(246,477,0),(228,521,0)], 14, .085),
        ([(288,446,0),(268,477,0),(258,516,0),(242,545,0),(251,563,0)], 8, .055),
    ]
    count = 0
    for side in (-1, 1):
        for idx, (guide, width, height) in enumerate(guides):
            verts, faces, texcoords = [], [], []
            ns, nw = 56, 12
            for i in range(ns + 1):
                t = i / ns
                point = Vector(spline(guide, t))
                tangent = Vector(spline(guide, min(1, t + .001))) - Vector(spline(guide, max(0, t - .001)))
                tangent.normalize()
                perpendicular = Vector((-tangent.y, tangent.x, 0))
                taper = .12 + .88 * math.sin(math.pi * t) ** .5
                for j in range(nw + 1):
                    w = -1 + 2 * j / nw
                    pixel = point + perpendicular * width * taper * w
                    px = pixel.x if side == -1 else 977 - pixel.x
                    pz = pixel.y + (3 * math.sin(t * 5) if side == 1 else 0)
                    x = (px / 955 - .5) / .238
                    z = (1 - pz / 1647 - .677) / .156
                    hit, normal, _, _ = tree.ray_cast(Vector((x, -3, z)), Vector((0, 1, 0)))
                    if hit is None:
                        hit, normal, _, dist = tree.find_nearest(Vector((x, -.35, z)))
                        if hit is None or dist > .6:
                            raise ValueError('Guide outside bounded head neighborhood')
                        # Keep the original illustrated silhouette; use nearest
                        # scalp depth only where a swept lock exceeds the head.
                    y = hit.y - .035 - height * max(0, 1 - w * w) * math.sin(math.pi * t) ** .4
                    verts.append((x, y, z))
                    texcoords.append((px / 955, 1 - pz / 1647))
            for i in range(ns):
                for j in range(nw):
                    a = i * (nw + 1) + j
                    faces.append((a, a + 1, a + nw + 2, a + nw + 1))
            mesh = bpy.data.meshes.new(f'MF_illustrated_hair_lock_{side}_{idx}')
            mesh.from_pydata(verts, [], faces); mesh.update()
            ob = bpy.data.objects.new(mesh.name, mesh); bpy.context.scene.collection.objects.link(ob)
            mat = material.copy(); mat.name = mesh.name + '_material'; mesh.materials.append(mat)
            uv = mesh.uv_layers.new(name='ApprovedFrontalProjection')
            alpha = mesh.attributes.new('MF_crown_edge_blend', 'FLOAT', 'POINT')
            for i, a in enumerate(alpha.data):
                row, col = divmod(i, nw + 1)
                a.value = smooth(min(col, nw - col) / 1.7) * smooth(min(row, ns - row) / 3)
            for p in mesh.polygons:
                p.use_smooth = True
                for li in p.loop_indices:
                    uv.data[li].uv = texcoords[mesh.loops[li].vertex_index]
            count += 1
    return count


def wrapped_x(x):
    if abs(x) <= .9:
        return x
    return math.copysign(.9 + .15 * (1 - math.exp(-(abs(x) - .9) / .15)), x)


def wrapped_locks(material):
    """Geometry-hypothesis reassessment: loft smooth rounded swept-back locks.

    One bounded correction after the three projection previews, not an
    open-ended variant sweep. Avoid per-edge ray discontinuities and outward
    card ends. The retained frontal reference supplies all painted detail.
    """
    import bpy
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    from hair_anatomy_refinement import spline
    body = bpy.data.objects['MF_continuous_head_neck']
    tree = BVHTree.FromObject(body, bpy.context.evaluated_depsgraph_get())
    guides = [
        ([(484,315,0),(441,315,0),(389,366,0),(299,409,0),(237,441,0)], 18, .10),
        ([(482,294,0),(427,275,0),(360,308,0),(282,369,0),(235,406,0)], 24, .14),
        ([(480,266,0),(434,238,0),(364,253,0),(290,312,0),(242,361,0)], 24, .12),
        ([(475,242,0),(433,218,0),(371,234,0),(309,273,0),(257,322,0)], 19, .10),
        ([(368,361,0),(329,415,0),(287,454,0),(251,494,0),(248,550,0)], 14, .09),
        ([(315,408,0),(287,457,0),(267,506,0),(253,549,0),(260,580,0)], 11, .07),
    ]
    count = 0
    for side in (-1, 1):
        for idx, (guide, width, height) in enumerate(guides):
            # Surface depth sampled only at the sparse guide centers, then
            # interpolated smoothly. Width never inherits nearest-hit jumps.
            centers = []
            for k, (px0, py, _) in enumerate(guide):
                px = px0 if side == -1 else 977 - px0
                x = wrapped_x((px / 955 - .5) / .238)
                z = (1 - py / 1647 - .677) / .156
                hit, normal, _, _ = tree.ray_cast(Vector((x, -3, z)), Vector((0, 1, 0)))
                if hit is None:
                    hit, normal, _, dist = tree.find_nearest(Vector((x, -.3, z)))
                    if hit is None or dist > .6:
                        raise ValueError('Wrapped guide outside head')
                t = k / (len(guide) - 1)
                y = hit.y - .050 + .56 * smooth((t - .48) / .52)
                z -= .10 * smooth((t - .60) / .40)
                centers.append((x, y, z))
            verts, faces, texcoords = [], [], []
            ns, nw = 64, 16
            for i in range(ns + 1):
                t = i / ns
                c = Vector(spline(centers, t)); imagepoint = Vector(spline(guide, t))
                tangent = Vector(spline(centers, min(1, t + .001))) - Vector(spline(centers, max(0, t - .001)))
                tangent.normalize()
                # Rotate outward normal toward the temple and rear as the
                # lock sweeps back, rather than leaving flat frontal cards.
                normal = Vector((side * smooth((abs(c.x) - .35) / .65), -1 + 1.2 * smooth((t - .5) / .5), .22))
                normal.normalize(); across = tangent.cross(normal).normalized()
                itangent = Vector(spline(guide, min(1, t + .001))) - Vector(spline(guide, max(0, t - .001)))
                itangent.normalize(); iperp = Vector((-itangent.y, itangent.x, 0))
                taper = max(.015, math.sin(math.pi * t) ** .40)
                for j in range(nw + 1):
                    w = -1 + 2 * j / nw
                    co = c + across * (width / 955 / .238) * taper * w + normal * height * taper * math.sqrt(max(0, 1 - w * w))
                    verts.append(tuple(co))
                    ip = imagepoint + iperp * width * w * taper
                    px = ip.x if side == -1 else 977 - ip.x
                    texcoords.append((px / 955, 1 - ip.y / 1647))
            for i in range(ns):
                for j in range(nw):
                    a = i * (nw + 1) + j
                    faces.append((a, a + 1, a + nw + 2, a + nw + 1))
            mesh = bpy.data.meshes.new(f'MF_illustrated_hair_volume_{side}_{idx}')
            mesh.from_pydata(verts, [], faces); mesh.update()
            ob = bpy.data.objects.new(mesh.name, mesh); bpy.context.scene.collection.objects.link(ob)
            mat = material.copy(); mesh.materials.append(mat)
            n, links = mat.node_tree.nodes, mat.node_tree.links
            p = n.get('Principled BSDF')
            color = p.inputs['Base Color'].links[0].from_socket
            shade = n.new('ShaderNodeMixRGB'); shade.blend_type = 'MULTIPLY'
            shade.inputs[0].default_value = 1; shade.inputs[2].default_value = (.65, .65, .65, 1)
            links.new(color, shade.inputs[1]); links.new(shade.outputs[0], p.inputs['Base Color'])
            links.new(shade.outputs[0], p.inputs['Emission Color'])
            uv = mesh.uv_layers.new(name='ApprovedFrontalProjection')
            alpha = mesh.attributes.new('MF_crown_edge_blend', 'FLOAT', 'POINT')
            for i, a in enumerate(alpha.data):
                row, col = divmod(i, nw + 1)
                a.value = smooth(min(col, nw - col) / 1.3) * smooth(min(row, ns - row) / 2)
            for p in mesh.polygons:
                p.use_smooth = True
                for li in p.loop_indices:
                    uv.data[li].uv = texcoords[mesh.loops[li].vertex_index]
            count += 1
    return count


def run(job):
    out = validate(job)
    out.mkdir()
    import bpy
    from hair_anatomy_refinement import visibility
    from hijab_donor import review
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE), load_ui=False, use_scripts=False)
    before = protection()
    changes = build(job['candidate'])
    assert protection() == before, 'Non-hair change'
    visibility()
    scene = bpy.context.scene
    review(scene, out, (0, -.05, .13), 3.5, (('front', 0), ('left', -45), ('right', 45)))
    result = {'candidate': job['candidate'], 'operation': job['operation'],
              'reference_authority': REFERENCES, 'technical_source_sha256': SOURCE_SHA,
              'handler_sha256': digest(Path(__file__)), 'protected_exact': protection() == before,
              'changes': changes, 'director_acceptance': 'PENDING', 'full_groom_qualified': False}
    assert result['protected_exact']
    if job['operation'] == 'seal':
        for im in bpy.data.images:
            if im.source == 'FILE' and not (im.packed_file or im.packed_files):
                im.pack()
        native = out / 'illustrated-hair-section.blend'
        bpy.ops.wm.save_as_mainfile(filepath=str(native))
        bpy.ops.wm.open_mainfile(filepath=str(native), load_ui=False, use_scripts=False)
        result['fresh_reopen_protected_exact'] = protection() == before
        assert result['fresh_reopen_protected_exact']
        result['native_sha256'] = digest(native)
    assert digest(SOURCE) == SOURCE_SHA
    (out / 'result.json').write_text(json.dumps(result, indent=2))


if __name__ == '__main__':
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    args = sys.argv[sys.argv.index('--') + 1:]
    if len(args) != 1:
        raise ValueError('One structured job required')
    run(json.loads(Path(args[0]).read_text()))
