"""Causal control on the actual upper-arm skin owner, not pectoral weights.

Only four existing deform bones' segment counts can change. No edit mode,
pose curves, weights, geometry or primary joint matrices may change.
"""
import json
import numpy as np

BONES=('DEF-upper_arm.L','DEF-upper_arm.L.001','DEF-upper_arm.R','DEF-upper_arm.R.001')

def validate(e):
    if not isinstance(e,dict) or set(e)!={'kind','target','mode'} or e['kind']!='mounted_upperarm387_rigid' or e['target']!='horse':raise ValueError('UPPERARM387_FIELDS')
    if type(e['mode']) is not int or e['mode'] not in (0,1):raise ValueError('UPPERARM387_MODE')
    return e

def segments(bones,mode):
    old={b.name:b.bbone_segments for b in bones}
    if any(old.get(n)!=10 for n in BONES):raise ValueError('UPPERARM387_SOURCE_SEGMENTS')
    if mode:
        for n in BONES:bones[n].bbone_segments=1
    expected={n:(1 if mode and n in BONES else count) for n,count in old.items()}
    if {b.name:b.bbone_segments for b in bones}!=expected:raise ValueError('UPPERARM387_SEGMENT_DRIFT')
    return old,expected

def run(bpy,out,e,helpers):
    validate(e);horse=bpy.data.objects['horse'];rig=bpy.data.objects['horse.rig']
    if any(horse.get(k) for k in ('cache376','upperarm_rigid387','muscle386','support386','weights386','bind_preserve386')):raise ValueError('UPPERARM387_SOURCE')
    if len(horse.data.vertices)!=22514 or not rig.animation_data or not rig.animation_data.action:raise ValueError('UPPERARM387_DATA')
    raw=np.array([v.co[:] for v in horse.data.vertices],np.float32)
    names,w=helpers('anatomy_bind386').weights(horse);ownership=w[:,[names.index(n) for n in BONES]].sum(1);affected=ownership>0
    if not affected.any() or raw[affected,2].min()<.95:raise ValueError('UPPERARM387_WEIGHT_DOMAIN')
    geometry=helpers('nihang_prep367').frozen(bpy);actions=helpers('nihang_padsolve370').actions(bpy)
    rests={b.name:[list(row) for row in b.matrix_local] for b in rig.data.bones}
    all_names=[b.name for b in rig.pose.bones];cap=helpers('anatomy_muscle386')
    before,mat_before=cap.capture(bpy,horse,rig,all_names,helpers)
    old,new=segments(rig.data.bones,e['mode']);bpy.context.view_layer.update()
    after,mat_after=cap.capture(bpy,horse,rig,all_names,helpers)
    error=np.linalg.norm(after-before,axis=2);distal=raw[:,2]<.95
    metrics=dict(primary_matrix_error=float(abs(mat_after-mat_before).max()),outside_error=float(error[:,~affected].max()),distal_error=float(error[:,distal].max()),max_delta=float(error.max()),neutral_error=float(error[cap.FRAMES.index(283)].max()),affected_vertices=int(affected.sum()),minimum_affected_rest_z=float(raw[affected,2].min()),per_pose_max={str(f):float(error[i].max()) for i,f in enumerate(cap.FRAMES)})
    _,wa=helpers('anatomy_bind386').weights(horse)
    preserved=(geometry==helpers('nihang_prep367').frozen(bpy) and actions==helpers('nihang_padsolve370').actions(bpy) and rests=={b.name:[list(row) for row in b.matrix_local] for b in rig.data.bones} and np.array_equal(w,wa))
    report=dict(mode=e['mode'],metrics=metrics,segments_before=old,segments_after=new,geometry_weights_actions_rest_exact=preserved,frames=cap.FRAMES,scope='Actual upper-arm segmentation causal control only. Natural anatomy, embedding, complete performance and production approval remain separate.')
    (out/'anatomy387-upperarm.json').write_text(json.dumps(report,indent=2)+'\n')
    np.savez_compressed(out/'anatomy387-upperarm.npz',raw=raw,ownership=ownership,affected=affected,pose_before=before,pose_after=after,rig_before=mat_before,rig_after=mat_after,frames=np.array(cap.FRAMES))
    if not preserved or metrics['primary_matrix_error']>1e-7 or max(metrics['outside_error'],metrics['distal_error'])>2e-5 or metrics['max_delta']>.4 or (not e['mode'] and metrics['max_delta']>2e-5):raise ValueError('UPPERARM387_PRESERVATION')
    report['diagnostic_render_profile']=helpers('anatomy_static387').freeze(bpy.context.scene)
    if e['mode']:horse['upperarm_rigid387']=True
    (out/'anatomy387-upperarm.json').write_text(json.dumps(report,indent=2)+'\n');return report
