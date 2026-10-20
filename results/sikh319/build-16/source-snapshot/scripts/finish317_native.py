"""Reviewed local joint-orientation controls and reversible material finish."""
import sys,json,math,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
import bpy
from mathutils import Vector,Quaternion
from finish317 import validate,BASE
from movie_factory import sikh317_motion as m
def setup():
    s=bpy.context.scene;s.render.resolution_x=480;s.render.resolution_y=854;s.render.resolution_percentage=100;s.eevee.taa_render_samples=24;s.eevee.shadow_ray_count=1
    for light in bpy.data.lights:
        if hasattr(light,'use_shadow_jitter'):light.use_shadow_jitter=light.type=='SUN'
        if hasattr(light,'shadow_maximum_resolution'):light.shadow_maximum_resolution=.01
    return s
def draw(s,out,name):
    s.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True)
def study(out):
    s=setup();s.frame_set(324);rig=bpy.data.objects['horse.rig'];rows=[]
    original={side:rig.pose.bones['forefoot_fk.'+side].rotation_quaternion.copy() for side in ('L','R')}
    for offset in (0,.7,1.,1.4):
        s.frame_set(323);s.frame_set(324)
        for side in ('L','R'):
            pb=rig.pose.bones['forefoot_fk.'+side];axis=pb.bone.matrix_local.to_3x3().inverted()@Vector((1,0,0))
            pb.rotation_quaternion=Quaternion(axis,offset)@original[side];pb.keyframe_insert('rotation_quaternion',frame=324)
        bpy.context.view_layer.update()
        rows.append({'offset':offset,'bones':{n:{'head':list(rig.matrix_world@rig.pose.bones[n].head),'tail':list(rig.matrix_world@rig.pose.bones[n].tail)} for n in ('DEF-forearm.L','DEF-forefoot.L','DEF-f_toe.L') if n in rig.pose.bones}})
        draw(s,out,'wrist-'+str(offset))
    (out/'joint-coordinates.json').write_text(json.dumps(rows,indent=2))
def finish(out):
    from mathutils.kdtree import KDTree
    for p in (BASE/'build-03').glob('*.json'):
        if p.name not in ('job.json','bindings.json'):shutil.copy2(p,out/p.name)
    s=bpy.context.scene;s.frame_set(1);rig=bpy.data.objects['horse.rig'];rider=bpy.data.objects['mounted leader']
    head=next(o for o in rider.children if o.name.startswith('secondary adult head'))
    crown=next(o for o in rider.children if o.name.startswith('secondary facial and crown'))
    rest={o.name:o.rotation_euler.copy() for o in (head,crown)}
    bit=bpy.data.objects['292 bit support'];palm=bpy.data.objects['leader palm'];reins=sorted([o for o in bpy.data.objects if o.name.startswith('leader supported rein292')],key=lambda o:o.name)
    for f in range(1,697):
        s.frame_set(f);t=(f-1)/24*m.RATE
        for side in ('L','R'):
            lag=.055 if side=='R' else 0;fold=m.bump(t,14.98+lag,15.60+lag,16.27+lag,17.07+lag)
            for prefix,amount in [('forefoot_fk',.70),('f_toe_fk',.70)]:
                pb=rig.pose.bones[prefix+'.'+side];axis=pb.bone.matrix_local.to_3x3().inverted()@Vector((1,0,0))
                pb.rotation_quaternion=Quaternion(axis,amount*fold)@pb.rotation_quaternion;pb.keyframe_insert('rotation_quaternion',frame=f)
        pb=rig.pose.bones['head'];axis=pb.bone.matrix_local.to_3x3().inverted()@Vector((1,0,0))
        pb.rotation_quaternion=Quaternion(axis,.30*m.rear(t))@pb.rotation_quaternion;pb.keyframe_insert('rotation_quaternion',frame=f)
        for o in (head,crown):
            o.rotation_euler=rest[o.name];o.rotation_euler.x+=.055*m.gather(t)+.07*m.rear(t)
            o.rotation_euler.z-=.10*m.bump(t,12.9,13.7,17.9,19.3);o.keyframe_insert('rotation_euler',frame=f)
        bpy.context.view_layer.update()
        for sign,ob in zip((-1,1),reins):
            start=bit.matrix_world.translation+rig.matrix_world.to_3x3()@Vector((sign*.07,0,0));end=palm.matrix_world.translation
            for j,p in enumerate(ob.data.splines[0].points):
                u=j/(len(ob.data.splines[0].points)-1);q=start.lerp(end,u)+Vector((0,0,-.08*math.sin(math.pi*u)));p.co=(*q,1);p.keyframe_insert('co',frame=f)
    body=bpy.data.objects['horse'];fur=bpy.data.objects['317 rig-bound short horse nap'];mat=body.data.materials[0]
    # Fur must carry the same pigmentation attribute as the underlying skin.
    tree=KDTree(len(body.data.vertices))
    for v in body.data.vertices:tree.insert(v.co,v.index)
    tree.balance();attr=fur.data.color_attributes.new(name='315 coat pigmentation',type='FLOAT_COLOR',domain='POINT')
    original=body.data.color_attributes['315 coat pigmentation']
    for v,c in zip(fur.data.vertices,attr.data):c.color=original.data[tree.find(v.co)[1]].color
    n=mat.node_tree.nodes;l=mat.node_tree.links;b=n['Principled BSDF'];base=b.inputs['Base Color'].links[0].from_socket
    coord=n.new('ShaderNodeTexCoord');stretch=n.new('ShaderNodeVectorMath');stretch.operation='MULTIPLY';stretch.inputs[1].default_value=(5,1,10);l.new(coord.outputs['Object'],stretch.inputs[0])
    grain=n.new('ShaderNodeTexNoise');grain.inputs['Scale'].default_value=42;grain.inputs['Detail'].default_value=2;l.new(stretch.outputs[0],grain.inputs[0])
    ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].position=.24;ramp.color_ramp.elements[0].color=(.45,.43,.40,1);ramp.color_ramp.elements[1].position=.76;ramp.color_ramp.elements[1].color=(1.04,1.02,.97,1);l.new(grain.outputs['Fac'],ramp.inputs[0])
    mix=n.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=.75;l.new(base,mix.inputs[1]);l.new(ramp.outputs[0],mix.inputs[2]);l.new(mix.outputs[0],b.inputs['Base Color'])
    b.inputs['Roughness'].default_value=.64;b.inputs['Specular IOR Level'].default_value=.23;b.inputs['Sheen Weight'].default_value=.28
    # Soft asymmetric natural grey patches, not coarse rock-like bump relief.
    for v,c in zip(body.data.vertices,original.data):
        x,y,z=v.co;variation=.92+.08*math.sin(y*7+math.sin(z*8)+x*3)*math.sin(z*9+y*2)
        c.color=(*[v*variation for v in c.color[:3]],1)
    for action in bpy.data.actions:
        for layer in action.layers:
            for strip in layer.strips:
                for bag in strip.channelbags:
                    for fc in bag.fcurves:
                        for p in fc.keyframe_points:
                            if 'hide_' not in fc.data_path:p.interpolation='LINEAR'
    (out/'finish.json').write_text(json.dumps({'wrist_control':'study06 +0.7, full envelope','toe_offset':.70,'poll_flexion':.30,'leader':'bounded acknowledgement and downward gaze; crown follows head','fur_attribute_vertices':len(attr.data),'reins':'recomputed after poll correction','status':'UNREVIEWED'},indent=2))
    s.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(out/'sequence.blend'));setup()
    for f in (41,80,283,294,306,315,324,333,342,350,402,430,450,480,600):s.frame_set(f);draw(s,out,f'frame-{f:04d}')
def verify(out):
    raise RuntimeError('Verification handler not yet admitted')
def hoofprobe(out):
    s=bpy.context.scene;s.frame_set(324);rig=bpy.data.objects['horse.rig'];rows=[]
    for pb in rig.pose.bones:
        if 'hoof' in pb.name:
            rows.append({'name':pb.name,'parent':pb.parent.name if pb.parent else None,'inherit_rotation':pb.bone.use_inherit_rotation,'mode':pb.rotation_mode,'constraints':[{'type':c.type,'subtarget':getattr(c,'subtarget',None),'influence':c.influence} for c in pb.constraints],'head':list(rig.matrix_world@pb.head),'tail':list(rig.matrix_world@pb.tail)})
    (out/'hoof-bones.json').write_text(json.dumps(rows,indent=2));print(json.dumps(rows),flush=True)
def main():
    p=Path(sys.argv[sys.argv.index('--')+1]);op=validate(json.loads(p.read_text()));out=BASE/({'jointstudy':'jointstudy-04','jointstudy2':'jointstudy-05','jointstudy3':'jointstudy-06','hoofprobe':'hoofprobe-05','finish':'build-04','verify':'verify-04'}[op])
    if p.resolve()!=out/'job.json':raise ValueError('Unadmitted job path')
    source=BASE/('build-04' if op in ('verify','hoofprobe') else 'build-03')/'sequence.blend'
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False)
    {'jointstudy':study,'jointstudy2':study,'jointstudy3':study,'hoofprobe':hoofprobe,'finish':finish,'verify':verify}[op](out)
if __name__=='__main__':main()
