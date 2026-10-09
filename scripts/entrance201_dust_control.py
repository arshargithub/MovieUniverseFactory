"""Matched dust material control; no actor or geographic changes."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import wardrobe_motion178 as base

def treatment(mat):
    n,l=mat.node_tree.nodes,mat.node_tree.links
    vol=next(x for x in n if x.type=='PRINCIPLED_VOLUME')
    density=vol.inputs['Density'].links[0].from_node;density.inputs[1].default_value=.09
    emission=vol.inputs['Emission Strength'].links[0].from_node;emission.inputs[1].default_value=.20
    modulation=density.inputs[0].links[0].from_node.inputs[1].links[0].from_node
    # More internal variation at a lower optical depth, instead of an opaque
    # continuous exhaust-like core. Preserve the broad connected cloud.
    modulation.inputs[1].default_value=-.55
    multiply=modulation.inputs[0].links[0].from_node;multiply.inputs[1].default_value=2.5
    clamp=n.new('ShaderNodeMath');clamp.operation='MAXIMUM';clamp.inputs[1].default_value=.02;l.new(modulation.outputs[0],clamp.inputs[0])
    carrier=density.inputs[0].links[0].from_node;l.new(clamp.outputs[0],carrier.inputs[1])

def main():
    import bpy
    if json.loads(Path(sys.argv[sys.argv.index('--')+1]).read_text())!={'operation':'dust15'}:raise ValueError('Fixed control')
    out=base.BASE/'entrance201-dust15';source=base.BASE/'entrance201-route03/scene.blend'
    r=json.loads((source.parent/'result.json').read_text())
    if out.exists() or base.digest(source)!=r['native_sha256']:raise ValueError('Source/output')
    out.mkdir();(out/'handler.py').write_bytes(Path(__file__).read_bytes());bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False);scene=bpy.context.scene
    treatment(bpy.data.materials['201 shaded sunlit earth wake'])
    for ob in scene.objects:
        for m in ob.modifiers:
            if m.type in ('SMOOTH','CORRECTIVE_SMOOTH','SUBSURF'):m.show_viewport=False
    scene.render.resolution_x=432;scene.render.resolution_y=768;scene.render.resolution_percentage=100;scene.cycles.device='CPU';scene.cycles.samples=12;scene.render.use_persistent_data=False
    for f in (385,457,552):
        scene.frame_set(f);scene.render.filepath=str(out/f'frame-{f:04d}.png');bpy.ops.render.render(write_still=True)
    (out/'result.json').write_text(json.dumps({'source_sha256':r['native_sha256'],'changes':'Density.09; ambient.20; nonlinear density modulation','native_modified':False,'visual_gate':'NOT_RUN'},indent=2)+'\n');base.check_protected()

if __name__=='__main__':main()
