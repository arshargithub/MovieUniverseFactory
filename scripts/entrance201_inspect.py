"""Fixed read-only source inspection for the integrated entrance continuation."""
import json,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import wardrobe_motion178 as base
SOURCES={'opening':('entrance200-seal17','0c898747a695db3e59ba8d8a9676961f306f91873c5f050e35d61f00d1a0623f'),
         'route':('entrance190-perspective29','e13c0ff6c4dd9f20b552b258d34ba8422b7883cfcb882abebdf174ce8e041983'),
         'prior':('entrance190-blink03',None)}

def main():
    import bpy
    from wardrobe_motion178_controls import render_geometry_paused
    from entrance190_rider import source_pose_frame
    job=json.loads(Path(sys.argv[sys.argv.index('--')+1]).read_text())
    if job!={'operation':'inspect01'}:raise ValueError('Fixed read-only inspection')
    out=base.BASE/'entrance201-inspect01'
    if out.exists():raise ValueError('Preserve evidence')
    out.mkdir();(out/'handler.py').write_bytes(Path(__file__).read_bytes())
    with np.load(base.BASE/'entrance190-rider09/route.npz') as z:route={k:z[k] for k in z.files}
    phases=[source_pose_frame(s) for s in route['source_frame'][::8]]
    records={}
    for key,(folder,sha) in SOURCES.items():
        p=base.BASE/folder/'scene.blend';receipt=json.loads((p.parent/'result.json').read_text());sha=sha or receipt['native_sha256']
        if base.digest(p)!=sha:raise ValueError('Source changed')
        bpy.ops.wm.open_mainfile(filepath=str(p),load_ui=False,use_scripts=False);scene=bpy.context.scene;base.check_protected()
        rig=bpy.data.objects['MF_body156_fit_rig'];names=[b.name for b in rig.pose.bones];bases=[];matrices=[];world=[]
        frames=list(range(361,554)) if key=='route' else phases
        with render_geometry_paused():
            for f in frames:
                scene.frame_set(int(f),subframe=float(f)%1);bpy.context.view_layer.update()
                bases.append([np.array(b.matrix_basis) for b in rig.pose.bones]);matrices.append([np.array(b.matrix) for b in rig.pose.bones]);world.append(np.array(rig.matrix_world))
        np.savez_compressed(out/(key+'.npz'),names=names,frames=frames,bases=bases,matrices=matrices,world=world)
        objects={};caches=[]
        for ob in scene.objects:
            for m in ob.modifiers:
                if m.type=='MESH_CACHE':
                    q=Path(bpy.path.abspath(m.filepath)).resolve()
                    if not q.is_relative_to(base.BASE.resolve()):raise ValueError('Foreign cache')
                    caches.append({'object':ob.name,'path':str(q.relative_to(base.BASE)),'sha256':base.digest(q),'start':m.frame_start})
            if not ob.hide_render and hasattr(ob.data,'materials'):
                objects[ob.name]={'materials':[m.name if m else None for m in ob.data.materials],'parent':ob.parent.name if ob.parent else None}
        dust={}
        for mat in bpy.data.materials:
            if not mat.use_nodes or not any(x in mat.name.lower() for x in ('dust','wake')):continue
            dust[mat.name]=[{'name':n.name,'type':n.type,'inputs':{s.name:{'value':list(s.default_value) if hasattr(s.default_value,'__len__') else s.default_value,'links':[l.from_node.name for l in s.links]} for s in n.inputs if hasattr(s,'default_value')}} for n in mat.node_tree.nodes]
        records[key]={'source_sha256':sha,'objects':objects,'caches':caches,'dust':dust}
    (out/'result.json').write_text(json.dumps(records,indent=2)+'\n')
    base.check_protected()

if __name__=='__main__':main()
