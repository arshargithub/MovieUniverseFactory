"""Native blocked/unblocked airflow fixture before garment shielding claims."""
import json
from pathlib import Path
import numpy as np


def run(out):
    import bpy
    from mathutils import Vector
    from wardrobe_motion178 import sheet_grid
    from wardrobe185_lower_cloth import panel,profile,sample
    (out/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
    records={};trajectories={}
    for name,strength,absorption in (('off',0.,0.),('exposed',4.,0.),('shielded',4.,1.)):
        bpy.ops.wm.read_factory_settings(use_empty=True)
        scene=bpy.context.scene;scene.render.fps=24;scene.gravity=(0,0,0)
        p,f=sheet_grid(13,13,lambda u,v:(.4*(u-.5),0.,.4*v))
        p=np.array(p);f=np.array(f);ob=panel('Airflow test cloth',p,f)
        pins=np.flatnonzero(p[:,2]>.399);group=ob.vertex_groups.new(name='support')
        group.add(pins.tolist(),1.,'REPLACE')
        bpy.ops.mesh.primitive_cube_add(size=1,location=(0,-.5,.2))
        blocker=bpy.context.object;blocker.scale=(.8,.04,.8)
        bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
        blocker.modifiers.new('Airflow occluder','COLLISION')
        blocker.collision.absorption=absorption
        domain=bpy.data.collections.new('Occluder');scene.collection.children.link(domain);domain.objects.link(blocker)
        mod=profile(ob,domain);mod.collision_settings.use_self_collision=False;mod.point_cache.frame_end=72
        bpy.ops.object.effector_add(type='WIND',location=(0,-3,.2));wind=bpy.context.object
        wind.rotation_euler=Vector((0,1,0)).to_track_quat('Z','Y').to_euler()
        wind.field.strength=strength;wind.field.use_absorption=True
        frames=[]
        for frame in range(1,73):
            scene.frame_set(frame);bpy.context.view_layer.update();frames.append(sample(ob))
        frames=np.array(frames);trajectories[name]=frames
        records[name]={'wind_strength':strength,'absorption':absorption,'max_y_displacement_m':float(abs(frames[:,:,1]).max())}
    exposed=records['exposed']['max_y_displacement_m'];shielded=records['shielded']['max_y_displacement_m']
    passed=exposed>.005 and shielded<max(1e-5,exposed*.05)
    np.savez_compressed(out/'fixture.npz',**trajectories)
    (out/'result.json').write_text(json.dumps({'cases':records,'shielding_control_pass':passed,
        'scope':'Installed native airflow attenuation fixture, not calibrated aerodynamics or garment qualification'},indent=2)+'\n')
    if not passed:raise ValueError('Native airflow shielding fixture failed')
