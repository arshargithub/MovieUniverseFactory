"""Read-only saved-scene geometry/material/visibility diagnostic."""
import json
import sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import wardrobe_motion178 as base

def main():
    import bpy
    from mathutils import Vector
    job=json.loads(Path(sys.argv[sys.argv.index('--')+1]).read_text())
    if job!={'operation':'scenediagnose20'}:raise ValueError('Fixed diagnostic required')
    folder=base.BASE/'entrance190-composition19';source=folder/'scene.blend';out=base.BASE/'entrance190-scene-diagnose20'
    r=json.loads((folder/'result.json').read_text())
    if out.exists() or base.digest(source)!=r['native_sha256']:raise ValueError('Unbound source')
    out.mkdir();bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False);scene=bpy.context.scene
    rows=[]
    for f in (361,457,552):
        scene.frame_set(f);bpy.context.view_layer.update();land=bpy.data.objects['AS_valley_landform'];root=bpy.data.objects['AS_world_travel'];cam=scene.camera
        ob=bpy.data.objects['MF190_shared_route_actor'];p=ob.matrix_world@Vector((0,.2,-20.931))
        local=land.matrix_world.inverted()@p;hit=land.ray_cast(local+Vector((0,0,1000)),Vector((0,0,-1)))
        mats=[]
        for slot in land.material_slots:
            mat=slot.material;mats.append({'link':slot.link,'name':mat.name,'maps':[{'name':n.name,'inputs':{s.name:s.default_value for s in n.inputs if s.type=='VALUE'},'source':[(l.from_node.name,l.from_socket.name) for l in n.inputs['Value'].links]} for n in mat.node_tree.nodes if n.type=='MAP_RANGE']})
        rows.append({'frame':f,'root_matrix':[list(q) for q in root.matrix_world],'land_matrix':[list(q) for q in land.matrix_world],'actor_floor':list(p),'ray_height':list(land.matrix_world@hit[1]) if hit[0] else None,'materials':mats,
          'visible_near_props':[{'name':o.name,'location':list(o.matrix_world.translation),'dimensions':list(o.dimensions),'type':o.type} for o in scene.objects if not o.hide_render and o.parent==root and o!=land and (o.matrix_world.translation-p).length<120 and max(o.dimensions)>10]})
    cam.animation_data_clear();cam.data.animation_data_clear();scene.frame_set(361)
    cam.location=(100,40,450);target=Vector((-115,-275,-10));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=640
    bpy.context.view_layer.update();scene.cycles.samples=4;scene.cycles.device='CPU';scene.render.filepath=str(out/'actual-geography.png');bpy.ops.render.render(write_still=True)
    (out/'result.json').write_text(json.dumps({'source_sha256':r['native_sha256'],'rows':rows},indent=2)+'\n')

if __name__=='__main__':main()
