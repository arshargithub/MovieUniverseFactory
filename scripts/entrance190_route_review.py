"""Fixed cheap route/horse visual proof, without pretending it is final art."""
import json
import sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import wardrobe_motion178 as base

SOURCE_SHA='08e3d6a3599a655f975db790e9690dc79e0a0e30068fc02f68ae4533f96dc7ef'

def validate(job):
    if job!={'operation':'overview03'}:raise ValueError('Fixed route overview required')
    source=base.BASE/'entrance190-route-horse02/horse-route.blend'
    if SOURCE_SHA is None or source.is_symlink() or base.digest(source)!=SOURCE_SHA:raise ValueError('Unbound route source')
    out=base.BASE/'entrance190-route-overview03'
    if out.exists():raise ValueError('Preserve evidence')
    return source,out

def stage(scene,data):
    import bpy
    from mathutils import Vector
    def mesh(name,verts,faces,color):
        me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update()
        ob=bpy.data.objects.new(name,me);scene.collection.objects.link(ob)
        mat=bpy.data.materials.new(name);mat.diffuse_color=(*color,1);mat.use_nodes=True
        mat.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(*color,1)
        mat.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.85
        me.materials.append(mat);return ob
    # Same sampled surface as the actual contact function, broad enough to
    # show both alternatives. Colour is diagnostic, not new art direction.
    centres=data['position'][::8];yaw=data['heading'][::8];verts=[]
    for p,y in zip(centres,yaw):
        right=np.array([np.cos(y),np.sin(y),0.])
        verts.extend([(p-right*2.2).tolist(),(p+right*2.2).tolist()])
    mesh('190 uphill route',verts,[(i*2,i*2+1,i*2+3,i*2+2) for i in range(len(centres)-1)],(.38,.28,.16))
    mesh('190 blocked easy road',[(-2.6,5,-.004),(2.6,5,-.004),(2.6,-75,-.004),(-2.6,-75,-.004)],[(0,1,2,3)],(.28,.31,.28))
    for x in (-1.8,0,1.8):
        bpy.ops.mesh.primitive_cube_add(size=1,location=(x,-45,.7));o=bpy.context.object
        o.name='190 provisional route obstruction';o.scale=(.8,.35,.7)
    world=bpy.data.worlds.new('190 diagnostic daylight');world.use_nodes=True
    world.node_tree.nodes['Background'].inputs['Color'].default_value=(.28,.31,.36,1)
    world.node_tree.nodes['Background'].inputs['Strength'].default_value=.6;scene.world=world
    sun=bpy.data.lights.new('190 diagnostic sun','SUN');sun.energy=2.5
    ob=bpy.data.objects.new(sun.name,sun);scene.collection.objects.link(ob);ob.rotation_euler=(.4,-.5,-.4)
    camera=bpy.data.objects.new('190 route camera',bpy.data.cameras.new('190 route lens'));scene.collection.objects.link(camera);scene.camera=camera
    camera.data.type='ORTHO';camera.data.clip_end=300
    scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=8;scene.cycles.use_denoising=True
    scene.render.resolution_x=800;scene.render.resolution_y=600;scene.render.resolution_percentage=100
    return camera

def main():
    import bpy
    from mathutils import Vector
    job=json.loads(Path(sys.argv[sys.argv.index('--')+1]).read_text());source,out=validate(job);out.mkdir()
    (out/'handler.py').write_bytes(Path(__file__).read_bytes())
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False)
    with np.load(source.parent/'route.npz',allow_pickle=False) as z:data={k:z[k] for k in z.files}
    scene=bpy.context.scene;camera=stage(scene,data)
    for f in (0,36,72,108,144,192):
        scene.frame_set(f);bpy.context.view_layer.update()
        i=f*8;p=Vector(data['position'][i])+Vector((0,0,1.1));y=float(data['heading'][i])
        right=Vector((np.cos(y),np.sin(y),0));forward=Vector((np.sin(y),-np.cos(y),0))
        for label,offset in (('side',right*7+Vector((0,0,1.))),('quarter',right*5+forward*5+Vector((0,0,2.)))):
            camera.location=p+offset;camera.rotation_euler=(p-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.ortho_scale=5.4
            scene.render.filepath=str(out/(label+'-%04d.png'%f));bpy.ops.render.render(write_still=True)
    p=Vector((12,-27,0));camera.location=(12,-12,65);camera.rotation_euler=(p-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.ortho_scale=85
    scene.render.filepath=str(out/'geography.png');bpy.ops.render.render(write_still=True)
    (out/'result.json').write_text(json.dumps({'source_sha256':SOURCE_SHA,'visual_gate':'NOT_RUN','scope':'Coarse horse route and contacts, no rider/cloth/groom/effects qualification'},indent=2)+'\n')

if __name__=='__main__':main()
