"""Fixed local crowd seam diagnostic and derivative; no external inputs."""
import os,sys,json,time,subprocess,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'.runtime/art-direction/series01-sikh317'
SOURCE=BASE/'build-05/sequence.blend'
def worker(op,out):
    import bpy
    from mathutils import Vector
    from sikh297_layers import endpoints
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE),load_ui=False,use_scripts=False)
    s=bpy.context.scene;rows=[]
    roots=sorted([o for o in bpy.data.objects if o.name.startswith('FOOT WARRIOR ')],key=lambda o:int(o.name.split()[-1]))
    if op=='repair':
        from sikh297_layers import sleeve_points,sleeve_faces
        from sikh257_native import mesh
        from finish317_native import setup,draw
        for p in SOURCE.parent.glob('*.json'):
            if p.name not in ('bindings.json','job.json'):shutil.copy2(p,out/p.name)
        from sikh317_scene import crowd
        crowd(out,bake=False)
        pairs=[]
        # Sources excluded from viewport evaluation were frozen during the old
        # bake. Keep them evaluated but render-hidden; bake the visible mesh.
        times=[1]+list(range(340,441))+[696]
        for r in roots:
            ups=sorted([o for o in r.children if o.name.startswith('PROXY thigh')],key=lambda o:o.name)
            lows=sorted([o for o in r.children if o.name.startswith('PROXY calf')],key=lambda o:o.name)
            feet=sorted([o for o in r.children if o.name.startswith('PROXY boot')],key=lambda o:o.name)
            old=sorted([o for o in r.children if o.name.startswith('317 planted crowd trousers')],key=lambda o:o.name)
            mat=old[0].data.materials[0]
            for o in ups+lows:o.hide_viewport=False;o.hide_render=True;o.display_type='WIRE'
            for o in old:o.hide_viewport=True;o.hide_render=True
            for up,lo,foot in zip(ups,lows,feet):
                samples=[]
                for f in times:
                    s.frame_set(f);bpy.context.view_layer.update()
                    a,b=endpoints(up,.074);b2,c=endpoints(lo,.057)
                    samples.append(sleeve_points(a,(b+b2)/2,c,(.087,.072,.052)))
                ob=mesh('317 evaluated crowd trousers',samples[0],sleeve_faces(),mat);ob.parent=r;ob.shape_key_add(name='Basis')
                for i,(f,points) in enumerate(zip(times,samples)):
                    sk=ob.shape_key_add(name=f'pose{f:04d}')
                    for p,q in zip(sk.data,points):p.co=q
                    for ff,val in ((times[i-1] if i else 0,0),(f,1),(times[i+1] if i+1<len(times) else 697,0)):
                        sk.value=val;sk.keyframe_insert('value',frame=ff)
                for layer in ob.data.shape_keys.animation_data.action.layers:
                    for strip in layer.strips:
                        for bag in strip.channelbags:
                            for fc in bag.fcurves:
                                for k in fc.keyframe_points:k.interpolation='LINEAR'
                pairs.append((r,foot,ob))
        maximum=0.;perframe=[]
        for f in range(1,697):
            s.frame_set(f);bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get();errs=[]
            for r,foot,ob in pairs:
                ev=ob.evaluated_get(deps);me=ev.to_mesh();center=sum((v.co for v in list(me.vertices)[-24:]),Vector())/24
                errs.append((ev.matrix_world@center-foot.matrix_world.translation).length);ev.to_mesh_clear()
            maximum=max(maximum,max(errs));perframe.append({'frame':f,'maximum_ankle_ring_to_boot_m':max(errs)})
        (out/'crowd-seams.json').write_text(json.dumps({'maximum_m':maximum,'threshold_m':.001,'frames':perframe,
            'cause':'Hidden source limbs were not evaluated during prior garment bake; boot-only support checks missed the rendered cloth interface.',
            'correction':'Render-hidden but evaluated limb sources; rebake actual changing window at each frame, held rest endpoints through696.'},indent=2))
        if maximum>.001:raise ValueError('Visible garment/boot seam still separates')
        s.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(out/'sequence.blend'));setup()
        for f in (375,380,390,402,415,430,450):s.frame_set(f);draw(s,out,f'frame-{f:04d}')
        return
    for enabled in (False,True):
        if enabled:
            for r in roots:
                for o in r.children:
                    if o.name.startswith(('PROXY thigh','PROXY calf')):o.hide_viewport=False
        for f in (1,375,390,405,430,450):
            s.frame_set(f);bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get()
            for r in roots:
                feet=sorted([o for o in r.children if o.name.startswith('PROXY boot')],key=lambda o:o.name)
                lowers=sorted([o for o in r.children if o.name.startswith('PROXY calf')],key=lambda o:o.name)
                pants=sorted([o for o in r.children if o.name.startswith('317 planted crowd trousers')],key=lambda o:o.name)
                for foot,lo,pant in zip(feet,lowers,pants):
                    ev=pant.evaluated_get(deps);mesh=ev.to_mesh()
                    center=sum((v.co for v in list(mesh.vertices)[-24:]),Vector())/24
                    point=ev.matrix_world@center;target=foot.matrix_world.translation
                    rows.append({'enabled_sources':enabled,'actor':r.name,'frame':f,'foot':foot.name,
                        'visible_seam_m':(point-target).length,
                        'control_seam_m':(r.matrix_world@endpoints(lo,.057)[1]-target).length,
                        'active_shapes':[(k.name,k.value) for k in pant.data.shape_keys.key_blocks if abs(k.value)>.001]})
                    ev.to_mesh_clear()
    (out/'seams.json').write_text(json.dumps(rows,indent=2));print(json.dumps({'max_visible_seam':max(r['visible_seam_m'] for r in rows),'max_control_seam':max(r['control_seam_m'] for r in rows)}),flush=True)
def main():
    from movie_factory import production_knowledge as pk
    op=sys.argv[1];assert op in ('inspect','repair')
    out=BASE/('crowd-probe-07' if op=='inspect' else 'build-07')
    paths=[SOURCE,Path(__file__),ROOT/'scripts/sikh297_layers.py',ROOT/'scripts/finish317_native.py',ROOT/'scripts/sikh317_scene.py',ROOT/'src/movie_factory/sikh317_motion.py',ROOT/'results/sikh317/STRATEGY.md']
    task=json.loads((ROOT/'results/sikh317/build-5/task.json').read_text());task['id']='sikh317-crowd-'+op+'-7';task['inputs']={str(p.relative_to(ROOT)):pk.file_hash(p) for p in paths};packet=pk.task_packet(ROOT,task)
    if not packet['dispatch_ready']:raise ValueError(packet['blockers'])
    dest=ROOT/'results/sikh317/build-7';dest.mkdir(exist_ok=True)
    for n,d in (('task',task),('packet',packet)):(dest/(n+'.json')).write_text(json.dumps(d,indent=2))
    (dest/'packet.md').write_text(pk.packet_markdown(packet))
    if '--prepare' in sys.argv:print(dest/'packet.md');return
    out.mkdir(exist_ok=False)
    for p in paths:
        if p.suffix in ('.py','.md'):
            d=out/'source-snapshot'/p.relative_to(ROOT);d.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,d)
    env={k:os.environ[k] for k in ('PATH','HOME','TMPDIR','LANG','LC_ALL') if k in os.environ}
    for k,d in (('BLENDER_USER_CONFIG','config'),('BLENDER_USER_SCRIPTS','scripts'),('BLENDER_USER_DATAFILES','data')):env[k]=str(out/'sandbox'/d)
    tick=time.monotonic()
    with (out/'worker.log').open('x') as log:r=subprocess.run(['/Applications/Blender.app/Contents/MacOS/Blender','-b','--factory-startup','--disable-autoexec','--offline-mode','--python-exit-code','7','--python',str(Path(__file__).resolve()),'--','worker',op,str(out)],env=env,stdout=log,stderr=subprocess.STDOUT)
    changed=[p for p,h in task['inputs'].items() if pk.file_hash(ROOT/p)!=h]
    (dest/'receipt.json').write_text(json.dumps({'returncode':r.returncode,'seconds':time.monotonic()-tick,'changed_sources':changed},indent=2))
    if r.returncode or changed:raise RuntimeError(out/'worker.log')
    print(out)
if __name__=='__main__':
    if 'worker' in sys.argv:
        sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')];worker(sys.argv[-2],Path(sys.argv[-1]))
    else:main()
