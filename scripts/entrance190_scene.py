"""Fixed integrated shared-route look proof; source-bound local operation."""
import json
import sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import wardrobe_motion178 as base
SOURCE_SHA='0cbb3916b644f4d9abd4711da5074f55b179480401804dc266fd38fbaa27f192'


def path_sample(route,t):
    if t<0:return np.array([0.,-12*t,0.])
    return np.array([np.interp(t,route['time'],route['position'][:,j]) for j in range(3)])


def wake(scene,route):
    """Overlapping path-history density fields; authored volume, not fluid."""
    import bpy
    from entrance_astra_world import mesh_object
    for ob in scene.objects:
        if 'dust' in ob.name.lower():ob.hide_render=True
    mat=bpy.data.materials.new('190 curved ochre wake');mat.use_nodes=True
    n,l=mat.node_tree.nodes,mat.node_tree.links;n.clear()
    def mathnode(op,a,b=None):
        q=n.new('ShaderNodeMath');q.operation=op
        for i,v in enumerate((a,b) if b is not None else (a,)):
            if isinstance(v,(int,float)):q.inputs[i].default_value=v
            else:l.new(v,q.inputs[i])
        return q.outputs[0]
    def vector(op,a,b=None):
        q=n.new('ShaderNodeVectorMath');q.operation=op
        for i,v in enumerate((a,b) if b is not None else (a,)):
            if isinstance(v,tuple):q.inputs[i].default_value=v
            else:l.new(v,q.inputs[i])
        return q
    tc=n.new('ShaderNodeTexCoord');extent=vector('MULTIPLY',tc.outputs['Generated'],(1.,1.,1.))
    origin=vector('ADD',extent.outputs['Vector'],(0.,0.,0.));world=origin.outputs[0]
    age=np.linspace(.12,2.4,14);centers=[];total=0.
    for a in age:
        delta=vector('SUBTRACT',world,(0.,0.,0.));centers.append(delta.inputs[1])
        # Broad overlapping cells eliminate separate smoke-ball silhouettes.
        radii=(5+10*a,8+10*a,3+10*a)
        norm=vector('DIVIDE',delta.outputs[0],radii);dist=vector('DOT_PRODUCT',norm.outputs[0],norm.outputs[0]).outputs['Value']
        f=mathnode('POWER',mathnode('MAXIMUM',mathnode('SUBTRACT',1,dist),0),2)
        total=mathnode('ADD',total,mathnode('MULTIPLY',f,float((1-a/3)**1.4)))
    noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=.18;noise.inputs['Detail'].default_value=3
    l.new(world,noise.inputs['Vector']);density=mathnode('MULTIPLY',mathnode('MULTIPLY',total,noise.outputs['Fac']),.12)
    vol=n.new('ShaderNodeVolumePrincipled');vol.inputs['Color'].default_value=(.95,.85,.65,1);vol.inputs['Anisotropy'].default_value=.28
    l.new(density,vol.inputs['Density']);vol.inputs['Emission Color'].default_value=(.65,.43,.20,1)
    l.new(mathnode('MULTIPLY',density,.65),vol.inputs['Emission Strength']);out=n.new('ShaderNodeOutputMaterial');l.new(vol.outputs[0],out.inputs['Volume'])
    verts=[(-1,-1,-1),(-1,-1,1),(-1,1,-1),(-1,1,1),(1,-1,-1),(1,-1,1),(1,1,-1),(1,1,1)]
    faces=[(0,2,6,4),(1,5,7,3),(0,4,5,1),(2,3,7,6),(0,1,3,2),(4,6,7,5)]
    ob=mesh_object('MF190_curved_wake',verts,faces,scene.collection);ob.data.materials.append(mat)
    for f in range(361,554):
        t=(f-361)/24;points=[]
        for a,socket in zip(age,centers):
            p=path_sample(route,t-a)*8.3+np.array([0,.2,-20.931]);p[2]+=(3+10*a)*.25
            points.append(p);socket.default_value=tuple(p);socket.keyframe_insert(data_path='default_value',frame=f)
        points=np.array(points);lo=points.min(0)-[31,35,28];hi=points.max(0)+[31,35,28]
        ob.location=(lo+hi)/2;ob.scale=(hi-lo)/2
        ob.keyframe_insert(data_path='location',frame=f);ob.keyframe_insert(data_path='scale',frame=f)
        extent.inputs[1].default_value=tuple(hi-lo);origin.inputs[1].default_value=tuple(lo)
        extent.inputs[1].keyframe_insert(data_path='default_value',frame=f);origin.inputs[1].keyframe_insert(data_path='default_value',frame=f)
    return {'method':'Path-history overlapping volume field','fluid_simulation':False,'history_seconds':2.4}


def camera_pose(route,frame,geography=False):
    from mathutils import Vector
    t=(frame-361)/24;p=path_sample(route,t)*8.3+np.array([0,.2,-20.931])
    if geography:
        return Vector((85,65,175)),Vector((-80,-235,-5)),210.
    # One steady high trailing view: both alternatives are visible early;
    # the horse gains distance at the end instead of the camera racing ahead.
    lag=path_sample(route,max(0,t-1.25))*8.3+np.array([0,.2,-20.931])
    weight=np.clip(t/2,0,1);weight=weight*weight*(3-2*weight)
    location=lag+np.array([100-35*weight,65,92-24*weight])
    target=p+np.array([-12,-12,9])
    return Vector(location),Vector(target),105+10*max(0,t-5)


def main():
    import bpy
    from mathutils import Matrix,Vector
    from entrance190_geography import build
    job=json.loads(Path(sys.argv[sys.argv.index('--')+1]).read_text())
    if job!={'operation':'scene18'}:raise ValueError('Fixed shared-scene operation required')
    source=base.BASE/'entrance190-integration14/integrated.blend';out=base.BASE/'entrance190-scene18'
    if out.exists() or base.digest(source)!=SOURCE_SHA:raise ValueError('Unbound source or existing evidence')
    out.mkdir();(out/'handler.py').write_bytes(Path(__file__).read_bytes())
    record=json.loads((source.parent/'result.json').read_text())
    with np.load(base.BASE/'entrance190-rider09/route.npz',allow_pickle=False) as z:route={k:z[k] for k in z.files}
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False);base.check_protected();scene=bpy.context.scene
    geography=build(scene,route,record['prior_visibility']);dust=wake(scene,route)
    root=bpy.data.objects['MF190_shared_route_actor'];scene.frame_set(361);bpy.context.view_layer.update()
    for ob in scene.objects:
        if ob.type=='LIGHT' and ob.data.type!='SUN' and ob.parent is None:
            old=ob.matrix_world.copy();ob.parent=root;ob.matrix_world=old
    cam=scene.camera;cam.animation_data_clear();cam.data.animation_data_clear();cam.data.type='ORTHO';cam.data.clip_end=12000
    for f in range(361,554):
        loc,target,scale=camera_pose(route,f);cam.location=loc;cam.rotation_euler=(target-loc).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=scale
        cam.keyframe_insert(data_path='location',frame=f);cam.keyframe_insert(data_path='rotation_euler',frame=f);cam.data.keyframe_insert(data_path='ortho_scale',frame=f)
    scene.render.resolution_x=432;scene.render.resolution_y=768;scene.render.resolution_percentage=100
    scene.cycles.samples=8;scene.cycles.device='CPU';scene.render.use_persistent_data=True
    for f in (361,385,409,433,457,481,505,529,552):
        scene.frame_set(f);scene.render.filepath=str(out/('frame-%04d.png'%f));bpy.ops.render.render(write_still=True)
    scene.frame_set(361);old=cam.matrix_world.copy();scale=cam.data.ortho_scale
    loc,target,s=camera_pose(route,361,True);cam.location=loc;cam.rotation_euler=(target-loc).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=s
    scene.render.filepath=str(out/'geography.png');bpy.ops.render.render(write_still=True)
    cam.matrix_world=old;cam.data.ortho_scale=scale;scene.frame_set(362);scene.frame_set(361)
    for ob in scene.objects:
        for m in ob.modifiers:
            if m.type=='MESH_CACHE':m.filepath=bpy.path.abspath(m.filepath)
    bpy.context.preferences.filepaths.save_version=0
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'scene.blend'),compress=True);bpy.ops.file.make_paths_relative();bpy.ops.wm.save_as_mainfile(filepath=str(out/'scene.blend'),compress=True)
    (out/'result.json').write_text(json.dumps({'source_sha256':SOURCE_SHA,'native_sha256':base.digest(out/'scene.blend'),'geography':geography,'dust':dust,'visual_gate':'NOT_RUN'},indent=2)+'\n')


if __name__=='__main__':main()
