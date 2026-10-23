"""Fixed23 neutral-cloth transfer to the qualified59 sampled arm scaffold."""
import json,importlib.util
from pathlib import Path
import numpy as np

def module(name):
    spec=importlib.util.spec_from_file_location('mf352_'+name,Path(__file__).with_name(name+'.py'))
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def blend_weights(rows,distances):
    weights=1/np.maximum(np.asarray(distances),.002)**2;weights/=sum(weights)
    result={}
    for factor,row in zip(weights,rows):
        for name,value in row:result[name]=result.get(name,0)+float(factor)*value
    total=sum(result.values())
    if total<.1:raise ValueError('CLOTH352_EMPTY_WEIGHT')
    return {n:w/total for n,w in result.items() if w>1e-6}

def elbow_ease(p,s,e,w,amount=.022):
    p,s,e,w=map(np.asarray,(p,s,e,w));candidates=[]
    for a,b in ((s,e),(e,w)):
        t=np.clip(np.dot(p-a,b-a)/np.dot(b-a,b-a),0,1);q=a+t*(b-a)
        candidates.append((float(np.linalg.norm(p-q)),q))
    distance,q=min(candidates,key=lambda item:item[0])
    if distance<1e-7:return p.copy()
    weight=np.exp(-(np.linalg.norm(p-e)/.105)**2)
    return p+(p-q)/distance*amount*weight

def refine(bpy,out):
    import bmesh,math
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    rig=bpy.data.objects['MF coherent Nihang rig'];coat=bpy.data.objects['MF coherent coat']
    if not rig.get('cloth352') or rig.get('cloth352_refine'):raise ValueError('CLOTH352_REFINE_PARENT')
    rig.data.pose_position='REST';bpy.context.view_layer.update();coat.data=coat.data.copy();old=len(coat.data.vertices)
    changed=0
    for v in coat.data.vertices:
        arms=sum(g.weight for g in v.groups if coat.vertex_groups[g.group].name.startswith(('upperarm','lowerarm')))
        if arms<.25:continue
        side='L' if v.co.x>0 else 'R'
        p=elbow_ease(np.array(v.co),np.array(rig.data.bones['upperarm01.'+side].head_local),np.array(rig.data.bones['lowerarm01.'+side].head_local),np.array(rig.data.bones['wrist.'+side].head_local))
        if np.linalg.norm(p-np.array(v.co))>.0001:changed+=1
        v.co=Vector(p)
    bm=bmesh.new();bm.from_mesh(coat.data)
    # Rest cuffs are above1.1; this cut affects the central hem only.
    bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=1e-6,plane_co=(0,0,1.075),plane_no=(0,0,1),clear_inner=True)
    loose=[v for v in bm.verts if not v.link_faces]
    if loose:bmesh.ops.delete(bm,geom=loose,context='VERTS')
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(coat.data);bm.free();coat.data.update()
    copied_rows=[[(coat.vertex_groups[g.group].name,g.weight) for g in v.groups] for v in coat.data.vertices]
    for name in ('MF coherent layer support','MF346 waist-only coat support'):
        ob=bpy.data.objects[name];ob.data=coat.data.copy();ob.vertex_groups.clear()
        for g in coat.vertex_groups:ob.vertex_groups.new(name=g.name)
        if name=='MF346 waist-only coat support':
            g=ob.vertex_groups.get('spine05') or ob.vertex_groups.new(name='spine05');g.add(list(range(len(ob.data.vertices))),1,'REPLACE')
        else:
            for i,row in enumerate(copied_rows):
                for n,w in row:ob.vertex_groups[n].add([i],w,'REPLACE')
    tree=BVHTree.FromPolygons([v.co for v in coat.data.vertices],[tuple(p.vertices) for p in coat.data.polygons])
    band=bpy.data.objects['MF coherent waist wrap'];pts=[];faces=[];rows=9;cols=97
    for j in range(rows):
        for k in range(cols):
            a=math.tau*k/(cols-1);z=1.083+.085*j/(rows-1);axis=Vector((math.sin(a),-math.cos(a),0));origin=Vector((0,-.02,z))
            hit=tree.ray_cast(origin+axis*.6,-axis)[0]
            if hit is None:raise ValueError('CLOTH352_BAND_UNSUPPORTED')
            pts.append(hit+axis*(.014+.0015*math.sin(j*.9+a*2)))
            if j and k:
                n=j*cols+k;faces.append((n-cols-1,n-cols,n,n-1))
    data=bpy.data.meshes.new('352 coherent garment waist band');data.from_pydata(pts,[],faces);data.update()
    for mat in band.data.materials:data.materials.append(mat)
    band.data=data;band.vertex_groups.clear();g=band.vertex_groups.new(name='spine05');g.add(list(range(len(pts))),1,'REPLACE');band.modifiers.clear()
    arm=band.modifiers.new('352 waist owner','ARMATURE');arm.object=rig;arm.use_deform_preserve_volume=True
    sub=band.modifiers.new('352 woven band surface','SUBSURF');sub.levels=1;sub.render_levels=1
    solid=band.modifiers.new('352 band thickness','SOLIDIFY');solid.thickness=.002
    for p in data.polygons:p.use_smooth=True
    rig['cloth352_refine']=1;rig.data.pose_position='POSE';bpy.context.scene.frame_set(327);bpy.context.view_layer.update()
    report=dict(changed=True,source_preserved=True,vertices=len(coat.data.vertices),previous_vertices=old,elbow_ease_vertices=changed,band_vertices=len(pts),scope='Localized garment interfaces only; body/pose unchanged. Whole actor and dynamics not passed.')
    (out/'cloth352.json').write_text(json.dumps(report,indent=2)+'\n');return report

def run(bpy,out):
    import bmesh
    from mathutils import Vector
    from mathutils.kdtree import KDTree
    from mathutils.bvhtree import BVHTree
    rig=bpy.data.objects['MF coherent Nihang rig'];body=bpy.data.objects['MF coherent Nihang body'];coat=bpy.data.objects['MF coherent coat']
    if not rig.get('arm352') or rig.get('cloth352'):raise ValueError('CLOTH352_PARENT')
    neutral=module('nihang_neutral');transfer=module('nihang_transfer')
    source=bpy.data.objects[neutral.CLOTH];rest=np.array([v.co[:] for v in source.data.vertices]);faces=[tuple(p.vertices) for p in source.data.polygons]
    baseline=Path(__file__).resolve().parents[4]/'.runtime/factory-native/sikh342-look-c23-save/neutral-proof.npz'
    approved=np.load(baseline,allow_pickle=False)['final']
    if rest.shape!=approved.shape or not np.allclose(rest,approved,atol=1e-6):raise ValueError('CLOTH352_NEUTRAL_CHANGED')
    scene=bpy.context.scene;rig.data.pose_position='REST';bpy.context.view_layer.update()
    states=[(m,m.show_viewport,m.show_render) for m in body.modifiers]
    for m,_,_ in states:m.show_viewport=False;m.show_render=False
    bpy.context.view_layer.update();raw=bpy.data.meshes.new_from_object(body.evaluated_get(bpy.context.evaluated_depsgraph_get()))
    if len(raw.vertices)!=len(body.data.vertices):raise ValueError('CLOTH352_BODY_INDEX')
    kd=KDTree(len(raw.vertices))
    for v in raw.vertices:kd.insert(v.co,v.index)
    kd.balance()
    for m,v,r in states:
        if m.type=='MASK':m.show_viewport=v;m.show_render=r
    bpy.context.view_layer.update();surface=bpy.data.meshes.new_from_object(body.evaluated_get(bpy.context.evaluated_depsgraph_get()))
    tree=BVHTree.FromPolygons([v.co for v in surface.vertices],[tuple(p.vertices) for p in surface.polygons])
    pts=rest.copy();pts[:,0]*=1.08;pts[:,2]=1.265*rest[:,2]-.202
    for sign,side in ((-1,'R'),(1,'L')):
        reflected=rest.copy();reflected[:,0]*=sign;component=neutral.connected_arm(reflected,faces)
        cuff=np.flatnonzero(component&(rest[:,2]<.935))
        if len(cuff)<8:raise ValueError('CLOTH352_CUFF')
        a=np.array([sign*.18,0,1.36]);b=np.array([sign*.285,-.005,1.13]);cc=rest[cuff].mean(0)
        aa=np.array(rig.data.bones['upperarm01.'+side].head_local);bb=np.array(rig.data.bones['lowerarm01.'+side].head_local)
        wrist=np.array(rig.data.bones['wrist.'+side].head_local);axis=(wrist-bb)/np.linalg.norm(wrist-bb);wc=wrist-.025*axis
        up=transfer.segment_points(rest,a,b,aa,bb);low=transfer.segment_points(rest,b,cc,bb,wc)
        fore=transfer.ease((1.19-rest[:,2])/.12);blend=transfer.ease((rest[:,0]*sign-.145)/.085)
        blend=np.where(rest[:,2]<1.17,component.astype(float),blend)
        moved=up*(1-fore[:,None])+low*fore[:,None];pts=pts*(1-blend[:,None])+moved*blend[:,None]
    # Push inside-rest vertices out only; never shrink outside cloth to skin.
    offsets=[]
    for i,p in enumerate(pts):
        hit,n,_,_=tree.find_nearest(Vector(p));signed=float(np.dot(p-np.array(hit),np.array(n)))
        correction=max(0,.012-signed)
        if correction>.12:raise ValueError('CLOTH352_FIT_OUTSIDE_BOUND')
        pts[i]+=np.array(n)*correction;offsets.append(correction)
    rows=[]
    for p in pts:
        near=kd.find_n(Vector(p),4);wr=[]
        for _,i,_ in near:wr.append([(body.vertex_groups[g.group].name,g.weight) for g in body.data.vertices[i].groups if body.vertex_groups[g.group].name in rig.data.bones])
        rows.append(blend_weights(wr,[n[2] for n in near]))
    mesh=bpy.data.meshes.new('352 independent neutral-derived cloth');mesh.from_pydata(pts,[],faces);mesh.update()
    bm=bmesh.new();bm.from_mesh(mesh);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(mesh);bm.free()
    for mat in coat.data.materials:mesh.materials.append(mat)
    owners=[coat]+[o for o in bpy.data.objects if o.name in ('MF coherent layer support','MF346 waist-only coat support')]
    for ob in owners:
        ob.data=mesh.copy() if ob!=coat else mesh;ob.vertex_groups.clear();ob.modifiers.clear()
        for i,row in enumerate(rows):
            if ob.name=='MF346 waist-only coat support':row={n:w for n,w in row.items() if not n.startswith(('upperarm','lowerarm','wrist','finger'))} or {'spine05':1.}
            total=sum(row.values())
            for n,w in row.items():
                g=ob.vertex_groups.get(n) or ob.vertex_groups.new(name=n);g.add([i],w/total,'REPLACE')
        arm=ob.modifiers.new('352 shared anatomical skeleton','ARMATURE');arm.object=rig;arm.use_deform_preserve_volume=True
        sub=ob.modifiers.new('352 independent cloth surface','SUBSURF');sub.levels=1;sub.render_levels=1
        if ob==coat:
            solid=ob.modifiers.new('352 fabric thickness','SOLIDIFY');solid.thickness=.002
        for poly in ob.data.polygons:poly.use_smooth=True
    for m,v,r in states:m.show_viewport=v;m.show_render=r
    bpy.data.meshes.remove(raw);bpy.data.meshes.remove(surface)
    rig.data.pose_position='POSE';rig['cloth352']=1;scene.frame_set(327);bpy.context.view_layer.update()
    report=dict(changed=True,source=neutral.CLOTH,vertices=len(pts),faces=len(faces),source_preserved=True,
                maximum_rest_push=max(offsets),pushed_vertices=sum(x>0 for x in offsets),owners=[o.name for o in owners],
                scope='Independent neutral garment, not body shell. No motion/look acceptance; actual clearances and old trim interfaces require review.')
    (out/'cloth352.json').write_text(json.dumps(report,indent=2)+'\n');return report
