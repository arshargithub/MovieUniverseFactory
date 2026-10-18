"""Finish known interface defects without rebuilding protected choreography."""
import json
import bpy
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view
from movie_factory import sikh305_motion as c
from sikh257_native import camera_at
from sikh257_layout import key
def finish(out):
    removed=[]
    for ob in list(bpy.data.objects):
        if ob.name.startswith('304 intermittent silt'):
            removed.append(ob.name);bpy.data.objects.remove(ob,do_unlink=True)
    mat=bpy.data.materials['305 compacted clay and silty road'];n=mat.node_tree.nodes;l=mat.node_tree.links;b=n['Principled BSDF'];source=b.inputs['Base Color'].links[0].from_socket
    coord=n.new('ShaderNodeTexCoord');xyz=n.new('ShaderNodeSeparateXYZ');l.new(coord.outputs['Object'],xyz.inputs[0])
    def mathnode(op,a=None,value=0):
        m=n.new('ShaderNodeMath');m.operation=op;m.inputs[1].default_value=value
        if a is not None:l.new(a,m.inputs[0])
        return m.outputs[0]
    ax=mathnode('ABSOLUTE',xyz.outputs['X'])
    wave=mathnode('SINE',mathnode('MULTIPLY',xyz.outputs['Y'],.18));center=mathnode('ADD',mathnode('MULTIPLY',wave,.12),2.72)
    delta=n.new('ShaderNodeMath');delta.operation='SUBTRACT';l.new(ax,delta.inputs[0]);l.new(center,delta.inputs[1]);distance=mathnode('ABSOLUTE',delta.outputs[0])
    wet=n.new('ShaderNodeMapRange');wet.inputs['From Min'].default_value=.035;wet.inputs['From Max'].default_value=.26;wet.inputs['To Min'].default_value=.60;wet.inputs['To Max'].default_value=0;l.new(distance,wet.inputs[0])
    noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=3.4;noise.inputs['Detail'].default_value=3;l.new(coord.outputs['Object'],noise.inputs[0])
    weight=n.new('ShaderNodeMath');weight.operation='MULTIPLY';l.new(wet.outputs[0],weight.inputs[0]);l.new(noise.outputs['Fac'],weight.inputs[1])
    mix=n.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[2].default_value=(.42,.46,.36,1);l.new(weight.outputs[0],mix.inputs[0]);l.new(source,mix.inputs[1]);l.new(mix.outputs[0],b.inputs['Base Color'])
    # Dirt moisture has soft irregular transitions on the shared surface;
    # there are no separate quads casting long sliver shadows in the ditch.
    s=bpy.context.scene;cam=s.camera;root=bpy.data.objects['BIKE travel owner'];rows=json.loads((out/'camera-relative.json').read_text())
    for row in rows:
        f=row['frame'];t=row['source_t']
        if not 20.5<=t<23:continue
        s.frame_set(f);y=c.travel(t);u=c.ease((t-22)/1.0)
        loc=Vector((-2.7,y+4.6,.70)).lerp(Vector((-2.7,-22,2)),u)
        camera_at(cam,loc,(0,y+.2*(1-u)-.2*u,1.02));cam.data.lens=32+2*u;key(cam,f);cam.data.keyframe_insert('lens',frame=f);bpy.context.view_layer.update()
        row['camera']=list(cam.location);row['subject_screen']=list(world_to_camera_view(s,cam,root.matrix_world@Vector((0,0,1.25))))
    (out/'camera-relative.json').write_text(json.dumps(rows,indent=2))
    (out/'finish.json').write_text(json.dumps({'removed_derivative_overlays':removed,'ground_geometry_changed':False,'launch_camera_source_interval':[20.5,23.0],'principal_or_stop_changed':False},indent=2))

def launch_camera(out):
    """Stay within the opened corridor, not inside a crowd member."""
    s=bpy.context.scene;cam=s.camera;root=bpy.data.objects['BIKE travel owner']
    rows=json.loads((out/'camera-relative.json').read_text())
    for row in rows:
        f=row['frame'];t=row['source_t']
        if t<20.5:continue
        s.frame_set(f);loc,aim,lens=c.departure_camera(t)
        camera_at(cam,loc,aim);cam.data.lens=lens
        key(cam,f);cam.data.keyframe_insert('lens',frame=f);bpy.context.view_layer.update()
        row['camera']=list(cam.location);row['subject_screen']=list(world_to_camera_view(s,cam,root.matrix_world@Vector((0,0,1.25))))
    (out/'camera-relative.json').write_text(json.dumps(rows,indent=2))

def final_interfaces(out):
    launch_camera(out)
    from sikh305_scene import dust
    dust(json.loads((out/'coordinated-motion.json').read_text()))
    (out/'finish.json').write_text(json.dumps({'launch_camera_end_matches_following_shot':[-2.7,-22,2],'launch_dust':'larger contact cloud only during driven-wheel slip; stop dust and stop position preserved','horse_motion_changed':False},indent=2))
