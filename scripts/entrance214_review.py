"""Reopen and render only the reviewed214 native derivatives and fixed clocks."""
import json
import hashlib
import os
import sys
import time
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import wardrobe_motion178 as base

OPS={
    'proof09':('opening08',(245,277,300,330,360),False),
    'proof10':('route07',(390,427,472,550,620),False),
    'motion11':('opening08',tuple(range(217,361)),True),
    'motion12':('route07',tuple(range(361,649)),True),
    'proof13':('route07',(390,427,472,550,620),False),
    'proof16':('opening14',(245,277,300,330,360),False),
    'proof17':('route15',(390,427,472,550,620),False),
    'motion18':('opening14',tuple(range(217,361)),True),
    'motion19':('route15',tuple(range(361,649)),True),
    'proof26':('217-opening24',(245,277,300,330,360),False),
    'proof27':('217-route25',(390,427,472,550,620),False),
    'motion28':('217-opening24',tuple(range(217,361)),True),
    'motion29':('217-route25',tuple(range(361,649)),True),
    'diagnostic30':('217-opening24',tuple(range(217,361)),True),
    'diagnostic31':('217-route25',tuple(range(361,649)),True),
    'diagnostic32':('217-opening24',tuple(range(217,361)),True),
    'diagnostic33':('217-route25',tuple(range(361,649)),True),
    'diagnostic34':('217-opening24',tuple(range(217,361)),True),
    'diagnostic35':('217-route25',tuple(range(361,649)),True),
    'diagnostic36':('217-opening24',tuple(range(217,361)),True),
    'diagnostic37':('217-route25',tuple(range(361,649)),True),
    'diagnostic38':('217-opening24',tuple(range(217,361)),True),
    'diagnostic39':('217-route25',tuple(range(361,649)),True),
    'proof40':('218-opening12',(277,330,360),False),
    'proof41':('218-route13',(390,427,472,550,620),False),
    'diagnostic42':('218-opening12',tuple(range(217,361)),True),
    'diagnostic43':('218-route13',tuple(range(361,649)),True),
    'diagnostic44':('218-route13',tuple(range(433,505)),True),
    'diagnostic45':('218-route13',tuple(range(505,649)),True),
}

def validate(job):
    if not isinstance(job,dict) or set(job)!={'operation'} or job['operation'] not in OPS:
        raise ValueError('Closed214 review operation required')
    return OPS[job['operation']]

def geometry_hash():
    """Same mesh digest as198 fingerprint, without unrelated action traversal."""
    import bpy
    h=hashlib.sha256()
    for m in sorted(bpy.data.meshes,key=lambda m:m.name):
        h.update(m.name.encode())
        for collection,prop,width,dtype in ((m.vertices,'co',3,np.float32),(m.loops,'vertex_index',1,np.int32),(m.polygons,'loop_total',1,np.int32)):
            a=np.empty(len(collection)*width,dtype=dtype);collection.foreach_get(prop,a);h.update(a.tobytes())
        if m.shape_keys:
            for block in m.shape_keys.key_blocks:
                a=np.empty(len(block.data)*3,dtype=np.float32);block.data.foreach_get('co',a);h.update(block.name.encode());h.update(a.tobytes())
    return h.hexdigest()

def main():
    import bpy
    from mathutils import Vector
    job=json.loads(Path(sys.argv[sys.argv.index('--')+1]).read_text());folder,frames,full=validate(job)
    diagnostic=job['operation'].startswith('diagnostic')
    isolated=diagnostic and job['operation'] not in ('diagnostic30','diagnostic31')
    coarse=job['operation'] in ('diagnostic38','diagnostic39','diagnostic42','diagnostic43','diagnostic44','diagnostic45')
    src=base.BASE/(('entrance'+folder) if folder.startswith(('217-','218-')) else ('entrance214-'+folder));out=base.BASE/('entrance214-'+job['operation'])
    record=json.loads((src/'result.json').read_text())
    if out.exists() or base.digest(src/'scene.blend')!=record['native_sha256'] or base.digest(src/'contact.npz')!=record['contact_sha256']:
        raise ValueError('Native/evidence changed or output exists')
    if full:
        admission=json.loads((src/'internal-review.json').read_text())
        if admission.get('status')!='PROCEED_TO_FULL_MOTION' or admission.get('source_sha256')!=record['native_sha256']:
            raise ValueError('Visual admission required')
    for row in record['caches']:
        path=(src/row['path']).resolve()
        if not path.is_relative_to(base.BASE.resolve()) or base.digest(path)!=row['sha256']:raise ValueError('Cache drift')
    out.mkdir();(out/'handler.py').write_bytes(Path(__file__).read_bytes())
    bpy.ops.wm.open_mainfile(filepath=str(src/'scene.blend'),load_ui=False,use_scripts=False);scene=bpy.context.scene
    base.check_protected()
    if geometry_hash()!=record['protected_geometry_sha256']:raise ValueError('Geometry drift on reopen')
    for ob in scene.objects:
        for m in ob.modifiers:
            if m.type in ('SMOOTH','CORRECTIVE_SMOOTH','SUBSURF'):m.show_viewport=False
    scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=8;scene.render.use_persistent_data=False
    scene.render.threads_mode='FIXED';scene.render.threads=8
    scene.render.resolution_x=432;scene.render.resolution_y=768;scene.render.resolution_percentage=100
    diagnostic_camera=None
    if diagnostic:
        scene.render.engine='BLENDER_WORKBENCH'
        sh=scene.display.shading;sh.light='STUDIO';sh.color_type='OBJECT';sh.show_shadows=True;sh.show_cavity=True
        sh.background_type='WORLD';scene.world.color=(.20,.23,.27)
        for ob in scene.objects:
            ob.color=(.25,.31,.48,1) if any(k in ob.name.lower() for k in ('shawl','sleeve','tunic','headfall')) else (.55,.42,.31,1)
            if ob.name=='MF217 fitted leather gloves':ob.color=(.16,.09,.045,1)
            if ob.name.startswith('MF185_rein'):ob.color=(.40,.20,.08,1)
            # Volumetric dust is a lighting effect, not solid collision geometry.
            if ob.type=='MESH' and any(m and m.use_nodes and any(n.type=='OUTPUT_MATERIAL' and n.inputs['Volume'].is_linked for n in m.node_tree.nodes) for m in ob.data.materials):ob.hide_render=True
        data=bpy.data.cameras.new('217 diagnostic contact camera');diagnostic_camera=bpy.data.objects.new(data.name,data);scene.collection.objects.link(diagnostic_camera);data.lens=55
        if isolated:
            # Reversible diagnostic visibility only. Render no landscape, hair,
            # cloth simulation or dust; their actual integration is checked in
            # the bound Cycles controls. Keep rig/parents and exact hand mesh.
            keep={'MF_studio_adult_body','MF217 fitted leather gloves','MF185_rein_L','MF185_rein_R'}
            for ob in scene.objects:
                if ob.type in ('MESH','CURVE','CURVES') and ob.name not in keep:
                    ob.hide_render=True;ob.hide_viewport=True
            scene.display.render_aa='8'
            if job['operation'] not in ('diagnostic32','diagnostic33'):
                # In-memory dependency closure, never saved back to production.
                retained={bpy.data.objects[n] for n in keep if n in bpy.data.objects}
                retained.update((scene.camera,diagnostic_camera,bpy.data.objects['MF_body156_fit_rig']))
                pending=list(retained)
                while pending:
                    ob=pending.pop();refs=[ob.parent]
                    owners=[ob,ob.data,*ob.modifiers,*ob.constraints]
                    if ob.type=='ARMATURE':
                        owners.extend(c for b in ob.pose.bones for c in b.constraints)
                    for owner in owners:
                        if owner is None:continue
                        for prop in owner.bl_rna.properties:
                            if prop.type=='POINTER' and prop.identifier!='rna_type':
                                value=getattr(owner,prop.identifier,None)
                                if isinstance(value,bpy.types.Object):refs.append(value)
                        ad=getattr(owner,'animation_data',None)
                        if ad:
                            for driver in ad.drivers:
                                refs.extend(t.id for v in driver.driver.variables for t in v.targets if isinstance(t.id,bpy.types.Object))
                    for ref in refs:
                        if ref is not None and getattr(ref,'name',None) in bpy.data.objects and bpy.data.objects[ref.name]==ref and ref not in retained:
                            retained.add(ref);pending.append(ref)
                removed=[ob for ob in bpy.data.objects if ob not in retained]
                print('217 diagnostic closure',len(retained),'retained',len(removed),'removed in memory',flush=True)
                for ob in removed:bpy.data.objects.remove(ob,do_unlink=True)
            if coarse:
                for ob in scene.objects:
                    for m in ob.modifiers:
                        if m.type in ('SMOOTH','CORRECTIVE_SMOOTH','SUBSURF'):
                            m.show_render=False
                print('217 coarse motion: surface smoothing/subdivision disabled, pose and contact unchanged',flush=True)
    with np.load(src/'contact.npz') as z:data={k:z[k].copy() for k in z.files}
    reuse={}
    if full and job['operation'] in ('motion18','motion19','motion28','motion29'):
        proof_name={'motion18':'proof16','motion19':'proof17','motion28':'proof26','motion29':'proof27'}[job['operation']]
        proof=base.BASE/('entrance214-'+proof_name)
        proofrecord=json.loads((proof/'result.json').read_text())
        if not proofrecord.get('complete') or proofrecord['source_sha256']!=record['native_sha256'] or proofrecord['fps']!=24 or proofrecord['resolution']!=[432,768]:
            raise ValueError('Incompatible proof reuse')
        for r in proofrecord['frames']:
            p=proof/f"frame-{r['index']:04d}.png"
            if base.digest(p)!=r['sha256']:raise ValueError('Modified proof frame')
            reuse[r['native_frame']]=p
    hand_mask=None;hand_groups={}
    if job['operation'] in ('diagnostic44','diagnostic45'):
        # Supplement the obscured turn interval without changing production.
        # Preserve evaluated hand vertices; hide the opposite arm/body only.
        body=bpy.data.objects['MF_studio_adult_body']
        names={g.index:g.name for g in body.vertex_groups}
        for side in ('L','R'):
            group=body.vertex_groups.new(name='218 diagnostic hand '+side)
            ids=[v.index for v in body.data.vertices if sum(g.weight for g in v.groups
                if names.get(g.group,'').endswith('.'+side) and
                ('finger' in names[g.group] or names[g.group]=='hand.'+side))>.01]
            group.add(ids,1.,'REPLACE');hand_groups[side]=group.name
        hand_mask=body.modifiers.new('218 diagnostic visibility only','MASK')
        hand_mask.show_render=False;hand_mask.show_viewport=False
    rig=bpy.data.objects['MF_body156_fit_rig'];rows=[]
    for f in frames:
        t=time.monotonic();scene.frame_set(f);bpy.context.view_layer.update();i=list(data['frames']).index(f)
        pose=np.array([np.array(rig.matrix_world@rig.pose.bones[str(n)].matrix) for n in data['names']])
        pose_error=float(abs(pose-data['before'][i]).max())
        camera_error=max(float(abs(np.array(scene.camera.matrix_world)-data['cameras'][i]).max()),abs(scene.camera.data.lens-data['lenses'][i]))
        thumb_error=float(abs(np.array([np.array(rig.pose.bones[str(n)].matrix_basis) for n in data['thumb_names']])-data['thumb_bases'][i]).max())
        pts=np.array([[list(ob.matrix_world@p.co.to_3d()) for p in ob.data.splines[0].points]
                      for ob in [bpy.data.objects['MF185_rein_'+s] for s in ('L','R')]])
        rein_error=float(abs(pts-data['reins'][i]).max())
        errors=dict(protected_pose_error=pose_error,camera_error=camera_error,thumb_error=thumb_error,rein_error=rein_error)
        if max(errors.values())>2e-5:
            (out/'failure.json').write_text(json.dumps(dict(native_frame=f,errors=errors,
                per_bone={str(n):float(abs(pose[k]-data['before'][i,k]).max()) for k,n in enumerate(data['names'])
                          if abs(pose[k]-data['before'][i,k]).max()>2e-5}),indent=2)+'\n')
            raise ValueError('Reopen motion or contact mismatch: '+json.dumps(errors))
        p=out/f'frame-{f-217:04d}.png';scene.render.filepath=str(p)
        if f in reuse:os.link(reuse[f],p)
        elif bpy.ops.render.render(write_still=True)!={'FINISHED'}:raise ValueError('Render failed')
        if diagnostic:
            actual_camera=scene.camera;hidden=[]
            for ob in scene.objects:
                if ob.type in ('MESH','CURVE','CURVES') and ob.name not in ('MF_studio_adult_body','MF217 fitted leather gloves','MF185_rein_L','MF185_rein_R'):
                    hidden.append((ob,ob.hide_render));ob.hide_render=True
            scene.camera=diagnostic_camera;scene.render.resolution_x=320;scene.render.resolution_y=320
            for side,sign in (('L',1),('R',-1)):
                if hand_mask:
                    hand_mask.vertex_group=hand_groups[side];hand_mask.show_render=True
                target=rig.matrix_world@rig.pose.bones['hand.'+side].head.lerp(rig.pose.bones['hand.'+side].tail,.6)
                diagnostic_camera.location=target+Vector((-sign*2,-3,-.4))
                diagnostic_camera.rotation_euler=(target-diagnostic_camera.location).to_track_quat('-Z','Y').to_euler()
                scene.render.filepath=str(out/f'{side}-{f-217:04d}.png')
                if bpy.ops.render.render(write_still=True)!={'FINISHED'}:raise ValueError('Contact render interrupted')
            if hand_mask:hand_mask.show_render=False
            for ob,flag in hidden:ob.hide_render=flag
            scene.camera=actual_camera;scene.render.resolution_x=432;scene.render.resolution_y=768
        row=dict(index=f-217,native_frame=f,sha256=base.digest(p),seconds=time.monotonic()-t,
                 protected_pose_error=pose_error,camera_error=camera_error,thumb_error=thumb_error,rein_error=rein_error,
                 reused_from=str(reuse[f].relative_to(base.ROOT)) if f in reuse else None,
                 contacts={s:base.digest(out/f'{s}-{f-217:04d}.png') for s in ('L','R')} if diagnostic else None)
        rows.append(row)
        tmp=out/'progress.tmp';tmp.write_text(json.dumps(dict(source_sha256=record['native_sha256'],frames=rows,complete=False),indent=2)+'\n');tmp.replace(out/'progress.json')
        print('214 FRAME',f,round(row['seconds'],2),flush=True)
    if isolated:
        if base.digest(src/'scene.blend')!=record['native_sha256']:raise ValueError('Production file changed')
    else:base.check_protected()
    (out/'result.json').write_text(json.dumps(dict(source_sha256=record['native_sha256'],frames=rows,complete=True,
       fps=24,resolution=[432,768],renderer='WORKBENCH_MOTION_ONLY' if diagnostic else 'CYCLES_CPU',
       isolated_hands=isolated,coarse_surfaces=coarse,visual_gate='NOT_RUN'),indent=2)+'\n')

if __name__=='__main__':main()
