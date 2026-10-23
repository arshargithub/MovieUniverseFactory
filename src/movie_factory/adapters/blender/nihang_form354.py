"""Fixed local form reconstruction on integrated353; no recipe code or assets."""
import json,math
import numpy as np

def beard_path(root,eye,index,steps=14):
    r=np.asarray(root,dtype=float);x=r[0];a=min(1,abs(x)/.076)
    phase=index*2.399963;group=round(x/.009)
    # Rounded broad lower envelope; cheek roots flow down jaw before releasing.
    end=eye-.181+.029*a*a+.009*math.sin(group*1.7)+.009*math.sin(phase)
    length=max(.020,r[2]-end)
    pts=[]
    for j in range(steps):
        t=j/(steps-1);u=t*t*(3-2*t);wave=math.sin(math.pi*t)
        pts.append(r+np.array((-.12*x*u+.0055*math.sin(group+8*t)*wave,
          -.020*u-.006*math.sin(math.pi*t)+.0035*math.sin(group+13*t)*wave,
          -length*t+.0018*math.sin(phase+9*t)*wave)))
    return np.array(pts)

def moustache_path(root,index,steps=10):
    r=np.asarray(root,dtype=float);side=1 if r[0]>=0 else -1;a=min(1,abs(r[0])/.041)
    # Short overlapping upper-lip flow, not an outward pointed wing.
    return np.array([r+np.array((side*(.007-.004*a)*t,
        -.0035*math.sin(math.pi*t),-(.007+.009*a)*t-.005*(1-a)))
        for t in np.linspace(0,1,steps)])

def run(bpy,out):
    rig=bpy.data.objects['MF coherent Nihang rig'];body=bpy.data.objects['MF coherent Nihang body']
    if not rig.get('gesture353') or rig.get('form354'):raise ValueError('FORM354_PARENT')
    ob=bpy.data.objects['MF347 integrated beard and moustache'];ob.data=ob.data.copy()
    eye=rig.data.bones['eye.L'].head_local.z;beard=0;mustache=0
    for i,s in enumerate(ob.data.splines):
        root=s.points[0].co[:3]
        if len(s.points)==14:pts=beard_path(root,eye,i,len(s.points));beard+=1
        else:pts=moustache_path(root,i,len(s.points));mustache+=1
        for j,(p,co) in enumerate(zip(s.points,pts)):
            p.co=(*co,1);t=j/(len(pts)-1);p.radius=max(.025,(1-t)**.65)*(.76+.24*(.5+.5*math.sin(i*1.37)))
    ob.data.bevel_depth=.00023
    # Record all visible attachments: hidden donor cards must not compete.
    inventory=[dict(name=o.name,type=o.type,hidden=o.hide_render,dimensions=list(o.dimensions),modifiers=[m.type for m in o.modifiers]) for o in rig.children_recursive]
    pad=bpy.data.objects['fitted saddle blanket292']
    report=dict(changed=True,source_preserved=True,beard_curves=beard,moustache_curves=mustache,eye=eye,attachments=inventory,
      pad=dict(matrix=[list(row) for row in pad.matrix_world],bounds=[list(p) for p in pad.bound_box],vertices=len(pad.data.vertices),modifiers=[dict(name=m.name,type=m.type) for m in pad.modifiers]),
      limitation='Form proof only; face, costume, tack and full-speed action remain unqualified.')
    report['sash']=rebuild_sash(bpy,rig)
    rig['form354']=1;bpy.context.view_layer.update()
    (out/'form354.json').write_text(json.dumps(report,indent=2)+'\n');return report

def rebuild_sash(bpy,rig):
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    from mathutils.kdtree import KDTree
    coat=bpy.data.objects['MF coherent coat'];sash=bpy.data.objects['MF coherent shoulder sash']
    previous=rig.data.pose_position;rig.data.pose_position='REST';bpy.context.view_layer.update()
    # Base garment and its weights share topology; no opposing solid-shell query.
    pts=[v.co.copy() for v in coat.data.vertices]
    weights=[[(coat.vertex_groups[g.group].name,g.weight) for g in v.groups] for v in coat.data.vertices]
    allowed=[abs(v.x)<.24 and sum(w for n,w in weights[i] if n.startswith(('lowerarm','hand','finger')))<.1 for i,v in enumerate(pts)]
    faces=[tuple(p.vertices) for p in coat.data.polygons if all(allowed[i] for i in p.vertices)]
    tree=BVHTree.FromPolygons(pts,faces);kd=KDTree(sum(allowed))
    for i,p in enumerate(pts):
        if allowed[i]:kd.insert(p,i)
    kd.balance();lo=min(v.co.z for v in sash.data.vertices);hi=max(v.co.z for v in sash.data.vertices)
    shoulder=tree.ray_cast(Vector((-.16,0,hi+.4)),Vector((0,0,-1)))[0]
    if shoulder is None:raise ValueError('FORM354_SASH_TOP_ENVELOPE')
    hi=min(hi,shoulder.z-.025)
    cols=9;rows=89;points=[];ws=[]
    for j in range(rows):
        if j<=40:t=j/40;side=-1;x=.13-.29*t;z=lo+(hi-lo)*t
        elif j>=48:t=(88-j)/40;side=1;x=.13-.29*t;z=lo+(hi-lo)*t
        else:t=(j-40)/8;side=0;x=-.16;z=hi
        for k in range(cols):
            off=(k/(cols-1)-.5)*.066
            if side:
                xx=x+off*.88;zz=z+off*.47
                cap=tree.ray_cast(Vector((xx,0,hi+.4)),Vector((0,0,-1)))[0]
                if cap is not None:zz=min(zz,cap.z-.028)
                origin=Vector((xx,side*.7,zz));hit,n,_,_=tree.ray_cast(origin,Vector((0,-side,0)))
                if hit is None:raise ValueError(f'FORM354_SASH_SUPPORT:{j}:{k}')
                p=hit+Vector((0,side*(.014+.0015*math.cos(off*65)),0))
            else:
                front=points[40*cols+k];back=tree.ray_cast(Vector((x+off,.7,hi)),Vector((0,-1,0)))[0]
                if back is None:back=Vector((x+off,.08,hi))
                y=front.y*(1-t)+back.y*t
                hit,n,_,_=tree.ray_cast(Vector((x+off,y,hi+.3)),Vector((0,0,-1)))
                if hit is None:raise ValueError('FORM354_SASH_SHOULDER')
                p=hit+Vector((0,0,.014))
            points.append(p);_,idx,_=kd.find(p);ws.append(weights[idx])
    data=bpy.data.meshes.new('354 continuous supported sash');polys=[]
    for j in range(rows-1):
        for k in range(cols-1):a=j*cols+k;polys.append((a,a+1,a+1+cols,a+cols))
    data.from_pydata(points,[],polys);data.update();mat=sash.data.materials[0].copy();data.materials.append(mat)
    sash.data=data
    for m in list(sash.modifiers):sash.modifiers.remove(m)
    sash.vertex_groups.clear()
    for i,weight in enumerate(ws):
        total=sum(w for n,w in weight)
        for n,w in weight:
            group=sash.vertex_groups.get(n) or sash.vertex_groups.new(name=n);group.add([i],w/total,'REPLACE')
    arm=sash.modifiers.new('354 same garment deformation owner','ARMATURE');arm.object=rig;arm.use_deform_preserve_volume=True
    sub=sash.modifiers.new('354 continuous woven edge','SUBSURF');sub.levels=2;sub.render_levels=2
    solid=sash.modifiers.new('354 turned cloth thickness','SOLIDIFY');solid.thickness=.002;solid.offset=0
    for p in data.polygons:p.use_smooth=True
    rig.data.pose_position=previous;bpy.context.view_layer.update()
    return dict(vertices=len(points),owned_support_faces=len(faces),height=[lo,hi],method='Continuous semantic torso/shoulder rays with inherited garment weights; no nearest-surface postprojection.',scope='Actual posed clearance still needs visible proof.')
