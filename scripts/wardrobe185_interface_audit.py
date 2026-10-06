"""Read-only visible-interface proof on the repaired integrated character.

Magenta skin is a diagnostic material substitution, not an asset correction.
No selected native or visual PASS is produced by this handler.
"""
import json
from pathlib import Path
import numpy as np


def neutral_lower():
    import bpy
    from wardrobe_motion178 import BASE,digest
    source=BASE/'wardrobe185-lowercloth05/standing.npz'
    if digest(source)!='160e4ca1c9eb2b54d388badd3ae5ba6aa9754b32b4868463d3843b696e85c566':
        raise ValueError('Neutral lower solve changed')
    with np.load(source,allow_pickle=False) as data:points=data['frames'][-1]
    ob=bpy.data.objects['MF185_free_lower_tunic']
    if len(ob.data.vertices)!=len(points) or np.max(abs(np.array(ob.matrix_world)-np.eye(4)))>1e-7:
        raise ValueError('Unexpected lower-cloth coordinates')
    for mod in list(ob.modifiers):
        if mod.type=='MESH_CACHE':ob.modifiers.remove(mod)
    ob.data=ob.data.copy();ob.data.vertices.foreach_set('co',points.astype(np.float32).ravel());ob.data.update()
    ob['qualification']='Frozen separately simulated standing drape; no mounting transition qualified'


def run(out):
    import bpy
    from mathutils import Vector
    from wardrobe_motion178 import BASE,digest,check_protected
    from wardrobe185_shot import REPAIRED_SHA
    from wardrobe185_delivery import neutral_state
    from wardrobe_riding_fit import fit_render
    source=BASE/'wardrobe185-lowerreview07/integration-working.blend'
    if digest(source)!=REPAIRED_SHA:raise ValueError('Unbound interface source')
    (out/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False)
    scene=bpy.context.scene;scene.camera.animation_data_clear();scene.camera.data.type='ORTHO'
    scene.cycles.device='CPU';scene.cycles.samples=8;scene.render.use_persistent_data=True
    check_protected();body=bpy.data.objects['MF_studio_adult_body'];original=body.data
    body.data=original.copy();body.data.materials.clear()
    marker=bpy.data.materials.new('185 diagnostic skin visibility only');marker.use_nodes=True
    nodes=marker.node_tree.nodes;nodes.clear();output=nodes.new('ShaderNodeOutputMaterial');emit=nodes.new('ShaderNodeEmission')
    emit.inputs['Color'].default_value=(1,0,1,1);emit.inputs['Strength'].default_value=1
    marker.node_tree.links.new(emit.outputs[0],output.inputs['Surface']);body.data.materials.append(marker)
    for poly in body.data.polygons:poly.material_index=0
    frames=(169,193,217,223,265,280,326,360)
    try:
        for frame in frames:
            scene.frame_set(frame);bpy.context.view_layer.update()
            for angle,label in ((0,'front'),(90,'left'),(180,'rear'),(270,'right')):
                fit_render(out,'skin-control-'+label+'-'+str(frame),angle,(0,-.2,-8.),10.,(640,640))
    finally:body.data=original
    check_protected()
    # Full upper interfaces at partial and full required posture, using the
    # actual material, rather than relying only on an earlier source's images.
    rig=bpy.data.objects['MF_body156_fit_rig']
    for frame in (193,217,360):
        scene.frame_set(frame);bpy.context.view_layer.update()
        center=tuple(rig.matrix_world@rig.pose.bones['MF185_head'].head+Vector((0,0,-1.4)))
        for angle,label in ((0,'front'),(90,'left'),(180,'rear'),(270,'right')):
            fit_render(out,'upper-'+label+'-'+str(frame),angle,center,9.,(640,640))
    neutral_state();neutral_lower()
    for angle,label in ((0,'front'),(90,'left'),(180,'rear'),(270,'right')):
        fit_render(out,'neutral-upper-'+label,angle,(0,.15,-1.7),8.,(640,640))
        fit_render(out,'neutral-whole-'+label,angle,(0,0,-6.4),18.,(576,864))
    check_protected()
    (out/'result.json').write_text(json.dumps({'source_sha256':REPAIRED_SHA,'skin_control_frames':frames,
        'skin_control_scope':'All body skin replaced temporarily with magenta emission. Exposed hands are expected; covered thigh/seat/knee breakthroughs are not. Images require human or agent visual review, no automatic pixel pass.',
        'native_saved':False,'protected_exact':True,'visual_gate':'NOT_RUN'},indent=2)+'\n')
