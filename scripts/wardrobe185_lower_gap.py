"""Exact evaluated rider/horse fit, not a decimated-contact inference.

Read-only source inspection. Diagnostic cutaways are separate temporary meshes;
no body, motion, garment or protected master is edited or saved.
"""
import json
from pathlib import Path
import numpy as np

SOURCE_SHA='a483fdfd401a9bfc623f9d52611c2d453c540982c454420f30f381ab20566d7a'


def local_faces(points,faces,low=(-1.5,-2.5,-7.5),high=(1.5,1.5,-4.5)):
    triangles=points[faces]
    return faces[np.all(triangles.max(1)>=low,axis=1)&np.all(triangles.min(1)<=high,axis=1)]


def run(out):
    import bpy
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    from wardrobe_motion178 import BASE,digest,check_protected
    from wardrobe185_lower import fast_geometry
    from wardrobe185_lower_cloth import panel
    from wardrobe_doublewrap185 import color
    from wardrobe_riding_fit import fit_render
    source=BASE/'wardrobe185-lowerreview06/integration-working.blend'
    if digest(source)!=SOURCE_SHA:raise ValueError('Unbound exact gap source')
    (out/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False)
    scene=bpy.context.scene;scene.camera.animation_data_clear();scene.camera.data.type='ORTHO'
    scene.cycles.device='CPU';scene.cycles.samples=8;scene.render.use_persistent_data=True
    names={'body':'MF_studio_adult_body','upper':'MF185_fitted_upper_tunic',
        'pants':'MF_fit_trousers_173_visible','horse':'MF185_gait_horse',
        'saddle':'MF185_gait_saddle','pad':'MF185_gait_saddle.pad'}
    records={};payload={}
    for frame in (169,193,216,217,223,326,360):
        scene.frame_set(frame);bpy.context.view_layer.update();geometry={};trees={};row={}
        for key,name in names.items():
            ob=bpy.data.objects[name];p,f=fast_geometry(ob);f=local_faces(p,f)
            geometry[key]=(p,f);trees[key]=BVHTree.FromPolygons(p.tolist(),f.tolist(),all_triangles=True)
            if frame in (169,217,223):payload[key+'_points_'+str(frame)]=p;payload[key+'_faces_'+str(frame)]=f
        for actor in ('body','upper','pants'):
            for mount in ('horse','saddle','pad'):
                pairs=trees[actor].overlap(trees[mount]);p,f=geometry[actor]
                r={'local_triangle_pairs':len(pairs)}
                if pairs:
                    ids=np.unique(np.array(pairs)[:,0]);patch=p[np.unique(f[ids])]
                    r['actor_patch_bounds_native']=[patch.min(0).tolist(),patch.max(0).tolist()]
                    measurements=[]
                    for point in p[np.unique(f[ids])][::max(1,len(np.unique(f[ids]))//500)]:
                        hit,normal,index,distance=trees[mount].find_nearest(Vector(point))
                        measurements.append(float((Vector(point)-hit).dot(normal)*122.92759120464325))
                    r['nearest_normal_signed_distances_mm_quantiles']=np.quantile(measurements,[0,.05,.5,.95,1]).tolist()
                    r['distance_caveat']='Local nearest normal estimates; not a closed-volume penetration certificate'
                row[actor+'__'+mount]=r
        records[frame]=row
        if frame in (169,217,223):
            # Full rendered scene first, then diagnostic central strip of actual
            # evaluated triangles. The latter is explicitly not an asset render.
            fit_render(out,'actual-left-'+str(frame),90,(0,-.3,-6.4),5.,(720,720))
            states=[(ob,ob.hide_render) for ob in scene.objects if ob.type in ('MESH','CURVE','CURVES')]
            for ob,_ in states:ob.hide_render=True
            temporary=[]
            for key,rgb in (('horse',(.22,.13,.07)),('saddle',(.10,.07,.04)),('pad',(.25,.3,.3)),
                            ('body',(.75,.32,.18)),('pants',(.08,.18,.5)),('upper',(.15,.65,.4))):
                p,f=geometry[key];f=local_faces(p,f,(-.3,-2.5,-7.5),(.3,1.5,-4.5))
                ob=panel('DIAGNOSTIC center slice '+key,p,f);ob.data.materials.append(color('Gap '+key,rgb));temporary.append(ob)
            fit_render(out,'center-slice-'+str(frame),90,(0,-.3,-6.2),3.8,(720,720))
            for ob in temporary:bpy.data.objects.remove(ob,do_unlink=True)
            for ob,state in states:ob.hide_render=state
        print('Exact actor/horse gap',frame,flush=True)
    np.savez_compressed(out/'exact-local-geometry.npz',**payload)
    check_protected()
    (out/'result.json').write_text(json.dumps({'source_sha256':SOURCE_SHA,'frames':records,
        'scope':'Exact current evaluated geometry local waist region; no decimation, no source/native edits',
        'cutaway_colors':'skin orange, pants blue, upper green, horse brown, saddle dark, pad gray',
        'visual_gate':'NOT_RUN','protected_exact':True},indent=2)+'\n')
