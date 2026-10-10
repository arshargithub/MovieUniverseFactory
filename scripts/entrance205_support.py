"""Choreography-stage support transport. NOT a new cloth/hair simulation.

Phase-register admitted opening caches, carry new skeletal support changes,
and bind groom to actual re-solved horse surfaces. Inspect complete motion;
renew inertial cloth/groom finishing after Director choreography approval.
"""
import json
import numpy as np
from entrance205_actor import linear_sample, OPENING, OPENING_SHA
from entrance205_motion import smooth
import wardrobe_motion178 as base


def downhill_look(scene,data):
    """Compensate the uphill body pitch in the authored checkpoint glance.

    The initial 16-degree local down-look still pointed above world horizontal
    after the 26-degree climb pitch. Renew headfall support from actual rig
    matrices, not a texture or camera trick. No chest/hand/leg pose change.
    """
    import bpy,math
    from mathutils import Quaternion
    from entrance205_camera import glance
    from wardrobe_motion178_controls import render_geometry_paused
    rig=bpy.data.objects['MF_body156_fit_rig'];names=list(data['names']);after=[]
    rig.animation_data.action.use_fake_user=True;rig.animation_data.action=rig.animation_data.action.copy()
    with render_geometry_paused():
        for i in range(len(data['source_frames'])):
            f=361+i;scene.frame_set(f);g=glance(i/24)
            for name,deg in (('MF185_neck',4),('MF185_head',14)):
                bone=rig.pose.bones[name];bone.rotation_quaternion=bone.rotation_quaternion@Quaternion((1,0,0),math.radians(deg)*g)
                bone.keyframe_insert('rotation_quaternion',frame=f)
            bpy.context.view_layer.update();after.append([np.array(rig.pose.bones[n].matrix) for n in names])
    data['after']=np.array(after)
    return {'additional_local_pitch_degrees':18,'reason':'World-space checkpoint is below the actor; original local down-look was cancelled by uphill root pitch','visual_gate':'NOT_RUN'}


def source_caches():
    from entrance189_groom import read_mdd
    if base.digest(OPENING)!=OPENING_SHA:raise ValueError('Opening changed')
    r=json.loads((OPENING.parent/'result.json').read_text());result={}
    for row in r['caches']:
        p=(OPENING.parent/row['path']).resolve()
        if base.digest(p)!=row['sha256']:raise ValueError('Opening cache changed')
        result[row['object']]=(read_mdd(p),row['start'])
    return result


def periodic(a,start,f):
    period=24/2.2;low=360-period
    # Close the retained single-cycle secondary-motion seam smoothly. This
    # is authored blocking reuse, not a claim that old simulation was cyclic.
    u=np.clip((f-low)/period,0,1)
    correction=linear_sample(a,360-start)-linear_sample(a,low-start)
    return linear_sample(a,f-start)-smooth(u)*correction


def clothes(scene,out,data,caches):
    import bpy
    from mathutils import Matrix
    from entrance189_groom import write_mdd,attach_cache
    from wardrobe_motion178_controls import render_geometry_paused
    names=list(data['names']);before=data['before'];after=data['after'];phases=data['source_frames'];world=data['world'];rows=[]
    def delta(i,n):
        j=names.index(n);return world[i]@after[i,j]@np.linalg.inv(before[i,j])@np.linalg.inv(world[i])
    for name,label in (('MF185_moving_shawl','shawl'),('MF185_free_lower_tunic','skirt')):
        a,start=caches[name];ob=bpy.data.objects[name]
        def frames():
            for i,f in enumerate(phases):
                p=periodic(a,start,f)
                def moved(n):
                    m=delta(i,n);return p@m[:3,:3].T+m[:3,3]
                if label=='skirt':q=moved('pelvis')
                else:
                    h=world[i]@before[i,names.index('MF185_head')];inv=np.linalg.inv(h)
                    local=p@inv[:3,:3].T+inv[:3,3]
                    w=smooth((local[:,1]+1.2)/1.8)
                    # Keep back wrap courses chest-supported; do not drag the
                    # whole outer shawl round with the checking glance.
                    w[2501:]=0
                    q=moved('chest')*(1-w[:,None])+moved('MF185_head')*w[:,None]
                yield q.astype(np.float32)
        path=out/(label+'.mdd');write_mdd(path,len(phases),len(ob.data.vertices),frames());attach_cache(ob,path,361)
        rows.append({'object':name,'method':'Phase-closed source secondary motion with new support transport; inertial solve deferred, visual gate required'})
    # Hardware is rigidly supported by pelvis, not held at the last old key.
    with render_geometry_paused():
        for name in ('MF_173_belt_buckle','MF_173_buckle_tongue'):
            ob=bpy.data.objects[name];old=[]
            for f in phases:
                scene.frame_set(int(f),subframe=f%1);bpy.context.view_layer.update();old.append(np.array(ob.matrix_world))
            if ob.animation_data and ob.animation_data.action:ob.animation_data.action.use_fake_user=True
            ob.animation_data_clear();ob.rotation_mode='QUATERNION'
            for i,f in enumerate(phases):
                ob.matrix_world=Matrix(delta(i,'pelvis')@old[i])
                for prop in ('location','rotation_quaternion','scale'):ob.keyframe_insert(prop,frame=361+i)
    return rows


def groom(scene,out,data,caches):
    import bpy
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    from entrance189_groom import read_mdd,write_mdd,attach_cache
    from entrance188_groom import triangle_frames
    from wardrobe185_lower_drape import triangle_weights
    horse=bpy.data.objects['MF185_gait_horse'];horse.data.calc_loop_triangles()
    phases=data['source_frames'];oldhorse,start=caches['MF185_gait_horse']
    mods=[m for m in horse.modifiers if m.type=='MESH_CACHE']
    if len(mods)!=1 or mods[0].frame_start!=361:raise ValueError('Expected the selected route horse cache')
    path=__import__('pathlib').Path(bpy.path.abspath(mods[0].filepath)).resolve()
    if not path.is_relative_to(base.BASE.resolve()):raise ValueError('Foreign groom support source')
    newhorse=read_mdd(path)
    tris=np.array([tuple(t.vertices) for t in horse.data.loop_triangles if horse.data.polygons[t.polygon_index].material_index==0])
    h0=linear_sample(oldhorse,phases[0]-start);records={}
    for kind,name in (('mane','MF188_flowing_mane'),('tail','MF185_gait_Full Bushy Flowing Horse Tail')):
        a,offset=caches[name];rest=periodic(a,offset,phases[0]);ob=bpy.data.objects[name]
        points=rest.reshape(6282,12,3,3).mean(2).reshape(-1,3) if kind=='mane' else rest
        region=tris[np.all(h0[tris,1]<1,axis=1)&np.all(h0[tris,2]>-11,axis=1)] if kind=='mane' else tris[np.all(h0[tris,1]>3,axis=1)&np.all(h0[tris,2]>-12,axis=1)]
        tree=BVHTree.FromPolygons(h0.tolist(),region.tolist(),all_triangles=True);ids=[];bary=[]
        tailroot=rest[rest[:,1]<6.35].mean(0) if kind=='tail' else None
        for pt in points:
            hit,_,i,_=tree.find_nearest(Vector(tailroot if kind=='tail' else pt));ids.append(region[i]);bary.append(triangle_weights(hit,h0[region[i]]))
        ids=np.array(ids);bary=np.array(bary)
        def frames():
            for i,f in enumerate(phases):
                old=periodic(a,offset,f);oh=linear_sample(oldhorse,f-start);nh=np.asarray(newhorse[i],float)
                oldtri=oh[ids];newtri=nh[ids];oldbasis=triangle_frames(oldtri);newbasis=triangle_frames(newtri)
                oldanchor=(oldtri*bary[:,:,None]).sum(1);newanchor=(newtri*bary[:,:,None]).sum(1)
                if kind=='mane':
                    strands=old.reshape(-1,3,3);relative=strands-oldanchor[:,None,:]
                    local=np.einsum('nki,nij->nkj',relative,oldbasis)
                    q=newanchor[:,None,:]+np.einsum('nkj,nij->nki',local,newbasis)
                    q=q.reshape(-1,3)
                else:
                    local=np.einsum('ni,nij->nj',old-oldanchor,oldbasis)
                    q=newanchor+np.einsum('nj,nij->ni',local,newbasis)
                if i%72==0:print('205 groom transport',kind,i,flush=True)
                yield q.astype(np.float32)
        path=out/(kind+'.mdd');write_mdd(path,len(phases),len(rest),frames());attach_cache(ob,path,361)
        np.savez_compressed(out/(kind+'-binding.npz'),triangles=ids,barycentric=bary)
        records[kind]={'method':'Fixed triangle correspondence from phase-registered source to re-solved horse; retained source response, no new aerodynamic claim','horse_cache_sha256':base.digest(__import__('pathlib').Path(bpy.path.abspath(mods[0].filepath))),'visual_gate':'NOT_RUN'}
    return records
