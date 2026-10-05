"""Use Blender's shipped XPBD cloth asset in a fixed diagnostic graph.

No downloaded node code or runtime code payloads. Native per-frame vertices
are retained before rendering; this is a scoped solver test, not acceptance.
"""
from pathlib import Path
import json

ASSET=Path('/Applications/Blender.app/Contents/Resources/5.2/datafiles/assets/nodes/geometry_nodes_dynamics_assets.blend')
ASSET_SHA='a2e6b4013abfc3b9355927e33b2ae5af2182dc079e820041124652a75ce7b100'


def socket(node,identifier,output=False):
    return next(s for s in (node.outputs if output else node.inputs) if s.identifier==identifier)


def graph(ob,collision,mode='baseline'):
    import bpy
    import wardrobe_motion178 as foundation
    if ASSET.is_symlink() or foundation.digest(ASSET)!=ASSET_SHA:raise ValueError('Bundled solver changed; inspect before reuse')
    with bpy.data.libraries.load(str(ASSET),link=False) as (src,dst):
        dst.node_groups=['Cloth Dynamics (Experimental)','Collider']
    group=bpy.data.node_groups.new('MF180_shipped_cloth_probe','GeometryNodeTree')
    group.interface.new_socket(name='Geometry',in_out='INPUT',socket_type='NodeSocketGeometry')
    group.interface.new_socket(name='Geometry',in_out='OUTPUT',socket_type='NodeSocketGeometry')
    nodes=group.nodes;links=group.links
    inp=nodes.new('NodeGroupInput');out=nodes.new('NodeGroupOutput')
    cloth=nodes.new('GeometryNodeGroup');cloth.node_tree=next(g for g in dst.node_groups if g.name.startswith('Cloth Dynamics'))
    links.new(inp.outputs['Geometry'],socket(cloth,'Socket_0'))
    links.new(socket(cloth,'Socket_1',True),out.inputs['Geometry'])
    pin=nodes.new('GeometryNodeInputNamedAttribute');pin.data_type='FLOAT';pin.inputs['Name'].default_value='MF180_pin'
    links.new(pin.outputs['Attribute'],socket(cloth,'Socket_2'))
    if mode=='extra':socket(cloth,'Socket_22').default_value='MF180_pin'
    if mode=='index':
        index=nodes.new('GeometryNodeInputIndex');cmp=nodes.new('ShaderNodeMath');cmp.operation='LESS_THAN';cmp.inputs[1].default_value=1
        links.new(index.outputs['Index'],cmp.inputs[0]);links.new(cmp.outputs[0],socket(cloth,'Socket_2'))
    for key,value in {'Socket_6':0.,'Socket_30':.95,'Socket_14':5,'Socket_15':15,
                       'Socket_31':.001,'Socket_24':.025,'Socket_8':1.,'Socket_3':(0,0,-79.803),'Socket_11':False}.items():
        socket(cloth,key).default_value=value
    if mode in ('quality','metric'):
        socket(cloth,'Socket_14').default_value=15
        socket(cloth,'Socket_15').default_value=100
        if mode=='metric':socket(cloth,'Socket_3').default_value=(0,0,-9.81)
    if collision is not None:
        collisions=collision if isinstance(collision,list) else [collision]
        bundle=nodes.new('NodeCombineBundle')
        for i,source in enumerate(collisions):
            bundle.bundle_items.new('BUNDLE','Contact_%d'%i)
            info=nodes.new('GeometryNodeObjectInfo');info.transform_space='RELATIVE';info.inputs['Object'].default_value=source
            col=nodes.new('GeometryNodeGroup');col.node_tree=next(g for g in dst.node_groups if g.name.startswith('Collider'))
            links.new(info.outputs['Geometry'],socket(col,'Socket_0'))
            socket(col,'Socket_12').default_value=.02;socket(col,'Socket_2').default_value=.35
            socket(col,'Socket_5').default_value=True
            links.new(socket(col,'Socket_7',True),bundle.inputs['Contact_%d'%i])
        links.new(bundle.outputs['Bundle'],socket(cloth,'Socket_21'))
    mod=ob.modifiers.new('Bundled native XPBD cloth','NODES');mod.node_group=group
    return mod


def unit_probe(out,quality=False):
    import bpy
    import numpy as np
    import wardrobe_motion178 as foundation
    from wardrobe_shawl180 import measures
    records={}
    for mode in (('quality','metric') if quality else ('baseline','extra','index')):
        p,f=foundation.sheet_grid(9,9,lambda u,v:(u,v,1.));p=np.array(p);f=np.array(f)
        mesh=bpy.data.meshes.new(mode);mesh.from_pydata(p.tolist(),[],f.tolist());mesh.update()
        a=mesh.attributes.new('MF180_pin','FLOAT','POINT');a.data[0].value=1.
        ob=bpy.data.objects.new(mode,mesh);bpy.context.scene.collection.objects.link(ob)
        graph(ob,None,mode);bpy.context.scene.frame_start=1
        for frame in range(1,25):
            bpy.context.scene.frame_set(frame);bpy.context.view_layer.update()
            ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());m=ev.to_mesh()
            q=np.array([v.co[:] for v in m.vertices]);attrs=[a.name for a in m.attributes];ev.to_mesh_clear()
        records[mode]=measures(p,f,{24:q},1.)
        records[mode].update({'pin_displacement':float(np.linalg.norm(q[0]-p[0])),'attributes':attrs})
        bpy.data.objects.remove(ob,do_unlink=True)
    (out/'result.json').write_text(json.dumps(records,indent=2)+'\n')
    print(json.dumps(records),flush=True)


def groom_audit(out,mats):
    import bpy
    import numpy as np
    from wardrobe_shawl179 import screens
    import wardrobe_motion178 as foundation
    groom=bpy.data.objects['MF_173_static_groom_clearance']
    screens(out,(1,))
    proxy=out/'proxy';proxy.mkdir()
    groom.hide_render=False;groom.hide_set(False)
    groom.data.materials.clear();groom.data.materials.append(mats['scarf'])
    screens(proxy,(1,))
    np.savez_compressed(out/'proxy.npz',points=np.array([tuple(groom.matrix_world@v.co) for v in groom.data.vertices]))
    foundation.check_protected()


def contact_probe(out):
    import bpy
    import numpy as np
    import wardrobe_motion178_controls as controls
    from wardrobe_shawl180 import measures
    import wardrobe_motion178 as foundation
    original=foundation.BASE/'wardrobe180-xpbdflat03/trajectory.npz'
    with np.load(original,allow_pickle=False) as d:p=d['points'].copy();f=d['faces'].copy()
    contacts=collision_snapshot(separate=True);records={}
    for contact in contacts:
        mesh=bpy.data.meshes.new('contact_probe');mesh.from_pydata(p.tolist(),[],f.tolist());mesh.update()
        pin=mesh.attributes.new('MF180_pin','FLOAT','POINT')
        for i in range(10,23):pin.data[i].value=1.
        ob=bpy.data.objects.new('MF178_live_solver180_probe',mesh);bpy.context.scene.collection.objects.link(ob);ob.hide_render=True
        graph(ob,contact,'quality')
        with controls.render_geometry_paused():
            for frame in range(1,25):
                bpy.context.scene.frame_set(frame);bpy.context.view_layer.update()
                ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());m=ev.to_mesh()
                q=np.array([v.co[:] for v in m.vertices]);ev.to_mesh_clear()
        r=measures(p,f,{24:q},bpy.context.scene.unit_settings.scale_length)
        coords=np.array([v.co[:] for v in contact.data.vertices])
        r.update({'pin_error':float(np.linalg.norm(q[10:23]-p[10:23],axis=1).max()),
                  'bounds':[coords.min(axis=0).tolist(),coords.max(axis=0).tolist()]})
        records[contact.name]=r
        (out/'result.json').write_text(json.dumps(records,indent=2)+'\n')
        print(contact.name,json.dumps(r),flush=True)
        bpy.data.objects.remove(ob,do_unlink=True)


def collision_snapshot(groom_only=False,separate=False,closed=False):
    import bpy
    from mathutils import Vector
    p=[];f=[];objects=[]
    names=('MF_studio_adult_body','MF_fit_tunic_173_visible',
                 'MF_171_fitted_sleeve_L_173_visible','MF_171_fitted_sleeve_R_173_visible',
                 'MF_173_tension_harness_-1','MF_173_tension_harness_1','MF_173_static_groom_clearance')
    for name in (names[-1:] if groom_only else names):
        if separate:p=[];f=[]
        ob=bpy.data.objects[name]
        states=[(m,m.show_viewport) for m in ob.modifiers if m.type in (('SUBSURF',) if closed else ('SUBSURF','SOLIDIFY'))]
        for mod,_ in states:mod.show_viewport=False
        bpy.context.view_layer.update();ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=ev.to_mesh()
        coords=[ob.matrix_world@v.co for v in mesh.vertices]
        mapping={}
        for poly in mesh.polygons:
            if not closed and not all(coords[i].z>-4.5 for i in poly.vertices):continue
            face=[]
            for i in poly.vertices:
                if i not in mapping:mapping[i]=len(p);p.append(tuple(coords[i]))
                face.append(mapping[i])
            f.append(face)
        ev.to_mesh_clear()
        for mod,state in states:mod.show_viewport=state
        if separate:
            mesh=bpy.data.meshes.new('MF180_collision_'+name);mesh.from_pydata(p,[],f);mesh.update()
            if closed:
                import bmesh
                bm=bmesh.new();bm.from_mesh(mesh)
                boundary=[e for e in bm.edges if e.is_boundary]
                if boundary:bmesh.ops.holes_fill(bm,edges=boundary,sides=0)
                bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free()
            contact=bpy.data.objects.new('MF178_support180_'+name,mesh);bpy.context.scene.collection.objects.link(contact)
            contact.hide_render=True;objects.append(contact)
    if separate:return objects
    mesh=bpy.data.meshes.new('MF180_collision');mesh.from_pydata(p,[],f);mesh.update()
    ob=bpy.data.objects.new('MF178_support180_combined',mesh);bpy.context.scene.collection.objects.link(ob)
    ob.hide_render=True
    return ob


def probe(out,mats,profile):
    import bpy
    import numpy as np
    import wardrobe_motion178 as foundation
    import wardrobe_motion178_controls as controls
    import wardrobe_studio as studio
    from wardrobe_shawl180_cut import construction
    from wardrobe_shawl179 import screens
    from wardrobe_shawl180 import measures
    p,f,pins,construction_record=construction(2)
    if profile=='weld01':
        from wardrobe_shawl179_weld import WELD_INPUT,WELD_SHA
        if foundation.digest(WELD_INPUT)!=WELD_SHA:raise ValueError('Preserved179 input changed')
        with np.load(WELD_INPUT,allow_pickle=False) as data:
            p=data['points'].copy();f=data['faces'].copy();pins=dict(zip(data['pin_indices'].tolist(),data['pin_weights'].tolist()))
        construction_record={'preserved179_weld':str(WELD_INPUT),'sha256':WELD_SHA}
    if profile in ('flat01','flat02'):
        p,f=foundation.sheet_grid(25,33,lambda u,v:((v-.5)*5.5,-.08+4.5*u,1.40))
        p=np.array(p);f=np.array(f);pins={2*33+13:1.,2*33+19:1.} if profile=='flat01' else {i:1. for i in range(13,20)}
    if profile in ('flat03','flat04','flat05','flat06'):
        import math
        from mathutils import Vector
        from wardrobe_refinement import tree_for
        p,f=foundation.sheet_grid(25,33,lambda u,v:(1.42*math.sin((v-.5)*math.pi),.04+4.2*u,1.18-1.3*(1-math.cos((v-.5)*math.pi))))
        p=np.array(p);f=np.array(f);pins={i:1. for i in range(10,23)}
        tree=tree_for(bpy.data.objects['MF_173_static_groom_clearance'])
        for i in pins:
            hit,_,_,_=tree.ray_cast(Vector((p[i,0],p[i,1],2.)),Vector((0,0,-1)),4.)
            if hit is None:raise ValueError('Missing pin support')
            p[i,2]=hit.z+.07
    if profile in ('head07','head08'):
        import math
        from mathutils import Vector
        from wardrobe_refinement import tree_for
        def head(u,v):
            s=(v-.5)*7.6;a=max(-math.pi/2,min(math.pi/2,s/1.42));extra=max(0.,abs(s)-1.42*math.pi/2)
            length=3.8+(1.3*max(0.,math.cos(a)) if profile=='head08' else 0.)
            return (1.42*math.sin(a)+math.copysign(.02*extra,s),-.02+length*u,1.18-1.3*(1-math.cos(a))-extra)
        p,f=foundation.sheet_grid(25,49,head);p=np.array(p);f=np.array(f);pins={i:1. for i in range(20,29)}
        tree=tree_for(bpy.data.objects['MF_173_static_groom_clearance'])
        for i in pins:
            hit,_,_,_=tree.ray_cast(Vector((p[i,0],p[i,1],2.)),Vector((0,0,-1)),4.)
            if hit is None:raise ValueError('Missing crown support')
            p[i,2]=hit.z+.07
        construction_record={'logical_construction':'Cylindrical rectangular head drape with side lengths; free edges, crown contact only','head_vertices':len(p)}
    mesh=bpy.data.meshes.new('MF180_XPBD_cloth');mesh.from_pydata(p.tolist(),[],f.tolist());mesh.update()
    pin=mesh.attributes.new('MF180_pin','FLOAT','POINT')
    for i,w in pins.items():pin.data[i].value=w
    ob=bpy.data.objects.new('MF178_live_solver180_XPBD',mesh);bpy.context.scene.collection.objects.link(ob);ob.hide_render=True
    col=collision_snapshot(groom_only=profile=='flat03',separate=profile in ('flat05','flat06','cut03','weld01','head07','head08'),closed=profile in ('flat06','cut03','weld01','head07','head08'))
    mod=graph(ob,col,'baseline' if profile in ('flat01','cut01') else 'quality')
    scene=bpy.context.scene;scene.frame_start=1;scene.frame_end=72;scene.render.fps=24
    # Simulation nodes retain actual sequential evaluated state.
    samples={}
    with controls.render_geometry_paused():
        for frame in range(1,73):
            scene.frame_set(frame);bpy.context.view_layer.update()
            ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());m=ev.to_mesh()
            coords=np.array([v.co[:] for v in m.vertices]);ev.to_mesh_clear()
            if coords.shape!=p.shape or not np.isfinite(coords).all() or abs(coords).max()>100:raise ValueError('Invalid XPBD geometry')
            samples[frame]=coords
            if frame%12==0:
                np.savez_compressed(out/('sample-%03d.npz'%frame),points=coords)
                print('180 bundled XPBD sample',frame,flush=True)
    np.savez_compressed(out/'trajectory.npz',points=p,faces=f,frames=np.array(list(samples.values())))
    studio.panel('MF180_XPBD_display',samples[72].tolist(),f.tolist(),mats['scarf'],.012,1)
    screens(out,(72,))
    foundation.check_protected()
    result=measures(p,f,{1:samples[1],24:samples[24],72:samples[72]},scene.unit_settings.scale_length)
    result.update({'profile':profile,'protected_exact':True,'visual_gate':'NOT_RUN','native_solver':'Bundled Cloth Dynamics (Experimental)',
        'construction':construction_record,'asset_sha256':foundation.digest(ASSET),
        'collision_vertices':sum(len(c.data.vertices) for c in col) if isinstance(col,list) else len(col.data.vertices),'native_frames':72,'motion_scope':'Neutral gravity settling only; no riding/wind pass'})
    result['max_pin_displacement']=float(max(np.linalg.norm(samples[72][i]-p[i]) for i,w in pins.items() if w==1))
    (out/'result.json').write_text(json.dumps(result,indent=2)+'\n')
