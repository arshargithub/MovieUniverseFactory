"""Remove legacy ground fade and protect a readable action corridor."""
import json,os,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import wardrobe_motion178 as base

def main():
    import bpy
    if json.loads(Path(sys.argv[sys.argv.index('--')+1]).read_text())!={'operation':'integrate36'}:raise ValueError('Fixed integration only')
    source=base.BASE/'entrance196-outcrops30/scene.blend';out=base.BASE/'entrance196-integrate36';r=json.loads((source.parent/'result.json').read_text())
    if out.exists() or base.digest(source)!=r['native_sha256']:raise ValueError('Unbound source')
    out.mkdir();(out/'handler.py').write_bytes(Path(__file__).read_bytes())
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False);scene=bpy.context.scene;scene.frame_set(217);bpy.context.view_layer.update();base.check_protected()
    mat=bpy.data.objects['AS_valley_landform'].data.materials[0];n,l=mat.node_tree.nodes,mat.node_tree.links
    l.new(n.get('Principled BSDF').outputs[0],n.get('Material Output').inputs['Surface'])
    hidden=[];meshes={};rows=[]
    for ob in scene.objects:
        if not ob.name.startswith(('MF196_rock_cluster_','MF196_scanned_scree_','MF196_path_chip_')):continue
        if ob.data.name not in meshes:meshes[ob.data.name]=np.array([v.co[:] for v in ob.data.vertices])
        m=np.array(ob.matrix_world);q=meshes[ob.data.name]@m[:3,:3].T+m[:3,3]
        edge=float(np.min(abs(q[:,0])));size=float(np.max(np.ptp(q,axis=0)))
        # Keep small gravel near the hoof route. Larger boulders need both
        # geometric clearance and visual breathing room around the gait.
        if size>1.2 and edge<18:
            ob.hide_render=True;hidden.append(ob.name)
        else:rows.append({'object':ob.name,'inner_edge':edge,'size':size})
    (out/'corridor.json').write_text(json.dumps({'hidden':hidden,'visible':rows,'scope':'Straight opening only; small gravel retains4.2native clearance, rocks larger than1.2native require18native'},indent=2)+'\n')
    caches=[]
    for ob in scene.objects:
        for mod in ob.modifiers:
            if mod.type=='MESH_CACHE':
                p=Path(bpy.path.abspath(mod.filepath)).resolve();mod.filepath=str(p);caches.append({'object':ob.name,'path':os.path.relpath(p,out),'sha256':base.digest(p),'start':mod.frame_start})
    base.check_protected();bpy.context.preferences.filepaths.save_version=0
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'scene.blend'),compress=True);bpy.ops.file.make_paths_relative();bpy.ops.wm.save_as_mainfile(filepath=str(out/'scene.blend'),compress=True)
    (out/'result.json').write_text(json.dumps({'source_sha256':base.digest(source),'native_sha256':base.digest(out/'scene.blend'),'caches':caches,'large_rocks_culled':len(hidden),'motion_unchanged_from':'entrance196-build02','visual_gate':'NOT_RUN'},indent=2)+'\n')

if __name__=='__main__':main()
