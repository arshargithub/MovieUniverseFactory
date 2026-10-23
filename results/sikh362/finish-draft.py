"""Prepared fixed supporting finish; must be reviewed/admitted before native use."""
import json,math,importlib.util
from pathlib import Path
import numpy as np

def crown_point(p,center_y):
    x,y,z=map(float,p);a=math.atan2(x,y-center_y)
    # One common bounded deformation for core, courses and gathered cap: no
    # independently displaced bands, no compression of the fitted brow edge.
    if z>.225:z=.225+.028*math.tanh((z-.225)/.028)
    w=max(0.,min(1.,(z-.065)/.07));w=w*w*(3-2*w)
    dr=w*(.0010*math.sin(9*a+17*z)+.0006*math.sin(17*a-33*z))
    return x+dr*math.sin(a),y+dr*math.cos(a),z

def fabric(bpy,ob,index):
    old=ob.data.materials[index]
    if old is None or not old.use_nodes:return
    material=old.copy();ob.data.materials[index]=material;material.name='362 woven cloth '+ob.name
    n=material.node_tree.nodes;l=material.node_tree.links;bs=next(x for x in n if x.type=='BSDF_PRINCIPLED')
    previous=bs.inputs['Normal'].links[0].from_socket if bs.inputs['Normal'].is_linked else None
    attribute=ob.data.attributes.get('MF362 attached textile') or ob.data.attributes.new('MF362 attached textile','FLOAT_VECTOR','POINT')
    for datum,vertex in zip(attribute.data,ob.data.vertices):datum.vector=vertex.co
    rest=n.new('ShaderNodeAttribute');rest.attribute_name=attribute.name
    waves=[]
    for direction,scale in [('X',1750),('Z',1920)]:
        wave=n.new('ShaderNodeTexWave');wave.wave_type='BANDS';wave.bands_direction=direction
        wave.inputs['Scale'].default_value=scale;wave.inputs['Distortion'].default_value=1.2;wave.inputs['Detail Scale'].default_value=2.7
        l.new(rest.outputs['Vector'],wave.inputs['Vector']);waves.append(wave)
    cross=n.new('ShaderNodeMath');cross.operation='MULTIPLY';l.new(waves[0].outputs['Fac'],cross.inputs[0]);l.new(waves[1].outputs['Fac'],cross.inputs[1])
    bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.22;bump.inputs['Distance'].default_value=.00028
    l.new(cross.outputs[0],bump.inputs['Height'])
    if previous:l.new(previous,bump.inputs['Normal'])
    l.new(bump.outputs['Normal'],bs.inputs['Normal']);bs.inputs['Specular IOR Level'].default_value=.16
    bs.inputs['Sheen Weight'].default_value=.10
    # Existing dye/pigment keeps its palette, rest coordinates and forms.
    return material.name

def pigment_range(material):
    """Match the measured linear luminance domain, not sRGB intuition.

    Bound source-crop linear percentiles: p1=.298, p50=.345,p99=.389.
    The old .16.. .34 map clamps over half the crop to one multiplier.
    """
    count=0
    for node in material.node_tree.nodes:
        if node.type!='MAP_RANGE':continue
        if abs(node.inputs['From Min'].default_value-.16)<1e-6 and abs(node.inputs['From Max'].default_value-.34)<1e-6:
            node.inputs['From Min'].default_value=.295;node.inputs['From Max'].default_value=.390;count+=1
    return count

def run(bpy,out):
    spec=importlib.util.spec_from_file_location('tack354',Path(__file__).with_name('nihang_tack354.py'));helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper)
    sig=helper.action_signature(bpy);rig=bpy.data.objects['MF coherent Nihang rig']
    if not rig.get('look361') or rig.get('finish362'):raise ValueError('FINISH362_PARENT')
    crowns=[ob for ob in rig.children_recursive if ob.type=='MESH' and ob.name.startswith(('MF Nihang wrapped crown core','MF Nihang overlapped cloth','MF Nihang gathered crown'))]
    if len(crowns)!=8:raise ValueError('FINISH362_CROWN_SET')
    core=next(ob for ob in crowns if ob.name.startswith('MF Nihang wrapped crown core'))
    center_y=(min(v.co.y for v in core.data.vertices)+max(v.co.y for v in core.data.vertices))/2
    if not -.1<center_y<.05:raise ValueError('FINISH362_CROWN_COORDINATES')
    records=[]
    for ob in crowns:
        if ob.data.shape_keys:raise ValueError('FINISH362_UNSUPPORTED_CROWN_KEYS')
        ob.data=ob.data.copy();old=np.array([v.co[:] for v in ob.data.vertices]);new=np.array([crown_point(p,center_y) for p in old])
        movement=np.linalg.norm(new-old,axis=1)
        if movement.max()>.060 or not np.isfinite(new).all():raise ValueError('FINISH362_CROWN_BOUND')
        ob.data.vertices.foreach_set('co',new.astype('f4').ravel());ob.data.update()
        records.append(dict(name=ob.name,maximum_displacement=float(movement.max()),bounds_before=[old.min(0).tolist(),old.max(0).tolist()],bounds_after=[new.min(0).tolist(),new.max(0).tolist()]))
    cloth=[ob for ob in rig.children_recursive if ob.type=='MESH' and not ob.hide_render and ob.name.startswith(('MF coherent coat','MF coherent split chola','MF coherent shoulder sash','MF coherent waist wrap'))]+crowns
    materials=[]
    for ob in cloth:
        for index in range(len(ob.data.materials)):materials.append(dict(object=ob.name,material=fabric(bpy,ob,index)))
    grain=[]
    for ob in cloth+[bpy.data.objects['MF coherent Nihang body']]:
        for index,old in enumerate(list(ob.data.materials)):
            if ob.name=='MF coherent Nihang body' and index!=0:continue
            material=old.copy();ob.data.materials[index]=material
            grain.append(dict(object=ob.name,range_nodes=pigment_range(material)))
    if helper.action_signature(bpy)!=sig:raise ValueError('FINISH362_ACTION_DRIFT')
    rig['finish362']=1;bpy.context.view_layer.update()
    report=dict(actions_unchanged=True,action_signature=sig,crown=records,textiles=materials,grain=grain,scope='Same head owner, lower fitted crown and established palette preserved; upper crown rounding, attached textile relief and measured pigment range. Actual same-film and animation review required; not simulation or acceptance.')
    (out/'finish362.json').write_text(json.dumps(report,indent=2)+'\n');return report
