"""Pinned facial-readiness diagnostic; no arbitrary input paths/code or network.

Uses the locally installed KeenTools core through its observed native API.
Never modifies the accepted native asset. Does not activate/purchase licenses.
"""
import hashlib
import json
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / '.runtime/art-direction/series01-facebuilder-trial-01'
SOURCE = BASE / 'bust-atlas-build-02/character-upperbody.blend'
SOURCE_SHA = '408a982610f4fe9260101f34245099ae80731de9c7b56e58e46963f854a22dd5'
CORE = Path('/Users/adisharma/Library/Application Support/Blender/5.2/extensions/user_default/keentools/blender_independent_packages/pykeentools_loader/pykeentools/pykeentools_installation/pykeentools')


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(job):
    if not isinstance(job, dict) or set(job) != {'operation', 'candidate'}:
        raise ValueError('Exact structured keys required')
    if (job['operation'],job['candidate']) not in (('diagnose',1),('transfer',1),('transfer',2),('verify',2),('verify',3),('verify',4)) or type(job['candidate']) is not int:
        raise ValueError('Only diagnostic01 authorized')
    if SOURCE.is_symlink() or digest(SOURCE) != SOURCE_SHA:
        raise ValueError('Accepted source changed')
    out = BASE / f'face-performance-{job["operation"]}-{job["candidate"]:02}'
    if out.exists() or shutil.disk_usage(BASE).free < 5_000_000_000:
        raise ValueError('Existing output or disk low')
    return out


def neutral_geometry(ob):
    value={'vertices':[list(v.co) for v in ob.data.vertices],
           'polygons':[list(p.vertices) for p in ob.data.polygons],
           'uv':{layer.name:[list(p.uv) for p in layer.data] for layer in ob.data.uv_layers},
           'transform':[list(r) for r in ob.matrix_world]}
    return hashlib.sha256(json.dumps(value,sort_keys=True).encode()).hexdigest()


def boundary_loops(ob):
    """Connected boundary chains and bounds, not inferred anatomy labels."""
    import bmesh
    bm=bmesh.new();bm.from_mesh(ob.data)
    neighbors={}
    for e in bm.edges:
        if e.is_boundary:
            a,b=e.verts
            neighbors.setdefault(a,set()).add(b);neighbors.setdefault(b,set()).add(a)
    todo=set(neighbors);groups=[]
    while todo:
        stack=[todo.pop()];group=[]
        while stack:
            v=stack.pop();group.append(v)
            for other in neighbors[v]:
                if other in todo:todo.remove(other);stack.append(other)
        groups.append({'count':len(group),'all_degree_two':all(len(neighbors[v])==2 for v in group),
                       'min':[min(v.co[k] for v in group) for k in range(3)],
                       'max':[max(v.co[k] for v in group) for k in range(3)]})
    bm.free();return groups


def verify(out, summary_only=False):
    import bpy
    from bust_skin_review import protected_state
    from hijab_donor import review
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE),load_ui=False,use_scripts=False)
    original=bpy.data.objects['MF_continuous_head_neck']
    expected=neutral_geometry(original);other=protected_state()['other_objects']
    for o in bpy.context.scene.objects:
        if o.type in ('MESH','CURVE'):o.hide_render=o!=original
    if not summary_only:review(bpy.context.scene,out,(0,-.1,.1),2.7,(('accepted-front',0),('accepted-oblique',-35)))
    native=BASE/'face-performance-transfer-02/face-readiness.blend'
    if digest(native)!='747043d68620efc2f956bf0485a827e884d3f47cce2ecaed3ebfafe927288902':
        raise ValueError('Derivative changed')
    bpy.ops.wm.open_mainfile(filepath=str(native),load_ui=False,use_scripts=False)
    ob=bpy.data.objects['MF_continuous_head_neck']
    result={'source_sha256':SOURCE_SHA,'native_sha256':digest(native),'handler_sha256':digest(Path(__file__)),
            'fresh_open':True,'neutral_geometry_original_uvs_transform_exact':neutral_geometry(ob)==expected,
            'other_objects_exact':protected_state()['other_objects']==other,
            'control_values':{k.name:k.value for k in ob.data.shape_keys.key_blocks},
            'neutral_all_controls_zero':all(k.value==0 for k in list(ob.data.shape_keys.key_blocks)[1:]),
            'shape_keys':list(ob.data.shape_keys.key_blocks.keys()),'boundary_chains':boundary_loops(ob),
            'rest_position_matches_neutral':all((a.vector-v.co).length<1e-7 for a,v in zip(ob.data.attributes['MF_performance_rest_position'].data,ob.data.vertices)),
            'all_file_images_packed':all(bool(im.packed_file or im.packed_files) for im in bpy.data.images if im.source=='FILE')}
    result['checks_passed']=all(result[k] for k in ('neutral_geometry_original_uvs_transform_exact','other_objects_exact','neutral_all_controls_zero','rest_position_matches_neutral','all_file_images_packed'))
    # Preserve failed checks before diagnostic renders; never equate process exit
    # with a passing preservation gate.
    (out/'result.json').write_text(json.dumps(result,indent=2))
    if summary_only:
        result['evaluated_neutral_vertices_exact']=all((a.co-b.co).length<1e-7 for a,b in zip(ob.evaluated_get(bpy.context.evaluated_depsgraph_get()).data.vertices,ob.data.vertices))
        result['accepted_asset_unchanged']=digest(SOURCE)==SOURCE_SHA
        (out/'result.json').write_text(json.dumps(result,indent=2))
        return
    for o in bpy.context.scene.objects:
        if o.type in ('MESH','CURVE'):o.hide_render=o!=ob
    review(bpy.context.scene,out,(0,-.1,.1),2.7,(('derivative-front',0),('derivative-oblique',-35)))
    # Distinguish projected texture problems from geometric closure failures.
    clay=bpy.data.materials.new('MF_readiness_clay');clay.use_nodes=True
    p=clay.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(.4,.4,.4,1)
    p.inputs['Roughness'].default_value=.85
    ob.data.materials.clear();ob.data.materials.append(clay)
    for name in ('eyeBlinkLeft','eyeBlinkRight'):ob.data.shape_keys.key_blocks[name].value=1
    review(bpy.context.scene,out,(0,-.1,.1),2.7,(('blink-clay-front',0),('blink-clay-oblique',-35)))
    for key in ob.data.shape_keys.key_blocks:key.value=0
    result['neutral_after_control_reset_exact']=neutral_geometry(ob)==expected
    result['accepted_asset_unchanged']=digest(SOURCE)==SOURCE_SHA
    result['native_unchanged']=digest(native)=='747043d68620efc2f956bf0485a827e884d3f47cce2ecaed3ebfafe927288902'
    (out/'result.json').write_text(json.dumps(result,indent=2))


def uv_identity(mesh):
    """Per-vertex incident original UV sets: topological IDs, not proximity."""
    uv = mesh.uv_layers['UVMap'].data
    identities = [set() for _ in mesh.vertices]
    for loop in mesh.loops:
        identities[loop.vertex_index].add(tuple(round(float(x),6) for x in uv[loop.index].uv))
    return [tuple(sorted(a)) for a in identities]


def binding(source_ids, target_ids):
    lookup = {}
    for i, key in enumerate(source_ids):
        lookup.setdefault(key,[]).append(i)
    # Ambiguity is failure, never choose one overlapping lid/lip arbitrarily.
    return [lookup[key][0] if key and len(lookup.get(key,[]))==1 else None for key in target_ids]


def transfer(out):
    import bpy
    import numpy as np
    from bust_skin_review import protected_state
    from hijab_donor import review
    from bust_skin_atlas import smooth
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE),load_ui=False,use_scripts=False)
    before = protected_state()
    ob=bpy.data.objects['MF_continuous_head_neck']; donor=bpy.data.objects['FBHead']
    ids=binding(uv_identity(donor.data),uv_identity(ob.data))
    facial=[v.index for v in ob.data.vertices if v.co.z>-.85]
    missing=[i for i in facial if ids[i] is None]
    record={'source_sha256':SOURCE_SHA,'handler_sha256':digest(Path(__file__)),
            'facial_vertices':len(facial),'unmapped_facial_vertices':len(missing),
            'all_mapped_vertices':sum(i is not None for i in ids),'binding':'unique full incident original UVMap sets rounded6',
            'status':'NOT_TRANSFERRED'}
    if missing:
        record['missing_bounds']=[[min(ob.data.vertices[i].co[k] for i in missing),max(ob.data.vertices[i].co[k] for i in missing)] for k in range(3)]
        (out/'result.json').write_text(json.dumps(record,indent=2));return
    # Verify actual adjacency too; UV coincidence alone is insufficient.
    donor_edges={tuple(sorted(e.vertices)) for e in donor.data.edges}
    facial_set=set(facial)
    mismatch=[e.index for e in ob.data.edges if all(i in facial_set for i in e.vertices)
              and tuple(sorted(ids[i] for i in e.vertices)) not in donor_edges]
    record['facial_edge_mismatches']=len(mismatch)
    if mismatch:
        (out/'result.json').write_text(json.dumps(record,indent=2));return
    frozen=BASE/'face-performance-diagnose-01/donor-facs-deltas.npz'
    if digest(frozen)!='301d92be8bc3969fbf683940f8a49788cfb659bd257c3ff360165e64f2ae6703':
        raise ValueError('FACS evidence changed')
    with np.load(frozen,allow_pickle=False) as archive:
        deltas={name:archive[name] for name in archive.files}
    selected=('eyeBlinkLeft','eyeBlinkRight','eyeSquintLeft','eyeSquintRight',
              'browInnerUp','browOuterUpLeft','browOuterUpRight','browDownLeft','browDownRight',
              'jawOpen','mouthClose','mouthSmileLeft','mouthSmileRight','mouthFrownLeft','mouthFrownRight',
              'mouthPressLeft','mouthPressRight','cheekSquintLeft','cheekSquintRight')
    neutral=np.array([tuple(v.co) for v in ob.data.vertices],dtype=np.float32)
    ob.shape_key_add(name='Basis')
    for name in selected:
        arr=neutral.copy()
        for i,source_i in enumerate(ids):
            if source_i is not None:
                arr[i]+=deltas[name][source_i]*smooth((float(neutral[i,2])+1.0)/.15)
        key=ob.shape_key_add(name=name);key.data.foreach_set('co',arr.ravel());key.value=0
    print('Transferred19 shapes with unique UV/adjacency binding',flush=True)
    # Per-vertex rest coordinates are interpolated with the surface. This preserves
    # the existing shader functions without introducing cylindrical UV seams.
    mat=ob.data.materials[0].copy();ob.data.materials[0]=mat
    attr=ob.data.attributes.new('MF_performance_rest_position','FLOAT_VECTOR','POINT')
    attr.data.foreach_set('vector',neutral.ravel())
    node=mat.node_tree.nodes.new('ShaderNodeAttribute');node.attribute_name=attr.name
    replacements=0
    for n in list(mat.node_tree.nodes):
        if n.type=='TEX_COORD':
            for link in list(n.outputs['Object'].links):
                mat.node_tree.links.new(node.outputs['Vector'],link.to_socket);replacements+=1
    record['rest_coordinate_links']=replacements
    # Full original state comparison after temporarily removing only new keys.
    original_uv_digest=hashlib.sha256(json.dumps([[list(p.uv) for p in layer.data] for layer in ob.data.uv_layers]).encode()).hexdigest()
    record['neutral_vertex_sha256']=hashlib.sha256(neutral.tobytes()).hexdigest()
    record['original_uv_sha256']=original_uv_digest
    record['shape_keys']=selected
    record['status']='TRANSFERRED_PREVIEW_NOT_QUALIFIED'
    record['neutral_exact']=np.array_equal(neutral,np.array([tuple(v.co) for v in ob.data.vertices],dtype=np.float32))
    record['other_objects_unchanged']=protected_state()['other_objects']==before['other_objects']
    assert record['neutral_exact'] and record['other_objects_unchanged']
    native=out/'face-readiness.blend';bpy.ops.wm.save_as_mainfile(filepath=str(native))
    record['native_sha256']=digest(native)
    # Four cheap complete pose diagnostics before any long animation rendering.
    for o in bpy.context.scene.objects:
        if o.type in ('MESH','CURVE'):o.hide_render=o!=ob
    poses={'neutral':{},'blink':{'eyeBlinkLeft':1.,'eyeBlinkRight':1.},
           'smile':{'mouthSmileLeft':.28,'mouthSmileRight':.28,'cheekSquintLeft':.15,'cheekSquintRight':.15},
           'jaw':{'jawOpen':.20}}
    for label,values in poses.items():
        for key in ob.data.shape_keys.key_blocks:key.value=values.get(key.name,0.)
        review(bpy.context.scene,out,(0,-.1,.1),2.7,((label,0),))
    record['accepted_asset_unchanged']=digest(SOURCE)==SOURCE_SHA
    (out/'result.json').write_text(json.dumps(record,indent=2))


def components(ob):
    parent = list(range(len(ob.data.vertices)))
    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i
    for e in ob.data.edges:
        a, b = e.vertices
        parent[find(a)] = find(b)
    groups = {}
    for i in range(len(parent)):
        groups.setdefault(find(i), []).append(i)
    return sorted(groups.values(), key=len, reverse=True)


def topology(ob):
    groups = components(ob)
    return {'vertices': len(ob.data.vertices), 'polygons': len(ob.data.polygons),
            'components': [{'count': len(g), 'first_indices': g[:12],
                'min': [min(ob.data.vertices[i].co[k] for i in g) for k in range(3)],
                'max': [max(ob.data.vertices[i].co[k] for i in g) for k in range(3)]}
                for g in groups],
            'uv_layers': list(ob.data.uv_layers.keys())}


def diagnose(out):
    import bpy
    import numpy as np
    from mathutils.kdtree import KDTree
    from bust_skin_review import protected_state, material_record
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE), load_ui=False, use_scripts=False)
    before = protected_state()
    target = bpy.data.objects['MF_continuous_head_neck']
    donor = bpy.data.objects['FBHead']
    result = {'source_sha256': SOURCE_SHA, 'handler_sha256': digest(Path(__file__)),
              'target': topology(target), 'donor': topology(donor),
              'material': material_record(target.data.materials[0])}
    # Coordinate correspondence is inspected, never assumed from vertex counts.
    tree = KDTree(len(donor.data.vertices))
    for v in donor.data.vertices:
        tree.insert(v.co, v.index)
    tree.balance()
    distances = [tree.find(v.co)[2] for v in target.data.vertices if v.co.z > -.65]
    result['upper_head_nearest_donor'] = {'count': len(distances),
        'max': max(distances), 'within_1e_5': sum(d < 1e-5 for d in distances),
        'warning': 'Diagnostic only; nearest vertex is not a valid transfer binding.'}
    lib = CORE / 'pykeentools.cpython-313-darwin.so'
    result['core_library_sha256'] = digest(lib)
    sys.path.insert(0, str(CORE))
    import pykeentools as pkt
    result['facs_available_for_donor'] = bool(pkt.FacsExecutor.facs_available(len(donor.data.vertices)))
    result['facs_available_for_target'] = bool(pkt.FacsExecutor.facs_available(len(target.data.vertices)))
    # Exactly the coordinate convention used by installed KeenTools blendshapes.py.
    rotation = np.array([[1., 0., 0.], [0., 0., -1.], [0., 1., 0.]], dtype=np.float32)
    vertices = np.array([tuple(v.co) for v in donor.data.vertices], dtype=np.float32)
    result['generation'] = {'status': 'NOT_RUN'}
    try:
        executor = pkt.FacsExecutor(vertices @ rotation, 1.0)
        if not executor.facs_enabled():
            result['generation'] = {'status': 'UNAVAILABLE'}
        else:
            names = list(executor.facs_names)
            arrays = {}
            for i, name in enumerate(names):
                shape = np.asarray(executor.get_facs_blendshape(i)) @ rotation.T
                if shape.shape != vertices.shape or not np.isfinite(shape).all():
                    raise ValueError('Invalid native FACS result')
                arrays[name] = shape - vertices
            np.savez_compressed(out / 'donor-facs-deltas.npz', **arrays)
            result['generation'] = {'status': 'RECOVERED_NOT_TRANSFERRED', 'names': names,
                'count': len(names), 'max_displacements': {n: float(np.linalg.norm(a, axis=1).max()) for n,a in arrays.items()},
                'deltas_sha256': digest(out/'donor-facs-deltas.npz'),
                'scale': 1.0, 'scale_provenance': 'Standalone FACS head default in installed addon; must validate spatial results'}
    except Exception as err:
        result['generation'] = {'status': 'FAILED', 'exception_type': type(err).__name__}
        # Do not dump third-party exception text, which may contain license details.
    assert protected_state() == before
    result['accepted_asset_unchanged'] = digest(SOURCE) == SOURCE_SHA
    (out/'result.json').write_text(json.dumps(result, indent=2))


def run(job):
    out = validate(job)
    out.mkdir()
    if job['operation']=='diagnose':diagnose(out)
    elif job['operation']=='transfer':transfer(out)
    else:verify(out,job['candidate']==4)


if __name__ == '__main__':
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    args = sys.argv[sys.argv.index('--')+1:]
    if len(args) != 1:
        raise ValueError('One structured job required')
    run(json.loads(Path(args[0]).read_text()))
