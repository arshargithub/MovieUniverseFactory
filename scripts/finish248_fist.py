"""Closed, source-bound final hand diagnosis and correction. No runtime code inputs."""
import json, sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import wardrobe_motion178 as base
OUT=ROOT/'.runtime/art-direction/series01-finish248'
SOURCES={'opening':('finish245-opening01','0442db9c875f2c0c337fbb5f3e3d11f5f0d125ad923d38eb3efb4ebad39ca4c2'),
         'route':('finish245-route03','cc5f164e435d93c3f34f1391970ee276137c4850a11c8980276624eb103b69af')}
OPS={'inspect01','rest02','shape03','shape04','shape05','shape06','fit07','opening08','route09'}
def validate(job):
    if not isinstance(job,dict) or set(job)!={'operation'} or job['operation'] not in OPS:
        raise ValueError('Closed248 operation required')
    return job['operation']
def load(kind):
    import bpy
    name,sha=SOURCES[kind];folder=base.BASE/name
    rec=json.loads((folder/'result.json').read_text())
    if base.digest(folder/'scene.blend')!=sha or rec['native_sha256']!=sha:raise ValueError('Native source changed')
    for c in rec['caches']:
        if base.digest((folder/c['path']).resolve())!=c['sha256']:raise ValueError('Cache changed')
    bpy.ops.wm.open_mainfile(filepath=str(folder/'scene.blend'),load_ui=False,use_scripts=False)
    return bpy.context.scene
def inspect(scene,out,rest=False):
    import bpy
    import entrance218_fist as old
    import entrance214_contact as contact
    scene.frame_set(360)
    base.check_protected()
    old.isolate(scene)
    rig=bpy.data.objects['MF_body156_fit_rig'];body=bpy.data.objects['MF_studio_adult_body']
    contact.hand_data(scene,out)
    rest={b.name:dict(head=list(b.head_local),tail=list(b.tail_local),matrix=[list(r) for r in b.matrix_local]) for b in rig.data.bones if 'finger' in b.name or b.name.startswith('hand.')}
    weights=[[(body.vertex_groups[g.group].name,g.weight) for g in v.groups] for v in body.data.vertices]
    (out/'rest.json').write_text(json.dumps(dict(bones=rest,weights=weights,body_matrix=[list(r) for r in body.matrix_world],rig_matrix=[list(r) for r in rig.matrix_world],modifiers=[(m.name,m.type) for m in body.modifiers]),indent=2))
    np.savez_compressed(out/'rest.npz',vertices=np.array([v.co for v in body.data.vertices]),faces=np.array([list(p.vertices) for p in body.data.polygons],dtype=object))
    for side in ('L','R'):bpy.data.objects['MF185_rein_'+side].hide_render=True
    if rest:
        rig.animation_data_clear()
        for b in rig.pose.bones:
            if 'MF_fit_finger_' in b.name:b.matrix_basis.identity()
        bpy.context.view_layer.update()
    old.views(scene,out)
def repair_roots(body,rig,shift,complete=False):
    """Move MCP origins toward measured palm, retaining PIP/DIP/rest surface.

    Reassign proximal skin across that hinge; no changes to other body weights.
    This is a shot-specific rig derivative, not an accepted neutral mesh edit.
    """
    import bpy
    from mathutils import Vector
    bpy.context.view_layer.objects.active=rig;rig.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    for side in ('L','R'):
        h=rig.data.edit_bones['hand.'+side]
        delta=h.matrix.to_3x3()@Vector((0,-shift,0))
        for d in range(4):
            b=rig.data.edit_bones[f'MF_fit_finger_{d}_0.{side}']
            z=b.z_axis.copy();b.head+=delta;b.align_roll(z)
    bpy.ops.object.mode_set(mode='OBJECT')
    transform=rig.matrix_world.inverted()@body.matrix_world
    names={g.index:g.name for g in body.vertex_groups}
    for side in ('L','R'):
        hand=body.vertex_groups['hand.'+side]
        chains=[[rig.data.bones[f'MF_fit_finger_{d}_{j}.{side}'] for j in range(3)] for d in range(4)]
        for v in body.data.vertices:
            current={names[g.group]:g.weight for g in v.groups}
            if sum(current.get(f'MF_fit_finger_4_{j}.{side}',0) for j in range(3))>.05:continue
            total=current.get(hand.name,0)+sum(current.get(b.name,0) for ch in chains for b in ch)
            if total<.01:continue
            p=transform@v.co
            def projected(ch):
                rows=[];start=0
                for b in ch:
                    axis=(b.tail_local-b.head_local).normalized();u=(p-b.head_local).dot(axis)
                    rows.append(((p-b.head_local-axis*max(0,min(b.length,u))).length,start+u))
                    start+=b.length
                return min(rows)
            weighted=max(chains,key=lambda ch:sum(current.get(b.name,0) for b in ch))
            chain=weighted if sum(current.get(b.name,0) for b in weighted)>.03 else min(chains,key=lambda ch:projected(ch)[0])
            distance,u=projected(chain)
            support=min(1,max(0,(u+.075)/.15))*min(1,max(0,(.22-distance)/.075))
            if complete:support=min(1,max(0,(u+.075)/.15))
            j1=chain[0].length;j2=j1+chain[1].length
            def smooth(x):x=min(1,max(0,x));return x*x*(3-2*x)
            a=smooth((u-j1+.07)/.14);b=smooth((u-j2+.055)/.11)
            fractions=(1-a,a*(1-b),a*b)
            for ch in chains:
                for bone in ch:body.vertex_groups[bone.name].remove([v.index])
            hand.add([v.index],total*(1-support),'REPLACE')
            for bone,w in zip(chain,fractions):body.vertex_groups[bone.name].add([v.index],total*support*w,'REPLACE')
    bpy.context.view_layer.update()
def final_pose(rig,side):
    import bpy,math
    from mathutils import Vector,Quaternion
    from entrance218_fist import rotate_aim
    hand=rig.pose.bones['hand.'+side]
    for d in range(5):
        for j in range(3):
            b=rig.pose.bones[f'MF_fit_finger_{d}_{j}.{side}'];b.rotation_mode='QUATERNION';b.rotation_quaternion=Quaternion();b.location=(0,0,0);b.scale=(1,1,1)
    bpy.context.view_layer.update();inv=hand.matrix.inverted()
    roots={d:inv@rig.pose.bones[f'MF_fit_finger_{d}_0.{side}'].head for d in range(4)}
    lateral=(roots[3]-roots[2]).normalized();longitudinal=Vector((0,1,0));longitudinal-=lateral*longitudinal.dot(lateral);longitudinal.normalize()
    normal=lateral.cross(longitudinal).normalized()
    if normal.x*(1 if side=='L' else -1)>0:normal=-normal
    for d,target in ((2,-.23),(0,-.075),(1,.08),(3,.225)):
        root=rig.pose.bones[f'MF_fit_finger_{d}_0.{side}'];m=root.matrix.copy();m.translation+=hand.matrix.to_3x3()@lateral*(target-roots[d].dot(lateral));root.matrix=m;bpy.context.view_layer.update()
        total=0
        for j,angle in enumerate((80,120,50)):
            total+=math.radians(angle);b=rig.pose.bones[f'MF_fit_finger_{d}_{j}.{side}']
            rotate_aim(b,b.head+hand.matrix.to_3x3()@(longitudinal*math.cos(total)+normal*math.sin(total)))
    for j in range(3):
        b=rig.pose.bones[f'MF_fit_finger_4_{j}.{side}'];direction=(longitudinal+lateral*.14+normal*(-.08 if j<2 else -.3)).normalized();rotate_aim(b,b.head+hand.matrix.to_3x3()@direction)
    names=[f'MF_fit_finger_{d}_{j}.{side}' for d in range(4) for j in range(3)]
    matrices={n:rig.pose.bones[n].matrix.copy() for n in names}
    for n in names:
        m=matrices[n].copy()
        for axis in (0,2):
            for row in range(3):m[row][axis]*=1.35
        rig.pose.bones[n].matrix=m;bpy.context.view_layer.update()
def shapes(scene,out,refined=False,complete=False):
    import bpy
    import entrance218_fist as old
    scene.frame_set(360);base.check_protected();old.isolate(scene)
    rig=bpy.data.objects['MF_body156_fit_rig'];body=bpy.data.objects['MF_studio_adult_body']
    rig.animation_data_clear()
    original=rig.data.copy()
    weights=[[(g.group,g.weight) for g in v.groups] for v in body.data.vertices]
    for side in ('L','R'):bpy.data.objects['MF185_rein_'+side].hide_render=True
    variants=[('continuous12',.12)] if complete else ([('smooth12',.12),('smooth12slim',.12)] if refined else [('rest',0),('pivot12',.12),('pivot20',.20)])
    for label,shift in variants:
        rig.data=original.copy()
        for group in body.vertex_groups:group.remove(list(range(len(body.data.vertices))))
        for i,row in enumerate(weights):
            for gi,w in row:body.vertex_groups[gi].add([i],w,'REPLACE')
        for b in rig.pose.bones:
            if 'MF_fit_finger_' in b.name:b.matrix_basis.identity()
        if shift:
            repair_roots(body,rig,shift,complete=complete)
            for side in ('L','R'):
                if complete:final_pose(rig,side)
                else:old.pose(rig,side,7)
            if label=='smooth12slim':
                # Test prior pad widening as a separate source of a swollen grasp.
                for side in ('L','R'):
                    names=[f'MF_fit_finger_{d}_{j}.{side}' for d in range(4) for j in range(3)]
                    matrices={n:rig.pose.bones[n].matrix.copy() for n in names}
                    for n in names:
                        m=matrices[n].copy()
                        for axis in (0,2):
                            for row in range(3):m[row][axis]*=1.18/1.45
                        rig.pose.bones[n].matrix=m;bpy.context.view_layer.update()
        bpy.context.view_layer.update()
        folder=out/label;folder.mkdir();old.views(scene,folder)
        body.modifiers.remove(body.modifiers['218 isolate viewed hand'])
        body.vertex_groups.remove(body.vertex_groups['218 isolated diagnostic hand'])
        if complete:
            for m in body.modifiers:
                if m.type=='SUBSURF':m.show_render=True;m.render_levels=2
            folder=out/(label+'-surface');folder.mkdir();old.views(scene,folder)
def surface_config(scene):
    import bpy,os
    if os.environ.get('CYCLES_METAL_DISABLE_BINARY_ARCHIVES')!='1':raise ValueError('Metal workaround required')
    prefs=bpy.context.preferences.addons['cycles'].preferences;prefs.compute_device_type='METAL'
    devices=prefs.get_devices_for_type('METAL')
    if not any(d.type=='METAL' for d in devices):raise ValueError('No Metal device')
    for d in devices:d.use=d.type=='METAL'
    prefs.metalrt='ON'
    for ob in scene.objects:
        for m in ob.modifiers:
            if m.type in ('SMOOTH','CORRECTIVE_SMOOTH','SUBSURF'):m.show_viewport=False
    scene.render.engine='CYCLES';scene.cycles.device='GPU';scene.cycles.samples=16
    scene.render.use_persistent_data=False;scene.render.use_motion_blur=False
    scene.render.resolution_x=1080;scene.render.resolution_y=1920;scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGB';scene.render.image_settings.color_depth='8'
def fit(scene,out):
    import bpy
    import entrance214_contact as contact
    from entrance218_fist import rein_shape
    from wardrobe_motion178_controls import render_geometry_paused
    scene.frame_set(360);base.check_protected()
    rig=bpy.data.objects['MF_body156_fit_rig'];body=bpy.data.objects['MF_studio_adult_body']
    with render_geometry_paused():
        rig.animation_data_clear();repair_roots(body,rig,.12,complete=True)
        for side in ('L','R'):final_pose(rig,side)
        for side in ('L','R'):bpy.data.objects['MF185_rein_'+side].hide_viewport=False
        contact.reins(scene,shape_fn=rein_shape)
    surface_config(scene)
    scene.render.filepath=str(out/'actual-360.png');bpy.ops.render.render(write_still=True)
    contact.controls(scene,out);base.check_protected()
def production(scene,out,kind):
    import bpy
    import entrance214_contact as contact
    from entrance218_fist import rein_shape
    from wardrobe_motion178_controls import render_geometry_paused
    admission=json.loads((OUT/'fit07/admission.json').read_text())
    if admission['status']!='PROCEED_TO_BUILD':raise ValueError('No surface/contact admission')
    for p,sha in admission['evidence'].items():
        if base.digest(ROOT/p)!=sha:raise ValueError('Changed admission evidence')
    rig=bpy.data.objects['MF_body156_fit_rig'];body=bpy.data.objects['MF_studio_adult_body']
    base.check_protected();rig.data.use_fake_user=True;rig.data=rig.data.copy()
    with render_geometry_paused():repair_roots(body,rig,.12,complete=True)
    frames=range(217,451) if kind=='opening' else range(451,697)
    contact.build(scene,out,kind,pose_fn=final_pose,changed_digits=tuple(range(5)),key_transform=True,shape_fn=rein_shape,frames_override=frames,source_sha256=SOURCES[kind][1])
    rec=json.loads((out/'result.json').read_text());rec.update(scope='248 reversible hand-only MCP origins/weights/finger pose/rein derivative; neutral mesh and all non-finger motion preserved',frames=[frames.start,frames.stop-1],handler_sha256=base.digest(Path(__file__)))
    (out/'result.json').write_text(json.dumps(rec,indent=2)+'\n')
    surface_config(scene)
    for frame in ((305,360,410,450) if kind=='opening' else (475,499,523,580,631,676,696)):
        scene.frame_set(frame);scene.render.filepath=str(out/f'actual-{frame}.png');bpy.ops.render.render(write_still=True)
def main():
    job=json.loads(Path(sys.argv[sys.argv.index('--')+1]).read_text());op=validate(job)
    out=OUT/op
    if out.exists():raise ValueError('Preserve earlier evidence')
    out.mkdir(parents=True)
    kind='route' if op=='route09' else 'opening';scene=load(kind)
    if op in ('shape03','shape04','shape05','shape06'):shapes(scene,out,refined=op=='shape04',complete=op in ('shape05','shape06'))
    elif op=='fit07':fit(scene,out)
    elif op in ('opening08','route09'):production(scene,out,kind)
    else:inspect(scene,out,rest=op=='rest02')
if __name__=='__main__':main()
