"""Trusted fixed native staging handler. Inputs contain no executable payload."""
import sys,json,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'));sys.path.insert(0,str(ROOT/'scripts'))
import bpy
import numpy as np
from mathutils import Vector,Matrix
from movie_factory.sikh289_motion import validate_job
from sikh257_native import scene_setup,camera_at,material,mesh,sphere

BIKE=ROOT/'.runtime/assets/series01-motorcycle289/royal_enfield.glb'
BASE=ROOT/'.runtime/art-direction/series01-sikh289'

def inspect(out):
    s,cam=scene_setup();s.render.engine='BLENDER_EEVEE';s.render.resolution_x=800;s.render.resolution_y=600
    before=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(BIKE));bpy.context.view_layer.update()
    objects=[o for o in set(bpy.data.objects)-before if o.type=='MESH'];rows=[]
    for o in objects:
        pts=np.array([tuple(o.matrix_world@Vector(v)) for v in o.bound_box]);rows.append({'name':o.name,'vertices':len(o.data.vertices),'min':pts.min(0).tolist(),'max':pts.max(0).tolist(),'center':pts.mean(0).tolist()})
    # Export chunks are not mechanical parts. Weld spatial seams and inspect
    # connected components before assigning wheel/steering ownership.
    bpy.ops.object.select_all(action='DESELECT')
    for o in objects:o.select_set(True)
    bpy.context.view_layer.objects.active=objects[0];bpy.ops.object.join()
    joined=bpy.context.object;bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
    import bmesh
    bm=bmesh.new();bm.from_mesh(joined.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.0001);bm.to_mesh(joined.data);bm.free()
    bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.mesh.separate(type='LOOSE');bpy.ops.object.mode_set(mode='OBJECT')
    parts=[]
    for i,o in enumerate(sorted(bpy.context.selected_objects,key=lambda x:len(x.data.vertices),reverse=True)):
        o.name=f'donor-part-{i:03d}'
        pts=np.array([tuple(o.matrix_world@v.co) for v in o.data.vertices]);lo=pts.min(0);hi=pts.max(0)
        parts.append({'name':o.name,'vertices':len(pts),'min':lo.tolist(),'max':hi.tolist(),'center':((lo+hi)/2).tolist()})
    (out/'components.json').write_text(json.dumps(parts,indent=2))
    # Normalize lighting scale for diagnostic readability only.
    for o in bpy.context.selected_objects:
        o.scale=(.1,.1,.1)
    bpy.context.view_layer.update()
    low=np.min([r['min'] for r in rows],axis=0);high=np.max([r['max'] for r in rows],axis=0);center=(low+high)/2;size=float(max(high-low))
    (out/'parts.json').write_text(json.dumps({'min':low.tolist(),'max':high.tolist(),'parts':sorted(rows,key=lambda x:x['name'])},indent=2))
    center*=.1;size*=.1
    cam.data.ortho_scale=size*1.35;s.world.node_tree.nodes['Background'].inputs[1].default_value=.8
    for name,offset in [('x',(1,0,.3)),('y',(0,-1,.3)),('top',(0,0,1))]:
        camera_at(cam,Vector(center)+Vector(offset)*size*3,center);s.render.filepath=str(out/f'{name}.png');bpy.ops.render.render(write_still=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'donor.blend'))

def main():
    path=Path(sys.argv[sys.argv.index('--')+1]);job=validate_job(json.loads(path.read_text()))
    out=BASE/f"{job['operation']}-{job['version']:02d}"
    if path.resolve()!=out/'job.json':raise ValueError('Job path not admitted')
    if job['operation']=='inspect':inspect(out)
    elif job['operation'] in ('controls','movie','diagnose','reopen','camera_patch'):
        from sikh289_scene import controls,movie,diagnose,reopen,camera_patch
        {'controls':controls,'movie':movie,'diagnose':diagnose,'reopen':reopen,'camera_patch':camera_patch}[job['operation']](out)
    else:raise ValueError('Construction not yet admitted')

if __name__=='__main__':main()
