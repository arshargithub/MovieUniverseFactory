"""Neutral fitted belt and surface-following rigid buckle for the racing shot.

No accepted body changes. Leather follows the evaluated waist, not a single
pelvis bone while the lumbar area bends above it. Buckle remains rigid.
"""
import json,math
from pathlib import Path
import numpy as np


def band_frame(q,rows=96,cols=5):
    """Front belt frame: tangent X, outward Y, superior Z."""
    grid=np.asarray(q).reshape(rows,cols,3);row=rows//2
    center=grid[row].mean(0);x=grid[row+1,2]-grid[row-1,2];z=grid[row,-1]-grid[row,0]
    if not np.isfinite(grid).all() or min(np.linalg.norm(x),np.linalg.norm(z))<1e-7:raise ValueError('Degenerate belt attachment')
    x/=np.linalg.norm(x);y=np.cross(z,x)
    if np.linalg.norm(y)<1e-7:raise ValueError('Collapsed belt attachment')
    y/=np.linalg.norm(y);z=np.cross(x,y)
    matrix=np.eye(4);matrix[:3,:3]=np.stack([x,y,z],axis=1);matrix[:3,3]=center
    return matrix


def frame_from_band(q):
    from mathutils import Matrix
    return Matrix(band_frame(q))


def inspect(out):
    import bpy
    from wardrobe_motion178 import BASE,digest
    from wardrobe185_gallop import DIAGNOSTIC_SHA
    source=BASE/'wardrobe185-gallopscreen01/diagnostic.blend'
    if digest(source)!=DIAGNOSTIC_SHA:raise ValueError('Unbound buckle inspection')
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False)
    bpy.context.scene.frame_set(1);bpy.context.view_layer.update();record={}
    for name in ('MF_173_belt_buckle','MF_173_buckle_tongue','MF_173_waist_belt'):
        ob=bpy.data.objects[name]
        record[name]={'type':ob.type,'parent':ob.parent.name if ob.parent else None,
            'modifiers':[{'type':m.type,'name':m.name,'target':getattr(getattr(m,'object',None),'name',None)} for m in ob.modifiers],
            'constraints':[{'type':c.type,'target':getattr(getattr(c,'target',None),'name',None),'bone':getattr(c,'subtarget',None)} for c in ob.constraints],
            'delta_location':list(ob.delta_location),'delta_rotation':list(ob.delta_rotation_euler),'delta_scale':list(ob.delta_scale),
            'world_matrix':np.array(ob.matrix_world).tolist()}
    (out/'inspection.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record),flush=True)


def fit(out):
    import bpy
    from mathutils import Vector,Matrix
    from mathutils.bvhtree import BVHTree
    from wardrobe_motion178_controls import render_surface_target,bind_render_surface,render_geometry_paused,smooth
    scene=bpy.context.scene;scene.frame_set(1);bpy.context.view_layer.update()
    belt=bpy.data.objects['MF_173_waist_belt']
    old=np.array([belt.matrix_world@v.co for v in belt.data.vertices])
    z0=float(np.median(old[:,2]));width=float(np.ptp(old[:,2]))
    if not -6<z0<-4 or not .1<width<.8:raise ValueError('Unexpected belt rest dimensions')
    target=render_surface_target();deps=bpy.context.evaluated_depsgraph_get();ev=target.evaluated_get(deps);mesh=ev.to_mesh();mesh.calc_loop_triangles()
    vertices=np.array([target.matrix_world@v.co for v in mesh.vertices]);faces=np.array([t.vertices[:] for t in mesh.loop_triangles]);ev.to_mesh_clear()
    points=vertices[faces];mask=(abs(points[:,:,0]).max(1)<2)&(points[:,:,2].min(1)>z0-1)&(points[:,:,2].max(1)<z0+1)
    tree=BVHTree.FromPolygons(vertices.tolist(),faces[mask].tolist(),all_triangles=True)
    strap_changes={}
    for sign in (-1,1):
        strap=bpy.data.objects['MF_173_tension_harness_'+str(sign)];strap.data=strap.data.copy()
        for mod in list(strap.modifiers):
            if mod.type=='SURFACE_DEFORM':strap.modifiers.remove(mod)
        changed=0;maximum=0.
        for i in range(0,len(strap.data.vertices),2):
            a,b=strap.data.vertices[i:i+2];pa=strap.matrix_world@a.co;pb=strap.matrix_world@b.co;center=(pa+pb)*.5
            weight=smooth((z0+.24-center.z)/.22)
            if not weight:continue
            hit,normal,_,_=tree.find_nearest(center)
            if normal.dot(center-Vector((0,.14,center.z)))<0:normal=-normal
            shift=(hit+normal*.075-center)*weight
            if shift.length>.10:raise ValueError('Harness end needs more than a local under-belt seat')
            inverse=strap.matrix_world.inverted();a.co=inverse@(pa+shift);b.co=inverse@(pb+shift)
            changed+=2;maximum=max(maximum,shift.length)
        strap.data.update();bind_render_surface(strap,target)
        strap_changes[str(sign)]={'vertices':changed,'maximum_native':maximum,'scope':'Coherent end-band translation beneath waist belt'}
    q=[];f=[];rows=96;cols=5;distances=[]
    for row in range(rows):
        theta=math.tau*row/rows;direction=Vector((math.sin(theta),math.cos(theta),0))
        for col in range(cols):
            z=z0+width*(col/(cols-1)-.5);origin=Vector((0,.14,z))+direction*3
            hit,normal,_,_=tree.ray_cast(origin,-direction,4)
            if hit is None:raise ValueError('Missing measured waist surface')
            if normal.dot(direction)<0:normal=-normal
            p=hit+normal*.11;q.append(tuple(p));distances.append((p-hit).length)
    for row in range(rows):
        for col in range(cols-1):f.append((row*cols+col,((row+1)%rows)*cols+col,((row+1)%rows)*cols+col+1,row*cols+col+1))
    mats=list(belt.data.materials)
    for mod in list(belt.modifiers):
        if mod.type in ('SURFACE_DEFORM','ARMATURE'):belt.modifiers.remove(mod)
    data=bpy.data.meshes.new('185 measured waist belt');data.from_pydata(q,[],f);data.update()
    for mat in mats:data.materials.append(mat)
    for poly in data.polygons:poly.use_smooth=True
    attr=data.attributes.new('MF_173_material_coords','FLOAT_VECTOR','POINT')
    for v,item in zip(data.vertices,attr.data):item.vector=v.co
    belt.data=data;belt.matrix_world=Matrix.Identity(4);bind_render_surface(belt,target)
    # Record exact pre-subdivision band positions for rigid buckle tracking.
    flags=[(m,m.show_viewport) for m in belt.modifiers if m.type!='SURFACE_DEFORM']
    for m,_ in flags:m.show_viewport=False
    def evaluated():
        bpy.context.view_layer.update();ev=belt.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh()
        result=np.array([belt.matrix_world@v.co for v in me.vertices]);ev.to_mesh_clear()
        if result.shape!=(rows*cols,3):raise ValueError('Belt correspondence changed')
        return result
    basis=frame_from_band(evaluated());oldfront=old[np.argsort(old[:,1])[:max(2,len(old)//48)]].mean(0)
    shift=basis.translation-Vector(oldfront)
    buckles=[]
    for name in ('MF_173_belt_buckle','MF_173_buckle_tongue'):
        ob=bpy.data.objects[name];world=ob.matrix_world.copy()
        for mod in list(ob.modifiers):
            if mod.type in ('SURFACE_DEFORM','ARMATURE'):ob.modifiers.remove(mod)
        ob.constraints.clear();ob.parent=None;ob.animation_data_clear();world.translation+=shift
        ob.matrix_world=world;ob.rotation_mode='QUATERNION';buckles.append((ob,world.copy()))
    traces=[];rigid_errors=[]
    with render_geometry_paused():
        belt.hide_viewport=False;target.hide_viewport=False
        for ob,_ in buckles:ob.hide_viewport=False
        for frame in range(1,361):
            scene.frame_set(frame);bpy.context.view_layer.update();points=evaluated();transform=frame_from_band(points)@basis.inverted()
            traces.append(np.array(transform))
            for ob,world in buckles:
                ob.matrix_world=transform@world
                for path in ('location','rotation_quaternion','scale'):ob.keyframe_insert(data_path=path,frame=frame)
                bpy.context.view_layer.update();ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh()
                actual=np.array([ev.matrix_world@v.co for v in me.vertices]);expected=np.array([transform@world@v.co for v in ob.data.vertices]);ev.to_mesh_clear()
                if actual.shape!=expected.shape:raise ValueError('Buckle rigid geometry changed')
                error=float(np.max(abs(actual-expected)));rigid_errors.append(error)
                if error>1e-5:raise ValueError('Buckle evaluated twice or detached from target frame')
            if frame%60==0:print('185 fitted waist',frame,flush=True)
    for m,state in flags:m.show_viewport=state
    scene.frame_set(1);bpy.context.view_layer.update()
    np.savez_compressed(out/'buckle-transforms.npz',matrices=np.array(traces))
    return {'rest_center_z':z0,'retained_width_native':width,'clearance_native':distances[0],'harness_ends':strap_changes,'buckle_rigid_error_all_frames':max(rigid_errors),
        'attachment':'Leather surface-deformed with current waist; rigid buckle follows evaluated front-band frame',
        'visual_gate':'NOT_RUN'}


def screen(out):
    import bpy
    from wardrobe_motion178 import BASE,digest,check_protected
    from wardrobe185_gallop import transfer_action,DIAGNOSTIC_SHA
    from wardrobe185_convex import RIDER07_SHA
    from wardrobe_riding_fit import fit_render
    source=BASE/'wardrobe185-gallopscreen01/diagnostic.blend';rider=BASE/'wardrobe185-riding07/rider-rig.blend'
    if digest(source)!=DIAGNOSTIC_SHA or digest(rider)!=RIDER07_SHA:raise ValueError('Belt source changed')
    (out/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False);scene=bpy.context.scene
    with bpy.data.libraries.load(str(rider),link=False) as (_,loaded):loaded.objects=['MF_body156_fit_rig']
    donor=loaded.objects[0];scene.collection.objects.link(donor);transfer_action(donor,bpy.data.objects['MF_body156_fit_rig']);bpy.data.objects.remove(donor,do_unlink=True)
    record=fit(out)
    for ob in scene.objects:
        if ob.name.startswith(('MF185_gait_','MF185_rein_','MF185_stirrup_','MF185_moving_shawl')):ob.hide_render=True
    scene.cycles.device='CPU';scene.cycles.samples=8;scene.render.use_persistent_data=True
    rig=bpy.data.objects['MF_body156_fit_rig']
    for frame in (1,193,217,348):
        scene.frame_set(frame);bpy.context.view_layer.update()
        center=tuple(rig.matrix_world@rig.pose.bones['spine'].head)
        for angle,label in ((0,'front'),(90,'left'),(180,'rear'),(270,'right')):fit_render(out,label+'-'+str(frame),angle,center,5.8,(640,640))
    check_protected();(out/'result.json').write_text(json.dumps(record,indent=2)+'\n')
