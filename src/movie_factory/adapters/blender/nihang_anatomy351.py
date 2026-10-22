"""Fixed elbow-plane reconstruction for the existing supporting actor.

Preserves original wrist/hand matrices and shoulder origins. No new rig, weights,
body shape, clothing or horse motion. Pure geometry functions are tested outside
Blender; numerical continuity is not artistic acceptance.
"""
import math
import numpy as np


def unit(v):
    v=np.asarray(v,dtype=float); length=np.linalg.norm(v)
    if not np.isfinite(length) or length<1e-8:raise ValueError('ARM351_DEGENERATE')
    return v/length


def plane_rotation(source_axis,source_other,target_axis,target_other):
    def frame(a,b):
        y=unit(a);z=unit(np.cross(y,b));x=np.cross(y,z)
        return np.column_stack((x,y,z))
    return frame(target_axis,target_other)@frame(source_axis,source_other).T


def reachable_elbow(shoulder,wrist,upper,lower,hint):
    a=np.asarray(shoulder);b=np.asarray(wrist);axis=unit(b-a);d=np.linalg.norm(b-a)
    if not abs(upper-lower)+1e-5<d<upper+lower-1e-5:raise ValueError('ARM351_UNREACHABLE')
    along=(upper**2-lower**2+d*d)/(2*d)
    center=a+axis*along
    pole=np.asarray(hint)-center;pole-=axis*np.dot(pole,axis)
    return center+unit(pole)*math.sqrt(max(0,upper**2-along**2))


def spear_elbow_hint(shoulder):
    """Below and slightly forward/outboard, rather than behind the rib cage.

    Rig-local coordinates: +X is actor left, -Y anterior, +Z up. This is a
    tested placement hypothesis, not a generic human-arm pose rule.
    """
    return np.asarray(shoulder,dtype=float)+np.array([.10,-.10,-.28])


def run(bpy,out):
    import json
    from mathutils import Matrix,Vector,Quaternion
    scene=bpy.context.scene;rig=bpy.data.objects['MF coherent Nihang rig']
    if rig.get('anatomy351'):raise ValueError('ARM351_ALREADY_APPLIED')
    rest=rig.data.bones;records=[];samples={}
    # Snapshot every pose before editing any key: no feedback from earlier edits.
    for f in range(252,442):
        scene.frame_set(f);bpy.context.view_layer.update()
        samples[f]={s:{n:rig.pose.bones[n].matrix.copy() for n in rig.pose.bones.keys()
                      if n.endswith('.'+s) and n.startswith(('upperarm','lowerarm','wrist','finger'))}
                    for s in ('L','R')}
    for f in range(252,442):
        scene.frame_set(f);bpy.context.view_layer.update()
        for side in ('L','R'):
            suffix='.'+side;old=samples[f][side]
            sn='upperarm01'+suffix;en='lowerarm01'+suffix;wn='wrist'+suffix
            s0=np.array(rest[sn].head_local);e0=np.array(rest[en].head_local);w0=np.array(rest[wn].head_local)
            s=np.array(old[sn].translation);w=np.array(old[wn].translation)
            hint=spear_elbow_hint(s) if side=='L' else old[en].translation
            e=reachable_elbow(s,w,np.linalg.norm(e0-s0),np.linalg.norm(w0-e0),hint)
            ru=plane_rotation(e0-s0,w0-e0,e-s,w-e)
            rl=plane_rotation(w0-e0,e0-s0,w-e,e-s)
            # Keep the original mild split-chain curvature. One rigid transform
            # per anatomical segment avoids individually straightening each bone.
            for names,rot,origin,target in ((('upperarm01','upperarm02'),ru,s0,s),
                                          (('lowerarm01','lowerarm02'),rl,e0,e)):
                for name in names:
                    pb=rig.pose.bones[name+suffix]
                    matrix=(Matrix(rot.tolist())@pb.bone.matrix_local.to_3x3()).to_4x4()
                    matrix.translation=Vector(target+rot@(np.array(pb.bone.head_local)-origin))
                    pb.rotation_mode='QUATERNION';pb.matrix=matrix
                    for prop in ('location','rotation_quaternion','scale'):pb.keyframe_insert(prop,frame=f)
                    bpy.context.view_layer.update()
            # Restore both wrist and every digit in armature space, so changing
            # forearm frames cannot drag the contact solve away from its owner.
            for name,matrix in old.items():
                if not name.startswith(('wrist','finger')):continue
                pb=rig.pose.bones[name];pb.rotation_mode='QUATERNION';pb.matrix=matrix
                for prop in ('location','rotation_quaternion','scale'):pb.keyframe_insert(prop,frame=f)
                bpy.context.view_layer.update()
            error=max((rig.pose.bones[n].matrix.translation-m.translation).length for n,m in old.items() if n.startswith(('wrist','finger')))
            if error>1e-4:raise ValueError('ARM351_CONTACT_CHANGED')
            records.append(dict(frame=f,side=side,elbow_shift=float(np.linalg.norm(e-np.array(old[en].translation))),contact_error=error))
    rig['anatomy351']=1;scene.frame_set(327);bpy.context.view_layer.update()
    report=dict(changed=True,method='Rest elbow plane transported to actual bend plane; split curvature retained; original wrist and digit matrices restored.',
                records=records,scope='Pose-only causal candidate; no visual or AV pass.')
    (out/'anatomy351.json').write_text(json.dumps(report,indent=2)+'\n')
    return report
