"""Vertical entrance proof on the integrated actor, not a new world campaign."""
import json
from pathlib import Path
import numpy as np

WORKING_SHA='91fa8fd8dde5dcccb3831641b1f06df110873d6042ee8ec112cc15dffb3b2efe'
REPAIRED_SHA='65a36ea7a0f7c73d6ac19101841d28ba06dd896bc213e1c5f475645608196a29'


def camera_path(t):
    """Reuse the accepted C1 travel method, rescale for this actor/9:16 shot."""
    from demo_reuse import camera_offset
    if not 0<=t<=1:raise ValueError('Shot time outside fixed passage')
    profile={'path_interpolation':'continuous','offset_start':[0.,42.,42.],
        'offset_end':[-7.,-17.,2.6],'camera_path':[
        {'at':0.,'offset':[0.,42.,42.]},
        {'at':.55,'offset':[-26.,8.,10.]},
        {'at':.72,'offset':[-22.,-6.,5.]},
        {'at':1.,'offset':[-7.,-17.,2.6]}]}
    return np.array(camera_offset(profile,t))


def setup_camera(scene,rig,frame):
    from mathutils import Vector
    t=(frame-217)/143;focus=t*t*(3-2*t)
    head=rig.matrix_world@rig.pose.bones['MF185_head'].head
    target=Vector((0,-.5,-8.5)).lerp(head+Vector((0,0,-.65)),focus)
    camera=scene.camera;camera.data.type='PERSP';camera.data.lens=42
    camera.data.sensor_fit='VERTICAL';camera.data.sensor_height=24;camera.data.dof.use_dof=False
    camera.location=target+Vector(camera_path(t));camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler()
    return {'frame':frame,'t':t,'position':list(camera.location),'target':list(target),'lens_mm':42,'format':'9:16'}


def setup_lighting(scene):
    from mathutils import Vector
    lights=sorted((ob for ob in scene.objects if ob.name.startswith('MF_body156_softbox')),key=lambda ob:ob.name)
    for light,point in zip(lights,((-7,-9,7),(7,-6,4))):
        light.location=point;light.rotation_euler=(Vector((0,-1,-2))-light.location).to_track_quat('-Z','Y').to_euler()


def layout(out):
    import bpy
    from mathutils import Vector
    from wardrobe_motion178 import BASE,digest,check_protected
    source=BASE/'wardrobe185-finishreview01/integration-working.blend'
    if WORKING_SHA is None or digest(source)!=WORKING_SHA:raise ValueError('Unbound integrated shot source')
    (out/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False)
    scene=bpy.context.scene;rig=bpy.data.objects['MF_body156_fit_rig']
    inspected={}
    for name in ('MF_fit_tunic_173_visible','MF185_fitted_upper_tunic','MF185_gait_saddle.stirrup'):
        ob=bpy.data.objects[name]
        inspected[name]={'vertices':len(ob.data.vertices),'modifiers':[
            {'name':m.name,'type':m.type,'viewport':m.show_viewport,'render':m.show_render,
             'target':getattr(getattr(m,'target',None),'name',None)} for m in ob.modifiers]}
    (out/'garment-inspection.json').write_text(json.dumps(inspected,indent=2)+'\n')
    scene.render.resolution_x=576;scene.render.resolution_y=1024;scene.render.resolution_percentage=100
    scene.cycles.device='CPU';scene.cycles.samples=8;scene.render.use_persistent_data=True
    setup_lighting(scene)
    records=[]
    for frame in (217,253,289,325,360):
        scene.frame_set(frame);bpy.context.view_layer.update();records.append(setup_camera(scene,rig,frame))
        scene.render.filepath=str(out/('shot-%03d.png'%frame));bpy.ops.render.render(write_still=True)
    check_protected()
    (out/'camera-layout.json').write_text(json.dumps({'source_sha256':WORKING_SHA,'poses':records,
        'scope':'Camera/framing and visible structural proof only; neutral backdrop, not final trailer footage',
        'basis':'Accepted smoother demonstrator camera method; new composition requires review',
        'visual_gate':'NOT_RUN','temporal_gate':'NOT_RUN'},indent=2)+'\n')


def motion(out):
    """Every frame of the six-second entrance; no endpoint-only motion claim."""
    import bpy
    from mathutils import Vector
    from wardrobe_motion178 import BASE,digest,check_protected
    source=BASE/'wardrobe185-finishreview01/integration-working.blend'
    source_sha=WORKING_SHA
    if out.name.endswith('shotmotion02'):
        source=BASE/'wardrobe185-lowerreview07/integration-working.blend';source_sha=REPAIRED_SHA
    if digest(source)!=source_sha:raise ValueError('Unbound integrated motion source')
    (out/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False)
    scene=bpy.context.scene;rig=bpy.data.objects['MF_body156_fit_rig']
    scene.camera.animation_data_clear()
    scene.render.resolution_x=432;scene.render.resolution_y=768;scene.render.resolution_percentage=100
    scene.cycles.device='CPU';scene.cycles.samples=4;scene.render.use_persistent_data=True
    setup_lighting(scene)
    records=[]
    for frame in range(217,361):
        scene.frame_set(frame);bpy.context.view_layer.update();records.append(setup_camera(scene,rig,frame))
        scene.camera.keyframe_insert(data_path='location',frame=frame)
        scene.camera.keyframe_insert(data_path='rotation_euler',frame=frame)
        scene.render.filepath=str(out/('frame-%04d.png'%frame));bpy.ops.render.render(write_still=True)
    # A travelling camera does not expose both garment/leg interfaces equally.
    # Inspect a full gait cycle from the unoccluded side as a separate control.
    from wardrobe_riding_fit import fit_render
    scene.camera.animation_data_clear();scene.camera.data.type='ORTHO'
    for frame in (217,219,221,223,225,227):
        scene.frame_set(frame);bpy.context.view_layer.update()
        fit_render(out,'side-%03d'%frame,90,(0,-1.8,-8),30.,(640,640))
    check_protected()
    (out/'motion-render.json').write_text(json.dumps({'source_sha256':source_sha,'poses':records,
        'frame_range':[217,360],'fps':24,'rendered_frames':len(records),'scope':'Neutral-backdrop character entrance proof, not final trailer footage',
        'visual_gate':'NOT_RUN','temporal_gate':'NOT_RUN'},indent=2)+'\n')
