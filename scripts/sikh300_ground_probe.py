"""Fixed transient ground-owner discriminator; never alters saved input."""
import sys,json
from pathlib import Path
import bpy
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[1]
def main():
    p=Path(sys.argv[sys.argv.index('--')+1]);job=json.loads(p.read_text())
    if job!={'operation':'ground-probe','version':1}:raise ValueError('Unknown job')
    bpy.ops.wm.open_mainfile(filepath=str(ROOT/'.runtime/art-direction/series01-sikh300/controls-08/sequence.blend'),use_scripts=False)
    s=bpy.context.scene;s.frame_set(360);s.render.resolution_x=360;s.render.resolution_y=640
    road=bpy.data.objects['irregular packed farm track'];old=road.data.materials[0]
    deps=bpy.context.evaluated_depsgraph_get();camera=s.camera;corners=camera.data.view_frame(scene=s);hits=[]
    # Perspective view frame: interpolate local near-plane corners by extrema.
    xmin=min(c.x for c in corners);xmax=max(c.x for c in corners);ymin=min(c.y for c in corners);ymax=max(c.y for c in corners);z=corners[0].z
    for x,y in ((160,560),(190,560),(140,500),(220,500),(180,600),(200,600)):
        direction=camera.matrix_world.to_3x3()@Vector((xmin+(x+.5)/360*(xmax-xmin),ymax-(y+.5)/640*(ymax-ymin),z));origin=camera.matrix_world.translation
        ok,point,normal,index,ob,matrix=s.ray_cast(deps,origin,direction.normalized())
        hits.append({'pixel':[x,y],'object':ob.name if ok else None,'point':list(point),'normal':list(normal),'polygon':index})
    (p.parent/'hits.json').write_text(json.dumps(hits,indent=2))
    def render(name):s.render.filepath=str(p.parent/(name+'.png'));bpy.ops.render.render(write_still=True)
    render('baseline')
    bs=old.node_tree.nodes.get('Principled BSDF');normal=bs.inputs['Normal'].links[0].from_socket
    old.node_tree.links.remove(bs.inputs['Normal'].links[0]);render('no-bump');old.node_tree.links.new(normal,bs.inputs['Normal'])
    mat=bpy.data.materials.new('300 diagnostic clay');mat.use_nodes=True;b=mat.node_tree.nodes['Principled BSDF'];b.inputs['Base Color'].default_value=(.25,.20,.13,1);b.inputs['Roughness'].default_value=.9
    road.data.materials[0]=mat;render('uniform-clay')
    mat.node_tree.nodes.clear();em=mat.node_tree.nodes.new('ShaderNodeEmission');em.inputs[0].default_value=(.25,.20,.13,1);out=mat.node_tree.nodes.new('ShaderNodeOutputMaterial');mat.node_tree.links.new(em.outputs[0],out.inputs[0]);render('uniform-emission')
if __name__=='__main__':main()
