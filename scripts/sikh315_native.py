"""Reviewed native handler with validated operation and paths."""
import sys,json,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
import bpy
from mathutils import Vector
from sikh315_run import OPS,BASE,SOURCE,source_for,validate_job
from sikh257_native import camera_at
def main():
    path=Path(sys.argv[sys.argv.index('--')+1]);job=json.loads(path.read_text())
    op,v=validate_job(job);out=BASE/f'{op}-{v:02d}'
    admitted=out/'chunks'/f"{job['start']:04d}"/'job.json' if 'start' in job else out/'job.json'
    if path.resolve()!=admitted:raise ValueError('Unadmitted path')
    bpy.ops.wm.open_mainfile(filepath=str(source_for(op,v)),load_ui=False,use_scripts=False)
    s=bpy.context.scene;s.frame_set(1)
    if op=='inspect':
        rig=bpy.data.objects['horse.rig'];data={'bones':[],'objects':[]}
        for b in rig.pose.bones:
            if not b.name.startswith(('MCH','ORG','DEF','VIS')):data['bones'].append({'name':b.name,'head':list(b.head),'tail':list(b.tail),'parent':b.parent.name if b.parent else None,'constraints':[c.type for c in b.constraints]})
        for o in s.objects:
            if any(q in o.name for q in ('horse','HORSE','leader','LEADER','dust','earth chip')):data['objects'].append({'name':o.name,'type':o.type,'parent':o.parent.name if o.parent else None,'pos':list(o.matrix_world.translation),'dimensions':list(o.dimensions),'hidden':o.hide_render})
        horse=bpy.data.objects['horse'];data['horse_materials']=[x.name for x in horse.data.materials];data['horse_bounds']=[[min(v.co[k] for v in horse.data.vertices),max(v.co[k] for v in horse.data.vertices)] for k in range(3)]
        with bpy.data.libraries.load(str(ROOT/'.runtime/assets/demonstrator-01/horse.blend'),link=False) as (_,dest):dest.objects=['horse']
        donor=dest.objects[0];data['donor_materials']=[x.name if x else None for x in donor.data.materials];data['donor_counts']=[len(donor.data.vertices),len(donor.data.polygons)];data['body_counts']=[len(horse.data.vertices),len(horse.data.polygons)]
        from collections import Counter
        data['donor_material_usage']=dict(Counter(p.material_index for p in donor.data.polygons))
        (out/'inspection.json').write_text(json.dumps(data,indent=2));return
    if op=='build':
        from sikh315_scene import build
        build(out);s.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(out/'sequence.blend'))
    if op=='finish':
        from sikh315_finish import finish
        finish(out);s.frame_set(1);bpy.ops.wm.save_as_mainfile(filepath=str(out/'sequence.blend'))
    if op=='reopen':
        from sikh315_verify import verify
        verify(out,source_for(op,v).parent)
    s.render.resolution_x=480;s.render.resolution_y=854;s.eevee.taa_render_samples=32
    if op!='profile' and v>=7:
        # Profile6 matched720 controls retain soft sun shadows; point lights
        # keep their existing physical size without expensive emitter jitter.
        s.eevee.shadow_ray_count=1
        for light in bpy.data.lights:
            if hasattr(light,'use_shadow_jitter'):light.use_shadow_jitter=light.type=='SUN'
            if v>=8 and hasattr(light,'shadow_maximum_resolution'):light.shadow_maximum_resolution=.01
    if op=='profile':
        fields={p.identifier:getattr(s.eevee,p.identifier) for p in s.eevee.bl_rna.properties if 'shadow' in p.identifier and p.type in ('INT','FLOAT','BOOLEAN')}
        if not hasattr(s.eevee,'shadow_ray_count'):raise ValueError('No admitted shadow sampling control')
        original=s.eevee.shadow_ray_count;rows=[];s.render.resolution_x=720;s.render.resolution_y=1280
        profiles=(('reference',48,original),('candidate',32,1),('selective',32,1)) if v==6 else (('inherited',32,1),('bounded_shadow',32,1))
        for label,samples,rays in profiles:
            s.eevee.taa_render_samples=samples;s.eevee.shadow_ray_count=rays
            for light in bpy.data.lights:
                if hasattr(light,'use_shadow_jitter'):light.use_shadow_jitter=(light.type=='SUN' or (v==6 and label!='selective'))
                if v!=6 and hasattr(light,'shadow_maximum_resolution'):light.shadow_maximum_resolution=.01 if label=='bounded_shadow' else .0005
            for f in (315,480):
                s.frame_set(f);s.render.filepath=str(out/f'{label}-{f:04d}.png');start=time.monotonic();bpy.ops.render.render(write_still=True);rows.append({'profile':label,'frame':f,'samples':samples,'shadow_rays':rays,'seconds':time.monotonic()-start})
        (out/'profile.json').write_text(json.dumps({'initial':fields,'renders':rows,'selection':'NOT_RUN_VISUAL_COMPARISON'},indent=2));return
    if op in ('movie','proof'):
        (out/'frames').mkdir(exist_ok=op=='movie');s.render.resolution_x=720 if op=='movie' else 360;s.render.resolution_y=1280 if op=='movie' else 640;s.eevee.taa_render_samples=32 if op=='movie' else 20
        windows=((job.get('start',1),job.get('end',696)),) if op=='movie' else ((275,356),(414,506))
        for a,b in windows:
            if any((out/'frames'/f'frame-{f:04d}.png').exists() for f in range(a,b+1)):raise ValueError('Refusing to overwrite rendered evidence')
            s.frame_start=a;s.frame_end=b;s.render.filepath=str(out/'frames/frame-');bpy.ops.render.render(animation=True)
        return
    for f in (80,126,150,283,294,306,315,324,333,342,350,420,435,450,465,480,500,600,680):
        s.frame_set(f);s.render.filepath=str(out/f'frame-{f:04d}.png');bpy.ops.render.render(write_still=True)
    if op in ('build','finish'):
        if op=='finish' and v>=8:return
        if op=='finish' and v==5:
            s.frame_set(480)
            fx=[o for o in bpy.data.objects if o.name.startswith(('315 detached world wake','305 hoof earth puff'))]
            states=[o.hide_render for o in fx]
            for o in fx:o.hide_render=True
            s.render.filepath=str(out/'no-volume-control-0480.png');bpy.ops.render.render(write_still=True)
            for o,state in zip(fx,states):o.hide_render=state
        from sikh257_native import material
        clay=material('315 diagnostic untextured earth',(.32,.32,.32));clay.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.85
        road=bpy.data.objects['irregular packed farm track'];saved=list(road.data.materials);road.data.materials.clear();road.data.materials.append(clay)
        for f in (80,315):
            s.frame_set(f);s.render.filepath=str(out/f'ground-clay-{f:04d}.png');bpy.ops.render.render(write_still=True)
        road.data.materials.clear()
        for mat in saved:road.data.materials.append(mat)
        cam=s.camera;cam.animation_data_clear();cam.data.animation_data_clear();s.render.resolution_x=s.render.resolution_y=600;cam.data.lens=48
        for f in (294,306,315,330,342,350):
            s.frame_set(f);camera_at(cam,(14,-28,5.2),(7.5,-29,5));s.render.filepath=str(out/f'horse-side-{f:04d}.png');bpy.ops.render.render(write_still=True)
if __name__=='__main__':main()
