"""Reviewed native sheathed prop; fixed geometry and deterministic suspension.

Reference-space coordinates are the measured rider-rig space at opening277.
Negative X is anatomical right; positive Y is rearward. No generated payload.
"""
import math
import numpy as np

MOUTH=np.array([-2.20,.05,-6.85])

def centerline(t):
    t=np.asarray(t,dtype=float)
    return np.stack((-2.20-.90*(1-np.exp(-5*t)), .05+1.65*t+2.55*t*t,
                     -6.85-5.20*t+.75*t*t),axis=-1)

def sheath_mesh(t0=0.,t1=1.,inflate=0.,rings=65):
    ts=np.linspace(t0,t1,rings);p=centerline(ts)
    tangent=np.gradient(p,axis=0);side=np.cross(np.tile([1.,0.,0.],(rings,1)),tangent)
    side/=np.linalg.norm(side,axis=1)[:,None]
    verts=[]
    for i,t in enumerate(ts):
        w=(.235*(1-.52*t)+inflate)*max(.12,min(1,(1.022-t)/.045))
        for j in range(12):
            a=2*math.pi*j/12
            verts.append(p[i]+[math.cos(a)*(.075+inflate),0,0]+side[i]*math.sin(a)*w)
    faces=[]
    for i in range(rings-1):
        for j in range(12):faces.append((i*12+j,i*12+(j+1)%12,(i+1)*12+(j+1)%12,(i+1)*12+j))
    faces.extend([tuple(reversed(range(12))),tuple(range((rings-1)*12,rings*12))])
    return np.asarray(verts),faces

def material(name,colors,metallic,roughness):
    import bpy
    m=bpy.data.materials.new(name);m.use_nodes=True;n=m.node_tree.nodes;l=m.node_tree.links
    p=n.get('Principled BSDF');p.inputs['Metallic'].default_value=metallic;p.inputs['Roughness'].default_value=roughness
    tex=n.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=19;tex.inputs['Detail'].default_value=2
    ramp=n.new('ShaderNodeValToRGB')
    for e,c in zip(ramp.color_ramp.elements,colors):e.color=(*c,1)
    l.new(tex.outputs['Fac'],ramp.inputs['Fac']);l.new(ramp.outputs['Color'],p.inputs['Base Color'])
    bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.14;bump.inputs['Distance'].default_value=.009
    l.new(tex.outputs['Fac'],bump.inputs['Height']);l.new(bump.outputs['Normal'],p.inputs['Normal'])
    return m

def mesh(name,verts,faces,mat,parent=None):
    import bpy
    m=bpy.data.meshes.new(name);m.from_pydata(verts,[],faces);m.update();o=bpy.data.objects.new(name,m)
    bpy.context.scene.collection.objects.link(o);o.parent=parent;o.data.materials.append(mat)
    for f in m.polygons:f.use_smooth=True
    return o

def tube(name,points,radius,mat,parent):
    import bpy
    c=bpy.data.curves.new(name,'CURVE');c.dimensions='3D';c.bevel_depth=radius;c.bevel_resolution=3;c.resolution_u=12
    s=c.splines.new('POLY');s.points.add(len(points)-1)
    for p,v in zip(s.points,points):p.co=(*v,1)
    o=bpy.data.objects.new(name,c);bpy.context.scene.collection.objects.link(o);o.parent=parent;c.materials.append(mat);return o

def construct():
    import bpy
    from mathutils import Vector
    root=bpy.data.objects.new('MF209_palwar_suspension',None);bpy.context.scene.collection.objects.link(root)
    leather=material('MF209_worn_umber_leather',[(.035,.014,.009),(.105,.052,.027)],0,.6)
    steel=material('MF209_patinated_iron',[(.07,.075,.077),(.23,.22,.18)],.72,.43)
    brass=material('MF209_old_brass',[(.12,.07,.025),(.36,.23,.09)],.65,.45)
    sheath=mesh('MF209_curved_scabbard',*sheath_mesh(),leather,root)
    for name,a,b in [('throat',0,.08),('upper_band',.14,.19),('lower_band',.31,.355),('chape',.83,1.)]:
        mesh('MF209_'+name,*sheath_mesh(a,b,.017,12),steel,root)
    tangent=centerline(.003)-centerline(0);tangent/=np.linalg.norm(tangent)
    # Grip follows the mouth direction, not a separate floating visual hilt.
    grip=[MOUTH-tangent*t for t in np.linspace(.04,1.05,25)]
    tube('MF209_grip',grip,.115,steel,root)
    side=np.cross([1.,0.,0.],tangent);side/=np.linalg.norm(side)
    guard=[]
    for x in np.linspace(-1,1,29):guard.append(MOUTH+side*x*.46+tangent*(.03+.23*abs(x)**3))
    tube('MF209_downturned_quillons',guard,.07,steel,root)
    top=MOUTH-tangent*1.05
    verts=[];faces=[]
    for level,rad in [(0,.16),(.07,.29),(.16,.30),(.19,.25)]:
        for j in range(32):
            a=2*math.pi*j/32;verts.append(top-tangent*level+np.array([1,0,0])*math.cos(a)*rad+side*math.sin(a)*rad)
    for k in range(3):
        for j in range(32):faces.append((k*32+j,k*32+(j+1)%32,(k+1)*32+(j+1)%32,(k+1)*32+j))
    faces.append(tuple(range(96,128)));mesh('MF209_cup_pommel',verts,faces,steel,root)
    for t in (.09,.32,.82):
        mesh('MF209_fine_mount_trim',*sheath_mesh(t,t+.009,.024,3),brass,root)
    # Two load-bearing leather hangers, updated against evaluated belt anchors.
    straps=[];rings=[]
    box=[(-.5,-.5,0),(.5,-.5,0),(.5,.5,0),(-.5,.5,0),(-.5,-.5,1),(.5,-.5,1),(.5,.5,1),(-.5,.5,1)]
    faces=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
    for i,t in enumerate((.07,.30)):
        p=centerline(t)+np.array([-.085,0,.07]);rings.append(p)
        circle=[p+np.array([0,math.cos(a)*.115,math.sin(a)*.115]) for a in np.linspace(0,2*math.pi,33)]
        tube('MF209_suspension_ring_'+str(i),circle,.032,steel,root)
        straps.append(mesh('MF209_belt_hanger_'+str(i),box,faces,leather))
    return root,sheath,straps,rings

def animate(scene,root,straps,rings,kind):
    import bpy
    from mathutils import Matrix,Vector
    from wardrobe_motion178_controls import render_geometry_paused
    from worker import action_channels
    rig=bpy.data.objects['MF_body156_fit_rig'];belt=bpy.data.objects['MF_173_waist_belt']
    from wardrobe_motion178 import BASE
    ref=np.load(BASE/'entrance209-inspect02/geometry.npz');pose0=Matrix(ref['pelvis'].tolist())
    bp=ref['MF_173_waist_belt_verts']
    targets=np.array([[-1.36,-.78,-6.19],[-1.31,-.08,-5.98]])
    ids=[int(np.argmin(np.linalg.norm(bp-t,axis=1))) for t in targets]
    frames=range(217,361) if kind=='opening' else range(361,649)
    rows=[]
    with render_geometry_paused():
        belt.hide_viewport=False
        for f in frames:
            scene.frame_set(f);bpy.context.view_layer.update()
            phase=2*math.pi*1.7*(f-217)/24
            lag=.022*math.sin(phase-.8)+.008*math.sin(phase*.51)
            wobble=Matrix.Translation(Vector(MOUTH))@Matrix.Rotation(lag,4,'X')@Matrix.Translation(-Vector(MOUTH))
            W=rig.matrix_world@rig.pose.bones['pelvis'].matrix@pose0.inverted()@wobble
            root.matrix_world=W;root.rotation_mode='QUATERNION'
            # Changing rotation mode after assignment can reinterpret Euler state.
            loc,rot,scale=W.decompose();root.location=loc;root.rotation_quaternion=rot;root.scale=scale
            for prop in ('location','rotation_quaternion','scale'):root.keyframe_insert(prop,frame=f)
            ev=belt.evaluated_get(bpy.context.evaluated_depsgraph_get());m=ev.to_mesh()
            anchors=[ev.matrix_world@m.vertices[i].co for i in ids];ev.to_mesh_clear()
            ends=[]
            for i,strap in enumerate(straps):
                end=W@Vector(rings[i]);start=anchors[i];delta=end-start
                strap.location=start;strap.rotation_mode='QUATERNION';strap.rotation_quaternion=delta.to_track_quat('Z','Y')
                strap.scale=(.17*rig.matrix_world.to_scale().x,.035*rig.matrix_world.to_scale().x,delta.length)
                for prop in ('location','rotation_quaternion','scale'):strap.keyframe_insert(prop,frame=f)
                ends.append([list(start),list(end)])
            rows.append({'frame':f,'root':np.array(W).tolist(),'supports':ends,'camera':np.array(scene.camera.matrix_world).tolist(),'lens':scene.camera.data.lens})
            if f%48==0:print('209 suspension',f,flush=True)
    for ob in [root]+straps:
        for fc in action_channels(ob.animation_data.action):
            for k in fc.keyframe_points:k.interpolation='LINEAR'
    return {'side':'anatomical_right','rig_right_axis':'negative_X','rear_axis':'positive_Y','belt_vertex_ids':ids,'frames':rows,'motion':'deterministic authored bounded lag; not free-body simulation'}
