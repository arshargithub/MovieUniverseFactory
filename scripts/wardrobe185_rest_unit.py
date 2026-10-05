"""Does the installed native cloth solver actually use our authored metric?"""
import json
from pathlib import Path
import numpy as np


def run(out):
    import bpy
    from wardrobe_doublewrap185 import cloth_settings
    from wardrobe_motion178 import sheet_grid
    (out/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
    records={}
    cases=('reset','reopen') if out.name.endswith('restunit02') else ('none','rest','tagged')
    if out.name.endswith('restunit03'):cases=('triangulate','weld','dummy')
    for case in cases:
        bpy.ops.wm.read_factory_settings(use_empty=True);scene=bpy.context.scene;scene.gravity=(0,0,0)
        p,f=sheet_grid(9,9,lambda u,v:(.4*u,.4*v,1.))
        mesh=bpy.data.meshes.new('unit');mesh.from_pydata(p,[],f);mesh.update()
        ob=bpy.data.objects.new('unit',mesh);scene.collection.objects.link(ob);bpy.context.view_layer.objects.active=ob
        ob.shape_key_add(name='Basis');key=ob.shape_key_add(name='Half-size fabric')
        for v in key.data:v.co.x*=.5;v.co.y*=.5
        key.value=0;ob.active_shape_key_index=0;ob.show_only_shape_key=False
        group=ob.vertex_groups.new(name='support');group.add([0],1.,'REPLACE')
        if case=='triangulate':ob.modifiers.new('Explicit mesh evaluation','TRIANGULATE')
        if case=='weld':
            weld=ob.modifiers.new('Explicit mesh evaluation','WELD');weld.merge_threshold=1e-6
        if case=='dummy':
            dummy=ob.shape_key_add(name='Active unchanged shape');dummy.value=1.
            for v,q in zip(dummy.data,p):v.co=q
            ob.active_shape_key_index=0;ob.show_only_shape_key=False
        mod=cloth_settings(ob,1);s=mod.settings;s.mass=.3;s.quality=24;s.tension_stiffness=200;s.compression_stiffness=200;s.shear_stiffness=100
        mod.collision_settings.use_self_collision=False
        if case!='none':s.rest_shape_key=key
        s.use_dynamic_mesh=False
        if case=='tagged':
            ob.data.shape_keys.update_tag();ob.data.update();ob.update_tag(refresh={'DATA'});bpy.context.view_layer.update()
        if case=='reset':scene.frame_set(0);bpy.context.view_layer.update()
        if case=='reopen':
            bpy.ops.wm.save_as_mainfile(filepath=str(out/'rest-control.blend'),check_existing=False)
            bpy.ops.wm.open_mainfile(filepath=str(out/'rest-control.blend'),load_ui=False,use_scripts=False)
            scene=bpy.context.scene;ob=bpy.data.objects['unit'];mod=ob.modifiers[0];s=mod.settings;key=ob.data.shape_keys.key_blocks['Half-size fabric']
        for frame in range(1,49):
            scene.frame_set(frame);bpy.context.view_layer.update()
            ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());m=ev.to_mesh();q=np.array([v.co[:] for v in m.vertices]);ev.to_mesh_clear()
        records[case]={'extent':np.ptp(q,axis=0).tolist(),'key':s.rest_shape_key.name if s.rest_shape_key else None,
            'key_extent':np.ptp(np.array([v.co[:] for v in key.data]),axis=0).tolist(),'dynamic':s.use_dynamic_mesh}
    (out/'result.json').write_text(json.dumps(records,indent=2)+'\n');print(json.dumps(records),flush=True)
