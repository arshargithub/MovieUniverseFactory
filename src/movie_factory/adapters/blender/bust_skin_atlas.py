"""Bounded full-map skin authoring: native bake, image ingestion, protected face.

Only named operations on pinned local files. No provider, code-string or asset
script execution. Original UVs are restored after the temporary bake channel.
"""
import hashlib
import json
import math
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / '.runtime/art-direction/series01-facebuilder-trial-01'
SOURCE = BASE / 'posterior-neck-build-16/character-upperbody.blend'
SOURCE_SHA = '76b2a6c7f4f1c2288ed746ebb3cf146b4146650058e263c6dd16b6f9225ef080'
TEXTURE = BASE / 'bust-atlas-input-01/skin-authored.png'
TEXTURE_SHA = 'a5c85d73f42f135af5980950967eed5549ca365e66c1d286280d26ebd2eb709a'
ZMIN, ZMAX = -2.8, 1.65


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def smooth(t):
    t = max(0., min(1., t))
    return t*t*(3-2*t)


def uv_point(x, y, z):
    return (.5 + math.atan2(x, -y) / math.tau, (z-ZMIN)/(ZMAX-ZMIN))


def core_weight(x, y, z):
    """Exact original eyes, brows, nose/mouth; feather across cheeks/chin.

    Upper outer temple is excluded to avoid retaining projected hair traces.
    """
    ax = abs(x)
    upper = .74-.32*min(ax/.72, 1.)**2
    lower = -.78+.18*min(ax/.75, 1.)**2
    return (smooth((.77-ax)/.28)*smooth((-.26-y)/.27)
            *smooth((upper-z)/.16)*smooth((z-lower)/.16))


def validate(job):
    if not isinstance(job, dict) or set(job) != {'operation', 'candidate'}:
        raise ValueError('Exact operation/candidate keys required')
    if job['operation'] not in ('prepare', 'build', 'portraits', 'emission', 'verify'):
        raise ValueError('Unsupported operation')
    if type(job['candidate']) is not int or job['candidate'] != 1:
        raise ValueError('Only candidate01 authorized')
    if SOURCE.is_symlink() or digest(SOURCE) != SOURCE_SHA:
        raise ValueError('Pinned anatomy changed')
    if job['operation'] != 'prepare':
        if TEXTURE_SHA is None or TEXTURE.is_symlink() or digest(TEXTURE) != TEXTURE_SHA:
            raise ValueError('Authored texture not pinned')
    out = BASE / f'bust-atlas-{job["operation"]}-01'
    if out.exists() or shutil.disk_usage(BASE).free < 5_000_000_000:
        raise ValueError('Existing output or disk low')
    return out


def prepare(out):
    import bpy
    from bust_skin_regions import material
    material(3)
    ob = bpy.data.objects['MF_continuous_head_neck']
    mat = ob.data.materials[0]; n, links = mat.node_tree.nodes, mat.node_tree.links
    original_uv = ob.data.uv_layers.active.name
    uv_source = n.new('ShaderNodeUVMap'); uv_source.uv_map = original_uv
    # Freeze implicit UV consumers before a temporary baking channel is selected.
    for node in list(n):
        if node.type == 'TEX_IMAGE' and not node.inputs['Vector'].is_linked:
            links.new(uv_source.outputs[0], node.inputs['Vector'])
        if node.type == 'TEX_COORD':
            for link in list(node.outputs['UV'].links):
                links.new(uv_source.outputs[0], link.to_socket)
    layer = ob.data.uv_layers.new(name='MF_temporary_authoring_atlas')
    for poly in ob.data.polygons:
        coords = [uv_point(*ob.data.vertices[ob.data.loops[i].vertex_index].co) for i in poly.loop_indices]
        crosses = max(p[0] for p in coords)-min(p[0] for p in coords) > .5
        for i, (u, v) in zip(poly.loop_indices, coords):
            layer.data[i].uv = (u+1 if crosses and u < .5 else u, v)
    im = bpy.data.images.new('MF_atlas_reference', width=2048, height=2048, alpha=False)
    im.generated_color = (.68, .30, .16, 1)
    im.colorspace_settings.name = 'sRGB'
    target = n.new('ShaderNodeTexImage'); target.image = im; n.active = target
    p = n['Principled BSDF']; em = n.new('ShaderNodeEmission')
    links.new(p.inputs['Base Color'].links[0].from_socket, em.inputs['Color'])
    output = next(q for q in n if q.type == 'OUTPUT_MATERIAL' and q.is_active_output)
    links.new(em.outputs[0], output.inputs['Surface'])
    bpy.ops.object.select_all(action='DESELECT'); ob.hide_set(False)
    ob.select_set(True); bpy.context.view_layer.objects.active = ob
    scene = bpy.context.scene; scene.render.engine = 'CYCLES'
    scene.cycles.samples = 1; scene.render.bake.margin = 32
    scene.render.bake.use_clear = False
    bpy.ops.object.bake(type='EMIT', uv_layer=layer.name)
    im.filepath_raw = str(out/'atlas-reference.png'); im.file_format = 'PNG'; im.save()
    ob.data.uv_layers.remove(layer)
    ob.data.uv_layers.active = ob.data.uv_layers[original_uv]
    return {'reference_sha256': digest(out/'atlas-reference.png'),
            'mapping': 'u=.5+atan2(x,-y)/tau; v=(z+2.8)/4.45; backside seam',
            'temporary_uv_removed': True, 'source_material': 'region03 diagnostic, not accepted skin'}


def apply_texture():
    import bpy
    ob = bpy.data.objects['MF_continuous_head_neck']
    mat = ob.data.materials[0].copy(); ob.data.materials[0] = mat
    mat.name = 'MF_authored_skin_atlas_01'
    n, links = mat.node_tree.nodes, mat.node_tree.links
    im = bpy.data.images.load(str(TEXTURE), check_existing=False)
    if min(im.size) < 1024 or max(im.size) > 4096:
        raise ValueError('Texture resolution out of bounds')
    im.colorspace_settings.name = 'sRGB'; im.pack()
    def mathnode(op, a, b=0):
        q=n.new('ShaderNodeMath');q.operation=op
        for i,v in enumerate((a,b)):
            if isinstance(v,(float,int)):q.inputs[i].default_value=v
            else:links.new(v,q.inputs[i])
        return q.outputs[0]
    tc=n.new('ShaderNodeTexCoord');xyz=n.new('ShaderNodeSeparateXYZ')
    links.new(tc.outputs['Object'],xyz.inputs[0])
    u=mathnode('ADD',.5,mathnode('DIVIDE',mathnode('ARCTAN2',xyz.outputs['X'],mathnode('MULTIPLY',xyz.outputs['Y'],-1)),math.tau))
    v=mathnode('DIVIDE',mathnode('SUBTRACT',xyz.outputs['Z'],ZMIN),ZMAX-ZMIN)
    uv=n.new('ShaderNodeCombineXYZ');links.new(u,uv.inputs[0]);links.new(v,uv.inputs[1])
    tex=n.new('ShaderNodeTexImage');tex.image=im;tex.extension='REPEAT';links.new(uv.outputs[0],tex.inputs['Vector'])
    a=ob.data.attributes.new('MF_atlas_original_face','FLOAT','POINT')
    for vertex,d in zip(ob.data.vertices,a.data):d.value=core_weight(*vertex.co)
    mask=n.new('ShaderNodeAttribute');mask.attribute_name=a.name
    mix=n.new('ShaderNodeMixRGB');links.new(mask.outputs['Fac'],mix.inputs[0])
    links.new(tex.outputs['Color'],mix.inputs[1])
    links.new(n['Mix (Legacy).001'].outputs['Color'],mix.inputs[2])
    links.new(mix.outputs[0],n['Principled BSDF'].inputs['Base Color'])
    return {'texture_sha256':TEXTURE_SHA,'texture_size':list(im.size),'original_face_weight_range':[min(d.value for d in a.data),max(d.value for d in a.data)],
            'geometry_changed':False,'uv_channels_changed':False,
            'limitation':'Generated outside-face color requires native review; original face has illustrated baked-in tone, not calibrated albedo.'}


def run(job):
    out=validate(job)
    import bpy
    from bust_skin_review import protected_state, material_record, render
    from bust_skin_detail import render_portraits
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE),load_ui=False,use_scripts=False)
    before=protected_state();out.mkdir()
    result={'job':job,'source_sha256':SOURCE_SHA,'handler_sha256':digest(Path(__file__)),
            'skin_director_accepted':False}
    if job['operation']=='prepare':
        result['edit']=prepare(out)
    elif job['operation']=='build':
        result['edit']=apply_texture()
        assert protected_state()==before
        native=out/'character-upperbody.blend';bpy.ops.wm.save_as_mainfile(filepath=str(native))
        result['native_sha256']=digest(native)
    else:
        folder=BASE/'bust-atlas-build-01';native=folder/'character-upperbody.blend'
        record=json.loads((folder/'result.json').read_text())
        if native.is_symlink() or digest(native)!=record['native_sha256']:raise ValueError('Candidate changed')
        bpy.ops.wm.open_mainfile(filepath=str(native),load_ui=False,use_scripts=False)
        result['native_sha256']=record['native_sha256']
    assert protected_state()==before,'Geometry/original UVs/other objects changed'
    result['protected_state']=before
    result['materials']=[material_record(m) for m in bpy.data.objects['MF_continuous_head_neck'].data.materials]
    result['images']=[{'name':im.name,'packed':bool(im.packed_file or im.packed_files),'size':list(im.size)}
                      for im in bpy.data.images if im.source=='FILE']
    assert all(im['packed'] for im in result['images']), 'Unpacked image dependency'
    if job['operation'] not in ('prepare','build'):
        assert json.loads(json.dumps(result['materials']))==record['materials']
    if job['operation']=='portraits':render_portraits(out)
    elif job['operation'] in ('build','emission'):render(out,job['operation']=='emission')
    assert digest(SOURCE)==SOURCE_SHA
    (out/'result.json').write_text(json.dumps(result,indent=2))


if __name__=='__main__':
    sys.path.insert(0,str(Path(__file__).resolve().parent))
    args=sys.argv[sys.argv.index('--')+1:]
    if len(args)!=1:raise ValueError('One structured job required')
    run(json.loads(Path(args[0]).read_text()))
