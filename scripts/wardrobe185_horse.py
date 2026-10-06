"""Read-only source-gallop audit for the authorized rider integration.

Keep the complete source graph and its original action/constraints. The old
static fitting mesh is not evidence of temporal horse or tack readiness.
"""
import json
from pathlib import Path
import numpy as np


def gait_cache(out):
    """Sample existing evaluated motion, no source animation reconstruction."""
    import bpy
    from mathutils import Matrix,Vector
    from wardrobe_riding_fit import HORSE,HORSE_SHA
    from wardrobe_motion178 import digest
    from wardrobe_shawl180_cache import cache
    if HORSE.is_symlink() or digest(HORSE)!=HORSE_SHA:raise ValueError('Horse source changed')
    (out/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
    bpy.ops.wm.open_mainfile(filepath=str(HORSE),load_ui=False,use_scripts=False)
    source=bpy.context.scene;source.frame_set(0);bpy.context.view_layer.update()
    names=('horse','saddle','saddle.pad','saddle.stirrup','saddle.stirrup.strap','bridle','bridle.body','bit','Torus.002','Full Bushy Flowing Horse Tail')
    target=bpy.data.scenes.new('185 evaluated horse library');target.render.fps=24
    transform=Matrix.Translation((0,.20,-6.85))@Matrix.Scale(8.3,4)@Matrix.Translation((0,-2.52,-1.57))
    path=source.objects['horse diagnostic path'];origin=path.matrix_world.translation.copy()
    objects={};samples={n:[] for n in names};saddles=[];bits=[];travel=[]
    for frame in range(144):
        source.frame_set(frame);bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get()
        shift=path.matrix_world.translation-origin;registration=transform@Matrix.Translation(-shift)
        saddles.append(np.array(registration@source.objects['saddle'].matrix_world));travel.append(list(transform.to_3x3()@shift))
        for name in names:
            ob=source.objects[name];ev=ob.evaluated_get(deps);mesh=ev.to_mesh()
            coordinates=np.empty(len(mesh.vertices)*3,dtype=np.float32);mesh.vertices.foreach_get('co',coordinates);coordinates=coordinates.reshape(-1,3)
            world=np.array(registration@ev.matrix_world);points=(coordinates@world[:3,:3].T+world[:3,3]).astype(np.float32)
            if frame==0:
                data=bpy.data.meshes.new_from_object(ev,preserve_all_data_layers=True,depsgraph=deps)
                data.vertices.foreach_set('co',points.ravel());data.update()
                copy=bpy.data.objects.new('MF185_gait_'+name,data);target.collection.objects.link(copy);objects[name]=copy
            elif len(points)!=len(objects[name].data.vertices):raise ValueError('Horse/tack topology changed: '+name)
            if not np.isfinite(points).all():raise ValueError('Nonfinite horse cache')
            samples[name].append(points);ev.to_mesh_clear()
            if name=='bit':
                ends=[]
                for sign in (1,-1):
                    side=points[points[:,0]*sign>0]
                    if not len(side):raise ValueError('Bit has no side')
                    outer=side[side[:,0]*sign>=np.quantile(side[:,0]*sign,.8)]
                    ends.append(outer.mean(0))
                bits.append(ends)
        if frame%24==0:print('185 cached source gait',frame,flush=True)
    bpy.context.window.scene=target;checks={}
    for name,ob in objects.items():
        mod=cache(ob,np.array(samples[name]),out/(name.replace(' ','_')+'.mdd'));mod.frame_start=217
    for f in (217,218,220,240,288,360,230):
        target.frame_set(f);bpy.context.view_layer.update();worst=0.
        for name,ob in objects.items():
            ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());m=ev.to_mesh()
            p=np.empty(len(m.vertices)*3,dtype=np.float32);m.vertices.foreach_get('co',p);ev.to_mesh_clear()
            worst=max(worst,float(np.max(abs(p.reshape(-1,3)-samples[name][f-217]))))
        checks[f]=worst
    if max(checks.values())>1e-5:raise ValueError('Horse cache transfer failed')
    bpy.data.libraries.write(str(out/'horse-library.blend'),set(objects.values()),fake_user=True,compress=True)
    np.savez_compressed(out/'contacts.npz',saddle_matrices=np.array(saddles),bit_points=np.array(bits),world_travel=np.array(travel))
    (out/'result.json').write_text(json.dumps({'source_sha256':HORSE_SHA,'source_unchanged':digest(HORSE)==HORSE_SHA,
        'native_sha256':digest(out/'horse-library.blend'),'contacts_sha256':digest(out/'contacts.npz'),'cache_errors_native':checks,
        'reference_frame':'Subtract constant source path translation; retain complete horse/tack articulation',
        'visual_gate':'NOT_RUN','rider_integration':'NOT_RUN'},indent=2)+'\n')


def probe(out):
    import bpy
    from mathutils import Vector
    from wardrobe_riding_fit import HORSE,HORSE_SHA
    from wardrobe_motion178 import digest
    if HORSE.is_symlink() or digest(HORSE)!=HORSE_SHA:raise ValueError('Horse source changed')
    (out/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
    bpy.ops.wm.open_mainfile(filepath=str(HORSE),load_ui=False,use_scripts=False)
    source=bpy.context.scene
    names=('horse','saddle','saddle.pad','saddle.stirrup','saddle.stirrup.strap','bridle','bridle.body','bit','Torus.002','Full Bushy Flowing Horse Tail')
    missing=[n for n in names if n not in source.objects]
    if missing:raise ValueError('Missing source horse assembly: '+str(missing))
    target=bpy.data.scenes.new('185 isolated source horse diagnostic')
    target.render.engine='CYCLES';target.cycles.device='CPU';target.cycles.samples=8;target.cycles.use_denoising=True
    target.render.resolution_x=720;target.render.resolution_y=540;target.render.resolution_percentage=100
    target.world=bpy.data.worlds.new('185 neutral horse world');target.world.use_nodes=True
    target.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.14,.14,.14,1)
    target.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.65
    camera=bpy.data.objects.new('185 source horse camera',bpy.data.cameras.new('185 horse lens'));target.collection.objects.link(camera)
    camera.data.type='ORTHO';camera.data.ortho_scale=4.6;target.camera=camera
    lights=[]
    for i,power in enumerate((500,300)):
        data=bpy.data.lights.new('185 horse softbox '+str(i),'AREA');data.energy=power;data.shape='DISK';data.size=4
        ob=bpy.data.objects.new(data.name,data);target.collection.objects.link(ob);lights.append(ob)
    meshes={};records=[];samples=[];saddles=[];topology=None
    for frame in range(49):
        bpy.context.window.scene=source;source.frame_set(frame);bpy.context.view_layer.update()
        deps=bpy.context.evaluated_depsgraph_get();horse=source.objects['horse'].evaluated_get(deps)
        data=horse.to_mesh();points=np.array([horse.matrix_world@v.co for v in data.vertices]);horse.to_mesh_clear()
        if topology is None:topology=len(points)
        if len(points)!=topology or not np.isfinite(points).all():raise ValueError('Source horse topology or finite coordinates failed')
        samples.append(points);saddles.append(np.array(source.objects['saddle'].matrix_world))
        rig=source.objects['horse.rig']
        records.append({'frame':frame,'bounds':[points.min(0).tolist(),points.max(0).tolist()],
            'torso_matrix':np.array(rig.matrix_world@rig.pose.bones['torso'].matrix).tolist(),
            'head_bones':{b.name:np.array(rig.matrix_world@b.matrix).tolist() for b in rig.pose.bones if b.name in ('head','DEF-head','neck','DEF-neck')}})
        if frame not in (0,3,6,9):continue
        for name in names:
            ob=source.objects[name];ev=ob.evaluated_get(deps)
            if ob.type not in ('MESH','CURVE'):continue
            data=bpy.data.meshes.new_from_object(ev,preserve_all_data_layers=True,depsgraph=deps)
            if name in meshes:
                copy=meshes[name];old=copy.data;copy.data=data;bpy.data.meshes.remove(old)
            else:
                copy=bpy.data.objects.new('185 sample '+name,data);target.collection.objects.link(copy);meshes[name]=copy
            copy.matrix_world=ev.matrix_world.copy()
        bpy.context.window.scene=target;bpy.context.view_layer.update()
        center=Vector((points.min(0)+points.max(0))*.5)
        for light,offset in zip(lights,((3,-4,5),(-3,2,4))):
            light.location=center+Vector(offset);light.rotation_euler=(center-light.location).to_track_quat('-Z','Y').to_euler()
        for label,offset in (('side',(6,0,.35)),('front-quarter',(4,-6,1.5))):
            camera.location=center+Vector(offset);camera.rotation_euler=(center-camera.location).to_track_quat('-Z','Y').to_euler()
            target.render.filepath=str(out/(label+'-%03d.png'%frame));bpy.ops.render.render(write_still=True)
    invalid=[]
    for ob in source.objects:
        animation=ob.animation_data
        if animation:
            invalid.extend({'object':ob.name,'path':f.data_path} for f in animation.drivers if not f.driver.is_valid)
    np.savez_compressed(out/'horse-samples.npz',frames=np.array(samples),saddle_matrices=np.array(saddles))
    (out/'result.json').write_text(json.dumps({'source':str(HORSE),'sha256':HORSE_SHA,'source_unchanged':digest(HORSE)==HORSE_SHA,
        'topology':topology,'poses':records,'invalid_drivers':invalid,'visual_gate':'NOT_RUN','rider_integration':'NOT_RUN'},indent=2)+'\n')
