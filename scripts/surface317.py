"""Fixed candidate05: airborne hoof ownership and admitted coat-texture reuse."""
import sys,json,os,subprocess,time,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'.runtime/art-direction/series01-sikh317';SOURCE=BASE/'build-04/sequence.blend';OUT=BASE/'build-05'
TEXTURE=ROOT/'.runtime/art-direction/series01-entrance-art188/horse-coat-v01.png'
def worker():
    import bpy
    from movie_factory import sikh317_motion as m
    from finish317_native import setup,draw
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE),load_ui=False,use_scripts=False)
    for p in SOURCE.parent.glob('*.json'):
        if p.name not in ('job.json','bindings.json'):shutil.copy2(p,OUT/p.name)
    s=bpy.context.scene;rig=bpy.data.objects['horse.rig'];controls=[]
    for side in ('L','R'):
        pb=rig.pose.bones['MCH-f_hoof.'+side];c=next(c for c in pb.constraints if c.type=='COPY_TRANSFORMS' and c.subtarget=='MCH-f_hoof_ik_socket.'+side)
        c.driver_remove('influence');controls.append(c)
    # While airborne, inherit the actual FK toe chain rather than a planted
    # IK socket's orientation. Original socket ownership returns before impact.
    for f in range(1,697):
        t=(f-1)/24*m.RATE;a=m.ease(m.rear(t)/.20)
        for c in controls:c.influence=1-a;c.keyframe_insert('influence',frame=f)
    body=bpy.data.objects['horse'];mat=body.data.materials[0];fur=bpy.data.objects['317 rig-bound short horse nap']
    furmat=mat.copy();furmat.name='317 independent short nap material';fur.data.materials[0]=furmat
    if not body.data.uv_layers:raise ValueError('No admitted original UV surface')
    n=mat.node_tree.nodes;l=mat.node_tree.links;b=n['Principled BSDF'];base=b.inputs['Base Color'].links[0].from_socket
    # UV attachment remains stable through skeletal deformation. Keep the
    # original grey colour; reuse authored hair structure, not the bay hue.
    coords=n.new('ShaderNodeTexCoord');scale=n.new('ShaderNodeVectorMath');scale.operation='SCALE';scale.inputs[3].default_value=4;l.new(coords.outputs['UV'],scale.inputs[0])
    tex=n.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(TEXTURE),check_existing=True);tex.image.pack();tex.extension='REPEAT';l.new(scale.outputs[0],tex.inputs[0])
    bw=n.new('ShaderNodeRGBToBW');l.new(tex.outputs['Color'],bw.inputs[0]);remap=n.new('ShaderNodeMapRange');remap.inputs['From Min'].default_value=.025;remap.inputs['From Max'].default_value=.35;remap.inputs['To Min'].default_value=.45;remap.inputs['To Max'].default_value=1.05;l.new(bw.outputs[0],remap.inputs[0])
    mix=n.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=.70;l.new(base,mix.inputs[1]);l.new(remap.outputs[0],mix.inputs[2]);l.new(mix.outputs[0],b.inputs['Base Color'])
    bump=n.new('ShaderNodeBump');bump.inputs['Distance'].default_value=.0012;bump.inputs['Strength'].default_value=.28;l.new(bw.outputs[0],bump.inputs['Height'])
    if b.inputs['Normal'].is_linked:l.new(b.inputs['Normal'].links[0].from_socket,bump.inputs['Normal'])
    l.new(bump.outputs[0],b.inputs['Normal'])
    # Replace shader object-coordinate grain with original UVs on body only.
    for node in n:
        if node.type=='TEX_COORD':
            for link in list(node.outputs['Object'].links):l.new(node.outputs['UV'],link.to_socket)
    for action in bpy.data.actions:
        for layer in action.layers:
            for strip in layer.strips:
                for bag in strip.channelbags:
                    for fc in bag.fcurves:
                        if 'MCH-f_hoof' in fc.data_path:
                            for p in fc.keyframe_points:p.interpolation='LINEAR'
    (OUT/'hoof-ownership.json').write_text(json.dumps({'cause':'MCH-f_hoof copied IK socket through the FK rear','repair':'airborne FK inheritance; original socket restored at zero rise','source_probe':str((BASE/'hoofprobe-05/hoof-bones.json').relative_to(ROOT)),'new_pose_or_ground_clock':False},indent=2))
    (OUT/'coat-reuse.json').write_text(json.dumps({'texture':str(TEXTURE.relative_to(ROOT)),'source_use':'existing Pashtun horse authored coat detail','adaptation':'luminance only, original grey retained, tiled original UV, packed image','qualification':'candidate awaiting shot review; not universal material admission'},indent=2))
    s.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'sequence.blend'));setup()
    for f in (80,294,306,315,324,333,342,350):s.frame_set(f);draw(s,OUT,f'frame-{f:04d}')
def main():
    from movie_factory import production_knowledge as pk
    paths=[SOURCE,Path(__file__),ROOT/'scripts/finish317_native.py',ROOT/'src/movie_factory/sikh317_motion.py',TEXTURE,TEXTURE.with_suffix('.prompt.txt'),ROOT/'results/sikh317/STRATEGY.md']
    task=json.loads((ROOT/'results/sikh317/build-4/task.json').read_text());task['id']='sikh317-build-5';task['inputs']={str(p.relative_to(ROOT)):pk.file_hash(p) for p in paths};packet=pk.task_packet(ROOT,task)
    if not packet['dispatch_ready']:raise ValueError(packet['blockers'])
    dest=ROOT/'results/sikh317/build-5';dest.mkdir(parents=True,exist_ok=True)
    for name,data in [('task',task),('packet',packet)]:(dest/(name+'.json')).write_text(json.dumps(data,indent=2))
    (dest/'packet.md').write_text(pk.packet_markdown(packet))
    if '--prepare' in sys.argv:print(dest/'packet.md');return
    OUT.mkdir(exist_ok=False);(OUT/'bindings.json').write_text(json.dumps(task['inputs'],indent=2))
    for p in paths:
        if p.suffix in ('.py','.md','.txt'):
            d=OUT/'source-snapshot'/p.relative_to(ROOT);d.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,d)
    env={k:os.environ[k] for k in ('PATH','HOME','TMPDIR','LANG','LC_ALL') if k in os.environ}
    for k,d in (('BLENDER_USER_CONFIG','config'),('BLENDER_USER_SCRIPTS','scripts'),('BLENDER_USER_DATAFILES','data')):env[k]=str(OUT/'sandbox'/d)
    start=time.monotonic()
    with (OUT/'worker.log').open('w') as log:r=subprocess.run(['/Applications/Blender.app/Contents/MacOS/Blender','-b','--factory-startup','--disable-autoexec','--offline-mode','--python-exit-code','7','--python',str(Path(__file__).resolve()),'--','worker'],env=env,stdout=log,stderr=subprocess.STDOUT)
    changed=[p for p,h in task['inputs'].items() if pk.file_hash(ROOT/p)!=h];(dest/'receipt.json').write_text(json.dumps({'returncode':r.returncode,'seconds':time.monotonic()-start,'changed_inputs':changed},indent=2))
    if r.returncode or changed:raise RuntimeError(OUT/'worker.log')
    print(OUT)
if __name__=='__main__':
    if sys.argv[-1]=='worker':sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')];worker()
    else:main()
