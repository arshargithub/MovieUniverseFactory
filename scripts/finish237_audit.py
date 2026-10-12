"""Closed differential diagnosis: exact preserved route sample versus237."""
import json,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import wardrobe_motion178 as base
def main():
    import bpy
    from wardrobe_motion178_controls import render_geometry_paused
    job=json.loads(Path(sys.argv[sys.argv.index('--')+1]).read_text())
    if job!={'operation':'audit'}:raise ValueError('Closed differential audit')
    out=ROOT/'.runtime/art-direction/series01-finish237/route-audit04.json'
    if out.exists():raise ValueError('Preserve audit')
    rows=[]
    for folder,f in [('entrance218-route13',391),('finish237-route04',463)]:
        src=base.BASE/folder;meta=json.loads((src/'result.json').read_text())
        if base.digest(src/'scene.blend')!=meta['native_sha256']:raise ValueError('Changed input')
        bpy.ops.wm.open_mainfile(filepath=str(src/'scene.blend'),load_ui=False,use_scripts=False);scene=bpy.context.scene
        with render_geometry_paused():
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
        scene.frame_set(364 if folder.startswith('entrance') else 415);bpy.context.view_layer.update()
        prefix={n:dict(location=list(bpy.data.objects[n].location),world=list(bpy.data.objects[n].matrix_world.translation),hidden=bpy.data.objects[n].hide_render) for n in ('MF205_shared_route_actor','MF_body156_camera','MF201_dramatic_dust','MF201_dramatic_dust.001')}
        rows.append(dict(mats=mats,bones=bones,lens=lens,cache=cache,prefix=prefix,geometry=geometry))
    result={k:sorted([(n,float(np.max(abs(v-rows[1][k][n])))) for n,v in rows[0][k].items() if n in rows[1][k]],key=lambda x:-x[1])[:25] for k in ('mats','bones','geometry')}
    result['lenses']=[r['lens'] for r in rows];result['caches']=[r['cache'] for r in rows];result['prefix']=[r['prefix'] for r in rows]
    out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='caches'}))
if __name__=='__main__':main()
