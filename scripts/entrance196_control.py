"""Read-only isolating controls for196's first overhead artifact."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import wardrobe_motion178 as base

def main():
    import bpy
    if json.loads(Path(sys.argv[sys.argv.index('--')+1]).read_text())!={'operation':'control08'}:raise ValueError('Fixed control only')
    source=base.BASE/'entrance196-build02/scene.blend';out=base.BASE/'entrance196-control08'
    if out.exists() or base.digest(source)!='638f7c5a057eb94183f172b199a476ab324f5c806e20a42e16b23a705bd69e96':raise ValueError('Source mismatch')
    out.mkdir();bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False);scene=bpy.context.scene
    for ob in scene.objects:
        for m in ob.modifiers:
            if m.type in ('SMOOTH','CORRECTIVE_SMOOTH','SUBSURF'):m.show_viewport=False
    scene.cycles.device='CPU';scene.cycles.samples=8;scene.render.resolution_x=360;scene.render.resolution_y=640;scene.render.use_persistent_data=True;scene.frame_set(217)
    debris=bpy.data.objects['MF196_hoof_ejected_pebbles'];stones=bpy.data.objects['MF196_clustered_rocky_margins']
    for label,d,s in [('no-debris',True,False),('no-rocks',False,True),('neither',True,True)]:
        debris.hide_render=d;stones.hide_render=s;scene.render.filepath=str(out/(label+'.png'))
        if bpy.ops.render.render(write_still=True)!={'FINISHED'}:raise RuntimeError('Canceled')
    land=bpy.data.objects['AS_valley_landform'];mat=land.data.materials[0];n,l=mat.node_tree.nodes,mat.node_tree.links
    l.new(n.get('Principled BSDF').outputs[0],n.get('Material Output').inputs['Surface'])
    scene.render.filepath=str(out/'opaque-ground.png');bpy.ops.render.render(write_still=True)
    inventory=[]
    for o in scene.objects:
        if o.name.startswith(('AS_stone','MF188_bank')) and o.type=='MESH':
            inventory.append({'name':o.name,'vertices':len(o.data.vertices),'materials':[s.material.name for s in o.material_slots if s.material]})
            if len(inventory)>12:break
    (out/'result.json').write_text(json.dumps({'inventory':inventory,'native_modified':False},indent=2)+'\n');base.check_protected()

if __name__=='__main__':main()
