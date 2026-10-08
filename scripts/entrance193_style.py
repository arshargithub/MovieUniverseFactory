"""Reversible illustrated-C lighting/material treatment, not an image filter."""
import json
import sys
import time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import wardrobe_motion178 as base


def painterly(scene, stronger=False, soft_skin=False):
    import bpy
    import mathutils
    # Preserve the authored distant painting. Modify physical foreground
    # surfaces, not the final image, volumes, corneas or facial transparency.
    protected=json.loads((base.SOURCE.parent/'result.json').read_text())['protected_signatures']
    targets=set();copies={};eligible=[]
    protected_data={bpy.data.objects[n].data for n in protected if bpy.data.objects[n].data is not None}
    for ob in scene.objects:
        if ob.hide_render or ob.name in protected or ob.type not in ('MESH','CURVE','CURVES'):continue
        if ob.data in protected_data:continue
        eligible.append(ob)
        for slot in ob.material_slots:
            mat=slot.material
            if mat:
                if slot.link!='DATA':raise ValueError('Unexpected source object material override')
                if mat not in copies:
                    copies[mat]=mat.copy();copies[mat].name=mat.name+' 193 illustrated derivative'
                targets.add(copies[mat])
    # Assign once per shared datablock. Keep tree/rock instances truly shared;
    # none of these datablocks belongs to a protected source object.
    assigned=set()
    for ob in eligible:
        if ob.data in assigned:continue
        assigned.add(ob.data)
        for slot in ob.material_slots:
            if slot.material in copies:slot.material=copies[slot.material]
    records=[]
    direction=mathutils.Vector((-.48,-.52,.71)).normalized()
    for mat in sorted(targets,key=lambda m:m.name):
        if not mat.use_nodes:continue
        nodes=mat.node_tree.nodes;links=mat.node_tree.links
        out=next((n for n in nodes if n.type=='OUTPUT_MATERIAL' and n.is_active_output),None)
        if out is None or not out.inputs['Surface'].is_linked:continue
        shader=out.inputs['Surface'].links[0].from_node
        # Do not replace mixed opacity, image-emission matte, eyes or hair BSDF.
        if shader.type!='BSDF_PRINCIPLED' or any(w in mat.name.lower() for w in ('cornea','eye','gums','teeth','mouth')):continue
        skin='skin' in mat.name.lower() or 'neck' in mat.name.lower()
        original=out.inputs['Surface'].links[0].from_socket
        color=shader.inputs['Base Color']
        geometry=nodes.new('ShaderNodeNewGeometry');geometry.label='193 form planes, world-consistent'
        dot=nodes.new('ShaderNodeVectorMath');dot.operation='DOT_PRODUCT';dot.inputs[1].default_value=direction
        links.new(geometry.outputs['Normal'],dot.inputs[0])
        remap=nodes.new('ShaderNodeMapRange');remap.inputs['From Min'].default_value=-1;remap.inputs['From Max'].default_value=1
        links.new(dot.outputs['Value'],remap.inputs['Value'])
        ramp=nodes.new('ShaderNodeValToRGB');ramp.label='193 cool shadow / warm lit planes'
        ramp.color_ramp.interpolation='EASE'
        stops=[(.0,(.29,.36,.49,1)),(.42,(.39,.43,.52,1)),(.50,(.70,.68,.64,1)),(.72,(1.12,1.02,.84,1)),(1.,(1.22,1.10,.88,1))]
        if stronger:
            stops=[(0.,(.21,.28,.43,1)),(.44,(.21,.28,.43,1)),(.49,(.70,.66,.61,1)),(.66,(.70,.66,.61,1)),(.71,(1.65,1.36,.94,1)),(1.,(1.65,1.36,.94,1))]
        if soft_skin and skin:
            stops=[(0.,(.35,.40,.48,1)),(.30,(.43,.45,.52,1)),(.58,(.85,.76,.66,1)),(.85,(1.3,1.08,.85,1)),(1.,(1.3,1.08,.85,1))]
        for i,(p,c) in enumerate(stops):
            e=ramp.color_ramp.elements[i] if i<2 else ramp.color_ramp.elements.new(p)
            e.position=p;e.color=c
        plane=remap.outputs['Result']
        if stronger:
            tex=nodes.new('ShaderNodeTexCoord');stretch=nodes.new('ShaderNodeVectorMath');stretch.operation='MULTIPLY'
            stretch.inputs[1].default_value=(28,90,1);links.new(tex.outputs['UV'],stretch.inputs[0])
            noise=nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=1.6;noise.inputs['Detail'].default_value=1.
            links.new(stretch.outputs['Vector'],noise.inputs['Vector'])
            center=nodes.new('ShaderNodeMath');center.operation='MULTIPLY_ADD';center.inputs[1].default_value=.14;center.inputs[2].default_value=-.07
            if soft_skin and skin:center.inputs[1].default_value=.035;center.inputs[2].default_value=-.0175
            links.new(noise.outputs['Fac'],center.inputs[0])
            add=nodes.new('ShaderNodeMath');add.operation='ADD';links.new(plane,add.inputs[0]);links.new(center.outputs[0],add.inputs[1]);plane=add.outputs[0]
        links.new(plane,ramp.inputs[0])
        multiply=nodes.new('ShaderNodeMixRGB');multiply.blend_type='MULTIPLY';multiply.inputs[0].default_value=.88 if skin else 1.
        if soft_skin and skin:multiply.inputs[0].default_value=.65
        if color.is_linked:links.new(color.links[0].from_socket,multiply.inputs[1])
        else:multiply.inputs[1].default_value=color.default_value
        links.new(ramp.outputs['Color'],multiply.inputs[2])
        emission=nodes.new('ShaderNodeEmission');emission.inputs['Strength'].default_value=1.15 if stronger else .85
        links.new(multiply.outputs[0],emission.inputs['Color'])
        mix=nodes.new('ShaderNodeMixShader');mix.inputs[0].default_value=(.72 if skin else .85) if stronger else (.54 if skin else .72)
        if soft_skin and skin:mix.inputs[0].default_value=.50
        links.new(original,mix.inputs[1]);links.new(emission.outputs[0],mix.inputs[2]);links.new(mix.outputs[0],out.inputs['Surface'])
        # Existing UV/rest-coordinate painted grain and fabric marks remain.
        # A broad surface response supersedes plastic highlights, not detail.
        if not shader.inputs['Roughness'].is_linked:shader.inputs['Roughness'].default_value=max(.65,shader.inputs['Roughness'].default_value)
        if 'Specular IOR Level' in shader.inputs:shader.inputs['Specular IOR Level'].default_value=.16 if skin else .12
        records.append({'material':mat.name,'skin':skin,'illustrated_mix':float(mix.inputs[0].default_value)})
    return records


def main():
    import bpy
    job=json.loads(Path(sys.argv[sys.argv.index('--')+1]).read_text())
    if job not in ({'operation':'painter05'},{'operation':'painter08'},{'operation':'painter09'},{'operation':'painter12'},{'operation':'painter13'}):raise ValueError('Fixed style control required')
    source=base.BASE/'entrance193-bind03/scene.blend';out=base.BASE/('entrance193-'+job['operation'])
    r=json.loads((source.parent/'result.json').read_text())
    if out.exists() or base.digest(source)!=r['native_sha256']:raise ValueError('Changed source or prior evidence')
    for row in r['caches']:
        p=(source.parent/row['path']).resolve()
        if not p.is_relative_to(base.BASE.resolve()) or base.digest(p)!=row['sha256']:raise ValueError('Changed cache')
    out.mkdir();(out/'handler.py').write_bytes(Path(__file__).read_bytes())
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False);base.check_protected()
    scene=bpy.context.scene;changes=painterly(scene,stronger=job['operation']!='painter05',soft_skin=job['operation']=='painter13')
    base.check_protected()
    # Resolve before save; Blender rebases relative caches to the new scene.
    for ob in scene.objects:
        for m in ob.modifiers:
            if m.type=='MESH_CACHE':m.filepath=bpy.path.abspath(m.filepath)
    scene.frame_set(217);bpy.context.preferences.filepaths.save_version=0
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'scene.blend'),compress=True)
    bpy.ops.file.make_paths_relative();bpy.ops.wm.save_as_mainfile(filepath=str(out/'scene.blend'),compress=True)
    native_sha=base.digest(out/'scene.blend')
    for ob in scene.objects:
        for m in ob.modifiers:
            if m.type in ('SMOOTH','CORRECTIVE_SMOOTH','SUBSURF') and m.show_viewport:m.show_viewport=False
    scene.cycles.device='CPU';scene.cycles.samples=8;scene.render.use_persistent_data=True
    scene.render.resolution_percentage=100;scene.render.resolution_x=432;scene.render.resolution_y=768
    rows=[]
    for f in (265,271,360):
        start=time.monotonic();scene.frame_set(f);scene.render.filepath=str(out/f'frame-{f:04d}.png')
        bpy.ops.render.render(write_still=True);rows.append({'frame':f,'seconds':time.monotonic()-start})
    base.check_protected()
    (out/'result.json').write_text(json.dumps({'source_sha256':r['native_sha256'],'native_sha256':native_sha,
        'changes':changes,'frames':rows,'visual_gate':'NOT_RUN','geometry_animation_camera_unchanged':True,
        'treatment':'Object-space shading hierarchy with cool shadow/warm light planes, retained authored texture; no image filter'},indent=2)+'\n')


if __name__=='__main__':main()
