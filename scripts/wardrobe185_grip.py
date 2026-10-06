"""Fixed native hand-deformation controls before claiming rein grasp."""
import json
from pathlib import Path
import numpy as np


def riding_grip(rig):
    """Narrow authored hold, not a general grasp/contact solver."""
    import math
    for side in ('L','R'):
        for digit in range(4):
            for joint,angle in enumerate((80,100,55)):
                b=rig.pose.bones[f'MF_fit_finger_{digit}_{joint}.{side}']
                b.rotation_mode='XYZ';b.rotation_euler.x=math.radians(angle)


def rein_channel(rig,side):
    """Inside each curled chain rather than its skin/bone endpoint.

    Ordered ring/pinky entrance, palm, index exit. This is an authored
    geometric hypothesis that requires the rendered grip review.
    """
    centers={}
    for digit in range(4):
        bones=[rig.pose.bones[f'MF_fit_finger_{digit}_{j}.{side}'] for j in range(3)]
        centers[digit]=rig.matrix_world@((bones[0].head+bones[0].tail+bones[1].tail+bones[2].tail)/4)
    return [centers[3].lerp(centers[1],.5),centers[1],centers[0],centers[2]]


def audit(out):
    import bpy
    from mathutils import Matrix
    from wardrobe_motion178 import BASE,digest,check_protected
    from wardrobe_riding_fit import riding_pose,fit_render
    from wardrobe_motion178_controls import render_geometry_paused
    source=BASE/'wardrobe185-motionreview03/diagnostic.blend'
    if digest(source)!='0f128ba60947d4451f7e0bbaa3a5f6f275173702e3d4bddd245cef73d2310bd7':raise ValueError('Grip input changed')
    (out/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False)
    body=bpy.data.objects['MF_studio_adult_body'];rig=bpy.data.objects['MF_body156_fit_rig'];scene=bpy.context.scene
    with render_geometry_paused():
        rig.animation_data_clear();riding_pose(rig,1.)
        if out.name.endswith(('gripcheck02','gripcheck03')):
            import math
            for side in ('L','R'):
                for digit in range(4):
                    for joint,angle in enumerate((80,100,55)):
                        b=rig.pose.bones[f'MF_fit_finger_{digit}_{joint}.{side}'];b.rotation_mode='XYZ';b.rotation_euler.x=math.radians(angle)
        bpy.context.view_layer.update()
    names={g.index:g.name for g in body.vertex_groups};counts={n:0 for n in names.values() if 'finger' in n or n.startswith('hand.')}
    sums={n:0. for n in counts}
    for v in body.data.vertices:
        for g in v.groups:
            if names[g.group] in counts and g.weight>1e-5:counts[names[g.group]]+=1;sums[names[g.group]]+=g.weight
    flags=[(m,m.show_viewport) for m in body.modifiers if m.type=='SUBSURF']
    for m,_ in flags:m.show_viewport=False
    def points():
        bpy.context.view_layer.update();ev=body.evaluated_get(bpy.context.evaluated_depsgraph_get());m=ev.to_mesh()
        q=np.array([v.co[:] for v in m.vertices]);ev.to_mesh_clear();return q
    posed={b.name:b.matrix_basis.copy() for b in rig.pose.bones if 'MF_fit_finger' in b.name}
    before=points()
    for name in posed:rig.pose.bones[name].matrix_basis=Matrix.Identity(4)
    zero=points()
    for name,matrix in posed.items():rig.pose.bones[name].matrix_basis=matrix
    for m,state in flags:m.show_viewport=state
    bpy.context.view_layer.update()
    result={'counts':counts,'weight_sums':sums,'max_finger_control_vertex_change_native':float(np.linalg.norm(before-zero,axis=1).max()),
        'vertices_changed':int(np.count_nonzero(np.linalg.norm(before-zero,axis=1)>1e-5)),
        'finger_controls':{n:{'use_deform':rig.data.bones[n].use_deform,'head_rest':list(rig.data.bones[n].head_local),'basis':[list(r) for r in m]} for n,m in posed.items()},
        'modifiers':[{'name':m.name,'type':m.type,'viewport':m.show_viewport,'render':m.show_render,'object':getattr(m,'object',None).name if getattr(m,'object',None) else None,'vertex_group':getattr(m,'vertex_group',None)} for m in body.modifiers],
        'shape_values':{k.name:k.value for k in body.data.shape_keys.key_blocks}}
    (out/'result.json').write_text(json.dumps(result,indent=2)+'\n')
    if out.name.endswith('gripcheck03'):
        for ob in scene.objects:
            if ob.type in ('MESH','CURVE','CURVES'):ob.hide_render=ob!=body
        group=body.vertex_groups.new(name='185 isolated left hand')
        ids=[v.index for v in body.data.vertices if sum(g.weight for g in v.groups if names.get(g.group,'').endswith('.L') and ('finger' in names[g.group] or names[g.group]=='hand.L'))>.1]
        group.add(ids,1.,'REPLACE')
        mask=body.modifiers.new('Isolated hand diagnostic','MASK');mask.vertex_group=group.name
        # Group interpolates through subdivision; no changes to source basis.
        result['posed_bones']={b.name:{'head':list(b.head),'tail':list(b.tail),'matrix':[list(r) for r in b.matrix]} for b in rig.pose.bones if 'finger' in b.name or b.name.startswith('hand.')}
        (out/'result.json').write_text(json.dumps(result,indent=2)+'\n')
    scene.cycles.device='CPU';scene.cycles.samples=8
    for side,angle in (('L',70),('R',290)):
        target=rig.matrix_world@rig.pose.bones['hand.'+side].head
        fit_render(out,'closed-'+side,angle,tuple(target),2.8,(600,600))
    if out.name.endswith(('gripcheck02','gripcheck03')):
        target=rig.matrix_world@rig.pose.bones['hand.L'].head
        for label,angle in (('palm',250),('front',0)):
            fit_render(out,label+'-L',angle,tuple(target),2.8,(600,600))
    check_protected()
