"""Stage one: drape a clean rectangular sheet over the actual groom envelope."""
import json,math
from pathlib import Path
import numpy as np

HEAD05_SHA='81a6e84910e54cc41d7c0a4b72e2a1b8bea09e38ca89fdccb6109df983b98e09'
HEAD06_SHA='c2be9aa725e106b6af3e7fb373953b0d53f5ec0e966fc59403fe922b26ea5f48'


def screen(out):
    import bpy
    import wardrobe_studio as studio
    from wardrobe_motion178 import BASE,digest,check_protected
    from wardrobe_riding_fit import fit_render
    from wardrobe_doublewrap185 import color
    source=BASE/'wardrobe185-motionreview03/diagnostic.blend'
    head=BASE/'wardrobe185-headdress05/trajectory.npz'
    if digest(source)!='0f128ba60947d4451f7e0bbaa3a5f6f275173702e3d4bddd245cef73d2310bd7' or digest(head)!=HEAD05_SHA:raise ValueError('Unbound head review')
    (out/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
    with np.load(head,allow_pickle=False) as d:p=d['frames'][-1];f=d['faces']
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False)
    scene=bpy.context.scene;scene.frame_set(1);bpy.context.view_layer.update()
    bpy.data.objects['MF185_moving_shawl'].hide_render=True
    studio.panel('MF185_redressed_head',p.tolist(),f.tolist(),color('new indigo head',(.06,.10,.18)),.012,1)
    scene.cycles.device='CPU';scene.cycles.samples=8;scene.render.use_persistent_data=True
    for angle,label in ((0,'front'),(60,'left-quarter'),(90,'left'),(180,'rear'),(270,'right'),(300,'right-quarter')):
        fit_render(out,label,angle,(0,.1,-1.3),7.,(640,640))
    check_protected()
    (out/'result.json').write_text(json.dumps({'head_sha256':HEAD05_SHA,'visual_gate':'NOT_RUN','motion_gate':'NOT_RUN'},indent=2)+'\n')


def pattern(crown=1.30, front_width=.78, spread_tails=False, rear_width=.78, length_m=.55):
    rows,cols=41,61;scale=.12292759120464325
    if not (.45<=rear_width<=1.2 and .4<=length_m<=.8):raise ValueError('Cut outside scoped headfall dimensions')
    length=length_m/scale
    p=[];r=[];f=[]
    for i in range(rows):
        u=i/(rows-1)
        local_width=(front_width*(1-u)+rear_width*u)/scale
        for j in range(cols):
            s=(j/(cols-1)-.5)*local_width;a=max(-math.pi/2,min(math.pi/2,s/1.36))
            extra=max(0,abs(s)-1.36*math.pi/2)
            p.append((1.36*math.sin(a)+math.copysign((.90 if spread_tails else .025)*extra,s),.05+length*u,crown-1.36*(1-math.cos(a))-(.30 if spread_tails else 1.)*extra))
            r.append((length*u,s,0))
    for i in range(rows-1):
        for j in range(cols-1):f.append((i*cols+j,(i+1)*cols+j,(i+1)*cols+j+1,i*cols+j+1))
    return np.array(p),np.array(f),np.array(r)


def run(out):
    import bpy
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    import wardrobe_motion178 as base
    from wardrobe_doublewrap185_solve import inside
    from wardrobe185_cut import winding_inside
    from wardrobe_doublewrap185 import cloth_settings
    from wardrobe_shawl180 import measures
    (out/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
    regional=out.name.endswith(('05','06','07'))
    bpy.ops.wm.read_factory_settings(use_empty=True);scene=bpy.context.scene;scene.render.fps=24;scene.gravity=(0,0,-9.81)
    revised=out.name.endswith(('02','03','04','05','06','07'))
    front_width=1.18 if out.name.endswith(('06','07')) else .94 if out.name.endswith(('03','04','05')) else .78
    rear_width=.58 if out.name.endswith('07') else .78;length_m=.62 if out.name.endswith('07') else .55
    scale=.12292759120464325;p,f,r=pattern(1.10 if revised else 1.30,front_width,spread_tails=out.name.endswith(('04','05','06','07')),rear_width=rear_width,length_m=length_m)
    if regional:
        from wardrobe185_convex import static_contacts
        contact=static_contacts(out,scale)
    else:
        path=base.BASE/'wardrobe185-proxy02/proxy.npz'
        if base.digest(path)!='19cce587247a325e2f0b081f49e14eb0a40bf6c3364896a327af4639a6d4f7eb':raise ValueError('Proxy changed')
        with np.load(path,allow_pickle=False) as d:cp=d['points'];cf=d['faces']
        mesh=bpy.data.meshes.new('Actor');mesh.from_pydata((cp*scale).tolist(),[],cf.tolist());mesh.update()
        contact=bpy.data.objects.new('Actor',mesh);scene.collection.objects.link(contact);bpy.context.view_layer.objects.active=contact
        dec=contact.modifiers.new('Contact reduction','DECIMATE');dec.ratio=min(1,12000/len(cf));bpy.ops.object.modifier_apply(modifier=dec.name)
    mesh=contact.data
    mesh.calc_loop_triangles();v=np.array([x.co[:] for x in mesh.vertices]);t=np.array([x.vertices[:] for x in mesh.loop_triangles])
    tree=BVHTree.FromPolygons(v.tolist(),t.tolist(),all_triangles=True);deltas=[]
    for i,point in enumerate(p*scale):
        q=Vector(point);h,n,_,dist=tree.find_nearest(q)
        try:within=inside(tree,q)
        except ValueError:within=winding_inside(point,v[t])
        if within or dist<.005:
            direction=h-q if within else q-h
            if direction.length<1e-7:direction=n
            q=h+direction.normalized()*.005
        deltas.append((q-Vector(point)).length);p[i]=np.array(q)/scale
    (out/'construction.json').write_text(json.dumps({'max_adjustment_m':max(deltas),'front_width_m':front_width,'rear_width_m':rear_width,'length_m':length_m},indent=2)+'\n')
    if max(deltas)>.03:raise ValueError('Fresh pattern penetrates actor; correct initial drape')
    contact.modifiers.new('Collision','COLLISION');contact.collision.thickness_outer=.0015;contact.collision.cloth_friction=15
    domain=bpy.data.collections.new('Domain');scene.collection.children.link(domain);domain.objects.link(contact)
    mesh=bpy.data.meshes.new('Head sheet');mesh.from_pydata((p*scale).tolist(),[],f.tolist());mesh.update()
    ob=bpy.data.objects.new('Head sheet',mesh);scene.collection.objects.link(ob)
    group=ob.vertex_groups.new(name='support');pins=list(range(25,36));group.add(pins,1.,'REPLACE')
    ob.shape_key_add(name='Basis');key=ob.shape_key_add(name='Rectangle')
    for v,q in zip(key.data,r*scale):v.co=q
    key.value=0.;ob.active_shape_key_index=0
    weld=ob.modifiers.new('Verified rest evaluation','WELD');weld.merge_threshold=1e-6
    mod=cloth_settings(ob,1,domain);mod.settings.rest_shape_key=key;mod.settings.use_dynamic_mesh=False
    s=mod.settings;s.mass=.3;s.air_damping=.2;s.bending_stiffness=.05;s.tension_stiffness=200;s.compression_stiffness=200;s.shear_stiffness=100;s.quality=24
    end=240 if revised else 120
    mod.point_cache.frame_end=end;frames=[]
    pin_distances=[tree.find_nearest(Vector(p[i]*scale))[3] for i in pins]
    (out/'support-check.json').write_text(json.dumps({'pin_nearest_distances_m':pin_distances,'crown_native':1.10 if revised else 1.30},indent=2)+'\n')
    for frame in range(1,end+1):
        scene.frame_set(frame);bpy.context.view_layer.update();ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());m=ev.to_mesh()
        q=np.array([x.co[:] for x in m.vertices])/scale;ev.to_mesh_clear()
        if q.shape!=p.shape or not np.isfinite(q).all() or abs(q).max()>50:raise ValueError('Invalid staged head solve')
        frames.append(q)
        if frame%24==0:print('185 clean head drape',frame,flush=True)
    np.savez_compressed(out/'trajectory.npz',points=p,faces=f,rest=r,frames=np.array(frames),counts=[len(p)],pin_indices=pins,pin_weights=np.ones(len(pins)))
    (out/'result.json').write_text(json.dumps({'metric':measures(r,f,{end:q},scale),'last_max_step_m':float(np.linalg.norm(frames[-1]-frames[-2],axis=1).max()*scale),'visual_gate':'NOT_RUN','motion_gate':'NOT_RUN','representation':'Dressed rectangular fabric, not inherited settled headfall'},indent=2)+'\n')
