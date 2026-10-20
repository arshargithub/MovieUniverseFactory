"""Reviewed319 fixed native operations. No external scripts or expression inputs."""
import sys,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'src'),str(ROOT/'scripts')]
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from sikh319 import BASE,validate,source_for

def inspect(out):
    s=bpy.context.scene;s.frame_set(283)
    roots=[bpy.data.objects['mounted leader']]+sorted([o for o in bpy.data.objects if o.name.startswith('FOOT WARRIOR ')],key=lambda o:o.name)
    rows=[]
    for root in roots:
        rows.append({'root':root.name,'matrix':[list(r) for r in root.matrix_world],
          'children':[{'name':o.name,'type':o.type,'location':list(o.location),'scale':list(o.scale),'rotation':list(o.rotation_euler),
            'hidden':o.hide_render,'dimensions':list(o.dimensions),
            'vertices':len(o.data.vertices) if o.type=='MESH' else None,
            'materials':[m.name for m in o.data.materials if m] if hasattr(o.data,'materials') else [],
            'children':[c.name for c in o.children]} for o in root.children]})
    (out/'actors.json').write_text(json.dumps(rows,indent=2))

def main():
    j=validate(json.loads(Path(sys.argv[sys.argv.index('--')+1]).read_text()));op=j['operation'];v=j['version']
    out=BASE/f'{op}-{v:02d}'
    bpy.ops.wm.read_factory_settings(use_empty=True)
    if op=='donor':
        from sikh319_cast import DONOR
        from sikh257_native import material
        with bpy.data.libraries.load(str(DONOR),link=False) as (_,d):d.objects=['GEO-body_male_realistic']
        ob=d.objects[0];bpy.context.collection.objects.link(ob)
        for mod in ob.modifiers:
            if mod.type=='MULTIRES':mod.levels=min(2,mod.total_levels)
        ob.data.materials.clear();ob.data.materials.append(material('319 anatomical clay',(.30,.24,.19)))
        bpy.context.view_layer.update()
        center=(-2.705880880355835-1.8228728771209717)/2
        ob.location.x-=center;bpy.context.view_layer.update()
        s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=16;s.cycles.use_denoising=True
        s.render.resolution_x=900;s.render.resolution_y=1000;s.render.resolution_percentage=100
        s.world=bpy.data.worlds.new('319 donor neutral');s.world.use_nodes=True
        s.world.node_tree.nodes['Background'].inputs[0].default_value=(.18,.18,.18,1)
        cd=bpy.data.cameras.new('319 donor camera');cam=bpy.data.objects.new(cd.name,cd)
        s.collection.objects.link(cam);s.camera=cam;cd.type='ORTHO';cd.ortho_scale=1.8
        cam.location=(0,-4,1.0);cam.rotation_euler=(Vector((0,0,1.0))-cam.location).to_track_quat('-Z','Y').to_euler()
        ld=bpy.data.lights.new('319 donor key','AREA');ld.energy=300;ld.size=2
        lo=bpy.data.objects.new(ld.name,ld);s.collection.objects.link(lo);lo.location=(-1,-2,3)
        lo.rotation_euler=(Vector((0,0,1))-lo.location).to_track_quat('-Z','Y').to_euler()
        s.render.filepath=str(out/'frames/frame-0001.png');bpy.ops.render.render(write_still=True)
        points=[ob.matrix_world@v.co for v in ob.evaluated_get(bpy.context.evaluated_depsgraph_get()).data.vertices]
        (out/'bounds.json').write_text(json.dumps({'bounds':[[min(p[k] for p in points),max(p[k] for p in points)] for k in range(3)]},indent=2))
        return
    bpy.ops.wm.open_mainfile(filepath=str(source_for(op,v)),load_ui=False,use_scripts=False)
    if op=='inspect':inspect(out);return
    if op=='build':
        import sikh319_cast
        report=sikh319_cast.build()
        (out/'cast.json').write_text(json.dumps(report,indent=2))
        bpy.ops.wm.save_as_mainfile(filepath=str(out/'sequence.blend'))
        return
    if op in ('look','study','movie','reopen'):
        s=bpy.context.scene;s.render.resolution_x=720;s.render.resolution_y=1280
        s.render.resolution_percentage=100;s.eevee.taa_render_samples=32;s.eevee.shadow_ray_count=1
        for light in bpy.data.lights:
            if hasattr(light,'use_shadow_jitter'):light.use_shadow_jitter=light.type=='SUN'
            if hasattr(light,'shadow_maximum_resolution'):light.shadow_maximum_resolution=.01
        if op=='study':
            root=bpy.data.objects['mounted leader']
            keep={root,*root.children_recursive}
            for ob in bpy.data.objects:
                if ob not in keep:ob.hide_render=True
            d=bpy.data.cameras.new('319 study camera');camera=bpy.data.objects.new('319 study camera',d)
            s.collection.objects.link(camera);s.camera=camera;d.type='ORTHO';d.ortho_scale=.85
            s.world=bpy.data.worlds.new('319 neutral study');s.world.use_nodes=True
            s.world.node_tree.nodes['Background'].inputs[0].default_value=(.09,.09,.09,1)
            head=next(o for o in root.children if o.name.startswith('secondary adult head'))
            surface=BVHTree.FromPolygons([p.co for p in head.data.vertices],[tuple(p.vertices) for p in head.data.polygons])
            samples=[]
            for z in (-.06,-.04,-.02,0,.02,.04,.06,.08,.10):
                for x in (0,.025,.035,.045,.06):
                    hit=surface.ray_cast(Vector((x,-.4,z)),Vector((0,1,0)))[0]
                    samples.append({'x':x,'z':z,'front_y':hit.y if hit else None})
            (out/'face-surface.json').write_text(json.dumps(samples,indent=2))
            lights=[]
            for name,pos,energy,size in [('key',(-1,-2,2),130,2),('fill',(2,-1,1),60,2)]:
                ld=bpy.data.lights.new('319 '+name,'AREA');ld.energy=energy;ld.size=size
                lo=bpy.data.objects.new(ld.name,ld);s.collection.objects.link(lo);lights.append((lo,Vector(pos)))
        for f in j['frames']:
            dest=out/'frames'/f'frame-{f:04d}.png'
            if dest.exists():raise ValueError('Refusing overwrite')
            s.frame_set(f)
            if op=='study':
                target=root.matrix_world@Vector((0,0,.59))
                offset=Vector((0,-2,.1)) if f==283 else Vector((1.4,-1.5,.1))
                camera.location=target+root.matrix_world.to_quaternion()@offset
                camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler()
                for lo,pos in lights:
                    lo.location=target+root.matrix_world.to_quaternion()@pos
                    lo.rotation_euler=(target-lo.location).to_track_quat('-Z','Y').to_euler()
            s.render.filepath=str(dest);bpy.ops.render.render(write_still=True)
        return
    raise ValueError('Unimplemented operation')
if __name__=='__main__':main()
