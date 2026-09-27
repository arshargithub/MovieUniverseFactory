"""Fixed reference-led finishing operations on the preserved integrated groom.

Data-only jobs; no provider calls, runtime code strings or source overwrites.
"""
import hashlib
import json
import math
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / '.runtime/art-direction/series01-facebuilder-trial-01'
SOURCE = BASE / 'integrated24-surface-seal-23/integrated-hair.blend'
SOURCE_SHA = 'bbadab6723e31824df869ddd49dfb69160da0da85612fc0d8b9b6ab63dacb591'
REF = ROOT / '.runtime/art-direction/series01-pashtun-uncovered-v01'
ORIGINAL_REF = ROOT / '.runtime/art-direction/series01-pashtun-baseline-v01'
ORIGINAL_PINS = {
    'frontal-v02-individualized.png': '7f959fed6ca4f57cb1b7fdaa20aa4a0fdd64208595a8b5debd8d060c79068c75',
    'portrait-v07-individualized.png': 'e6afc72b56fa57642b521fd7a922894d81a900b8cab0103f7c3f2cfb39a795f1',
}
PINS = {
    'front-uncovered-v01.png': '3344c7d880fb6b50f46e9af268790be2772863c6cca0db2cdd83ea54d216f8f6',
    'three-quarter-screen-right-uncovered-v01.png': 'd8b3e07494b0ac6f3fd0233d5463d03ae98cb5a7b50b23a2b1588be146c09dfc',
    'three-quarter-screen-left-uncovered-v01.png': '73ea1adb291f98d4d5b82c4160318db065ab268d1f916b38d362bbb5596ddccc',
    'back-uncovered-v01.png': 'd9357b9baf5da1b821288cdd27938d07871d83ffbaefe643e6585b590e71b085',
}
NAME = 'MF_integrated24_hair_painted'
MAIN = 'MF_integrated24_hair_long hair main'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(job):
    if (not isinstance(job, dict) or set(job) != {'operation', 'candidate'}
            or job['operation'] not in ('preview', 'seal', 'verify', 'audit')
            or type(job['candidate']) is not int or job['candidate'] not in tuple(range(1, 19))):
        raise ValueError('Fixed uncovered finish job required')
    for p, h in [(SOURCE, SOURCE_SHA), *[(REF/n, h) for n, h in PINS.items()],
                 *[(ORIGINAL_REF/n,h) for n,h in ORIGINAL_PINS.items()]]:
        if p.is_symlink() or digest(p) != h:
            raise ValueError('Pinned source/reference changed')
    out = BASE / f'finalhair142-{job["operation"]}-{job["candidate"]:02}'
    if out.exists() or out.is_symlink() or out.resolve().parent != BASE.resolve():
        raise ValueError('Fresh confined output required')
    if shutil.disk_usage(BASE).free < 5_000_000_000:
        raise ValueError('Insufficient disk')
    if job['operation'] in ('seal', 'verify'):
        stage = 'preview' if job['operation'] == 'seal' else 'seal'
        folder = BASE/f'finalhair142-{stage}-{job["candidate"]:02}'
        result = folder/'result.json'
        if folder.is_symlink() or result.is_symlink() or not result.is_file():
            raise ValueError('Prerequisite missing')
        record = json.loads(result.read_text())
        if (not record['protected_exact'] or record.get('candidate') != job['candidate']
                or record.get('handler_sha256') != digest(Path(__file__))):
            raise ValueError('Protection, candidate or current handler binding failed')
        if stage == 'seal':
            native = folder/'finished-hair.blend'
            if native.is_symlink() or digest(native) != record['native_sha256']:
                raise ValueError('Native changed')
    return out


def smooth(t):
    t = max(0., min(1., t))
    return t*t*(3-2*t)


def crown_offset(point, root, t, candidate):
    """Lift distinct upper lock families without moving roots or lower hair."""
    x,y,z=point
    if t>=.45 or z<=.55 or (t<=0 and candidate==13):
        return (0.,0.,0.)
    side=1 if x>=0 else -1
    if candidate>=16:
        # Connected crest; large independently lifted root bands made the
        # previous hypothesis scalloped. Small unequal overlaps sit on this
        # continuous profile instead of defining separate peaks.
        upper=smooth((z-.65)/.70)
        frontal=smooth((y+.82)/.4)*(1-smooth((y-.15)/.65))
        crest=.17*math.exp(-(x/.65)**2)*frontal*upper
        env=math.sin(math.pi*t/.45)**1.2
        overlap=.025*(1+math.sin(root[1]*7+side*.55))*env*upper
        overlap*=1-smooth((y-.1)/.5)
        return (0.,-.04*env*upper*(1-smooth((y-.1)/.5)),crest+overlap)
    envelope=math.sin(math.pi*t/.45)**1.2
    upper=smooth((z-.55)/.65)*(1-smooth((abs(x)-.7)/.6))
    rear=1-smooth((root[1]-.3)/.6)
    centers=(-.92,-.57,-.18,.25)
    heights=(.23,.29,.20,.25) if side<0 else (.27,.20,.30,.19)
    weights=[math.exp(-((root[1]-c)/.15)**2) for c in centers]
    lift=(.065+sum(h*w for h,w in zip(heights,weights)))*envelope*upper*rear
    # Neighbouring coherent root bands have different lift/depth. The
    # near-center part roots and the whole face/forehead remain untouched.
    depth=(.07+.035*math.sin(root[1]*8+side))*envelope*upper*rear
    if candidate>=14:
        # Upper part roots, unlike the frontal hairline, can lift with the
        # crest. Keeping all of them pinned made13's two detached humps.
        apex=(.14 if candidate>=15 else .24)*math.exp(-(x/.70)**2)*smooth((z-.75)/.65)
        apex*=smooth((y+.82)/.50)*(1-smooth((y-.5)/.5))
        apex*=1-smooth((t-.22)/.23)
        lift=.40*lift+apex
        depth*=.6
    return (side*.018*lift,-depth,lift)


def shape(point, candidate):
    """Continuous hair-only deformation, preserving frontal root positions."""
    x, y, z = point
    side = 1 if x >= 0 else -1
    front = 1-smooth((y+.12)/.75)
    temple = math.exp(-((z-.45)/.46)**2)*smooth((abs(x)-.53)/.32)*front
    # Reduce the theatrical outward flip without pinching roots onto the ear.
    x -= side*.095*temple
    z -= .13*temple
    y += .10*temple
    # Close the artificial mirrored rear split only behind the crown.
    rear = smooth((y-.05)/.60)
    center = math.exp(-(x/.32)**2)*smooth((z-.65)/.55)*rear
    x -= .045*math.tanh(x/.12)*center
    z += .08*center
    # Long waves form a connected continuation, not uniformly vertical fibers.
    lower = smooth((.35-z)/.90)
    wave = math.sin(z*5.8 + x*2.7 + y*1.1)
    x += lower*(.09*wave + side*.065*smooth((abs(x)-.50)/.5))
    y += lower*.10*math.sin(z*5.8+x*2.7+y*1.1+.9)
    if candidate >= 2:
        x += lower*.045*math.sin(z*10.5+x*4.2)
        y += lower*.035*math.sin(z*10.5+x*4.2+.5)
        x -= .10*math.tanh(x/.18)*rear*lower
    if candidate >= 3:
        x += lower*side*.035*smooth((abs(x)-.45)/.5)
    if candidate >= 5:
        flare = smooth((abs(x)-.75)/.35)*math.exp(-((z-.65)/.32)**2)*front
        x -= side*.105*flare
        z -= .07*flare
        x += side*.14*lower*smooth((abs(x)-.45)/.45)
    return x, y, z


def finish(candidate):
    import bpy
    import numpy as np
    ob = bpy.data.objects[NAME]
    values = np.empty(len(ob.data.points)*3, dtype=np.float32)
    ob.data.attributes['position'].data.foreach_get('vector', values)
    values = np.array([shape(p, candidate) for p in values.reshape(-1, 3)], dtype=np.float32)
    ob.data.attributes['position'].data.foreach_set('vector', values.ravel())
    if candidate >= 2:
        # Feathered high side ends created the clipped, wing-like silhouette.
        # Reorient only their free tips toward the reference's descending flow.
        for curve in ob.data.curves:
            for k, point in enumerate(curve.points):
                t = k/max(1, len(curve.points)-1)
                q = point.position.copy()
                weight = smooth((t-.45)/.5)*smooth((abs(q.x)-.70)/.3)*smooth((q.z-.10)/.35)
                q.z -= .23*weight
                q.x *= 1-.055*weight
                point.position = q
    if candidate == 6:
        # The source swept half curls upward again at the temple. The approved
        # loose hairstyle instead continues downward after its crown lift.
        # Remove that reversal per complete strand, not by pinching the scalp.
        for curve in ob.data.curves:
            limit = curve.points[8].position.z
            for k in range(9,len(curve.points)):
                q=curve.points[k].position.copy()
                limit=min(limit,q.z)
                q.z=min(q.z,limit+.008)
                curve.points[k].position=q
    if candidate >= 7:
        # Smooth whole-arc fitting, replacing6's rejected hard z constraint.
        for curve in ob.data.curves:
            if curve.points[0].position.y > .2:
                continue
            start=curve.points[8].position.copy();end=curve.points[32].position.copy()
            for k in range(9,32):
                t=(k-8)/24
                w=math.sin(math.pi*t)**2
                q=curve.points[k].position.copy();target=start.lerp(end,t)
                q.x=q.x*(1-.65*w)+target.x*(.65*w)
                q.z=q.z*(1-.70*w)+target.z*(.70*w)
                curve.points[k].position=q
    if candidate >= 8:
        for curve in ob.data.curves:
            for point in curve.points:
                q = point.position.copy()
                # Untucked face-framing fall, rather than the donor's backward
                # flip. Blend over the entire temporal arc to avoid a kink.
                w = smooth((abs(q.x)-.55)/.35)*math.exp(-((q.z-.15)/.60)**2)
                w *= 1-smooth((q.y-.05)/.65)
                q.z -= .25*w
                q.y -= .22*w
                q.x += (.05 if q.x>0 else -.05)*w
                # Overlap the two mirrored rear halves below the crown. The
                # front center part remains untouched, and roots stay editable.
                rear=smooth((q.y-.15)/.5)*smooth((q.z+.1)/.5)
                q.x -= .16*math.tanh(q.x/.10)*math.exp(-(q.x/.55)**2)*rear
                point.position=q
    if candidate >= 9:
        for curve in ob.data.curves:
            root = curve.points[0].position.copy()
            front = 1-smooth((root.y+.65)/.50)
            for k, point in enumerate(curve.points):
                q=point.position.copy()
                fall=smooth((k-8)/24)*front
                # Bring the long face-framing locks forward, instead of
                # retaining a short front sweep above an unrelated rear mass.
                q.y-=.75*fall
                q.x+=(.14 if q.x>0 else -.14)*fall
                q.z-=.14*math.sin(math.pi*min(1,k/40))*front
                point.position=q
    if candidate == 10:
        for curve in ob.data.curves:
            points=np.array([tuple(p.position) for p in curve.points])
            root=points[0].copy()
            front=1-smooth((root[1]+.65)/.50)
            for k in range(len(points)):
                t=k/(len(points)-1)
                points[k,2]-=.28*smooth((t-.50)/.40)*front
            for _ in range(8):
                points[1:-1]=(points[:-2]+2*points[1:-1]+points[2:])/4
            for p,q in zip(curve.points,points):p.position=q
    if candidate >= 11:
        offset=0
        for curve in ob.data.curves:
            original=values[offset:offset+len(curve.points)].copy()
            offset+=len(curve.points)
            front=1-smooth((original[0,1]+.45)/.70)
            if front <= 0:continue
            start=original[8].copy(); end=original[40].copy()
            side=1 if start[0]>0 else -1
            goal=end.copy();goal[0]=side*(1.04+.12*abs(end[0]));goal[1]=-.20+.15*original[0,1]
            goal[2]=min(end[2],-.70)
            shift=goal-end
            for k in range(8,len(curve.points)):
                if k<=40:
                    t=(k-8)/32
                    target=start*(1-t)+goal*t
                    target[0]+=side*.13*math.sin(math.pi*t)
                    if candidate >= 12:
                        phase=original[0,1]*1.8+original[0,2]
                        target[0]+=side*.13*math.sin(t*math.pi*2.3+phase)*math.sin(math.pi*t)
                        target[1]+=.10*math.sin(t*math.pi*2.3+phase+.8)*math.sin(math.pi*t)
                else:
                    target=original[k]+shift
                original[k]=original[k]*(1-front)+target*front
            for _ in range(10):
                original[1:-1]=(original[:-2]+2*original[1:-1]+original[2:])/4
            for p,q in zip(curve.points,original):p.position=q
        if candidate >= 12:
            for curve in ob.data.curves:
                for point in curve.points:
                    q=point.position.copy()
                    rear=smooth((q.y-.15)/.5)*smooth((q.z+.1)/.5)
                    q.x-=.16*math.tanh(q.x/.10)*math.exp(-(q.x/.55)**2)*rear
                    point.position=q
    if candidate >= 13:
        for curve in ob.data.curves:
            root=tuple(curve.points[0].position)
            for k,p in enumerate(curve.points):
                q=p.position.copy()
                delta=crown_offset(q,root,k/(len(curve.points)-1),candidate)
                p.position=tuple(a+b for a,b in zip(q,delta))
    ob.data.update_tag()
    # Keep live native curves and a single material language. Use the now
    # approved uncovered source, not scarf/skin pixels from the hooded portrait.
    mat = ob.data.materials[0]
    for node in mat.node_tree.nodes:
        if node.type == 'TEX_IMAGE':
            node.image = bpy.data.images.load(str(REF/'front-uncovered-v01.png'), check_existing=True)
    # Remove orange skin from the crown projection by tightening its existing
    # linear-red validity threshold; preserve original input images verbatim.
    for node in mat.node_tree.nodes:
        if node.type == 'MATH' and node.operation == 'LESS_THAN' and not node.inputs[1].is_linked:
            if abs(node.inputs[1].default_value-.42) < .001:
                node.inputs[1].default_value = .19
        if candidate >= 2 and node.type == 'MATH' and node.operation == 'SUBTRACT' and not node.inputs[0].is_linked:
            if abs(node.inputs[0].default_value-542) < .01:
                node.inputs[0].default_value = 500
    if candidate >= 3:
        root_foundation()
    if candidate >= 4:
        uncovered_material(mat, candidate)
    return ob


def uncovered_material(mat, candidate):
    """Regional reference coordinates on native strands, not composited renders."""
    import bpy
    nodes, links = mat.node_tree.nodes, mat.node_tree.links
    nodes.clear()
    output = nodes.new('ShaderNodeOutputMaterial')
    p = nodes.new('ShaderNodeBsdfPrincipled')
    p.inputs['Roughness'].default_value = .95
    p.inputs['Specular IOR Level'].default_value = 0
    p.inputs['Emission Strength'].default_value = .40 if candidate>=15 else .60
    links.new(p.outputs[0], output.inputs['Surface'])
    def mathnode(op, a, b=None):
        node=nodes.new('ShaderNodeMath');node.operation=op
        for i,v in enumerate((a,b)):
            if v is None:continue
            if isinstance(v,(int,float)):node.inputs[i].default_value=v
            else:links.new(v,node.inputs[i])
        return node.outputs[0]
    def mix(factor,a,b):
        node=nodes.new('ShaderNodeMixRGB')
        for i,v in enumerate((factor,a,b)):
            if isinstance(v,(int,float,tuple)):node.inputs[i].default_value=v
            else:links.new(v,node.inputs[i])
        return node.outputs[0]
    xyz=nodes.new('ShaderNodeSeparateXYZ');geo=nodes.new('ShaderNodeNewGeometry')
    links.new(geo.outputs['Position'],xyz.inputs[0])
    x,y,z=xyz.outputs['X'],xyz.outputs['Y'],xyz.outputs['Z']
    attr=nodes.new('ShaderNodeAttribute');attr.attribute_name='MF_paint'
    fallback=mix(.45,attr.outputs['Color'],(.007,.0028,.0014,1))
    def project(name,scale,offset,slope):
        vec=nodes.new('ShaderNodeCombineXYZ')
        u=mathnode('DIVIDE',mathnode('ADD',477,mathnode('MULTIPLY',x,scale)),955)
        v=mathnode('SUBTRACT',1,mathnode('DIVIDE',mathnode('SUBTRACT',offset,mathnode('MULTIPLY',z,slope)),1647))
        links.new(u,vec.inputs[0]);links.new(v,vec.inputs[1])
        tex=nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(REF/name),check_existing=True)
        links.new(vec.outputs[0],tex.inputs[0])
        rgb=nodes.new('ShaderNodeSeparateColor');links.new(tex.outputs[0],rgb.inputs[0])
        valid=mathnode('MULTIPLY',mathnode('LESS_THAN',rgb.outputs['Red'],.24),mathnode('GREATER_THAN',rgb.outputs['Red'],mathnode('MULTIPLY',rgb.outputs['Green'],1.18)))
        valid=mathnode('MULTIPLY',valid,mathnode('GREATER_THAN',rgb.outputs['Red'],mathnode('MULTIPLY',rgb.outputs['Blue'],1.35)))
        return mix(valid,fallback,tex.outputs[0])
    front=project('front-uncovered-v01.png',260,570 if candidate>=15 else 650,265 if candidate>=15 else 350)
    rear=project('back-uncovered-v01.png',-230,675,280)
    frontweight=mathnode('MINIMUM',1,mathnode('MAXIMUM',0,mathnode('DIVIDE',mathnode('SUBTRACT',.10,y),.70)))
    rearweight=mathnode('MINIMUM',1,mathnode('MAXIMUM',0,mathnode('DIVIDE',mathnode('SUBTRACT',y,.05),.65)))
    if candidate >= 5:
        # Reject the full portrait projection: shaded marks crossed the real
        # flow and copied face detail at temples. Keep only safe upper crown.
        height=mathnode('MINIMUM',1,mathnode('MAXIMUM',0,mathnode('DIVIDE',mathnode('SUBTRACT',z,.30 if candidate>=17 else .65),.50 if candidate>=17 else .45)))
        frontweight=mathnode('MULTIPLY',frontweight,height)
        rearweight=0.
    color=mix(frontweight,fallback,front)
    color=mix(rearweight,color,rear)
    links.new(color,p.inputs['Base Color']);links.new(color,p.inputs['Emission Color'])


def root_foundation():
    """Opaque scalp-fitted undergrowth behind sparse roots, never face edits."""
    import bpy
    name = 'MF_finalhair142_root_foundation'
    if name in bpy.data.objects:
        return
    head = bpy.data.objects['MF_continuous_head_neck']
    vertices = [head.matrix_world @ (v.co+v.normal*.010) for v in head.data.vertices]
    keep = {i for i, q in enumerate(vertices) if q.z > max(.24, .995-1.12*q.x*q.x)}
    faces = [list(p.vertices) for p in head.data.polygons if all(i in keep for i in p.vertices)]
    used = sorted({i for f in faces for i in f})
    remap = {index:i for i,index in enumerate(used)}
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata([vertices[i] for i in used], [], [[remap[i] for i in f] for f in faces])
    mesh.update()
    ob = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(ob)
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    p = mat.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value = (.008,.003,.0015,1)
    p.inputs['Roughness'].default_value = .95
    p.inputs['Specular IOR Level'].default_value = 0
    mesh.materials.append(mat)
    for p in mesh.polygons:
        p.use_smooth = True


def rebuild(candidate):
    import bpy
    from hair_donor import rebuild_painted
    rebuild_painted(bpy.data.objects[MAIN], 23)
    return finish(candidate)


def control(candidate, protected):
    import bpy
    from mathutils import Vector
    from hair_donor import painted_state, curve_state
    from illustrated_hair_section import protection
    main = bpy.data.objects[MAIN]
    baseline = painted_state(bpy.data.objects[NAME])
    before = curve_state(main)
    ci, pi = 7, 4
    old = main.data.curves[ci].points[pi].position.copy()
    main.data.curves[ci].points[pi].position = old+Vector((0, -.08, .04))
    main.data.update_tag()
    changed_source = curve_state(main)
    changed = painted_state(rebuild(candidate))
    main.data.curves[ci].points[pi].position = old
    main.data.update_tag()
    restored = painted_state(rebuild(candidate))
    assert before != changed_source and baseline != changed and restored == baseline
    assert protection() == protected
    return {'source_changed': True, 'rendered_changed': True, 'rollback_exact': True,
            'protected_exact': True, 'baseline': baseline, 'changed': changed,
            'scope': 'One static source guide edit plus explicit derivative rebuild; motion unqualified'}


def run(job):
    out = validate(job)
    import bpy
    from hair_donor import painted_state
    from illustrated_hair_section import protection
    from hijab_donor import review
    out.mkdir()
    shutil.copyfile(__file__, out/'handler-source.py')
    candidate = job['candidate']
    if job['operation'] == 'audit':
        bpy.ops.wm.open_mainfile(filepath=str(SOURCE), load_ui=False, use_scripts=False)
        protected = protection()
        ob = finish(candidate)
        inventory = [{'name':o.name, 'type':o.type, 'materials':[m.name for m in o.data.materials] if hasattr(o.data,'materials') else []} for o in bpy.context.scene.objects if not o.hide_render]
        (out/'inventory.json').write_text(json.dumps(inventory,indent=2)+'\n')
        paths = []
        for ci, c in enumerate(ob.data.curves):
            if ci % 173 == 0:
                paths.append({'index':ci,'points':[list(c.points[k].position) for k in (0,8,16,24,32,40,48,56,63)]})
        (out/'paths.json').write_text(json.dumps(paths,indent=2)+'\n')
        if candidate == 3:
            return
        mat = ob.data.materials[0]
        nodes, links = mat.node_tree.nodes, mat.node_tree.links
        emission = nodes.new('ShaderNodeEmission')
        emission.inputs['Color'].default_value = (.12,.20,.24,1)
        links.new(emission.outputs[0],nodes.get('Material Output').inputs['Surface'])
        review(bpy.context.scene,out,(0,0,-.20),4.2,(('front',0),))
        assert protection() == protected
        return
    if job['operation'] == 'verify':
        folder = BASE/f'finalhair142-seal-{candidate:02}'
        record = json.loads((folder/'result.json').read_text())
        native = folder/'finished-hair.blend'
        bpy.ops.wm.open_mainfile(filepath=str(native), load_ui=False, use_scripts=False)
        protected = protection()
        assert protected == record['protected_digest']
        assert painted_state(bpy.data.objects[NAME]) == record['rendered_baseline']
        result = control(candidate, protected)
        assert result == record['control']
        review(bpy.context.scene, out, (0, 0, -.20), 4.2, (('front', 0),))
        assert digest(native) == record['native_sha256']
        result.update(fresh_reopen_exact=True, native_unchanged=True)
    else:
        bpy.ops.wm.open_mainfile(filepath=str(SOURCE), load_ui=False, use_scripts=False)
        protected = protection()
        ob = finish(candidate)
        result = {'rendered_baseline': painted_state(ob)}
        review(bpy.context.scene, out, (0, 0, -.20), 4.2,
               (('front', 0), ('left', -45), ('right', 45), ('back', 180)))
        if job['operation'] == 'seal':
            result['control'] = control(candidate, protected)
            bpy.context.scene['MF_hair_reference_status'] = 'SIX_APPROVED_REFERENCES_NATIVE_REVIEW_PENDING'
            bpy.ops.file.pack_all()
            unpacked=[im.name for im in bpy.data.images if im.source=='FILE' and im.has_data and not im.packed_file]
            assert not unpacked, unpacked
            result['loaded_file_images_packed']=True
            native = out/'finished-hair.blend'
            bpy.ops.wm.save_as_mainfile(filepath=str(native), compress=True)
            result['native_sha256'] = digest(native)
    assert protection() == protected
    result.update(candidate=candidate, protected_exact=True, protected_digest=protected,
                  source_sha256=SOURCE_SHA, reference_authority=PINS,
                  original_identity_authority=ORIGINAL_PINS,
                  handler_sha256=digest(out/'handler-source.py'), director_acceptance='PENDING',
                  scalp_motion='NOT_RUN', derived_binding='EXPLICIT_REBUILD')
    (out/'result.json').write_text(json.dumps(result, indent=2)+'\n')


if __name__ == '__main__':
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    args = sys.argv[sys.argv.index('--')+1:]
    if len(args) != 1:
        raise ValueError('One structured job required')
    run(json.loads(Path(args[0]).read_text()))
