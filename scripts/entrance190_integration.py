"""Internal full-costume turn review; not final geography or camera delivery."""
import json
import math
import sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import wardrobe_motion178 as base
SOURCE_SHA='c56b0972bd1e910371dde49db6678eb2376d637f89ed06edc7242d05958e7a6c'


def actor_object(ob):
    return ob.name.startswith(('MF185_','MF_173_','MF_natural147_','MF_aimable_eye_')) or ob.name in (
        'MF_studio_adult_body','MF_body156_fit_rig','MF_fit_trousers_173_visible','MF188_flowing_mane','MF188_short_coat_fuzz')


def main():
    import bpy
    from mathutils import Matrix,Vector
    from entrance189_groom import read_mdd,write_mdd,attach_cache
    from entrance190_contacts import world_transform
    from entrance190_groom import update as groom_update
    job=json.loads(Path(sys.argv[sys.argv.index('--')+1]).read_text())
    if job!={'operation':'integration14'}:raise ValueError('Fixed integration review required')
    source=base.BASE/'entrance190-fitted12/fitted.blend';out=base.BASE/'entrance190-integration14'
    if out.exists() or source.is_symlink() or base.digest(source)!=SOURCE_SHA:raise ValueError('Unbound integration source')
    cloth={}
    for label,folder,key in (('shawl','entrance190-shawl17','MF185_moving_shawl'),('skirt','entrance190-lower16','MF185_free_lower_tunic')):
        d=base.BASE/folder;r=json.loads((d/'result.json').read_text());p=d/'trajectory.npz'
        if base.digest(p)!=r['trajectory_sha256']:raise ValueError('Changed cloth source')
        with np.load(p,allow_pickle=False) as z:
            a=z['frames'][-193:]
            if len(a)!=193:raise ValueError('Incomplete continuation')
            cloth[key]=(label,a)
    out.mkdir();(out/'handler.py').write_bytes(Path(__file__).read_bytes())
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False);base.check_protected()
    scene=bpy.context.scene;rig=bpy.data.objects['MF_body156_fit_rig']
    for name,(label,a) in cloth.items():
        ob=bpy.data.objects[name]
        if len(ob.data.vertices)!=a.shape[1]:raise ValueError('Cloth topology mismatch')
        path=out/(label+'.mdd');write_mdd(path,193,a.shape[1],iter(a));attach_cache(ob,path,361)
    groom=groom_update(out)
    # A replacement cache is inserted before shell/subdivision. Verify final
    # stacks, not transient dependency warnings while constructing modifiers.
    cache_rows=[]
    for ob in scene.objects:
        if not actor_object(ob) or ob.hide_render:continue
        for i,m in enumerate(ob.modifiers):
            if m.type!='MESH_CACHE':continue
            p=Path(bpy.path.abspath(m.filepath)).resolve();a=read_mdd(p)
            if len(ob.data.vertices)!=a.shape[1] or i!=0:raise ValueError('Unexpected final cache topology/stack: '+ob.name)
            m.filepath=str(p);cache_rows.append({'object':ob.name,'path':str(p),'vertices':a.shape[1],'frames':len(a),'sha256':base.digest(p)})
    raw=bpy.data.objects['MF185_gait_saddle.stirrup.strap'];raw.hide_render=True
    # Buckle hardware follows the same pelvis attachment, not a held old key.
    with np.load(base.BASE/'entrance190-fitted12/lower-contacts.npz',allow_pickle=False) as z:pm=z['pelvis_matrices'];ref=z['reference_pelvis']
    scene.frame_set(360);bpy.context.view_layer.update()
    for name in ('MF_173_belt_buckle','MF_173_buckle_tongue'):
        ob=bpy.data.objects[name];old=ob.matrix_world.copy();ob.animation_data_clear();ob.rotation_mode='QUATERNION'
        for i,mat in enumerate(pm):
            ob.matrix_world=Matrix(mat@np.linalg.inv(ref))@old
            for prop in ('location','rotation_quaternion','scale'):ob.keyframe_insert(data_path=prop,frame=361+i)
    original_visibility={o.name:not o.hide_render for o in scene.objects}
    actors={o for o in scene.objects if actor_object(o) and not o.hide_render};actors.add(rig)
    required=set(actors)
    for _ in range(10):
        prior=len(required)
        for ob in list(required):
            if ob.parent:required.add(ob.parent)
            for m in ob.modifiers:
                for prop in ('target','object'):
                    target=getattr(m,prop,None)
                    if isinstance(target,bpy.types.Object):required.add(target)
            for c in ob.constraints:
                target=getattr(c,'target',None)
                if isinstance(target,bpy.types.Object):required.add(target)
        if len(required)==prior:break
    root=bpy.data.objects.new('MF190_shared_route_actor',None);scene.collection.objects.link(root);root.rotation_mode='QUATERNION'
    for ob in required:
        if ob.parent is None and not any(c.type=='CHILD_OF' and c.target in required for c in ob.constraints):
            mat=ob.matrix_world.copy();ob.parent=root;ob.matrix_world=mat
    with np.load(base.BASE/'entrance190-rider09/route.npz',allow_pickle=False) as z:route={k:z[k] for k in z.files}
    for frame in range(361,554):
        root.matrix_world=world_transform(route,frame)
        for prop in ('location','rotation_quaternion','scale'):root.keyframe_insert(data_path=prop,frame=frame)
    # Diagnostic view: no stale straight-road world or held dust is displayed.
    for ob in scene.objects:
        if ob.type not in ('LIGHT','CAMERA','EMPTY'):ob.hide_render=ob not in actors
    scene.camera.animation_data_clear();scene.camera.data.animation_data_clear();scene.camera.data.type='ORTHO'
    scene.camera.data.clip_end=12000;scene.cycles.device='CPU';scene.cycles.samples=8;scene.render.use_persistent_data=True
    lights={o:o.matrix_world.copy() for o in scene.objects if o.type=='LIGHT' and o.data.type!='SUN'}
    scene.render.resolution_x=720;scene.render.resolution_y=720;scene.render.resolution_percentage=100
    for frame in (361,409,457,505,553):
        scene.frame_set(frame);bpy.context.view_layer.update();rootmat=root.matrix_world.copy()
        yaw=Matrix.Rotation(float(route['heading'][(frame-361)*8]),4,'Z')
        for ob,mat in lights.items():ob.matrix_world=rootmat@mat
        for angle,label in ((0,'front'),(70,'left'),(180,'back'),(290,'right')):
            center=rootmat@Vector((0,-2,-4.7));offset=yaw@Matrix.Rotation(math.radians(angle),4,'Z')@Vector((0,-32,5))
            scene.camera.location=center+offset;scene.camera.rotation_euler=(center-scene.camera.location).to_track_quat('-Z','Y').to_euler();scene.camera.data.ortho_scale=17
            scene.render.filepath=str(out/(label+'-'+str(frame)+'.png'));bpy.ops.render.render(write_still=True)
    for ob,mat in lights.items():ob.matrix_world=mat
    # Keep environment hidden until its shared-geography construction, rather
    # than saving a misleading actor riding off the old road as ready footage.
    for ob in scene.objects:
        for m in ob.modifiers:
            if m.type=='MESH_CACHE':m.filepath=bpy.path.abspath(m.filepath)
    scene.frame_start=361;scene.frame_end=553;scene.frame_set(409)
    scene['MF190_status']='Integrated costume/groom candidate; visual review pending; geography and final camera NOT_RUN'
    bpy.context.preferences.filepaths.save_version=0
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'integrated.blend'),compress=True);bpy.ops.file.make_paths_relative()
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'integrated.blend'),compress=True)
    (out/'result.json').write_text(json.dumps({'source_sha256':SOURCE_SHA,'native_sha256':base.digest(out/'integrated.blend'),
        'groom':groom,'caches':cache_rows,'prior_visibility':original_visibility,'actor_roots':[o.name for o in root.children],
        'visual_gate':'NOT_RUN','scope':'Actual bank/grade with new cloth and fitted contacts; no geography/complete moving-camera proof'},indent=2)+'\n')


if __name__=='__main__':main()
