"""Reviewed structured local eye/mouth integration on a pinned derivative."""
import hashlib
import json
import math
from pathlib import Path
import shutil
import sys

ROOT=Path(__file__).resolve().parents[4]
BASE=ROOT/'.runtime/art-direction/series01-facebuilder-trial-01'
SOURCE=BASE/'face-performance-transfer-02/face-readiness.blend'
SOURCE_SHA='747043d68620efc2f956bf0485a827e884d3f47cce2ecaed3ebfafe927288902'
INTEGRATED=BASE/'face-surface-build-02/face-integrated.blend'
INTEGRATED_SHA='c7d119fe276d8198de3cd87bb2da46cfd6bbdeb580a62b34413afeb77edc57cf'


def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def validate(job):
    if not isinstance(job,dict) or set(job)!={'operation','candidate'}:
        raise ValueError('Exact operation/candidate required')
    if (job['operation'],job['candidate']) not in (('inspect',1),('build',1),('build',2),('audit',1),('verify',2),('motion',2),('reopen',2)) or type(job['candidate']) is not int:
        raise ValueError('Unsupported integration operation')
    if SOURCE.is_symlink() or digest(SOURCE)!=SOURCE_SHA:raise ValueError('Source changed')
    if job['operation'] in ('verify','motion') and (INTEGRATED.is_symlink() or digest(INTEGRATED)!=INTEGRATED_SHA):raise ValueError('Integrated source changed')
    out=BASE/f'face-surface-{job["operation"]}-{job["candidate"]:02}'
    if out.exists() or shutil.disk_usage(BASE).free<5_000_000_000:raise ValueError('Output exists or disk low')
    return out


def reopen(out):
    import bpy
    import numpy as np
    native=BASE/'face-surface-motion-02/face-acting.blend'
    sha='2f213e15c9d03ae0ae30f1a8c62c2df3a04e8d108d601a86fa6e2404d8b06a31'
    if native.is_symlink() or digest(native)!=sha:raise ValueError('Acting native changed')
    bpy.ops.wm.open_mainfile(filepath=str(native),load_ui=False,use_scripts=False)
    ob=bpy.data.objects['MF_continuous_head_neck'];reference=np.array([tuple(v.co) for v in ob.data.vertices])
    snapshots=[]
    for frame in (1,35,84,144,240):
        bpy.context.scene.frame_set(frame);bpy.context.view_layer.update();values,gaze=performance((frame-1)/24)
        error=max(abs(k.value-values.get(k.name,0)) for k in list(ob.data.shape_keys.key_blocks)[1:])
        eye_error=max(abs(bpy.data.objects['MF_aimable_eye_'+side].rotation_euler.z-gaze) for side in ('Left','Right'))
        drivers=[float(ob.data.materials[0].node_tree.path_resolve(d.data_path)) for d in ob.data.materials[0].node_tree.animation_data.drivers]
        assert error<1e-6 and eye_error<1e-6 and all(abs(v-values['eyeBlinkLeft'])<1e-6 for v in drivers)
        evaluated=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());positions=np.array([tuple(v.co) for v in evaluated.data.vertices])
        if frame in (1,240):assert np.array_equal(reference,positions)
        snapshots.append({'frame':frame,'control_max_error':error,'eye_max_error':eye_error,'blink_drivers':drivers})
    result={'native_sha256':sha,'fresh_open_without_addon':True,'fixed_keyframes_and_drivers_reproduced':True,
            'first_last_neutral_exact':True,'snapshots':snapshots,'native_unchanged':digest(native)==sha,
            'all_images_packed':all(bool(im.packed_file or im.packed_files) for im in bpy.data.images if im.source=='FILE')}
    (out/'result.json').write_text(json.dumps(result,indent=2))


def mesh_authority(ob,uv_names):
    return {'vertices':[[float(c) for c in v.co] for v in ob.data.vertices],
            'faces':[list(p.vertices) for p in ob.data.polygons],
            'uv':{name:[list(d.uv) for d in ob.data.uv_layers[name].data] for name in uv_names},
            'transform':[list(r) for r in ob.matrix_world]}


def verify(out):
    import bpy
    import numpy as np
    from hijab_donor import review
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE),load_ui=False,use_scripts=False)
    original=bpy.data.objects['MF_continuous_head_neck'];uv_names=list(original.data.uv_layers.keys())
    original_state=mesh_authority(original,uv_names)
    bpy.ops.wm.open_mainfile(filepath=str(INTEGRATED),load_ui=False,use_scripts=False)
    ob=bpy.data.objects['MF_continuous_head_neck']
    record={'source_sha256':SOURCE_SHA,'integrated_sha256':INTEGRATED_SHA,'fresh_open':True,
            'original_geometry_uvs_transform_exact':mesh_authority(ob,uv_names)==original_state,
            'all_expression_controls_zero':all(k.value==0 for k in list(ob.data.shape_keys.key_blocks)[1:]),
            'all_images_packed':all(bool(im.packed_file or im.packed_files) for im in bpy.data.images if im.source=='FILE')}
    assert record['original_geometry_uvs_transform_exact'] and record['all_expression_controls_zero'] and record['all_images_packed']
    for o in bpy.context.scene.objects:
        if o.type in ('MESH','CURVE'):o.hide_render=o!=ob and not o.name.startswith('MF_aimable_eye_')
    review(bpy.context.scene,out,(0,-.1,.1),2.7,(('neutral',0),('neutral-oblique',-35)))
    for name in ('eyeBlinkLeft','eyeBlinkRight'):ob.data.shape_keys.key_blocks[name].value=1
    bpy.context.scene.frame_set(1)
    record['blink_driver_values']=[float(ob.data.materials[0].node_tree.path_resolve(d.data_path)) for d in ob.data.materials[0].node_tree.animation_data.drivers]
    assert record['blink_driver_values']==[1.,1.]
    review(bpy.context.scene,out,(0,-.1,.1),2.7,(('blink-oblique',-35),))
    # Visibility diagnostic: white emissive eyeballs, black face, transparent
    # replaced caps unchanged. No recoloring is saved to the native asset.
    def emission(name,color):
        m=bpy.data.materials.new(name);m.use_nodes=True;n=m.node_tree.nodes;n.clear()
        e=n.new('ShaderNodeEmission');e.inputs[0].default_value=(*color,1)
        target=n.new('ShaderNodeOutputMaterial');m.node_tree.links.new(e.outputs[0],target.inputs[0]);return m
    black=emission('MF_mask_face',(0,0,0));white=emission('MF_mask_eye',(1,1,1))
    ob.data.materials[0]=black;ob.data.materials[2]=black
    for side in ('Left','Right'):bpy.data.objects['MF_aimable_eye_'+side].data.materials[0]=white
    visibility={}
    for label,value in (('open',0),('closed',1)):
        for name in ('eyeBlinkLeft','eyeBlinkRight'):ob.data.shape_keys.key_blocks[name].value=value
        bpy.context.scene.frame_set(1)
        review(bpy.context.scene,out,(0,-.1,.1),2.7,((label+'-eye-mask',0),))
        im=bpy.data.images.load(str(out/(label+'-eye-mask.png')),check_existing=False)
        pixels=np.empty(len(im.pixels),dtype=np.float32);im.pixels.foreach_get(pixels)
        visibility[label]=int(np.all(pixels.reshape(-1,4)[:,:3]>.95,axis=1).sum());bpy.data.images.remove(im)
    record['eye_visibility_pixels']=visibility
    record['full_blink_eye_occlusion']=visibility['open']>100 and visibility['closed']==0
    for key in list(ob.data.shape_keys.key_blocks)[1:]:key.value=0
    record['neutral_return_exact']=mesh_authority(ob,uv_names)==original_state
    record['sources_unchanged']=digest(SOURCE)==SOURCE_SHA and digest(INTEGRATED)==INTEGRATED_SHA
    (out/'result.json').write_text(json.dumps(record,indent=2))


def envelope(t,a,b,c,d):
    if t<a or t>d:return 0.
    if t<b:return smooth((t-a)/(b-a))
    if t<=c:return 1.
    return 1.-smooth((t-c)/(d-c))


def performance(t):
    blink=envelope(t,1.33,1.42,1.46,1.58)
    skeptical=envelope(t,2.5,3.1,4.1,4.8)
    smile=envelope(t,4.7,5.7,7.3,8.8)
    gaze=envelope(t,1.2,1.6,7.8,9.3)
    return {'eyeBlinkLeft':blink,'eyeBlinkRight':blink,
            'browOuterUpLeft':.23*skeptical,'browInnerUp':.035*skeptical,
            'mouthPressLeft':.07*skeptical,'mouthPressRight':.07*skeptical,
            'mouthSmileLeft':.28*smile,'mouthSmileRight':.28*smile,
            'cheekSquintLeft':.13*smile,'cheekSquintRight':.13*smile,
            'eyeSquintLeft':.025*gaze,'eyeSquintRight':.025*gaze},math.radians(5)*gaze


def motion(out):
    import bpy
    import numpy as np
    from mathutils import Vector
    from matched_face_review import rotate_z
    proof=json.loads((BASE/'face-surface-verify-02/result.json').read_text())
    if not proof['full_blink_eye_occlusion']:raise ValueError('Eye occlusion prerequisite failed')
    bpy.ops.wm.open_mainfile(filepath=str(INTEGRATED),load_ui=False,use_scripts=False)
    ob=bpy.data.objects['MF_continuous_head_neck'];keys=list(ob.data.shape_keys.key_blocks)[1:]
    eyes=[bpy.data.objects['MF_aimable_eye_'+side] for side in ('Left','Right')]
    scene=bpy.context.scene;scene.render.fps=24;scene.frame_start=1;scene.frame_end=240
    reference=np.array([tuple(v.co) for v in ob.data.vertices])
    samples=[]
    for frame in range(1,241):
        values,gaze=performance((frame-1)/24)
        for key in keys:
            key.value=values.get(key.name,0.);key.keyframe_insert(data_path='value',frame=frame)
        for eye in eyes:
            eye.rotation_euler.z=gaze;eye.keyframe_insert(data_path='rotation_euler',index=2,frame=frame)
    # Scene motion is baked into explicit trusted native curves, no callbacks.
    for frame in range(1,241):
        scene.frame_set(frame);bpy.context.view_layer.update()
        evaluated=ob.evaluated_get(bpy.context.evaluated_depsgraph_get())
        positions=np.array([tuple(v.co) for v in evaluated.data.vertices])
        assert len(positions)==len(reference) and np.isfinite(positions).all()
        samples.append({'frame':frame,'max_displacement':float(np.linalg.norm(positions-reference,axis=1).max()),
                        'blink':ob.data.shape_keys.key_blocks['eyeBlinkLeft'].value,'gaze':eyes[0].rotation_euler.z})
    assert samples[0]['max_displacement']==0 and samples[-1]['max_displacement']==0
    for o in scene.objects:
        if o.type in ('MESH','CURVE'):o.hide_render=o!=ob and o not in eyes
        if o.type=='LIGHT':o.hide_render=True
    target=Vector((0,-.1,.1))
    data=bpy.data.cameras.new('MF_facial_acting_review');cam=bpy.data.objects.new(data.name,data);scene.collection.objects.link(cam)
    data.type='ORTHO';data.ortho_scale=2.7;scene.camera=cam
    lights=[]
    for sign in (-1,1):
        ld=bpy.data.lights.new('MF_facial_acting_softbox','AREA');ld.energy=300;ld.shape='DISK';ld.size=5
        light=bpy.data.objects.new(ld.name,ld);scene.collection.objects.link(light);lights.append((light,(sign*3,-4,3)))
    scene.world=bpy.data.worlds.new('MF_facial_acting_world');scene.world.use_nodes=True
    scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.12,.12,.12,1)
    scene.render.engine='CYCLES';scene.cycles.samples=12;scene.cycles.seed=0;scene.cycles.use_animated_seed=False
    scene.render.resolution_x=384;scene.render.resolution_y=480;scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG';scene.render.film_transparent=False
    def angle(degrees):
        cam.location=target+Vector(rotate_z((0,-10,0),degrees));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
        for light,offset in lights:
            light.location=target+Vector(rotate_z(offset,degrees));light.rotation_euler=(target-light.location).to_track_quat('-Z','Y').to_euler()
    angle(0);scene.frame_set(1)
    native=out/'face-acting.blend';bpy.ops.wm.save_as_mainfile(filepath=str(native))
    result={'integrated_sha256':INTEGRATED_SHA,'native_sha256':digest(native),'handler_sha256':digest(Path(__file__)),
            'fps_native':24,'fps_preview':12,'duration_seconds':10,'all_240_frames_finite':True,
            'neutral_first_last_exact':True,'samples':samples,'rendering':'IN_PROGRESS','director_accepted':False}
    (out/'result.json').write_text(json.dumps(result,indent=2))
    for label,degrees in (('front',0),('oblique',-35)):
        directory=out/label;directory.mkdir();angle(degrees)
        for index,frame in enumerate(range(1,241,2)):
            scene.frame_set(frame);scene.render.filepath=str(directory/f'{index:04}.png');bpy.ops.render.render(write_still=True)
    result['rendering']='COMPLETE';result['frames_per_view']=120
    (out/'result.json').write_text(json.dumps(result,indent=2))


def audit(out):
    import bpy
    bpy.ops.wm.open_mainfile(filepath=str(BASE/'face-surface-build-01/face-integrated.blend'),load_ui=False,use_scripts=False)
    ob=bpy.data.objects['MF_continuous_head_neck'];mat=ob.data.materials[0]
    record={}
    for value in (0,1):
        for name in ('eyeBlinkLeft','eyeBlinkRight'):ob.data.shape_keys.key_blocks[name].value=value
        bpy.context.scene.frame_set(1);bpy.context.view_layer.update()
        record[str(value)]={'drivers':[{'path':d.data_path,'valid':d.driver.is_valid,'value':mat.node_tree.path_resolve(d.data_path)} for d in mat.node_tree.animation_data.drivers]}
    pixels=list(mat.node_tree.nodes['Image Texture'].image.pixels);width,height=mat.node_tree.nodes['Image Texture'].image.size
    for side in ('Left','Right'):
        layer=ob.data.uv_layers['MF_closed_lid_'+side];attr=ob.data.attributes['MF_lid_reconstruction_'+side]
        samples=[]
        for loop in ob.data.loops:
            if attr.data[loop.vertex_index].value>.95:
                u,v=layer.data[loop.index].uv;i=4*(min(height-1,max(0,int(v*height)))*width+min(width-1,max(0,int(u*width))))
                if len(samples)<20:samples.append({'co':list(ob.data.vertices[loop.vertex_index].co),'uv':[u,v],'color':pixels[i:i+3]})
        record[side]=samples
    (out/'result.json').write_text(json.dumps(record,indent=2))


def smooth(t):
    t=max(0.,min(1.,t));return t*t*(3-2*t)


def sphere_fit(points):
    import numpy as np
    q=np.asarray(points,dtype=float)
    if len(q)<20:raise ValueError('Insufficient eye surface samples')
    c=np.linalg.lstsq(np.column_stack((2*q,np.ones(len(q)))),np.sum(q*q,axis=1),rcond=None)[0]
    radius=float((c[3]+np.sum(c[:3]**2))**.5)
    error=float(np.sqrt(np.mean((np.linalg.norm(q-c[:3],axis=1)-radius)**2)))
    if not .10<radius<.19 or error>.003:raise ValueError('Eye sphere fit outside bounds')
    return c[:3],radius,error


def attach_blink_driver(socket,ob,key):
    # Fixed, simple native expression only; no runtime Python or scripted callbacks.
    driver=socket.driver_add('default_value').driver
    driver.type='AVERAGE';var=driver.variables.new();var.name='blink';var.type='SINGLE_PROP'
    var.targets[0].id_type='KEY';var.targets[0].id=ob.data.shape_keys
    var.targets[0].data_path=f'key_blocks["{key}"].value'


def build(out,candidate):
    import bpy
    import numpy as np
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    from mathutils.geometry import barycentric_transform
    from bust_skin_review import protected_state
    from face_performance_readiness import neutral_geometry
    from hijab_donor import review
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE),load_ui=False,use_scripts=False)
    ob=bpy.data.objects['MF_continuous_head_neck'];mesh=ob.data
    before=neutral_geometry(ob);other=protected_state()['other_objects']
    coords=np.array([tuple(v.co) for v in mesh.vertices],dtype=np.float32)
    mesh.calc_loop_triangles()
    mat=mesh.materials[0].copy();mesh.materials[0]=mat
    n,links=mat.node_tree.nodes,mat.node_tree.links
    original_color=n['Principled BSDF'].inputs['Base Color'].links[0].from_socket
    # Keep all source vertex/shape arrays intact. Only embedded inner-cap faces
    # become transparent; independently rotating full eye spheres replace them.
    clear=bpy.data.materials.new('MF_internal_eye_cap_replaced');clear.use_nodes=True
    cn=clear.node_tree.nodes;cn.clear();tr=cn.new('ShaderNodeBsdfTransparent');output=cn.new('ShaderNodeOutputMaterial')
    clear.node_tree.links.new(tr.outputs[0],output.inputs['Surface']);mesh.materials.append(clear)
    cap_material_index=len(mesh.materials)-1
    record={'source_sha256':SOURCE_SHA,'handler_sha256':digest(Path(__file__)), 'eyes':[]}
    for sign,side,keyname in ((1,'Left','eyeBlinkLeft'),(-1,'Right','eyeBlinkRight')):
        blink=np.array([tuple(p.co) for p in mesh.shape_keys.key_blocks[keyname].data])-coords
        stationary=np.linalg.norm(blink,axis=1)<1e-5
        fit=(sign*coords[:,0]>.24)&(sign*coords[:,0]<.41)&(coords[:,2]>.29)&(coords[:,2]<.34)&(coords[:,1]<-.7)&stationary
        center,radius,error=sphere_fit(coords[fit])
        cap=(np.abs(np.linalg.norm(coords-center,axis=1)-radius)<.0025)&stationary
        polygons=[p.index for p in mesh.polygons if all(cap[i] for i in p.vertices)]
        if not 50<len(polygons)<250:raise ValueError('Eye cap extent outside bounds')
        triangles=[t for t in mesh.loop_triangles if t.polygon_index in set(polygons)]
        triangle_indices=[tuple(t.vertices) for t in triangles]
        tree=BVHTree.FromPolygons([Vector(v) for v in coords],triangle_indices,all_triangles=True)
        bpy.ops.mesh.primitive_uv_sphere_add(segments=64,ring_count=32,radius=radius,location=Vector(center))
        eye=bpy.context.object;eye.name='MF_aimable_eye_'+side
        eye.data.materials.append(mat.copy())
        for p in eye.data.polygons:p.use_smooth=True
        # Map the original illustrated eye color onto the fitted sphere. Stable
        # local UV/rest data rotates with it; original face is not repainted.
        samples=[]
        for v in eye.data.vertices:
            co=v.co+Vector(center);hit,normal,idx,distance=tree.find_nearest(co)
            triangle=triangles[idx]
            samples.append((triangle,hit))
        for layer in mesh.uv_layers:
            dest=eye.data.uv_layers.get(layer.name) or eye.data.uv_layers.new(name=layer.name)
            for loop in eye.data.loops:
                triangle,hit=samples[loop.vertex_index]
                abc=[Vector(coords[i]) for i in triangle.vertices]
                uv=[Vector((*layer.data[i].uv,0)) for i in triangle.loops]
                dest.data[loop.index].uv=barycentric_transform(hit,*abc,*uv).xy
        eye.data.uv_layers.active=eye.data.uv_layers['UVMap']
        for attr in mesh.attributes:
            if attr.domain=='POINT' and attr.data_type=='FLOAT':
                dest=eye.data.attributes.new(attr.name,'FLOAT','POINT')
                for i,(triangle,hit) in enumerate(samples):
                    abc=[Vector(coords[j]) for j in triangle.vertices]
                    vals=[Vector((attr.data[j].value,0,0)) for j in triangle.vertices]
                    dest.data[i].value=barycentric_transform(hit,*abc,*vals).x
        rest=eye.data.attributes.new('MF_performance_rest_position','FLOAT_VECTOR','POINT')
        for v,d in zip(eye.data.vertices,rest.data):d.vector=v.co+Vector(center)
        for i in polygons:mesh.polygons[i].material_index=cap_material_index
        record['eyes'].append({'side':side,'center':center.tolist(),'radius':radius,'fit_rms':error,'replaced_face_indices':polygons})
        # Reconstruct only hidden lid skin from an adjacent upper-lid sample.
        # Animated blend is zero at accepted neutral and tied to native blink.
        layer=mesh.uv_layers.new(name='MF_closed_lid_'+side)
        source_uv=mesh.uv_layers['UVMap']
        fulltree=BVHTree.FromPolygons([Vector(v) for v in coords],[tuple(t.vertices) for t in mesh.loop_triangles],all_triangles=True)
        alltri=list(mesh.loop_triangles)
        weights=[];sampleuv={}
        for i,v in enumerate(coords):
            weight=smooth((-float(blink[i,2])-.003)/.025) if sign*v[0]>0 and v[1]<-.6 and .15<v[2]<.55 else 0.
            weights.append(weight)
            if weight:
                point=Vector(v);point.z=(.14+.30*(float(v[2])-.33)) if candidate>=2 else float(v[2])+.12
                hit,normal,idx,dist=fulltree.find_nearest(point);t=alltri[idx]
                sampleuv[i]=barycentric_transform(hit,*[Vector(coords[j]) for j in t.vertices],*[Vector((*source_uv.data[j].uv,0)) for j in t.loops]).xy
        for loop,d in zip(mesh.loops,layer.data):d.uv=sampleuv.get(loop.vertex_index,source_uv.data[loop.index].uv)
        attr=mesh.attributes.new('MF_lid_reconstruction_'+side,'FLOAT','POINT')
        for d,w in zip(attr.data,weights):d.value=w
        if candidate>=2:
            corrected=0
            shape=mesh.shape_keys.key_blocks[keyname]
            for i,w in enumerate(weights):
                if w>.05:
                    p=shape.data[i].co
                    disk=radius*radius-(p.x-center[0])**2-(p.z-center[2])**2
                    if disk>0:
                        surface_y=center[1]-math.sqrt(disk)-.003
                        if p.y>surface_y:p.y=surface_y;corrected+=1
            record['eyes'][-1]['blink_surface_corrective_vertices']=corrected
        uvnode=n.new('ShaderNodeUVMap');uvnode.uv_map=layer.name
        texture=n.new('ShaderNodeTexImage');texture.image=n['Image Texture'].image
        links.new(uvnode.outputs[0],texture.inputs['Vector'])
        mask=n.new('ShaderNodeAttribute');mask.attribute_name=attr.name
        multiply=n.new('ShaderNodeMath');multiply.operation='MULTIPLY';links.new(mask.outputs['Fac'],multiply.inputs[0])
        attach_blink_driver(multiply.inputs[1],ob,keyname)
        mix=n.new('ShaderNodeMixRGB');links.new(multiply.outputs[0],mix.inputs[0]);links.new(original_color,mix.inputs[1]);links.new(texture.outputs['Color'],mix.inputs[2]);original_color=mix.outputs[0]
    links.new(original_color,n['Principled BSDF'].inputs['Base Color'])
    mesh.uv_layers.active=mesh.uv_layers['UVMap']
    # Dark matte mouth lining on recessed inner-cap faces only; retain exterior
    # lip contour. Detailed teeth/tongue remain outside this small-open proof.
    oral=bpy.data.materials.new('MF_basic_mouth_lining');oral.use_nodes=True
    p=oral.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(.018,.0035,.004,1)
    p.inputs['Roughness'].default_value=.9;mesh.materials.append(oral);oral_index=len(mesh.materials)-1
    mouth=[]
    jaw_preview=coords+.2*(np.array([tuple(v.co) for v in mesh.shape_keys.key_blocks['jawOpen'].data])-coords)
    for p in mesh.polygons:
        x,y,z=p.center
        if candidate>=2:
            selected=False
            if abs(x)<.3 and -.38<z<-.22 and y<-.7:
                f=list(p.vertices);a=coords[f];b=jaw_preview[f]
                area0=sum(np.linalg.norm(np.cross(a[j]-a[0],a[j+1]-a[0])) for j in range(1,len(f)-1))
                area1=sum(np.linalg.norm(np.cross(b[j]-b[0],b[j+1]-b[0])) for j in range(1,len(f)-1))
                selected=area1/max(area0,1e-10)>3
        else:selected=(x/.245)**2+((z+.300)/.034)**2<1 and y> -1.14 and y<-.85
        if selected:
            p.material_index=oral_index;mouth.append(p.index)
    record['mouth_lining_face_indices']=mouth
    # Smooth the displacement field across the upper neck; never move neutral.
    jaw=mesh.shape_keys.key_blocks['jawOpen']
    delta=np.array([tuple(v.co) for v in jaw.data])-coords
    edges=np.array([tuple(e.vertices) for e in mesh.edges]);a,b=edges.T
    degree=np.bincount(edges.ravel(),minlength=len(coords))
    band=(coords[:,2]<-.67)&(coords[:,2]>-1.18)
    for _ in range(100):
        acc=np.zeros_like(delta);np.add.at(acc,a,delta[b]);np.add.at(acc,b,delta[a])
        delta[band]=.35*delta[band]+.65*(acc/np.maximum(1,degree[:,None]))[band]
    jaw.data.foreach_set('co',(coords+delta).astype(np.float32).ravel())
    record['jaw_corrective_vertices']=int(band.sum())
    record['neutral_vertices_exact']=all(tuple(v.co)==tuple(coords[v.index]) for v in mesh.vertices)
    current_other=protected_state()['other_objects']
    record['other_existing_objects_unchanged']=all(current_other.get(k)==v for k,v in other.items())
    assert record['neutral_vertices_exact'] and record['other_existing_objects_unchanged']
    native=out/'face-integrated.blend';bpy.ops.wm.save_as_mainfile(filepath=str(native));record['native_sha256']=digest(native)
    (out/'result.json').write_text(json.dumps(record,indent=2))
    for o in bpy.context.scene.objects:
        if o.type in ('MESH','CURVE'):o.hide_render=o!=ob and not o.name.startswith('MF_aimable_eye_')
    poses={'neutral':{},'half-blink':{'eyeBlinkLeft':.5,'eyeBlinkRight':.5},'blink':{'eyeBlinkLeft':1.,'eyeBlinkRight':1.},'jaw':{'jawOpen':.2}}
    for label,values in poses.items():
        for key in list(mesh.shape_keys.key_blocks)[1:]:key.value=values.get(key.name,0.)
        bpy.context.view_layer.update()
        review(bpy.context.scene,out,(0,-.1,.1),2.7,((label,0),))
    for key in list(mesh.shape_keys.key_blocks)[1:]:key.value=0
    for side in ('Left','Right'):bpy.data.objects['MF_aimable_eye_'+side].rotation_euler.z=math.radians(5)
    review(bpy.context.scene,out,(0,-.1,.1),2.7,(('gaze',0),('gaze-oblique',-35)))
    assert digest(SOURCE)==SOURCE_SHA


def inspect(out):
    import bpy
    import numpy as np
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE),load_ui=False,use_scripts=False)
    ob=bpy.data.objects['MF_continuous_head_neck'];mesh=ob.data
    coords=np.array([tuple(v.co) for v in mesh.vertices],dtype=np.float32)
    keys={key.name:np.array([tuple(v.co) for v in key.data],dtype=np.float32) for key in mesh.shape_keys.key_blocks}
    np.savez_compressed(out/'surface.npz',vertices=coords,edges=np.array([list(e.vertices) for e in mesh.edges]),
        loops=np.array([l.vertex_index for l in mesh.loops]),uv=np.array([list(d.uv) for d in mesh.uv_layers['UVMap'].data]),**keys)
    (out/'polygons.json').write_text(json.dumps([list(p.vertices) for p in mesh.polygons]))
    region=[{'id':v.index,'co':list(v.co),'normal':list(v.normal)} for v in mesh.vertices
            if .15<v.co.x<.7 and .15<v.co.z<.6 and v.co.y<-.4]
    (out/'eye-region.json').write_text(json.dumps(region))
    (out/'result.json').write_text(json.dumps({'source_sha256':SOURCE_SHA,'handler_sha256':digest(Path(__file__)),
        'snapshot_sha256':digest(out/'surface.npz'),'vertices':len(coords),'eye_region_vertices':len(region)},indent=2))


def run(job):
    out=validate(job);out.mkdir()
    if job['operation']=='inspect':inspect(out)
    elif job['operation']=='audit':audit(out)
    elif job['operation']=='verify':verify(out)
    elif job['operation']=='motion':motion(out)
    elif job['operation']=='reopen':reopen(out)
    else:build(out,job['candidate'])


if __name__=='__main__':
    sys.path.insert(0,str(Path(__file__).resolve().parent))
    args=sys.argv[sys.argv.index('--')+1:]
    if len(args)!=1:raise ValueError('One structured job required')
    run(json.loads(Path(args[0]).read_text()))
