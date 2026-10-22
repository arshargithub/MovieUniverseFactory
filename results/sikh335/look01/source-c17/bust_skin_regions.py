"""Bounded local projected-hair cleanup and nonrepeating illustrated infill."""
import hashlib
import json
from pathlib import Path
import shutil
import sys

ROOT=Path(__file__).resolve().parents[4]
BASE=ROOT/'.runtime/art-direction/series01-facebuilder-trial-01'
SOURCE=BASE/'posterior-neck-build-16/character-upperbody.blend'
SOURCE_SHA='76b2a6c7f4f1c2288ed746ebb3cf146b4146650058e263c6dd16b6f9225ef080'

def smooth(t):
    t=max(0.,min(1.,t));return t*t*(3-2*t)

def temple_weight(x,y,z):
    ax=abs(x);upper_brow=.54-.22*min(ax/.75,1.)**2
    return smooth((z-upper_brow)/.08)*smooth((ax-.38)/.14)*smooth((.88-ax)/.10)*smooth((-.16-y)/.30)

def temple_weight_lower(x,y,z):
    ax=abs(x);upper_brow=.48-.23*min(ax/.75,1.)**2
    return smooth((z-upper_brow)/.07)*smooth((ax-.45)/.15)*smooth((.88-ax)/.10)*smooth((-.16-y)/.30)

def face_weight(x,y,z):
    ax=abs(x)
    top=.89-.50*min(ax/.85,1.)**1.7
    bottom=-.86+.32*min(ax/.80,1.)**2
    return smooth((top-z)/.19)*smooth((z-bottom)/.14)*smooth((-.26-y)/.40)*smooth((.85-ax)/.28)

def validate(job):
    if not isinstance(job,dict) or set(job)!={'operation','candidate'}:raise ValueError('Exact keys required')
    if job['operation'] not in ('build','emission','portraits','verify') or type(job['candidate']) is not int or job['candidate'] not in (1,2,3):raise ValueError('Unsupported job')
    if SOURCE.is_symlink() or hashlib.sha256(SOURCE.read_bytes()).hexdigest()!=SOURCE_SHA:raise ValueError('Pinned source changed')
    out=BASE/f'bust-region-{job["operation"]}-{job["candidate"]:02}'
    if out.exists() or shutil.disk_usage(BASE).free<5_000_000_000:raise ValueError('Existing output or disk low')
    return out

def material(candidate):
    import bpy
    ob=bpy.data.objects['MF_continuous_head_neck'];assert ob.data.users==1
    prior_mix=None
    if candidate==3:
        # Isolate the localized fix from the rejected whole-bust alternatives.
        # Retain detail07's (still unaccepted) body treatment for a controlled comparison.
        from bust_skin_detail import texture_material
        texture_material(7);mat=ob.data.materials[0]
        prior_mix=mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].links[0].from_node
    else:
        mat=ob.data.materials[0].copy();ob.data.materials[0]=mat
    mat.name=f'MF_region_skin_{candidate:02}'
    n,l=mat.node_tree.nodes,mat.node_tree.links;p=n['Principled BSDF'];original=n['Mix (Legacy).001'].outputs['Color']
    for name,fn in (('MF_face_retained',face_weight),('MF_temple_cleanup',temple_weight if candidate==1 else temple_weight_lower)):
        a=ob.data.attributes.new(name,'FLOAT','POINT')
        for v,d in zip(ob.data.vertices,a.data):d.value=fn(*v.co)
    def node(kind):return n.new('ShaderNode'+kind)
    def math(op,a,b=0):
        q=node('Math');q.operation=op
        for i,v in enumerate((a,b)):
            if isinstance(v,(int,float)):q.inputs[i].default_value=v
            else:l.new(v,q.inputs[i])
        return q.outputs[0]
    def attr(name):
        q=node('Attribute');q.attribute_name=name;return q.outputs['Fac']
    def mix(a,b,f):
        q=node('MixRGB')
        if isinstance(f,(int,float)):q.inputs[0].default_value=f
        else:l.new(f,q.inputs[0])
        for i,v in enumerate((a,b),1):
            if isinstance(v,tuple):q.inputs[i].default_value=v
            else:l.new(v,q.inputs[i])
        return q.outputs[0]
    coords=node('TexCoord');xyz=node('SeparateXYZ');l.new(coords.outputs['Object'],xyz.inputs[0])
    # One bounded, nonrepeating projection of clean forehead skin for each temple.
    uv=node('CombineXYZ')
    u=math('ADD',.470 if candidate==3 else .445,math('MULTIPLY',math('MINIMUM',math('MAXIMUM',math('DIVIDE',math('SUBTRACT',math('ABSOLUTE',xyz.outputs['X']),.38),.5),0),1),.065 if candidate==3 else .13))
    v=math('SUBTRACT',1,math('DIVIDE',math('MINIMUM',math('MAXIMUM',math('SUBTRACT',420,math('MULTIPLY',math('SUBTRACT',xyz.outputs['Z'],.40),60 if candidate==3 else 150)),390 if candidate==3 else 360),423),1647))
    l.new(u,uv.inputs[0]);l.new(v,uv.inputs[1])
    tex=node('TexImage');tex.image=bpy.data.images['frontal-v02-individualized.png'];tex.extension='EXTEND';l.new(uv.outputs[0],tex.inputs['Vector'])
    cleaned=mix(original,tex.outputs['Color'],attr('MF_temple_cleanup'))
    # Aperiodic cells supply paint-like tonal facets, not tiled portrait fragments.
    vor=node('TexVoronoi');vor.feature='F1';vor.distance='EUCLIDEAN';vor.inputs['Scale'].default_value=25
    if candidate>=2:
        vor.feature='SMOOTH_F1';vor.inputs['Smoothness'].default_value=.30
    l.new(coords.outputs['Object'],vor.inputs['Vector'])
    bw=node('RGBToBW');l.new(vor.outputs['Color'],bw.inputs[0])
    ramp=node('ValToRGB');ramp.color_ramp.interpolation='LINEAR'
    ramp.color_ramp.elements[0].position=.15;ramp.color_ramp.elements[1].position=.85
    base=(.68,.30,.16)
    spread=.17 if candidate==1 else .12
    ramp.color_ramp.elements[0].color=tuple(c*(1-spread) for c in base)+(1,)
    ramp.color_ramp.elements[1].color=tuple(c*(1+spread) for c in base)+(1,)
    l.new(bw.outputs[0],ramp.inputs[0])
    noise=node('TexNoise');noise.inputs['Scale'].default_value=90;noise.inputs['Detail'].default_value=2;l.new(coords.outputs['Object'],noise.inputs['Vector'])
    grain=node('ValToRGB');grain.color_ramp.elements[0].color=tuple(c*.96 for c in base)+(1,);grain.color_ramp.elements[1].color=tuple(c*1.04 for c in base)+(1,);l.new(noise.outputs['Fac'],grain.inputs[0])
    infill=mix(ramp.outputs[0],grain.outputs[0],.15)
    if candidate==3:
        l.new(cleaned,prior_mix.inputs[2]);l.new(prior_mix.outputs[0],p.inputs['Base Color'])
    else:l.new(mix(infill,cleaned,attr('MF_face_retained')),p.inputs['Base Color'])
    return {'candidate':candidate,'method':'Localized temple cleanup on unchanged detail07 texture treatment' if candidate==3 else 'Source-face preservation, local nonrepeating forehead donor for projected hair, aperiodic native painted-facet infill',
        'whole_bust_style_resolved':False,
        'not_claimed':'Exact reproduction of source texture or fully de-lit albedo','geometry_changed':False}

def run(job):
    out=validate(job)
    import bpy
    from bust_skin_review import protected_state,material_record,render
    from bust_skin_detail import render_portraits
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE),load_ui=False,use_scripts=False)
    before=protected_state();out.mkdir()
    result={'job':job,'source_sha256':SOURCE_SHA,'handler_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'skin_director_accepted':False}
    if job['operation']=='build':
        result['edit']=material(job['candidate']);assert protected_state()==before
        native=out/'character-upperbody.blend';bpy.ops.wm.save_as_mainfile(filepath=str(native));result['native_sha256']=hashlib.sha256(native.read_bytes()).hexdigest()
    else:
        folder=BASE/f'bust-region-build-{job["candidate"]:02}';native=folder/'character-upperbody.blend';record=json.loads((folder/'result.json').read_text())
        if native.is_symlink() or hashlib.sha256(native.read_bytes()).hexdigest()!=record['native_sha256']:raise ValueError('Candidate changed')
        bpy.ops.wm.open_mainfile(filepath=str(native),load_ui=False,use_scripts=False);result['native_sha256']=record['native_sha256']
    result['materials']=[material_record(m) for m in bpy.data.objects['MF_continuous_head_neck'].data.materials]
    if job['operation']!='build':assert json.loads(json.dumps(result['materials']))==record['materials']
    assert protected_state()==before;result['protected_state']=before
    result['images']=[{'name':im.name,'packed':bool(im.packed_file or im.packed_files)} for im in bpy.data.images if im.source=='FILE']
    assert all(im['packed'] for im in result['images'])
    if job['operation']=='portraits':render_portraits(out)
    elif job['operation']!='verify':render(out,job['operation']=='emission')
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==SOURCE_SHA
    (out/'result.json').write_text(json.dumps(result,indent=2))

if __name__=='__main__':
    sys.path.insert(0,str(Path(__file__).resolve().parent))
    args=sys.argv[sys.argv.index('--')+1:]
    if len(args)!=1:raise ValueError('One structured job required')
    run(json.loads(Path(args[0]).read_text()))
