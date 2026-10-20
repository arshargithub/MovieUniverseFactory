"""Read-only preservation and actual garment-interface evidence for319."""
import hashlib
import json
import bpy
import numpy as np
from pathlib import Path
from sikh319 import SOURCE

def digest_object(ob):
    h=hashlib.sha256()
    def add(value):h.update(json.dumps(value,sort_keys=True,separators=(',',':')).encode())
    add({'name':ob.name,'type':ob.type,'parent':ob.parent.name if ob.parent else None,
         'render':ob.hide_render,'matrix':[list(r) for r in ob.matrix_world]})
    if ob.type=='MESH':
        a=np.empty(len(ob.data.vertices)*3,dtype=np.float32);ob.data.vertices.foreach_get('co',a);h.update(a.tobytes())
        a=np.empty(len(ob.data.loops),dtype=np.int32);ob.data.loops.foreach_get('vertex_index',a);h.update(a.tobytes())
    if hasattr(ob.data,'materials'):add([m.name if m else None for m in ob.data.materials])
    for owner in (ob,ob.data,getattr(ob.data,'shape_keys',None)):
        ad=getattr(owner,'animation_data',None);action=ad.action if ad else None
        if action:
            for layer in action.layers:
                for strip in layer.strips:
                    for bag in strip.channelbags:
                        for fc in bag.fcurves:
                            add([fc.data_path,fc.array_index,[(list(p.co),p.interpolation) for p in fc.keyframe_points]])
    return h.hexdigest()

def verify(out,candidate):
    # Protected-scene comparison uses the same explicit frame on both sources.
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE),load_ui=False,use_scripts=False)
    bpy.context.scene.frame_set(283)
    roots=[bpy.data.objects['mounted leader']]+[o for o in bpy.data.objects if o.name.startswith('FOOT WARRIOR ')]
    excluded={o.name for r in roots for o in [r,*r.children_recursive]}
    source={o.name:digest_object(o) for o in bpy.context.scene.objects if o.name not in excluded}
    bpy.ops.wm.open_mainfile(filepath=str(candidate),load_ui=False,use_scripts=False)
    s=bpy.context.scene;s.frame_set(283)
    changed=[name for name,h in source.items() if name not in bpy.data.objects or digest_object(bpy.data.objects[name])!=h]
    missing=[im.filepath for im in bpy.data.images if im.source=='FILE' and not im.packed_file and im.filepath and not Path(bpy.path.abspath(im.filepath)).exists()]
    root=bpy.data.objects['mounted leader']
    shirt=next(o for o in root.children if o.name.startswith('319 anatomically'))
    palms=[o for o in root.children if o.name.startswith('leader palm')]
    cuff_ids=json.loads(shirt['cuff_indices'])
    rows=[]
    for f in range(1,697):
        s.frame_set(f)
        ev=shirt.evaluated_get(bpy.context.evaluated_depsgraph_get())
        pts=np.array([v.co[:] for v in ev.data.vertices])
        for label,ids in cuff_ids.items():
            p=next(o for o in palms if o.location.x*int(label)>0)
            target=np.array((root.matrix_world.inverted()@p.matrix_world.translation)[:])
            rows.append({'frame':f,'side':int(label),'cuff_to_palm_m':float(np.linalg.norm(pts[ids].mean(axis=0)-target))})
        if not np.isfinite(pts).all():raise ValueError('Nonfinite garment')
    report={'protected_objects_compared':len(source),'protected_changes':changed,
            'missing_images':missing,'leader_cuff_centroid_max_m':max(r['cuff_to_palm_m'] for r in rows),
            'samples':696,'limits':'Geometry/action preservation and cuff-centroid checks, not perceptual animation, grip or cloth acceptance.',
            'thresholds':{'cuff_centroid_m':.012},
            'status':'PASS' if not changed and not missing and max(r['cuff_to_palm_m'] for r in rows)<.012 else 'FAIL'}
    (out/'interfaces.json').write_text(json.dumps(report,indent=2))
    (out/'cuff-samples.json').write_text(json.dumps(rows,indent=2))
    print(json.dumps(report),flush=True)
