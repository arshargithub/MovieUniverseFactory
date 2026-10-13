"""Closed reviewed native timing derivative; immutable input/cache dependencies.

Explicit physical, camera/attention and world-travel clocks. The first prefix
reuses steady gait phases, not pixels. Its seams remain a visual hypothesis.
"""
import json,sys,math
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import wardrobe_motion178 as base
from finish237_clock import clocks
OUT=ROOT/'.runtime/art-direction/series01-finish237'
OPS={'opening01':'opening','route02':'route','opening03':'opening','route04':'route',
     'finish245-opening01':'opening','finish245-route01':'route'}
def validate(job):
    if not isinstance(job,dict) or set(job)!={'operation'} or job['operation'] not in OPS:raise ValueError('Closed237 operation')
def channels(action):
    from worker import action_channels
    return action_channels(action)
def setkeys(fc,frames,values):
    fc.keyframe_points.clear();fc.keyframe_points.add(len(frames))
    fc.keyframe_points.foreach_set('co',np.column_stack((frames,values)).ravel())
    for k in fc.keyframe_points:k.interpolation='LINEAR'
    fc.update()
def frame(scene,t):
    scene.frame_set(int(t),subframe=t-int(t))
def main():
    import bpy
    from mathutils import Vector,Quaternion
    from wardrobe_motion178_controls import render_geometry_paused
    from entrance206_performance import escape_weight
    from entrance189_groom import read_mdd,write_mdd,attach_cache
    from entrance205_actor import save
    job=json.loads(Path(sys.argv[sys.argv.index('--')+1]).read_text());validate(job)
    current245=job['operation'].startswith('finish245-')
    kind=OPS[job['operation']];out=base.BASE/(job['operation'] if current245 else 'finish237-'+job['operation'])
    clock=clocks
    if current245:
        from finish245_clock import clocks as clock
    if out.exists():raise ValueError('Preserve derivative')
    rec=json.loads((OUT/'inspection.json').read_text())[kind];src=ROOT/rec['source']
    if base.digest(src)!=rec['sha']:raise ValueError('Source changed')
    meta=json.loads((src.parent/'result.json').read_text())
    for row in meta['caches']:
        if base.digest((src.parent/row['path']).resolve())!=row['sha256']:raise ValueError('Changed cache')
    bpy.ops.wm.open_mainfile(filepath=str(src),load_ui=False,use_scripts=False);scene=bpy.context.scene;base.check_protected()
    out.mkdir();start=217 if kind=='opening' else (451 if current245 else 415);count=(234 if current245 else 198) if kind=='opening' else 306
    frames=np.arange(start,start+count);times=np.array([clock(kind,i) for i in range(count)])
    rig=bpy.data.objects['MF_body156_fit_rig'];cam=scene.camera
    camrows=[];oldhead=[];oldneck=[];headbasis=[];oldroots=[]
    travel=bpy.data.objects['AS_world_travel' if kind=='opening' else 'MF205_shared_route_actor']
    t0=217 if kind=='opening' else 361
    with render_geometry_paused():
        frame(scene,t0);travel0=np.array(travel.location)
        frame(scene,t0+1);velocity=np.array(travel.location)-travel0
        for physical,editorial,world in times:
            frame(scene,physical);bpy.context.view_layer.update()
            oldhead.append(np.array(rig.matrix_world@rig.pose.bones['MF185_head'].matrix))
            headbasis.append([rig.pose.bones[n].rotation_quaternion.copy() for n in ('MF185_neck','MF185_head')])
            oldroots.append(np.array(travel.location))
            frame(scene,editorial);bpy.context.view_layer.update()
            h=(rig.matrix_world@rig.pose.bones['MF185_head'].matrix).translation
            camrows.append((cam.matrix_world.copy(),cam.data.lens,h.copy()))
    # Hidden mesh transforms are not guaranteed to evaluate during paused
    # geometry. Sample their source channels explicitly before editing them.
    source_locations={}
    for ob in scene.objects:
        if ob.type=='LIGHT' or ob.name.startswith(('MF201_dramatic_dust','MF196_bounded_pebble','MF209_')):
            loc=np.tile(np.array(ob.location),(count,1));ad=ob.animation_data
            if ad and ad.action:
                for fc in channels(ad.action):
                    if fc.data_path=='location':loc[:,fc.array_index]=[fc.evaluate(float(t)) for t in times[:,0]]
            source_locations[ob.name]=loc
    # Only IDs actually owning actions are changed; unreferenced historical
    # actions remain untouched. Face/blink have distinct attention/physical time.
    owners=list(bpy.data.objects)+list(bpy.data.shape_keys)+list(bpy.data.cameras)+list(bpy.data.curves)
    owners += [m.node_tree for m in bpy.data.materials if m.use_nodes]
    action_map={};bake=[]
    for owner in owners:
        ad=getattr(owner,'animation_data',None)
        if not ad or not ad.action:continue
        old=ad.action;key=(old.as_pointer(),owner in bpy.data.shape_keys.values())
        if key not in action_map:
            new=old.copy();new.name='MF237 '+old.name
            for fc in channels(new):
                isface=key[1] and 'eyeBlink' not in fc.data_path
                clock=times[:,1] if isface else times[:,0]
                values=[fc.evaluate(float(t)) for t in clock]
                setkeys(fc,frames,values)
            action_map[key]=new
        ad.action=action_map[key];bake.append(owner.name)
    # Native MDD random access is driven by the physical clock, no cache copy.
    cache_rows=[]
    for ob in scene.objects:
        for m in ob.modifiers:
            if m.type!='MESH_CACHE':continue
            path=Path(bpy.path.abspath(m.filepath)).resolve();offset=m.frame_start
            m.filepath=str(path);m.play_mode='CUSTOM';m.time_mode='FRAME'
            for f,t in zip(frames,times[:,0]):m.eval_frame=float(t-offset);m.keyframe_insert('eval_frame',frame=int(f))
            cache_rows.append(dict(object=ob.name,path=str(path),start=offset))
    # Source travel is linear in the straight prefix; original route movement
    # remains exactly sampled after the eighteen new OTS frames.
    newhead=[];rootdelta=[]
    rein_origins={n:bpy.data.objects[n].location.copy() for n in ('MF185_rein_L','MF185_rein_R')}
    with render_geometry_paused():
        for i,(f,(physical,editorial,world)) in enumerate(zip(frames,times)):
            scene.frame_set(int(f));bpy.context.view_layer.update()
            desired=travel0+velocity*(world-t0) if kind=='opening' or i<18 else oldroots[i]
            delta=desired-oldroots[i];rootdelta.append(delta)
            travel.location=desired;travel.keyframe_insert('location',frame=int(f))
            if kind=='opening':
                # Emitted pebbles were stored relative to scrolling terrain.
                for ob in scene.objects:
                    if ob.parent==travel and ob.name.startswith('MF196_bounded_pebble'):
                        ob.location=Vector(source_locations[ob.name][i]-delta);ob.keyframe_insert('location',frame=int(f))
                for j,(name,deg) in enumerate((('MF185_neck',-7),('MF185_head',-23))):
                    q=headbasis[i][j]@Quaternion((0,1,0),math.radians(deg)*(escape_weight(editorial)-escape_weight(physical)))
                    b=rig.pose.bones[name];b.rotation_quaternion=q;b.keyframe_insert('rotation_quaternion',frame=int(f))
            elif i<18:
                # These world-space companions are not children of route root.
                for name in ('MF209_palwar_suspension','MF209_belt_hanger_0','MF209_belt_hanger_1'):
                    ob=bpy.data.objects[name];ob.location=Vector(source_locations[name][i]+delta);ob.keyframe_insert('location',frame=int(f))
                for ob in scene.objects:
                    if (ob.type=='LIGHT' and ob.data.type!='SUN') or ob.name.startswith(('MF201_dramatic_dust','MF196_bounded_pebble')):
                        ob.location=Vector(source_locations[ob.name][i]+delta);ob.keyframe_insert('location',frame=int(f))
            if kind=='route':
                for name,origin in rein_origins.items():
                    ob=bpy.data.objects[name];ob.location=origin+(Vector(delta) if i<18 else Vector((0,0,0)));ob.keyframe_insert('location',frame=int(f))
            bpy.context.view_layer.update();h=(rig.matrix_world@rig.pose.bones['MF185_head'].matrix)
            newhead.append(np.array(h));mat,lens,priorhead=camrows[i]
            if kind=='opening':mat.translation+=h.translation-priorhead
            elif i<48:
                # Keep screen-space OTS tracking while looking toward the same
                # distant decision geography; this is inspected, not assumed.
                mat.translation+=h.translation-priorhead
            cam.matrix_world=mat;cam.rotation_mode='QUATERNION'
            cam.rotation_quaternion=mat.to_quaternion();cam.location=mat.translation;cam.data.lens=lens
            cam.keyframe_insert('location',frame=int(f));cam.keyframe_insert('rotation_quaternion',frame=int(f));cam.data.keyframe_insert('lens',frame=int(f))
    if kind=='opening':
        shawl=bpy.data.objects['MF185_moving_shawl'];m=next(m for m in shawl.modifiers if m.type=='MESH_CACHE')
        a=read_mdd(bpy.path.abspath(m.filepath));offset=next(x['start'] for x in cache_rows if x['object']==shawl.name)
        def rows():
            for i,t in enumerate(times[:,0]):
                x=t-offset;j=int(x);u=x-j;p=np.asarray(a[j],float)*(1-u)+np.asarray(a[min(j+1,len(a)-1)],float)*u
                inv=np.linalg.inv(oldhead[i]);local=p@inv[:3,:3].T+inv[:3,3]
                w=np.clip((local[:,1]+1.2)/1.8,0,1);w=w*w*(3-2*w);w[2501:]=0
                delta=newhead[i]@inv;q=p@delta[:3,:3].T+delta[:3,3];yield (p+(q-p)*w[:,None]).astype(np.float32)
        path=out/'headfall.mdd';write_mdd(path,count,len(shawl.data.vertices),rows());attach_cache(shawl,path,start)
    scenery=None
    if current245:
        from finish245_checkpoint import build
        # Route camera's last OTS frame must use the source390 pose, never
        # interpolate across the hard cut into the frontal turn391.
        if kind=='route':
            i=47;mat,lens,priorhead=camrows[i]
            # editorial clock is capped390; retain its exact matrix here.
            frame(scene,float(frames[i]));cam.matrix_world=mat
            cam.rotation_quaternion=mat.to_quaternion();cam.location=mat.translation;cam.data.lens=lens
            cam.keyframe_insert('location',frame=int(frames[i]));cam.keyframe_insert('rotation_quaternion',frame=int(frames[i]));cam.data.keyframe_insert('lens',frame=int(frames[i]))
        scene.frame_set(start);bpy.context.view_layer.update();scenery=build(scene,kind)
    scene.frame_start=start;scene.frame_end=int(frames[-1]);scene.render.fps=24;scene.frame_set(start)
    save(scene,out,dict(source_sha256=rec['sha'],clock=times.tolist(),frames=frames.tolist(),baked_owners=bake,
        method='Independent native gait, editorial and travel clocks; fixed original-speed route after prefix',
        scenery=scenery,caveat='Cyclic prefix seam, cache mapping and new travel require visual proof; not a passing result'))
    for ob in scene.objects:
        for m in ob.modifiers:
            if m.type in ('SMOOTH','CORRECTIVE_SMOOTH','SUBSURF'):m.show_viewport=False
    scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=2;scene.render.use_persistent_data=False
    scene.render.resolution_x=216;scene.render.resolution_y=384;scene.render.resolution_percentage=100
    indices=([0,54,137,197] if kind=='opening' else [0,7,17,18,47,48]) if job['operation'] in ('opening03','route04') else ([0,52,53,54,55,72,114,127,137,151,177,197] if kind=='opening' else [0,1,7,8,17,18,19,35,47,48,100,200,305])
    if current245:indices=([0,89,90,96,138,173,233] if kind=='opening' else [0,24,47,48,90,180,250])
    for i in indices:
        scene.frame_set(int(frames[i]));scene.render.filepath=str(out/f'control-{i:03d}.png');bpy.ops.render.render(write_still=True);print('237 CONTROL',kind,i,flush=True)
    base.check_protected()
if __name__=='__main__':main()
