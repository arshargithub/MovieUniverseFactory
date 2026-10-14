"""Reviewed fixed local handlers. Asset text/scripts are never executed."""
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
sys.path.insert(0,str(ROOT/'scripts'))
from movie_factory.sikh257_contract import validate, SOURCES, digest, LAYOUT_CACHE
from movie_factory.sikh257_geometry import cloth_strip,end_translation

def material(name,color):
    import bpy
    m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True
    b=m.node_tree.nodes.get('Principled BSDF');b.inputs['Base Color'].default_value=(*color,1);b.inputs['Roughness'].default_value=.78
    return m

def mesh(name,verts,faces,mat):
    import bpy
    data=bpy.data.meshes.new(name);data.from_pydata(verts,[],faces);data.update()
    ob=bpy.data.objects.new(name,data);bpy.context.scene.collection.objects.link(ob);data.materials.append(mat)
    for p in data.polygons:p.use_smooth=True
    return ob

def sphere(name,loc,scale,mat):
    import bpy
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24,ring_count=16,location=loc)
    ob=bpy.context.object;ob.name=name;ob.scale=scale;ob.data.materials.append(mat)
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    for p in ob.data.polygons:p.use_smooth=True
    return ob

def scene_setup():
    import bpy
    from mathutils import Vector
    bpy.ops.wm.read_factory_settings(use_empty=True)
    s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=16;s.cycles.use_denoising=True
    s.render.resolution_x=640;s.render.resolution_y=640;s.render.resolution_percentage=100;s.render.fps=24
    s.world=bpy.data.worlds.new('neutral proof');s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.12,.15,.2,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.5
    for name,loc,power,size in [('key',(-2,-3,4),400,3),('fill',(3,-1,2),180,3),('rim',(0,2,3),300,2)]:
        d=bpy.data.lights.new(name,'AREA');d.energy=power;d.shape='DISK';d.size=size
        ob=bpy.data.objects.new(name,d);s.collection.objects.link(ob);ob.location=loc;ob.rotation_euler=(Vector((0,0,1.5))-ob.location).to_track_quat('-Z','Y').to_euler()
    d=bpy.data.cameras.new('proof lens');cam=bpy.data.objects.new('proof camera',d);s.collection.objects.link(cam);s.camera=cam;d.type='ORTHO';d.ortho_scale=.78
    return s,cam

def camera_at(cam,loc,target=(0,0,1.48)):
    from mathutils import Vector
    cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler()

def male_bust():
    import bpy
    from mathutils import Matrix
    source=ROOT/next(iter(SOURCES))
    with bpy.data.libraries.load(str(source),link=False) as (_,loaded):loaded.objects=['GEO-body_male_realistic']
    ob=loaded.objects[0];bpy.context.scene.collection.objects.link(ob)
    bpy.context.view_layer.update()
    world=ob.matrix_world.copy();points=[world@v.co for v in ob.data.vertices]
    center=(-2.705880880355835-1.8228728771209717)/2
    ids={i for i,p in enumerate(points) if p.z>1.19};remap={i:j for j,i in enumerate(sorted(ids))}
    verts=[(points[i].x-center,points[i].y,points[i].z) for i in sorted(ids)]
    faces=[tuple(remap[i] for i in p.vertices) for p in ob.data.polygons if all(i in ids for i in p.vertices)]
    bpy.data.objects.remove(ob,do_unlink=True)
    skin=material('temporary warm skin - not character approval',(.35,.18,.095))
    bust=mesh('source male bust diagnostic',verts,faces,skin)
    sub=bust.modifiers.new('donor smooth','SUBSURF');sub.levels=1
    bust.modifiers.new('body contact','COLLISION');bust.collision.thickness_outer=.002
    hair=material('beard placeholder',(.035,.019,.012))
    beard=sphere('beard volume contact',(0,-.082,1.446),(.070,.073,.067),hair)
    beard.modifiers.new('beard contact','COLLISION');beard.collision.thickness_outer=.002
    eye=material('eyes diagnostic',(.63,.55,.43));iris=material('brown iris diagnostic',(.045,.025,.010))
    for x in (-.032,.032):
        sphere('eye',(x,-.119,1.573),(.0115,.0115,.0115),eye)
        sphere('iris',(x,-.129,1.573),(.005,.0025,.005),iris)
    return bust,beard

def cloth_control(out, mode='cloth_control'):
    import bpy
    import numpy as np
    from mathutils import Vector
    s,cam=scene_setup();bust,beard=male_bust();d=cloth_strip()
    cloth=mesh('one cloth crown and face end',d['verts'],d['faces'],material('indigo cloth',(.028,.043,.085)))
    cloth.shape_key_add(name='Basis');flat=cloth.shape_key_add(name='material rest',from_mix=False);flat.value=0
    for v,p in zip(flat.data,d['rest']):v.co=p
    lift=cloth.shape_key_add(name='hand end transport',from_mix=False)
    for i,v in enumerate(lift.data):
        if i//d['cols']>=d['rows']-2:v.co=Vector(d['verts'][i])+Vector((-.04,-.085,-.24))
    # Use three separate endpoint channels so pull-clear precedes lowering.
    cloth.shape_key_remove(lift)
    keys=[]
    for axis in range(3):
        key=cloth.shape_key_add(name='end axis '+str(axis),from_mix=False)
        for i,v in enumerate(key.data):
            v.co=d['verts'][i]
            if i//d['cols']>=d['rows']-2:v.co[axis]+=(.04,.135,.24)[axis]
        key.slider_min=-1;keys.append(key)
    for frame in range(1,145):
        delta=end_translation(frame)
        for a,key in enumerate(keys):key.value=delta[a]/(.04,.135,.24)[a];key.keyframe_insert('value',frame=frame)
    pins=cloth.vertex_groups.new(name='secured crown and held end')
    pins.add(list(range(d['crown_rows']*d['cols'])),1,'REPLACE')
    pins.add(list(range((d['rows']-2)*d['cols'],len(d['verts']))),1,'REPLACE')
    weld=cloth.modifiers.new('verified rest-state evaluation precedent','WELD');weld.merge_threshold=.000001
    sim=cloth.modifiers.new('free end cloth','CLOTH');st=sim.settings
    st.quality=16;st.mass=.015;st.tension_stiffness=50;st.compression_stiffness=50;st.shear_stiffness=30;st.bending_stiffness=.15
    st.vertex_group_mass=pins.name;st.pin_stiffness=1;st.rest_shape_key=flat
    sim.collision_settings.use_collision=True;sim.collision_settings.distance_min=.002
    sim.collision_settings.use_self_collision=True;sim.collision_settings.self_distance_min=.0007
    sim.point_cache.frame_start=1;sim.point_cache.frame_end=144
    if mode=='cloth_self_off':sim.collision_settings.use_self_collision=False
    if mode=='cloth_rest_off':st.rest_shape_key=None
    if mode=='cloth_contact_off':sim.collision_settings.use_collision=False
    if mode=='cloth_free':
        sim.collision_settings.use_collision=False;sim.collision_settings.use_self_collision=False;st.rest_shape_key=None
        cloth.modifiers.remove(weld)
    if mode=='cloth_proxy':
        cloth.modifiers.remove(weld);st.rest_shape_key=None
        for actor in (bust,beard):
            for mod in list(actor.modifiers):
                if mod.type=='COLLISION':actor.modifiers.remove(mod)
        proxy=sphere('closed contact diagnostic',(0,-.005,1.565),(.104,.135,.135),bust.data.materials[0]);proxy.hide_render=True
        proxy.modifiers.new('closed head collision','COLLISION');proxy.collision.thickness_outer=.002
        sim.collision_settings.use_self_collision=False
    if mode=='cloth_release':
        cloth.modifiers.remove(weld);st.rest_shape_key=None
        st.bending_stiffness=.04;st.air_damping=2;st.quality=24
        sim.collision_settings.use_self_collision=False
        support=cloth.vertex_groups.new(name='supported wrapped state')
        support.add(list(range(len(d['verts']))),1,'REPLACE')
        mix=cloth.modifiers.new('untuck support transfer','VERTEX_WEIGHT_MIX')
        mix.vertex_group_a=support.name;mix.vertex_group_b=pins.name;mix.mix_mode='SET';mix.mix_set='ALL';mix.default_weight_b=0
        for frame,value in ((1,0),(30,0),(54,1),(144,1)):
            mix.mask_constant=value;mix.keyframe_insert('mask_constant',frame=frame)
        bpy.context.view_layer.objects.active=cloth
        bpy.ops.object.modifier_move_up(modifier=mix.name)
        st.vertex_group_mass=support.name
        chest=sphere('new tunic chest contact',(0,.025,1.22),(.24,.145,.18),bust.data.materials[0]);chest.hide_render=True
        chest.modifiers.new('tunic contact','COLLISION');chest.collision.thickness_outer=.002
    sub=cloth.modifiers.new('cloth display','SUBSURF');sub.levels=1
    solid=cloth.modifiers.new('single thickness','SOLIDIFY');solid.thickness=.001
    s.frame_start=1;s.frame_end=144
    s.frame_set(1);bpy.context.view_layer.update()
    assert flat.value==0, 'Rest metric must not replace dressed initial shape'
    (out/'initial-inventory.json').write_text(json.dumps({'objects':[{'name':o.name,'hide_render':o.hide_render,'location':list(o.location),'mesh_bounds':[[min(v.co[a] for v in o.data.vertices) for a in range(3)],[max(v.co[a] for v in o.data.vertices) for a in range(3)]] if o.type=='MESH' and len(o.data.vertices) else None} for o in s.objects],'keys':[(k.name,k.value) for k in cloth.data.shape_keys.key_blocks]},indent=2))
    records=[];samples=[]
    frame_end=144 if mode in ('cloth_control','cloth_release') else 24
    for frame in range(1,frame_end+1):
        s.frame_set(frame);bpy.context.view_layer.update()
        ev=cloth.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh()
        ar=np.array([v.co[:] for v in me.vertices]);ev.to_mesh_clear()
        if not np.isfinite(ar).all() or np.abs(ar).max()>4:raise RuntimeError('Cloth diverged at '+str(frame))
        samples.append(ar.astype(np.float32))
        if frame in (1,24,48,72,96,120,144):
            for view,loc in [('front',(0,-3,1.55)),('right',(-2,-2,1.55)),('rear',(0,3,1.55))]:
                camera_at(cam,loc);s.render.filepath=str(out/f'{frame:03d}-{view}.png')
                if bpy.ops.render.render(write_still=True)!={'FINISHED'}:raise RuntimeError('Render cancelled')
            records.append({'frame':frame,'bounds':[ar.min(0).tolist(),ar.max(0).tolist()],
                            'gravity':list(s.gravity),'keys':[(k.name,k.value,k.relative_key.name) for k in cloth.data.shape_keys.key_blocks],
                            'basis_samples':[list(cloth.data.shape_keys.key_blocks[0].data[i].co) for i in (0,2640,2992,3344)],
                            'evaluated_samples':[ar[i].tolist() for i in (0,2640,2992,3344)],
                            'pin_weights':[(i, next((g.weight for g in cloth.data.vertices[i].groups if g.group==pins.index),0)) for i in (0,2640,2992,3344)]})
        if frame%12==0:print('cloth frame',frame,flush=True)
    ev=cloth.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh()
    faces=np.array([list(p.vertices) for p in me.polygons],dtype=np.int32)
    ev.to_mesh_clear()
    np.savez_compressed(out/'evaluated-cloth.npz',points=np.stack(samples),faces=faces)
    (out/'construction.json').write_text(json.dumps({'mode':mode,'single_strip':True,'material_length_m':d['length'],'crown_rows':d['crown_rows'],'rows':d['rows'],'records':records,'status':'UNREVIEWED_CONTROL','limitations':['Endpoint transport uses held/tucked target; actual hand and release integration not yet tested','No final identity approval','No bike or acceleration proof']},indent=2)+'\n')
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'cloth-control.blend'))

def inspect(out):
    import bpy
    from mathutils import Vector
    result={}
    for rel in SOURCES:
        warning=None
        try:bpy.ops.wm.open_mainfile(filepath=str(ROOT/rel),load_ui=False,use_scripts=False)
        except RuntimeError as exc:
            if rel.endswith('/horse.blend') and "ShapeKey KEKey.001 has an invalid 'from' pointer" in str(exc) and bpy.data.objects.get('horse'):
                warning=str(exc)
            else:raise
        bpy.context.scene.frame_set(0)
        rows=[]
        for ob in bpy.data.objects:
            if 'human_base' in rel and not (ob.name.startswith('GEO-') and 'male' in ob.name and 'female' not in ob.name):continue
            bounds=[ob.matrix_world@Vector(c) for c in ob.bound_box]
            rows.append({'name':ob.name,'type':ob.type,'parent':ob.parent.name if ob.parent else None,
                         'bounds':[[min(c[i] for c in bounds) for i in range(3)],[max(c[i] for c in bounds) for i in range(3)]],
                         'vertices':len(ob.data.vertices) if ob.type=='MESH' else None,
                         'bones':[{'name':b.name,'head':list(b.head_local),'tail':list(b.tail_local)} for b in ob.data.bones] if ob.type=='ARMATURE' else [],
                         'asset':{k:getattr(ob.asset_data,k,None) for k in ('author','license','copyright')} if ob.asset_data else None})
        result[rel]={'sha256':digest(ROOT/rel),'objects':rows,'load_warning':warning,
                     'license_texts':{t.name:t.as_string() for t in bpy.data.texts if t.name.lower() in ('license','readme')}}
        (out/'inventory.partial.json').write_text(json.dumps(result,indent=2)+'\n')
    (out/'inventory.json').write_text(json.dumps(result,indent=2)+'\n')

def main():
    job=json.loads(Path(sys.argv[sys.argv.index('--')+1]).read_text())
    out=validate(job);out.mkdir(parents=True)
    (out/'source.py').write_bytes(Path(__file__).read_bytes())
    for relative in ('src/movie_factory/sikh257_geometry.py','src/movie_factory/sikh257_contract.py','scripts/sikh257_run.py'):
        (out/Path(relative).name).write_bytes((ROOT/relative).read_bytes())
    if job['operation']=='inspect':inspect(out)
    elif job['operation'].startswith('cloth_'):cloth_control(out,job['operation'])
    elif job['operation'].startswith('layout'):
        from sikh257_layout import build
        (out/'sikh257_layout.py').write_bytes((ROOT/'scripts/sikh257_layout.py').read_bytes())
        build(out,ROOT/LAYOUT_CACHE,job['operation'].endswith('stills'),'eevee' in job['operation'])
    else:raise ValueError('Handler not implemented; no partial dispatch')
    (out/'completed.json').write_text(json.dumps({'operation':job['operation'],'status':'technical_complete_not_visual_pass'}))

if __name__=='__main__':main()
