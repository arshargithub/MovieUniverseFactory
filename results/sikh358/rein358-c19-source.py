"""Consume anatomical bit-ring anchors in existing real hand-owned reins."""
import json,math,importlib.util,hashlib
from pathlib import Path

def influence(u):
    t=max(0.,min(1.,u/.75))
    return 1-t*t*(3-2*t)

def seed_weights(u):
    """Zero end displacement; outward route biased toward the horse, not hand."""
    return math.sin(math.pi*u)*(1-u), math.sin(math.pi*u)

def exterior_path(points, bvh, margin=.018):
    """Tension-relaxed route against the actual evaluated skin, endpoints pinned.

    This is shot-authored contact, not a rope simulation. Dense final sampling
    below explicitly rejects any remaining segment penetration.
    """
    p=[v.copy() for v in points]
    for _ in range(90):
        q=[v.copy() for v in p]
        for j in range(1,len(p)-1):
            v=p[j]*.55+(p[j-1]+p[j+1])*.225
            hit,n,_,dist=bvh.find_nearest(v)
            if hit is not None:
                signed=(v-hit).dot(n)
                if signed<margin:v=hit+n*margin
            q[j]=v
        p=q
    return p

def run(bpy,out):
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    spec=importlib.util.spec_from_file_location('tack354',Path(__file__).with_name('nihang_tack354.py'));h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
    rig=bpy.data.objects['horse.rig'];scene=bpy.context.scene
    if not rig.get('tack358') or rig.get('rein358'):raise ValueError('REIN358_PARENT')
    anchors=json.loads(rig['tack358_anchors']);reins=sorted([o for o in bpy.data.objects if o.name.startswith('leader supported rein292')],key=lambda o:o.name)
    if len(reins)!=2:raise ValueError('REIN358_PAIR')
    # Preserve every existing non-rein action byte. Temporarily remove the two
    # action datablocks only from the signature selection, never from the scene.
    excluded={o.data.animation_data.action.name for o in reins if o.data.animation_data and o.data.animation_data.action}
    def protected_signature():
        rows=[]
        for a in bpy.data.actions:
            if a.name in excluded:continue
            curves=[]
            if hasattr(a,'fcurves'):
                try:curves=list(a.fcurves)
                except RuntimeError:pass
            if not curves:
                for layer in a.layers:
                    for strip in layer.strips:
                        for bag in getattr(strip,'channelbags',[]):curves.extend(bag.fcurves)
            rows.append((a.name,[(fc.data_path,fc.array_index,[(tuple(k.co),k.interpolation) for k in fc.keyframe_points]) for fc in curves]))
        return hashlib.sha256(json.dumps(rows,sort_keys=True).encode()).hexdigest()
    sig=protected_signature();captured={};frame=scene.frame_current
    invrest=rig.data.bones['DEF-head'].matrix_local.inverted()
    for f in range(252,442):
        scene.frame_set(f);bpy.context.view_layer.update()
        captured[f]=[]
        horse=bpy.data.objects['horse'];evaluated=horse.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=evaluated.to_mesh()
        verts=[evaluated.matrix_world@v.co for v in mesh.vertices]
        bvh=BVHTree.FromPolygons(verts,[list(p.vertices) for p in mesh.polygons])
        evaluated.to_mesh_clear()
        for label,obj in zip(('R','L'),reins):
            # Ring's rear rim is the actual leather attachment station.
            anchor=Vector(anchors[label])+Vector((0,.021,0))
            target=rig.matrix_world@rig.pose.bones['DEF-head'].matrix@invrest@anchor
            original=[obj.matrix_world@Vector(p.co[:3]) for p in obj.data.splines[0].points]
            side=-1 if label=='R' else 1
            lateral=(rig.matrix_world@rig.pose.bones['DEF-head'].matrix).to_3x3()@Vector((1,0,0));lateral.normalize()
            hand=original[-1];seed=[]
            for j in range(65):
                u=j/64;side_w,up_w=seed_weights(u)
                seed.append(target.lerp(hand,u)+lateral*(side*.30*side_w)+Vector((0,0,.035*up_w)))
            path=exterior_path(seed,bvh)
            clearance=[]
            for a,b in zip(path,path[1:]):
                for t in (0,.25,.5,.75):
                    v=a.lerp(b,t);hit,n,_,dist=bvh.find_nearest(v);clearance.append((v-hit).dot(n))
            if min(clearance)<.004:raise ValueError('REIN358_SKIN_PENETRATION:'+str((f,label,min(clearance))))
            captured[f].append((target,original,obj.matrix_world.copy(),path,min(clearance)))
    # Retain failed/previous action datablocks as evidence; new curve data action
    # owns the denser route. No unrelated horse or rider keys are touched.
    for obj in reins:
        if obj.data.animation_data and obj.data.animation_data.action:obj.data.animation_data.action.use_fake_user=True
        obj.data.animation_data_clear();obj.data.splines.clear();s=obj.data.splines.new('POLY');s.points.add(64)
        obj.data.bevel_depth=.0045
    errors=[];grip_errors=[];records=[]
    for f,rows in captured.items():
        scene.frame_set(f);bpy.context.view_layer.update()
        for obj,(target,original,world,path,clearance) in zip(reins,rows):
            delta=target-original[0];inv=world.inverted();points=obj.data.splines[0].points
            for j,p in enumerate(points):
                v=path[j]
                p.co=(*(inv@v),1);p.keyframe_insert('co',frame=f)
                if j==len(points)-1:grip_errors.append((v-original[-1]).length)
            errors.append((world@Vector(points[0].co[:3])-target).length)
            records.append(dict(frame=f,object=obj.name,bit_world=list(target),displacement=delta.length,hand_world=list(original[-1]),minimum_skin_clearance=clearance,length=sum((a-b).length for a,b in zip(path,path[1:]))))
    leather=bpy.data.materials['358 worn dark umber bridle leather']
    for obj in reins:
        obj.data.materials.clear();obj.data.materials.append(leather)
        a=obj.data.animation_data.action
        excluded.add(a.name)
        curves=[]
        if hasattr(a,'fcurves'):
            try:curves=list(a.fcurves)
            except RuntimeError:pass
        if not curves:
            for layer in a.layers:
                for strip in layer.strips:
                    for bag in getattr(strip,'channelbags',[]):curves.extend(bag.fcurves)
        for fc in curves:
            for k in fc.keyframe_points:
                if 252<=k.co.x<=441:k.interpolation='LINEAR'
    # Read the animation back after switching frames; same-write checks alone
    # cannot establish that the retained action actually evaluates correctly.
    playback_errors=[]
    for f,rows in captured.items():
        scene.frame_set(f);bpy.context.view_layer.update()
        for obj,(_,_,_,expected,_) in zip(reins,rows):
            playback_errors.extend((obj.matrix_world@Vector(p.co[:3])-v).length for p,v in zip(obj.data.splines[0].points,expected))
    if max(playback_errors)>1e-4:raise ValueError('REIN358_ANIMATION_READBACK')
    if protected_signature()!=sig:raise ValueError('REIN358_PROTECTED_ACTION_DRIFT')
    if max(errors)>1e-5 or max(grip_errors)>1e-8:raise ValueError('REIN358_CONTACT')
    rig['rein358']=1;scene.frame_set(frame);bpy.context.view_layer.update()
    report=dict(changed=True,source_preserved=True,protected_action_signature=sig,protected_actions_unchanged=True,maximum_bit_error=max(errors),maximum_grip_change=max(grip_errors),maximum_animation_readback_error=max(playback_errors),minimum_skin_clearance=min(x['minimum_skin_clearance'] for x in records),records=records,scope='Entire exterior span reconstructed against evaluated horse skin; actual hand endpoints preserved. Shot-authored contact, not rope simulation; images and timing still required.')
    (out/'rein358.json').write_text(json.dumps(report,indent=2)+'\n');return report
