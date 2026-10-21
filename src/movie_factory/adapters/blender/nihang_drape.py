"""Bounded local drape proof. No arbitrary code, provider or master mutation."""
import numpy as np


def torso_weight(points, leader):
    p=np.asarray(points)
    if p.ndim!=2 or p.shape[1]!=3 or not np.isfinite(p).all():
        raise ValueError('DRAPE_INVALID_POINTS')
    bottom=.055 if leader else .885
    u=np.clip((p[:,2]-bottom)/.40,0,1)
    edge=np.minimum(np.clip(u/.16,0,1),np.clip((1-u)/.20,0,1))
    return edge*np.clip((.23-np.abs(p[:,0]))/.075,0,1)


def checked_delta(start, end, weight):
    delta=(np.asarray(end)-np.asarray(start))*np.asarray(weight)[:,None]
    if not np.isfinite(delta).all() or np.max(np.linalg.norm(delta,axis=1))>.09:
        raise ValueError('DRAPE_UNSUPPORTED_DISPLACEMENT')
    return delta


def settle(bpy, shirt, leader):
    """Static posed drape; all animation qualification remains downstream."""
    original=bpy.context.window.scene
    dg=bpy.context.evaluated_depsgraph_get()
    evaluated=shirt.evaluated_get(dg)
    source=np.asarray([v.co[:] for v in evaluated.data.vertices],dtype=np.float64)
    if len(source)!=len(shirt.data.vertices):raise ValueError('DRAPE_TOPOLOGY_CHANGED')
    weight=torso_weight(source,leader)
    eased=source.copy();eased[:,0]*=1+.10*weight;eased[:,1]*=1+.16*weight
    collision=source.copy();collision[:,0]*=.95;collision[:,1]*=.92
    faces=[tuple(p.vertices) for p in evaluated.data.polygons]
    temp=bpy.data.scenes.new('MF isolated static cloth proof')
    objects=[];meshes=[]
    try:
        bpy.context.window.scene=temp
        temp.render.fps=24;temp.gravity=(0,0,-9.81)
        def obj(name,points):
            data=bpy.data.meshes.new(name);meshes.append(data)
            data.from_pydata(points,[],faces);data.update()
            ob=bpy.data.objects.new(name,data);objects.append(ob);temp.collection.objects.link(ob)
            return ob
        proxy=obj('MF temporary drape collision',collision)
        proxy.modifiers.new('Local cloth collision','COLLISION')
        proxy.collision.thickness_outer=.003
        cloth=obj('MF temporary eased cloth',eased)
        pin=cloth.vertex_groups.new(name='Supported seams')
        for i,w in enumerate(weight):pin.add([i],float(1-w),'REPLACE')
        mod=cloth.modifiers.new('Gravity drape proof','CLOTH')
        settings=mod.settings
        settings.quality=8;settings.mass=.25
        settings.tension_stiffness=15;settings.compression_stiffness=10
        settings.shear_stiffness=8;settings.bending_stiffness=.20
        settings.vertex_group_mass=pin.name;settings.pin_stiffness=1
        mod.collision_settings.use_collision=True
        mod.collision_settings.use_self_collision=False
        mod.collision_settings.distance_min=.004
        mod.point_cache.frame_start=1;mod.point_cache.frame_end=48
        for f in range(1,49):
            temp.frame_set(f);bpy.context.view_layer.update()
            current=cloth.evaluated_get(bpy.context.evaluated_depsgraph_get())
            if f==48:final=np.asarray([v.co[:] for v in current.data.vertices])
        delta=checked_delta(source,final,weight)
    finally:
        bpy.context.window.scene=original
        for ob in objects:bpy.data.objects.remove(ob,do_unlink=True)
        bpy.data.scenes.remove(temp)
        for data in meshes:
            if data.users==0:bpy.data.meshes.remove(data)
    blocks=([key.data for key in shirt.data.shape_keys.key_blocks]
            if shirt.data.shape_keys else [shirt.data.vertices])
    for block in blocks:
        coords=np.empty(len(block)*3,dtype=np.float32);block.foreach_get('co',coords)
        result=coords.reshape(-1,3)+delta
        if not np.isfinite(result).all():raise ValueError('DRAPE_NONFINITE_CACHE')
        block.foreach_set('co',result.ravel())
    return {'method':'isolated built-in cloth gravity/collision drape','frames':48,
            'maximum_displacement':float(np.max(np.linalg.norm(delta,axis=1))),
            'cached_poses':len(blocks),'qualification':'Static prototype; animated transfer NOT qualified'}
