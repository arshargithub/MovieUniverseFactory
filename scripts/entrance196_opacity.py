"""One-variable control for legacy ground transparency versus object support."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import wardrobe_motion178 as base

def main():
    import bpy
    if json.loads(Path(sys.argv[sys.argv.index('--')+1]).read_text())!={'operation':'opacity34'}:raise ValueError('Fixed opacity control only')
    source=base.BASE/'entrance196-outcrops30/scene.blend';out=base.BASE/'entrance196-opacity34';r=json.loads((source.parent/'result.json').read_text())
    if out.exists() or base.digest(source)!=r['native_sha256']:raise ValueError('Unbound source')
    out.mkdir();bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False);scene=bpy.context.scene
    for ob in scene.objects:
        for m in ob.modifiers:
            if m.type in ('SMOOTH','CORRECTIVE_SMOOTH','SUBSURF'):m.show_viewport=False
    mat=bpy.data.objects['AS_valley_landform'].data.materials[0];n,l=mat.node_tree.nodes,mat.node_tree.links;output=n.get('Material Output')
    prior=[{'from':x.from_node.name,'type':x.from_node.type} for x in output.inputs['Surface'].links]
    l.new(n.get('Principled BSDF').outputs[0],output.inputs['Surface'])
    scene.cycles.device='CPU';scene.cycles.samples=12;scene.render.resolution_x=432;scene.render.resolution_y=768;scene.render.resolution_percentage=100;scene.render.use_persistent_data=True
    for f in (265,360):
        scene.frame_set(f);scene.render.filepath=str(out/f'frame-{f:04d}.png')
        if bpy.ops.render.render(write_still=True)!={'FINISHED'}:raise RuntimeError('Render failed')
    (out/'result.json').write_text(json.dumps({'source_sha256':r['native_sha256'],'prior_output':prior,'native_modified':False},indent=2)+'\n');base.check_protected()

if __name__=='__main__':main()
