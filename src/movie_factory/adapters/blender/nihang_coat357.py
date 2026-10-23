"""Fixed horse short-coat proof, dominant surface-area slot only, no action edits."""
import json,importlib.util
from collections import Counter
from pathlib import Path

def coat_slot(rows):
    counts=Counter()
    for index,area in rows:counts[index]+=area
    slot,count=counts.most_common(1)[0]
    if count/sum(counts.values())<.65:raise ValueError('COAT357_AMBIGUOUS_SKIN_SLOT')
    return slot

def run(bpy,out):
    s=importlib.util.spec_from_file_location('tack354',Path(__file__).with_name('nihang_tack354.py'));h=importlib.util.module_from_spec(s);s.loader.exec_module(h)
    sig=h.action_signature(bpy);rig=bpy.data.objects['MF coherent Nihang rig'];horse=bpy.data.objects['horse']
    if not rig.get('fabric357') or rig.get('coat357'):raise ValueError('COAT357_PARENT')
    slot=coat_slot([(p.material_index,p.area) for p in horse.data.polygons]);mat=horse.data.materials[slot].copy();horse.data.materials[slot]=mat;mat.name='357 dark bay directional short coat'
    n=mat.node_tree.nodes;l=mat.node_tree.links;bs=next(x for x in n if x.type=='BSDF_PRINCIPLED')
    for key in ('Base Color','Normal','Roughness'):
        for link in list(bs.inputs[key].links):l.remove(link)
    tc=n.new('ShaderNodeTexCoord');scale=n.new('ShaderNodeVectorMath');scale.operation='SCALE';scale.inputs[3].default_value=4;l.new(tc.outputs['UV'],scale.inputs[0])
    texture=Path(__file__).resolve().parents[4]/'.runtime/art-direction/series01-entrance-art188/horse-coat-v01.png'
    tex=n.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(texture),check_existing=True);tex.image.pack();tex.extension='REPEAT';l.new(scale.outputs[0],tex.inputs[0])
    bw=n.new('ShaderNodeRGBToBW');l.new(tex.outputs['Color'],bw.inputs[0])
    norm=n.new('ShaderNodeMapRange');norm.inputs['From Min'].default_value=.025;norm.inputs['From Max'].default_value=.30;norm.clamp=True;l.new(bw.outputs[0],norm.inputs[0])
    ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].color=(.015,.007,.003,1);ramp.color_ramp.elements[1].color=(.090,.043,.018,1)
    l.new(norm.outputs[0],ramp.inputs[0]);l.new(ramp.outputs[0],bs.inputs['Base Color'])
    bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.28;bump.inputs['Distance'].default_value=.0012;l.new(bw.outputs[0],bump.inputs['Height']);l.new(bump.outputs[0],bs.inputs['Normal'])
    rough=n.new('ShaderNodeMapRange');rough.inputs['To Min'].default_value=.62;rough.inputs['To Max'].default_value=.82;l.new(norm.outputs[0],rough.inputs[0]);l.new(rough.outputs[0],bs.inputs['Roughness'])
    bs.inputs['Metallic'].default_value=0;bs.inputs['Specular IOR Level'].default_value=.20;bs.inputs['Sheen Weight'].default_value=.18
    changes=[]
    for mod in horse.modifiers:
        if mod.type=='SUBSURF':changes.append(dict(name=mod.name,before=mod.render_levels));mod.render_levels=max(2,mod.render_levels)
    rig['coat357']=1;bpy.context.view_layer.update()
    if h.action_signature(bpy)!=sig:raise ValueError('COAT357_ACTION_DRIFT')
    report=dict(changed=True,source_preserved=True,actions_unchanged=True,action_signature=sig,skin_slot=slot,slot_counts=dict(Counter(p.material_index for p in horse.data.polygons)),subdivision=changes,texture=str(texture),uv_scale=4,scope='Dominant skin surface only; eyes, mouth and hoof slots retained. Reused authored188 texture structure, not hue; shader finish not fur simulation. Actual head and production checks required.')
    (out/'coat357.json').write_text(json.dumps(report,indent=2)+'\n');return report
