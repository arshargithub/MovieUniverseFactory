"""Read-only anatomical-space crown/contact inspection, no sculpt or hair edit."""
import json,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import wardrobe_motion178 as base

def main():
    import bpy
    from entrance189_groom import read_mdd
    from wardrobe_motion178_controls import render_geometry_paused
    if json.loads(Path(sys.argv[sys.argv.index('--')+1]).read_text())!={'operation':'head20'}:raise ValueError('Fixed contact inspection')
    source=base.BASE/'entrance201-opening17/scene.blend';out=base.BASE/'entrance201-head20';r=json.loads((source.parent/'result.json').read_text())
    if out.exists() or base.digest(source)!=r['native_sha256']:raise ValueError('Source/output')
    out.mkdir();(out/'handler.py').write_bytes(Path(__file__).read_bytes());bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False);scene=bpy.context.scene;rig=bpy.data.objects['MF_body156_fit_rig']
    names=('MF_natural147_hair_long hair main','MF_natural147_hair_long hair strands')
    with render_geometry_paused():
        for n in names:bpy.data.objects[n].hide_viewport=False
        for f in (289,360):
            scene.frame_set(f);bpy.context.view_layer.update();head=np.array(rig.matrix_world@rig.pose.bones['MF185_head'].matrix);inv=np.linalg.inv(head);arrays={}
            for j,n in enumerate(names):
                ob=bpy.data.objects[n];ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get())
                if ob.type=='CURVES':
                    attr=ev.data.attributes.get('position')
                    if attr is None:raise ValueError('No native guide positions')
                    p=np.empty(len(attr.data)*3,np.float32);attr.data.foreach_get('vector',p);p=p.reshape(-1,3)
                else:
                    me=ev.to_mesh();p=np.empty(len(me.vertices)*3,np.float32);me.vertices.foreach_get('co',p);p=p.reshape(-1,3);ev.to_mesh_clear()
                m=inv@np.array(ob.matrix_world);p=p@m[:3,:3].T+m[:3,3];arrays['hair'+str(j)]=p[p[:,1]>.35]
            ob=bpy.data.objects['MF185_moving_shawl'];mod=next(m for m in ob.modifiers if m.type=='MESH_CACHE');a=read_mdd(bpy.path.abspath(mod.filepath));m=inv@np.array(ob.matrix_world);arrays['cloth']=np.asarray(a[f-int(mod.frame_start),:2501])@m[:3,:3].T+m[:3,3]
            np.savez_compressed(out/f'crown-{f}.npz',**arrays)
    records=[];route=base.BASE/'entrance201-route16/scene.blend'
    if base.digest(route)!='0e108be33bd395e4a9a939881677bdce4d4fdb3c8c5a3e739567d5b4f8cb01f9':raise ValueError('Route changed')
    bpy.ops.wm.open_mainfile(filepath=str(route),load_ui=False,use_scripts=False);scene=bpy.context.scene;rig=bpy.data.objects['MF_body156_fit_rig'];ob=bpy.data.objects['MF185_moving_shawl']
    with render_geometry_paused():
        for f in (361,385,457,552):
            scene.frame_set(f);bpy.context.view_layer.update();resolved=ob.parent.matrix_world@ob.matrix_parent_inverse@ob.matrix_basis
            records.append({'frame':f,'cached_world':[list(x) for x in ob.matrix_world],'resolved_world':[list(x) for x in resolved], 'resolved_head_local':[list(x) for x in resolved.inverted()@rig.matrix_world@rig.pose.bones['MF185_head'].matrix]})
    (out/'result.json').write_text(json.dumps({'source_sha256':r['native_sha256'],'native_modified':False,'route_parent_control':records},indent=2)+'\n');base.check_protected()

if __name__=='__main__':main()
