"""Contact ablation on exact retained garment geometry; no actor rebuild."""
import json
from pathlib import Path
import numpy as np


def run(out):
    import bpy
    import wardrobe_motion178 as base
    from wardrobe_doublewrap185 import cloth_settings
    from wardrobe_shawl180 import measures
    (out/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
    sources={'conditioning.npz':'88a2705bf0b5e5ba2ff76d25a664936f11e1b4c9cc98836744158344a1715860',
        'trajectory.npz':'17b6312aa1c87b4c341b2a54e8b2df251f6e4e79b4a0026a183c7f2a64cb669e'}
    root=base.BASE/'wardrobe185-settle03'
    for name,sha in sources.items():
        if base.digest(root/name)!=sha:raise ValueError('Ablation input changed')
    with np.load(root/'conditioning.npz',allow_pickle=False) as d:cp=d['contact_points'];cf=d['contact_faces']
    with np.load(root/'trajectory.npz',allow_pickle=False) as d:
        p=d['points'];f=d['faces'];pins=d['pin_indices'];weights=d['pin_weights'];counts=d['counts']
    source_p=p.copy()
    if out.name.endswith('isolate04'):
        proxy=base.BASE/'wardrobe185-proxy02/proxy.npz'
        if base.digest(proxy)!='19cce587247a325e2f0b081f49e14eb0a40bf6c3364896a327af4639a6d4f7eb':raise ValueError('Envelope input changed')
        with np.load(proxy,allow_pickle=False) as d:cp=d['points'];cf=d['faces']
    bpy.ops.wm.open_mainfile(filepath=str(base.SOURCE),load_ui=False,use_scripts=False)
    scale=bpy.context.scene.unit_settings.scale_length
    source_fields=[{'name':o.name,'type':o.field.type,'strength':o.field.strength}
        for o in bpy.context.scene.objects if o.field and o.field.type!='NONE']
    records={'source_fields':source_fields,'scale':scale,'sources':sources,'cases':{}}
    cases=(('both',True,True),('external',False,True),('self',True,False),('none',False,False))
    if out.name.endswith('isolate02'):cases=(('thin_inner',False,True),('culled',False,True))
    if out.name.endswith('isolate03'):cases=(('normal',False,True),('nocull',False,True),('undecimated',False,True))
    if out.name.endswith('isolate04'):cases=(('envelope',False,True),('envelope_clear',True,True))
    for name,self_contact,external in cases:
        p=source_p.copy();conditioning=None
        bpy.ops.wm.read_factory_settings(use_empty=True)
        scene=bpy.context.scene;scene.render.fps=24;scene.gravity=(0,0,-9.81)
        scene.unit_settings.scale_length=scale
        mesh=bpy.data.meshes.new('cloth');mesh.from_pydata((p*scale).tolist(),[],f.tolist());mesh.update()
        ob=bpy.data.objects.new('cloth',mesh);scene.collection.objects.link(ob)
        group=ob.vertex_groups.new(name='support')
        for i,w in zip(pins,weights):group.add([int(i)],float(w),'REPLACE')
        mesh=bpy.data.meshes.new('contact');mesh.from_pydata(cp.tolist(),[],cf.tolist());mesh.update()
        contact=bpy.data.objects.new('contact',mesh);scene.collection.objects.link(contact)
        bpy.context.view_layer.objects.active=contact
        if name!='undecimated':
            dec=contact.modifiers.new('Same contact reduction','DECIMATE');dec.ratio=min(1,12000/len(cf))
            bpy.ops.object.modifier_apply(modifier=dec.name)
        for v in contact.data.vertices:v.co*=scale
        contact.data.update();contact.modifiers.new('Collision','COLLISION')
        contact.collision.thickness_outer=.0015;contact.collision.cloth_friction=15
        default_inner=contact.collision.thickness_inner
        if name in ('thin_inner','culled'):contact.collision.thickness_inner=.0015
        if name=='culled':contact.collision.use_culling=True
        if name=='normal':contact.collision.use_normal=True
        if name=='nocull':contact.collision.use_culling=False
        if name=='envelope_clear':
            from mathutils import Vector
            from mathutils.bvhtree import BVHTree
            from wardrobe_doublewrap185_solve import inside
            tree=BVHTree.FromPolygons([v.co[:] for v in contact.data.vertices],[v.vertices[:] for v in contact.data.polygons])
            distances=[]
            for i,point in enumerate(p*scale):
                q=Vector(point);h,n,_,distance=tree.find_nearest(q);within=inside(tree,q)
                if within or distance<.005:
                    direction=h-q if within else q-h
                    if direction.length<1e-7:direction=n
                    q=h+direction.normalized()*.005
                distances.append((q-Vector(point)).length);p[i]=np.array(q)/scale
                ob.data.vertices[i].co=q
            ob.data.update();conditioning={'max_m':max(distances),'adjusted':sum(d>1e-7 for d in distances)}
            if max(distances)>.03:raise ValueError('Envelope conditioning requires material reconstruction')
        domain=bpy.data.collections.new('Contact domain');scene.collection.children.link(domain);domain.objects.link(contact)
        mod=cloth_settings(ob,1,domain if external else None)
        mod.settings.mass=.3;mod.settings.air_damping=.2;mod.settings.bending_stiffness=.05
        mod.settings.tension_stiffness=200;mod.settings.compression_stiffness=200;mod.settings.shear_stiffness=100
        mod.settings.quality=24;mod.collision_settings.use_self_collision=self_contact
        samples=[]
        for frame in range(1,49):
            scene.frame_set(frame);bpy.context.view_layer.update()
            ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());m=ev.to_mesh()
            q=np.array([v.co[:] for v in m.vertices])/scale;ev.to_mesh_clear()
            if q.shape!=p.shape or not np.isfinite(q).all():raise ValueError('Invalid isolated trajectory')
            samples.append(q)
        np.savez_compressed(out/(name+'.npz'),points=p,faces=f,frames=np.array(samples),counts=counts)
        r=measures(p,f,{48:samples[-1]},scale);r['max_displacement_m']=float(np.linalg.norm(samples[-1]-p,axis=1).max()*scale)
        r['collision_settings']={'default_inner':default_inner,'inner':contact.collision.thickness_inner,
            'outer':contact.collision.thickness_outer,'culling':contact.collision.use_culling,'normal':contact.collision.use_normal}
        r['contact_polygons']=len(contact.data.polygons)
        r['initial_conditioning']=conditioning
        r['collision_setting_descriptions']={k:contact.collision.bl_rna.properties[k].description for k in ('use_culling','use_normal','thickness_inner','thickness_outer')}
        records['cases'][name]=r
        (out/'result.json').write_text(json.dumps(records,indent=2)+'\n')
        print(name,json.dumps(r),flush=True)
