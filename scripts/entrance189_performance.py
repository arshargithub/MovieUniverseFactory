"""Scoped, authored riding attention and head follow-through; not a general rig."""
import math
import numpy as np


def smooth(x):
    x=np.clip(x,0,1)
    return x*x*(3-2*x)


def facial_values(frame):
    t=(frame-217)/24
    blink=max(0.,1-abs(t-3.95)/.115)**1.4
    effort=.5+.5*math.sin(t*2.1+.6)
    return {'eyeBlinkLeft':blink,'eyeBlinkRight':blink,
        'eyeSquintLeft':.10+.035*effort,'eyeSquintRight':.10+.035*effort,
        'browDownLeft':.055,'browDownRight':.045,
        'mouthPressLeft':.07,'mouthPressRight':.07,
        'jawOpen':.025+.018*effort,'cheekSquintLeft':.025,'cheekSquintRight':.025}


def neck_weights(body):
    count=0
    for v in body.data.vertices:
        x,y,z=v.co
        if not (-2.05<z<-.8 and abs(x)<.88):continue
        blend=float(smooth((.88-abs(x))/.25)*smooth((z+2.05)/.25)*smooth((-.8-z)/.12))
        neck=float(smooth((z+1.95)/.65));head=float(smooth((z+1.24)/.40))
        weights={'chest':1-neck,'MF185_neck':neck*(1-head),'MF185_head':neck*head}
        for name,new in weights.items():
            g=body.vertex_groups[name]
            try:old=g.weight(v.index)
            except RuntimeError:old=0.
            g.add([v.index],old*(1-blend)+new*blend,'REPLACE')
        count+=1
    return count


def animate(scene,out):
    import bpy
    from mathutils import Quaternion
    from wardrobe_motion178_controls import render_geometry_paused
    rig=bpy.data.objects['MF_body156_fit_rig'];body=bpy.data.objects['MF_studio_adult_body']
    body.data=body.data.copy()
    modified=neck_weights(body)
    old=[];basis=[];new=[]
    head=rig.pose.bones['MF185_head']
    with render_geometry_paused():
        for f in range(217,361):
            scene.frame_set(f);bpy.context.view_layer.update()
            old.append(np.array(rig.matrix_world@head.matrix));basis.append(head.rotation_quaternion.copy())
        z=np.array(old)[:,2,3];velocity=np.gradient(z)
        # Filter observed gait response, avoiding an unrelated oscillation clock.
        pitch=np.convolve(velocity,np.array([1,2,3,2,1])/9,mode='same')
        pitch=np.deg2rad(1.4)*np.tanh(pitch/.055)
        for i,f in enumerate(range(217,361)):
            scene.frame_set(f);t=i/24
            attention=math.radians(1.7)*float(smooth((t-3.5)/1.4))
            roll=math.radians(.35)*math.sin(t*2.0)
            head.rotation_quaternion=Quaternion((0,0,1),attention)@Quaternion((0,1,0),roll)@Quaternion((1,0,0),float(pitch[i]))@basis[i]
            head.keyframe_insert(data_path='rotation_quaternion',frame=f)
            for name,value in facial_values(f).items():
                k=body.data.shape_keys.key_blocks[name];k.value=value;k.keyframe_insert(data_path='value',frame=f)
            for side in ('Left','Right'):
                eye=bpy.data.objects['MF_aimable_eye_'+side]
                eye.rotation_euler.z=math.radians(2.4)*float(smooth((t-3.2)/.6))
                eye.keyframe_insert(data_path='rotation_euler',index=2,frame=f)
            bpy.context.view_layer.update();new.append(np.array(rig.matrix_world@head.matrix))
    # Native explicit curves only. No handlers/scripts are needed at playback.
    from entrance189_groom import read_mdd, write_mdd, attach_cache
    shawl=bpy.data.objects['MF185_moving_shawl']
    source=next(m for m in shawl.modifiers if m.type=='MESH_CACHE')
    a=read_mdd(bpy.path.abspath(source.filepath))
    start=int(source.frame_start)
    inverse=np.linalg.inv(np.array(shawl.matrix_world))
    transform=np.array(shawl.matrix_world)
    old=np.array(old);new=np.array(new)
    count=len(a);indices=np.arange(count)+start-217
    def frames():
        for i,row in enumerate(a):
            f=indices[i];p=np.array(row,dtype=np.float64)
            if 0<=f<144:
                world=p@transform[:3,:3].T+transform[:3,3]
                local=world@np.linalg.inv(old[f])[:3,:3].T+np.linalg.inv(old[f])[:3,3]
                # Height relative to head pivot: crown follows fully; shoulder
                # courses remain fixed. Continuous falloff avoids a new seam.
                height=world[:,2]-old[f,2,3]
                weights=smooth((height+1.05)/1.75)
                moved=local@new[f,:3,:3].T+new[f,:3,3]
                world+=(moved-world)*weights[:,None]
                p=world@inverse[:3,:3].T+inverse[:3,3]
            yield p.astype(np.float32)
    path=out/'performance-shawl.mdd';write_mdd(path,len(a),len(shawl.data.vertices),frames())
    attach_cache(shawl,path,start)
    np.savez_compressed(out/'head-motion.npz',before=old,after=new)
    return {'neck_vertices_reweighted':modified,'head_pitch_radians_range':[float(pitch.min()),float(pitch.max())],
        'shawl_method':'Small shot-space head-follow corrective on simulated cache; not resimulated cloth',
        'contact_and_visual_gate':'NOT_RUN','original_neutral_coordinates_preserved':True,
        'scope':'Six-second composed riding performance; not dialogue or arbitrary acting'}
