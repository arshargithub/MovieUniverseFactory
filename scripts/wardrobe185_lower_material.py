"""Gravity/rest-metric control independent of actor or collision surfaces."""
import json
from pathlib import Path
import numpy as np


def area(points,faces):
    t=np.asarray(points)[np.asarray(faces)]
    return float(np.sum(np.linalg.norm(np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]),axis=1)+
        np.linalg.norm(np.cross(t[:,2]-t[:,0],t[:,3]-t[:,0]),axis=1))*.5)


def run(out):
    import bpy
    from wardrobe_motion178 import BASE,digest
    from wardrobe185_lower_cloth import panel,profile,sample,COMPLETE_LAYOUT_SHA
    from wardrobe185_lower_drape import SCALE
    from wardrobe_shawl180_cache import cache
    source=BASE/'wardrobe185-lowerdress14/initial-layout.npz'
    if digest(source)!=COMPLETE_LAYOUT_SHA:raise ValueError('Unbound material control')
    (out/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
    with np.load(source,allow_pickle=False) as d:
        rest=d['rest']*SCALE;faces=d['faces'];pins=d['pin_indices'];weights=d['pin_weights']
    surface_area=area(rest,faces);masses={'inherited':.3,'area_based':.24*surface_area/len(rest)}
    records={};edges=np.unique(np.sort(np.concatenate([faces[:,[i,(i+1)%4]] for i in range(4)]),axis=1),axis=0)
    lengths=np.linalg.norm(rest[edges[:,0]]-rest[edges[:,1]],axis=1)
    for label,mass in masses.items():
        bpy.ops.wm.read_factory_settings(use_empty=True);scene=bpy.context.scene;scene.render.fps=24
        scene.gravity=(0,0,-9.81);scene.unit_settings.scale_length=1.
        ob=panel('Lower gravity control',rest,faces);ob.shape_key_add(name='Basis');key=ob.shape_key_add(name='Rest metric')
        key.data.foreach_set('co',rest.astype(np.float32).ravel())
        group=ob.vertex_groups.new(name='support')
        for i,w in zip(pins,weights):group.add([int(i)],float(w),'REPLACE')
        cache(ob,np.repeat(rest[None],120,axis=0),out/(label+'.mdd'))
        weld=ob.modifiers.new('Explicit rest evaluation','WELD');weld.merge_threshold=1e-7
        mod=profile(ob);mod.settings.rest_shape_key=key;mod.settings.mass=mass;mod.settings.quality=48
        mod.collision_settings.use_collision=False;mod.collision_settings.use_self_collision=False
        mod.point_cache.frame_end=120;frames=[];metrics=[]
        for frame in range(1,121):
            scene.frame_set(frame);bpy.context.view_layer.update();q=sample(ob);frames.append(q)
            if frame%24==0:
                ratio=np.linalg.norm(q[edges[:,0]]-q[edges[:,1]],axis=1)/lengths
                row={'frame':frame,'edge_quantiles':np.quantile(ratio,[.01,.5,.99,1]).tolist()};metrics.append(row)
                print('Lower gravity material',label,json.dumps(row),flush=True)
        np.savez_compressed(out/(label+'.npz'),frames=np.array(frames),faces=faces,rest=rest)
        records[label]={'mass_per_vertex':mass,'total_mass_setting':mass*len(rest),'metrics':metrics}
    (out/'result.json').write_text(json.dumps({'source_sha256':COMPLETE_LAYOUT_SHA,'area_m2':surface_area,
        'authored_density_kg_m2':.24,'density_not_measured_textile':True,'cases':records,
        'scope':'Same hanging cut/waist and gravity; no actor, wind, external or self contacts. Material diagnostic only.',
        'visual_gate':'NOT_RUN'},indent=2)+'\n')
