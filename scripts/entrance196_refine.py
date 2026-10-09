"""Replace failed batched synthetic stones with instanced existing rock art."""
import json,math,os,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import wardrobe_motion178 as base

def main():
    import bpy
    if json.loads(Path(sys.argv[sys.argv.index('--')+1]).read_text())!={'operation':'refine09'}:raise ValueError('Fixed refinement only')
    source=base.BASE/'entrance196-build02/scene.blend';out=base.BASE/'entrance196-refine09'
    if out.exists() or base.digest(source)!='638f7c5a057eb94183f172b199a476ab324f5c806e20a42e16b23a705bd69e96':raise ValueError('Source mismatch')
    out.mkdir();(out/'handler.py').write_bytes(Path(__file__).read_bytes())
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False);base.check_protected();scene=bpy.context.scene;scene.frame_set(217)
    bpy.data.objects['MF196_clustered_rocky_margins'].hide_render=True
    original=bpy.data.objects['MF188_bank_stone_0000'];temp=original.copy();temp.data=original.data.copy();scene.collection.objects.link(temp)
    temp.name='196 rock LOD temporary';temp.hide_viewport=False
    for m in list(temp.modifiers):temp.modifiers.remove(m)
    mod=temp.modifiers.new('196 geometry reduction','DECIMATE');mod.ratio=.06
    bpy.context.view_layer.objects.active=temp;bpy.ops.object.modifier_apply(modifier=mod.name)
    mesh=temp.data;mesh.name='196 existing boulder reduced reusable';p=np.array([v.co[:] for v in mesh.vertices]);center=(p.max(0)+p.min(0))/2;span=np.max(np.ptp(p,axis=0))
    for v in mesh.vertices:v.co=tuple((np.array(v.co)-center)/(span/2))
    mesh.update();bpy.data.objects.remove(temp,do_unlink=True)
    # Actual inherited UV rock artwork stays intact, without making each
    # instance a separate texture/mesh copy.
    for poly in mesh.polygons:poly.use_smooth=False
    rng=np.random.default_rng(19609);root=bpy.data.objects['AS_world_travel']
    from entrance188_ground import bank_height
    count=0
    for i in range(3900):
        x=float(rng.uniform(-118,100));y=float(rng.uniform(-720,110))
        cluster=.40+.30*math.sin(y/28+math.sin(x/14)*2)+.2*math.sin(y/8+x/13)
        if abs(x)<7 or rng.random()>cluster:continue
        size=float(rng.uniform(.25,1.0))
        if abs(x)>13 and rng.random()<.26:size=float(rng.uniform(1.1,2.5))
        if abs(x)>28 and rng.random()<.06:size=float(rng.uniform(3,5.3))
        o=bpy.data.objects.new('MF196_scanned_scree_'+str(count),mesh);scene.collection.objects.link(o);o.parent=root
        o.location=(x,y,bank_height(x,y)-.12*size);o.scale=(size,size*rng.uniform(.75,1.3),size*rng.uniform(.40,.78))
        o.rotation_euler=(rng.uniform(-.25,.25),rng.uniform(-.2,.2),rng.uniform(0,math.tau));count+=1
    land=bpy.data.objects['AS_valley_landform'];mat=land.data.materials[0];bs=mat.node_tree.nodes.get('Principled BSDF')
    mix=bs.inputs['Base Color'].links[0].from_node
    if mix.type!='MIX_RGB' or abs(mix.inputs[0].default_value-.25)>1e-5:raise ValueError('Unexpected ground node')
    mix.inputs[0].default_value=.12
    ramp=mix.inputs[2].links[0].from_node;noise=ramp.inputs[0].links[0].from_node
    noise.inputs['Scale'].default_value=.32
    # Inactive debris keeps tiny valid triangles underground rather than
    # degenerate point faces. Preserve all active flight coordinates.
    from entrance189_groom import read_mdd,write_mdd,attach_cache
    debris=bpy.data.objects['MF196_hoof_ejected_pebbles'];mod=next(m for m in debris.modifiers if m.type=='MESH_CACHE');a=read_mdd(bpy.path.abspath(mod.filepath))
    from entrance196_build import prototype
    proto,_=prototype(np.random.default_rng(19604));nv=len(proto)
    def frames():
        for row in a:
            q=np.array(row,float).reshape(-1,nv,3);collapsed=np.max(np.ptp(q,axis=1),axis=1)<1e-8
            q[collapsed]+=proto[None]*.001
            yield q.reshape(-1,3).astype(np.float32)
    path=out/'debris.mdd';write_mdd(path,144,len(debris.data.vertices),frames());attach_cache(debris,path)
    caches=[]
    for ob in scene.objects:
        for m in ob.modifiers:
            if m.type=='MESH_CACHE':
                p=Path(bpy.path.abspath(m.filepath)).resolve();m.filepath=str(p)
                caches.append({'object':ob.name,'path':os.path.relpath(p,out),'sha256':base.digest(p),'start':m.frame_start})
    base.check_protected();bpy.context.preferences.filepaths.save_version=0
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'scene.blend'),compress=True);bpy.ops.file.make_paths_relative();bpy.ops.wm.save_as_mainfile(filepath=str(out/'scene.blend'),compress=True)
    (out/'result.json').write_text(json.dumps({'source_sha256':base.digest(source),'native_sha256':base.digest(out/'scene.blend'),'caches':caches,'rock_instances':count,'shared_rock_vertices':len(mesh.vertices),'visual_gate':'NOT_RUN','motion_unchanged_from':'entrance196-build02'},indent=2)+'\n')

if __name__=='__main__':main()
