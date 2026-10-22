"""Closed, sewn low-resolution shirt pattern and surface-bound pose transfer.

The original anatomical shirt is a collision/binding donor, not the final cloth.
No downloaded code or arbitrary recipe Python is executed here.
"""
import math
import numpy as np


def barycentric(point, a, b, c):
    e=b-a;f=c-a;q=point-a
    d=float(np.dot(e,e)*np.dot(f,f)-np.dot(e,f)**2)
    if abs(d)<1e-14:raise ValueError('GARMENT_DEGENERATE_BIND_TRIANGLE')
    v=(np.dot(f,f)*np.dot(q,e)-np.dot(e,f)*np.dot(q,f))/d
    w=(np.dot(e,e)*np.dot(q,f)-np.dot(e,f)*np.dot(q,e))/d
    return np.array([1-v-w,v,w])


def transport(vector, old_axis, new_axis):
    """Minimal frame rotation, avoiding sleeve orientation flips at a bent elbow."""
    cross=np.cross(old_axis,new_axis);cos=float(np.dot(old_axis,new_axis))
    if cos<-.999:raise ValueError('GARMENT_FRAME_REVERSAL')
    return vector+np.cross(cross,vector)+np.cross(cross,np.cross(cross,vector))/(1+cos)


def sleeve_axis(origin, elbow, cuff, t):
    """Pose a two-segment rest sleeve without a quadratic overshoot at the elbow.

    Arc distance on the straight rest sleeve determines segment ownership. A
    short quadratic fillet stays INSIDE the elbow control triangle; the old
    curve passed through the elbow and overshot it between samples.
    """
    a=np.linalg.norm(elbow-origin);b=np.linalg.norm(cuff-elbow)
    if min(a,b)<.025:raise ValueError('GARMENT_SHORT_ARM_SEGMENT')
    d=t*(a+b);fillet=min(.035,a*.2,b*.2)
    u=(elbow-origin)/a;v=(cuff-elbow)/b
    if d<a-fillet:return origin+u*d,u
    if d>a+fillet:return elbow+v*(d-a),v
    s=(d-a+fillet)/(2*fillet)
    left=elbow-u*fillet;right=elbow+v*fillet
    center=(1-s)**2*left+2*s*(1-s)*elbow+s*s*right
    tangent=(1-s)*u+s*v;tangent/=np.linalg.norm(tangent)
    return center,tangent


def outward_triangles(points,triangles,leader):
    """Orient an open torso proxy by its measured front/back, not signed volume.

    The319 source has inward winding on both chest and back. Keep the original
    asset unchanged; repair only this collision/binding proxy and verify the vote.
    """
    tri=points[triangles];center=tri.mean(axis=1)
    normal=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0])
    normal/=np.maximum(1e-12,np.linalg.norm(normal,axis=1))[:,None]
    base=0 if leader else .83
    torso=(abs(center[:,0])<.10)&(center[:,2]>base+.13)&(center[:,2]<base+.36)
    if torso.sum()<20:raise ValueError('GARMENT_NORMAL_CONTROL_MISSING')
    mid=float(np.median(center[torso,1]))
    select=torso&(abs(center[:,1]-mid)>.04)
    if select.sum()<20:raise ValueError('GARMENT_NORMAL_CONTROL_AMBIGUOUS')
    vote=float(np.mean(normal[select,1]*np.sign(center[select,1]-mid)))
    if abs(vote)<.5:raise ValueError('GARMENT_NORMAL_CONTROL_INCONSISTENT')
    return (triangles[:,::-1].copy() if vote<0 else triangles.copy()),vote


def pattern(source, cuffs, elbows, leader):
    """Front/back panels, sewn shoulders/sides and connected sleeve tubes."""
    rows=33;cols=33;arm=22;points=[];faces=[];pins=[]
    bottom=.055 if leader else .885
    height=.435;half=.205
    for side in (-1,1):
        for j in range(rows):
            u=j/(rows-1)
            for k in range(cols):
                x=half*(2*k/(cols-1)-1)
                top=height-.025*math.exp(-(x/.075)**4)
                z=bottom+top*u
                band=source[(abs(source[:,2]-z)<.025)&(abs(source[:,0])<.16)]
                if len(band)<8:raise ValueError('GARMENT_TORSO_MEASUREMENT')
                low,high=np.quantile(band[:,1],[.03,.97]);center=(low+high)/2
                depth=(high-low)/2+.025
                if not .045<depth<.24:raise ValueError('GARMENT_TORSO_DEPTH')
                # Ease belongs to the complete pattern, not a local depth patch.
                y=center+side*(.016+depth*math.sqrt(max(0,1-(x/half)**2)))
                points.append((x,y,z))
                pins.append(max(0,1-j/2,1-(rows-1-j)/2))
        off=(0 if side==-1 else rows*cols)
        for j in range(rows-1):
            for k in range(cols-1):
                a=off+j*cols+k;quad=(a,a+1,a+1+cols,a+cols)
                faces.append(quad if side==-1 else quad[::-1])
    def idx(side,j,k):return side*rows*cols+j*cols+k
    # Side seams end at the armhole; shoulders join outside the neckline.
    for k in (0,cols-1):
        for j in range(arm):
            faces.append((idx(0,j,k),idx(1,j,k),idx(1,j+1,k),idx(0,j+1,k)))
    for k in range(cols-1):
        if abs(half*(2*(k+.5)/(cols-1)-1))>.07:
            faces.append((idx(0,rows-1,k),idx(1,rows-1,k),idx(1,rows-1,k+1),idx(0,rows-1,k+1)))
    for sign,k in ((-1,0),(1,cols-1)):
        loop=([idx(0,j,k) for j in range(arm,rows)]+
              [idx(1,j,k) for j in range(rows-1,arm-1,-1)])
        base=np.array([points[i] for i in loop]);origin=base.mean(axis=0)
        cuff=np.asarray(cuffs[str(sign)])
        elbow=np.asarray(elbows[str(sign)])
        axis=cuff-origin;length=np.linalg.norm(axis)
        chain=np.linalg.norm(elbow-origin)+np.linalg.norm(cuff-elbow)
        if not (.06<length<.85 and .18<chain<.95):
            raise ValueError(f'GARMENT_SLEEVE_LENGTH:{length:.5f}:chain={chain:.5f}:origin={origin}:elbow={elbow}:cuff={cuff}')
        direction=(elbow-origin)/np.linalg.norm(elbow-origin)
        vertical=np.array([0.,0.,1.]);v=vertical-direction*np.dot(vertical,direction)
        if np.linalg.norm(v)<.1:v=np.array([0.,1.,0.])
        v/=np.linalg.norm(v);w=np.cross(direction,v)
        previous=loop
        # Preserve the armhole parameterization continuously, rather than joining
        # mismatched ring orders. Wrist opening is left open, with a pinned cuff.
        angles=np.arctan2((base-origin)@w,(base-origin)@v)
        for ring in range(1,25):
            t=ring/24
            center,tangent=sleeve_axis(origin,elbow,cuff,t)
            v=transport(v,direction,tangent);direction=tangent
            v/=np.linalg.norm(v);w=np.cross(tangent,v)
            radius=.078*(1-t)+.043*t
            ids=[]
            for n,a in enumerate(angles):
                target=center+radius*(v*math.cos(a)+w*math.sin(a))
                blend=min(1,t/.25)
                p=(base[n]+center-origin)*(1-blend)+target*blend
                ids.append(len(points));points.append(tuple(p))
                pins.append(min(1,max(.35*math.exp(-((t-.5)/.13)**2),(t-.92)/.08)))
            for n in range(len(loop)):
                m=(n+1)%len(loop);faces.append((previous[n],ids[n],ids[m],previous[m]))
            previous=ids
    return np.asarray(points),faces,np.asarray(pins)


def build(bpy,shirt,leader,diagnostic_dir=None):
    import json
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    original=bpy.context.window.scene;dg=bpy.context.evaluated_depsgraph_get()
    ev=shirt.evaluated_get(dg);src=np.array([v.co[:] for v in ev.data.vertices])
    ev.data.calc_loop_triangles();tri=np.array([tuple(t.vertices) for t in ev.data.loop_triangles])
    tri,normal_vote=outward_triangles(src,tri,leader)
    print('GARMENT_PROXY_NORMAL_VOTE',normal_vote,flush=True)
    tree=BVHTree.FromPolygons(src,tri,all_triangles=True)
    cuff_ids=json.loads(shirt['cuff_indices'])
    cuffs={s:src[ids].mean(axis=0) for s,ids in cuff_ids.items()}
    elbows={}
    actor=shirt.parent.parent
    prefix='318 endpoint-bound leader sleeve' if leader else '297 crowd sleeve'
    for ob in actor.children_recursive:
        if not ob.name.startswith(prefix):continue
        evaluated=ob.evaluated_get(dg)
        # These hidden legacy sleeves are geometry caches in the original actor
        # coordinates.319 built the visible shirt from their raw evaluated points;
        # their stale object inverses are not valid world-space contact owners.
        pts=np.array([tuple(v.co) for v in evaluated.data.vertices])
        if len(pts)!=312:raise ValueError('GARMENT_SLEEVE_DONOR_TOPOLOGY')
        a=pts[:24].mean(axis=0);b=pts[144:168].mean(axis=0)
        elbows[str(-1 if a[0]<0 else 1)]=b
    if set(elbows)!={'-1','1'}:raise ValueError('GARMENT_ELBOW_OWNERS')
    print('GARMENT_MEASUREMENTS',json.dumps({'leader':leader,'cuffs':{k:list(v) for k,v in cuffs.items()},'elbows':{k:list(v) for k,v in elbows.items()}}),flush=True)
    for side,p in elbows.items():
        if tree.find_nearest(Vector(p))[3]>.09:raise ValueError('GARMENT_ELBOW_BIND_DISTANCE')
    start,faces,pins=pattern(src,cuffs,elbows,leader)
    if diagnostic_dir is not None:
        np.savez_compressed(diagnostic_dir/('leader-pattern.npz' if leader else 'crowd-pattern.npz'),
                            source=src,triangles=tri,start=start,faces=np.asarray(faces),pins=pins)
    temporary=bpy.data.scenes.new('MF sewn shirt drape proof');objects=[];meshes=[]
    def new(name,vertices,polygons,scene):
        data=bpy.data.meshes.new(name);data.from_pydata(vertices,[],polygons);data.update()
        ob=bpy.data.objects.new(name,data);scene.collection.objects.link(ob);return ob
    try:
        bpy.context.window.scene=temporary;temporary.render.fps=24
        body=new('MF shirt collision donor',src,tri,temporary);objects.append(body);meshes.append(body.data)
        body.modifiers.new('Cloth body support','COLLISION');body.collision.thickness_outer=.002
        cloth=new('MF sewn shirt simulation',start,faces,temporary);objects.append(cloth);meshes.append(cloth.data)
        # Normalize face orientation before evaluating cloth collisions.
        import bmesh
        bm=bmesh.new();bm.from_mesh(cloth.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(cloth.data);bm.free()
        group=cloth.vertex_groups.new(name='Shoulder waist cuff support')
        for i,w in enumerate(pins):group.add([i],float(w),'REPLACE')
        mod=cloth.modifiers.new('Sewn garment gravity settle','CLOTH');s=mod.settings
        s.quality=10;s.mass=.28;s.tension_stiffness=35;s.compression_stiffness=25
        s.shear_stiffness=20;s.bending_stiffness=.4;s.air_damping=6
        s.vertex_group_mass=group.name;s.pin_stiffness=1;s.time_scale=.6
        mod.collision_settings.distance_min=.003;mod.collision_settings.use_self_collision=True
        mod.collision_settings.self_distance_min=.002
        mod.point_cache.frame_start=1;mod.point_cache.frame_end=40
        for f in range(1,41):
            temporary.frame_set(f);bpy.context.view_layer.update()
            evaluated=cloth.evaluated_get(bpy.context.evaluated_depsgraph_get())
        final=np.array([v.co[:] for v in evaluated.data.vertices])
        delta=np.linalg.norm(final-start,axis=1)
        if diagnostic_dir is not None:
            np.savez_compressed(diagnostic_dir/('leader-settle.npz' if leader else 'crowd-settle.npz'),
                                start=start,final=final,faces=np.asarray(faces),pins=pins,displacement=delta)
        if not np.isfinite(final).all() or delta.max()>.09:
            worst=np.argsort(delta)[-5:]
            print('GARMENT_DRAPE_FAILURE',json.dumps({'indices':worst.tolist(),'start':start[worst].tolist(),'end':final[worst].tolist()}),flush=True)
            raise ValueError(f'GARMENT_DRAPE_DISPLACEMENT:{float(delta.max()):.6f}')
        faces=[tuple(p.vertices) for p in cloth.data.polygons]
    finally:
        bpy.context.window.scene=original
        for ob in objects:bpy.data.objects.remove(ob,do_unlink=True)
        bpy.data.scenes.remove(temporary)
        for data in meshes:
            if not data.users:bpy.data.meshes.remove(data)
    # Barycentric attachment to the original animated donor, including a local
    # normal offset. This preserves the existing pose animation without baking
    # a world-space correction into every bent sleeve.
    ids=[];weights=[];offsets=[]
    for p in final:
        hit,normal,index,distance=tree.find_nearest(Vector(p))
        if hit is None or distance>.10:raise ValueError('GARMENT_BIND_DISTANCE')
        ids.append(tri[index]);weights.append(barycentric(np.array(hit),*src[tri[index]]))
        offsets.append(float(np.dot(p-np.array(hit),np.array(normal))))
    ids=np.array(ids);weights=np.array(weights);offsets=np.array(offsets)
    def transfer(coords):
        triangles=coords[ids];center=(triangles*weights[:,:,None]).sum(axis=1)
        normal=np.cross(triangles[:,1]-triangles[:,0],triangles[:,2]-triangles[:,0])
        lengths=np.linalg.norm(normal,axis=1)
        if np.min(lengths)<1e-12:raise ValueError('GARMENT_BIND_COLLAPSED')
        return center+normal/lengths[:,None]*offsets[:,None]
    result=new('MF sewn chola complete upper',final,faces,original)
    result.parent=shirt.parent;result.matrix_local=shirt.matrix_local.copy()
    result.data.materials.append(shirt.data.materials[0])
    for p in result.data.polygons:p.use_smooth=True
    blocks=shirt.data.shape_keys.key_blocks if shirt.data.shape_keys else []
    for block in blocks:
        key=result.shape_key_add(name=block.name)
        coords=np.array([p.co[:] for p in block.data]);posed=transfer(coords)
        key.data.foreach_set('co',posed.ravel());key.value=block.value
    if blocks and shirt.data.shape_keys.animation_data:
        result.data.shape_keys.animation_data_create()
        result.data.shape_keys.animation_data.action=shirt.data.shape_keys.animation_data.action.copy()
    sub=result.modifiers.new('Tailored cloth subdivision','SUBSURF');sub.levels=1;sub.render_levels=1
    solid=result.modifiers.new('Woven cloth thickness','SOLIDIFY');solid.thickness=.0015
    shirt.hide_render=True;shirt.hide_viewport=True
    return result,{'method':'complete sewn panels and sleeves, gravity settle, barycentric pose transfer',
                   'vertices':len(final),'cached_poses':len(blocks) or 1,'frames':40,
                   'maximum_displacement':float(delta.max()),'qualification':'Static construction proof; animation and appearance require review'}
