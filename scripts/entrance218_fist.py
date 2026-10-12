"""Closed bare-fist discrimination; no source parameters or runtime code."""
import json, sys, math
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import entrance214_contact as contact
OPS={'shape01':0,'shape02':1,'shape03':2,'shape04':3,'shape05':4,'shape06':5,'shape07':6,'shape08':7,'shape09':8,'fit10':7,'fit11':7,'opening12':7,'route13':7,'fit14':7,'fit15':7}

def rein_shape(old,channel,matrix,side):
    # Replace the old entrance as well as the interior channel. Otherwise the
    # previous little-finger position remains hidden in the retained polyline.
    import bpy
    rig=bpy.data.objects['MF_body156_fit_rig']
    pinky=rig.pose.bones['MF_fit_finger_3_0.'+side]
    ring=rig.pose.bones['MF_fit_finger_1_0.'+side]
    outward=((pinky.tail-pinky.head)+(ring.tail-ring.head)).normalized()
    entry=rig.matrix_world@((pinky.tail+ring.tail)*.5+outward*.065)
    incoming=np.array(old[:16],dtype=float)
    incoming+=(np.asarray(entry)-incoming[-1])*np.linspace(0,1,16)[:,None]**3
    points=np.vstack((incoming,np.array(channel)))
    start=points[-1];tangent=start-points[-2];tangent/=np.linalg.norm(tangent)
    end=start+tangent*.55+np.array([0.,0.,-1.4])
    a=start+tangent*.5;b=end+np.array([0.,0.,.3])
    tail=np.array([(1-t)**3*start+3*(1-t)**2*t*a+3*(1-t)*t*t*b+t**3*end for t in np.linspace(0,1,18)])
    return np.vstack((points,tail[1:]))

def rotate_aim(bone,target):
    import bpy
    from entrance200_pose_control import aim
    loc=bone.location.copy();scale=bone.scale.copy()
    aim(bone,target)
    q=bone.matrix_basis.to_quaternion().normalized()
    bone.rotation_mode='QUATERNION';bone.rotation_quaternion=q
    bone.location=loc;bone.scale=scale
    bpy.context.view_layer.update()

def pose(rig,side,variant=1):
    import bpy
    from mathutils import Vector,Quaternion
    sign=1 if side=='L' else -1
    hand=rig.pose.bones['hand.'+side]
    # Each root remains at its original joint. Bring PIP joints into a compact
    # staggered row with adduction, rather than curling the original spread fan.
    for d in range(5):
        for j in range(3):
            b=rig.pose.bones[f'MF_fit_finger_{d}_{j}.{side}']
            b.rotation_mode='QUATERNION';b.rotation_quaternion=Quaternion()
            b.location=(0,0,0)
            b.scale=(1,1,1)
    bpy.context.view_layer.update()
    if variant>=3:
        palm_pose(rig,side,adduct=variant==4,cup=variant>=5,distributed=variant>=6,resting_thumb=variant>=7,thumb_adduct=variant>=8)
        if variant>=6:
            # Shot-specific pad-volume corrective. Keep each posed joint center
            # and phalanx length; widen only transverse skinning axes. Explicit
            # world matrices avoid inherited scale compounding down the chain.
            names=[f'MF_fit_finger_{d}_{j}.{side}' for d in range(4) for j in range(3)]
            matrices={n:rig.pose.bones[n].matrix.copy() for n in names}
            for n in names:
                matrix=matrices[n].copy()
                for axis in (0,2):
                    for row in range(3):matrix[row][axis]*=1.45
                rig.pose.bones[n].matrix=matrix;bpy.context.view_layer.update()
        return
    ztargets={2:-.235,0:-.08,1:.065,3:.205}
    for d in (2,0,1,3):
        b=rig.pose.bones[f'MF_fit_finger_{d}_0.{side}']
        root=hand.matrix.inverted()@b.head
        # Curl nearly perpendicular into the palm, with modest lengthwise bend.
        target=Vector((root.x-sign*b.bone.length,.79-(.16 if variant>=2 else 0),ztargets[d]))
        if variant==0:target.z=root.z # control: no adduction
        rotate_aim(b,hand.matrix@target)
        for j,angle in ((1,115 if variant>=2 else 105),(2,75 if variant>=2 else 40)):
            bone=rig.pose.bones[f'MF_fit_finger_{d}_{j}.{side}']
            bone.rotation_mode='QUATERNION';bone.rotation_quaternion=Quaternion((1,0,0),math.radians(angle))
        bpy.context.view_layer.update()
    chain=[rig.pose.bones[f'MF_fit_finger_4_{j}.{side}'] for j in range(3)]
    origin=chain[0].head.copy();target=hand.matrix@Vector((sign*.08,.695,-.31) if variant>=2 else (sign*.025,.65,-.26))
    a=chain[0].bone.length;b=sum(x.bone.length for x in chain[1:])
    axis=(target-origin).normalized();distance=(target-origin).length
    if not abs(a-b)+.001<distance<a+b-.001:raise ValueError('Thumb reach')
    bend=hand.matrix.to_3x3()@Vector((sign*(.25 if variant<2 else -.25),0,-1))
    bend-=axis*bend.dot(axis);bend.normalize()
    c=(a*a+distance*distance-b*b)/(2*a*distance)
    joint=origin+axis*a*c+bend*a*math.sqrt(1-c*c)
    rotate_aim(chain[0],joint);rotate_aim(chain[1],target);rotate_aim(chain[2],target)

def palm_pose(rig,side,adduct=False,cup=False,distributed=False,resting_thumb=False,thumb_adduct=False):
    """Measured palm frame, coherent flexion plane, no translated joints."""
    import bpy
    from mathutils import Vector
    hand=rig.pose.bones['hand.'+side];inv=hand.matrix.inverted()
    roots={d:inv@rig.pose.bones[f'MF_fit_finger_{d}_0.{side}'].head for d in range(4)}
    lateral=(roots[3]-roots[2]).normalized()
    longitudinal=Vector((0,1,0));longitudinal-=lateral*longitudinal.dot(lateral);longitudinal.normalize()
    normal=lateral.cross(longitudinal).normalized()
    if normal.x*(1 if side=='L' else -1)>0:normal=-normal
    if cup:
        # Scoped metacarpal-cupping proxy: the coarse rig has no metacarpals.
        # Translate only finger roots within the hand, retaining phalanx lengths
        # and source mesh. Weight falloff blends these bases into the palm.
        goals={2:-.23,0:-.075,1:.08,3:.225}
        for d in (2,0,1,3):
            root=rig.pose.bones[f'MF_fit_finger_{d}_0.{side}']
            delta=lateral*(goals[d]-roots[d].dot(lateral))
            matrix=root.matrix.copy();matrix.translation+=hand.matrix.to_3x3()@delta
            root.matrix=matrix;bpy.context.view_layer.update()
    for d in (2,0,1,3):
        total=0
        for j,angle in enumerate((100,95,35)):
            total+=math.radians(angle)
            b=rig.pose.bones[f'MF_fit_finger_{d}_{j}.{side}']
            direction=longitudinal*math.cos(total)+normal*math.sin(total)
            if adduct and j==0:
                # The original splayed hand has roughly .23 root spacing;
                # flexion alone preserves those conspicuous lateral gaps.
                goals={2:-.24,0:-.075,1:.09,3:.245}
                direction+=lateral*((goals[d]-roots[d].dot(lateral))/b.bone.length)
                direction.normalize()
            rotate_aim(b,b.head+hand.matrix.to_3x3()@direction)
    # Thumb is nearly extended above the index, not folded around its side.
    chain=[rig.pose.bones[f'MF_fit_finger_4_{j}.{side}'] for j in range(3)]
    if resting_thumb:
        # A riding thumb lies along the upper index, not around a target in a
        # pinching arc. Retain full chain length with a small distal pad flex.
        if thumb_adduct:
            matrix=chain[0].matrix.copy();matrix.translation+=hand.matrix.to_3x3()@lateral*.07
            chain[0].matrix=matrix;bpy.context.view_layer.update()
        for j,bone in enumerate(chain):
            direction=(longitudinal+lateral*(0. if thumb_adduct else .14)+normal*(-.08 if j<2 else -.3)).normalized()
            rotate_aim(bone,bone.head+hand.matrix.to_3x3()@direction)
        return
    index=rig.pose.bones[f'MF_fit_finger_2_1.{side}']
    target=index.head.lerp(index.tail,.5)-hand.matrix.to_3x3()@lateral*.07
    origin=chain[0].head.copy();axis=(target-origin).normalized()
    a=chain[0].bone.length;b=sum(x.bone.length for x in chain[1:]);distance=(target-origin).length
    distance=min(a+b-.002,max(abs(a-b)+.002,distance));target=origin+axis*distance
    bend=hand.matrix.to_3x3()@(-lateral);bend-=axis*bend.dot(axis);bend.normalize()
    if distributed:
        lengths=[q.bone.length for q in chain]
        lo,hi=0.,math.pi*.9
        for _ in range(48):
            angle=(lo+hi)/2
            x=sum(l*math.cos(k*angle) for l,k in zip(lengths,(1,0,-1)))
            y=sum(l*math.sin(k*angle) for l,k in zip(lengths,(1,0,-1)))
            if math.hypot(x,y)>distance:lo=angle
            else:hi=angle
        correction=math.atan2(y,x)
        for bone,k in zip(chain,(1,0,-1)):
            direction=axis*math.cos(k*angle-correction)+bend*math.sin(k*angle-correction)
            rotate_aim(bone,bone.head+direction)
        return
    c=(a*a+distance*distance-b*b)/(2*a*distance)
    joint=origin+axis*a*c+bend*a*math.sqrt(1-c*c)
    rotate_aim(chain[0],joint);rotate_aim(chain[1],target);rotate_aim(chain[2],target)

def isolate(scene):
    import bpy
    retained={bpy.data.objects[n] for n in ('MF_studio_adult_body','MF_body156_fit_rig','MF185_rein_L','MF185_rein_R')}
    retained.add(scene.camera);pending=list(retained)
    while pending:
        ob=pending.pop();refs=[ob.parent]
        owners=[ob,ob.data,*ob.modifiers,*ob.constraints]
        if ob.type=='ARMATURE':owners.extend(c for b in ob.pose.bones for c in b.constraints)
        for owner in owners:
            if owner is None:continue
            for prop in owner.bl_rna.properties:
                if prop.type=='POINTER' and prop.identifier!='rna_type':
                    value=getattr(owner,prop.identifier,None)
                    if isinstance(value,bpy.types.Object):refs.append(value)
            ad=getattr(owner,'animation_data',None)
            if ad:
                for driver in ad.drivers:
                    refs.extend(t.id for v in driver.driver.variables for t in v.targets if isinstance(t.id,bpy.types.Object))
        for ref in refs:
            if ref is not None and ref not in retained:retained.add(ref);pending.append(ref)
    for ob in list(bpy.data.objects):
        if ob not in retained:bpy.data.objects.remove(ob,do_unlink=True)
    for ob in scene.objects:
        for m in ob.modifiers:
            if m.type in ('SMOOTH','CORRECTIVE_SMOOTH','SUBSURF'):m.show_render=False;m.show_viewport=False

def views(scene,out):
    import bpy
    from mathutils import Vector
    rig=bpy.data.objects['MF_body156_fit_rig'];cam=scene.camera
    cam.animation_data_clear();cam.data.animation_data_clear();cam.parent=None;cam.constraints.clear()
    cam.rotation_mode='XYZ';cam.data.type='ORTHO';cam.data.ortho_scale=1.85
    scene.render.engine='BLENDER_WORKBENCH';scene.render.resolution_x=640;scene.render.resolution_y=640;scene.render.resolution_percentage=100
    scene.display.shading.light='STUDIO';scene.display.shading.studiolight_rotate_z=.5
    scene.display.shading.color_type='SINGLE';scene.display.shading.single_color=(.55,.43,.34)
    scene.display.shading.show_shadows=True;scene.display.shading.show_cavity=True
    scene.display.shading.cavity_type='BOTH';scene.display.shading.background_type='WORLD';scene.world.color=(.18,.18,.18)
    scene.display.render_aa='16'
    body=bpy.data.objects['MF_studio_adult_body']
    group=body.vertex_groups.new(name='218 isolated diagnostic hand')
    mask=body.modifiers.new('218 isolate viewed hand','MASK');mask.vertex_group=group.name
    for side,sign in (('L',1),('R',-1)):
        group.remove(list(range(len(body.data.vertices))))
        names={g.index:g.name for g in body.vertex_groups}
        ids=[v.index for v in body.data.vertices if sum(g.weight for g in v.groups if names.get(g.group,'').endswith('.'+side) and ('finger' in names[g.group] or names[g.group]=='hand.'+side))>.05]
        group.add(ids,1.,'REPLACE')
        mat=rig.matrix_world@rig.pose.bones['hand.'+side].matrix
        target=mat@Vector((0,.55,-.02))
        for name,offset in [('palm',(-sign*3,0,-.4)),('side',(-sign*1.8,.4,-3)),('knuckles',(sign*3,0,-.3))]:
            cam.location=target+mat.to_3x3()@Vector(offset)
            cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
            scene.render.filepath=str(out/f'{side}-{name}.png');bpy.ops.render.render(write_still=True)

def validate(job):
    if not isinstance(job,dict) or set(job)!={'operation'} or job['operation'] not in OPS:raise ValueError('Closed218 operation required')
    return OPS[job['operation']]

def fit_control(scene,out,new_route=False):
    import bpy
    from wardrobe_motion178_controls import render_geometry_paused
    rig=bpy.data.objects['MF_body156_fit_rig'];cam=scene.camera
    for ob in scene.objects:
        for m in ob.modifiers:
            if m.type in ('SMOOTH','CORRECTIVE_SMOOTH','SUBSURF'):m.show_viewport=False
    scene.frame_set(360);bpy.context.view_layer.update();rig.animation_data.action=None
    # Full surfaces and actual materials. No gloves, no pruned diagnostic.
    with render_geometry_paused():
        for side in ('L','R'):pose(rig,side,7)
    contact.reins(scene,shape_fn=rein_shape if new_route else contact.rein_shape)
    for side in ('L','R'):
        ob=bpy.data.objects['MF185_rein_'+side];ob.data.bevel_mode='OBJECT';ob.data.bevel_object=contact.leather_profile(scene)
    contact.hand_data(scene,out)
    scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=8;scene.render.use_persistent_data=False
    scene.render.resolution_x=432;scene.render.resolution_y=768;scene.render.resolution_percentage=100
    scene.render.filepath=str(out/'actual-360.png');bpy.ops.render.render(write_still=True)
    contact.controls(scene,out)
    contact.base.check_protected()
    (out/'result.json').write_text(json.dumps({'source_sha256':contact.SOURCES['opening'][1],'visual_gate':'NOT_RUN','scope':'Bare pose08 with actual rein and finished surfaces, no production native saved'},indent=2)+'\n')

def selected_pose(rig,side):
    pose(rig,side,7)

def production(scene,out,kind):
    import bpy
    control=contact.base.BASE/'entrance218-fit15'
    admission=json.loads((control/'internal-review.json').read_text())
    if admission.get('status')!='PROCEED_TO_BUILD':raise ValueError('Bare fist and rein admission required')
    for name,sha in admission['images'].items():
        if contact.base.digest(control/name)!=sha:raise ValueError('Changed control evidence')
    contact.build(scene,out,kind,pose_fn=selected_pose,changed_digits=tuple(range(5)),key_transform=True,shape_fn=rein_shape)
    for ob in scene.objects:
        for m in ob.modifiers:
            if m.type in ('SMOOTH','CORRECTIVE_SMOOTH','SUBSURF'):m.show_viewport=False
    scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=8;scene.render.use_persistent_data=False
    scene.render.resolution_x=432;scene.render.resolution_y=768;scene.render.resolution_percentage=100
    for frame in ((277,330,360) if kind=='opening' else (390,427,472,550,620)):
        scene.frame_set(frame);scene.render.filepath=str(out/f'actual-{frame}.png');bpy.ops.render.render(write_still=True)
    scene.frame_set(360 if kind=='opening' else 427)
    contact.hand_data(scene,out);contact.controls(scene,out);contact.base.check_protected()

def main():
    import bpy
    job=json.loads(Path(sys.argv[sys.argv.index('--')+1]).read_text());variant=validate(job)
    out=contact.base.BASE/('entrance218-'+job['operation'])
    if out.exists():raise ValueError('Preserve previous evidence')
    out.mkdir();(out/'handler.py').write_bytes(Path(__file__).read_bytes())
    kind='route' if job['operation']=='route13' else 'opening'
    scene=contact.load(kind)
    if job['operation'] in ('opening12','route13'):
        production(scene,out,kind);return
    if job['operation'] in ('fit10','fit11','fit14','fit15'):
        fit_control(scene,out,new_route=job['operation']!='fit10');return
    for ob in scene.objects:
        for m in ob.modifiers:
            if m.type in ('SMOOTH','CORRECTIVE_SMOOTH','SUBSURF'):m.show_viewport=False
    scene.frame_set(360);bpy.context.view_layer.update()
    contact.base.check_protected();isolate(scene)
    rig=bpy.data.objects['MF_body156_fit_rig'];rig.animation_data.action=None
    if variant==4:
        from mathutils import Quaternion
        for bone in rig.pose.bones:
            if 'MF_fit_finger' in bone.name:bone.rotation_mode='QUATERNION';bone.rotation_quaternion=Quaternion()
        bpy.context.view_layer.update()
        rest=out/'rest';rest.mkdir();views(scene,rest)
        body=bpy.data.objects['MF_studio_adult_body']
        body.modifiers.remove(body.modifiers['218 isolate viewed hand'])
        body.vertex_groups.remove(body.vertex_groups['218 isolated diagnostic hand'])
    for side in ('L','R'):pose(rig,side,variant)
    for side in ('L','R'):bpy.data.objects['MF185_rein_'+side].hide_render=True
    contact.hand_data(scene,out);views(scene,out)
    (out/'result.json').write_text(json.dumps({'source_sha256':contact.SOURCES['opening'][1],'visual_gate':'NOT_RUN','variant':variant,'scope':'Unsaved bare-hand coarse shape control; no gloves or rein'},indent=2)+'\n')
if __name__=='__main__':main()
