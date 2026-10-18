"""Screen-scale surface structure after coherent terrain and crop layout."""
import math
import bpy
import numpy as np
from mathutils import Vector
from sikh292_assets import surface

def earth(mat,ruts=False):
    n=mat.node_tree.nodes;l=mat.node_tree.links;b=n['Principled BSDF']
    original=b.inputs['Base Color'].links[0].from_socket
    tc=n.new('ShaderNodeTexCoord');fine=n.new('ShaderNodeTexNoise');fine.inputs['Scale'].default_value=68;fine.inputs['Detail'].default_value=3;l.new(tc.outputs['Object'],fine.inputs[0])
    ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].position=.25;ramp.color_ramp.elements[0].color=(.62,.62,.62,1);ramp.color_ramp.elements[1].position=.72;ramp.color_ramp.elements[1].color=(1.12,1.12,1.12,1);l.new(fine.outputs['Fac'],ramp.inputs[0])
    mult=n.new('ShaderNodeMixRGB');mult.blend_type='MULTIPLY';mult.inputs[0].default_value=.65;l.new(original,mult.inputs[1]);l.new(ramp.outputs[0],mult.inputs[2]);l.new(mult.outputs[0],b.inputs['Base Color'])
    oldnormal=b.inputs['Normal'].links[0].from_socket
    relief=n.new('ShaderNodeTexNoise');relief.inputs['Scale'].default_value=27;relief.inputs['Detail'].default_value=3;l.new(tc.outputs['Object'],relief.inputs[0]);bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.34;bump.inputs['Distance'].default_value=.006;l.new(relief.outputs['Fac'],bump.inputs['Height']);l.new(oldnormal,bump.inputs['Normal']);l.new(bump.outputs[0],b.inputs['Normal'])
    if ruts:
        # The same +/-0.7m lanes as the actual shallow geometry. Longitudinal
        # wear changes soil colour, never a hovering separate road surface.
        sep=n.new('ShaderNodeSeparateXYZ');l.new(tc.outputs['Object'],sep.inputs[0]);a=n.new('ShaderNodeMath');a.operation='ABSOLUTE';l.new(sep.outputs['X'],a.inputs[0]);sub=n.new('ShaderNodeMath');sub.operation='SUBTRACT';sub.inputs[1].default_value=.70;l.new(a.outputs[0],sub.inputs[0]);ab=n.new('ShaderNodeMath');ab.operation='ABSOLUTE';l.new(sub.outputs[0],ab.inputs[0]);mask=n.new('ShaderNodeMapRange');mask.inputs['From Min'].default_value=.04;mask.inputs['From Max'].default_value=.35;mask.inputs['To Min'].default_value=.30;mask.inputs['To Max'].default_value=0;l.new(ab.outputs[0],mask.inputs[0]);mix=n.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[2].default_value=(.65,.62,.54,1);l.new(mask.outputs[0],mix.inputs[0]);l.new(mult.outputs[0],mix.inputs[1]);l.new(mix.outputs[0],b.inputs['Base Color'])

def cereal():
    rng=np.random.default_rng(30433)
    for k in range(4):
        ob=bpy.data.objects['300 reusable wheat tiller clump '+str(k)];leaf=ob.data.materials[0]
        ear=surface('304 ripening ear '+str(k),[(.16,.14,.052),(.29,.275,.12)],18,rough=.9,bump=.0003)
        vs=[];fs=[];mi=[]
        def face(points,material=0):
            q=len(vs);vs.extend(points);fs.append(tuple(range(q,q+len(points))));mi.append(material)
        for j in range(7):
            ang=float(rng.uniform(0,math.tau));p=Vector((float(rng.uniform(-.12,.12)),float(rng.uniform(-.12,.12)),0));h=float(rng.uniform(.62,.91));lean=float(rng.uniform(-.04,.06));d=Vector((math.cos(ang),math.sin(ang),0));w=Vector((-d.y,d.x,0));top=p+Vector((lean,0,h))
            for axis in (d,w):face([p-axis*.0017,p+axis*.0017,top+axis*.0013,top-axis*.0013])
            for m in range(3):
                base=p+Vector((lean*(.2+m*.2),0,h*(.2+m*.2)));direction=d*((-1)**m);length=float(rng.uniform(.20,.31));pairs=[]
                for step in range(7):
                    u=step/6;center=base+direction*length*u+Vector((0,0,.11*math.sin(math.pi*u)-.025*u));width=.009*math.sin(math.pi*(u*.98+.01));pairs.append((center-w*width,center+w*width))
                for a,b in zip(pairs,pairs[1:]):face([a[0],a[1],b[1],b[0]])
            for m in range(6):
                center=top+Vector((0,0,m*.015));r=.011*math.sin((m+1)/7*math.pi)
                for side in (-1,1):
                    v=center+w*r*side;face([v-d*.006,v+w*.008*side+Vector((0,0,.009)),v+d*.006,v+Vector((0,0,.017))],1)
            for side in (-1,1):face([top+w*.008*side-d*.0005,top+w*.008*side+d*.0005,top+w*.016*side+Vector((0,0,.14))],1)
        data=bpy.data.meshes.new('304 curved cereal leaves and distinct seed heads');data.from_pydata(vs,[],fs);data.materials.append(leaf);data.materials.append(ear)
        for poly,idx in zip(data.polygons,mi):poly.material_index=idx
        data.update();ob.data=data

def finish():
    earth(bpy.data.materials['304 compacted silty farm soil'],True)
    earth(bpy.data.materials['304 earthy bank'])
    # Sediment borders are feathered into the same soil palette, not a dark
    # ruler-straight ribbon. Exact endpoints still conform to existing ground.
    mat=bpy.data.materials['304 moist ditch sediment'];n=mat.node_tree.nodes;l=mat.node_tree.links;b=n['Principled BSDF'];src=b.inputs['Base Color'].links[0].from_socket
    mix=n.new('ShaderNodeMixRGB');mix.inputs[0].default_value=.55;mix.inputs[2].default_value=(.155,.137,.087,1);l.new(src,mix.inputs[1]);l.new(mix.outputs[0],b.inputs['Base Color']);b.inputs['Roughness'].default_value=.94
    cereal()
