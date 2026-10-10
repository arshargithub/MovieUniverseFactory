"""Cheap full-route native motion proof, explicitly not finished actor footage."""
import json,sys,math,time
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import wardrobe_motion178 as base


def main():
    import bpy
    from mathutils import Vector,Matrix
    from entrance205_geography import fields
    from entrance205_camera import route_camera
    job=json.loads(Path(sys.argv[sys.argv.index('--')+1]).read_text())
    if job not in ({'operation':'coarse02'},{'operation':'coarse06'}):raise ValueError('Fixed205 coarse operation')
    src=base.BASE/'entrance205-horse01/horse-route.blend';out=base.BASE/('entrance205-'+job['operation'])
    r=json.loads((src.parent/'result.json').read_text())
    if out.exists() or base.digest(src)!=r['native_sha256']:raise ValueError('Source/output')
    out.mkdir();(out/'handler.py').write_bytes(Path(__file__).read_bytes())
    bpy.ops.wm.open_mainfile(filepath=str(src),load_ui=False,use_scripts=False)
    scene=bpy.context.scene
    with np.load(src.parent/'route.npz') as z:route={k:z[k] for k in z.files}
    x=np.arange(-130,71,1.);y=np.arange(-145,31,1.);xx,yy=np.meshgrid(x,y)
    xy=np.column_stack((xx.ravel(),yy.ravel()));z,_=fields(xy,route)
    me=bpy.data.meshes.new('205 coarse ledge');nx=len(x)
    faces=[(j*nx+i,j*nx+i+1,(j+1)*nx+i+1,(j+1)*nx+i) for j in range(len(y)-1) for i in range(nx-1)]
    me.from_pydata(np.column_stack((xy,z)).tolist(),[],faces);me.update()
    land=bpy.data.objects.new('205 ledge',me);scene.collection.objects.link(land);land.color=(.65,.52,.35,1)
    for a in (-1,1):
        bpy.ops.mesh.primitive_cube_add(size=1,location=(a*2.3,-66.3,.7));o=bpy.context.object;o.scale=(.14,.14,1.4);o.color=(.10,.07,.04,1)
        bpy.ops.mesh.primitive_uv_sphere_add(segments=12,ring_count=6,radius=.22,location=(a*1.3,-66.8,1.6));o=bpy.context.object;o.color=(.15,.12,.1,1)
    bpy.ops.mesh.primitive_cube_add(size=1,location=(0,-66.3,1.2));o=bpy.context.object;o.scale=(4.8,.12,.15);o.color=(.1,.07,.04,1)
    bpy.ops.mesh.primitive_uv_sphere_add(segments=16,ring_count=8,radius=1);head=bpy.context.object;head.name='205 rider head PROXY';head.scale=(.11,.12,.16);head.color=(.5,.22,.1,1)
    camera=bpy.data.objects.new('205 coarse camera',bpy.data.cameras.new('205 camera'));scene.collection.objects.link(camera);scene.camera=camera
    camera.data.type='PERSP';camera.data.sensor_fit='VERTICAL';camera.data.sensor_height=36;camera.data.clip_end=1000;camera.data.clip_start=.05
    scene.render.engine='BLENDER_WORKBENCH';scene.display.shading.light='STUDIO';scene.display.shading.color_type='OBJECT';scene.display.shading.show_shadows=True;scene.display.shading.show_cavity=True
    scene.display.shading.background_type='WORLD';scene.world.color=(.35,.4,.47)
    scene.render.resolution_x=288;scene.render.resolution_y=512;scene.render.resolution_percentage=100
    rows=[]
    for f in range(0,288,2):
        scene.frame_set(f);p=route['position'][f*8];head.location=p+[0,0,2.6]
        loc,target,lens,shot=route_camera(f/24);camera.location=loc;camera.rotation_euler=(Vector(target)-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.lens=lens
        scene.render.filepath=str(out/f'frame-{f:04d}.png');bpy.ops.render.render(write_still=True)
        rows.append({'frame':f,'shot':shot,'camera':loc.tolist(),'target':target.tolist()})
        if f%24==0:print('205 coarse second',f/24,flush=True)
    (out/'result.json').write_text(json.dumps({'source_sha256':r['native_sha256'],'frames':rows,'visual_gate':'NOT_RUN','limits':'Horse plus proxy head; no actual rider, cloth, effects, or finished appearance'},indent=2)+'\n')


if __name__=='__main__':main()
