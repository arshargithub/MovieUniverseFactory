"""Closed245 preserved-route audit against original218, excluding new scenery."""
import json,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import wardrobe_motion178 as base
def main():
    import bpy
    from wardrobe_motion178_controls import render_geometry_paused
    from worker import action_channels
    job=json.loads(Path(sys.argv[sys.argv.index('--')+1]).read_text())
    if job not in ({'operation':'audit'},{'operation':'audit02'}):raise ValueError('Closed differential audit')
    newer=job['operation']=='audit02'
    out=ROOT/'.runtime/art-direction/series01-finish245'/('route-audit02.json' if newer else 'route-audit01.json')
    if out.exists():raise ValueError('Preserve audit')
    rows=[]
    for folder,f in [('entrance218-route13',391),('finish245-route03' if newer else 'finish245-route02',499)]:
        src=base.BASE/folder;meta=json.loads((src/'result.json').read_text())
        if base.digest(src/'scene.blend')!=meta['native_sha256']:raise ValueError('Changed input')
        bpy.ops.wm.open_mainfile(filepath=str(src/'scene.blend'),load_ui=False,use_scripts=False);scene=bpy.context.scene
        # Entire preserved route: compare authored camera/root/rig channels,
        # not just one attractive pose. Native/cache evaluation is checked below.
        sample_frames=np.arange(391,649)+(0 if folder.startswith('entrance') else 108)
        authored={}
        for label,owner in [('camera',scene.camera),('lens',scene.camera.data),('rig',bpy.data.objects['MF_body156_fit_rig']),('travel',bpy.data.objects['MF205_shared_route_actor'])]:
            for fc in action_channels(owner.animation_data.action):
                authored[f'{label}:{fc.data_path}:{fc.array_index}']=np.array([fc.evaluate(int(q)) for q in sample_frames])
        with render_geometry_paused():
            camera_world=[]
            for q in sample_frames:
                scene.frame_set(int(q));bpy.context.view_layer.update()
                camera_world.append(np.array(scene.camera.matrix_world))
            scene.frame_set(f);bpy.context.view_layer.update()
            mats={o.name:np.array(o.matrix_world) for o in scene.objects}
            rig=bpy.data.objects['MF_body156_fit_rig'];bones={b.name:np.array(rig.matrix_world@b.matrix) for b in rig.pose.bones}
            lens=scene.camera.data.lens
        scene.frame_set(f);bpy.context.view_layer.update()
        mats={o.name:np.array(o.matrix_world) for o in scene.objects if not o.hide_viewport}
        geometry={};deps=bpy.context.evaluated_depsgraph_get()
        for n in ('MF185_gait_horse','MF185_moving_shawl','MF_studio_adult_body'):
            ob=bpy.data.objects[n]
            ev=ob.evaluated_get(deps);mesh=ev.to_mesh();v=np.empty(len(mesh.vertices)*3);mesh.vertices.foreach_get('co',v)
            v=v.reshape(-1,3);m=np.array(ev.matrix_world);geometry[n]=v@m[:3,:3].T+m[:3,3];ev.to_mesh_clear()
        cache={o.name:[dict(start=m.frame_start,mode=m.play_mode,eval=m.eval_frame) for m in o.modifiers if m.type=='MESH_CACHE'] for o in scene.objects if any(m.type=='MESH_CACHE' for m in o.modifiers)}
        scene.frame_set(364 if folder.startswith('entrance') else 451);bpy.context.view_layer.update()
        prefix={n:dict(location=list(bpy.data.objects[n].location),world=list(bpy.data.objects[n].matrix_world.translation),hidden=bpy.data.objects[n].hide_render) for n in ('MF205_shared_route_actor','MF_body156_camera','MF201_dramatic_dust','MF201_dramatic_dust.001')}
        rows.append(dict(mats=mats,bones=bones,lens=lens,cache=cache,prefix=prefix,geometry=geometry,authored=authored,camera_world=np.array(camera_world)))
    result={k:sorted([(n,float(np.max(abs(v-rows[1][k][n])))) for n,v in rows[0][k].items() if n in rows[1][k]],key=lambda x:-x[1])[:25] for k in ('mats','bones','geometry')}
    result['lenses']=[r['lens'] for r in rows];result['caches']=[r['cache'] for r in rows];result['prefix']=[r['prefix'] for r in rows]
    common=set(rows[0]['authored'])&set(rows[1]['authored'])
    # Report representation differences before deciding equivalence. A newly
    # keyed camera rotation is not automatically a changed camera pose.
    differences=sorted([(k,float(np.max(abs(rows[0]['authored'][k]-rows[1]['authored'][k])))) for k in common],key=lambda x:-x[1])
    result['preserved_route_authored_channels']=dict(frames=258,common_channels=len(common),
        removed=sorted(set(rows[0]['authored'])-set(rows[1]['authored'])),
        added=sorted(set(rows[1]['authored'])-set(rows[0]['authored'])),
        differences=differences,maximum_difference=max(v for _,v in differences),
        evaluated_camera_world_maximum_difference=float(np.max(abs(rows[0]['camera_world']-rows[1]['camera_world']))),
        interpretation='Diagnostic measurement only; inspect added channels and evaluated geometry before asserting preservation.')
    out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='caches'}))
if __name__=='__main__':main()
