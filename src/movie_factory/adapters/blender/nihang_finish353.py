"""Fixed owned supporting-actor finish; preserve geometry/animation masters."""
import json,math,importlib.util
from pathlib import Path

def crown_part(name):
    return name.startswith(('MF Nihang gathered crown','MF Nihang overlapped cloth','MF Nihang wrapped crown core'))

def run(bpy,out):
    rig=bpy.data.objects['MF coherent Nihang rig'];body=bpy.data.objects['MF coherent Nihang body']
    if not rig.get('waist353_attached') or rig.get('finish353'):raise ValueError('FINISH353_PARENT')
    spec=importlib.util.spec_from_file_location('finish347',Path(__file__).with_name('nihang_whole347.py'))
    helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper)
    owned=[];crowns=[];eyes=[]
    for ob in rig.children_recursive:
        if crown_part(ob.name) and ob.type=='MESH':
            ob.data=ob.data.copy()
            for v in ob.data.vertices:v.co.x*=.90;v.co.y*=.90
            ob.data.update();crowns.append(ob.name)
        if ob.type=='MESH' and (crown_part(ob.name) or ob.name.startswith(('MF coherent coat','MF coherent split chola','MF coherent pants'))):
            for i,mat in enumerate(ob.data.materials):
                m=mat.copy();m.name='353 owned indigo '+ob.name;ob.data.materials[i]=m
                helper.material(bpy,m,(.012,.025,.060),(.022,.043,.090),1100)
            owned.append(ob.name)
        if ob.name.startswith(('eyeball.','iris.','pupil.','brow.')):
            eyes.append(dict(name=ob.name,hidden=ob.hide_render,location=list(ob.matrix_world.translation),dimensions=list(ob.dimensions)))
        if ob.name.startswith('brow.') and ob.type=='CURVE':
            ob.data=ob.data.copy();ob.data.bevel_depth=.00020
            # Reorient individual strokes along the brow, not parallel lashes.
            for i,s in enumerate(ob.data.splines):
                points=s.points if s.type!='BEZIER' else s.bezier_points
                if not points:continue
                root=points[0].co.copy();factor=.65+.30*(.5+.5*math.sin(i*2.399))
                for j,p in enumerate(points):
                    u=j/max(1,len(points)-1)
                    p.co=root+(p.co-root)*factor
                    p.co.x+=math.copysign(.0020*u,root.x)+.0008*math.sin(i*1.73)*u
                    p.co.z+=.00070*math.cos(i*2.13)*u
                    p.radius=(.65+.35*(.5+.5*math.sin(i*3.1)))*(1-.75*u)
    if len(crowns)!=8 or 'MF Nihang wrapped crown core' not in crowns:
        raise ValueError('FINISH353_CROWN_ASSEMBLY')
    skin=body.data.materials[0].copy();body.data.materials[0]=skin;skin.name='353 retained pigment skin'
    bs=next(n for n in skin.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
    bs.inputs['Metallic'].default_value=0;bs.inputs['Roughness'].default_value=.50;bs.inputs['Specular IOR Level'].default_value=.28
    bs.inputs['Subsurface Weight'].default_value=.055
    # Preserve pigment source, add modest multi-scale variation instead of
    # repainting the face or changing its identity/anatomy.
    n=skin.node_tree.nodes;l=skin.node_tree.links
    previous=bs.inputs['Base Color'].links[0].from_socket
    tc=n.new('ShaderNodeTexCoord');noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=120
    l.new(tc.outputs['Object'],noise.inputs['Vector'])
    ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].color=(.58,.48,.43,1);ramp.color_ramp.elements[1].color=(1,.94,.87,1)
    l.new(noise.outputs['Fac'],ramp.inputs[0]);mix=n.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=.45
    l.new(previous,mix.inputs[1]);l.new(ramp.outputs[0],mix.inputs[2]);l.new(mix.outputs[0],bs.inputs['Base Color'])
    for n in skin.node_tree.nodes:
        if n.type=='BUMP':n.inputs['Strength'].default_value=.20;n.inputs['Distance'].default_value=.00035
    beard=bpy.data.objects['MF347 integrated beard and moustache'];beard.data=beard.data.copy();count=0
    for i,spline in enumerate(beard.data.splines):
        root=spline.points[0].co.copy();end=spline.points[-1].co.copy()
        if root.z-end.z<.045:continue  # preserve moustache construction
        factor=.86+.12*min(1,abs(root.x)/.065)+.035*math.sin(i*2.399)
        for j,p in enumerate(spline.points):
            u=j/(len(spline.points)-1);p.co.z=root.z+(p.co.z-root.z)*factor
            p.co.x+=math.copysign(.003*u*u,root.x)
        count+=1
    sash=bpy.data.objects['MF coherent shoulder sash']
    mod=sash.modifiers.new('353 support on actual dressed coat','SHRINKWRAP');mod.target=bpy.data.objects['MF coherent coat']
    mod.wrap_method='NEAREST_SURFACEPOINT';mod.wrap_mode='OUTSIDE_SURFACE';mod.offset=.006
    horse=bpy.data.objects['horse'];horse_materials=[]
    for i,mat in enumerate(horse.data.materials):
        m=mat.copy();m.name='353 dark short-coat '+str(i);horse.data.materials[i]=m
        p=next((n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
        if p:
            for link in list(p.inputs['Roughness'].links):m.node_tree.links.remove(link)
            p.inputs['Roughness'].default_value=.68;p.inputs['Metallic'].default_value=0;p.inputs['Specular IOR Level'].default_value=.22;p.inputs['Sheen Weight'].default_value=.18
            n=m.node_tree.nodes;l=m.node_tree.links;tc=n.new('ShaderNodeTexCoord')
            mapping=n.new('ShaderNodeVectorMath');mapping.operation='MULTIPLY';mapping.inputs[1].default_value=(150,24,1)
            l.new(tc.outputs['UV'],mapping.inputs[0]);noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=5
            l.new(mapping.outputs[0],noise.inputs['Vector']);bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.30;bump.inputs['Distance'].default_value=.00065
            if p.inputs['Normal'].is_linked:l.new(p.inputs['Normal'].links[0].from_socket,bump.inputs['Normal'])
            l.new(noise.outputs['Fac'],bump.inputs['Height']);l.new(bump.outputs[0],p.inputs['Normal'])
            rough=n.new('ShaderNodeMapRange');rough.inputs['To Min'].default_value=.62;rough.inputs['To Max'].default_value=.84
            l.new(noise.outputs['Fac'],rough.inputs[0]);l.new(rough.outputs[0],p.inputs['Roughness'])
        horse_materials.append(m.name)
    pad=bpy.data.objects['fitted saddle blanket292'];mat=pad.data.materials[0].copy();pad.data.materials[0]=mat
    # Retain the existing woven border rather than erasing its color ownership.
    helper.saddle_finish(bpy)
    skirts=[]
    for ob in rig.children_recursive:
        if not ob.name.startswith('MF coherent split chola') or ob.type!='MESH':continue
        ob.data=ob.data.copy();zs=[v.co.z for v in ob.data.vertices];lo=min(zs);hi=max(zs)
        for v in ob.data.vertices:
            u=max(0,min(1,(hi-v.co.z)/(hi-lo)));a=math.atan2(v.co.x,-v.co.y-.02)
            fold=.009*u*math.sin(11*a+1.2*u)+.004*u*math.sin(19*a-.7*u)
            v.co.x+=fold*math.sin(a);v.co.y-=fold*math.cos(a)
            v.co.z+=.006*u*u*math.sin(7*a+.8)
            # Hip attachment remains fixed; reduce the thigh's cardboard-like
            # carry of the hanging hem. This is authored drape, not simulation.
            rows=[(ob.vertex_groups[g.group].name,g.weight) for g in v.groups]
            moved=0
            for name,w in rows:
                if name.startswith('upperleg'):
                    retained=w*.65;ob.vertex_groups[name].add([v.index],retained,'REPLACE');moved+=w-retained
            if moved:
                group=ob.vertex_groups.get('spine05');old=next((w for name,w in rows if name=='spine05'),0)
                group.add([v.index],old+moved,'REPLACE')
        ob.data.update();skirts.append(ob.name)
    rig['finish353']=1;bpy.context.view_layer.update()
    report=dict(changed=True,source_preserved=True,vertices=len(body.data.vertices),owned_material_objects=owned,crowns=crowns,beard_curves=count,eyes=eyes,horse_materials=horse_materials,skirts=skirts,horse_vertices=len(horse.data.vertices),horse_modifiers=[dict(name=m.name,type=m.type) for m in horse.modifiers],scope='Appearance candidate only; authored skirt drape is not simulation. Face/cloth/tack and motion require actual review.')
    (out/'finish353.json').write_text(json.dumps(report,indent=2)+'\n');return report
