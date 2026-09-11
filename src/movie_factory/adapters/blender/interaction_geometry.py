"""Independent evaluated surface and ownership inspection for 3D-05 v2.

Triangle-centroid cover radii give conservative distance lower bounds; BVH
triangle overlap and closed-surface parity tests supplement distance sampling.
No whole-grip sphere exclusion. Region 1=handle, 2=guard, 3=blade.
"""
import math
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree


def ownership(sword):
    evaluated=sword.evaluated_get(bpy.context.evaluated_depsgraph_get())
    return [{"name":c.name,"type":c.type,"muted":c.mute,"influence":float(c.influence),
             "valid":c.is_valid,"target":getattr(getattr(c,'target',None),'name',None),
             "bone":getattr(c,'subtarget','')} for c in evaluated.constraints]


def _sword_surface():
    points,triangles,regions=[],[],[]
    deps=bpy.context.evaluated_depsgraph_get()
    for obj in bpy.context.scene.objects:
        if obj.type!='MESH' or obj.get('mf_entity')!='sword_01':continue
        evaluated=obj.evaluated_get(deps);data=evaluated.to_mesh()
        try:
            attr=data.attributes.get('mf_sword_region')
            if attr is None:raise ValueError('Sword surface missing explicit face regions')
            offset=len(points);points.extend(evaluated.matrix_world@v.co for v in data.vertices)
            data.calc_loop_triangles()
            for tri in data.loop_triangles:
                region=int(attr.data[tri.polygon_index].value)
                if region not in (1,2,3):raise ValueError('Unclassified sword triangle')
                triangles.append(tuple(offset+i for i in tri.vertices));regions.append(region)
        finally:evaluated.to_mesh_clear()
    if set(regions)!={1,2,3}:raise ValueError('Sword requires handle, guard and blade surfaces')
    return points,triangles,regions


def _covers(a,b,c,maximum_edge=.03):
    stack=[(a,b,c)]
    while stack:
        a,b,c=stack.pop()
        lengths=[(a-b).length_squared,(b-c).length_squared,(c-a).length_squared]
        if max(lengths)<=maximum_edge**2:
            center=(a+b+c)/3
            yield center,max((center-p).length for p in (a,b,c))
        else:
            i=lengths.index(max(lengths))
            if i==0:
                m=(a+b)/2;stack.extend(((a,m,c),(m,b,c)))
            elif i==1:
                m=(b+c)/2;stack.extend(((a,b,m),(a,m,c)))
            else:
                m=(c+a)/2;stack.extend(((a,b,m),(m,b,c)))


def _inside(tree,point):
    # Majority vote reduces edge/vertex ray degeneracy. Mesh closure is an
    # admitted-fixture assumption, not a claim about arbitrary open meshes.
    votes=[]
    for direction in (Vector((1,.371,.113)).normalized(),Vector((.173,1,.419)).normalized(),Vector((.293,.127,1)).normalized()):
        origin=point.copy();count=0
        for _ in range(128):
            hit=tree.ray_cast(origin,direction)
            if hit[0] is None:break
            count+=1;origin=hit[0]+direction*1e-6
        else:raise ValueError('Containment ray did not terminate')
        votes.append(count%2)
    return sum(votes)>=2


def _nearest(tree,point):
    hit=tree.find_nearest(point)
    if hit is None or hit[0] is None:raise ValueError('Missing surface nearest point')
    return hit


def inspect(mesh,character):
    points,triangles,regions=proxy_surface()
    mesh.data.calc_loop_triangles()
    body_tri=[tuple(t.vertices) for t in mesh.data.loop_triangles]
    family={}
    for vertex in mesh.data.vertices:
        weights=sorted(vertex.groups,key=lambda g:g.weight,reverse=True)
        name=mesh.vertex_groups[weights[0].group].name if weights else ''
        family[vertex.index]='hand' if name.startswith('RightHand') else 'head' if name.startswith('Head') else 'body'
    body_regions=['hand' if all(family[i]=='hand' for i in tri) else 'head' if any(family[i]=='head' for i in tri) else 'body' for tri in body_tri]
    whole=BVHTree.FromPolygons(character,body_tri,all_triangles=True)
    protected=BVHTree.FromPolygons(character,[tri for tri,kind in zip(body_tri,body_regions) if kind!='hand'],all_triangles=True)
    head=BVHTree.FromPolygons(character,[tri for tri,kind in zip(body_tri,body_regions) if kind=='head'],all_triangles=True)
    prop=BVHTree.FromPolygons(points,triangles,all_triangles=True)
    forbidden_overlaps=[(a,b) for a,b in prop.overlap(whole) if not(regions[a]==1 and body_regions[b]=='hand') and triangles_intersect(tuple(points[i] for i in triangles[a]),tuple(character[i] for i in body_tri[b]))]
    lower={region:math.inf for region in (1,2,3)};head_lower=math.inf;hand_nonhandle_lower=math.inf
    sample_count=0;contained=0;worst_radius=0;head_witness=None;head_upper=math.inf
    hand_tri=[tri for tri,kind in zip(body_tri,body_regions) if kind=='hand']
    hand=BVHTree.FromPolygons(character,hand_tri,all_triangles=True)
    for tri,region in zip(triangles,regions):
        for point,radius in _covers(*(points[i] for i in tri)):
            sample_count+=1;worst_radius=max(worst_radius,radius)
            lower[region]=min(lower[region],max(0,_nearest(protected,point)[3]-radius))
            head_hit=_nearest(head,point)
            head_lower=min(head_lower,max(0,head_hit[3]-radius))
            if head_hit[3]<head_upper:
                head_upper=head_hit[3];head_witness={"sword_point":list(point),"head_point":list(head_hit[0]),"sword_region":region}
            if region!=1:hand_nonhandle_lower=min(hand_nonhandle_lower,max(0,_nearest(hand,point)[3]-radius))
    # Test vertices on both sides for wholly contained components, which have
    # no surface intersection. Nearest normal is only a prefilter for parity.
    vertex_regions={i:region for tri,region in zip(triangles,regions) for i in tri}
    for index,point in enumerate(points):
        hit=_nearest(whole,point)
        intentional=vertex_regions[index]==1 and body_regions[hit[2]]=='hand'
        if (point-hit[0]).dot(hit[1]) < -1e-5 and not intentional and _inside(whole,point):contained+=1
    for i,point in enumerate(character):
        hit=_nearest(prop,point)
        if (point-hit[0]).dot(hit[1]) < -1e-5 and not(family[i]=='hand' and regions[hit[2]]==1) and _inside(prop,point):contained+=1
    return {'surface_basis':'qualified_convex_region_proxies_enclosing_render_mesh','protected_body_clearance_lower_bound_m':min(lower.values()),
            'head_clearance_lower_bound_m':head_lower,'head_nearest_sample_m':head_upper,'head_witness':head_witness,'nonhandle_hand_clearance_lower_bound_m':hand_nonhandle_lower,
            'forbidden_triangle_intersections':len(forbidden_overlaps),'forbidden_contained_vertices':contained,
            'surface_sample_count':sample_count,'maximum_surface_cover_radius_m':worst_radius,
            'region_triangle_counts':{str(k):regions.count(k) for k in (1,2,3)},
            'region_body_clearance_lower_bound_m':{str(k):v for k,v in lower.items()},
            'intersection_pairs':[[a,b] for a,b in forbidden_overlaps[:20]],'intersection_region_pairs':[[regions[a],body_regions[b]] for a,b in forbidden_overlaps[:20]]}


def triangles_intersect(first,second,eps=1e-8):
    """Narrow phase after BVH overlap; reject overlapping AABBs alone."""
    def segment_triangle(p,q,tri):
        a,b,c=tri;d=q-p;e1=b-a;e2=c-a;h=d.cross(e2);det=e1.dot(h)
        if abs(det)<eps:return False
        inv=1/det;s=p-a;u=s.dot(h)*inv
        if u < -eps or u > 1+eps:return False
        v=d.dot(s.cross(e1))*inv;t=e2.dot(s.cross(e1))*inv
        return v>=-eps and u+v<=1+eps and -eps<=t<=1+eps
    for tri,other in ((first,second),(second,first)):
        for i in range(3):
            if segment_triangle(tri[i],tri[(i+1)%3],other):return True
    normal=(first[1]-first[0]).cross(first[2]-first[0])
    if normal.length<eps:raise ValueError('Degenerate collision triangle')
    normal.normalize()
    if any(abs((p-first[0]).dot(normal))>eps for p in second):return False
    drop=max(range(3),key=lambda i:abs(normal[i]));axes=[i for i in range(3) if i!=drop]
    a=[tuple(p[i] for i in axes) for p in first];b=[tuple(p[i] for i in axes) for p in second]
    def orient(p,q,r):return (q[0]-p[0])*(r[1]-p[1])-(q[1]-p[1])*(r[0]-p[0])
    def inside(p,tri):
        signs=[orient(tri[i],tri[(i+1)%3],p) for i in range(3)]
        return min(signs)>=-eps or max(signs)<=eps
    if any(inside(p,b) for p in a) or any(inside(p,a) for p in b):return True
    for i in range(3):
        for j in range(3):
            p,q=a[i],a[(i+1)%3];r,s=b[j],b[(j+1)%3]
            if orient(p,q,r)*orient(p,q,s)<-eps and orient(r,s,p)*orient(r,s,q)<-eps:return True
    return False


def selftest():
    def tri(v):return tuple(Vector(p) for p in v)
    a=tri([(0,0,0),(2,0,0),(0,2,0)])
    separated=tri([(1.5,1.5,0),(3,1.5,0),(1.5,3,0)])
    crossing=tri([(.5,.5,-1),(.5,.5,1),(3,.5,0)])
    contained=tri([(.2,.2,0),(.4,.2,0),(.2,.4,0)])
    tests={'aabb_overlap_is_not_collision':not triangles_intersect(a,separated),'between_vertices_crossing':triangles_intersect(a,crossing),'coplanar_containment':triangles_intersect(a,contained)}
    return {'passed':all(tests.values()),'checks':tests}


def closed_surface_topology(points,faces):
    from collections import Counter
    vertices={};ids=[]
    for p in points:
        key=tuple(round(float(v),6) for v in p)
        if key not in vertices:vertices[key]=len(vertices)
        ids.append(vertices[key])
    edges=Counter()
    for face in faces:
        for a,b in zip(face,face[1:]+face[:1]):
            a,b=ids[a],ids[b]
            if a!=b:edges[tuple(sorted((a,b)))]+=1
    boundary=sum(n==1 for n in edges.values());nonmanifold=sum(n!=2 for n in edges.values())
    return {'closed_after_micrometre_weld':bool(edges) and nonmanifold==0,'boundary_edges':boundary,'nonmanifold_edges':nonmanifold,'welded_vertices':len(vertices)}


def build_region_proxies(obj):
    """Close each admitted convex section conservatively; never alter render mesh."""
    import bmesh,json
    attr=obj.data.attributes.get('mf_sword_region')
    if attr is None:raise ValueError('Proxy requires explicit sword regions')
    result={}
    for region in sorted({int(item.value) for item in attr.data}):
        indices={i for p in obj.data.polygons if attr.data[p.index].value==region for i in p.vertices}
        coords=sorted({tuple(float(v) for v in obj.data.vertices[i].co) for i in indices})
        bm=bmesh.new()
        try:
            verts=[bm.verts.new(co) for co in coords]
            bmesh.ops.convex_hull(bm,input=verts,use_existing_faces=False)
            bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
            bmesh.ops.triangulate(bm,faces=list(bm.faces))
            bm.verts.index_update();bm.faces.index_update();bm.normal_update()
            used=sorted({v for f in bm.faces for v in f.verts},key=lambda v:tuple(v.co))
            lookup={v:i for i,v in enumerate(used)}
            points=[v.co.copy() for v in used];faces=sorted(tuple(lookup[v] for v in f.verts) for f in bm.faces)
            topology=closed_surface_topology(points,faces)
            if not topology['closed_after_micrometre_weld']:raise ValueError('Region proxy is not closed')
            center=sum(points,Vector())/len(points)
            planes=[]
            for face in faces:
                a,b,c=[points[i] for i in face];normal=(b-a).cross(c-a).normalized()
                if (center-a).dot(normal)>0:normal=-normal
                planes.append((a,normal))
            if any((Vector(p)-a).dot(n)>1e-5 for p in coords for a,n in planes):raise ValueError('Proxy does not enclose source section')
            result[str(region)]={'points':[list(p) for p in points],'triangles':[list(f) for f in faces],'topology':topology,'encloses_render_vertices':True}
        finally:bm.free()
    obj['mf_region_collision_proxies_json']=json.dumps(result,sort_keys=True)


def proxy_surface():
    import json
    points,triangles,regions=[],[],[]
    for obj in bpy.context.scene.objects:
        if obj.type!='MESH' or obj.get('mf_entity')!='sword_01':continue
        data=obj.get('mf_region_collision_proxies_json')
        if not data:raise ValueError('Missing qualified section collision proxies')
        for key,part in sorted(json.loads(data).items()):
            if not part['topology']['closed_after_micrometre_weld'] or not part['encloses_render_vertices']:raise ValueError('Unqualified collision proxy')
            offset=len(points);points.extend(obj.matrix_world@Vector(p) for p in part['points'])
            triangles.extend(tuple(offset+i for i in tri) for tri in part['triangles']);regions.extend([int(key)]*len(part['triangles']))
    return points,triangles,regions


def penetration_proxies():
    points,triangles,regions=proxy_surface();result=[]
    for region in sorted(set(regions)):
        faces=[tri for tri,r in zip(triangles,regions) if r==region]
        # Separate objects in a fault control can share a label; this function
        # is used for the admitted three convex sections during hand sampling.
        tree=BVHTree.FromPolygons(points,faces,all_triangles=True)
        ids={i for tri in faces for i in tri};coords=[points[i] for i in ids]
        result.append((tree,Vector(tuple(min(p[a] for p in coords) for a in range(3))),Vector(tuple(max(p[a] for p in coords) for a in range(3)))))
    return result


def proxy_penetration(point,proxies):
    values=[]
    for tree,low,high in proxies:
        if all(low[a]-1e-7<=point[a]<=high[a]+1e-7 for a in range(3)) and _inside(tree,point):values.append(_nearest(tree,point)[3])
    return max(values,default=0.0)
