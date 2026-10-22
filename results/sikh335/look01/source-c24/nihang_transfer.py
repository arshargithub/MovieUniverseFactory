"""Fixed neutral-to-supporting-actor transfer; no external code or asset paths."""
import importlib.util
import json
from pathlib import Path
import numpy as np


def module(name):
    spec=importlib.util.spec_from_file_location('mf_'+name,Path(__file__).with_name(name+'.py'))
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m


def ease(x):
    x=np.clip(x,0,1);return x*x*(3-2*x)


def segment_points(points,a,b,ta,tb):
    """Rigid radial form with measured axial length, using minimal rotation."""
    a,b,ta,tb=map(lambda p:np.asarray(p,dtype=float),(a,b,ta,tb))
    old=b-a;new=tb-ta;lo=np.linalg.norm(old);ln=np.linalg.norm(new)
    if min(lo,ln)<.04 or not .45<ln/lo<1.8:raise ValueError('TRANSFER_SEGMENT_RANGE')
    u=old/lo;v=new/ln;cross=np.cross(u,v);cos=float(np.dot(u,v))
    if cos<-.9999:raise ValueError('TRANSFER_AMBIGUOUS_ROLL')
    x,y,z=cross;k=np.array([[0,-z,y],[z,0,-x],[-y,x,0]])
    rot=np.eye(3)+k+k@k/(1+cos)
    along=(points-a)@(old/lo)
    return (points-a)@rot.T+ta+along[:,None]*(new/ln)[None,:]*(ln/lo-1)


def pose_points(rest,offset,arms,targets):
    """Keep torso rest drape; pose connected arms into measured cache endpoints."""
    result=rest.copy();result[:,2]+=offset
    for side in (-1,1):
        arm=arms[side];a=arm['shoulder'];b=arm['elbow'];c=arm['wrist']
        ta,tb,tc=targets[side]
        up=segment_points(rest,a,b,ta,tb);low=segment_points(rest,b,c,tb,tc)
        fore=ease((1.19-rest[:,2])/.12)
        w=ease((rest[:,0]*side-.145)/.085)
        # Complete connected cuffs must move together, including medial edge.
        w=np.where(rest[:,2]<1.17,arm['component'].astype(float),w)
        moved=up*(1-fore[:,None])+low*fore[:,None]
        result=result*(1-w[:,None])+moved*w[:,None]
    return result


def run(bpy,phase,out):
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    if phase not in ('leader','near_crowd'):raise ValueError('TRANSFER_PHASE')
    neutral=module('nihang_neutral');source=bpy.data.objects.get(neutral.CLOTH)
    if source is None or source.get('neutral_rest_proof')!=1 or source.get('proof_bend_degrees'):
        raise ValueError('TRANSFER_NEUTRAL_UNBENT_REQUIRED')
    root=bpy.data.objects['mounted leader' if phase=='leader' else 'FOOT WARRIOR 0']
    scene=next(s for s in bpy.data.scenes if root.name in s.objects)
    bpy.context.window.scene=scene;scene.frame_set(283);bpy.context.view_layer.update()
    upper=next(o for o in root.children if o.name.startswith('320 articulated upper body'))
    old=next(o for o in upper.children if o.name.startswith('319 anatomically'))
    name='MF Nihang neutral-derived chola '+root.name
    if bpy.data.objects.get(name):raise ValueError('TRANSFER_ALREADY_EXISTS')
    rest=np.array([v.co[:] for v in source.data.vertices]);faces=[tuple(p.vertices) for p in source.data.polygons]
    leader=phase=='leader';offset=-.9 if leader else .01
    if not leader:rest[:,:2]*=-1
    arms={}
    for side in (-1,1):
        reflected=rest.copy();reflected[:,0]*=side
        component=neutral.connected_arm(reflected,faces)
        ids=np.flatnonzero(component & (rest[:,2]<.935))
        if len(ids)<8:raise ValueError('TRANSFER_CUFF_MISSING')
        arms[side]={'component':component,'shoulder':np.array([side*.18,0,1.36]),
            'elbow':np.array([side*.285,-.005 if leader else .005,1.13]),
            'wrist':rest[ids].mean(0),'cuff':ids}
    sleeves=[o for o in root.children_recursive if o.name.startswith('318 endpoint-bound leader sleeve' if leader else '297 crowd sleeve')]
    if len(sleeves)!=2:raise ValueError('TRANSFER_CACHE_OWNERS')
    times=sorted(set(range(1,697,4))|set(range(276,317))|{696}) if leader else [283]
    poses=[];cuff_errors=[]
    for f in times:
        targets={}
        for sleeve in sleeves:
            if leader:
                key=sleeve.data.shape_keys.key_blocks.get(f'pose{f:04d}')
                if key is None:raise ValueError('TRANSFER_CACHE_FRAME')
                pts=np.array([p.co[:] for p in key.data])
            else:pts=np.array([p.co[:] for p in sleeve.data.vertices])
            if len(pts)!=312:raise ValueError('TRANSFER_CACHE_TOPOLOGY')
            target=np.array([pts[j*24:(j+1)*24].mean(0) for j in (0,6,12)])
            side=-1 if target[0,0]<0 else 1
            if side in targets:raise ValueError('TRANSFER_CACHE_SIDE')
            targets[side]=target
        posed=pose_points(rest,offset,arms,targets)
        if not np.isfinite(posed).all():raise ValueError('TRANSFER_NONFINITE')
        for side in (-1,1):cuff_errors.append(float(np.linalg.norm(posed[arms[side]['cuff']].mean(0)-targets[side][2])))
        poses.append(posed.astype('f4'))
    if max(cuff_errors)>.007:raise ValueError('TRANSFER_CUFF_CONTACT:'+str(max(cuff_errors)))
    data=bpy.data.meshes.new(name);data.from_pydata(poses[0],[],faces);data.update()
    for p in data.polygons:p.use_smooth=True
    obj=bpy.data.objects.new(name,data);scene.collection.objects.link(obj)
    obj.parent=old.parent;obj.matrix_parent_inverse=old.matrix_parent_inverse.copy();obj.matrix_basis=old.matrix_basis.copy()
    data.materials.append(old.data.materials[0].copy())
    if leader:
        obj.shape_key_add(name='Basis')
        for i,(f,points) in enumerate(zip(times,poses)):
            key=obj.shape_key_add(name=f'bound{f:04d}');key.data.foreach_set('co',points.ravel())
            for ff,val in ((times[i-1] if i else 0,0),(f,1),(times[i+1] if i+1<len(times) else 697,0)):
                key.value=val;key.keyframe_insert('value',frame=ff)
        action=data.shape_keys.animation_data.action
        for layer in action.layers:
            for strip in layer.strips:
                for bag in strip.channelbags:
                    for fc in bag.fcurves:
                        for key in fc.keyframe_points:key.interpolation='LINEAR'
    sub=obj.modifiers.new('Continuous neutral cloth surface','SUBSURF');sub.levels=1;sub.render_levels=1
    solid=obj.modifiers.new('Woven cloth thickness','SOLIDIFY');solid.thickness=.0015
    old.hide_render=True;old.hide_viewport=True
    scene.frame_set(283);bpy.context.view_layer.update()
    ev=obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
    tree=BVHTree.FromPolygons([v.co for v in ev.data.vertices],[tuple(p.vertices) for p in ev.data.polygons])
    layers=[];facing=-1 if leader else 1
    for ob in upper.children:
        if ob.name.startswith(('319 overlapping chola chest panel','319 bound chola neckline')):
            ob.hide_render=True;ob.hide_viewport=True
        if ob.type!='MESH' or not ob.name.startswith(('297 woven diagonal sash','319 chola folded placket')):continue
        ob.data=ob.data.copy()
        for mod in list(ob.modifiers):
            if mod.type=='SHRINKWRAP':ob.modifiers.remove(mod)
        hits=0
        for p in ob.data.vertices:
            hit=tree.ray_cast(Vector((p.co.x,facing*.8,p.co.z)),Vector((0,-facing,0)))[0]
            if hit is not None:p.co.y=hit.y+facing*.008;hits+=1
        wrap=ob.modifiers.new('Supported by actual transferred garment','SHRINKWRAP')
        wrap.target=obj;wrap.wrap_method='NEAREST_SURFACEPOINT';wrap.wrap_mode='OUTSIDE_SURFACE';wrap.offset=.008
        layers.append({'name':ob.name,'hits':hits,'vertices':len(ob.data.vertices)})
    np.savez_compressed(out/f'{phase}-transfer.npz',rest=rest,poses=np.array(poses),frames=np.array(times),cuff_errors=np.array(cuff_errors))
    obj['neutral_transfer_proof']=1
    return {'phase':phase,'shirt':obj.name,'source_vertices':len(rest),'cached_poses':len(poses),
            'maximum_cuff_mean_error':max(cuff_errors),'layers':layers,
            'limits':'Actual actor transfer candidate. Shape/contact/material/full-speed review still required; no automatic costume or ensemble pass.'}
