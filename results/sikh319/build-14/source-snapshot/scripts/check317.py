"""Read-only fixed candidate08 contact and persistence checks."""
import sys,json,os,subprocess,time,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'.runtime/art-direction/series01-sikh317';SOURCE=BASE/'build-08/sequence.blend';OUT=BASE/'check-08'
def worker():
    import bpy
    import numpy as np
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    from movie_factory import sikh317_motion as m
    from sikh315_verify import verify
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE),load_ui=False,use_scripts=False)
    bpy.context.scene.frame_set(324);rig=bpy.data.objects['horse.rig'];bones=[]
    for pb in rig.pose.bones:
        if 'forefoot' in pb.name or 'f_toe' in pb.name:
            bones.append({'name':pb.name,'parent':pb.parent.name if pb.parent else None,'mode':pb.rotation_mode,'quaternion':list(pb.rotation_quaternion),'head':list(rig.matrix_world@pb.head),'tail':list(rig.matrix_world@pb.tail),'constraints':[{'type':c.type,'subtarget':getattr(c,'subtarget',None),'influence':c.influence} for c in pb.constraints]})
    (OUT/'hoof-chain.json').write_text(json.dumps(bones,indent=2))
    verify(OUT,SOURCE.parent)
    s=bpy.context.scene;road=bpy.data.objects['irregular packed farm track'];ground=BVHTree.FromPolygons([v.co.copy() for v in road.data.vertices],[list(p.vertices) for p in road.data.polygons])
    wheels=[bpy.data.objects['BIKE '+n+' rolling owner'] for n in ('front','rear')]
    tires=[next(o for o in owner.children if o.type=='MESH' and 'charcoal tire' in o.name) for owner in wheels]
    verts=[np.asarray([list(v.co) for v in ob.data.vertices]) for ob in tires]
    roots=sorted([o for o in bpy.data.objects if o.name.startswith('FOOT WARRIOR ')],key=lambda o:int(o.name.split()[-1]))
    feet=[sorted([o for o in r.children if o.name.startswith('PROXY boot')],key=lambda o:o.name) for r in roots]
    pants=[sorted([o for o in r.children if o.name.startswith('317 evaluated crowd trousers')],key=lambda o:o.name) for r in roots]
    assert all(len(p)==2 for p in pants)
    leader=bpy.data.objects['mounted leader']
    sleeves=sorted([o for o in leader.children if o.name.startswith(globals().get('SLEEVE_PREFIX','317 endpoint-bound leader sleeve'))],key=lambda o:o.name)
    assert len(sleeves)==2,'Must inspect both visible sleeves'
    palms=sorted([o for o in leader.children if o.name.startswith('leader palm')],key=lambda o:o.name)
    leader_interfaces=[]
    previous={};wheel_errors=[];stance_errors=[];support_errors=[];seam_errors=[]
    for f in range(1,697):
        s.frame_set(f);bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get();t=(f-1)/24*m.RATE
        for sleeve,palm in zip(sleeves,palms):
            ev=sleeve.evaluated_get(deps);me=ev.to_mesh()
            center=sum((v.co for v in list(me.vertices)[-24:]),Vector())/24
            leader_interfaces.append({'frame':f,'sleeve':sleeve.name,'wrist_to_palm_m':(ev.matrix_world@center-palm.matrix_world.translation).length,'active_shape_sum':sum(k.value for k in sleeve.data.shape_keys.key_blocks[1:])})
            ev.to_mesh_clear()
        for ob,points in zip(tires,verts):
            matrix=np.asarray(ob.matrix_world);world=points@matrix[:3,:3].T+matrix[:3,3];p=world[np.argmin(world[:,2])];hit=ground.ray_cast(Vector((p[0],p[1],10)),Vector((0,0,-1)))[0]
            if hit is None:raise ValueError('No tire ground')
            wheel_errors.append(float(p[2]-hit.z))
        for i,(r,pair) in enumerate(zip(roots,feet)):
            for k,foot in enumerate(pair):
                d,h,_,_=m.crowd_step(t,i,k);p=foot.matrix_world.translation.copy();old=previous.get((i,k))
                if old and h==0 and old[1]==0 and d==old[2]:stance_errors.append((p-old[0]).length)
                if h==0:
                    hit=ground.ray_cast(p+Vector((0,0,5)),Vector((0,0,-1)))[0]
                    if hit is None:raise ValueError('No crowd ground')
                    support_errors.append(abs(p.z-.055*r.scale.z-hit.z))
                previous[i,k]=(p,h,d)
                ev=pants[i][k].evaluated_get(deps);me=ev.to_mesh()
                center=sum((v.co for v in list(me.vertices)[-24:]),Vector())/24
                seam_errors.append((ev.matrix_world@center-p).length);ev.to_mesh_clear()
    (OUT/'leader-clothing-interface.json').write_text(json.dumps(leader_interfaces,indent=2))
    fur=bpy.data.objects['317 rig-bound short horse nap'];body=bpy.data.objects['horse']
    missing=[]
    for im in bpy.data.images:
        if im.source=='FILE' and not im.packed_file and im.filepath and not Path(bpy.path.abspath(im.filepath)).exists():missing.append(im.filepath)
    report={'actual_rendered_tire_ground_max_m':max(abs(e) for e in wheel_errors),'planted_boot_center_drift_max_m':max(stance_errors),'boot_support_height_max_m':max(support_errors),'fur_has_pigmentation':bool(fur.data.color_attributes.get('315 coat pigmentation')),'fur_armature_shared':any(x.type=='ARMATURE' and x.object==bpy.data.objects['horse.rig'] for x in fur.modifiers),'missing_images':missing,'samples':696,'thresholds':{'tire_m':.016,'planted_drift_m':.0002,'boot_support_m':.0002},'limits':'Control/geometry checks, not natural movement or AV acceptance.'}
    report['evaluated_crowd_ankle_seam_max_m']=max(seam_errors);report['thresholds']['ankle_seam_m']=.001
    report['evaluated_leader_cuff_seam_max_m']=max(r['wrist_to_palm_m'] for r in leader_interfaces);report['thresholds']['cuff_seam_m']=.001
    report['status']='PASS' if report['actual_rendered_tire_ground_max_m']<.016 and report['planted_boot_center_drift_max_m']<.0002 and report['boot_support_height_max_m']<.0002 and max(seam_errors)<.001 and report['evaluated_leader_cuff_seam_max_m']<.001 and report['fur_has_pigmentation'] and report['fur_armature_shared'] and not missing else 'FAIL'
    (OUT/'interfaces.json').write_text(json.dumps(report,indent=2));print(json.dumps(report),flush=True)
    if report['status']!='PASS':raise ValueError('Interface verification failed')
def main():
    from movie_factory.production_knowledge import file_hash
    OUT.mkdir(exist_ok=False);paths=[SOURCE,Path(__file__),ROOT/'scripts/sikh315_verify.py',ROOT/'src/movie_factory/sikh317_motion.py'];bindings={str(p.relative_to(ROOT)):file_hash(p) for p in paths};(OUT/'bindings.json').write_text(json.dumps(bindings,indent=2))
    for p in paths:
        if p.suffix=='.py':
            d=OUT/'source-snapshot'/p.relative_to(ROOT);d.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,d)
    env={k:os.environ[k] for k in ('PATH','HOME','TMPDIR','LANG','LC_ALL') if k in os.environ}
    for k,d in (('BLENDER_USER_CONFIG','config'),('BLENDER_USER_SCRIPTS','scripts'),('BLENDER_USER_DATAFILES','data')):env[k]=str(OUT/'sandbox'/d)
    start=time.monotonic()
    with (OUT/'worker.log').open('w') as log:r=subprocess.run(['/Applications/Blender.app/Contents/MacOS/Blender','-b','--factory-startup','--disable-autoexec','--offline-mode','--python-exit-code','7','--python',str(Path(__file__).resolve()),'--','worker'],env=env,stdout=log,stderr=subprocess.STDOUT)
    changed=[p for p,h in bindings.items() if file_hash(ROOT/p)!=h];(OUT/'receipt.json').write_text(json.dumps({'returncode':r.returncode,'seconds':time.monotonic()-start,'changed_sources':changed},indent=2))
    if r.returncode or changed:raise RuntimeError(OUT/'worker.log')
    print(OUT)
if __name__=='__main__':
    if sys.argv[-1]=='worker':sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')];worker()
    else:main()
