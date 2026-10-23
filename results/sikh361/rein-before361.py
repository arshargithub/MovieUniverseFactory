"""Consume anatomical bit-ring anchors in existing real hand-owned reins."""
import json,math,importlib.util,hashlib,heapq
from pathlib import Path

def influence(u):
    t=max(0.,min(1.,u/.75))
    return 1-t*t*(3-2*t)

def seed_weights(u):
    """Zero end displacement; outward route biased toward the horse, not hand."""
    return math.sin(math.pi*u)*(1-u), math.sin(math.pi*u)

def exterior_path(points, bvh, margin=.018):
    """Tension-relaxed route against the actual evaluated skin, endpoints pinned.

    This is shot-authored contact, not a rope simulation. Dense final sampling
    below explicitly rejects any remaining segment penetration.
    """
    p=[v.copy() for v in points]
    for _ in range(90):
        q=[v.copy() for v in p]
        for j in range(1,len(p)-1):
            v=p[j]*.55+(p[j-1]+p[j+1])*.225
            hit,n,_,dist=bvh.find_nearest(v)
            if hit is not None:
                signed=(v-hit).dot(n)
                if signed<margin:v=hit+n*margin
            q[j]=v
        p=q
    return p

def visible(bvh,a,b,margin=.006):
    d=b-a;length=d.length
    if length<1e-8:return True
    hit,_,_,distance=bvh.ray_cast(a,d.normalized(),length)
    if hit is not None and distance<length-1e-6:return False
    for u in (.25,.5,.75):
        v=a.lerp(b,u);p,n,_,_=bvh.find_nearest(v)
        if (v-p).dot(n)<margin:return False
    return True

def surface_route(target,hand,bvh,verts,normals,edges,cache):
    """Shortest exterior route on offset skin connectivity, then safe shortcuts.

    Local projection alone can jump across a neck. Connected skin edges and
    visibility tests preserve an exterior path between the two contact owners.
    """
    nodes=[v+n*.05 for v,n in zip(verts,normals)];n=len(nodes)
    direct=(target-hand).length
    active={i for i,v in enumerate(nodes) if (v-target).length+(v-hand).length<direct*2.8}
    nodes.extend((target,hand));adj={i:[] for i in active|{n,n+1}}
    def connect(i,j):
        a,b=nodes[i],nodes[j]
        if not visible(bvh,a,b):return
        # Discourage an under-throat detour when the rein can pass beside/above.
        penalty=1+max(0.,min(target.z,hand.z)-min(a.z,b.z))*3
        cost=(a-b).length*penalty;adj[i].append((j,cost));adj[j].append((i,cost))
    if cache:
        # Same actual horse surface in this frame, second rein. Retain graph
        # vertices required by either side; endpoint edges never enter cache.
        adj={i:list(row) for i,row in cache['adj'].items()};active=set(adj)
        adj[n]=[];adj[n+1]=[]
    else:
        for a,b in edges:
            if a in active and b in active:connect(a,b)
        cache['adj']={i:list(row) for i,row in adj.items() if i<n}
    for i in (n,n+1):
        for j in sorted(active,key=lambda j:(nodes[j]-nodes[i]).length_squared)[:100]:connect(i,j)
    connect(n,n+1)
    dist={n:0.};previous={};queue=[(0.,n)]
    while queue:
        cost,i=heapq.heappop(queue)
        if cost!=dist.get(i):continue
        if i==n+1:break
        for j,w in adj[i]:
            v=cost+w
            if v<dist.get(j,float('inf')):dist[j]=v;previous[j]=i;heapq.heappush(queue,(v,j))
    if n+1 not in dist:raise ValueError('REIN358_NO_EXTERIOR_ROUTE')
    ids=[n+1]
    while ids[-1]!=n:ids.append(previous[ids[-1]])
    path=[nodes[i] for i in reversed(ids)]
    # Pull taut only through visible shortcuts; never tunnel through the skin.
    simple=[path[0]];i=0
    while i<len(path)-1:
        j=len(path)-1
        while j>i+1 and not visible(bvh,path[i],path[j],.012):j-=1
        simple.append(path[j]);i=j
    # Conservative corner rounding, retaining only collision-free replacements.
    for _ in range(3):
        smooth=[simple[0]]
        for a,b,c in zip(simple,simple[1:],simple[2:]):
            q=a.lerp(b,.8);s=b.lerp(c,.2)
            if visible(bvh,smooth[-1],q,.01) and visible(bvh,q,s,.01):smooth.extend((q,s))
            else:smooth.append(b)
        smooth.append(simple[-1]);simple=smooth
    # Preserve every visible-path corner. Uniform arclength sampling can
    # shortcut across a corner and penetrate the mesh it was avoiding.
    lengths=[(a-b).length for a,b in zip(simple,simple[1:])]
    if len(lengths)>128:raise ValueError('REIN358_ROUTE_COMPLEXITY')
    spare=128-len(lengths);total=sum(lengths)
    quotas=[spare*x/total for x in lengths];counts=[1+int(x) for x in quotas]
    for i in sorted(range(len(counts)),key=lambda i:quotas[i]-int(quotas[i]),reverse=True)[:128-sum(counts)]:counts[i]+=1
    result=[]
    for a,b,count in zip(simple,simple[1:],counts):result.extend(a.lerp(b,k/count) for k in range(count))
    result.append(simple[-1])
    result[0]=target.copy();result[-1]=hand.copy()
    return result

def run(bpy,out):
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    spec=importlib.util.spec_from_file_location('tack354',Path(__file__).with_name('nihang_tack354.py'));h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
    rig=bpy.data.objects['horse.rig'];scene=bpy.context.scene
    if not rig.get('tack358') or rig.get('rein358'):raise ValueError('REIN358_PARENT')
    anchors=json.loads(rig['tack358_anchors']);reins=sorted([o for o in bpy.data.objects if o.name.startswith('leader supported rein292')],key=lambda o:o.name)
    if len(reins)!=2:raise ValueError('REIN358_PAIR')
    # Preserve every existing non-rein action byte. Temporarily remove the two
    # action datablocks only from the signature selection, never from the scene.
    excluded={o.data.animation_data.action.name for o in reins if o.data.animation_data and o.data.animation_data.action}
    def protected_signature():
        rows=[]
        for a in bpy.data.actions:
            if a.name in excluded:continue
            curves=[]
            if hasattr(a,'fcurves'):
                try:curves=list(a.fcurves)
                except RuntimeError:pass
            if not curves:
                for layer in a.layers:
                    for strip in layer.strips:
                        for bag in getattr(strip,'channelbags',[]):curves.extend(bag.fcurves)
            rows.append((a.name,[(fc.data_path,fc.array_index,[(tuple(k.co),k.interpolation) for k in fc.keyframe_points]) for fc in curves]))
        return hashlib.sha256(json.dumps(rows,sort_keys=True).encode()).hexdigest()
    sig=protected_signature();captured={};frame=scene.frame_current
    invrest=rig.data.bones['DEF-head'].matrix_local.inverted()
    def skin():
        evaluated=bpy.data.objects['horse'].evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=evaluated.to_mesh()
        verts=[evaluated.matrix_world@v.co for v in mesh.vertices]
        nm=evaluated.matrix_world.to_3x3().inverted().transposed();normals=[(nm@v.normal).normalized() for v in mesh.vertices]
        edges=[tuple(e.vertices) for e in mesh.edges]
        bvh=BVHTree.FromPolygons(verts,[list(p.vertices) for p in mesh.polygons]);evaluated.to_mesh_clear()
        return bvh,verts,normals,edges
    # Choose ONE fixed rear-half ring station per side against the entire
    # motion. It remains on the actual ring, not a per-frame floating offset.
    angles=[0,-math.pi/6,math.pi/6,-math.pi/3,math.pi/3]
    scores={label:[float('inf')]*len(angles) for label in ('R','L')}
    for f in range(252,442):
        scene.frame_set(f);bpy.context.view_layer.update();bvh,_,_,_=skin()
        transform=rig.matrix_world@rig.pose.bones['DEF-head'].matrix@invrest
        for label in scores:
            for j,a in enumerate(angles):
                v=transform@(Vector(anchors[label])+Vector((0,.021*math.cos(a),.021*math.sin(a))))
                hit,n,_,_=bvh.find_nearest(v);scores[label][j]=min(scores[label][j],(v-hit).dot(n))
    stations={}
    for label,values in scores.items():
        valid=[i for i,v in enumerate(values) if v>.007]
        if not valid:raise ValueError('REIN358_RING_CONTACT_CLEARANCE:'+str((label,values)))
        stations[label]=angles[valid[0]]
    for f in range(252,442):
        scene.frame_set(f);bpy.context.view_layer.update()
        captured[f]=[]
        bvh,verts,normals,edges=skin();cache={}
        for label,obj in zip(('R','L'),reins):
            # Ring's rear rim is the actual leather attachment station.
            a=stations[label];anchor=Vector(anchors[label])+Vector((0,.021*math.cos(a),.021*math.sin(a)))
            target=rig.matrix_world@rig.pose.bones['DEF-head'].matrix@invrest@anchor
            original=[obj.matrix_world@Vector(p.co[:3]) for p in obj.data.splines[0].points]
            side=-1 if label=='R' else 1
            lateral=(rig.matrix_world@rig.pose.bones['DEF-head'].matrix).to_3x3()@Vector((1,0,0));lateral.normalize()
            hand=original[-1];seed=[]
            for j in range(65):
                u=j/64;side_w,up_w=seed_weights(u)
                seed.append(target.lerp(hand,u)+lateral*(side*.30*side_w)+Vector((0,0,.035*up_w)))
            path=surface_route(target,hand,bvh,verts,normals,edges,cache)
            clearance=[]
            for a,b in zip(path,path[1:]):
                for t in (0,.25,.5,.75):
                    v=a.lerp(b,t);hit,n,_,dist=bvh.find_nearest(v);clearance.append((v-hit).dot(n))
            if min(clearance)<.006:raise ValueError('REIN358_SKIN_PENETRATION:'+str((f,label,min(clearance),clearance.index(min(clearance)))))
            captured[f].append((target,original,obj.matrix_world.copy(),path,min(clearance)))
    # Retain failed/previous action datablocks as evidence; new curve data action
    # owns the denser route. No unrelated horse or rider keys are touched.
    for obj in reins:
        if obj.data.animation_data and obj.data.animation_data.action:obj.data.animation_data.action.use_fake_user=True
        obj.data.animation_data_clear();obj.data.splines.clear();s=obj.data.splines.new('POLY');s.points.add(128)
        obj.data.bevel_depth=.0045
    errors=[];grip_errors=[];records=[]
    for f,rows in captured.items():
        scene.frame_set(f);bpy.context.view_layer.update()
        for obj,(target,original,world,path,clearance) in zip(reins,rows):
            delta=target-original[0];inv=world.inverted();points=obj.data.splines[0].points
            for j,p in enumerate(points):
                v=path[j]
                p.co=(*(inv@v),1);p.keyframe_insert('co',frame=f)
                if j==len(points)-1:grip_errors.append((v-original[-1]).length)
            errors.append((world@Vector(points[0].co[:3])-target).length)
            records.append(dict(frame=f,object=obj.name,bit_world=list(target),displacement=delta.length,hand_world=list(original[-1]),minimum_skin_clearance=clearance,length=sum((a-b).length for a,b in zip(path,path[1:]))))
    leather=bpy.data.materials['358 worn dark umber bridle leather']
    for obj in reins:
        obj.data.materials.clear();obj.data.materials.append(leather)
        a=obj.data.animation_data.action
        excluded.add(a.name)
        curves=[]
        if hasattr(a,'fcurves'):
            try:curves=list(a.fcurves)
            except RuntimeError:pass
        if not curves:
            for layer in a.layers:
                for strip in layer.strips:
                    for bag in getattr(strip,'channelbags',[]):curves.extend(bag.fcurves)
        for fc in curves:
            for k in fc.keyframe_points:
                if 252<=k.co.x<=441:k.interpolation='LINEAR'
    # Read the animation back after switching frames; same-write checks alone
    # cannot establish that the retained action actually evaluates correctly.
    playback_errors=[]
    for f,rows in captured.items():
        scene.frame_set(f);bpy.context.view_layer.update()
        for obj,(_,_,_,expected,_) in zip(reins,rows):
            playback_errors.extend((obj.matrix_world@Vector(p.co[:3])-v).length for p,v in zip(obj.data.splines[0].points,expected))
    if max(playback_errors)>1e-4:raise ValueError('REIN358_ANIMATION_READBACK')
    if protected_signature()!=sig:raise ValueError('REIN358_PROTECTED_ACTION_DRIFT')
    if max(errors)>1e-5 or max(grip_errors)>1e-8:raise ValueError('REIN358_CONTACT')
    rig['rein358']=1;scene.frame_set(frame);bpy.context.view_layer.update()
    report=dict(changed=True,source_preserved=True,protected_action_signature=sig,protected_actions_unchanged=True,maximum_bit_error=max(errors),maximum_grip_change=max(grip_errors),maximum_animation_readback_error=max(playback_errors),minimum_skin_clearance=min(x['minimum_skin_clearance'] for x in records),ring_stations=stations,ring_clearance_candidates=scores,records=records,scope='Entire exterior span reconstructed against evaluated horse skin; actual hand endpoints preserved. Shot-authored contact, not rope simulation; images and timing still required.')
    (out/'rein358.json').write_text(json.dumps(report,indent=2)+'\n');return report
