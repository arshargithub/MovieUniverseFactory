"""Fixed torso-owned waist reconstruction. No model-provided code/parameters."""
import json, math
import numpy as np

def torso_faces(faces, weights):
    """All vertices must belong to the trunk; a sleeve hit cannot be support."""
    valid=[]
    for i, face in enumerate(faces):
        if all(sum(w for n,w in weights[v] if n.startswith(('upperarm','lowerarm','wrist','finger','clavicle'))) < .10
               and sum(w for n,w in weights[v] if n.startswith(('spine','pelvis','root','upperleg'))) > .85 for v in face):
            valid.append(i)
    if not valid:raise ValueError('WAIST353_NO_TORSO_FACES')
    return valid

def check_envelope(radii):
    r=np.asarray(radii)
    if not np.isfinite(r).all() or r.min()<.06 or r.max()>.28:
        raise ValueError('WAIST353_RADIAL_ENVELOPE')
    if np.abs(r-np.roll(r,1,axis=1)).max()>.025:
        raise ValueError('WAIST353_RADIAL_SPIKE')
    return dict(minimum=float(r.min()),maximum=float(r.max()),max_step=float(np.abs(r-np.roll(r,1,axis=1)).max()))

def run(bpy,out):
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    rig=bpy.data.objects['MF coherent Nihang rig'];coat=bpy.data.objects['MF coherent coat']
    if not rig.get('cloth352_refine') or rig.get('waist353'):raise ValueError('WAIST353_PARENT')
    rig.data.pose_position='REST';bpy.context.view_layer.update()
    weights=[[(coat.vertex_groups[g.group].name,g.weight) for g in v.groups] for v in coat.data.vertices]
    faces=[tuple(p.vertices) for p in coat.data.polygons];ids=torso_faces(faces,weights)
    vertices=[v.co for v in coat.data.vertices]
    tree=BVHTree.FromPolygons(vertices,[faces[i] for i in ids])
    legacy=BVHTree.FromPolygons(vertices,faces)
    rows=9;cols=96;radii=[];old=[];points=[];polys=[]
    for j in range(rows):
        rr=[];oo=[]
        for k in range(cols):
            a=math.tau*k/cols;axis=Vector((math.sin(a),-math.cos(a),0));origin=Vector((0,-.02,1.083+.085*j/(rows-1)))
            hit=tree.ray_cast(origin+axis*.6,-axis)[0];prior=legacy.ray_cast(origin+axis*.6,-axis)[0]
            if hit is None:
                near=tree.find_nearest(origin+axis*.16)
                print('WAIST353_MISSING',json.dumps(dict(row=j,column=k,selected=len(ids),nearest=list(near[0]) if near[0] else None,groups=[g.name for g in coat.vertex_groups])),flush=True)
                raise ValueError('WAIST353_UNSUPPORTED_TORSO')
            rr.append((hit-origin).dot(axis));oo.append((prior-origin).dot(axis) if prior is not None else None)
        radii.append(rr);old.append(oo)
    envelope=check_envelope(radii)
    # Small periodic filtering removes inherited cloth micro-ripples from the
    # load-bearing belt, without introducing support from a different body part.
    r=np.asarray(radii)
    for _ in range(2):r=(np.roll(r,1,axis=1)+2*r+np.roll(r,-1,axis=1))/4
    for j in range(rows):
        for k in range(cols):
            a=math.tau*k/cols;rad=r[j,k]+.014+.001*math.sin(j*.8+a*2)
            points.append((rad*math.sin(a),-.02-rad*math.cos(a),1.083+.085*j/(rows-1)))
            if j:polys.append(((j-1)*cols+k,(j-1)*cols+(k+1)%cols,j*cols+(k+1)%cols,j*cols+k))
    band=bpy.data.objects['MF coherent waist wrap'];data=bpy.data.meshes.new('353 torso-owned closed waist')
    data.from_pydata(points,[],polys);data.update()
    for mat in band.data.materials:data.materials.append(mat)
    band.data=data;band.vertex_groups.clear();g=band.vertex_groups.new(name='spine05');g.add(list(range(len(points))),1,'REPLACE')
    for p in data.polygons:p.use_smooth=True
    rig['waist353']=1;rig.data.pose_position='POSE';bpy.context.scene.frame_set(327);bpy.context.view_layer.update()
    report=dict(changed=True,source_preserved=True,vertices=len(coat.data.vertices),torso_faces=len(ids),excluded_faces=len(faces)-len(ids),envelope=envelope,
      maximum_legacy_radius=float(np.nanmax(np.array(old,dtype=float))),legacy_differing_rays=int(np.sum(np.abs(np.array(old,dtype=float)-np.array(radii))>.01)),
      scope='Torso-only waist support; no whole-character or performance approval.')
    (out/'waist353.json').write_text(json.dumps(report,indent=2)+'\n');return report

def attach(bpy,out):
    from mathutils import Vector
    from mathutils.kdtree import KDTree
    from mathutils.bvhtree import BVHTree
    import importlib.util
    from pathlib import Path
    spec=importlib.util.spec_from_file_location('cloth352_weights',Path(__file__).with_name('nihang_cloth352.py'))
    helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper)
    rig=bpy.data.objects['MF coherent Nihang rig'];coat=bpy.data.objects['MF coherent coat'];band=bpy.data.objects['MF coherent waist wrap']
    if not rig.get('waist353') or rig.get('waist353_attached'):raise ValueError('WAIST353_ATTACH_PARENT')
    rig.data.pose_position='REST';bpy.context.view_layer.update()
    rows=[[(coat.vertex_groups[g.group].name,g.weight) for g in v.groups] for v in coat.data.vertices]
    faces=[tuple(p.vertices) for p in coat.data.polygons];ids=torso_faces(faces,rows)
    owned=sorted({v for i in ids for v in faces[i]});kd=KDTree(len(owned))
    for i in owned:kd.insert(coat.data.vertices[i].co,i)
    kd.balance();tree=BVHTree.FromPolygons([v.co for v in coat.data.vertices],[faces[i] for i in ids])
    new=[];weights=[]
    for v in band.data.vertices:
        axis=Vector((v.co.x,v.co.y+.02,0)).normalized();origin=Vector((0,-.02,v.co.z))
        hit=tree.ray_cast(origin+axis*.6,-axis)[0]
        if hit is None:raise ValueError('WAIST353_ATTACH_SUPPORT')
        new.append(hit+axis*.022)
        near=kd.find_n(hit,4);weights.append(helper.blend_weights([rows[i] for _,i,_ in near],[d for _,_,d in near]))
    band.data=band.data.copy();band.vertex_groups.clear()
    for v,p,row in zip(band.data.vertices,new,weights):
        v.co=p
        for name,w in row.items():
            group=band.vertex_groups.get(name) or band.vertex_groups.new(name=name);group.add([v.index],w,'REPLACE')
    band.data.update();rig['waist353_attached']=1;rig.data.pose_position='POSE';bpy.context.scene.frame_set(327);bpy.context.view_layer.update()
    report=dict(changed=True,source_preserved=True,vertices=len(coat.data.vertices),excluded_faces=len(faces)-len(ids),band_vertices=len(new),weight_groups=sorted({n for row in weights for n in row}),scope='Coat-matched band deformation, no actor acceptance.')
    (out/'waist353.json').write_text(json.dumps(report,indent=2)+'\n');return report
