"""320 cloth construction and materials at supporting-character shot scale."""
import math
import bpy
import numpy as np
from mathutils import Vector
from sikh257_native import mesh
from sikh319_cast import strands
def textile(mat,blue=True):
    mat=mat.copy();mat.name='320 worn woven '+mat.name
    n=mat.node_tree.nodes;l=mat.node_tree.links;b=n.get('Principled BSDF')
    n.clear();out=n.new('ShaderNodeOutputMaterial');b=n.new('ShaderNodeBsdfPrincipled');l.new(b.outputs[0],out.inputs[0])
    tc=n.new('ShaderNodeTexCoord');tex=n.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=5.5;tex.inputs['Detail'].default_value=3;tex.inputs['Roughness'].default_value=.72;l.new(tc.outputs['Object'],tex.inputs[0])
    ramp=n.new('ShaderNodeValToRGB')
    for el,pos,col in zip(ramp.color_ramp.elements,(.17,.83),((.012,.026,.060,1),(.065,.115,.19,1)) if blue else ((.08,.043,.012,1),(.28,.18,.07,1))):el.position=pos;el.color=col
    l.new(tex.outputs['Fac'],ramp.inputs[0]);l.new(ramp.outputs[0],b.inputs['Base Color'])
    b.inputs['Roughness'].default_value=.88;b.inputs['Specular IOR Level'].default_value=.22;b.inputs['Sheen Weight'].default_value=.24
    mapping=n.new('ShaderNodeVectorMath');mapping.operation='MULTIPLY';mapping.inputs[1].default_value=(1,1,2.8);l.new(tc.outputs['Object'],mapping.inputs[0])
    micro=n.new('ShaderNodeTexNoise');micro.inputs['Scale'].default_value=190;micro.inputs['Detail'].default_value=2;l.new(mapping.outputs[0],micro.inputs[0])
    bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.26;bump.inputs['Distance'].default_value=.00065;l.new(micro.outputs['Fac'],bump.inputs['Height']);l.new(bump.outputs[0],b.inputs['Normal'])
    rough=n.new('ShaderNodeMapRange');rough.inputs['To Min'].default_value=.76;rough.inputs['To Max'].default_value=.96;l.new(tex.outputs['Fac'],rough.inputs[0]);l.new(rough.outputs[0],b.inputs['Roughness'])
    return mat
def costume(out):
    s=bpy.context.scene;s.frame_set(283)
    roots=[bpy.data.objects['mounted leader']]+sorted([o for o in s.objects if o.name.startswith('FOOT WARRIOR ')],key=lambda o:int(o.name.split()[-1]))
    material_map={};report=[]
    for i,root in enumerate(roots):
        leader=i==0;upper=next(o for o in root.children if o.name.startswith('320 articulated upper body'))
        objects=list(root.children_recursive)
        for ob in objects:
            if ob.hide_render or not hasattr(ob.data,'materials'):continue
            for k,mat in enumerate(ob.data.materials):
                if mat and mat.name.startswith(('319 indigo cloth','319 handled ochre sash')):
                    if mat.name not in material_map:material_map[mat.name]=textile(mat,mat.name.startswith('319 indigo'))
                    ob.data.materials[k]=material_map[mat.name]
        shirt=next(o for o in upper.children if o.name.startswith('319 anatomically'))
        # Frozen cloth coordinates; distort all cached poses equally only in
        # torso region. Cuffs and shoulder ownership remain untouched.
        blocks=[k.data for k in shirt.data.shape_keys.key_blocks] if shirt.data.shape_keys else [shirt.data.vertices]
        coords=np.array([v.co[:] for v in shirt.data.vertices]);z0=.06 if leader else .88;zt=.46 if leader else 1.28
        weight=np.clip((.19-np.abs(coords[:,0]))/.07,0,1)*np.clip((coords[:,2]-z0)/.07,0,1)*np.clip((zt-coords[:,2])/.06,0,1)
        # Diagonal tension folds converge on the waist, not sculpted pectorals.
        phase=coords[:,2]*46+np.abs(coords[:,0])*25+i*.4
        ridge=.008*np.sin(phase)+.003*np.sin(phase*1.7+.8)
        dy=np.sign(coords[:,1])*(.008+ridge)*weight
        for block in blocks:
            a=np.array([v.co[:] for v in block],dtype=np.float32);a[:,1]+=dy;block.foreach_set('co',a.ravel())
        # Cloth chest overlay must follow the same fold field.
        for ob in upper.children:
            if ob.type!='MESH' or not ob.name.startswith('319 overlapping chola'):continue
            for p in ob.data.vertices:
                w=max(0,min(1,(.19-abs(p.co.x))/.07))*max(0,min(1,(p.co.z-z0)/.07))*max(0,min(1,(zt-p.co.z)/.06))
                phase=p.co.z*46+abs(p.co.x)*25+i*.4;p.co.y+=math.copysign((.008+.008*math.sin(phase)+.003*math.sin(phase*1.7+.8))*w,p.co.y)
        # More cloth at thighs/knees, not tight blue tubular trousers.
        for ob in objects:
            if ob.hide_render or ob.type!='MESH' or 'trousers' not in ob.name:continue
            blocks=[k.data for k in ob.data.shape_keys.key_blocks] if ob.data.shape_keys else [ob.data.vertices]
            for block in blocks:
                for j in range(13):
                    ring=list(block)[j*24:(j+1)*24]
                    if len(ring)!=24:continue
                    center=sum((p.co for p in ring),Vector())/24
                    for k,p in enumerate(ring):
                        u=j/12;amount=(.16 if leader else .12)*math.sin(math.pi*u)
                        p.co=center+(p.co-center)*(1+amount+.045*math.sin(k*math.tau/24*6+j*.75)*math.sin(math.pi*u))
        skirt=next(o for o in root.children if o.name.startswith('319 flared chola skirt'))
        zmax=max(p.co.z for p in skirt.data.vertices);zmin=min(p.co.z for p in skirt.data.vertices)
        for p in skirt.data.vertices:
            u=max(0,min(1,(zmax-p.co.z)/max(.01,zmax-zmin)));a=math.atan2(p.co.y,p.co.x)
            scale=1+.075*u+.055*u*math.sin(a*7+.5*math.sin(a*3)+u*1.3)
            p.co.x*=scale;p.co.y*=scale;p.co.z+=.009*u*u*math.sin(a*5+i)
        skirt.shape_key_add(name='Basis');swing=skirt.shape_key_add(name='Pelvis driven cloth lag')
        for p in swing.data:
            u=max(0,min(1,(zmax-p.co.z)/max(.01,zmax-zmin)));p.co.y+=.030*u*u;p.co.x+=.012*u*u
        for f in range(252,442):
            t=(f-1)/24;envelope=max(0,min(1,(f-345)/30))*max(0,min(1,(440-f)/25)) if not leader else math.exp(-((f-347)/25)**2)
            swing.value=envelope*(.55*math.sin(t*6+i)+.2*math.sin(t*9+i*.4));swing.keyframe_insert('value',frame=f)
        # Raised hems from the old cylindrical garment no longer match this
        # skirt; use a narrow actual-edge binding rather than a floating pipe.
        for ob in root.children:
            if ob.name.startswith(('297 lower hem binding','297 chola front seam')):ob.hide_render=True
        hem=[p.co.copy() for p in skirt.data.vertices if p.co.z<zmin+.035]
        if len(hem)>8:
            hem.sort(key=lambda p:math.atan2(p.y,p.x));hem.append(hem[0]);strands('320 turned skirt hem',[hem],.0018,skirt.data.materials[0],root,False)
        # Worn sash folds and seams replace perfectly flat saturated bands.
        for ob in objects:
            if ob.hide_render or ob.type!='MESH' or not ob.name.startswith(('297 cloth waist sash','297 woven diagonal sash')):continue
            normals=[v.normal.copy() for v in ob.data.vertices]
            for p,normal in zip(ob.data.vertices,normals):p.co+=normal*(.0035*math.sin(p.co.z*170+p.co.x*13)+.0015*math.sin(p.co.z*300+p.co.y*19))
        report.append({'actor':root.name,'surface':'indigo/ochre woven cloth, restrained roughness, waist tension folds and gathered trousers','limits':'shot-authored deformation; not general cloth simulation'})
    return report
