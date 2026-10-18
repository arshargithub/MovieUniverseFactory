"""Preservation, trajectory and lifecycle measurements, not artistic certification."""
import json,hashlib
from pathlib import Path
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[1]
def fcurves(id):
    if not id.animation_data or not id.animation_data.action:return []
    return [f for l in id.animation_data.action.layers for s in l.strips for b in s.channelbags for f in b.fcurves]
def curve_signature(id):
    data=[(f.data_path,f.array_index,[(tuple(p.co),p.interpolation) for p in f.keyframe_points]) for f in fcurves(id)]
    return hashlib.sha256(json.dumps(sorted(data),sort_keys=True).encode()).hexdigest()
def protected():
    s=bpy.context.scene
    return {'camera':curve_signature(s.camera),'lens':curve_signature(s.camera.data),
            'bike':{o.name:curve_signature(o) for o in bpy.data.objects if o.name.startswith('BIKE ')},
            'crowd':{o.name:(tuple(o.location),tuple(o.rotation_euler),curve_signature(o)) for o in bpy.data.objects if o.name.startswith(('crowd ','FOOT WARRIOR '))},
            'lane':[(v.index,tuple(v.co)) for v in bpy.data.objects['irregular packed farm track'].data.vertices if abs(v.co.x)<=1.6]}
def audit(out,source):
    current=protected()
    assert len(current['bike'])>0 and sum(k.startswith('FOOT WARRIOR ') for k in current['crowd'])>0
    dependencies=[]
    for im in bpy.data.images:
        if im.source!='FILE':continue
        packed=bool(im.packed_file or im.packed_files)
        path=Path(bpy.path.abspath(im.filepath)) if im.filepath else None
        exists=bool(path and path.is_file())
        dependencies.append(dict(name=im.name,packed=packed,external_exists=exists,path=None if packed else str(path)))
        assert packed or exists,im.name
    s=bpy.context.scene;road=bpy.data.objects['irregular packed farm track'];rig=bpy.data.objects['horse.rig']
    bvh=BVHTree.FromPolygons([v.co.copy() for v in road.data.vertices],[list(p.vertices) for p in road.data.polygons])
    rows=[]
    for f in range(274,358):
        s.frame_set(f);bpy.context.view_layer.update();feet={}
        for name in ('DEF-f_toe.L','DEF-f_toe.R','DEF-r_toe.L','DEF-r_toe.R'):
            p=rig.matrix_world@rig.pose.bones[name].tail;hit=bvh.ray_cast(Vector((p.x,p.y,12)),Vector((0,0,-1)))[0]
            feet[name]={'world':list(p),'skeletal_ground_gap':None if hit is None else p.z-hit.z}
        rows.append({'frame':f,'feet':feet,'head':list(rig.matrix_world@rig.pose.bones['head'].head)})
    debris=[]
    for ob in bpy.data.objects:
        if not ob.name.startswith('299 tire-contact earth chip'):continue
        curves=fcurves(ob);hide=next(f for f in curves if f.data_path=='hide_render')
        birth=min(p.co.x for p in hide.keyframe_points if p.co.y==0)
        assert all(hide.evaluate(f)==0 for f in range(round(birth),697)),ob.name
        tails=[f for f in curves if f.data_path in ('location','rotation_euler')]
        assert all(abs(f.evaluate(600)-f.evaluate(696))<1e-8 for f in tails)
        debris.append(ob.name)
    assert debris
    assert not any(o.name.startswith('304 worn cross-field bund') for o in bpy.data.objects)
    bpy.ops.wm.open_mainfile(filepath=str(ROOT/'.runtime/art-direction/series01-sikh305/build-13/sequence.blend'),load_ui=False,use_scripts=False)
    before=protected();checks={k:before[k]==current[k] for k in current}
    result={'protected_checks':checks,'dependencies':dependencies,'persistent_settled_chip_count':len(debris),'green_overlay_count':0,'horse_samples':rows,'source_native':str(source.relative_to(ROOT)),'limits':'Skeletal endpoints are not deformed hoof contact; curves and image inspection do not certify real-time motion/audio.'}
    (out/'audit.json').write_text(json.dumps(result,indent=2))
    assert all(checks.values()),checks
