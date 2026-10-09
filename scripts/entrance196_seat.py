"""Respect the scanned rock's usable orientation and protect the full route width."""
import json,math,os,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import wardrobe_motion178 as base

def main():
    import bpy
    from mathutils import Euler
    from entrance188_ground import bank_height
    if json.loads(Path(sys.argv[sys.argv.index('--')+1]).read_text())!={'operation':'seat17'}:raise ValueError('Fixed seating correction required')
    source=base.BASE/'entrance196-compose13/scene.blend';out=base.BASE/'entrance196-seat17'
    if out.exists() or base.digest(source)!='e216d9b959fc7ceeff73fb2ea6c450b6749408e498878081213112efbfd42169':raise ValueError('Source changed')
    out.mkdir();(out/'handler.py').write_bytes(Path(__file__).read_bytes())
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False);scene=bpy.context.scene;scene.frame_set(217);base.check_protected()
    rng=np.random.default_rng(19617);rows=[];meshes={}
    for ob in scene.objects:
        if not ob.name.startswith(('MF196_rock_cluster_','MF196_scanned_scree_','MF196_path_chip_')):continue
        if ob.data.name not in meshes:meshes[ob.data.name]=np.array([v.co[:] for v in ob.data.vertices])
        p=meshes[ob.data.name];is_chip=ob.name.startswith('MF196_path_chip_')
        ob.rotation_euler=(rng.uniform(.65,1.9),rng.uniform(-.6,.6),rng.uniform(0,math.tau))
        if not is_chip:ob.scale.z*=.72
        q=(p*np.array(ob.scale))@np.array(ob.rotation_euler.to_matrix()).T
        lo=q.min(0);hi=q.max(0);x,y=ob.location.x,ob.location.y
        # Check the actual transformed surface extent, not centre placement.
        corridor=4.2 if is_chip else 5.2
        if x>0:x=max(x,corridor-lo[0])
        else:x=min(x,-corridor-hi[0])
        z=bank_height(x,y)-lo[2]-(hi[2]-lo[2])*(.30 if not is_chip else .44)
        ob.location=(x,y,z)
        rows.append({'name':ob.name,'inner_edge':float(x+lo[0] if x>0 else -(x+hi[0])),'surface_height':float(hi[2]-lo[2]),'chip':is_chip})
    if min(r['inner_edge'] for r in rows)<4.19:raise ValueError('New stone enters hoof corridor')
    caches=[]
    for ob in scene.objects:
        for m in ob.modifiers:
            if m.type=='MESH_CACHE':
                p=Path(bpy.path.abspath(m.filepath)).resolve();m.filepath=str(p);caches.append({'object':ob.name,'path':os.path.relpath(p,out),'sha256':base.digest(p),'start':m.frame_start})
    (out/'rock-clearance.json').write_text(json.dumps({'rows':rows,'minimum_new_stone_abs_x':min(r['inner_edge'] for r in rows),'scope':'Actual transformed vertices, static-x opening only; not arbitrary later route'},indent=2)+'\n')
    base.check_protected();bpy.context.preferences.filepaths.save_version=0
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'scene.blend'),compress=True);bpy.ops.file.make_paths_relative();bpy.ops.wm.save_as_mainfile(filepath=str(out/'scene.blend'),compress=True)
    (out/'result.json').write_text(json.dumps({'source_sha256':base.digest(source),'native_sha256':base.digest(out/'scene.blend'),'caches':caches,'reseated_rocks':len(rows),'motion_unchanged_from':'entrance196-build02','visual_gate':'NOT_RUN'},indent=2)+'\n')

if __name__=='__main__':main()
