"""Bounded material-only work on Director-approved anatomy16; no geometry edits."""
import hashlib
import json
import math
import statistics
from pathlib import Path
import shutil
import sys

ROOT=Path(__file__).resolve().parents[4]
BASE=ROOT/'.runtime/art-direction/series01-facebuilder-trial-01'
SOURCE=BASE/'posterior-neck-build-16/character-upperbody.blend'
SOURCE_SHA='76b2a6c7f4f1c2288ed746ebb3cf146b4146650058e263c6dd16b6f9225ef080'
VIEWS=(('front',0),('left',-60),('right',60),('back',180),('three-quarter',-35))


def validate(job):
    if not isinstance(job,dict) or set(job)!={'operation','candidate'}:raise ValueError('Exact job keys required')
    if job['operation'] not in ('inspect','emission','build','verify','verify-final') or type(job['candidate']) is not int or not 0<=job['candidate']<=3:raise ValueError('Unsupported job')
    if job['operation']=='inspect' and job['candidate']!=0:raise ValueError('Only baseline inspection')
    if job['operation'] in ('build','verify','verify-final') and job['candidate']==0:raise ValueError('Positive candidate required')
    if SOURCE.is_symlink() or hashlib.sha256(SOURCE.read_bytes()).hexdigest()!=SOURCE_SHA:raise ValueError('Pinned anatomy changed')
    out=BASE/f'bust-skin-{job["operation"]}-{job["candidate"]:02}'
    if out.exists() or shutil.disk_usage(BASE).free<5_000_000_000:raise ValueError('Existing output or disk low')
    return out


def protected_state():
    import bpy
    from neck_anatomy_review import signature
    ob=bpy.data.objects['MF_continuous_head_neck']
    return {'skin_geometry':signature(ob)['geometry'],
        'other_objects':{o.name:signature(o) for o in bpy.context.scene.objects if o.type in ('MESH','CURVE') and o!=ob}}


def material_record(mat):
    def value(v):
        if isinstance(v,(int,float,str,bool)):return v
        try:return list(v)
        except TypeError:return str(v)
    return {'name':mat.name,'nodes':[{'name':n.name,'type':n.type,
        'operation':getattr(n,'operation',None),'blend_type':getattr(n,'blend_type',None),
        'inputs':{s.name:value(s.default_value) for s in n.inputs if hasattr(s,'default_value')},
        'image':n.image.name if n.type=='TEX_IMAGE' and n.image else None,
        'ramp':[(e.position,list(e.color)) for e in n.color_ramp.elements] if hasattr(n,'color_ramp') else None}
        for n in mat.node_tree.nodes],
        'links':[(l.from_node.name,l.from_socket.name,l.to_node.name,l.to_socket.name) for l in mat.node_tree.links]}


def smooth(t):
    t=max(0.,min(1.,t));return t*t*(3-2*t)


def face_weight(x,y,z):
    ax=abs(x)
    top=.91-.59*min(ax/.85,1.)**1.7
    bottom=-.65+.40*min(ax/.80,1.)**2
    return smooth((top-z)/.12)*smooth((z-bottom)/.13)*smooth((-.16-y)/.28)*smooth((.86-ax)/.12)


def feature_weight(x,y,z):
    eye=smooth((z-.15)/.08)*smooth((.61-z)/.10)*smooth((.68-abs(x))/.10)
    mouth=smooth((z+.44)/.06)*smooth((.09-z)/.08)*smooth((.40-abs(x))/.10)
    return max(eye,mouth)*smooth((-.28-y)/.20)


def soft_face_weight(x,y,z):
    ax=abs(x)
    top=.87-.51*min(ax/.85,1.)**1.7
    bottom=-.69+.30*min(ax/.80,1.)**2
    return smooth((top-z)/.28)*smooth((z-bottom)/.24)*smooth((-.16-y)/.40)*smooth((.82-ax)/.24)


def inset_face_weight(x,y,z):
    ax=abs(x)
    top=.82-.50*min(ax/.85,1.)**1.7
    bottom=-.69+.30*min(ax/.80,1.)**2
    return smooth((top-z)/.28)*smooth((z-bottom)/.24)*smooth((-.34-y)/.28)*smooth((.76-ax)/.20)


def skin_material(candidate):
    import bpy
    from likeness_cleanup import linear_channel
    ob=bpy.data.objects['MF_continuous_head_neck'];assert ob.data.users==1
    mat=ob.data.materials[0].copy();ob.data.materials[0]=mat;mat.name=f'MF_bust_skin_{candidate:02}'
    n,l=mat.node_tree.nodes,mat.node_tree.links;p=n.get('Principled BSDF')
    original=p.inputs['Base Color'].links[0].from_socket
    # Samples from the measured emission review, not a guessed complexion.
    path=BASE/'bust-skin-emission-00/front.png';im=bpy.data.images.load(str(path),check_existing=False)
    if tuple(im.size)!=(640,800) or bpy.context.scene.view_settings.view_transform!='Standard':raise ValueError('Uncalibrated emission sample')
    pixels=list(im.pixels)
    samples=[pixels[4*((799-y)*640+x):4*((799-y)*640+x)+3] for x in range(246,285,3) for y in range(291,321,3)]
    encoded=[statistics.median(s[k] for s in samples) for k in range(3)]
    color=[linear_channel(c) for c in encoded]
    if candidate>=2:color=[color[0]*.90,color[1]*.97,color[2]*1.06]
    bpy.data.images.remove(im)
    face_fn={1:face_weight,2:soft_face_weight,3:inset_face_weight}[candidate]
    for name,fn in (('MF_skin_face_retention',face_fn),('MF_skin_feature_retention',feature_weight)):
        attr=ob.data.attributes.new(name,'FLOAT','POINT')
        for v,value in zip(ob.data.vertices,attr.data):value.value=fn(*v.co)
    def attr(name):
        node=n.new('ShaderNodeAttribute');node.attribute_name=name;return node.outputs['Fac']
    def math_node(op,a,b=None):
        node=n.new('ShaderNodeMath');node.operation=op
        for i,v in enumerate((a,b)):
            if v is None:continue
            if isinstance(v,(int,float)):node.inputs[i].default_value=v
            else:l.new(v,node.inputs[i])
        return node.outputs[0]
    coord=n.new('ShaderNodeTexCoord');noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=18;noise.inputs['Detail'].default_value=2
    l.new(coord.outputs['Object'],noise.inputs['Vector'])
    ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].position=.15;ramp.color_ramp.elements[1].position=.85
    ramp.color_ramp.elements[0].color=tuple(c*.94 for c in color)+(1,)
    ramp.color_ramp.elements[1].color=tuple(c*1.06 for c in color)+(1,);l.new(noise.outputs['Fac'],ramp.inputs[0])
    lum=n.new('ShaderNodeRGBToBW');l.new(original,lum.inputs[0])
    gate=n.new('ShaderNodeMapRange');gate.clamp=True;gate.interpolation_type='SMOOTHERSTEP'
    gate.inputs['From Min'].default_value=.07;gate.inputs['From Max'].default_value=.23;l.new(lum.outputs[0],gate.inputs['Value'])
    keep=math_node('MULTIPLY',attr('MF_skin_face_retention'),math_node('MAXIMUM',gate.outputs['Result'],attr('MF_skin_feature_retention')))
    if candidate>=2:keep=attr('MF_skin_face_retention')
    mix=n.new('ShaderNodeMixRGB');l.new(keep,mix.inputs[0]);l.new(ramp.outputs[0],mix.inputs[1]);l.new(original,mix.inputs[2]);l.new(mix.outputs[0],p.inputs['Base Color'])
    p.inputs['IOR'].default_value=1.4;p.inputs['Roughness'].default_value=.68;p.inputs['Specular IOR Level'].default_value=.25
    p.inputs['Subsurface Weight'].default_value=.025;p.inputs['Subsurface Scale'].default_value=.015
    return {'reference_sample_count':len(samples),'reference_encoded':encoded,'reference_linear':color,
        'face_detail':'Original accepted facial color retained by spatial/feature masks; non-skin scalp/nape and lower neck replaced',
        'geometry_changed':False,'candidate':candidate}


def render(out,emission=False):
    import bpy
    from hijab_donor import review
    ob=bpy.data.objects['MF_continuous_head_neck'];ob.hide_set(False)
    for o in bpy.context.scene.objects:
        if o.type in ('MESH','CURVE'):o.hide_render=o!=ob
    if emission:
        mat=ob.data.materials[0].copy();ob.data.materials[0]=mat
        n,l=mat.node_tree.nodes,mat.node_tree.links
        p=next(n for n in n if n.type=='BSDF_PRINCIPLED')
        em=n.new('ShaderNodeEmission');em.inputs['Strength'].default_value=1
        if p.inputs['Base Color'].is_linked:l.new(p.inputs['Base Color'].links[0].from_socket,em.inputs['Color'])
        else:em.inputs['Color'].default_value=p.inputs['Base Color'].default_value
        output=next(n for n in n if n.type=='OUTPUT_MATERIAL' and n.is_active_output)
        l.new(em.outputs[0],output.inputs['Surface'])
    review(bpy.context.scene,out,(0,-.1,-.55),4.8,VIEWS)


def run(job):
    out=validate(job)
    import bpy
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE),load_ui=False,use_scripts=False)
    before=protected_state();out.mkdir()
    result={'job':job,'source_sha256':SOURCE_SHA,'handler_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'anatomy_director_accepted':True,'skin_director_accepted':False}
    if job['operation']=='build':
        result['material_edit']=skin_material(job['candidate'])
        assert protected_state()==before,'Geometry or other objects changed'
        native=out/'character-upperbody.blend';bpy.ops.wm.save_as_mainfile(filepath=str(native))
        result['native_sha256']=hashlib.sha256(native.read_bytes()).hexdigest()
    elif job['candidate']>0:
        folder=BASE/f'bust-skin-build-{job["candidate"]:02}';native=folder/'character-upperbody.blend'
        record=json.loads((folder/'result.json').read_text())
        if hashlib.sha256(native.read_bytes()).hexdigest()!=record['native_sha256']:raise ValueError('Candidate changed')
        bpy.ops.wm.open_mainfile(filepath=str(native),load_ui=False,use_scripts=False)
        result['native_sha256']=record['native_sha256']
    ob=bpy.data.objects['MF_continuous_head_neck']
    result['materials']=[material_record(m) for m in ob.data.materials]
    if job['candidate']>0 and job['operation']!='build':
        assert json.loads(json.dumps(result['materials']))==record['materials'],'Material recipe changed on reopen'
    result['images']=[{'name':im.name,'size':list(im.size),'colorspace':im.colorspace_settings.name,
            'packed':bool(im.packed_file or im.packed_files)} for im in bpy.data.images if im.source=='FILE']
    assert all(im['packed'] for im in result['images']),'Unpacked image dependency'
    assert protected_state()==before,'Protected state changed'
    result['protected_state']=before
    if job['operation'] not in ('verify','verify-final'):render(out,job['operation']=='emission')
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==SOURCE_SHA
    (out/'result.json').write_text(json.dumps(result,indent=2))


if __name__=='__main__':
    sys.path.insert(0,str(Path(__file__).resolve().parent))
    args=sys.argv[sys.argv.index('--')+1:]
    if len(args)!=1:raise ValueError('One structured job required')
    run(json.loads(Path(args[0]).read_text()))
