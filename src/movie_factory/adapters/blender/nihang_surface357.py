"""Bounded supporting face finish: owned pigment, natural brow flow, no shape edits."""
import json,math,importlib.util
from pathlib import Path
import numpy as np

def brow_path(root,side,index):
    r=np.asarray(root,dtype=float);t=np.linspace(0,1,7)
    u=min(1,max(0,(abs(r[0])-.008)/.05));length=.0055+.0015*math.sin(index*2.399)
    p=np.tile(r,(7,1));p[:,0]+=side*length*t
    p[:,1]-=.0007*np.sin(np.pi*t)
    p[:,2]+=(.0022*(1-u)-.0011*u)*t
    return p

def run(bpy,out):
    s=importlib.util.spec_from_file_location('tack354',Path(__file__).with_name('nihang_tack354.py'));h=importlib.util.module_from_spec(s);s.loader.exec_module(h)
    sig=h.action_signature(bpy);rig=bpy.data.objects['MF coherent Nihang rig'];body=bpy.data.objects['MF coherent Nihang body']
    if not rig.get('groom357') or rig.get('surface357'):raise ValueError('SURFACE357_PARENT')
    skin=body.data.materials[0].copy();body.data.materials[0]=skin;skin.name='357 warm weathered pigment'
    n=skin.node_tree.nodes;l=skin.node_tree.links;bs=next(x for x in n if x.type=='BSDF_PRINCIPLED')
    old=bs.inputs['Base Color'].links[0].from_socket
    tc=n.new('ShaderNodeTexCoord');coarse=n.new('ShaderNodeTexNoise');coarse.inputs['Scale'].default_value=46;coarse.inputs['Detail'].default_value=4
    l.new(tc.outputs['Object'],coarse.inputs['Vector'])
    palette=n.new('ShaderNodeValToRGB');palette.color_ramp.elements[0].position=.2;palette.color_ramp.elements[0].color=(.185,.077,.030,1)
    palette.color_ramp.elements[1].position=.8;palette.color_ramp.elements[1].color=(.315,.162,.077,1);l.new(coarse.outputs['Fac'],palette.inputs[0])
    # Keep a fraction of the inspected featureless source pigment. The palette
    # restores value/chroma without importing another protagonist's features.
    blend=n.new('ShaderNodeMixRGB');blend.inputs[0].default_value=.78;l.new(old,blend.inputs[1]);l.new(palette.outputs[0],blend.inputs[2]);l.new(blend.outputs[0],bs.inputs['Base Color'])
    fine=n.new('ShaderNodeTexNoise');fine.inputs['Scale'].default_value=1100;fine.inputs['Detail'].default_value=2.5;l.new(tc.outputs['Object'],fine.inputs['Vector'])
    bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.22;bump.inputs['Distance'].default_value=.00014
    if bs.inputs['Normal'].is_linked:l.new(bs.inputs['Normal'].links[0].from_socket,bump.inputs['Normal'])
    l.new(fine.outputs['Fac'],bump.inputs['Height']);l.new(bump.outputs[0],bs.inputs['Normal'])
    rough=n.new('ShaderNodeMapRange');rough.inputs['To Min'].default_value=.46;rough.inputs['To Max'].default_value=.65;l.new(coarse.outputs['Fac'],rough.inputs[0]);l.new(rough.outputs[0],bs.inputs['Roughness'])
    bs.inputs['Specular IOR Level'].default_value=.25;bs.inputs['Subsurface Weight'].default_value=.035
    brows=[];rng=np.random.default_rng(35777)
    for ob in rig.children_recursive:
        if not ob.name.startswith('brow.') or ob.type!='CURVE':continue
        roots=[np.array(s.points[0].co[:3]) for s in ob.data.splines if len(s.points)]
        if len(roots)<50:raise ValueError('SURFACE357_BROW_ROOTS')
        data=bpy.data.curves.new('357 overlapping brow fibers '+ob.name,'CURVE');data.dimensions='3D';data.bevel_depth=.00019;data.bevel_resolution=1
        mat=bpy.data.materials.new('357 brow dark chestnut');mat.use_nodes=True;p=mat.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(.017,.009,.004,1);p.inputs['Roughness'].default_value=.52;data.materials.append(mat)
        for i,r in enumerate(roots):
            side=1 if r[0]>=0 else -1
            for j in range(4):
                root=r+np.array([rng.uniform(-.0007,.0007),-.0002,rng.uniform(-.0011,.0011)])
                pts=brow_path(root,side,i*4+j);s=data.splines.new('POLY');s.points.add(len(pts)-1)
                for k,(p,co) in enumerate(zip(s.points,pts)):p.co=(*co,1);p.radius=(.8+.3*rng.random())*(1-.92*k/(len(pts)-1))
        ob.data=data;brows.append(dict(name=ob.name,strands=len(data.splines)))
    if len(brows)!=2:raise ValueError('SURFACE357_BROW_COUNT')
    rig['surface357']=1;bpy.context.view_layer.update()
    if h.action_signature(bpy)!=sig:raise ValueError('SURFACE357_ACTION_DRIFT')
    report=dict(changed=True,source_preserved=True,actions_unchanged=True,action_signature=sig,brows=brows,scope='Supporting face material/brow proof. Shape, source pigment, attachments and actions preserved; no whole actor or AV pass.')
    (out/'surface357.json').write_text(json.dumps(report,indent=2)+'\n');return report
