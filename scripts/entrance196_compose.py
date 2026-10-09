"""Compose inherited rock geometry at readable size; preserve the hoof corridor."""
import json,math,os,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import wardrobe_motion178 as base

def main():
    import bpy
    if json.loads(Path(sys.argv[sys.argv.index('--')+1]).read_text())!={'operation':'compose13'}:raise ValueError('Fixed composition required')
    source=base.BASE/'entrance196-refine09/scene.blend';out=base.BASE/'entrance196-compose13'
    if out.exists() or base.digest(source)!='223e2061c0ce20eac08cc64b75112581b0e7091968956854f51a00dc9a2f2ced':raise ValueError('Changed source')
    out.mkdir();(out/'handler.py').write_bytes(Path(__file__).read_bytes())
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False);scene=bpy.context.scene;scene.frame_set(217);base.check_protected()
    from entrance188_ground import bank_height
    root=bpy.data.objects['AS_world_travel'];source_mesh=bpy.data.objects['MF196_scanned_scree_0'].data
    mesh=source_mesh.copy();mesh.name='196 weathered clustered rock shared'
    for i,original in enumerate(list(mesh.materials)):
        mat=original.copy();mat.name='196 cool weathered '+original.name;mesh.materials[i]=mat
        n,l=mat.node_tree.nodes,mat.node_tree.links;bs=next(x for x in n if x.type=='BSDF_PRINCIPLED')
        if bs.inputs['Base Color'].is_linked:
            old=bs.inputs['Base Color'].links[0].from_socket;mix=n.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=.62;mix.inputs[2].default_value=(.53,.59,.64,1)
            l.new(old,mix.inputs[1]);l.new(mix.outputs[0],bs.inputs['Base Color'])
        bs.inputs['Roughness'].default_value=.9
    zmin=min(v.co.z for v in mesh.vertices);zmax=max(v.co.z for v in mesh.vertices)
    rng=np.random.default_rng(19613);count=0;centers=[]
    for i in range(130):
        x=float(rng.choice([-1,1])*rng.uniform(18,105));y=float(rng.uniform(-720,95));centers.append((x,y))
        for j in range(int(rng.integers(10,27))):
            px=x+rng.normal(0,6);py=y+rng.normal(0,8)
            if abs(px)<9:continue
            s=float(rng.uniform(.65,2.6))
            if j==0:s=float(rng.uniform(4.2,7.8))
            elif rng.random()<.14:s=float(rng.uniform(2.8,4.1))
            height=s*rng.uniform(.85,1.55)
            o=bpy.data.objects.new('MF196_rock_cluster_'+str(count),mesh);scene.collection.objects.link(o);o.parent=root
            o.scale=(s,s*rng.uniform(.6,1.4),height)
            o.location=(float(px),float(py),bank_height(px,py)-zmin*height-(zmax-zmin)*height*.20)
            o.rotation_euler=(rng.uniform(-.1,.1),rng.uniform(-.1,.1),rng.uniform(0,math.tau));count+=1
    # Tighten grass into survivor tufts rather than the previous even field.
    hidden=0
    for o in scene.objects:
        if o.name.startswith(('MF188_bank_grass','MF188_bank_scrub')) and not o.hide_render:
            if abs(o.location.x)<120 and math.sin(o.location.x*1.73+o.location.y*.73)>.1:
                o.hide_render=True;hidden+=1
    # Near-path chips use actual irregular rock forms, small enough not to
    # change hoof support. Avoid the x range occupied by the source hooves.
    chips=0
    for i in range(1300):
        x=float(rng.choice([-1,1])*rng.uniform(4.8,13));y=float(rng.uniform(-680,80));s=float(rng.uniform(.12,.35))
        o=bpy.data.objects.new('MF196_path_chip_'+str(i),mesh);scene.collection.objects.link(o);o.parent=root;o.scale=(s,s*.8,s*.5)
        o.location=(x,y,bank_height(x,y)-zmin*s*.5-.025);o.rotation_euler.z=float(rng.uniform(0,math.tau));chips+=1
    # A few larger airborne fragments make the authored contact readable at
    # preview size; same origins/timing/trajectories, no new random clock.
    from entrance189_groom import read_mdd,write_mdd,attach_cache
    ob=bpy.data.objects['MF196_hoof_ejected_pebbles'];mod=next(m for m in ob.modifiers if m.type=='MESH_CACHE');a=read_mdd(bpy.path.abspath(mod.filepath))
    def frames():
        for row in a:
            q=np.array(row,float).reshape(-1,17,3);cent=q.mean(axis=1,keepdims=True)
            factors=np.where(np.arange(len(q))%5==0,1.6,1.15)
            q=cent+(q-cent)*factors[:,None,None]
            yield q.reshape(-1,3).astype(np.float32)
    path=out/'debris.mdd';write_mdd(path,144,len(ob.data.vertices),frames());attach_cache(ob,path)
    caches=[]
    for o in scene.objects:
        for m in o.modifiers:
            if m.type=='MESH_CACHE':
                p=Path(bpy.path.abspath(m.filepath)).resolve();m.filepath=str(p);caches.append({'object':o.name,'path':os.path.relpath(p,out),'sha256':base.digest(p),'start':m.frame_start})
    base.check_protected();bpy.context.preferences.filepaths.save_version=0
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'scene.blend'),compress=True);bpy.ops.file.make_paths_relative();bpy.ops.wm.save_as_mainfile(filepath=str(out/'scene.blend'),compress=True)
    (out/'result.json').write_text(json.dumps({'source_sha256':base.digest(source),'native_sha256':base.digest(out/'scene.blend'),'caches':caches,'clustered_rocks':count,'path_chips':chips,'grass_culled':hidden,'source_rock_z_bounds':[zmin,zmax],'motion_unchanged_from':'entrance196-build02','visual_gate':'NOT_RUN'},indent=2)+'\n')

if __name__=='__main__':main()
