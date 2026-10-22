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
        raise ValueError('DRAPE_UNSUPPORTED_DISPLACEMENT:'+str(float(np.max(np.linalg.norm(delta,axis=1)))))
    return delta


def settle(bpy, shirt, leader):
    """Static posed drape; all animation qualification remains downstream."""
    original=bpy.context.window.scene
    dg=bpy.context.evaluated_depsgraph_get()
    evaluated=shirt.evaluated_get(dg)
    source=np.asarray([v.co[:] for v in evaluated.data.vertices],dtype=np.float64)
    if len(source)!=len(shirt.data.vertices):raise ValueError('DRAPE_TOPOLOGY_CHANGED')
    weight=torso_weight(source,leader)
    collision=source.copy();collision[:,0]*=.96;collision[:,1]*=.90
    faces=[tuple(p.vertices) for p in evaluated.data.polygons]
    # Uniform open cloth panels avoid simulating the donor's irregular anatomical
    # triangulation, intersecting arm topology and mixed tiny/long edges.
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    tree=BVHTree.FromPolygons([Vector(p) for p in source],faces)
    rows=35;cols=35;bottom=.105 if leader else .935
    zmax=bottom+.29
    # A rectangular patch assumed support at the narrow waist corners and failed.
    # Measure a common supported domain from this evaluated posed torso instead.
    widths=[]
    for z in np.linspace(bottom,zmax,rows):
        for side in (-1,1):
            for sign in (-1,1):
                last=0
                for radius in np.linspace(0,.18,37):
                    hit=tree.ray_cast(Vector((sign*radius,side*.8,float(z))),Vector((0,-side,0)))[0]
                    if hit is None:break
                    last=radius
                widths.append(last)
    xmax=float(min(widths))*.9
    if xmax<.06:raise ValueError('DRAPE_CENTRAL_SUPPORT_TOO_NARROW:'+str(xmax))
    panel=[];weights=[];panel_faces=[]
    for side in (-1,1):
        offset=len(panel)
        for j in range(rows):
            v=j/(rows-1);z=bottom+(zmax-bottom)*v
            for k in range(cols):
                u=k/(cols-1);x=-xmax+2*xmax*u
                hit=tree.ray_cast(Vector((x,side*.8,z)),Vector((0,-side,0)))[0]
                if hit is None:raise ValueError('DRAPE_PANEL_SUPPORT_MISSING:'+str((side,x,z)))
                interior=np.sin(np.pi*u)*np.sin(np.pi*v)
                panel.append((x,hit.y+side*(.004+.014*interior),z))
                weights.append(min(1,u/.08,(1-u)/.08,v/.08,(1-v)/.10))
        for j in range(rows-1):
            for k in range(cols-1):
                a=offset+j*cols+k
                panel_faces.append((a,a+1,a+cols+1,a+cols))
    panel=np.asarray(panel);weights=np.asarray(weights)
    temp=bpy.data.scenes.new('MF isolated static cloth proof')
    objects=[];meshes=[]
    try:
        bpy.context.window.scene=temp
        temp.render.fps=24;temp.gravity=(0,0,-9.81)
        def obj(name,points,polygons):
            data=bpy.data.meshes.new(name);meshes.append(data)
            data.from_pydata(points,[],polygons);data.update()
            ob=bpy.data.objects.new(name,data);objects.append(ob);temp.collection.objects.link(ob)
            return ob
        proxy=obj('MF temporary drape collision',collision,faces)
        proxy.modifiers.new('Local cloth collision','COLLISION')
        proxy.collision.thickness_outer=.003
        cloth=obj('MF temporary eased cloth panels',panel,panel_faces)
        pin=cloth.vertex_groups.new(name='Supported seams')
        for i,w in enumerate(weights):pin.add([i],float(1-w),'REPLACE')
        mod=cloth.modifiers.new('Gravity drape proof','CLOTH')
        settings=mod.settings
        settings.quality=8;settings.mass=.25
        settings.tension_stiffness=30;settings.compression_stiffness=30
        settings.shear_stiffness=15;settings.bending_stiffness=.35
        settings.vertex_group_mass=pin.name;settings.pin_stiffness=1
        mod.collision_settings.use_collision=True
        mod.collision_settings.use_self_collision=False
        mod.collision_settings.distance_min=.004
        mod.point_cache.frame_start=1;mod.point_cache.frame_end=48
        for f in range(1,49):
            temp.frame_set(f);bpy.context.view_layer.update()
            current=cloth.evaluated_get(bpy.context.evaluated_depsgraph_get())
            if f==48:final=np.asarray([v.co[:] for v in current.data.vertices])
        checked_delta(panel,final,weights)
        # Interpolate panel movement onto existing central torso, keeping the
        # original garment topology, boundaries and animation cache ownership.
        delta=np.zeros_like(source)
        for i,p in enumerate(source):
            x,y,z=p
            if weight[i]<=0 or abs(x)>=xmax or not bottom<z<zmax:continue
            side=0 if y<0 else 1
            u=(x+xmax)/(2*xmax)*(cols-1);v=(z-bottom)/(zmax-bottom)*(rows-1)
            k=min(cols-2,int(u));j=min(rows-2,int(v));fu=u-k;fv=v-j
            ids=[side*rows*cols+j*cols+k,side*rows*cols+j*cols+k+1,
                 side*rows*cols+(j+1)*cols+k,side*rows*cols+(j+1)*cols+k+1]
            blend=np.array([(1-fu)*(1-fv),fu*(1-fv),(1-fu)*fv,fu*fv])
            target=(final[ids]*blend[:,None]).sum(axis=0)
            # Only cloth depth is transferred; neither shoulder height nor
            # anatomy/arm positions are moved by this static panel experiment.
            fade=min(1,(xmax-abs(x))/.035,(z-bottom)/.04,(zmax-z)/.05)
            delta[i,1]=(target[1]-y)*weight[i]*fade
        checked_delta(source,source+delta,np.ones(len(source)))
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
    return {'method':'isolated regular cloth panels, collision-supported depth transfer','frames':48,
            'panel_vertices':len(panel),
            'supported_half_width':xmax,
            'maximum_displacement':float(np.max(np.linalg.norm(delta,axis=1))),
            'cached_poses':len(blocks),'qualification':'Static prototype; animated transfer NOT qualified'}
