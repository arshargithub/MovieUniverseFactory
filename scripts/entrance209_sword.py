"""Source-pinned, closed-enum prop operations. No external executable payload."""
import json
import sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import wardrobe_motion178 as base

SOURCES = {
    'opening': ('entrance207-opening09', '616d218533c2fded2488cd2cce83947c67f497ad50cb75adb3c549bc12715c63'),
    'route': ('entrance207-threat10', '3c03a3f58d57854f959cc0478089b6d8256322a07a3154fc4529405fd1441fb1'),
}
OPS = {'inspect01': 'route', 'inspect02': 'opening', 'opening03':'opening', 'route04':'route'}

def validate(job):
    if not isinstance(job, dict) or set(job) != {'operation'} or job['operation'] not in OPS:
        raise ValueError('Closed209 operation only')

def load(kind):
    import bpy
    folder, sha = SOURCES[kind]
    src = base.BASE / folder
    if base.digest(src / 'scene.blend') != sha:
        raise ValueError('Source changed')
    record = json.loads((src / 'result.json').read_text())
    for row in record['caches']:
        path = (src / row['path']).resolve()
        if not path.is_relative_to(base.BASE.resolve()) or base.digest(path) != row['sha256']:
            raise ValueError('Cache source changed')
    bpy.ops.wm.open_mainfile(filepath=str(src / 'scene.blend'), load_ui=False, use_scripts=False)
    base.check_protected()
    return bpy.context.scene

def inspect(scene, out):
    import bpy
    from wardrobe_motion178_controls import render_geometry_paused
    rig = bpy.data.objects['MF_body156_fit_rig']
    rows = []
    with render_geometry_paused():
        for f in (361,390,409,427,472,550,648):
            scene.frame_set(f)
            bpy.context.view_layer.update()
            rows.append({'frame':f, 'world':np.array(rig.matrix_world).tolist(),
                         'bones':{n:np.array(rig.pose.bones[n].matrix).tolist()
                                  for n in ('pelvis','spine','chest','thigh.L','thigh.R')}})
    scene.frame_set(427)
    bpy.context.view_layer.update()
    objects = []
    for ob in scene.objects:
        if ob.hide_render or ob.type != 'MESH':
            continue
        if any(t in ob.name.lower() for t in ('belt','harness','tunic','pants','shawl','saddle','horse')) or ob.name == 'MF_studio_adult_body':
            objects.append({'name':ob.name, 'vertices':len(ob.data.vertices),
                            'parent':ob.parent.name if ob.parent else None,
                            'bounds':[list(ob.matrix_world @ __import__('mathutils').Vector(v)) for v in ob.bound_box],
                            'modifiers':[(m.name,m.type) for m in ob.modifiers]})
    (out/'inspection.json').write_text(json.dumps({'rig':rows,'objects':objects},indent=2)+'\n')
    print(json.dumps(objects,indent=2),flush=True)

def main():
    job = json.loads(Path(sys.argv[sys.argv.index('--') + 1]).read_text())
    validate(job)
    out = base.BASE / ('entrance209-' + job['operation'])
    if out.exists():
        raise ValueError('Preserve previous output')
    out.mkdir()
    (out/'handler.py').write_bytes(Path(__file__).read_bytes())
    scene = load(OPS[job['operation']])
    if job['operation'] in ('opening03','route04'):
        import bpy
        from entrance209_prop import construct,animate
        from entrance205_actor import save
        kind=OPS[job['operation']]
        root,sheath,straps,rings=construct()
        record=animate(scene,root,straps,rings,kind)
        record.update(source_sha256=SOURCES[kind][1],protected_actor_animation='unchanged')
        scene.frame_set(277 if kind=='opening' else 427)
        save(scene,out,record)
        for ob in scene.objects:
            for m in ob.modifiers:
                if m.type in ('SMOOTH','CORRECTIVE_SMOOTH','SUBSURF'):m.show_viewport=False
        scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=8;scene.render.use_persistent_data=False
        scene.render.resolution_x=432;scene.render.resolution_y=768;scene.render.resolution_percentage=100
        for f in ((245,277,300) if kind=='opening' else (390,427,454,520,620)):
            scene.frame_set(f);scene.render.filepath=str(out/f'control-{f}.png');bpy.ops.render.render(write_still=True)
        print('209 prop controls complete',flush=True)
    elif job['operation']=='inspect01':
        inspect(scene, out)
    else:
        import bpy
        from wardrobe_motion178_controls import render_geometry_paused
        rig=bpy.data.objects['MF_body156_fit_rig']
        names=['MF_173_waist_belt','MF_studio_adult_body','MF185_gait_horse','MF185_gait_saddle','MF185_fitted_upper_tunic','MF185_moving_shawl','MF185_free_lower_tunic']
        with render_geometry_paused():
            scene.frame_set(277)
            for name in names:bpy.data.objects[name].hide_viewport=False
            bpy.context.view_layer.update()
            data={}
            inv=np.linalg.inv(np.array(rig.matrix_world))
            for name in names:
                ob=bpy.data.objects[name];ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());m=ev.to_mesh();M=inv@np.array(ev.matrix_world)
                p=np.array([v.co[:] for v in m.vertices]);p=p@M[:3,:3].T+M[:3,3];m.calc_loop_triangles()
                data[name+'_verts']=p;data[name+'_tris']=np.array([t.vertices[:] for t in m.loop_triangles]);ev.to_mesh_clear()
            data['pelvis']=np.array(rig.pose.bones['pelvis'].matrix);data['pelvis_rest']=np.array(rig.data.bones['pelvis'].matrix_local)
            np.savez_compressed(out/'geometry.npz',**data)
        print('209 geometry exported',flush=True)
    base.check_protected()

if __name__ == '__main__':
    main()
