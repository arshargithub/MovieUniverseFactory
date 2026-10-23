"""Fixed rein trajectory audit; no action/mesh/material changes."""
import json
import hashlib
import importlib.util
from pathlib import Path


def trajectory_metrics(paths):
    """Measure shape change after removing linear endpoint displacement."""
    import numpy as np
    p = np.asarray(paths, dtype=float)
    if p.ndim != 3 or p.shape[2] != 3 or p.shape[1] < 3 or not np.isfinite(p).all():
        raise ValueError('REIN361_TRAJECTORY')
    u = np.linspace(0, 1, p.shape[1])[None, :, None]
    chord = p[:, :1] * (1-u) + p[:, -1:] * u
    residual = p-chord
    delta = np.linalg.norm(np.diff(residual, axis=0), axis=2)
    lengths = np.linalg.norm(np.diff(p, axis=1), axis=2).sum(axis=1)
    worst = np.argsort(delta.max(axis=1))[::-1][:10]
    return dict(maximum_residual_step=float(delta.max()),
                maximum_length_step=float(abs(np.diff(lengths)).max()),
                worst=[dict(from_frame=252+int(i), to_frame=253+int(i),
                            residual_step=float(delta[i].max()),
                            point=int(delta[i].argmax()),
                            length_step=float(lengths[i+1]-lengths[i])) for i in worst])


def audit(bpy, out):
    from mathutils import Vector
    scene = bpy.context.scene
    rig = bpy.data.objects['horse.rig']
    if not rig.get('rein358'):
        raise ValueError('REIN361_AUDIT_PARENT')
    reins = sorted([o for o in bpy.data.objects if o.name.startswith('leader supported rein292')], key=lambda o:o.name)
    if len(reins) != 2 or any(len(o.data.splines[0].points) != 129 for o in reins):
        raise ValueError('REIN361_AUDIT_PAIR')
    frame = scene.frame_current
    paths = {o.name:[] for o in reins}
    for f in range(252, 442):
        scene.frame_set(f)
        bpy.context.view_layer.update()
        for ob in reins:
            paths[ob.name].append([list(ob.matrix_world@Vector(p.co[:3])) for p in ob.data.splines[0].points])
    scene.frame_set(frame)
    bpy.context.view_layer.update()
    report = dict(changed=False, source_preserved=True,
                  metrics={name:trajectory_metrics(rows) for name,rows in paths.items()},
                  scope='Exact retained native trajectory; endpoint-relative residual steps are diagnostic flags, not audiovisual acceptance.')
    (out/'rein361-audit.json').write_text(json.dumps(report, indent=2)+'\n')
    (out/'rein361-paths.json').write_text(json.dumps(paths)+'\n')
    return report


def advect(points, head_delta, hand_delta):
    """Carry one material path with its actual head/hand owners."""
    total=sum((b-a).length for a,b in zip(points,points[1:]))
    distance=0.;out=[]
    for i,p in enumerate(points):
        if i:distance+=(p-points[i-1]).length
        u=distance/total
        out.append(p+(head_delta@p-p)*(1-u)+hand_delta*u)
    return out


def relax(points,bvh,visible):
    """Small continuous unilateral contact corrections, endpoints pinned.

    No independent shortest route or nearest opposite-side reset. Starting
    from the previous certified path retains its side-of-neck relationship.
    Every final segment must still receive the conservative clearance test.
    """
    p=[v.copy() for v in points]
    for iteration in range(24):
        q=[v.copy() for v in p]
        for j in range(1,len(p)-1):
            v=p[j]*.70+(p[j-1]+p[j+1])*.15
            hit,n,_,_=bvh.find_nearest(v)
            signed=(v-hit).dot(n)
            if signed<.015:v+=n*(.015-signed)
            q[j]=v
        p=q
        if iteration>=3 and all(visible(bvh,a,b,.0065) for a,b in zip(p,p[1:])):
            return p,iteration+1
    raise ValueError('REIN361_LOCAL_CONTACT_NOT_CERTIFIED')


def protected_signature(bpy,excluded):
    rows=[]
    for action in bpy.data.actions:
        if action.name in excluded:continue
        curves=[]
        if hasattr(action,'fcurves'):
            try:curves=list(action.fcurves)
            except RuntimeError:pass
        if not curves:
            for layer in action.layers:
                for strip in layer.strips:
                    for bag in getattr(strip,'channelbags',[]):curves.extend(bag.fcurves)
        rows.append((action.name,[(fc.data_path,fc.array_index,[(tuple(k.co),k.interpolation) for k in fc.keyframe_points]) for fc in curves]))
    return hashlib.sha256(json.dumps(rows,sort_keys=True).encode()).hexdigest()


def run(bpy,out):
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    spec=importlib.util.spec_from_file_location('rein358',Path(__file__).with_name('nihang_rein358.py'))
    helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper)
    rig=bpy.data.objects['horse.rig'];scene=bpy.context.scene
    if not rig.get('rein358') or rig.get('rein361'):raise ValueError('REIN361_PARENT')
    reins=sorted([o for o in bpy.data.objects if o.name.startswith('leader supported rein292')],key=lambda o:o.name)
    if len(reins)!=2 or any(len(o.data.splines[0].points)!=129 for o in reins):raise ValueError('REIN361_PAIR')
    excluded={o.data.animation_data.action.name for o in reins}
    signature=protected_signature(bpy,excluded)
    original_frame=scene.frame_current
    original={};head={}
    for frame in range(252,442):
        scene.frame_set(frame);bpy.context.view_layer.update()
        original[frame]=[[ob.matrix_world@Vector(p.co[:3]) for p in ob.data.splines[0].points] for ob in reins]
        head[frame]=rig.matrix_world@rig.pose.bones['DEF-head'].matrix
    captured={};records=[]
    for frame in range(252,442):
        scene.frame_set(frame);bpy.context.view_layer.update()
        ev=bpy.data.objects['horse'].evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=ev.to_mesh()
        tree=BVHTree.FromPolygons([ev.matrix_world@v.co for v in mesh.vertices],[list(p.vertices) for p in mesh.polygons]);ev.to_mesh_clear()
        captured[frame]=[]
        for side,ob in enumerate(reins):
            source=original[frame][side]
            if frame==252:path=[p.copy() for p in source];iterations=0;correction=0.
            else:
                previous=captured[frame-1][side]
                proposed=advect(previous,head[frame]@head[frame-1].inverted(),source[-1]-previous[-1])
                proposed[0]=source[0].copy();proposed[-1]=source[-1].copy()
                path,iterations=relax(proposed,tree,helper.visible)
                correction=max((a-b).length for a,b in zip(path,proposed))
                # A construction guard, not a universal motion-quality score.
                if correction>.04:raise ValueError('REIN361_CONTACT_JUMP:'+str((frame,side,correction)))
            if not all(helper.visible(tree,a,b,.0065) for a,b in zip(path,path[1:])):raise ValueError('REIN361_FINAL_CLEARANCE:'+str((frame,side)))
            if (path[0]-source[0]).length>1e-7 or (path[-1]-source[-1]).length>1e-7:raise ValueError('REIN361_CONTACT_DRIFT')
            captured[frame].append(path)
            records.append(dict(frame=frame,object=ob.name,iterations=iterations,maximum_local_correction=correction,length=sum((a-b).length for a,b in zip(path,path[1:]))))
        if frame%10==2:print('REIN361 certified through',frame,flush=True)
    for ob in reins:
        ob.data.animation_data.action.use_fake_user=True
        ob.data.animation_data_clear()
    for frame,rows in captured.items():
        scene.frame_set(frame);bpy.context.view_layer.update()
        for ob,path in zip(reins,rows):
            inv=ob.matrix_world.inverted()
            for point,v in zip(ob.data.splines[0].points,path):
                point.co=(*(inv@v),1);point.keyframe_insert('co',frame=frame)
    for ob in reins:
        action=ob.data.animation_data.action;excluded.add(action.name)
        curves=[]
        for layer in action.layers:
            for strip in layer.strips:
                for bag in getattr(strip,'channelbags',[]):curves.extend(bag.fcurves)
        if not curves and hasattr(action,'fcurves'):curves=list(action.fcurves)
        for curve in curves:
            for key in curve.keyframe_points:key.interpolation='LINEAR'
    error=0.
    for frame,rows in captured.items():
        scene.frame_set(frame);bpy.context.view_layer.update()
        for ob,path in zip(reins,rows):
            error=max(error,max((ob.matrix_world@Vector(p.co[:3])-v).length for p,v in zip(ob.data.splines[0].points,path)))
    if error>1e-4:raise ValueError('REIN361_READBACK')
    if protected_signature(bpy,excluded)!=signature:raise ValueError('REIN361_ACTION_DRIFT')
    rig['rein361']=1;scene.frame_set(original_frame);bpy.context.view_layer.update()
    metrics={ob.name:trajectory_metrics([[list(p) for p in captured[f][i]] for f in range(252,442)]) for i,ob in enumerate(reins)}
    report=dict(changed=True,source_preserved=True,protected_actions_unchanged=True,protected_action_signature=signature,
                maximum_readback_error=error,certified_segment_clearance=.0065,records=records,metrics=metrics,
                scope='Chronological head/hand-owned path with small certified skin corrections. Not a rope simulation, physical material-length proof or audiovisual acceptance.')
    (out/'rein361.json').write_text(json.dumps(report,indent=2)+'\n')
    return report
