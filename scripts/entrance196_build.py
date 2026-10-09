"""A-derived ground/contact art and coordinated head response.

Trusted closed operation; authored shot effects, not calibrated dynamics.
"""
import json
import math
import os
import sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import wardrobe_motion178 as base
from entrance196 import SOURCE,SOURCE_SHA


def head_offsets(phase):
    """Retain partial gaze isolation, remove excessive counter-cancellation."""
    p=np.asarray(phase,float)
    if p.shape!=(144,) or not np.isfinite(p).all():raise ValueError('Bounded source phase required')
    lag=np.r_[p[0],p[:-1]];lag2=np.r_[p[0],p[0],p[:-2]]
    return np.column_stack((1.6*lag,1.4*lag2))


def ballistic(origin,velocity,age,radius):
    """One dissipative bounce on the local flat support, in ground space."""
    o=np.asarray(origin,float);v=np.asarray(velocity,float);t=max(0.,float(age));g=81.4
    hit=2*v[2]/g
    if t<=hit:
        p=o+v*t;p[2]-=.5*g*t*t
    else:
        dt=t-hit;v2=v.copy();v2[:2]*=.48;v2[2]*=.25
        p=o+np.array([v[0]*hit,v[1]*hit,0.])+v2*dt;p[2]-=.5*g*dt*dt
        p[2]=max(o[2],p[2])
    p[2]=max(o[2],p[2])
    return p


def motion(scene,out):
    import bpy
    from mathutils import Matrix,Quaternion
    from wardrobe_motion178_controls import render_geometry_paused
    from entrance189_groom import read_mdd,write_mdd,attach_cache
    rig=bpy.data.objects['MF_body156_fit_rig']
    with np.load(base.BASE/'entrance196-inspect01/rig.npz') as z:
        names=list(z['names']);before=z['matrices'].copy();basis=z['bases'].copy()
    with np.load(base.BASE/'entrance193-motion02/rig.npz') as z:offsets=head_offsets(z['phase'])
    rig.animation_data.action=rig.animation_data.action.copy();rig.animation_data.action.name='196 less-locked riding attention'
    after=[]
    with render_geometry_paused():
        for i,f in enumerate(range(217,361)):
            scene.frame_set(f)
            for name in ('MF185_neck','MF185_head'):
                rig.pose.bones[name].matrix_basis=Matrix(basis[i,names.index(name)])
            for name,angle in zip(('MF185_neck','MF185_head'),offsets[i]):
                b=rig.pose.bones[name];b.rotation_mode='QUATERNION'
                b.rotation_quaternion=Quaternion((1,0,0),math.radians(float(angle)))@b.rotation_quaternion
                b.keyframe_insert(data_path='rotation_quaternion',frame=f)
            bpy.context.view_layer.update();after.append([np.array(rig.matrix_world@b.matrix) for b in rig.pose.bones])
    after=np.array(after)
    unchanged=[n for n in names if n not in ('MF185_neck','MF185_head')]
    residual=max(float(np.max(abs(after[:,names.index(n)]-before[:,names.index(n)]))) for n in unchanged)
    if residual>1e-5:raise ValueError('Unexpected non-head rig change')
    shawl=bpy.data.objects['MF185_moving_shawl'];mod=next(m for m in shawl.modifiers if m.type=='MESH_CACHE')
    src=Path(bpy.path.abspath(mod.filepath));a=read_mdd(src);start=int(mod.frame_start)
    world=np.array(shawl.matrix_world);inv=np.linalg.inv(world);h=names.index('MF185_head')
    def frames():
        for k,row in enumerate(a):
            p=np.array(row,float);i=k+start-217
            if 0<=i<144:
                q=p@world[:3,:3].T+world[:3,3]
                # Same tested continuous support region; transform the whole
                # headfall coherently and leave shoulder courses unchanged.
                w=np.clip((q[:,2]-before[i,h,2,3]+1.2)/1.8,0,1);w=w*w*(3-2*w)
                d=after[i,h]@np.linalg.inv(before[i,h]);moved=q@d[:3,:3].T+d[:3,3]
                q+=(moved-q)*w[:,None];p=q@inv[:3,:3].T+inv[:3,3]
            yield p.astype(np.float32)
    path=out/'shawl.mdd';write_mdd(path,len(a),len(shawl.data.vertices),frames());attach_cache(shawl,path,start)
    np.savez_compressed(out/'motion.npz',names=names,before=before,after=after,offsets=offsets)
    return {'non_head_matrix_residual':residual,'neck_head_added_degrees':np.ptp(offsets,axis=0).tolist(),
            'source_shawl_sha256':base.digest(src),'method':'Partial release of counter-rotation with one/two-frame gait lag; headfall corrective transport, not new simulation'}


def rock_material(name,color):
    import bpy
    m=bpy.data.materials.new(name);m.use_nodes=True;n,l=m.node_tree.nodes,m.node_tree.links
    bs=n.get('Principled BSDF');bs.inputs['Roughness'].default_value=.94
    c=n.new('ShaderNodeTexCoord');mapping=n.new('ShaderNodeVectorMath');mapping.operation='MULTIPLY';mapping.inputs[1].default_value=(1.3,1.0,4.5)
    l.new(c.outputs['Object'],mapping.inputs[0])
    noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=2.4;noise.inputs['Detail'].default_value=3.2
    l.new(mapping.outputs[0],noise.inputs[0]);r=n.new('ShaderNodeValToRGB');r.color_ramp.elements[0].position=.28;r.color_ramp.elements[1].position=.73
    r.color_ramp.elements[0].color=(*[v*.46 for v in color],1);r.color_ramp.elements[1].color=(*[min(1,v*1.40) for v in color],1)
    l.new(noise.outputs['Fac'],r.inputs[0]);l.new(r.outputs[0],bs.inputs['Base Color'])
    bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.33;bump.inputs['Distance'].default_value=.07
    l.new(noise.outputs['Fac'],bump.inputs['Height']);l.new(bump.outputs[0],bs.inputs['Normal'])
    return m


def prototype(rng):
    angles=np.arange(8)*math.tau/8+rng.uniform(-.15,.15,8);rad=rng.uniform(.7,1.15,8)
    low=np.column_stack((np.cos(angles)*rad,np.sin(angles)*rad,rng.uniform(-.40,-.25,8)))
    high=np.column_stack((np.cos(angles+.10)*rad*.72,np.sin(angles+.10)*rad*.72,rng.uniform(.25,.65,8)))
    p=np.vstack((low,high,[[.15,-.08,.74]]));f=[]
    for i in range(8):
        j=(i+1)%8;f.extend([(i,j,8+j),(i,8+j,8+i),(8+i,8+j,16)])
    f.append(tuple(reversed(range(8))))
    return p,f


def terrain(scene,out):
    import bpy
    from entrance_astra_world import mesh_object
    from entrance188_ground import bank_height
    rng=np.random.default_rng(196);root=bpy.data.objects['AS_world_travel'];land=bpy.data.objects['AS_valley_landform']
    colors=[(.24,.225,.19),(.34,.28,.19),(.15,.17,.18),(.42,.36,.26),(.27,.26,.235)]
    mats=[rock_material('196 weathered stone '+str(i),c) for i,c in enumerate(colors)]
    proto=[prototype(rng) for _ in range(19)];verts=[];faces=[];indices=[];counts={'small':0,'medium':0,'outcrop':0}
    for i in range(6600):
        y=float(rng.uniform(-720,115));x=float(rng.uniform(-125,110))
        # Clustered sediment fans rather than a uniform particle carpet.
        cluster=.55+.30*math.sin(y/23+math.sin(x/19)*2)+.15*math.cos(y/9-x/17)
        if rng.random()>cluster:continue
        if abs(x)<7:continue # never introduce large obstacles under the hooves
        p,f=proto[i%len(proto)];size=float(rng.uniform(.25,.95))
        if abs(x)>13 and rng.random()<.27:size=float(rng.uniform(1,2.3))
        if abs(x)>25 and rng.random()<.04:size=float(rng.uniform(3,5.2))
        kind='small' if size<1 else ('medium' if size<3 else 'outcrop');counts[kind]+=1
        angle=rng.uniform(0,math.tau);c,s=math.cos(angle),math.sin(angle)
        q=p*np.array((size,size*rng.uniform(.65,1.4),size*rng.uniform(.42,.85)))
        q[:,:2]=q[:,:2]@np.array([[c,-s],[s,c]])
        q+=np.array((x,y,bank_height(x,y)+.10*size));first=len(verts);verts.extend(q.tolist())
        faces.extend(tuple(first+j for j in face) for face in f);indices.extend([int(rng.integers(len(mats)))]*len(f))
    ob=mesh_object('MF196_clustered_rocky_margins',verts,faces,scene.collection,root)
    for m in mats:ob.data.materials.append(m)
    for poly,index in zip(ob.data.polygons,indices):poly.material_index=index
    # Keep the large A color/light treatment; add bound irregular chipped
    # strata at visible ground scale, not a global tonal banding shader.
    mat=land.data.materials[0].copy();mat.name='196 stony ochre ground';land.data.materials[0]=mat
    n,l=mat.node_tree.nodes,mat.node_tree.links;bs=n.get('Principled BSDF');old=bs.inputs['Base Color'].links[0].from_socket
    tc=n.new('ShaderNodeTexCoord');mapping=n.new('ShaderNodeVectorMath');mapping.operation='MULTIPLY';mapping.inputs[1].default_value=(1.8,.65,1)
    l.new(tc.outputs['Object'],mapping.inputs[0]);noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=1.4;noise.inputs['Detail'].default_value=2
    l.new(mapping.outputs[0],noise.inputs[0]);r=n.new('ShaderNodeValToRGB');r.color_ramp.elements[0].position=.36;r.color_ramp.elements[1].position=.64
    r.color_ramp.elements[0].color=(.13,.14,.135,1);r.color_ramp.elements[1].color=(.65,.49,.31,1)
    l.new(noise.outputs['Fac'],r.inputs[0]);mix=n.new('ShaderNodeMixRGB');mix.inputs[0].default_value=.25
    l.new(old,mix.inputs[1]);l.new(r.outputs[0],mix.inputs[2]);l.new(mix.outputs[0],bs.inputs['Base Color'])
    hidden=0
    for o in scene.objects:
        if o.name.startswith(('AS_grass_','AS_scrub_')) and not o.hide_render and o.parent==root:
            # Retain broken grass tufts among stones, not grassy uniform turf.
            if abs(o.location.x)<100 and math.sin(o.location.y*.71+o.location.x*.9)>.0:o.hide_render=True;hidden+=1
    return {'rocks':counts,'vertices':len(verts),'central_large_obstacle_exclusion_native':14,'grass_culled':hidden,'mats':mats}


def debris(scene,out,mats):
    import bpy
    from entrance189_groom import read_mdd,write_mdd,attach_cache
    from entrance_astra_world import mesh_object,FLOOR
    sys.path.insert(0,str(ROOT/'src/movie_factory/adapters/blender'))
    from source_gallop_math import LEGS,PERIOD
    horse=bpy.data.objects['MF185_gait_horse'];m=next(m for m in horse.modifiers if m.type=='MESH_CACHE')
    data=read_mdd(bpy.path.abspath(m.filepath));world=np.array(horse.matrix_world)
    groups={leg:horse.vertex_groups.get(values[1]) for leg,values in LEGS.items()}
    if any(g is None for g in groups.values()):raise ValueError('Hoof groups missing')
    ids={leg:[v.index for v in horse.data.vertices if any(w.group==g.index and w.weight>.5 for w in v.groups)] for leg,g in groups.items()}
    if any(len(a)<5 for a in ids.values()):raise ValueError('Hoof source selection failed')
    with np.load(base.BASE/'entrance196-inspect01/rig.npz') as z:roots=z['roots'].copy()
    rng=np.random.default_rng(19604);events=[];particles=[];proto,faces=prototype(rng)
    for leg,values in LEGS.items():
        # Actual lowest point confirms emission height and original phase
        # identifies contacts even if the low-height plateau spans frames.
        td=values[4]
        for cyc in range(-1,14):
            frame=int(round((cyc+td)*PERIOD))
            if not 0<=frame<144:continue
            points=np.asarray(data[frame,ids[leg]])@world[:3,:3].T+world[:3,3]
            low=points[np.argsort(points[:,2])[:max(5,len(points)//5)]].mean(0)
            ground=low.copy();ground[2]=FLOOR+.09;ground-=roots[frame,:3,3]
            events.append({'frame':frame+217,'leg':leg,'hoof_min_z':float(points[:,2].min()),'origin_ground':ground.tolist()})
            for j in range(11):
                radius=float(rng.uniform(.055,.17));origin=ground+np.array((rng.uniform(-.32,.32),rng.uniform(-.2,.2),radius*.5))
                velocity=np.array((rng.uniform(-14,14),rng.uniform(5,23),rng.uniform(8,17)))
                particles.append((frame,origin,velocity,radius,rng.uniform(-5,5),float(rng.uniform(0,math.tau))))
    verts=[];allfaces=[]
    for i,_ in enumerate(particles):verts.extend(proto.tolist());allfaces.extend(tuple(i*len(proto)+j for j in f) for f in faces)
    ob=mesh_object('MF196_hoof_ejected_pebbles',verts,allfaces,scene.collection, bpy.data.objects['AS_world_travel'])
    for mat in mats:ob.data.materials.append(mat)
    for i,poly in enumerate(ob.data.polygons):poly.material_index=(i//len(faces))%len(mats)
    def frames():
        for frame in range(144):
            rows=[]
            for birth,origin,v,radius,spin,angle in particles:
                age=(frame-birth)/24
                if age<0 or age>1.5:
                    rows.append(np.repeat((origin+np.array((0,0,-8)))[None],len(proto),axis=0));continue
                center=ballistic(origin,v,age,radius);a=angle+spin*min(age,.7);c,s=math.cos(a),math.sin(a)
                q=proto*radius;q[:,[0,2]]=q[:,[0,2]]@np.array([[c,-s],[s,c]])
                rows.append(q+center)
            yield np.concatenate(rows).astype(np.float32)
    path=out/'debris.mdd';write_mdd(path,144,len(verts),frames());attach_cache(ob,path)
    (out/'debris-events.json').write_text(json.dumps(events,indent=2)+'\n')
    return {'events':len(events),'particles':len(particles),'max_event_hoof_height_error':max(abs(e['hoof_min_z']-FLOOR) for e in events),
            'method':'Original source contact phases, actual hoof vertex origins, seeded ballistic flight and one dissipative bounce in translating ground coordinates; not rigid-body collision simulation'}


def validate(job):
    if job!={'operation':'build02'}:raise ValueError('Fixed integrated build only')
    out=base.BASE/'entrance196-build02'
    if out.exists() or base.digest(SOURCE)!=SOURCE_SHA:raise ValueError('Changed source or existing evidence')
    r=json.loads((SOURCE.parent/'result.json').read_text())
    for row in r['caches']:
        p=(SOURCE.parent/row['path']).resolve()
        if not p.is_relative_to(base.BASE.resolve()) or base.digest(p)!=row['sha256']:raise ValueError('Cache mismatch')
    return out


def main():
    import bpy
    out=validate(json.loads(Path(sys.argv[sys.argv.index('--')+1]).read_text()))
    out.mkdir();(out/'handler.py').write_bytes(Path(__file__).read_bytes())
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE),load_ui=False,use_scripts=False);base.check_protected();scene=bpy.context.scene
    report={'source_sha256':SOURCE_SHA,'motion':motion(scene,out)}
    scene.frame_set(217);bpy.context.view_layer.update()
    report['terrain']=terrain(scene,out);report['debris']=debris(scene,out,report['terrain'].pop('mats'))
    caches=[]
    for o in scene.objects:
        for m in o.modifiers:
            if m.type=='MESH_CACHE':
                p=Path(bpy.path.abspath(m.filepath)).resolve()
                if not p.is_relative_to(base.BASE.resolve()):raise ValueError('External cache')
                caches.append({'object':o.name,'path':os.path.relpath(p,out),'sha256':base.digest(p),'start':m.frame_start});m.filepath=str(p)
    scene.frame_set(217);scene.frame_start=217;scene.frame_end=360;base.check_protected();bpy.context.preferences.filepaths.save_version=0
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'scene.blend'),compress=True);bpy.ops.file.make_paths_relative();bpy.ops.wm.save_as_mainfile(filepath=str(out/'scene.blend'),compress=True)
    report.update(native_sha256=base.digest(out/'scene.blend'),caches=caches,visual_gate='NOT_RUN')
    (out/'result.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='caches'}),flush=True)


if __name__=='__main__':main()
