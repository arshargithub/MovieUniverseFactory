"""Fixed local visible sleeve endpoint correction; preserves actor and shot."""
import json,os,sys,time,subprocess,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'.runtime/art-direction/series01-sikh317'
SOURCE=BASE/'build-07/sequence.blend';OUT=BASE/'build-08'
def worker():
    import bpy
    from mathutils import Vector
    from sikh257_native import mesh
    from finish317_native import setup,draw
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE),load_ui=False,use_scripts=False)
    s=bpy.context.scene;r=bpy.data.objects['mounted leader']
    sleeves=sorted([o for o in r.children if o.name.startswith('297 continuous leader sleeve')],key=lambda o:o.name)
    palms=sorted([o for o in r.children if o.name.startswith('leader palm')],key=lambda o:o.name)
    assert len(sleeves)==len(palms)==2
    for p in SOURCE.parent.glob('*.json'):
        if p.name not in ('job.json','bindings.json'):shutil.copy2(p,OUT/p.name)
    samples=[[],[]];before=[]
    # Preserve evaluated proximal/elbow form. Correct the distal forearm to
    # the actual palm, with a smooth local deformation, and rebake the entire
    # timeline. This is a scoped interface repair, not a new performance rig.
    for f in range(1,697):
        s.frame_set(f);bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get()
        for i,(ob,palm) in enumerate(zip(sleeves,palms)):
            ev=ob.evaluated_get(deps);me=ev.to_mesh();pts=[v.co.copy() for v in me.vertices]
            assert len(pts)==312
            center=sum(pts[-24:],Vector())/24
            target=ev.matrix_world.inverted()@palm.matrix_world.translation;delta=target-center
            before.append(delta.length)
            for j,p in enumerate(pts):
                u=max(0,min(1,((j//24)/12-.5)/.5));p+=delta*(u*u*(3-2*u))
            samples[i].append(pts);ev.to_mesh_clear()
    new=[]
    for old,poses in zip(sleeves,samples):
        s.frame_set(1);ob=mesh('317 endpoint-bound leader sleeve',poses[0],[tuple(p.vertices) for p in old.data.polygons],old.data.materials[0]);ob.parent=r;ob.matrix_local=old.matrix_local.copy()
        for p in ob.data.polygons:p.use_smooth=True
        ob.shape_key_add(name='Basis')
        for f,pts in enumerate(poses,1):
            sk=ob.shape_key_add(name=f'pose{f:04d}')
            for p,q in zip(sk.data,pts):p.co=q
            for ff,val in ((f-1,0),(f,1),(f+1,0)):sk.value=val;sk.keyframe_insert('value',frame=ff)
        for layer in ob.data.shape_keys.animation_data.action.layers:
            for strip in layer.strips:
                for bag in strip.channelbags:
                    for fc in bag.fcurves:
                        for k in fc.keyframe_points:k.interpolation='LINEAR'
        old.hide_render=True;old.hide_viewport=True;new.append(ob)
    errors=[]
    for f in range(1,697):
        s.frame_set(f);bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get()
        for ob,palm in zip(new,palms):
            ev=ob.evaluated_get(deps);me=ev.to_mesh();center=sum((v.co for v in list(me.vertices)[-24:]),Vector())/24
            errors.append((ev.matrix_world@center-palm.matrix_world.translation).length);ev.to_mesh_clear()
    assert max(errors)<.001
    (OUT/'leader-seams.json').write_text(json.dumps({'before_max_local_m':max(before),'after_max_world_m':max(errors),'threshold_m':.001,'samples':696,'scope':'Visible cuff-to-palm interface only; not character/performance acceptance.'},indent=2))
    s.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'sequence.blend'));setup()
    for f in (283,294,306,315,324,350,375):s.frame_set(f);draw(s,OUT,f'frame-{f:04d}')
def main():
    from movie_factory import production_knowledge as pk
    paths=[SOURCE,Path(__file__),ROOT/'scripts/finish317_native.py',ROOT/'scripts/sikh257_native.py',ROOT/'results/sikh317/STRATEGY.md']
    task=json.loads((ROOT/'results/sikh317/build-7/task.json').read_text());task['id']='sikh317-leader-interface-8';task['inputs']={str(p.relative_to(ROOT)):pk.file_hash(p) for p in paths}
    packet=pk.task_packet(ROOT,task);assert packet['dispatch_ready'],packet['blockers']
    dest=ROOT/'results/sikh317/build-8';dest.mkdir(exist_ok=True)
    for n,d in (('task',task),('packet',packet)):(dest/(n+'.json')).write_text(json.dumps(d,indent=2))
    (dest/'packet.md').write_text(pk.packet_markdown(packet))
    if sys.argv[1:]==['--prepare']:print(dest/'packet.md');return
    assert not sys.argv[1:];OUT.mkdir(exist_ok=False)
    for p in paths:
        if p.suffix in ('.py','.md'):
            d=OUT/'source-snapshot'/p.relative_to(ROOT);d.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,d)
    env={k:os.environ[k] for k in ('PATH','HOME','TMPDIR','LANG','LC_ALL') if k in os.environ}
    for k,d in (('BLENDER_USER_CONFIG','config'),('BLENDER_USER_SCRIPTS','scripts'),('BLENDER_USER_DATAFILES','data')):env[k]=str(OUT/'sandbox'/d)
    tick=time.monotonic()
    with (OUT/'worker.log').open('x') as log:r=subprocess.run(['/Applications/Blender.app/Contents/MacOS/Blender','-b','--factory-startup','--disable-autoexec','--offline-mode','--python-exit-code','7','--python',str(Path(__file__).resolve()),'--','worker'],env=env,stdout=log,stderr=subprocess.STDOUT)
    changed=[p for p,h in task['inputs'].items() if pk.file_hash(ROOT/p)!=h]
    (dest/'receipt.json').write_text(json.dumps({'returncode':r.returncode,'seconds':time.monotonic()-tick,'changed_sources':changed},indent=2))
    if r.returncode or changed:raise RuntimeError(OUT/'worker.log')
    print(OUT)
if __name__=='__main__':
    if sys.argv[-1]=='worker':sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')];worker()
    else:main()
