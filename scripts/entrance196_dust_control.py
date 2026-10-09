"""Discriminate the mid-shot volume-edge regression with one-variable controls."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import wardrobe_motion178 as base

def main():
    import bpy
    if json.loads(Path(sys.argv[sys.argv.index('--')+1]).read_text())!={'operation':'dust35'}:raise ValueError('Fixed control only')
    source=base.BASE/'entrance196-outcrops30/scene.blend';out=base.BASE/'entrance196-dust35';r=json.loads((source.parent/'result.json').read_text())
    if out.exists() or base.digest(source)!=r['native_sha256']:raise ValueError('Unbound source')
    out.mkdir();(out/'handler.py').write_bytes(Path(__file__).read_bytes())
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False);scene=bpy.context.scene
    for ob in scene.objects:
        for m in ob.modifiers:
            if m.type in ('SMOOTH','CORRECTIVE_SMOOTH','SUBSURF'):m.show_viewport=False
    rocks=[o for o in scene.objects if o.name.startswith(('MF196_rock_cluster_','MF196_scanned_scree_','MF196_path_chip_'))]
    dust=bpy.data.objects['MF189_continuous_trailing_dust'];debris=bpy.data.objects['MF196_hoof_ejected_pebbles']
    mat=bpy.data.objects['AS_valley_landform'].data.materials[0];n,l=mat.node_tree.nodes,mat.node_tree.links;output=n.get('Material Output');original=output.inputs['Surface'].links[0].from_socket
    scene.frame_set(295);scene.cycles.device='CPU';scene.cycles.samples=12;scene.render.resolution_x=432;scene.render.resolution_y=768;scene.render.resolution_percentage=100;scene.render.use_persistent_data=True
    for name in ('no-new-rocks','no-debris','opaque-ground','no-dust'):
        for o in rocks:o.hide_render=name=='no-new-rocks'
        debris.hide_render=name=='no-debris';dust.hide_render=name=='no-dust'
        l.new(n.get('Principled BSDF').outputs[0] if name=='opaque-ground' else original,output.inputs['Surface'])
        scene.render.filepath=str(out/(name+'.png'))
        if bpy.ops.render.render(write_still=True)!={'FINISHED'}:raise RuntimeError('Render failed')
    (out/'result.json').write_text(json.dumps({'source_sha256':r['native_sha256'],'native_modified':False,'controls':'Single factor at295: new rock visibility, new debris visibility, ground opacity, existing dust visibility'},indent=2)+'\n');base.check_protected()

if __name__=='__main__':main()
