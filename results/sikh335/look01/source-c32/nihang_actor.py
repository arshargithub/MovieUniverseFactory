"""Fixed local coherent MPFB actor adaptation; no addon or asset code execution.

Retain one weighted anatomical surface from head through hands and feet. Clothing
shares that skeleton, not independent posed skin fragments. Source265 is a
rejected principal look but an inspected structural donor, never accepted art.
"""
import math
from pathlib import Path
import numpy as np
import importlib.util

DONOR='.runtime/art-direction/series01-sikh265/candidate-04/character.blend'
BODY='Sikh265 coherent MPFB male'
def module(name):
    spec=importlib.util.spec_from_file_location('mf_actor_'+name,Path(__file__).with_name(name+'.py'))
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def garment_mask(points,kind,wrists,elbows):
    p=np.asarray(points);z=p[:,2]
    if kind=='pants':return (z>.075)&(z<1.075)
    if kind=='boots':return z<.255
    keep=(z>1.025)&(z<1.60)
    for side in (-1,1):
        axis=np.asarray(wrists[side])-elbows[side];axis/=np.linalg.norm(axis)
        # Wrist plane is joint-relative, not a rectangular body-coordinate cut.
        past=(p-np.asarray(wrists[side]))@axis>-.025
        keep&=~((p[:,0]*side>.28)&past)
    return keep

def run(bpy,out):
    import bmesh
    from mathutils import Vector,Matrix,Quaternion
    from mathutils.kdtree import KDTree
    from mathutils.bvhtree import BVHTree
    support=module('nihang_support');finish=module('nihang_finish');look=module('nihang_look')
    scene=support.select_production_scene(bpy);scene.frame_set(283);bpy.context.view_layer.update()
    root=bpy.data.objects['mounted leader'];upper=bpy.data.objects['320 articulated upper body mounted leader']
    if bpy.data.objects.get('MF coherent Nihang rig'):raise ValueError('ACTOR_ALREADY_EXISTS')
    old_children=list(root.children_recursive)
    old_head=next(o for o in old_children if o.name.startswith('secondary adult head'))
    old_hand={-1:bpy.data.objects['leader palm'],1:bpy.data.objects['leader palm.001']}
    boots=sorted([o for o in old_children if o.name.startswith('297 mounted boot')],key=lambda o:o.name)
    if len(boots)!=2:raise ValueError('ACTOR_BOOT_TARGETS')
    donor=Path(__file__).resolve().parents[4]/DONOR
    with bpy.data.libraries.load(str(donor),link=False) as (available,loaded):
        selected=[n for n in available.objects if n.startswith((BODY,'beard donor-guided','brow.','eyeball.','iris.','pupil.'))]
        if BODY not in selected or BODY+'.rig' not in selected:raise ValueError('ACTOR_DONOR_INVENTORY')
        loaded.objects=selected
    imported=list(loaded.objects)
    for ob in imported:scene.collection.objects.link(ob)
    body=next(o for o in imported if o.name==BODY)
    rig=next(o for o in imported if o.type=='ARMATURE');rig.name='MF coherent Nihang rig'
    rig.animation_data_clear();rig.data.pose_position='POSE'
    for pb in rig.pose.bones:
        if pb.constraints:raise ValueError('ACTOR_UNINSPECTED_CONSTRAINTS')
        pb.matrix_basis=Matrix.Identity(4)
    if len(rig.data.bones)!=163:raise ValueError('ACTOR_SKELETON_CHANGED')
    body.name='MF coherent Nihang body'
    original_matrices={o.name:o.matrix_world.copy() for o in imported}
    old_rig=rig.matrix_world.copy();old_inv=old_rig.inverted()
    weighted=[];accessories=[]
    for ob in imported:
        if ob==rig:continue
        arms=[m for m in ob.modifiers if m.type=='ARMATURE']
        if arms:
            if len(arms)!=1 or arms[0].object!=rig:raise ValueError('ACTOR_WEIGHT_OWNER')
            weighted.append(ob)
        else:accessories.append(ob)
    if body not in weighted:raise ValueError('ACTOR_BODY_UNWEIGHTED')
    # Flatten only source morphs, retaining the anatomical mesh index -> weights.
    states=[(m,m.show_viewport,m.show_render) for m in body.modifiers]
    for m,_,_ in states:m.show_viewport=False;m.show_render=False
    bpy.context.view_layer.update()
    raw=bpy.data.meshes.new_from_object(body.evaluated_get(bpy.context.evaluated_depsgraph_get()))
    if len(raw.vertices)!=len(body.data.vertices):raise ValueError('ACTOR_MORPH_INDEX_CHANGED')
    kd=KDTree(len(raw.vertices))
    for v in raw.vertices:kd.insert(v.co,v.index)
    kd.balance()
    for m,v,r in states:m.show_viewport=v if m.type=='MASK' else False;m.show_render=r if m.type=='MASK' else False
    bpy.context.view_layer.update()
    surface=bpy.data.meshes.new_from_object(body.evaluated_get(bpy.context.evaluated_depsgraph_get()))
    points=np.array([v.co[:] for v in surface.vertices]);faces=[tuple(p.vertices) for p in surface.polygons]
    closest=[kd.find(v.co)[1] for v in surface.vertices]
    weights=[[(body.vertex_groups[g.group].name,g.weight) for g in body.data.vertices[i].groups] for i in closest]
    if any(not w for w in weights):raise ValueError('ACTOR_EMPTY_WEIGHTS')
    for m,v,r in states:m.show_viewport=v;m.show_render=r
    def mesh(name,pts,polys,mat,ws):
        d=bpy.data.meshes.new(name);d.from_pydata(pts,[],polys);d.update()
        o=bpy.data.objects.new(name,d);scene.collection.objects.link(o)
        o.parent=rig;o.matrix_parent_inverse=Matrix.Identity(4);o.matrix_basis=old_inv@original_matrices[body.name]
        d.materials.append(mat)
        groups={}
        for i,row in enumerate(ws):
            for n,w in row:
                if n not in rig.data.bones:continue
                if n not in groups:groups[n]=o.vertex_groups.new(name=n)
                groups[n].add([i],w,'REPLACE')
        for p in d.polygons:p.use_smooth=True
        arm=o.modifiers.new('Shared anatomical skeleton','ARMATURE');arm.object=rig;arm.use_deform_preserve_volume=True
        sub=o.modifiers.new('Continuous cloth surface','SUBSURF');sub.levels=1;sub.render_levels=1
        return o
    blue=finish.fabric(bpy,'MF coherent weathered indigo');gold=finish.fabric(bpy,'MF coherent ochre weave',True)
    leather=finish.fabric(bpy,'MF coherent worn leather')
    bs=leather.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.73
    ramp=next(n for n in leather.node_tree.nodes if n.type=='VALTORGB')
    for e,c in zip(ramp.color_ramp.elements,((.018,.012,.008,1),(.050,.028,.015,1))):e.color=c
    wrists={s:np.array(rig.data.bones['wrist.'+('L' if s==1 else 'R')].head_local) for s in (-1,1)}
    elbows={s:np.array(rig.data.bones['lowerarm01.'+('L' if s==1 else 'R')].head_local) for s in (-1,1)}
    clothing=[]
    for kind,mat in [('coat',blue),('pants',blue),('boots',leather)]:
        mask=garment_mask(points,kind,wrists,elbows)
        polys=[f for f in faces if all(mask[i] for i in f)]
        ids=sorted({i for f in polys for i in f});remap={i:j for j,i in enumerate(ids)}
        pts=points[ids].copy();norm=np.array([surface.vertices[i].normal[:] for i in ids])
        pts+=norm*(.015 if kind=='coat' else .012)
        polys=[tuple(remap[i] for i in f) for f in polys];ws=[weights[i] for i in ids]
        if kind=='coat':
            # Reuse the qualified23 continuous cloth topology, not a spatially
            # clipped body surface that cuts holes through raised shoulders.
            neutral=module('nihang_neutral');transfer=module('nihang_transfer')
            source=bpy.data.objects[neutral.CLOTH]
            if source.get('proof_bend_degrees'):raise ValueError('ACTOR_CLOTH_NOT_REST')
            rest=np.array([v.co[:] for v in source.data.vertices]);polys=[tuple(p.vertices) for p in source.data.polygons]
            pts=rest.copy();pts[:,0]*=1.08;pts[:,2]=1.265*rest[:,2]-.202
            for sign,side in ((-1,'R'),(1,'L')):
                reflected=rest.copy();reflected[:,0]*=sign
                component=neutral.connected_arm(reflected,polys)
                cuff=np.flatnonzero(component&(rest[:,2]<.935))
                a=np.array([sign*.18,0,1.36]);b=np.array([sign*.285,-.005,1.13]);cc=rest[cuff].mean(0)
                aa=np.array(rig.data.bones['upperarm01.'+side].head_local);bb=elbows[sign]
                axis=wrists[sign]-bb;axis/=np.linalg.norm(axis);wc=wrists[sign]-.025*axis
                up=transfer.segment_points(rest,a,b,aa,bb);low=transfer.segment_points(rest,b,cc,bb,wc)
                fore=transfer.ease((1.19-rest[:,2])/.12)
                blend=transfer.ease((rest[:,0]*sign-.145)/.085)
                blend=np.where(rest[:,2]<1.17,component.astype(float),blend)
                posed=up*(1-fore[:,None])+low*fore[:,None]
                pts=pts*(1-blend[:,None])+posed*blend[:,None]
            ws=[]
            for p in pts:
                i=kd.find(Vector(p))[1];ws.append([(body.vertex_groups[g.group].name,g.weight) for g in body.data.vertices[i].groups])
            # Recalculate normals on the fitted continuous garment.
            temp=bpy.data.meshes.new('MF coat rest normals');temp.from_pydata(pts,[],polys);temp.update()
            norm=np.array([v.normal[:] for v in temp.vertices]);bpy.data.meshes.remove(temp)
        # Low-amplitude irregular compression marks; not a substitute for drape.
        amp=.002 if kind=='boots' else .003
        wave=np.sin(pts[:,2]*65+pts[:,0]*17)*np.sin(pts[:,0]*31+pts[:,1]*13)
        pts+=norm*(amp*wave[:,None])
        ob=mesh('MF coherent '+kind,pts,polys,mat,ws)
        if kind=='coat':
            shrink=ob.modifiers.new('Post-deform skin clearance','SHRINKWRAP');shrink.target=body
            shrink.wrap_method='NEAREST_SURFACEPOINT';shrink.wrap_mode='OUTSIDE_SURFACE';shrink.offset=.012
        solid=ob.modifiers.new('Turned material edge','SOLIDIFY');solid.thickness=.002
        clothing.append(ob)
    # Split chola skirt: actual front/back openings, waist supported by the same rig.
    for side in (-1,1):
        pts=[];ws=[];rows=20;cols=49
        for j in range(rows):
            u=j/(rows-1);z=1.06-.45*u
            for k in range(cols):
                a=(.035+(math.pi-.07)*k/(cols-1))*side
                radius=.205+.115*u+.008*u*math.sin(8*a+.8)+.004*u*math.sin(13*a-1.2)
                p=Vector((radius*math.sin(a),-.02-radius*.77*math.cos(a),z))
                pts.append(tuple(p))
                leg='L' if p.x>0 else 'R';w=u*u*.80
                ws.append([('spine05',1-w),('upperleg02.'+leg,w)])
        ob=mesh('MF coherent split chola',pts,look.grid(rows,cols),blue,ws)
        solid=ob.modifiers.new('Turned skirt hem','SOLIDIFY');solid.thickness=.002;clothing.append(ob)
    # Waist wrap is genuinely supported at the pelvis, not independent proxy skin.
    coat=clothing[0];tree=BVHTree.FromPolygons([v.co for v in coat.data.vertices],[tuple(p.vertices) for p in coat.data.polygons])
    pts=[];ws=[];rows=9;cols=97
    for j in range(rows):
        u=j/(rows-1)
        for k in range(cols):
            a=math.tau*k/(cols-1);z=1.06+.085*u+.004*math.sin(a)
            axis=Vector((math.sin(a),-math.cos(a),0));origin=Vector((0,-.02,z))
            hit=tree.ray_cast(origin+axis*.5,-axis)[0]
            if hit is None:raise ValueError('ACTOR_WAIST_SUPPORT_MISSING')
            p=hit+axis*(.006+.0015*math.sin(u*math.pi*3+a*2));pts.append(tuple(p))
            ws.append([('spine05',1)])
    clothing.append(mesh('MF coherent waist wrap',pts,look.grid(rows,cols),gold,ws))
    # Rest-space surface-supported diagonal sash shares skin weights with the coat.
    rows=41;cols=7;panels=[]
    for side in (-1,1):
        panel=[]
        for j in range(rows):
            t=j/(rows-1);x=.14-.31*t;z=1.07+.48*t
            for k in range(cols):
                off=(k/(cols-1)-.5)*.075;xx=x+off*.84;zz=z+off*.54
                hit=None
                for delta in range(21):
                    hit=tree.ray_cast(Vector((xx,side*.7,zz-.003*delta)),Vector((0,-side,0)))[0]
                    if hit is not None:break
                if hit is None:raise ValueError(f'ACTOR_SASH_UNSUPPORTED row={j} col={k} side={side}')
                panel.append((xx,hit.y+side*.009,hit.z))
        panels.append(np.array(panel).reshape(rows,cols,3))
    front,back=panels;bridge=[]
    for j in range(1,9):
        u=j/9;p=front[-1]*(1-u)+back[-1]*u
        for k in range(cols):
            hit=tree.ray_cast(Vector((p[k,0],p[k,1],1.9)),Vector((0,0,-1)))[0]
            if hit is None or hit.z<1.40:raise ValueError('ACTOR_SHOULDER_BRIDGE_UNSUPPORTED')
            p[k,2]=max(p[k,2],hit.z+.009)
        bridge.append(p)
    pts=np.concatenate((front,np.array(bridge),back[::-1])).reshape(-1,3)
    sashweights=[]
    for p in pts:
        i=kd.find(Vector(p))[1];sashweights.append([(body.vertex_groups[g.group].name,g.weight) for g in body.data.vertices[i].groups])
    clothing.append(mesh('MF coherent shoulder sash',pts,look.grid(len(pts)//cols,cols),gold,sashweights))
    # Head attachments and crown use the SAME head bone, not another neck mesh.
    holder=bpy.data.objects.new('MF coherent cranial frame',None);scene.collection.objects.link(holder)
    proxy=bpy.data.objects.new('secondary adult head MF fit-only',surface.copy());scene.collection.objects.link(proxy)
    parent=bpy.data.objects.new('MF coherent fit-only owner',None);scene.collection.objects.link(parent)
    holder.parent=parent;proxy.parent=parent;holder.location.z=1.746
    proxy.hide_render=True;proxy.hide_viewport=True;bpy.context.view_layer.update()
    crown_names=look.wrapped_crown(bpy,holder,blue,False)
    crown=[bpy.data.objects[n] for n in crown_names]
    for ob in crown:
        world=holder.matrix_world@ob.matrix_basis;ob.parent=None;ob.matrix_world=world;accessories.append(ob)
    bpy.data.objects.remove(proxy,do_unlink=True);bpy.data.objects.remove(holder,do_unlink=True);bpy.data.objects.remove(parent,do_unlink=True)
    # Capture rest attachment transforms before relocating the rig.
    attachment_rest={ob.name:ob.matrix_world.copy() for ob in accessories}
    head_rest=rig.data.bones['head'].matrix_local.copy()
    for ob in weighted:
        local=old_inv@original_matrices[ob.name]
        ob.parent=rig;ob.matrix_parent_inverse=Matrix.Identity(4);ob.matrix_basis=local
    for ob in accessories:ob.parent=rig;ob.matrix_parent_inverse=Matrix.Identity(4)
    rig.parent=root;rig.matrix_parent_inverse=Matrix.Identity(4)
    rig.matrix_basis=Matrix.Translation((0,0,-1.02))
    # Keep all former anatomy and clothes available, but never render two actors.
    for ob in old_children:
        if ob.type in {'MESH','CURVE'}:ob.hide_render=True
    required=('upperarm01','upperarm02','lowerarm01','lowerarm02','upperleg01','upperleg02','lowerleg01','lowerleg02')
    if any(n+'.'+s not in rig.pose.bones for n in required for s in ('L','R')):raise ValueError('ACTOR_CHAIN')
    contact=[]
    def set_segment(name,a,b):
        pb=rig.pose.bones[name];rest=pb.bone.matrix_local.to_3x3();axis=rest.col[1].normalized()
        q=axis.rotation_difference((b-a).normalized());m=(q.to_matrix()@rest).to_4x4();m.translation=a
        pb.rotation_mode='QUATERNION';pb.matrix=m
        for path in ('location','rotation_quaternion','scale'):pb.keyframe_insert(path,frame=f)
        bpy.context.view_layer.update()
    def chain(names,a,b):
        lens=[rig.data.bones[n].length for n in names];total=sum(lens);axis=(b-a).normalized();p=a.copy()
        for n,l in zip(names,lens):set_segment(n,p,p+axis*l);p+=axis*l
        return p
    for f in range(252,442):
        scene.frame_set(f);bpy.context.view_layer.update();inv=rig.matrix_world.inverted()
        # Distributed spine/neck acting preserves one deforming body surface.
        q=upper.rotation_euler.x
        for name,factor in [('spine04',.35),('spine02',.65)]:
            pb=rig.pose.bones[name];pb.rotation_mode='XYZ';pb.rotation_euler=(q*factor,0,0);pb.keyframe_insert('rotation_euler',frame=f)
        relative=root.matrix_world.to_quaternion().inverted()@old_head.matrix_world.to_quaternion()
        for name,factor in [('neck02',.35),('head',.65)]:
            pb=rig.pose.bones[name];pb.rotation_mode='QUATERNION';pb.rotation_quaternion=Quaternion().slerp(relative,factor);pb.keyframe_insert('rotation_quaternion',frame=f)
        bpy.context.view_layer.update()
        for sign,side in ((-1,'R'),(1,'L')):
            suffix='.'+side
            start=rig.pose.bones['upperarm01'+suffix].head.copy()
            palm=inv@old_hand[sign].matrix_world.translation
            wrist=palm+Vector((0,.073,-.018))
            ua=sum(rig.data.bones[n+suffix].length for n in ('upperarm01','upperarm02'))
            la=sum(rig.data.bones[n+suffix].length for n in ('lowerarm01','lowerarm02'))
            elbow=Vector(support.bend_joint(start,wrist,ua,la,(sign,.35,-.2)))
            chain(['upperarm01'+suffix,'upperarm02'+suffix],start,elbow)
            chain(['lowerarm01'+suffix,'lowerarm02'+suffix],elbow,wrist)
            set_segment('wrist'+suffix,wrist,wrist+Vector((0,-.97,.24)).normalized()*rig.data.bones['wrist'+suffix].length)
            hand=rig.pose.bones['wrist'+suffix].matrix@rig.data.bones['wrist'+suffix].matrix_local.inverted()
            across=(rig.data.bones['finger2-1'+suffix].head_local-rig.data.bones['finger5-1'+suffix].head_local).normalized()
            first=rig.data.bones['finger3-1'+suffix];second=rig.data.bones['finger3-2'+suffix]
            d1=(first.tail_local-first.head_local).normalized();d2=(second.tail_local-second.head_local).normalized()
            curl_sign=1 if across.cross(d1).dot(d2-d1)>0 else -1
            curl_axis=(hand.to_3x3()@across).normalized()
            for digit in range(1,6):
                total=0.;previous=None
                for j,angle in enumerate((.85,1.15,.75),1):
                    pb=rig.pose.bones[f'finger{digit}-{j}'+suffix];total+=angle*(.50 if digit==1 else 1)
                    rotation=Quaternion(curl_axis,total*curl_sign).to_matrix()@hand.to_3x3()@pb.bone.matrix_local.to_3x3()
                    m=rotation.to_4x4();m.translation=hand@pb.bone.head_local if previous is None else previous
                    pb.rotation_mode='QUATERNION';pb.matrix=m;previous=m.translation+rotation.col[1].normalized()*pb.bone.length
                    for path in ('location','rotation_quaternion','scale'):pb.keyframe_insert(path,frame=f)
                    bpy.context.view_layer.update()
            hip=rig.pose.bones['upperleg01'+suffix].head.copy()
            ankle=inv@boots[0 if sign==-1 else 1].matrix_world.translation+Vector((0,.035,.065))
            ul=sum(rig.data.bones[n+suffix].length for n in ('upperleg01','upperleg02'))
            ll=sum(rig.data.bones[n+suffix].length for n in ('lowerleg01','lowerleg02'))
            knee=Vector(support.bend_joint(hip,ankle,ul,ll,(sign*.35,-1,0)))
            chain(['upperleg01'+suffix,'upperleg02'+suffix],hip,knee)
            chain(['lowerleg01'+suffix,'lowerleg02'+suffix],knee,ankle)
            rest=rig.data.bones['foot'+suffix];set_segment('foot'+suffix,ankle,ankle+(rest.tail_local-rest.head_local))
            contact.append({'frame':f,'side':side,'wrist_target':list(wrist),'elbow':list(elbow),'ankle_target':list(ankle)})
        bpy.context.view_layer.update()
        for ob in accessories:
            ob.matrix_basis=rig.pose.bones['head'].matrix@head_rest.inverted()@old_inv@attachment_rest[ob.name]
            ob.rotation_mode='QUATERNION'
            for path in ('location','rotation_quaternion','scale'):ob.keyframe_insert(path,frame=f)
    scene.frame_set(283);bpy.context.view_layer.update()
    # All actual sampled owner/contact evidence is retained; not an AV pass.
    import json
    (out/'coherent-actor-contacts.json').write_text(json.dumps(contact,indent=2)+'\n')
    for d in (raw,surface):bpy.data.meshes.remove(d)
    return {'donor':DONOR,'bones':len(rig.data.bones),'body':body.name,'weighted_objects':[o.name for o in weighted],
            'clothing':[o.name for o in clothing],'attachments':[o.name for o in accessories],
            'frames':190,'scope':'One complete mounted actor; no crowd propagation or artistic acceptance. Original owners retained; old mesh assembly render-hidden.'}
