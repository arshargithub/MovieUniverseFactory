"""Trusted fixed318 native handler. Disable embedded scripts on all opens."""
import sys,json,math,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
import bpy
from mathutils import Vector
from sikh318 import BASE,SOURCE,validate,source_for
from movie_factory import sikh318_motion as m

def inspect(out):
    body=bpy.data.objects['horse']
    report={'vertices':len(body.data.vertices),'smooth_polygons':sum(p.use_smooth for p in body.data.polygons),'polygons':len(body.data.polygons),
        'modifiers':[{'name':x.name,'type':x.type,'render':x.show_render,'viewport':x.show_viewport,'levels':getattr(x,'levels',None),'render_levels':getattr(x,'render_levels',None)} for x in body.modifiers],
        'materials':[]}
    for mat in body.data.materials:
        report['materials'].append({'name':mat.name,'nodes':[{'name':n.name,'type':n.type,'values':{i.name:list(i.default_value) if hasattr(i.default_value,'__len__') else i.default_value for i in n.inputs if hasattr(i,'default_value') and isinstance(i.default_value,(float,int))}} for n in mat.node_tree.nodes if n.type in ('BSDF_PRINCIPLED','BUMP','TEX_NOISE')]})
    bpy.context.scene.frame_set(283);bpy.context.view_layer.update();rig=bpy.data.objects['horse.rig']
    report['head_bones']={b.name:{'head':list(rig.matrix_world@b.head),'tail':list(rig.matrix_world@b.tail)} for b in rig.pose.bones if b.name.startswith('DEF') and any(k in b.name for k in ('head','neck','ear'))}
    report['groom']=[{'name':o.name,'bone':o.parent_bone,'points':[list(o.matrix_world@p.co.xyz) for p in o.data.splines[0].points]} for o in bpy.data.objects if o.type=='CURVE' and o.name.startswith(('horse forelock292','rooted mane locks292'))]
    (out/'inspection.json').write_text(json.dumps(report,indent=2))

def sleeves(out):
    from sikh257_native import mesh
    s=bpy.context.scene;r=bpy.data.objects['mounted leader']
    old=sorted([o for o in r.children if o.name.startswith('297 continuous leader sleeve')],key=lambda o:o.name)
    palms=sorted([o for o in r.children if o.name.startswith('leader palm')],key=lambda o:o.name)
    for ob in old:ob.hide_viewport=False
    samples=[[],[]]
    for f in range(1,697):
        s.frame_set(f);bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get()
        for i,(ob,palm) in enumerate(zip(old,palms)):
            ev=ob.evaluated_get(deps);me=ev.to_mesh();pts=[v.co.copy() for v in me.vertices]
            assert len(pts)==312
            delta=ev.matrix_world.inverted()@palm.matrix_world.translation-sum(pts[-24:],Vector())/24
            for j,p in enumerate(pts):p+=delta*m.ease(((j//24)/12-.5)/.5)
            samples[i].append(pts);ev.to_mesh_clear()
    for ob in r.children:
        if ob.name.startswith('317 endpoint-bound leader sleeve'):ob.hide_render=True;ob.hide_viewport=True
    for original,poses in zip(old,samples):
        s.frame_set(1);ob=mesh('318 endpoint-bound leader sleeve',poses[0],[tuple(p.vertices) for p in original.data.polygons],original.data.materials[0]);ob.parent=r;ob.matrix_local=original.matrix_local.copy()
        for p in ob.data.polygons:p.use_smooth=True
        ob.shape_key_add(name='Basis')
        for f,pts in enumerate(poses,1):
            sk=ob.shape_key_add(name=f'pose{f:04d}')
            for p,q in zip(sk.data,pts):p.co=q
            for ff,val in ((f-1,0),(f,1),(f+1,0)):sk.value=val;sk.keyframe_insert('value',frame=ff)
        original.hide_render=True;original.hide_viewport=True

def build(out):
    from sikh257_layout import key
    import sikh315_scene as prior
    from sikh305_impacts import build_impacts
    from sikh317_scene import ditch
    for p in SOURCE.parent.glob('*.json'):
        if p.name not in ('job.json','bindings.json'):shutil.copy2(p,out/p.name)
    s=bpy.context.scene;rig=bpy.data.objects['horse.rig']
    if not bpy.data.materials.get('297 silver dapple coat'):
        mat=bpy.data.objects['horse'].data.materials[0].copy();mat.name='297 silver dapple coat'
    previous=prior.m;prior.m=m
    try:prior.horse(out)
    finally:prior.m=previous
    # Downstream hoof constraints must release during flight on the NEW clock.
    for f in range(1,697):
        s.frame_set(f);t=(f-1)/24*m.RATE
        for side in ('L','R'):
            for c in rig.pose.bones['MCH-f_hoof.'+side].constraints:
                if c.type=='COPY_TRANSFORMS':c.influence=1-m.ease(m.rear(t)/.20);c.keyframe_insert('influence',frame=f)
    sleeves(out)
    build_impacts(out,event_definitions=[('spear',14.28,None,.20),('grip-left',14.79,'DEF-f_toe.L',.16),('grip-right',15.08,'DEF-f_toe.R',.16),('hind-drive-left',15.48,'DEF-r_toe.L',.35),('hind-drive-right',15.52,'DEF-r_toe.R',.35),('landing-left',17.10,'DEF-f_toe.L',1.),('landing-right',17.14,'DEF-f_toe.R',.85)],follow_terrain=True)
    coat(out)
    fix_groom(out)
    # More of the established clustered bank growth, not new support geometry.
    ditch(out,seed=3185,count=5000)
    for action in bpy.data.actions:
        for layer in action.layers:
            for strip in layer.strips:
                for bag in strip.channelbags:
                    for fc in bag.fcurves:
                        for p in fc.keyframe_points:
                            if 'hide_' not in fc.data_path:p.interpolation='LINEAR'
    s.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(out/'sequence.blend'))

def fix_groom(out):
    # Inspection located the throat patch in the first neck mane group, not
    # the head forelock. Raycast from outside the actual dorsal neck surface.
    from mathutils.bvhtree import BVHTree
    from sikh257_layout import tube
    import numpy as np
    s=bpy.context.scene;s.frame_set(1);bpy.context.view_layer.update()
    rig=bpy.data.objects['horse.rig'];body=bpy.data.objects['horse']
    deps=bpy.context.evaluated_depsgraph_get();ev=body.evaluated_get(deps);me=ev.to_mesh()
    tree=BVHTree.FromPolygons([ev.matrix_world@v.co for v in me.vertices],[list(p.vertices) for p in me.polygons]);ev.to_mesh_clear()
    base=rig.matrix_world@rig.pose.bones['DEF-neck.001'].head;head=rig.matrix_world@rig.pose.bones['DEF-head'].head
    forward=head-base;forward.z=0;forward.normalize();back=-forward;side=forward.cross(Vector((0,0,1)))
    mat=bpy.data.materials['292 coarse horse mane'].copy();mat.name='318 brown black mane'
    bs=mat.node_tree.nodes['Principled BSDF']
    for link in list(bs.inputs['Base Color'].links):mat.node_tree.links.remove(link)
    bs.inputs['Base Color'].default_value=(.018,.010,.007,1);bs.inputs['Roughness'].default_value=.63
    roots=[];new=[];rng=np.random.default_rng(318)
    for ob in list(bpy.data.objects):
        if ob.type!='CURVE' or not ob.name.startswith(('rooted mane locks292','horse forelock292','horse tail fullness292','315 rooted companion lock')):continue
        ob.data.materials[0]=mat
        if not ob.parent_bone.startswith('DEF-neck'):continue
        pb=rig.pose.bones[ob.parent_bone];p=ob.matrix_world@ob.data.splines[0].points[0].co.xyz
        center=rig.matrix_world@pb.head
        if (p-center).dot(forward)<.025:continue
        # Match original root height with a bounded ray through the neck.
        center.z=p.z;dorsal=(back*.6+Vector((0,0,.8))).normalized()
        hit,normal,_,distance=tree.ray_cast(center+dorsal*1.5,-dorsal,2.2)
        if hit is None:raise ValueError('Missing dorsal mane support')
        if (hit-center).dot(forward)>.005:raise ValueError('Mane ray reached ventral surface')
        q=hit+normal*.0015;length=float(rng.uniform(.16,.23));drift=float(rng.uniform(.06,.11))
        pts=[q,q+side*drift*.4+back*.01+Vector((0,0,-length*.15)),q+side*drift+back*.025+Vector((0,0,-length*.6)),q+side*drift*.9+back*.035+Vector((0,0,-length))]
        fresh=tube('318 dorsal mane correction',pts,float(rng.uniform(.002,.0035)),mat)
        bpy.context.view_layer.update();world=fresh.matrix_world.copy();fresh.parent=rig;fresh.parent_type='BONE';fresh.parent_bone=ob.parent_bone;bpy.context.view_layer.update();fresh.matrix_world=world
        for i,pnt in enumerate(fresh.data.splines[0].points):pnt.radius=1-.75*i/3
        new.append((fresh,[p.co.copy() for p in fresh.data.splines[0].points]))
        roots.append({'old':ob.name,'new':fresh.name,'bone':ob.parent_bone,'surface_root_world':list(q),'source_root_world':list(p)})
        ob.hide_render=True;ob.hide_viewport=True
    assert roots,'Expected documented misplaced throat mane roots'
    for f in range(1,697):
        t=(f-1)/24*m.RATE;lag=m.rear(t-.075)-m.rear(t)
        for ob,pts in new:
            for i,(p,q) in enumerate(zip(ob.data.splines[0].points,pts)):
                u=i/3;v=q.copy();v.x+=u*u*.045*lag;v.z-=u*u*.03*lag;p.co=v;p.keyframe_insert('co',frame=f)
    (out/'groom318.json').write_text(json.dumps({'corrected_roots':roots,'forelock_relocated':False,'diagnosis':'first neck mane roots were on ventral surface; actual poll forelock was correctly attached','roots_fixed_local':True},indent=2))

def coat(out):
    # Dedicated skin shader avoids multiplying inherited stone-like noise stacks.
    body=bpy.data.objects['horse'];mat=bpy.data.materials.new('318 dark seal brown coat');mat.use_nodes=True
    n=mat.node_tree.nodes;l=mat.node_tree.links;b=n.get('Principled BSDF')
    b.inputs['Roughness'].default_value=.49;b.inputs['Specular IOR Level'].default_value=.28;b.inputs['Sheen Weight'].default_value=.16
    uv=n.new('ShaderNodeTexCoord');tex=n.new('ShaderNodeTexImage')
    tex.image=bpy.data.images.load(str(ROOT/'.runtime/art-direction/series01-entrance-art188/horse-coat-v01.png'),check_existing=True);tex.image.pack()
    l.new(uv.outputs['UV'],tex.inputs['Vector']);grey=n.new('ShaderNodeRGBToBW');l.new(tex.outputs['Color'],grey.inputs[0])
    ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].position=.12;ramp.color_ramp.elements[0].color=(.018,.009,.006,1);ramp.color_ramp.elements[1].position=.8;ramp.color_ramp.elements[1].color=(.095,.045,.022,1)
    l.new(grey.outputs[0],ramp.inputs[0]);l.new(ramp.outputs[0],b.inputs['Base Color'])
    scale=n.new('ShaderNodeVectorMath');scale.operation='MULTIPLY';scale.inputs[1].default_value=(5,1,8);l.new(uv.outputs['Object'],scale.inputs[0])
    noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=90;noise.inputs['Detail'].default_value=2;l.new(scale.outputs[0],noise.inputs[0])
    bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.13;bump.inputs['Distance'].default_value=.00018;l.new(noise.outputs['Fac'],bump.inputs['Height']);l.new(bump.outputs[0],b.inputs['Normal'])
    body.data.materials[0]=mat
    for p in body.data.polygons:p.use_smooth=True
    # Inspection found smooth normals but no subdivision. One render level
    # rounds the coarse cheek/muzzle silhouette without changing the rig.
    sub=body.modifiers.new('318 silhouette subdivision','SUBSURF');sub.levels=1;sub.render_levels=1
    fur=bpy.data.objects['317 rig-bound short horse nap'];furmat=mat.copy();furmat.name='318 dark short nap';fb=furmat.node_tree.nodes.get('Principled BSDF')
    for link in list(fb.inputs['Base Color'].links):furmat.node_tree.links.remove(link)
    fb.inputs['Base Color'].default_value=(.045,.021,.011,1);fur.data.materials[0]=furmat
    (out/'coat318.json').write_text(json.dumps({'colour':'dark seal brown','source':'existing authored188 UV coat','geometry':'original body; smooth shading; original deformation','scale_bump_distance':.00018,'scope':'look candidate, not accepted'},indent=2))

def main():
    path=Path(sys.argv[sys.argv.index('--')+1]);j=validate(json.loads(path.read_text()));op=j['operation'];v=j['version'];out=BASE/f'{op}-{v:02d}'
    if path.resolve()!=out/'chunks'/str(j['start'])/'job.json':raise ValueError('Invalid job path')
    source=source_for(op,v)
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False)
    if op=='inspect':inspect(out);return
    if op=='build':
        if v<3:build(out)
        else:
            for p in source.parent.glob('*.json'):
                if p.name not in ('job.json','bindings.json'):shutil.copy2(p,out/p.name)
            fix_groom(out);bpy.context.scene.frame_set(1)
            bpy.ops.wm.save_as_mainfile(filepath=str(out/'sequence.blend'))
        return
    if op=='check':
        import check317
        check317.SOURCE=source;check317.OUT=out;check317.SLEEVE_PREFIX='318 endpoint-bound leader sleeve';check317.worker();return
    s=bpy.context.scene;s.render.resolution_x=720;s.render.resolution_y=1280;s.render.resolution_percentage=100;s.eevee.taa_render_samples=32;s.eevee.shadow_ray_count=1
    for light in bpy.data.lights:
        if hasattr(light,'use_shadow_jitter'):light.use_shadow_jitter=light.type=='SUN'
        if hasattr(light,'shadow_maximum_resolution'):light.shadow_maximum_resolution=.01
    for f in range(j['start'],j['end']+1):
        dest=out/'frames'/f'frame-{f:04d}.png';assert not dest.exists();s.frame_set(f);s.render.filepath=str(dest);bpy.ops.render.render(write_still=True)
if __name__=='__main__':main()
