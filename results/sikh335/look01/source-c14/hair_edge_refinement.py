"""Pinned, front-only hair-edge feathering and rooted strands. No skin edits."""
import hashlib
import json
import math
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / '.runtime/art-direction/series01-facebuilder-trial-01'
SOURCE = BASE / 'frontfit-package-03/hair-front-fit.blend'
SOURCE_SHA = 'd099165e5c7803f0cb0d801f8ec52353ab41ab5c41a283f8589366d6ce627d87'
REFERENCES = {
    'frontal-v02-individualized.png': '7f959fed6ca4f57cb1b7fdaa20aa4a0fdd64208595a8b5debd8d060c79068c75',
    'portrait-v07-individualized.png': 'e6afc72b56fa57642b521fd7a922894d81a900b8cab0103f7c3f2cfb39a795f1',
}
REFBASE = ROOT / '.runtime/art-direction/series01-pashtun-baseline-v01'


def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def smooth(t):
    t = max(0., min(1., t))
    return t*t*(3-2*t)


def validate(job):
    if not isinstance(job, dict) or set(job) != {'operation', 'candidate'}:
        raise ValueError('Exact structured keys required')
    if job['operation'] not in ('preview', 'package') or type(job['candidate']) is not int or job['candidate'] not in (1, 2, 3):
        raise ValueError('Unsupported fixed operation')
    for p, h in [(SOURCE, SOURCE_SHA), *[(REFBASE/n, h) for n, h in REFERENCES.items()]]:
        if p.is_symlink() or digest(p) != h:
            raise ValueError('Pinned input changed')
    out = BASE / f'edge-{job["operation"]}-{job["candidate"]:02}'
    if out.exists() or out.is_symlink() or out.resolve().parent != BASE.resolve():
        raise ValueError('Output exists or escapes')
    if shutil.disk_usage(BASE).free < 5_000_000_000:
        raise ValueError('Disk low')
    if job['operation'] == 'package':
        p = BASE / f'edge-preview-{job["candidate"]:02}/result.json'
        if p.is_symlink() or not p.is_file():
            raise ValueError('Preview required')
        r = json.loads(p.read_text())
        if r.get('handler_sha256') != digest(Path(__file__)) or not r.get('protected_exact') or not r.get('base_geometry_exact'):
            raise ValueError('Stale preview or failed protection')
    return out


def opacity(x, y, z, edge, candidate):
    """Feather only a narrow frontal band, not the crown or rear surface."""
    width = (.055, .080, .065)[candidate-1]
    variation = .010*math.sin(37*x+.6)+.005*math.sin(89*x+1.3)
    feather = smooth((z-edge-variation+.006)/width)
    active = (1-smooth((y+.50)/.22))*(1-smooth((abs(x)-.74)/.10))
    return 1-active*(1-feather)


def temple_opacity(angle, z, edge, candidate):
    width = .060 if candidate == 2 else .065
    variation = .009*math.sin(39*angle+.6)+.004*math.sin(97*angle+1.3)
    active = 1-smooth((abs(angle)-1.35)/.15)
    return 1-active*(1-smooth((z-edge-variation+.006)/width))


def base_signature():
    import bpy
    return digest_bytes([(o.name, tuple(tuple(v.co) for v in o.data.vertices),
                          tuple(tuple(p.vertices) for p in o.data.polygons),
                          tuple(tuple(r) for r in o.matrix_world))
                         for o in sorted(bpy.context.scene.objects, key=lambda o:o.name)
                         if o.type == 'MESH' and not o.hide_render and 'hair' in o.name.lower()])


def digest_bytes(value):
    return hashlib.sha256(repr(value).encode()).hexdigest()


def build(candidate):
    import bpy
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    base = bpy.data.objects['MF_sculpt_hair_support']
    body = bpy.data.objects['MF_continuous_head_neck']
    assert base.matrix_world.is_identity and body.matrix_world.is_identity
    deps = bpy.context.evaluated_depsgraph_get()
    hairtree, bodytree = BVHTree.FromObject(base, deps), BVHTree.FromObject(body, deps)
    samples = []
    for i in range(169):
        x = -.84+i*.01
        edge = None
        for j in range(281):
            z = -.15+j*.005
            h, _, _, _ = hairtree.ray_cast(Vector((x,-3,z)), Vector((0,1,0)))
            b, _, _, _ = bodytree.ray_cast(Vector((x,-3,z)), Vector((0,1,0)))
            if h is not None and b is not None and h.y < b.y-.001:
                edge = z
                break
        if edge is None:
            raise ValueError('Front boundary sample missing')
        samples.append(edge)

    def edge_at(x):
        pos = max(0., min(167.999, (x+.84)/.01))
        i = int(pos); t = pos-i
        return samples[i]*(1-t)+samples[i+1]*t

    angular = []
    if candidate >= 2:
        for i in range(121):
            angle = -1.5+i*.025
            direction = Vector((math.sin(angle),-math.cos(angle),0))
            edge = None
            for j in range(321):
                z = -.3+j*.005
                origin = direction*3+Vector((0,0,z))
                h, _, _, _ = hairtree.ray_cast(origin,-direction)
                b, _, _, _ = bodytree.ray_cast(origin,-direction)
                if h is not None and b is not None and (h-b).dot(direction)>.001:
                    edge = z; break
            if edge is None: raise ValueError('Temple boundary sample missing')
            angular.append(edge)

    def angular_edge(angle):
        pos = max(0.,min(119.999,(angle+1.5)/.025))
        i = int(pos); t = pos-i
        return angular[i]*(1-t)+angular[i+1]*t

    attr = base.data.attributes.new('MF_front_edge_opacity', 'FLOAT', 'POINT')
    changed = 0
    for v in base.data.vertices:
        x,y,z = v.co
        a = opacity(x,y,z,edge_at(x),candidate)
        if candidate >= 2:
            angle = math.atan2(x,-y)
            a = temple_opacity(angle,z,angular_edge(angle),candidate)
        attr.data[v.index].value = a
        changed += a < .999
    # Clone only this object's materials; shared rear material stays exact.
    for i, source in enumerate(list(base.data.materials)):
        mat = source.copy(); mat.name = f'MF_hair_feathered_edge_{i}'
        base.data.materials[i] = mat
        nodes, links = mat.node_tree.nodes, mat.node_tree.links
        output = next(n for n in nodes if n.type == 'OUTPUT_MATERIAL')
        old_surface = output.inputs['Surface'].links[0].from_socket
        attribute = nodes.new('ShaderNodeAttribute'); attribute.attribute_name = attr.name
        transparent = nodes.new('ShaderNodeBsdfTransparent')
        mix = nodes.new('ShaderNodeMixShader')
        links.new(attribute.outputs['Fac'], mix.inputs[0])
        links.new(transparent.outputs[0], mix.inputs[1])
        links.new(old_surface, mix.inputs[2]); links.new(mix.outputs[0], output.inputs['Surface'])
    hidden = []
    for ob in bpy.context.scene.objects:
        if ob.name.startswith('MF_hair_front_edge_'):
            ob.hide_render = True; hidden.append(ob.name)
    # Thin, uneven curved wisps follow the sweeps instead of standing upright.
    mats = []
    for i, color in enumerate(((.021,.008,.003,1),(.036,.016,.007,1),(.061,.030,.013,1))):
        mat = bpy.data.materials.new(f'MF_hair_root_wisp_{i}'); mat.use_nodes = True
        p = mat.node_tree.nodes.get('Principled BSDF')
        p.inputs['Base Color'].default_value = color
        p.inputs['Roughness'].default_value = .78
        p.inputs['Specular IOR Level'].default_value = .10
        mats.append(mat)
    count = (36,66,46)[candidate-1]
    strands = []
    for side in (-1,1):
        for i in range(count):
            x = side*(.035+.70*i/(count-1)+.008*math.sin(i*2.17+side))
            root = edge_at(x)+.055+.025*(.5+.5*math.sin(i*1.9))
            travel = .045+.045*(.5+.5*math.sin(i*2.6+.4))
            drop = .025+.027*(.5+.5*math.sin(i*1.3+side))
            curve = bpy.data.curves.new(f'MF_hair_edge_wisp_{side}_{i}', 'CURVE')
            curve.dimensions = '3D'; curve.bevel_resolution = 2
            curve.bevel_depth = .0012+.0011*(.5+.5*math.sin(i*1.7))
            poly = curve.splines.new('POLY'); poly.points.add(16)
            for j, point in enumerate(poly.points):
                t = j/16
                px = x+side*travel*t
                pz = (root*(1-t)+(edge_at(px)-drop)*t)+.018*math.sin(math.pi*t)
                ray_origin, ray_dir = Vector((px,-3,pz)), Vector((0,1,0))
                if candidate >= 2:
                    angle0 = side*(.025+1.29*i/(count-1)+.007*math.sin(i*2.17+side))
                    angle = angle0+side*(.035+.025*math.sin(i*.7)**2)*t
                    rz = angular_edge(angle0)+.06+.018*math.sin(i*1.9)**2
                    if candidate == 3:
                        # Fewer, longer swept strokes: avoid a vertical fringe
                        # while following the diagonal brushwork in pair B.
                        angle0 = side*(.025+1.18*i/(count-1)+.009*math.sin(i*2.17+side))
                        angle = angle0+side*(.115+.080*math.sin(i*.7)**2)*t
                        rz = angular_edge(angle0)+.047+.019*math.sin(i*1.9)**2
                        drop = .008+.019*math.sin(i*1.3+side)**2
                    pz = rz*(1-t)+(angular_edge(angle)-drop)*t+.015*math.sin(math.pi*t)
                    ray_dir = Vector((-math.sin(angle),math.cos(angle),0))
                    ray_origin = -ray_dir*3+Vector((0,0,pz))
                b, _, _, _ = bodytree.ray_cast(ray_origin,ray_dir)
                h, _, _, _ = hairtree.ray_cast(ray_origin,ray_dir)
                if b is None: raise ValueError('Strand projection missing')
                if candidate >= 2:
                    co = b.copy()
                    if h is not None and (h-b).dot(-ray_dir)>0:
                        a = temple_opacity(angle,pz,angular_edge(angle),candidate)
                        co = b*(1-a)+h*a
                    co -= ray_dir*(.0015+.003*math.sin(math.pi*t))
                    point.co = (*co,1)
                    point.radius = (.60+.40*math.sin(math.pi*t))*(1-t)**.60
                    continue
                py = b.y
                if h is not None and h.y < b.y:
                    # Follow the attenuated shell without a floating fringe.
                    a = opacity(px,h.y,pz,edge_at(px),candidate)
                    py = b.y*(1-a)+h.y*a
                point.co = (px,py-.0015-.003*math.sin(math.pi*t),pz,1)
                point.radius = (.60+.40*math.sin(math.pi*t))*(1-t)**.60
            ob = bpy.data.objects.new(curve.name,curve); bpy.context.scene.collection.objects.link(ob)
            curve.materials.append(mats[i%3]); strands.append(ob.name)
    return {'feathered_vertices':changed,'new_curved_strands':len(strands),
            'hidden_prior_straight_wisps':hidden,'max_feather_width':(.055,.060,.065)[candidate-1],
            'geometry_changed':False,'source_texture_images_changed':False,
            'boundary_samples':samples,'angular_boundary_samples':angular,
            'qualification':'STATIC_ONLY_NOT_MOTION_TESTED'}


def run(job):
    out = validate(job); out.mkdir(); shutil.copyfile(Path(__file__),out/'handler-source.py')
    import bpy
    from illustrated_hair_section import protection
    from hair_anatomy_refinement import visibility
    from hijab_donor import review
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE),load_ui=False,use_scripts=False)
    before, geometry = protection(), base_signature()
    info = build(job['candidate']); visibility()
    assert protection() == before and base_signature() == geometry
    review(bpy.context.scene,out,(0,0,-.03),3.8,(('front',0),('left',-45),('right',45),('back',180)))
    result = {'candidate':job['candidate'],'source_sha256':SOURCE_SHA,'reference_authority':REFERENCES,
              'handler_sha256':digest(Path(__file__)),'protected_exact':protection()==before,
              'base_geometry_exact':base_signature()==geometry,'changes':info,
              'clothing_rendered':False,'director_acceptance':'PENDING'}
    if job['operation'] == 'package':
        review(bpy.context.scene,out,(0,0,-.03),3.8,(('portrait-front',0),('portrait-left',-45),('portrait-right',45)),portrait=True)
        native = out/'hair-edge.blend'; bpy.ops.wm.save_as_mainfile(filepath=str(native))
        bpy.ops.wm.open_mainfile(filepath=str(native),load_ui=False,use_scripts=False)
        result['fresh_reopen_protected_exact'] = protection()==before and base_signature()==geometry
        assert result['fresh_reopen_protected_exact']
        result['native_sha256'] = digest(native)
    assert protection()==before and base_signature()==geometry and digest(SOURCE)==SOURCE_SHA
    (out/'result.json').write_text(json.dumps(result,indent=2)+'\n')


if __name__ == '__main__':
    sys.path.insert(0,str(Path(__file__).resolve().parent))
    args = sys.argv[sys.argv.index('--')+1:]
    if len(args)!=1: raise ValueError('One fixed job required')
    run(json.loads(Path(args[0]).read_text()))
