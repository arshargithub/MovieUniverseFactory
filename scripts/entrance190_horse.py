"""Coarse source-rig turn proof with new ground-relative hoof projection.

Fixed authored path only. This diagnostic deliberately excludes rider, cloth,
effects and final look until actual horse contacts are evidenced.
"""
import json
import math
import numpy as np
from pathlib import Path
import entrance190_route_math as route

def build(out, corrected=False):
    import bpy
    from mathutils import Matrix,Vector
    from worker import action_channels
    from wardrobe_riding_fit import HORSE,HORSE_SHA
    from wardrobe_motion178 import digest
    from source_gallop_math import LEGS,PERIOD
    bpy.ops.wm.open_mainfile(filepath=str(HORSE),load_ui=False,use_scripts=False)
    scene=bpy.context.scene
    rig=bpy.data.objects['horse.rig'];horse=bpy.data.objects['horse'];path=bpy.data.objects['horse diagnostic path']
    names=('horse','saddle','saddle.pad','saddle.stirrup','saddle.stirrup.strap','bridle','bridle.body','bit','Torus.002')
    for o in scene.objects:
        o.hide_render=o.name not in names
        if o.type in ('MESH','CURVE','CURVES'):o.hide_viewport=o.name not in names
    for m in horse.modifiers:
        if m.type in ('PARTICLE_SYSTEM','COLLISION'):m.show_viewport=False;m.show_render=False
    data=route.trajectory();frames=data['time']*24
    # Resample existing whole-control source action and tack using one clock.
    for name in ('horse.rig',)+names:
        o=bpy.data.objects[name]
        if not o.animation_data or not o.animation_data.action:continue
        old=o.animation_data.action;new=old.copy();o.animation_data.action=new
        for a,b in zip(action_channels(old),action_channels(new)):
            vals=[a.evaluate(float(f)) for f in data['source_frame']]
            b.keyframe_points.clear();b.keyframe_points.add(len(frames))
            b.keyframe_points.foreach_set('co',np.column_stack((frames,vals)).ravel())
            for p in b.keyframe_points:p.interpolation='LINEAR'
    path.animation_data_clear();path.rotation_mode='QUATERNION'
    for i,f in enumerate(frames):
        rotation=Matrix.Rotation(float(data['heading'][i]),4,'Z')@Matrix.Rotation(-math.atan(float(data['grade'][i])),4,'X')@Matrix.Rotation(float(data['bank'][i]),4,'Y')
        path.matrix_world=Matrix.Translation(Vector(data['position'][i]))@rotation@Matrix.Translation((0,-2.52,0))
        path.keyframe_insert('location',frame=float(f));path.keyframe_insert('rotation_quaternion',frame=float(f))
    for fc in action_channels(path.animation_data.action):
        for p in fc.keyframe_points:p.interpolation='LINEAR'
    def refresh(f):
        scene.frame_set(int(f),subframe=float(f%1));bpy.context.view_layer.update()
    # Retain material vertex IDs across all samples. Use complete deformed
    # mesh, not foot control height or hoof-centroid-only contact assertions.
    selected=None
    def feet():
        nonlocal selected
        deps=bpy.context.evaluated_depsgraph_get();ev=horse.evaluated_get(deps);mesh=ev.to_mesh()
        try:
            if selected is None:
                groups={horse.vertex_groups[v[1]].index:k for k,v in LEGS.items()};selected={k:[] for k in LEGS}
                for v in mesh.vertices:
                    for g in v.groups:
                        if g.group in groups and g.weight>.5:selected[groups[g.group]].append(v.index)
            matrix=np.array(ev.matrix_world)
            return {k:(np.array([mesh.vertices[j].co[:] for j in ids])@matrix[:3,:3].T+matrix[:3,3]) for k,ids in selected.items()}
        finally:ev.to_mesh_clear()
    def ground(points):
        # Closest centreline station defines a shared unbanked road surface.
        p=np.asarray(points);centres=data['position'][::8]
        d=((p[:,None,:2]-centres[None,:,:2])**2).sum(2);ids=d.argmin(1)
        # Tangent-plane continuation avoids staircase heights between stations.
        idx=ids*8;forward=np.column_stack((np.sin(data['heading'][idx]),-np.cos(data['heading'][idx])))
        return centres[ids,2]+((p[:,:2]-centres[ids,:2])*forward).sum(1)*data['grade'][idx]
    records=[];states={};corrections=[]
    curves=list(action_channels(rig.animation_data.action))
    for i,f in enumerate(frames):
        refresh(float(f))
        if corrected:
            # Gather stride about each leg's neutral fore/aft station; keep
            # actual bone lengths and the original bend/control families.
            for ctrl in [v[0] for v in LEGS.values()]:
                pb=rig.pose.bones[ctrl];mat=pb.matrix.copy();neutral=pb.bone.head_local.y
                mat.translation.y=neutral+(mat.translation.y-neutral)*float(data['stride_ratio'][i]);pb.matrix=mat
            bpy.context.view_layer.update()
        raw=feet();row={'frame':float(f),'legs':{}}
        for leg,(ctrl,group,a,b,td,stroke) in LEGS.items():
            sf=float(data['source_frame'][i]);cycle=math.floor(sf/PERIOD-td)
            local=(sf/PERIOD-td)-cycle;duration=stroke/(12/2.2)
            margin=.10
            if local>duration+margin:cycle+=1;local-=1
            contact=0<=local<=duration
            w=float(route.smooth((local+margin)/margin)*route.smooth((duration+margin-local)/margin))
            pts=raw[leg];clearance=pts[:,2]-ground(pts);low=int(np.argmin(clearance))
            state=states.get(leg)
            if w>0:
                if state is None or state['cycle']!=cycle:
                    state={'cycle':cycle,'pivot':low,'anchor':pts[low].copy()};states[leg]=state
                    state['anchor'][2]=ground(state['anchor'][None,:])[0]+.003
                pivot=state['pivot']
                # Rolling pivot handoff preserves current planar correction.
                planar=state['anchor'][:2]-pts[pivot,:2]
                if clearance[pivot]-clearance[low]>.010:
                    state['pivot']=low;state['anchor']=pts[low].copy();state['anchor'][:2]+=planar
                    state['anchor'][2]=ground(state['anchor'][None,:])[0]+.003
                delta=np.array([planar[0],planar[1],.003-float(clearance.min())])*w
            else:
                states.pop(leg,None);delta=np.array([0.,0.,max(0.,.003-float(clearance.min()))])
            if corrected:
                # The planar capture also changes terrain height on a grade.
                # Never attenuate a below-ground correction in a blend margin.
                predicted=pts+delta
                delta[2]+=max(0.,.003-float((predicted[:,2]-ground(predicted)).min()))
            pb=rig.pose.bones[ctrl];mat=pb.matrix.copy();mat.translation+=rig.matrix_world.inverted().to_3x3()@Vector(delta);pb.matrix=mat
            bpy.context.view_layer.update()
            row['legs'][leg]={'stance':contact,'cycle':cycle,'raw_clearance':float(clearance.min()),'projection':delta.tolist()}
        if corrected:
            # Evaluated IK skin is not an exactly rigid translated hoof.
            # Close the small residual against the same actual mesh surface.
            for iteration in range(3):
                check=feet();changed=False
                for leg,pts in check.items():
                    deficit=.002-float((pts[:,2]-ground(pts)).min())
                    if deficit<=.0002:continue
                    pb=rig.pose.bones[LEGS[leg][0]];mat=pb.matrix.copy()
                    mat.translation+=rig.matrix_world.inverted().to_3x3()@Vector((0,0,deficit));pb.matrix=mat;changed=True
                if not changed:break
                bpy.context.view_layer.update()
        for ctrl in [v[0] for v in LEGS.values()]:corrections.append((float(f),ctrl,tuple(rig.pose.bones[ctrl].location)))
        actual=feet()
        for leg,pts in actual.items():
            clear=pts[:,2]-ground(pts);row['legs'][leg]['clearance']=float(clear.min())
            low=int(clear.argmin());row['legs'][leg]['lowest_point']=pts[low].tolist()
            if leg in states:
                row['legs'][leg]['pivot_point']=pts[states[leg]['pivot']].tolist()
                row['legs'][leg]['pivot_id']=int(states[leg]['pivot'])
                row['legs'][leg]['anchor']=states[leg]['anchor'].tolist()
                row['legs'][leg]['planar_residual']=float(np.linalg.norm(pts[states[leg]['pivot'],:2]-states[leg]['anchor'][:2]))
        records.append(row)
        if i%192==0:print('190 projected route second',i/192,flush=True)
    for ctrl in [v[0] for v in LEGS.values()]:
        rows=[r for r in corrections if r[1]==ctrl]
        for axis in range(3):
            fc=next(c for c in curves if c.data_path==rig.pose.bones[ctrl].path_from_id('location') and c.array_index==axis)
            fc.keyframe_points.clear();fc.keyframe_points.add(len(rows));fc.keyframe_points.foreach_set('co',[v for r in rows for v in (r[0],r[2][axis])])
            for p in fc.keyframe_points:p.interpolation='LINEAR'
    maximum=max(np.linalg.norm(v['projection']) for r in records for v in r['legs'].values())
    penetration=max(0.,-min(v['clearance'] for r in records for v in r['legs'].values()))
    (out/'contact.json').write_text(json.dumps({'source_sha256':HORSE_SHA,'maximum_projection_m':maximum,'maximum_penetration_m':penetration,'samples':records,'visual_gate':'NOT_RUN','scope':'Coarse horse contact diagnostic, no rider or renewed cloth'},indent=2)+'\n')
    np.savez_compressed(out/'route.npz',**data)
    scene.frame_start=0;scene.frame_end=192;scene.render.fps=24
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'horse-route.blend'),check_existing=False)
    if digest(HORSE)!=HORSE_SHA:raise ValueError('Source changed')
