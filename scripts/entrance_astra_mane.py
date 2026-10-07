"""Recover existing artist-authored mane from the admitted demonstration rig."""
import json
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import wardrobe_motion178 as base


def main():
    import bpy
    import numpy as np
    from mathutils import Matrix
    from wardrobe_riding_fit import HORSE,HORSE_SHA
    args=sys.argv[sys.argv.index('--')+1:]
    job=json.loads(Path(args[0]).read_text()) if len(args)==1 else None
    if job not in ({'operation':'mane-probe01'},{'operation':'mane-cache01'}):
        raise ValueError('Fixed mane probe required')
    if base.digest(HORSE)!=HORSE_SHA:raise ValueError('Horse source changed')
    out=base.BASE/('entrance-astra-'+job['operation'])
    if out.exists():raise ValueError('Preserve evidence')
    out.mkdir();(out/'handler.py').write_bytes(Path(__file__).read_bytes())
    bpy.ops.wm.open_mainfile(filepath=str(HORSE),load_ui=False,use_scripts=False)
    scene=bpy.context.scene;horse=bpy.data.objects['horse']
    for ob in scene.objects:
        if ob.type in ('MESH','CURVE','CURVES') and ob!=horse:ob.hide_viewport=True
    for mod in horse.modifiers:
        if mod.type=='PARTICLE_SYSTEM':
            mod.show_viewport=mod.show_render=mod.particle_system.name=='mane'
    scene.frame_set(0);bpy.context.view_layer.update()
    transform=Matrix.Translation((0,.20,-6.85))@Matrix.Scale(8.3,4)@Matrix.Translation((0,-2.52,-1.57))
    origin=scene.objects['horse diagnostic path'].matrix_world.translation.copy()
    rows=[];samples=[]
    frames=(0,12,48,143) if job['operation']=='mane-probe01' else range(144)
    for frame in frames:
        scene.frame_set(frame);bpy.context.view_layer.update()
        ev=horse.evaluated_get(bpy.context.evaluated_depsgraph_get());ps=ev.particle_systems['mane']
        count=len(ps.particles);steps=len(ps.particles[0].hair_keys)
        raw=np.array([[ps.co_hair(ev,particle_no=i,step=k)[:] for k in range(steps)] for i in range(count)])
        shift=scene.objects['horse diagnostic path'].matrix_world.translation-origin
        matrix=np.array(transform@Matrix.Translation(-shift))
        points=raw@matrix[:3,:3].T+matrix[:3,3]
        samples.append(points)
        rows.append({'frame':frame,'count':count,'steps':steps,'bounds':[points.reshape(-1,3).min(0).tolist(),points.reshape(-1,3).max(0).tolist()],
                     'root_example':points[0,0].tolist(),'tip_example':points[0,-1].tolist()})
    np.savez_compressed(out/'samples.npz',points=np.array(samples))
    (out/'result.json').write_text(json.dumps({'source_sha256':HORSE_SHA,'samples':rows},indent=2)+'\n')
    print(json.dumps(rows),flush=True)


if __name__=='__main__':main()
