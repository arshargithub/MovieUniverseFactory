"""Pinned native209 replay, complete rendering and actual-surface prop controls."""
import json,sys,time,hashlib
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import wardrobe_motion178 as base
OPS={'proof05':('opening03',(245,277,300),False),
     'proof06':('route04',(390,427,454,520,620),False),
     'opening07':('opening03',tuple(f for f in range(217,361) if f not in (245,277,300)),True),
     'route08':('route04',tuple(f for f in range(361,649) if f not in (390,427,454,520,620)),True)}

def validate(j):
    if not isinstance(j,dict) or set(j)!={'operation'} or j['operation'] not in OPS:raise ValueError('Closed209 review')

def protected(scene):
    import bpy
    from worker import action_channels
    h=hashlib.sha256()
    for m in sorted(bpy.data.meshes,key=lambda x:x.name):
        if m.name.startswith('MF209_'):continue
        h.update(m.name.encode())
        for c,p,w,dt in [(m.vertices,'co',3,np.float32),(m.loops,'vertex_index',1,np.int32),(m.polygons,'loop_total',1,np.int32)]:
            a=np.empty(len(c)*w,dtype=dt);c.foreach_get(p,a);h.update(a.tobytes())
        if m.shape_keys:
            for k in m.shape_keys.key_blocks:
                a=np.empty(len(k.data)*3,dtype=np.float32);k.data.foreach_get('co',a);h.update(k.name.encode());h.update(a.tobytes())
    actions=[(a.name,[(f.data_path,f.array_index,[(list(k.co),list(k.handle_left),list(k.handle_right),k.interpolation) for k in f.keyframe_points]) for f in action_channels(a)]) for a in sorted(bpy.data.actions,key=lambda x:x.name) if not a.name.startswith('MF209_')]
    return {'geometry_shapes':h.hexdigest(),'actions':hashlib.sha256(json.dumps(actions,sort_keys=True).encode()).hexdigest()}

def collision(scene):
    import bpy
    from mathutils.bvhtree import BVHTree
    from mathutils import Vector
    deps=bpy.context.evaluated_depsgraph_get()
    def tree(ob):
        ev=ob.evaluated_get(deps);m=ev.to_mesh();m.calc_loop_triangles()
        verts=[ev.matrix_world@v.co for v in m.vertices];tris=[tuple(t.vertices) for t in m.loop_triangles]
        b=BVHTree.FromPolygons(verts,tris,all_triangles=True);ev.to_mesh_clear();return b,verts
    sword,verts=tree(bpy.data.objects['MF209_curved_scabbard']);rows={}
    for name in ('MF_studio_adult_body','MF185_gait_horse','MF185_gait_saddle','MF185_fitted_upper_tunic','MF185_free_lower_tunic','MF185_moving_shawl'):
        other,_=tree(bpy.data.objects[name]);pairs=sword.overlap(other)
        near=[other.find_nearest(v)[3] for v in verts]
        rows[name]={'intersecting_triangle_pairs':len(pairs),'minimum_sample_distance_scene_units':min(near)}
    return rows

def main():
    import bpy
    from wardrobe_motion178_controls import render_geometry_paused
    from entrance209_sword import SOURCES
    j=json.loads(Path(sys.argv[sys.argv.index('--')+1]).read_text());validate(j);op=j['operation'];folder,frames,full=OPS[op]
    src=base.BASE/('entrance209-'+folder);out=base.BASE/('entrance209-'+op);r=json.loads((src/'result.json').read_text())
    if out.exists() or base.digest(src/'scene.blend')!=r['native_sha256']:raise ValueError('Source/output')
    if full:
        admission=json.loads((src/'internal-review.json').read_text())
        if admission.get('status')!='PROCEED_TO_FULL_MOTION' or admission['source_sha256']!=r['native_sha256']:raise ValueError('Missing visual admission')
    for row in r['caches']:
        p=(src/row['path']).resolve()
        if not p.is_relative_to(base.BASE.resolve()) or base.digest(p)!=row['sha256']:raise ValueError('Cache changed')
    out.mkdir();(out/'handler.py').write_bytes(Path(__file__).read_bytes())
    kind='opening' if folder.startswith('opening') else 'route';old,sha=SOURCES[kind]
    oldpath=base.BASE/old/'scene.blend'
    if base.digest(oldpath)!=sha:raise ValueError('Protected source changed')
    bpy.ops.wm.open_mainfile(filepath=str(oldpath),load_ui=False,use_scripts=False)
    before=protected(bpy.context.scene)
    bpy.ops.wm.open_mainfile(filepath=str(src/'scene.blend'),load_ui=False,use_scripts=False);scene=bpy.context.scene
    if protected(scene)!=before:raise ValueError('Protected original geometry/actions changed')
    base.check_protected()
    for ob in scene.objects:
        for m in ob.modifiers:
            if m.type in ('SMOOTH','CORRECTIVE_SMOOTH','SUBSURF'):m.show_viewport=False
    scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=8;scene.render.use_persistent_data=False
    scene.render.resolution_x=432;scene.render.resolution_y=768;scene.render.resolution_percentage=100
    rig=bpy.data.objects['MF_body156_fit_rig'];names=('pelvis','chest','MF185_neck','MF185_head','hand.L','hand.R','foot.L','foot.R');rows=[]
    for f in frames:
        t=time.monotonic();scene.frame_set(f);bpy.context.view_layer.update();p=out/f'frame-{f-217:04d}.png';scene.render.filepath=str(p)
        if bpy.ops.render.render(write_still=True)!={'FINISHED'}:raise ValueError('Render failed')
        row=dict(index=f-217,source_frame=f,sha256=base.digest(p),seconds=time.monotonic()-t,camera=np.array(scene.camera.matrix_world).tolist(),lens=scene.camera.data.lens,pose={n:np.array(rig.matrix_world@rig.pose.bones[n].matrix).tolist() for n in names})
        if not full:row['surface_control']=collision(scene)
        rows.append(row)
        tmp=out/'progress.tmp';tmp.write_text(json.dumps(dict(source_sha256=r['native_sha256'],frames=rows,complete=False),indent=2)+'\n');tmp.replace(out/'progress.json')
        print('209 FRAME',op,f,round(row['seconds'],2),flush=True)
    base.check_protected();(out/'result.json').write_text(json.dumps(dict(source_sha256=r['native_sha256'],frames=rows,protected_geometry_actions=before,fps=24,resolution=[432,768],visual_gate='NOT_RUN'),indent=2)+'\n')

if __name__=='__main__':main()
