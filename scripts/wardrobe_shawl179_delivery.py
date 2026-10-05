"""Fixed native cache review/reopen operations, never an appearance PASS."""
import json
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import wardrobe_motion178 as foundation
CACHE=foundation.BASE/'wardrobe179-weld-solve02/cloth-trajectory.npz'
CACHE_SHA='ab8af1ba14519bdbf48e599207966e39857c0c445a8a8b87c57e7700829cebf4'
OPERATIONS=('cacheaudit02','cacheaudit03','screen02','playback02','seal02','verify02')

def validate(job):
    if not isinstance(job,dict) or set(job)!={'operation'} or job['operation'] not in OPERATIONS:
        raise ValueError('Fixed delivery operation only')
    if foundation.SOURCE.is_symlink() or foundation.digest(foundation.SOURCE)!=foundation.SOURCE_SHA:
        raise ValueError('Protected foundation mismatch')
    if CACHE_SHA is None or CACHE.is_symlink() or foundation.digest(CACHE)!=CACHE_SHA:
        raise ValueError('Unbound or modified native trajectory')
    out=foundation.BASE/('wardrobe179-'+job['operation'])
    if out.exists() or out.is_symlink():raise ValueError('Never overwrite evidence')
    return out

def geometry(ob):
    import bpy
    import numpy as np
    ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=ev.to_mesh()
    points=np.array([v.co[:] for v in mesh.vertices]);ev.to_mesh_clear()
    return points

def review_frames(out,frames,whole=False):
    import bpy
    from mathutils import Vector
    import wardrobe_studio as studio
    from wardrobe_riding_fit import fit_render
    scene=bpy.context.scene;scene.render.engine='CYCLES'
    scene.cycles.device='CPU';scene.cycles.samples=8;scene.render.use_persistent_data=True
    for frame in frames:
        scene.frame_set(frame);bpy.context.view_layer.update()
        center=studio.torso_matrix(-2.7)@Vector((0,.15,-1.7))
        for label,angle in (('front',0),('rear',180),('left',90),('right',270)):
            fit_render(out,'%s-%03d'%(label,frame),angle,tuple(center),8.,(540,600))
        if whole:
            fit_render(out,'whole-front-%03d'%frame,0,(0,0,-5.8),16.,(540,900))
            fit_render(out,'whole-side-%03d'%frame,90,(0,0,-5.8),16.,(540,900))

def main():
    import bpy
    import numpy as np
    import wardrobe_motion178_controls as controls
    from wardrobe_motion178_proof import assembly
    job=json.loads(Path(sys.argv[sys.argv.index('--')+1]).read_text());out=validate(job);out.mkdir()
    op=job['operation']
    for name in ('wardrobe_shawl179_delivery.py','wardrobe_motion178_proof.py',
                 'wardrobe_motion178_controls.py','wardrobe_motion178_playback.py',
                 'wardrobe_underarm179_repair.py','wardrobe_motion178.py'):
        (out/name).write_bytes((ROOT/'scripts'/name).read_bytes())
    if op=='verify02':
        sealed=foundation.BASE/'wardrobe179-seal02'
        record=json.loads((sealed/'result.json').read_text());native=sealed/'moving-wardrobe.blend'
        if native.is_symlink() or foundation.digest(native)!=record['native_sha256']:
            raise ValueError('Sealed native mismatch')
        bpy.ops.wm.open_mainfile(filepath=str(native),load_ui=False,use_scripts=False)
        display=bpy.data.objects['MF178_moving_shawl'];foundation.check_protected()
        import wardrobe_studio as studio
        with np.load(CACHE,allow_pickle=False) as trajectory:
            matrices=trajectory['chest_matrices'].copy()
        with controls.render_geometry_paused():
            display.hide_viewport=False
            for frame in range(97,289):
                bpy.context.scene.frame_set(frame);bpy.context.view_layer.update()
                if abs(display.data.shape_keys.eval_time-10*(frame-96))>1e-5:
                    raise ValueError('Reopened cache clock mismatch')
                if np.max(np.abs(np.array(studio.torso_matrix(-1.))-matrices[frame-97]))>1e-6:
                    raise ValueError('Reopened actor/cache motion mismatch')
        with np.load(sealed/'evaluated.npz',allow_pickle=False) as expected:
            errors={}
            for frame in (97,145,288):
                bpy.context.scene.frame_set(frame);bpy.context.view_layer.update()
                points=geometry(display);ref=expected[str(frame)]
                if points.shape!=ref.shape:raise ValueError('Reopened topology mismatch')
                errors[str(frame)]=float(np.max(np.abs(points-ref)))
                if errors[str(frame)]>2e-5:raise ValueError('Reopened geometry mismatch')
        review_frames(out,(145,));result={'reopened':True,'evaluated_errors':errors}
    else:
        bpy.ops.wm.open_mainfile(filepath=str(foundation.SOURCE),load_ui=False,use_scripts=False)
        foundation.check_protected()
        with np.load(CACHE,allow_pickle=False) as record:display=assembly(record,3256,integrated=True)
        if op in ('cacheaudit02','cacheaudit03'):
            # A valid animated eval_time alone does not prove actual key data
            # samples match the solver. Audit the unmodified evaluated mesh.
            states=[(m,m.show_viewport) for m in display.modifiers]
            for mod,_ in states:mod.show_viewport=False
            errors=[]
            with controls.render_geometry_paused():
                display.hide_viewport=False
                with np.load(CACHE,allow_pickle=False) as trajectory:
                    for frame in range(97,289):
                        bpy.context.scene.frame_set(frame);bpy.context.view_layer.update()
                        points=geometry(display);expected=trajectory['frames'][frame-97]
                        if points.shape!=expected.shape:raise ValueError('Raw cached topology mismatch')
                        errors.append(float(np.max(np.abs(points-expected))))
                        if frame%24==0:print('179 actual raw cache audit',frame,flush=True)
            for mod,visible in states:mod.show_viewport=visible
            if max(errors)>2e-5:raise ValueError('Evaluated raw cache differs from native trajectory: %s'%max(errors))
            review_frames(out,(97,145))
            result={'all192_raw_cache_max_error':max(errors),'purpose':'Reconstruction diagnostic for rejected native screen, not approval'}
        elif op=='screen02':review_frames(out,(97,121,145,193,241,288),whole=True)
        elif op=='playback02':
            from mathutils import Vector
            import wardrobe_studio as studio
            from wardrobe_riding_fit import fit_render
            scene=bpy.context.scene
            scene.render.engine='BLENDER_WORKBENCH'
            scene.display.shading.light='STUDIO';scene.display.shading.color_type='MATERIAL'
            scene.display.shading.show_shadows=True;scene.display.shading.show_cavity=True
            for label,angle in (('front',0),('rear',180),('left',90),('right',270)):
                folder=out/label;folder.mkdir()
                for frame in range(97,289):
                    scene.frame_set(frame);bpy.context.view_layer.update()
                    center=studio.torso_matrix(-2.7)@Vector((0,.15,-1.7))
                    fit_render(folder,'%04d'%frame,angle,tuple(center),8.,(540,600))
                    if frame%24==0:print('179 complete geometry playback',label,frame,flush=True)
            result={'geometry_frames_per_angle':192,'angles':4,'fps':24,
                    'workbench_is_not_texture_or_style_acceptance':True}
        else:
            samples={}
            for frame in (97,145,288):
                bpy.context.scene.frame_set(frame);bpy.context.view_layer.update()
                samples[str(frame)]=geometry(display)
            np.savez_compressed(out/'evaluated.npz',**samples)
            bpy.context.scene.frame_set(97);bpy.ops.file.pack_all()
            native=out/'moving-wardrobe.blend'
            bpy.ops.wm.save_as_mainfile(filepath=str(native))
            result={'native_sha256':foundation.digest(native),
                    'representation':'Editable baked native per-frame cloth keys, not a portable live solver',
                    'native_fps':24,'native_frame_start':97,'native_frame_end':288}
        result=locals().get('result',{})
    foundation.check_protected()
    result.update({'protected_exact':True,'cache_sha256':CACHE_SHA,
                   'visual_gate':'NOT_RUN','director_acceptance':'NOT_RUN',
                   'scope':'Single-shawl eight-second local wardrobe proof; not a horse gait, contact or final shot qualification'})
    (out/'result.json').write_text(json.dumps(result,indent=2)+'\n')

if __name__=='__main__':main()
