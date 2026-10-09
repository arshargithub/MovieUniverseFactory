"""Fixed-source diagnostic views. No original scene is saved or modified."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from entrance200_inspect import SOURCE,SOURCE_SHA,base

def validate(job):
    if job!={'operation':'controls02'}:raise ValueError('Fixed controls only')
    out=base.BASE/'entrance200-controls02'
    if out.exists() or base.digest(SOURCE)!=SOURCE_SHA:raise ValueError('Changed source or output exists')
    return out

def main():
    import bpy
    from mathutils import Vector,Matrix
    out=validate(json.loads(Path(sys.argv[sys.argv.index('--')+1]).read_text()));out.mkdir()
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE),load_ui=False,use_scripts=False);scene=bpy.context.scene
    base.check_protected()
    for o in scene.objects:
        for m in o.modifiers:
            if m.type in ('SMOOTH','CORRECTIVE_SMOOTH','SUBSURF'):m.show_viewport=False
    scene.frame_set(360);rig=bpy.data.objects['MF_body156_fit_rig'];body=bpy.data.objects['MF_studio_adult_body']
    camera=scene.camera;camera.animation_data_clear();camera.data.type='PERSP';camera.data.lens=55
    scene.render.resolution_x=480;scene.render.resolution_y=480;scene.render.resolution_percentage=100
    scene.cycles.device='CPU';scene.cycles.samples=12;scene.render.use_persistent_data=True
    def render(label,target,delta):
        camera.location=target+Vector(delta);camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler()
        scene.render.filepath=str(out/(label+'.png'));bpy.ops.render.render(write_still=True)
    for s,sign in [('L',1),('R',-1)]:
        target=rig.matrix_world@(rig.pose.bones['hand.'+s].head.lerp(rig.pose.bones['hand.'+s].tail,.6))
        render('grip-'+s,target,(sign*2.8,-3.5,1.5))
    target=rig.matrix_world@rig.pose.bones['MF185_neck'].head+Vector((0,-.15,.2));delta=(2.,-8.5,1.3)
    render('neck-lit',target,delta)
    materials=list(body.data.materials);clay=bpy.data.materials.new('200 diagnostic clay');clay.use_nodes=True
    bs=clay.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.3,.3,.3,1);bs.inputs['Roughness'].default_value=.8
    for i in (0,3,4):body.data.materials[i]=clay
    render('neck-clay',target,delta)
    # Retain geometry and camera; remove directional scene light for a broad
    # camera-side diagnostic, not a proposed production lighting change.
    for o in scene.objects:
        if o.type=='LIGHT':o.hide_render=True
    light=bpy.data.lights.new('200 matched broad diagnostic','AREA');light.energy=900;light.shape='DISK';light.size=8
    ob=bpy.data.objects.new('200 matched broad diagnostic',light);scene.collection.objects.link(ob)
    ob.location=target+Vector((0,-8,3));ob.rotation_euler=(target-ob.location).to_track_quat('-Z','Y').to_euler()
    render('neck-clay-soft',target,delta)
    (out/'lights.json').write_text(json.dumps([{'name':o.name,'type':o.data.type,'energy':o.data.energy} for o in scene.objects if o.type=='LIGHT'],indent=2)+'\n')
    (out/'result.json').write_text(json.dumps({'source_sha256':SOURCE_SHA,'native_modified':False,'visual_gate':'NOT_RUN'},indent=2)+'\n')

if __name__=='__main__':main()
