"""Closed diagnostic for Director217's fitted gloves and relaxed riding fist.

Trusted repository handler; no arbitrary source paths, expressions or parameters.
"""
import json, sys, math
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import entrance214_contact as contact

OPS={'control21':'opening','control22':'opening','control23':'opening','opening24':'opening','route25':'route'}

def pose(rig,side):
    import bpy
    from mathutils import Quaternion
    for digit in range(4):
        for j,angle in enumerate((100,95,25)):
            bone=rig.pose.bones[f'MF_fit_finger_{digit}_{j}.{side}']
            bone.rotation_mode='QUATERNION'
            bone.rotation_quaternion=Quaternion((1,0,0),math.radians(angle))
    bpy.context.view_layer.update()
    contact.thumb(rig,side,((.025 if side=='L' else -.025),.66,-.30))

def gloves(scene):
    import bpy
    body=bpy.data.objects['MF_studio_adult_body']
    glove=body.copy();glove.data=body.data.copy();glove.name='MF217 fitted leather gloves'
    scene.collection.objects.link(glove)
    # Keep the full existing shape/armature stack so the fitted surface follows
    # the same deformations. Mask is a reversible derivative, not a body edit.
    names={g.index:g.name for g in glove.vertex_groups}
    group=glove.vertex_groups.new(name='MF217 hand and wrist coverage')
    ids=[]
    for v in glove.data.vertices:
        weight=sum(g.weight for g in v.groups if names.get(g.group,'').startswith(('hand.','MF_fit_finger')))
        if weight>.08:ids.append(v.index)
    if len(ids)<100:raise ValueError('Insufficient verified hand coverage')
    group.add(ids,1.,'REPLACE')
    mask=glove.modifiers.new('217 gloves only','MASK');mask.vertex_group=group.name;mask.threshold=.5
    shell=glove.modifiers.new('217 thin fitted leather','SOLIDIFY');shell.thickness=.018;shell.offset=1
    shell.use_even_offset=False;shell.thickness_clamp=1.
    mat=bpy.data.materials.new('MF217 worn umber leather');mat.use_nodes=True
    n=mat.node_tree.nodes;l=mat.node_tree.links;bs=n.get('Principled BSDF')
    bs.inputs['Roughness'].default_value=.69
    tex=n.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=80;tex.inputs['Detail'].default_value=3
    coord=n.new('ShaderNodeTexCoord');l.new(coord.outputs['Object'],tex.inputs['Vector'])
    ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].color=(.035,.018,.010,1)
    ramp.color_ramp.elements[1].color=(.13,.064,.030,1)
    l.new(tex.outputs['Fac'],ramp.inputs[0]);l.new(ramp.outputs['Color'],bs.inputs['Base Color'])
    bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.16;bump.inputs['Distance'].default_value=.012
    l.new(tex.outputs['Fac'],bump.inputs['Height']);l.new(bump.outputs['Normal'],bs.inputs['Normal'])
    glove.data.materials.clear();glove.data.materials.append(mat)
    for poly in glove.data.polygons:poly.material_index=0
    return glove

def validate(job):
    if not isinstance(job,dict) or set(job)!={'operation'} or job['operation'] not in OPS:
        raise ValueError('Closed217 operation required')
    return OPS[job['operation']]

def main():
    import bpy
    job=json.loads(Path(sys.argv[sys.argv.index('--')+1]).read_text());kind=validate(job)
    out=contact.base.BASE/('entrance217-'+job['operation'])
    if out.exists():raise ValueError('Preserve existing evidence')
    out.mkdir();(out/'handler.py').write_bytes(Path(__file__).read_bytes())
    scene=contact.load(kind);rig=bpy.data.objects['MF_body156_fit_rig']
    building=job['operation'] in ('opening24','route25')
    if building:
        control=contact.base.BASE/'entrance217-control23'
        admission=json.loads((control/'internal-review.json').read_text())
        if admission.get('status')!='PROCEED_TO_BUILD':raise ValueError('Hand control admission required')
        for name,digest in admission['images'].items():
            if contact.base.digest(control/name)!=digest:raise ValueError('Changed hand control evidence')
        contact.build(scene,out,kind,pose_fn=pose,changed_digits=tuple(range(5)),additions=gloves)
    for ob in scene.objects:
        for m in ob.modifiers:
            if m.type in ('SMOOTH','CORRECTIVE_SMOOTH','SUBSURF'):m.show_viewport=False
    scene.frame_set(360 if kind=='opening' else 427);bpy.context.view_layer.update()
    if not building:
        rig.animation_data.action=None
        for side in ('L','R'):pose(rig,side)
        contact.reins(scene)
        for side in ('L','R'):
            ob=bpy.data.objects['MF185_rein_'+side];ob.data.bevel_mode='OBJECT';ob.data.bevel_object=contact.leather_profile(scene)
    contact.hand_data(scene,out)
    if building:
        scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=8;scene.render.use_persistent_data=False
        scene.render.resolution_x=432;scene.render.resolution_y=768;scene.render.resolution_percentage=100
        for f in ((277,330,360) if kind=='opening' else (390,427,472,550,620)):
            scene.frame_set(f);scene.render.filepath=str(out/f'actual-{f}.png');bpy.ops.render.render(write_still=True)
        scene.frame_set(360 if kind=='opening' else 427)
    else:
        bare=out/'bare';bare.mkdir();contact.controls(scene,bare)
        glove=gloves(scene)
    dressed=out/'gloved';dressed.mkdir();contact.controls(scene,dressed)
    if not building:
        (out/'result.json').write_text(json.dumps({'source_sha256':contact.SOURCES[kind][1], 'glove_vertices':len(glove.data.vertices),'visual_gate':'NOT_RUN','scope':'Diagnostic only; no production native saved'},indent=2)+'\n')
    contact.base.check_protected()

if __name__=='__main__':main()
