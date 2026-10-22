"""Reuse approved cloth brush character through bounded native shader mapping.

No raster is edited/generated. Sample only the lower cloth region, never her face.
Brush-value modulation augments physical cloth construction; it cannot pass fit.
"""
from pathlib import Path

REFERENCE=Path(__file__).resolve().parents[4]/'.runtime/art-direction/series01-pashtun-baseline-v01/frontal-v02-individualized.png'
SHA='7f959fed6ca4f57cb1b7fdaa20aa4a0fdd64208595a8b5debd8d060c79068c75'


def pingpong(x):return 1-abs(x%2-1)


def fabric_uv(x,z):
    return (.22+.56*pingpong(.31*x+.10),.02+.18*pingpong(.37*z),0.)


def augment(mat,amount=.45):
    import bpy
    from wardrobe_riding_fit import digest
    if REFERENCE.is_symlink() or digest(REFERENCE)!=SHA:raise ValueError('Approved cloth reference changed')
    nodes=mat.node_tree.nodes;links=mat.node_tree.links;bsdf=nodes.get('Principled BSDF')
    prior=bsdf.inputs['Base Color'].links[0].from_socket
    coord=nodes.new('ShaderNodeAttribute');coord.attribute_name='MF_173_material_coords'
    separate=nodes.new('ShaderNodeSeparateXYZ');links.new(coord.outputs['Vector'],separate.inputs[0])
    combined=nodes.new('ShaderNodeCombineXYZ')
    for axis,scale,offset,span,low in [('X',.31,.10,.56,.22),('Z',.37,0.,.18,.02)]:
        multiply=nodes.new('ShaderNodeMath');multiply.operation='MULTIPLY';multiply.inputs[1].default_value=scale;links.new(separate.outputs[axis],multiply.inputs[0])
        add=nodes.new('ShaderNodeMath');add.operation='ADD';add.inputs[1].default_value=offset;links.new(multiply.outputs[0],add.inputs[0])
        fold=nodes.new('ShaderNodeMath');fold.operation='PINGPONG';fold.inputs[1].default_value=1.;links.new(add.outputs[0],fold.inputs[0])
        span_node=nodes.new('ShaderNodeMath');span_node.operation='MULTIPLY';span_node.inputs[1].default_value=span;links.new(fold.outputs[0],span_node.inputs[0])
        region=nodes.new('ShaderNodeMath');region.operation='ADD';region.inputs[1].default_value=low;links.new(span_node.outputs[0],region.inputs[0]);links.new(region.outputs[0],combined.inputs['X' if axis=='X' else 'Y'])
    image=bpy.data.images.load(str(REFERENCE),check_existing=True)
    samples=[]
    for dx,dy in [(0,0),(-.012,-.012),(-.012,.012),(.012,-.012),(.012,.012),(-.012,0),(.012,0),(0,-.012),(0,.012)]:
        shifted=nodes.new('ShaderNodeVectorMath');shifted.operation='ADD';shifted.inputs[1].default_value=(dx,dy,0);links.new(combined.outputs[0],shifted.inputs[0])
        tex=nodes.new('ShaderNodeTexImage');tex.image=image;tex.extension='EXTEND';links.new(shifted.outputs[0],tex.inputs['Vector'])
        value=nodes.new('ShaderNodeRGBToBW');links.new(tex.outputs['Color'],value.inputs[0]);samples.append(value.outputs[0])
    total=samples[1]
    for sample in samples[2:]:
        add=nodes.new('ShaderNodeMath');add.operation='ADD';links.new(total,add.inputs[0]);links.new(sample,add.inputs[1]);total=add.outputs[0]
    mean=nodes.new('ShaderNodeMath');mean.operation='MULTIPLY';mean.inputs[1].default_value=1/8;links.new(total,mean.inputs[0])
    detail=nodes.new('ShaderNodeMath');detail.operation='SUBTRACT';links.new(samples[0],detail.inputs[0]);links.new(mean.outputs[0],detail.inputs[1])
    modulate=nodes.new('ShaderNodeMapRange');modulate.clamp=True
    for name,v in [('From Min',-.014),('From Max',.014),('To Min',.65),('To Max',1.35)]:modulate.inputs[name].default_value=v
    links.new(detail.outputs[0],modulate.inputs['Value'])
    paint=nodes.new('ShaderNodeMixRGB');paint.blend_type='MULTIPLY';paint.inputs[0].default_value=amount;links.new(prior,paint.inputs[1]);links.new(modulate.outputs[0],paint.inputs[2]);links.new(paint.outputs[0],bsdf.inputs['Base Color'])
    mat['art_direction_source']='Approved frontal-v02 lower-cloth high-pass brush-value region; large painted fold shading removed; shader-only interpretation, not literal garment geometry'
