"""Bounded equipment/material and object-space secondary follow for supporting cast."""
import math
import bpy
import numpy as np
from mathutils import Vector, Euler
from sikh257_native import mesh,material
from sikh292_assets import surface

def finish():
    s=bpy.context.scene
    for mat in bpy.data.materials:
        if mat.name.startswith('319 indigo cloth'):
            bs=mat.node_tree.nodes['Principled BSDF']
            bs.inputs['Specular IOR Level'].default_value=.22
            bs.inputs['Sheen Weight'].default_value=.06
            bs.inputs['Roughness'].default_value=.94
    wood=surface('319 handled spear ash',[(.035,.019,.008),(.13,.080,.029)],12,rough=.82,bump=.0004)
    steel=material('319 forged spear steel',(.12,.15,.17))
    bs=steel.node_tree.nodes['Principled BSDF'];bs.inputs['Metallic'].default_value=.75;bs.inputs['Roughness'].default_value=.48
    for name,mat in [('leader spear shaft',wood),('leader spear point',steel)]:
        ob=bpy.data.objects[name];ob.data=ob.data.copy();ob.data.materials.clear();ob.data.materials.append(mat)
    sash=surface('319 handled ochre sash',[(.12,.069,.016),(.26,.16,.047)],12,rough=.96,bump=.0006)
    leather=surface('319 worn dark leather',[(.020,.012,.008),(.067,.041,.023)],19,rough=.83,bump=.0005)
    sole=material('319 dark sole edge',(.018,.013,.009))
    for root in [bpy.data.objects['mounted leader']]+[o for o in bpy.data.objects if o.name.startswith('FOOT WARRIOR ')]:
        for ob in list(root.children):
            mat=None
            if ob.name.startswith('300 leaf spearhead'):mat=steel
            if ob.name=='spear' or ob.name.startswith('spear.'):mat=wood
            if ob.name.startswith(('297 cloth waist sash','297 woven diagonal sash','300 loose woven sash end')):mat=sash
            if ob.name.startswith(('297 mounted boot','PROXY boot')):
                mat=leather
                # Sole is attached to the existing world-supported boot owner;
                # its lowest point remains the original contact minimum.
                pts=np.array([v.co[:] for v in ob.data.vertices])
                low=pts[:,2].min();rx=max(abs(pts[:,0]))*.99;ry=max(abs(pts[:,1]))*.99
                ob.data=ob.data.copy()
                for p in ob.data.vertices:
                    z=p.co.z
                    if z<0:
                        radial=math.sqrt((p.co.x/rx)**2+(p.co.y/ry)**2)
                        w=min(1,max(0,z/low));w=w*w*(3-2*w)
                        desired=radial+(1-radial)*w
                        if radial>.00001:p.co.x*=desired/radial;p.co.y*=desired/radial
                        p.co.z=low+.009+(z-low)*(1-.009/abs(low))
                vs=[(rx*math.cos(a),ry*math.sin(a),low+z) for z in (0,.009) for a in np.linspace(0,math.tau,48,endpoint=False)]
                fs=[(i,(i+1)%48,(i+1)%48+48,i+48) for i in range(48)]
                fs.extend([tuple(reversed(range(48))),tuple(range(48,96))])
                shoe=mesh('319 boot sole and welt',vs,fs,sole);shoe.parent=ob
            if mat:
                ob.data=ob.data.copy();ob.data.materials.clear();ob.data.materials.append(mat)
    # Replace the rigid triangle with a supported cloth pennant. The spear owner
    # and plant remain unchanged; root column cannot move.
    old=bpy.data.objects['leader standard cloth'];old.hide_render=True;old.hide_viewport=True
    cloth=surface('319 worn saffron pennant',[(.18,.063,.008),(.40,.19,.032)],9,rough=.97,bump=.0004)
    vs=[];fs=[];rows=25;cols=13
    for j in range(rows):
        t=j/(rows-1)
        for k in range(cols):
            u=k/(cols-1)
            vs.append((.009*t*math.sin(u*math.pi),.55*t,3.48-.36*t-.54*(1-t)*u))
        if j:
            for k in range(cols-1):
                a=j*cols+k;fs.append((a-cols,a-cols+1,a+1,a))
    flag=mesh('319 supported cloth pennant',vs,fs,cloth);flag.parent=old.parent
    flag.shape_key_add(name='Basis')
    key=flag.shape_key_add(name='Restrained breeze')
    for p in key.data:
        u=p.co.y/.55;p.co.x+=.05*u*u*math.sin(u*4+p.co.z*11)
    for f in range(1,697,3):
        t=(f-1)/24
        key.value=.45+.24*math.sin(t*1.7)+.17*math.sin(t*2.9+.8)
        key.keyframe_insert('value',frame=f)
    # Small rotational lag has bounded root displacement at this framing.
    # This avoids curve-data shape keys, whose saved candidate06 did not reopen.
    frames=[o for o in bpy.data.objects if o.name.startswith('secondary facial and crown frame292')]
    times=list(range(1,697,3))+[696];tracks={o.name:[] for o in frames}
    for f in times:
        s.frame_set(f)
        for ob in frames:tracks[ob.name].append(ob.matrix_world.to_quaternion().copy())
    report=[]
    pivot=Vector((0,-.12,-.035))
    for frame in frames:
        state=Vector((0,0,0));peak=0
        hairs=[o for o in frame.children if o.name.startswith('319 tapered beard fibers')]
        for f,q in zip(times,tracks[frame.name]):
            gravity=q.inverted()@Vector((0,0,-1))
            target=Vector((max(-.055,min(.055,-gravity.y*.15)),max(-.045,min(.045,gravity.x*.15)),0))
            state=state.lerp(target,.28);rot=Euler(tuple(state),'XYZ');translation=pivot-rot.to_matrix()@pivot
            peak=max(peak,state.length)
            for ob in hairs:
                ob.rotation_euler=rot;ob.location=translation
                ob.keyframe_insert('rotation_euler',frame=f);ob.keyframe_insert('location',frame=f)
        report.append({'head_owner':frame.name,'maximum_angle_radians':peak,
                       'method':'bounded root-near rotational lag; not strand dynamics',
                       'curve_data_shape_keys':False})
    s.frame_set(283);bpy.context.view_layer.update()
    return report
