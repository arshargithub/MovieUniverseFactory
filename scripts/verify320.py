"""Fixed scoped native checks. Frame-space facts, not perceptual admission."""
import json,sys,os,subprocess,math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
from movie_factory.production_knowledge import file_hash
from sikh320 import BASE,SOURCE,START,END
def worker(v):
    import bpy
    import numpy as np
    from mathutils import Vector
    from sikh319_verify import digest_object
    out=BASE/f'verify-{v:02d}';candidate=BASE/f'build-{v:02d}/sequence.blend'
    protected={};baseline={}
    for path in (SOURCE,candidate):
        bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False);s=bpy.context.scene;s.frame_set(283)
        names=[o.name for o in s.objects if o.name.startswith(('BIKE ','Motorcycle','irregular packed','low field bank','cultivated plain'))]+[s.camera.name]
        values={n:digest_object(bpy.data.objects[n]) for n in names}
        if path==SOURCE:protected=values
        else:changes=[n for n,h in protected.items() if values.get(n)!=h]
        rig=bpy.data.objects['horse.rig'];rows=[]
        for f in range(275,365):
            s.frame_set(f);bpy.context.view_layer.update()
            rows.append({'frame':f,'seconds':(f-1)/24,'hooves':{name:list(rig.matrix_world@rig.pose.bones[name].tail) for name in ('DEF-f_toe.L','DEF-f_toe.R')},'head':list(rig.matrix_world@rig.pose.bones['DEF-head'].head)})
        baseline['before' if path==SOURCE else 'after']=rows
    s.frame_set(283);upper=bpy.data.objects['320 articulated upper body mounted leader'];shirt=next(o for o in upper.children if o.name.startswith('319 anatomically'));palms=[o for o in upper.children if o.name.startswith('leader palm')];ids=json.loads(shirt['cuff_indices'])
    gaps=[];pole=[];gaze=[];neck_yaw=[]
    for f in range(START,END+1):
        s.frame_set(f);bpy.context.view_layer.update();ev=shirt.evaluated_get(bpy.context.evaluated_depsgraph_get());pts=np.array([p.co[:] for p in ev.data.vertices])
        for side,indices in ids.items():
            palm=next(o for o in palms if o.location.x*int(side)>0)
            point=ev.matrix_world@Vector(pts[indices].mean(axis=0));gaps.append((point-palm.matrix_world.translation).length)
        for actor in [o for o in s.objects if o.name.startswith('320 articulated upper body FOOT')]:
            head=next(o for o in actor.children if o.name.startswith('secondary adult head'))
            target=bpy.data.objects['BIKE travel owner'].matrix_world.translation-head.matrix_world.translation
            forward=head.matrix_world.to_3x3()@Vector((0,-1,0));forward.z=0;target.z=0
            gaze.append(math.degrees(math.acos(max(-1,min(1,forward.normalized().dot(target.normalized()))))))
            neck_yaw.append(abs((head.rotation_euler.z-math.pi+math.pi)%(2*math.pi)-math.pi))
            shaft=next(o for o in actor.children if o.name=='spear' or o.name.startswith('spear.'));hand=next(o for o in actor.children if o.name.startswith('secondary closed hand') and o.location.x>0)
            a,b=[shaft.matrix_world@Vector(p.co[:3]) for p in (shaft.data.splines[0].points[0],shaft.data.splines[0].points[-1])]
            axis=(b-a).normalized();ap=hand.matrix_world@Vector((.005,0,0));delta=ap-a;pole.append((delta-axis*delta.dot(axis)).length)
    (out/'hoof-trajectories.json').write_text(json.dumps(baseline,indent=2))
    report={'source_sha':file_hash(SOURCE),'candidate_sha':file_hash(candidate),'protected_objects':len(protected),'protected_changes':changes,'leader_cuff_max_m':max(gaps),'crowd_pole_max_m':max(pole),'crowd_gaze_max_horizontal_error_degrees':max(gaze),'crowd_neck_yaw_max_radians':max(neck_yaw),'thresholds_m':{'cuff':.012,'pole':.010},'gaze_threshold_degrees':8,'neck_yaw_threshold_radians':1.13,'direct_motion':False,'direct_audio':False,'status':'PASS' if not changes and max(gaps)<.012 and max(pole)<.010 and max(gaze)<8 and max(neck_yaw)<1.13 else 'FAIL'}
    (out/'interfaces.json').write_text(json.dumps(report,indent=2));print(json.dumps(report),flush=True)
def main():
    v=int(sys.argv[1]);assert 1<=v<=20
    if sys.argv[-1]=='worker':worker(v);return
    from movie_factory import production_knowledge as pk
    task=json.loads((ROOT/f'results/sikh320/look-{v}/task.json').read_text());task['id']=f'sikh320-verification-{v}'
    for p in (Path(__file__).resolve(),ROOT/'scripts/sikh319_verify.py',SOURCE):task['inputs'][str(p.relative_to(ROOT))]=file_hash(p)
    packet=pk.task_packet(ROOT,task);assert packet['dispatch_ready'],packet['blockers']
    record=ROOT/f'results/sikh320/verify-{v}';record.mkdir(exist_ok=True)
    for name,value in [('task',task),('packet',packet)]: (record/(name+'.json')).write_text(json.dumps(value,indent=2))
    (record/'packet.md').write_text(pk.packet_markdown(packet))
    if '--prepare' in sys.argv:print(record/'packet.md');return
    out=BASE/f'verify-{v:02d}';out.mkdir(exist_ok=False)
    env={k:os.environ[k] for k in ('PATH','HOME','TMPDIR','LANG','LC_ALL') if k in os.environ}
    for k,d in [('BLENDER_USER_CONFIG','config'),('BLENDER_USER_SCRIPTS','scripts'),('BLENDER_USER_DATAFILES','data')]:env[k]=str(out/'sandbox'/d)
    with (out/'worker.log').open('x') as log:
        r=subprocess.run(['/Applications/Blender.app/Contents/MacOS/Blender','-b','--factory-startup','--disable-autoexec','--offline-mode','--python-exit-code','7','--python',str(Path(__file__).resolve()),'--',str(v),'worker'],env=env,stdout=log,stderr=subprocess.STDOUT)
    assert r.returncode==0,out/'worker.log'
    assert all(file_hash(ROOT/p)==h for p,h in task['inputs'].items())
    print(out/'interfaces.json')
if __name__=='__main__':
    if '--' in sys.argv:sys.argv=[sys.argv[0]]+sys.argv[sys.argv.index('--')+1:]
    main()
