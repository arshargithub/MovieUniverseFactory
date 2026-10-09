"""Modest head-cover advance in anatomical coordinates; preserved wrap courses."""
import numpy as np

def cover_points(points,head_matrix):
    p=np.array(points,float,copy=True)
    if len(p)!=7205:raise ValueError('Expected sewn three-panel topology')
    inverse=np.linalg.inv(head_matrix);q=p[:2501]@inverse[:3,:3].T+inverse[:3,3]
    # Stable pattern coordinates: front hem is row0 of41x61, the two rear
    # wrap courses are untouched. Local head +Y is up and +Z is forward.
    row=np.repeat(np.arange(41),61)
    w=np.clip(1-row/15,0,1);w=w*w*(3-2*w)
    height=np.clip((q[:,1]-.3)/.8,0,1);height=height*height*(3-2*height);w*=height
    angle=np.deg2rad(9)*w;c=np.cos(angle);s=np.sin(angle)
    center=np.array([0.,.7,-.2]);r=q-center
    shifted=np.column_stack((r[:,0],c*r[:,1]-s*r[:,2],s*r[:,1]+c*r[:,2]))+center
    p[:2501]=shifted@head_matrix[:3,:3].T+head_matrix[:3,3]
    if np.linalg.norm(p-np.asarray(points),axis=1).max()>.33:raise ValueError('Cover exceeds modest fit change')
    return p.astype(np.float32)

def apply_opening(out):
    import bpy
    from pathlib import Path
    import wardrobe_motion178 as base
    from entrance189_groom import read_mdd,write_mdd,attach_cache
    from wardrobe_motion178_controls import render_geometry_paused
    ob=bpy.data.objects['MF185_moving_shawl'];rig=bpy.data.objects['MF_body156_fit_rig'];scene=bpy.context.scene
    m=next(m for m in ob.modifiers if m.type=='MESH_CACHE');source=Path(bpy.path.abspath(m.filepath));a=read_mdd(source);start=int(m.frame_start);heads=[]
    with render_geometry_paused():
        for f in range(217,361):
            scene.frame_set(f);bpy.context.view_layer.update();heads.append(np.array(ob.matrix_world.inverted()@rig.matrix_world@rig.pose.bones['MF185_head'].matrix))
    def frames():
        for k,p in enumerate(a):
            i=start+k-217
            yield cover_points(p,heads[i]) if 0<=i<144 else np.array(p,dtype=np.float32)
    path=out/'shawl-cover.mdd';write_mdd(path,len(a),a.shape[1],frames());attach_cache(ob,path,start)
    return {'source_sha256':base.digest(source),'maximum_rotation_degrees':9,'scope':'Front headfall only, feathered toward crown/rear and ear level; two outer wrap courses unchanged','new_simulation':False,'visual_gate':'NOT_RUN'}
