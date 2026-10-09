"""Fixed, source-bound entrance196 inspection and derivative jobs.

No caller-supplied paths, code or parameters. Protected originals are read-only.
"""
import json
import sys
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import wardrobe_motion178 as base
SOURCE=base.BASE/'entrance193-bind03/scene.blend'
SOURCE_SHA='6f0f647b6874a0f07c585c43d8685b1e8a5c3de7621f116148c51c75768df639'


def validate(job):
    if job!={'operation':'inspect01'}:raise ValueError('Fixed196 inspection required')
    out=base.BASE/'entrance196-inspect01'
    if out.exists() or SOURCE.is_symlink() or base.digest(SOURCE)!=SOURCE_SHA:raise ValueError('Source mismatch or existing evidence')
    r=json.loads((SOURCE.parent/'result.json').read_text())
    for row in r['caches']:
        p=(SOURCE.parent/row['path']).resolve()
        if not p.is_relative_to(base.BASE.resolve()) or base.digest(p)!=row['sha256']:raise ValueError('Unbound cache')
    return out


def main():
    import bpy
    from wardrobe_motion178_controls import render_geometry_paused
    out=validate(json.loads(Path(sys.argv[sys.argv.index('--')+1]).read_text()))
    out.mkdir();(out/'handler.py').write_bytes(Path(__file__).read_bytes())
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE),load_ui=False,use_scripts=False)
    base.check_protected();scene=bpy.context.scene;rig=bpy.data.objects['MF_body156_fit_rig']
    names=[b.name for b in rig.pose.bones];matrices=[];bases=[];eulers=[];roots=[];cameras=[]
    with render_geometry_paused():
        for f in range(217,361):
            scene.frame_set(f);bpy.context.view_layer.update()
            matrices.append([np.array(rig.matrix_world@b.matrix) for b in rig.pose.bones])
            bases.append([np.array(b.matrix_basis) for b in rig.pose.bones])
            eulers.append([list((rig.matrix_world@b.matrix).to_euler('XYZ')) for b in rig.pose.bones])
            roots.append(np.array(bpy.data.objects['AS_world_travel'].matrix_world))
            cameras.append(np.array(scene.camera.matrix_world))
    np.savez_compressed(out/'rig.npz',names=names,matrices=matrices,bases=bases,eulers=eulers,roots=roots,cameras=cameras)
    objects=[]
    for ob in scene.objects:
        if ob.hide_render:continue
        if ob.name.startswith(('AS_valley','AS_world','MF188','MF189','MF185_gait')):
            objects.append({'name':ob.name,'type':ob.type,'parent':ob.parent.name if ob.parent else None,
                'location':list(ob.location),'scale':list(ob.scale),'materials':[s.material.name if s.material else None for s in ob.material_slots],
                'modifiers':[{'name':m.name,'type':m.type} for m in ob.modifiers]})
    e=np.rad2deg(np.unwrap(np.array(eulers),axis=0))
    summary={n:{'euler_range_degrees':np.ptp(e[:,names.index(n)],axis=0).tolist(),
                  'world_position_range':np.ptp(np.array(matrices)[:,names.index(n),:3,3],axis=0).tolist()}
             for n in ('pelvis','spine','chest','MF185_neck','MF185_head')}
    (out/'result.json').write_text(json.dumps({'source_sha256':SOURCE_SHA,'motion':summary,'objects':objects},indent=2)+'\n')
    print(json.dumps(summary),flush=True);base.check_protected()


if __name__=='__main__':main()
