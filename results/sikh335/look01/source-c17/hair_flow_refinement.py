"""Bounded crown sampling and lower-wave variation on the pinned framing bust.

No face, scalp-support geometry, hairline, rig, costume or source edits.
Inputs select authored variants, never code, assets or arbitrary paths.
"""
import hashlib
import json
import math
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT / '.runtime/art-direction/series01-facebuilder-trial-01'
SOURCE = BASE / 'framing-package-03/hair-framing.blend'
SOURCE_SHA = 'f672d4faa324ffddb00234966d3d7e7c591ee7e9d81fad82598fa7620dcc51ee'
PAINTED_TEXTURE = BASE / 'hairflow-painted-texture-v01.png'
PAINTED_TEXTURE_SHA = 'e4f2d874ecebd5b46bd0b24923d4b746f0b6a159f82aaf0417bc3137ec215dbf'
REFBASE = ROOT / '.runtime/art-direction/series01-pashtun-baseline-v01'
REFERENCES = {
    'frontal-v02-individualized.png': '7f959fed6ca4f57cb1b7fdaa20aa4a0fdd64208595a8b5debd8d060c79068c75',
    'portrait-v07-individualized.png': 'e6afc72b56fa57642b521fd7a922894d81a900b8cab0103f7c3f2cfb39a795f1',
}


def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()


def smooth(t):
    t = max(0., min(1., t))
    return t*t*(3-2*t)


def validate(job):
    if not isinstance(job, dict) or set(job) != {'operation', 'candidate'}:
        raise ValueError('Exact structured keys required')
    if job['operation'] not in ('preview', 'package') or type(job['candidate']) is not int or job['candidate'] not in (1, 2, 3, 4, 5, 6):
        raise ValueError('Unsupported operation')
    for p, h in [(SOURCE, SOURCE_SHA), *[(REFBASE/n, h) for n, h in REFERENCES.items()]]:
        if p.is_symlink() or digest(p) != h:
            raise ValueError('Pinned input changed')
    if job['candidate']>=5 and (PAINTED_TEXTURE.is_symlink() or digest(PAINTED_TEXTURE)!=PAINTED_TEXTURE_SHA):
        raise ValueError('Pinned painted texture changed')
    out = BASE / f'hairflow-{job["operation"]}-{job["candidate"]:02}'
    if out.exists() or out.is_symlink() or out.resolve().parent != BASE.resolve():
        raise ValueError('Output exists or escapes')
    if shutil.disk_usage(BASE).free < 5_000_000_000:
        raise ValueError('Disk low')
    if job['operation'] == 'package':
        p = BASE / f'hairflow-preview-{job["candidate"]:02}/result.json'
        if p.is_symlink() or not p.is_file():
            raise ValueError('Preview required')
        r = json.loads(p.read_text())
        if r.get('handler_sha256') != digest(Path(__file__)) or not r.get('protected_exact') or not r.get('hairline_geometry_exact'):
            raise ValueError('Stale preview or failed protection')
    return out


def crown_uv(x, y, z, previous, candidate):
    """Sample a two-dimensional footprint inside the original painted crown.

    Avoid the old clamped top row. The forehead-adjacent lower UVs are exact.
    The extra surface behind the reference view remains an interpretation.
    """
    weight = smooth((z-1.01)/.25)*(1-smooth((y+.05)/.45))
    if candidate>=3:
        weight = smooth((z-.90)/.13)*(1-smooth((y+.05)/.45))
    if weight == 0:
        return previous
    py = 275-46*(z-1.0)+38*(y+.7)+16*abs(x)
    if candidate>=2:
        py = 230+90*abs(x)**1.5+65*smooth((y+.65)/.85)
    if candidate>=3:
        py = 430-125*z+10*(y+.6)
    rows = [(220,425,563),(240,392,598),(280,337,652),(330,301,690),(400,274,707)]
    py = max(221., min(399., py))
    i = next(i for i in range(len(rows)-1) if rows[i+1][0] >= py)
    a,b = rows[i], rows[i+1]; t = (py-a[0])/(b[0]-a[0])
    left = a[1]*(1-t)+b[1]*t; right = a[2]*(1-t)+b[2]*t
    center = 488.; delta = x*182
    limit = abs((right if delta>0 else left)-center)
    delta = limit*.91*math.tanh(delta/(limit*.91))
    if candidate>=2:
        delta=x*245
        if abs(delta)>limit*.84:
            delta=math.copysign(limit*(.84+.13*math.tanh((abs(delta)/limit-.84)/.13)),delta)
    uv = ((center+delta)/955, 1-py/1647)
    return tuple(p*(1-weight)+q*weight for p,q in zip(previous,uv))


def lower_wave(point, center, index, candidate):
    """Coherent ring deformation; fixed roots, uneven widths and loose lengths."""
    x,y,z = point; cx,cy,cz = center
    weight = smooth((.28-cz)/.85)
    if weight == 0:
        return point
    phase = index*1.731
    strength = 1 if candidate==1 else .30
    angle = strength*weight*(.115*math.sin(cz*2.3+phase)+.045*math.sin(cz*4.1+phase*.7))
    width = 1+strength*weight*(.16*math.sin(phase+.4)+.08*math.sin(cz*2.8+phase))
    x = cx+(x-cx)*width; y = cy+(y-cy)*width
    nx = x*math.cos(angle)-y*math.sin(angle)
    ny = x*math.sin(angle)+y*math.cos(angle)
    radius = strength*weight*.06*math.sin(cz*2.9+phase+.6)
    radius_len = max(.2, math.hypot(cx,cy))
    nx += radius*cx/radius_len; ny += radius*cy/radius_len
    nz = z-weight*(.18+.095*math.sin(phase+1.2))*(1 if candidate==1 else .40)
    return nx,ny,nz


def hairline_signature():
    import bpy
    ob = bpy.data.objects['MF_sculpt_hair_support']
    return hashlib.sha256(repr((tuple(tuple(v.co) for v in ob.data.vertices),
                               tuple(tuple(p.vertices) for p in ob.data.polygons),
                               tuple(tuple(r) for r in ob.matrix_world))).encode()).hexdigest()


def rear_art_uv(u,z):
    """Follow a narrow, actual illustrated hair swathe beside the left face."""
    t = max(0.,min(1.,(1.55-z)/3.60))
    rows = [(0.,356,310),(.15,304,380),(.30,283,460),(.45,264,530),
            (.60,261,590),(.75,275,675),(.90,291,750),(1.,310,800)]
    i = next(i for i in range(len(rows)-1) if rows[i+1][0]>=t)
    a,b=rows[i],rows[i+1]; f=(t-a[0])/(b[0]-a[0])
    px=a[1]*(1-f)+b[1]*f
    py=a[2]*(1-f)+b[2]*f
    px += 11*math.sin(u*93.4)+4*math.sin(u*31.1+.4)
    return px/955,1-py/1647


def reference_rear_material():
    import bpy
    mat = bpy.data.materials['MF_refined_hair_painted_flow']
    n,l = mat.node_tree.nodes,mat.node_tree.links
    uv=n.new('ShaderNodeUVMap'); uv.uv_map='RearHairArt'
    tex=n.new('ShaderNodeTexImage')
    original=next(node for node in n if node.bl_idname=='ShaderNodeTexImage')
    tex.image=original.image; l.new(uv.outputs[0],tex.inputs[0])
    mix=next(node for node in n if node.bl_idname=='ShaderNodeMixRGB')
    l.new(tex.outputs[0],mix.inputs[2])
    # The front projection stays authoritative. Only its existing fallback
    # changes from procedural stripes to image-derived hair brushwork.
    for ob in bpy.context.scene.objects:
        if ob.hide_render or ob.type!='MESH' or not any(m==mat for m in ob.data.materials): continue
        layer=ob.data.uv_layers.get('RearHairArt') or ob.data.uv_layers.new(name='RearHairArt')
        flow=ob.data.uv_layers['HairFlow']
        for loop in ob.data.loops:
            z=ob.data.vertices[loop.vertex_index].co.z
            layer.data[loop.index].uv=rear_art_uv(flow.data[loop.index].uv.x,z)


def authored_rear_material(candidate):
    import bpy
    mat=bpy.data.materials['MF_refined_hair_painted_flow']
    n,l=mat.node_tree.nodes,mat.node_tree.links
    uv=n.new('ShaderNodeUVMap'); uv.uv_map='HairFlow'
    scale=n.new('ShaderNodeVectorMath'); scale.operation='MULTIPLY'
    scale.inputs[1].default_value=(1.6,.95,1); l.new(uv.outputs[0],scale.inputs[0])
    tex=n.new('ShaderNodeTexImage'); tex.image=bpy.data.images.load(str(PAINTED_TEXTURE),check_existing=False); tex.image.pack()
    l.new(scale.outputs[0],tex.inputs[0])
    gain=n.new('ShaderNodeMixRGB'); gain.blend_type='MULTIPLY'; gain.inputs[0].default_value=1
    gain.inputs[2].default_value=(1.35,1.35,1.35,1); l.new(tex.outputs[0],gain.inputs[1])
    mix=next(node for node in n if node.bl_idname=='ShaderNodeMixRGB' and node!=gain)
    l.new(gain.outputs[0],mix.inputs[2])
    if candidate==6:
        # Hanging waves are wholly behind the face-framing shell. Do not
        # project the portrait's transverse crown strokes across their roots.
        rear=mat.copy(); rear.name='MF_painted_hanging_hair'
        rear_mix=rear.node_tree.nodes[mix.name]
        for link in list(rear_mix.inputs[0].links): rear.node_tree.links.remove(link)
        rear_mix.inputs[0].default_value=1
        for i in range(17):
            ob=bpy.data.objects[f'MF_illustrated_hair_lock_{100+i}']
            ob.data.materials.clear(); ob.data.materials.append(rear)


def build(candidate):
    import bpy
    base = bpy.data.objects['MF_sculpt_hair_support']
    ref = base.data.uv_layers['ReferenceHair']
    changed = 0
    for loop in base.data.loops:
        v = base.data.vertices[loop.vertex_index]
        old = tuple(ref.data[loop.index].uv)
        new = crown_uv(*v.co,old,candidate)
        ref.data[loop.index].uv = new
        changed += new != old
    mat = bpy.data.materials['MF_refined_hair_painted_flow']
    for node in mat.node_tree.nodes:
        if node.bl_idname == 'ShaderNodeMapRange' and abs(node.inputs['From Min'].default_value-1.43)<.001:
            node.inputs['From Min'].default_value = 3.0
            node.inputs['From Max'].default_value = 4.0
    moved = 0
    for i in range(17):
        ob = bpy.data.objects[f'MF_illustrated_hair_lock_{100+i}']
        mesh = ob.data
        if len(mesh.vertices) != 1662:
            raise ValueError('Unexpected authored lock topology')
        centers = []
        for ring in range(83):
            pts = [mesh.vertices[ring*20+j].co for j in range(20)]
            centers.append(tuple(sum(p[k] for p in pts)/20 for k in range(3)))
        for v in mesh.vertices:
            center = centers[v.index//20] if v.index<1660 else centers[0 if v.index==1660 else -1]
            old = tuple(v.co); v.co = lower_wave(old,center,i,candidate)
            moved += tuple(v.co) != old
        mesh.update()
    if candidate==4:
        reference_rear_material()
    if candidate>=5:
        authored_rear_material(candidate)
    return {'crown_uv_loops_changed':changed,'lower_wave_vertices_moved':moved,
            'scalp_support_geometry_changed':False,'rear_reference_available':False,
            'reference_brushwork_rear_material':candidate==4,
            'authored_painted_texture_sha256':PAINTED_TEXTURE_SHA if candidate>=5 else None,
            'rear_design':'PROVISIONAL_INTERPRETATION',
            'new_asset_purchases':0,'project_provider_api_calls':0,
            'built_in_texture_generation_used':candidate>=5}


def run(job):
    out = validate(job); out.mkdir(); shutil.copyfile(Path(__file__),out/'handler-source.py')
    import bpy
    from illustrated_hair_section import protection
    from hair_anatomy_refinement import visibility
    from hijab_donor import review
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE),load_ui=False,use_scripts=False)
    before = protection(); hairline = hairline_signature()
    info = build(job['candidate']); visibility()
    assert protection()==before and hairline_signature()==hairline
    review(bpy.context.scene,out,(0,0,-.03),3.8,(('front',0),('left',-45),('right',45),('back',180)))
    result = {'candidate':job['candidate'],'source_sha256':SOURCE_SHA,'reference_authority':REFERENCES,
              'handler_sha256':digest(Path(__file__)),'protected_exact':protection()==before,
              'hairline_geometry_exact':hairline_signature()==hairline,'changes':info,
              'clothing_rendered':False,'director_acceptance':'PENDING','hair_motion_qualified':False}
    if job['operation']=='package':
        review(bpy.context.scene,out,(0,0,-.03),3.8,(('portrait-front',0),('portrait-left',-45),('portrait-right',45)),portrait=True)
        native = out/'hair-flow.blend'; bpy.ops.wm.save_as_mainfile(filepath=str(native))
        bpy.ops.wm.open_mainfile(filepath=str(native),load_ui=False,use_scripts=False)
        result['fresh_reopen_protected_exact'] = protection()==before and hairline_signature()==hairline
        assert result['fresh_reopen_protected_exact']; result['native_sha256'] = digest(native)
    assert protection()==before and hairline_signature()==hairline and digest(SOURCE)==SOURCE_SHA
    (out/'result.json').write_text(json.dumps(result,indent=2)+'\n')


if __name__=='__main__':
    sys.path.insert(0,str(Path(__file__).resolve().parent))
    args = sys.argv[sys.argv.index('--')+1:]
    if len(args)!=1: raise ValueError('One fixed job required')
    run(json.loads(Path(args[0]).read_text()))
