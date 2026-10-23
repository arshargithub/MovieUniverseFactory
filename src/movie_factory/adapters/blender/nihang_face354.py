"""Face-following beard and owned pigment-scale proof, not identity replacement."""
import json,math,hashlib,importlib.util
from pathlib import Path
import numpy as np

def free_length(root_z,eye,index):
    # Cheek hairs remain close; chin/jaw carry the beard's free length.
    lower=max(0,min(1,(eye-.072-root_z)/.055))
    return .018+.060*lower+.007*math.sin(index*2.399)

def run(bpy,out):
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    spec=importlib.util.spec_from_file_location('tack354',Path(__file__).with_name('nihang_tack354.py'));helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper)
    actions=helper.action_signature(bpy)
    rig=bpy.data.objects['MF coherent Nihang rig'];body=bpy.data.objects['MF coherent Nihang body'];beard=bpy.data.objects['MF347 integrated beard and moustache']
    if not rig.get('tack354') or rig.get('face354'):raise ValueError('FACE354_PARENT')
    state=rig.data.pose_position;rig.data.pose_position='REST';bpy.context.view_layer.update()
    ev=body.evaluated_get(bpy.context.evaluated_depsgraph_get());local=rig.matrix_world.inverted()@body.matrix_world
    tree=BVHTree.FromPolygons([local@v.co for v in ev.data.vertices],[tuple(p.vertices) for p in ev.data.polygons])
    eye=rig.data.bones['eye.L'].head_local.z;chin=eye-.133;beard.data=beard.data.copy();supported=0;count=0
    for i,s in enumerate(beard.data.splines):
        if len(s.points)!=14:continue
        root=Vector(s.points[0].co[:3]);length=free_length(root.z,eye,i);phase=round(root.x/.012)*1.7
        last_y=root.y
        for j,p in enumerate(s.points):
            t=j/(len(s.points)-1);x=root.x*(1-.16*t)+.0035*math.sin(phase+9*t)*math.sin(math.pi*t)
            z=root.z-length*t
            hit=tree.ray_cast(Vector((x,-.6,z)),Vector((0,1,0)))[0] if z>chin else None
            if hit is not None and hit.y<-.025:
                y=hit.y-.0025-.002*math.sin(math.pi*t);last_y=y;supported+=1
            else:y=last_y-.009*t+.002*math.sin(phase+11*t)*math.sin(math.pi*t)
            if j==0:p.co=(*root,1)
            else:p.co=(x,y,z,1)
            p.radius=max(.025,(1-t)**.65)*(.45+.55*min(1,t/.18))
        count+=1
    # Small overlapping lip hairs fill the abrupt two-wing separation without
    # changing nose/lips/face anatomy. New hairs use the same data and owner.
    rng=np.random.default_rng(35472);added=0
    for i in range(420):
        x=float(rng.uniform(-.033,.033));z=eye-.067-float(rng.uniform(0,.006))
        hit=tree.ray_cast(Vector((x,-.6,z)),Vector((0,1,0)))[0]
        if hit is None:continue
        root=hit+Vector((0,-.002,0));s=beard.data.splines.new('POLY');s.points.add(7);side=1 if x>=0 else -1
        for j,p in enumerate(s.points):
            t=j/7;p.co=(*(root+Vector((side*.004*t,-.0015*math.sin(math.pi*t),-.007*t))),1);p.radius=.65*(1-t)+.025
        added+=1
    rig.data.pose_position=state;bpy.context.view_layer.update()
    skin=body.data.materials[0].copy();body.data.materials[0]=skin;skin.name='354 owned skin pigment visible scale'
    n=skin.node_tree.nodes;l=skin.node_tree.links;bs=next(x for x in n if x.type=='BSDF_PRINCIPLED')
    image=next(x.image for x in n if x.type=='TEX_IMAGE' and x.image)
    tc=n.new('ShaderNodeTexCoord');scale=n.new('ShaderNodeVectorMath');scale.operation='MULTIPLY';scale.inputs[1].default_value=(9,9,1);l.new(tc.outputs['UV'],scale.inputs[0])
    frac=n.new('ShaderNodeVectorMath');frac.operation='FRACTION';l.new(scale.outputs[0],frac.inputs[0])
    crop=n.new('ShaderNodeVectorMath');crop.operation='MULTIPLY';crop.inputs[1].default_value=(.23,.23,0);l.new(frac.outputs[0],crop.inputs[0])
    offset=n.new('ShaderNodeVectorMath');offset.operation='ADD';offset.inputs[1].default_value=(.01,.75,0);l.new(crop.outputs[0],offset.inputs[0])
    tex=n.new('ShaderNodeTexImage');tex.image=image;tex.extension='EXTEND';l.new(offset.outputs[0],tex.inputs[0])
    tint=n.new('ShaderNodeMixRGB');tint.blend_type='MULTIPLY';tint.inputs[0].default_value=1;tint.inputs[2].default_value=(.58,.65,.70,1);l.new(tex.outputs['Color'],tint.inputs[1]);l.new(tint.outputs[0],bs.inputs['Base Color'])
    bs.inputs['Roughness'].default_value=.55;bs.inputs['Specular IOR Level'].default_value=.25
    bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.17;bump.inputs['Distance'].default_value=.00045;l.new(tex.outputs['Color'],bump.inputs['Height']);l.new(bump.outputs[0],bs.inputs['Normal'])
    rig['face354']=1;bpy.context.view_layer.update()
    if helper.action_signature(bpy)!=actions:raise ValueError('FACE354_ACTION_DRIFT')
    report=dict(changed=True,source_preserved=True,actions_unchanged=True,action_signature=actions,face_supported_points=supported,beard_curves=count,lip_overlap_curves=added,texture_crop=[.01,.75,.24,.98],scope='Existing featureless pigment only; no Pashtun features/identity mapped. Material/root proof, not whole actor or AV pass.')
    (out/'face354.json').write_text(json.dumps(report,indent=2)+'\n');return report
