"""Fixed, reversible terrain material authoring. No geometry or action edits."""
import hashlib,json,os,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
import wardrobe_motion178 as base
from entrance198_inspect import SOURCE_HASH
TEXTURE=ROOT/'.runtime/art-direction/series01-terrain198/painted-earth-v01.png'
TEXTURE_SHA='d39314320580d58e6a3a868bc47eb99b31c78cddd6f92416d918c846eead5cbd'
MATERIALS=('196 stony ochre ground','boulder_03','196 cool weathered boulder_03',
           'MF189 dusty gravel','MF188_dry_hoof_dust','MF189 continuous ochre dust')+tuple('196 weathered stone '+str(i) for i in range(5))

def validate(job):
    if job!={'operation':'build02'}:raise ValueError('Fixed terrain build only')
    source=base.BASE/'entrance196-particles40/scene.blend';out=base.BASE/'entrance198-build02'
    if out.exists() or base.digest(source)!=SOURCE_HASH or not TEXTURE.is_file() or base.digest(TEXTURE)!=TEXTURE_SHA:raise ValueError('Changed source/texture or existing output')
    return source,out

def fingerprint(scene):
    """Static geometry, topology, transforms, modifier structure, actions and camera/light state."""
    import bpy
    from worker import action_channels
    h=hashlib.sha256();objects=[]
    for m in sorted(bpy.data.meshes,key=lambda m:m.name):
        h.update(m.name.encode())
        for collection,prop,width,dtype in ((m.vertices,'co',3,np.float32),(m.loops,'vertex_index',1,np.int32),(m.polygons,'loop_total',1,np.int32)):
            a=np.empty(len(collection)*width,dtype=dtype);collection.foreach_get(prop,a);h.update(a.tobytes())
        if m.shape_keys:
            for block in m.shape_keys.key_blocks:
                a=np.empty(len(block.data)*3,dtype=np.float32);block.data.foreach_get('co',a);h.update(block.name.encode());h.update(a.tobytes())
    for o in sorted(scene.objects,key=lambda o:o.name):
        objects.append({'name':o.name,'type':o.type,'data':o.data.name if o.data else None,'parent':o.parent.name if o.parent else None,
                        'basis':[list(x) for x in o.matrix_basis],'hide_render':o.hide_render,
                        'modifiers':[(m.name,m.type,m.show_render,m.show_viewport) for m in o.modifiers]})
    actions=[{'name':a.name,'channels':[{'path':f.data_path,'index':f.array_index,'keys':[(list(k.co),list(k.handle_left),list(k.handle_right),k.interpolation) for k in f.keyframe_points]} for f in action_channels(a)]} for a in sorted(bpy.data.actions,key=lambda a:a.name)]
    cameras=[(c.name,c.type,c.lens,c.ortho_scale,c.clip_start,c.clip_end,c.shift_x,c.shift_y) for c in sorted(bpy.data.cameras,key=lambda c:c.name)]
    lights=[(x.name,x.type,x.energy,list(x.color)) for x in sorted(bpy.data.lights,key=lambda x:x.name)]
    return {'geometry':h.hexdigest(),'objects':hashlib.sha256(json.dumps(objects,sort_keys=True).encode()).hexdigest(),
            'actions':hashlib.sha256(json.dumps(actions,sort_keys=True).encode()).hexdigest(),
            'camera_light':hashlib.sha256(json.dumps([cameras,lights,scene.camera.name,scene.view_settings.view_transform,scene.view_settings.look,scene.view_settings.exposure,scene.view_settings.gamma],sort_keys=True).encode()).hexdigest()}

def ramp(nodes,links,socket,stops,label):
    r=nodes.new('ShaderNodeValToRGB');r.label=label;r.color_ramp.interpolation='EASE'
    for i,(p,c) in enumerate(stops):
        e=r.color_ramp.elements[i] if i<2 else r.color_ramp.elements.new(p);e.position=p;e.color=(*c,1)
    links.new(socket,r.inputs[0]);return r.outputs[0]

def image_sample(n,l,coord,image,scale,angle=0,box=False):
    mp=n.new('ShaderNodeMapping');mp.inputs['Scale'].default_value=(scale,scale,scale);mp.inputs['Rotation'].default_value[2]=angle
    l.new(coord,mp.inputs['Vector']);im=n.new('ShaderNodeTexImage');im.image=image;im.interpolation='Linear';im.extension='REPEAT'
    if box:im.projection='BOX';im.projection_blend=.22
    l.new(mp.outputs['Vector'],im.inputs[0]);return im.outputs['Color']

def ground(mat,image):
    import bpy
    n,l=mat.node_tree.nodes,mat.node_tree.links;bs=next(x for x in n if x.type=='BSDF_PRINCIPLED')
    tex=n.new('ShaderNodeTexCoord');tex.object=bpy.data.objects['AS_world_travel'];tex.label='198 geography-bound painted marks'
    a=image_sample(n,l,tex.outputs['Object'],image,1/72)
    b=image_sample(n,l,tex.outputs['Object'],image,1/43,.83)
    noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=.033;noise.inputs['Detail'].default_value=1;l.new(tex.outputs['Object'],noise.inputs[0])
    mix=n.new('ShaderNodeMixRGB');l.new(noise.outputs['Fac'],mix.inputs[0]);l.new(a,mix.inputs[1]);l.new(b,mix.inputs[2]);l.new(mix.outputs[0],bs.inputs['Base Color'])
    # Brush color carries the illustration; micro-relief must not turn it
    # into photographed granular sand. Preserve real contact lighting.
    for link in list(bs.inputs['Normal'].links):l.remove(link)
    bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.12;bump.inputs['Distance'].default_value=.025
    l.new(a,bump.inputs['Height']);l.new(bump.outputs[0],bs.inputs['Normal'])
    bs.inputs['Roughness'].default_value=.96;bs.inputs['Specular IOR Level'].default_value=.10
    out=next(x for x in n if x.type=='OUTPUT_MATERIAL' and x.is_active_output);l.new(bs.outputs[0],out.inputs['Surface'])

def stone(mat,image):
    n,l=mat.node_tree.nodes,mat.node_tree.links;bs=next(x for x in n if x.type=='BSDF_PRINCIPLED')
    tex=n.new('ShaderNodeTexCoord');paint=image_sample(n,l,tex.outputs['Generated'],image,1.7,.19,True)
    bw=n.new('ShaderNodeRGBToBW');l.new(paint,bw.inputs[0])
    light=ramp(n,l,bw.outputs[0],[(.08,(.055,.070,.085)),(.35,(.21,.22,.20)),(.60,(.46,.37,.23)),(.86,(.78,.65,.43))],'198 warm weathered stone brush planes')
    dark=ramp(n,l,bw.outputs[0],[(.08,(.018,.025,.040)),(.38,(.045,.065,.09)),(.66,(.12,.16,.20)),(.90,(.39,.36,.28))],'198 selective slate anchors')
    info=n.new('ShaderNodeObjectInfo');threshold=n.new('ShaderNodeMath');threshold.operation='GREATER_THAN';threshold.inputs[1].default_value=.72;l.new(info.outputs['Random'],threshold.inputs[0])
    mix=n.new('ShaderNodeMixRGB');l.new(threshold.outputs[0],mix.inputs[0]);l.new(light,mix.inputs[1]);l.new(dark,mix.inputs[2]);l.new(mix.outputs[0],bs.inputs['Base Color'])
    for key,val in (('Roughness',.94),('Metallic',0.),('Specular IOR Level',.10)):
        for link in list(bs.inputs[key].links):l.remove(link)
        bs.inputs[key].default_value=val
    for node in n:
        if node.type=='NORMAL_MAP':node.inputs['Strength'].default_value=.25

def main():
    import bpy
    job=json.loads(Path(sys.argv[sys.argv.index('--')+1]).read_text());source,out=validate(job)
    r=json.loads((source.parent/'result.json').read_text())
    for row in r['caches']:
        p=(source.parent/row['path']).resolve()
        if not p.is_relative_to(base.BASE.resolve()) or base.digest(p)!=row['sha256']:raise ValueError('Cache mismatch')
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False);scene=bpy.context.scene;scene.frame_set(217);base.check_protected()
    before=fingerprint(scene);out.mkdir();(out/'handler.py').write_bytes(Path(__file__).read_bytes())
    originals={name:bpy.data.materials[name] for name in MATERIALS};copies={m:m.copy() for m in originals.values()}
    assigned=set();changed=[]
    for ob in scene.objects:
        if not hasattr(ob.data,'materials') or ob.data in assigned:continue
        assigned.add(ob.data)
        for i,mat in enumerate(list(ob.data.materials)):
            if mat not in copies:continue
            # Inspected source owners must all be terrain/effects, never actors.
            owners=[o.name for o in scene.objects if o.data==ob.data]
            if not all(s.startswith(('MF196_','MF188_bank_stone_','MF188_dust_','MF189_roadside_','MF189_continuous_','AS_valley_')) for s in owners):raise ValueError('Material shared with non-environment owner')
            copies[mat].name='198 painted '+mat.name;ob.data.materials[i]=copies[mat];changed.append({'data':ob.data.name,'slot':i,'source':mat.name,'new':copies[mat].name,'owner_count':len(owners)})
    image=bpy.data.images.load(str(TEXTURE),check_existing=False);image.name='198 authored pale earth';image.pack()
    for original,mat in copies.items():
        if original.name=='196 stony ochre ground':ground(mat,image)
        elif original.name in ('MF188_dry_hoof_dust','MF189 continuous ochre dust'):
            for node in mat.node_tree.nodes:
                if node.type=='PRINCIPLED_VOLUME':
                    node.inputs['Color'].default_value=(.99,.94,.81,1);node.inputs['Emission Color'].default_value=(.78,.65,.44,1)
        else:stone(mat,image)
    after=fingerprint(scene)
    if after!=before:raise ValueError('Material-only scope changed structure/action')
    base.check_protected();caches=[]
    for ob in scene.objects:
        for m in ob.modifiers:
            if m.type=='MESH_CACHE':
                p=Path(bpy.path.abspath(m.filepath)).resolve();m.filepath=str(p);caches.append({'object':ob.name,'path':os.path.relpath(p,out),'sha256':base.digest(p),'start':m.frame_start})
    bpy.context.preferences.filepaths.save_version=0
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'scene.blend'),compress=True);bpy.ops.file.make_paths_relative();bpy.ops.wm.save_as_mainfile(filepath=str(out/'scene.blend'),compress=True)
    (out/'result.json').write_text(json.dumps({'source_sha256':SOURCE_HASH,'native_sha256':base.digest(out/'scene.blend'),'caches':caches,'fingerprint':before,
        'changed_material_slots':changed,'texture_sha256':base.digest(TEXTURE),'texture_path':str(TEXTURE.relative_to(ROOT)),'visual_gate':'NOT_RUN',
        'scope':'Environment materials only; preserved geometry, object transforms, complete action channels, camera/light state and17 existing caches'},indent=2)+'\n')

if __name__=='__main__':main()
