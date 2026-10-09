"""Fixed integrated render/reopen controls; no runtime paths or code."""
import json,sys,time,shutil
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import wardrobe_motion178 as base
from entrance198_terrain import fingerprint
OPS={'controls04':(217,265,295,325,349,360),'fixed05':tuple(range(337,361)),
     'before06':tuple(range(337,361)),'motion07':tuple(range(217,361)),'verify08':(223,295,360),
     'diagnostic09':(217,265,295,325,349,360),'controls11':(217,265,295,325,349,360),
     'hair14':(235,343,350,349,360),'motion18':tuple(range(217,361)), 'verify19':(223,295,343,350,360)}

def validate(job):
    if set(job)!={'operation'} or job['operation'] not in OPS:raise ValueError('Fixed render only')
    op=job['operation'];stage='entrance198-build02' if op=='before06' else ('entrance200-candidate03' if op in ('controls04','diagnostic09') else 'entrance200-candidate10')
    if op in ('motion18','verify19'):stage='entrance200-seal17'
    source=base.BASE/stage/'scene.blend';out=base.BASE/('entrance200-'+op);r=json.loads((source.parent/'result.json').read_text())
    if out.exists() or base.digest(source)!=r['native_sha256']:raise ValueError('Source or output mismatch')
    for row in r['caches']:
        p=(source.parent/row['path']).resolve()
        if not p.is_relative_to(base.BASE.resolve()) or base.digest(p)!=row['sha256']:raise ValueError('Cache mismatch')
    if op in ('motion07','motion18'):
        gate=json.loads((source.parent/'internal-review.json').read_text())
        if gate.get('status')!='PROCEED_TO_FULL_MOTION' or gate.get('source_sha256')!=r['native_sha256']:raise ValueError('Missing source-bound internal gate')
    return source,out,r

def render(scene,path):
    import bpy
    scene.render.filepath=str(path)
    if bpy.ops.render.render(write_still=True)!={'FINISHED'} or not path.is_file():raise ValueError('Incomplete render')

def crops(scene,out):
    import bpy
    from mathutils import Vector,Matrix
    scene.frame_set(360);rig=bpy.data.objects['MF_body156_fit_rig'];body=bpy.data.objects['MF_studio_adult_body'];camera=scene.camera
    camera.animation_data_clear();camera.data.type='PERSP';camera.data.lens=55
    scene.render.resolution_x=480;scene.render.resolution_y=480
    def look(target,delta):
        camera.location=target+Vector(delta);camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler()
    for side,sign in [('L',1),('R',-1)]:
        target=rig.matrix_world@rig.pose.bones['hand.'+side].head.lerp(rig.pose.bones['hand.'+side].tail,.6)
        look(target,(sign*2.8,-3.5,1.5));render(scene,out/('grip-'+side+'.png'))
    target=rig.matrix_world@rig.pose.bones['MF185_neck'].head+Vector((0,-.15,.2));look(target,(2.,-8.5,1.3));render(scene,out/'neck-lit.png')
    clay=bpy.data.materials.new('200 diagnostic clay');clay.use_nodes=True
    bs=clay.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.3,.3,.3,1);bs.inputs['Roughness'].default_value=.8
    for i in (0,3,4):body.data.materials[i]=clay
    render(scene,out/'neck-clay.png')

def neutral_check(scene,out):
    import bpy
    from mathutils import Matrix
    from wardrobe_motion178_controls import render_geometry_paused
    rig=bpy.data.objects['MF_body156_fit_rig'];body=bpy.data.objects['MF_studio_adult_body']
    m=body.modifiers['200 preserve rest neck under riding extension']
    def points():
        bpy.context.view_layer.update();ev=body.evaluated_get(bpy.context.evaluated_depsgraph_get());me=ev.to_mesh();p=np.array([v.co[:] for v in me.vertices]);ev.to_mesh_clear();return p
    action=rig.animation_data.action;slot=rig.animation_data.action_slot;old={b.name:b.matrix_basis.copy() for b in rig.pose.bones}
    # Isolate the corrected modifier at rest without modifying saved state.
    rig.animation_data.action=None
    for b in rig.pose.bones:b.matrix_basis=Matrix.Identity(4)
    m.show_viewport=False;a=points();m.show_viewport=True;b=points();error=float(abs(a-b).max());neutral_factor=float(m.factor)
    rig.animation_data.action=action;rig.animation_data.action_slot=slot
    for b in rig.pose.bones:b.matrix_basis=old[b.name]
    scene.frame_set(360)
    row={'neutral_max_vertex_delta':error,'neutral_factor':neutral_factor,'status':'PASS' if error<2e-5 and neutral_factor==0 else 'FAIL','threshold':2e-5}
    (out/'neutral-check.json').write_text(json.dumps(row,indent=2)+'\n')
    return row

def main():
    import bpy
    job=json.loads(Path(sys.argv[sys.argv.index('--')+1]).read_text());source,out,r=validate(job);op=job['operation'];out.mkdir()
    (out/'handler.py').write_bytes(Path(__file__).read_bytes());bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False)
    scene=bpy.context.scene;scene.frame_set(217);base.check_protected();actual=fingerprint(scene)
    (out/'structural-parity.json').write_text(json.dumps({'status':'PASS' if actual==r['fingerprint'] else 'FAIL','actual':actual,'expected':r['fingerprint'],
        'mesh_names':[m.name for m in bpy.data.meshes],'action_names':[a.name for a in bpy.data.actions]},indent=2)+'\n')
    if actual!=r['fingerprint'] and op!='diagnostic09':raise ValueError('Reopened structure differs')
    if op in ('verify08','verify19'):
        from entrance193_render import cache_parity
        from entrance196_render import particle_parity
        cache_parity(r,out);particle_parity(scene,out)
        from wardrobe_motion178_controls import render_geometry_paused
        rig=bpy.data.objects['MF_body156_fit_rig'];errors=[]
        with np.load(source.parent/'motion.npz') as z:
            names=list(z['names']);expected=z['after']
        with render_geometry_paused():
            for f in (217,223,265,295,325,349,360):
                scene.frame_set(f);bpy.context.view_layer.update()
                actual=np.array([np.array(rig.matrix_world@rig.pose.bones[n].matrix) for n in names])
                errors.append(float(abs(actual-expected[f-217]).max()))
        (out/'pose-parity.json').write_text(json.dumps({'status':'PASS' if max(errors)<2e-5 else 'FAIL','max_error':max(errors),'frames':[217,223,265,295,325,349,360]},indent=2)+'\n')
        if max(errors)>=2e-5:raise ValueError('Reopened pose differs')
    else:
        for o in scene.objects:
            for m in o.modifiers:
                if m.type in ('SMOOTH','CORRECTIVE_SMOOTH','SUBSURF'):m.show_viewport=False
    scene.render.resolution_x=432;scene.render.resolution_y=768;scene.render.resolution_percentage=100
    scene.cycles.device='CPU';scene.cycles.samples=12;scene.render.use_persistent_data=op not in ('hair14','motion18','verify19')
    if op in ('fixed05','before06'):
        scene.frame_set(360);matrix=scene.camera.matrix_world.copy();scene.camera.animation_data_clear();scene.camera.matrix_world=matrix
        scene.render.resolution_x=288;scene.render.resolution_y=512;scene.cycles.samples=8
    frames=OPS[op]
    if op=='motion07':
        overview=(217,235,253,265,277,295,309,325,343,360);frames=overview+tuple(f for f in frames if f not in overview)
    rows=[]
    for f in frames:
        start=time.monotonic();scene.frame_set(f);path=out/f'frame-{f:04d}.png';reuse=False
        if op=='motion07' and f in OPS['controls11']:
            control=base.BASE/'entrance200-controls11';cr=json.loads((control/'result.json').read_text())
            if cr['source_sha256']!=r['native_sha256']:raise ValueError('Control source mismatch')
            shutil.copy2(control/path.name,path);reuse=True
        else:render(scene,path)
        rows.append({'frame':f,'seconds':time.monotonic()-start,'reused_control':reuse})
        (out/'progress.json').write_text(json.dumps({'completed':len(rows),'total':len(frames),'last_frame':f},indent=2)+'\n')
    base.check_protected()
    if op in ('controls04','diagnostic09','controls11'):crops(scene,out);neutral_check(scene,out)
    (out/'result.json').write_text(json.dumps({'source_sha256':r['native_sha256'],'frames':rows,'resolution':[432,768] if op not in ('fixed05','before06') else [288,512],'samples':12 if op not in ('fixed05','before06') else 8,'fps':24,'native_modified':False,'visual_gate':'NOT_RUN'},indent=2)+'\n')

if __name__=='__main__':main()
