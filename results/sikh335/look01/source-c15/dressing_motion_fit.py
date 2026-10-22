"""Fixed dressing-only continuation of the accepted restrained facial baseline."""
import hashlib
import json
import math
from pathlib import Path
import shutil
import sys

ROOT=Path(__file__).resolve().parents[4]
BASE=ROOT/'.runtime/art-direction/series01-facebuilder-trial-01'
SOURCE=BASE/'face-surface-build-02/face-integrated.blend'
SOURCE_SHA='c7d119fe276d8198de3cd87bb2da46cfd6bbdeb580a62b34413afeb77edc57cf'
SELECTED=BASE/'dressing-motion-build-04/character-dressed.blend'
SELECTED_SHA='77fa1fad9da232a6af156f0f62b1a3fd994f4aa28e89011643ea74574e77526e'

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def validate(job):
    if not isinstance(job,dict) or set(job)!={'operation','candidate'}:
        raise ValueError('Exact structured operation/candidate required')
    if type(job['candidate']) is not int or (job['operation'],job['candidate']) not in (('inspect',0),('build',1),('build',2),('build',3),('build',4),('verify',4)):
        raise ValueError('Unsupported dressing operation')
    if SOURCE.is_symlink() or digest(SOURCE)!=SOURCE_SHA:raise ValueError('Pinned source changed')
    if job['operation']=='verify' and (SELECTED.is_symlink() or digest(SELECTED)!=SELECTED_SHA):raise ValueError('Selected source changed')
    out=BASE/f'dressing-motion-{job["operation"]}-{job["candidate"]:02}'
    if out.exists() or shutil.disk_usage(BASE).free<5_000_000_000:raise ValueError('Existing output or disk low')
    return out

def smooth(t):
    t=max(0.,min(1.,t));return t*t*(3-2*t)

def hairline(x,y):
    # Center-part hairline falls toward temples, safely above brows.
    return .92-.64*min(abs(x)/.94,1.)**1.4-.08*math.exp(-(x/.075)**2)-.40*smooth((y+.3)/.7)

def crown(candidate):
    import bpy,bmesh
    head=bpy.data.objects['FBHead'];dg=bpy.context.evaluated_depsgraph_get()
    mesh=bpy.data.meshes.new_from_object(head.evaluated_get(dg),preserve_all_data_layers=True,depsgraph=dg)
    bm=bmesh.new();bm.from_mesh(mesh)
    remove=[]
    for face in bm.faces:
        c=face.calc_center_median()
        if c.z<hairline(c.x,c.y)-(.10 if candidate>=2 else 0):remove.append(face)
    bmesh.ops.delete(bm,geom=remove,context='FACES');bm.normal_update()
    for v in bm.verts:v.co+=v.normal*.007
    bm.to_mesh(mesh);bm.free()
    ob=bpy.data.objects.new('MF_reference_crown_hair',mesh);bpy.context.scene.collection.objects.link(ob)
    ob.matrix_world=head.matrix_world.copy();mesh.materials.clear()
    # Reference scalp UV and source material: no painted change to accepted skin.
    for m in head.data.materials:mesh.materials.append(m.copy())
    if candidate>=2:
        alpha=mesh.attributes.new('MF_crown_edge_blend','FLOAT','POINT')
        for v in mesh.vertices:alpha.data[v.index].value=smooth((v.co.z-hairline(v.co.x,v.co.y)+.07)/.12)
        for m in mesh.materials:
            n,l=m.node_tree.nodes,m.node_tree.links;p=n.get('Principled BSDF')
            attribute=n.new('ShaderNodeAttribute');attribute.attribute_name=alpha.name
            l.new(attribute.outputs['Fac'],p.inputs['Alpha'])
    return len(mesh.vertices)

def fit_scarf(candidate):
    import bpy
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    body=bpy.data.objects['MF_continuous_head_neck'];bpy.context.view_layer.update()
    tree=BVHTree.FromObject(body,bpy.context.evaluated_depsgraph_get())
    scarf=bpy.data.objects['MF_layered_upper_scarf']
    # The old partial shrinkwrap pulls the neckline onto the revised shoulders
    # but leaves adjacent rows inside them. Fit the whole surface consistently.
    for m in list(scarf.modifiers):
        if m.type=='SHRINKWRAP':scarf.modifiers.remove(m)
    modified=0
    for v in scarf.data.vertices:
        p=scarf.matrix_world@v.co;x,y,z=p
        a=math.atan2(x,.22-y);front=max(0.,math.cos(a));t=(v.index%49)/48
        if candidate>=2:
            weight=smooth((t-.10)/.3)*smooth((1-t)/.15)
            p.z+=.09*math.sin(a+.3)*weight*front
            delta=.045*math.sin(t*math.pi*3+1.8*math.sin(a))*weight
            p.x+=math.sin(a)*delta;p.y-=math.cos(a)*delta
        if candidate>=3:
            shoulder=smooth((abs(p.x)-.95)/.45)
            p.x+=(1 if p.x>0 else -1)*.15*shoulder
            p.z+=.10*shoulder
        center=Vector((0,.10,p.z));direction=p-center;direction.z=0;direction.normalize()
        hit,normal,_,_=tree.ray_cast(center+direction*4,-direction,5)
        gap=.12 if candidate>=2 else .065
        if hit is not None and (p-center).dot(direction)<(hit-center).dot(direction)+gap:
            p=center+direction*((hit-center).dot(direction)+gap);modified+=1
        v.co=scarf.matrix_world.inverted()@p
    scarf.data.update()
    return modified

def hood_folds():
    import bpy
    hood=bpy.data.objects['MF_adapted_donor_hood']
    for v in hood.data.vertices:
        x,y,z=v.co
        # Broad supported hanging folds; no face-opening or crown displacement.
        weight=smooth((-.35-z)/.6)*smooth((z+4.5)/.6)
        a=math.atan2(x,y-.22);rear=smooth((y-.15)/.5)
        delta=.065*math.sin(a*7+.45*z)*weight*rear
        v.co.x+=math.sin(a)*delta;v.co.y+=math.cos(a)*delta
    hood.data.update()

def shoulder_underlayer():
    import bpy,bmesh
    # The under-tunic needs actual shoulder coverage beneath the loose scarf.
    # Extract on a copy only; keep all accepted skin vertices and shape keys.
    source=bpy.data.objects['MF_continuous_head_neck']
    mesh=bpy.data.meshes.new_from_object(source.evaluated_get(bpy.context.evaluated_depsgraph_get()))
    bm=bmesh.new();bm.from_mesh(mesh)
    bmesh.ops.delete(bm,geom=[f for f in bm.faces if f.calc_center_median().z>-.8],context='FACES')
    # Flatten the intended curved neckline temporarily so the cut is exact.
    def edge(x):return -1.80+.40*smooth((abs(x)-.5)/.9)
    for v in bm.verts:v.co.z-=edge(v.co.x)
    bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),plane_co=(0,0,0),plane_no=(0,0,1),clear_outer=True,dist=1e-6)
    for v in bm.verts:v.co.z+=edge(v.co.x)
    bm.normal_update()
    for v in bm.verts:v.co+=v.normal*.025
    bm.to_mesh(mesh);bm.free();mesh.materials.clear()
    mesh.materials.append(bpy.data.objects['MF_upper_tunic'].data.materials[0])
    for p in mesh.polygons:p.material_index=0;p.use_smooth=True
    ob=bpy.data.objects.new('MF_tunic_shoulder_underlayer',mesh);bpy.context.scene.collection.objects.link(ob)
    ob.matrix_world=source.matrix_world.copy()
    ob.modifiers.new('Underlayer fabric thickness','SOLIDIFY').thickness=.012

def protected():
    import bpy
    from neck_anatomy_review import signature
    names=('MF_continuous_head_neck','FBHead','MF_aimable_eye_Left','MF_aimable_eye_Right')
    return {name:signature(bpy.data.objects[name]) for name in names}

def verify(out):
    import bpy
    import numpy as np
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    from face_surface_integration import performance
    from hijab_donor import review
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE),load_ui=False,use_scripts=False)
    before=protected()
    bpy.ops.wm.open_mainfile(filepath=str(SELECTED),load_ui=False,use_scripts=False)
    assert protected()==before
    body=bpy.data.objects['MF_continuous_head_neck'];keys=list(body.data.shape_keys.key_blocks)[1:]
    original=np.array([list(v.co) for v in body.data.vertices])
    # Central face clearance only. Scalp shells deliberately sit on the scalp;
    # this is not an all-garment intersection or dynamics qualification.
    region=[v.index for v in body.data.vertices if abs(v.co.x)<.62 and -.75<v.co.z<.66 and v.co.y<-.50]
    vertices=[];faces=[];names=[]
    dg=bpy.context.evaluated_depsgraph_get()
    for ob in bpy.context.scene.objects:
        if ob.type!='MESH' or ob.hide_render or ob==body or ob.name.startswith('MF_aimable_eye'):continue
        evaluated=ob.evaluated_get(dg);mesh=evaluated.to_mesh();offset=len(vertices)
        vertices.extend(ob.matrix_world@v.co for v in mesh.vertices)
        faces.extend(tuple(offset+i for i in p.vertices) for p in mesh.polygons)
        names.append(ob.name);evaluated.to_mesh_clear()
    tree=BVHTree.FromPolygons(vertices,faces)
    def pose(values,gaze=0):
        for key in keys:key.value=values.get(key.name,0)
        for side in ('Left','Right'):bpy.data.objects['MF_aimable_eye_'+side].rotation_euler.z=gaze
        bpy.context.scene.frame_set(1);bpy.context.view_layer.update()
        ev=body.evaluated_get(bpy.context.evaluated_depsgraph_get())
        coords=np.array([list(v.co) for v in ev.data.vertices]);assert np.isfinite(coords).all()
        minimum=min(tree.find_nearest(body.matrix_world@Vector(coords[i]))[3] for i in region)
        return float(minimum),float(np.linalg.norm(coords-original,axis=1).max())
    samples=[]
    for t in sorted(set([i/6 for i in range(61)]+[1.44,3.5,6.,9.958333])):
        values,gaze=performance(t);distance,displacement=pose(values,gaze)
        samples.append({'t':t,'central_face_mesh_clearance':distance,'max_displacement':displacement})
    diagnostic={}
    for label,values in [('blink',{'eyeBlinkLeft':1,'eyeBlinkRight':1}),('smile',performance(6)[0]),('jaw',{'jawOpen':.2})]:
        diagnostic[label]=pose(values)
        review(bpy.context.scene,out,(0,-.1,-.35),4.0,((label,0),(label+'-oblique',-35)))
    pose({});assert protected()==before
    packed=all(bool(i.packed_file or i.packed_files) for i in bpy.data.images if i.source=='FILE')
    assert packed
    result={'source_sha256':SOURCE_SHA,'selected_sha256':SELECTED_SHA,'fresh_open_without_addon':True,
        'protected_geometry_shapes_uv_materials_eyes_exact':True,'all_file_images_packed':packed,
        'samples':samples,'diagnostic_poses':diagnostic,'region_vertex_count':len(region),
        'clearance_scope':'Central face vertices only, nearest evaluated visible dressing mesh surface; excludes fine CURVE fibers and full-head/garment collision certification',
        'dressing_meshes':names,'minimum_sampled_clearance':min(s['central_face_mesh_clearance'] for s in samples),
        'sources_unchanged':digest(SOURCE)==SOURCE_SHA and digest(SELECTED)==SELECTED_SHA,
        'handler_sha256':digest(Path(__file__))}
    (out/'result.json').write_text(json.dumps(result,indent=2))

def run(job):
    out=validate(job);out.mkdir()
    if job['operation']=='verify':verify(out);return
    import bpy
    from hijab_donor import review
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE),load_ui=False,use_scripts=False)
    before=protected()
    inventory=[]
    for ob in bpy.context.scene.objects:
        if ob.type not in ('MESH','CURVE'):continue
        inventory.append({'name':ob.name,'type':ob.type,'hidden':ob.hide_render,
            'vertices':len(ob.data.vertices) if ob.type=='MESH' else None,
            'materials':[m.name for m in ob.data.materials],
            'bounds':[list(v) for v in ob.bound_box],
            'modifiers':[(m.name,m.type) for m in ob.modifiers]})
    (out/'inventory.json').write_text(json.dumps(inventory,indent=2))
    changes={}
    if job['operation']=='build':
        changes={'crown_vertices':crown(job['candidate']),'scarf_fitted_vertices':fit_scarf(2 if job['candidate']==4 else job['candidate'])}
        if job['candidate']>=3:hood_folds()
        if job['candidate']==4:shoulder_underlayer()
        assert protected()==before
        bpy.ops.wm.save_as_mainfile(filepath=str(out/'character-dressed.blend'))
    review(bpy.context.scene,out,(0,-.1,-1.40),6.8,(('front',0),('left',-45),('right',45),('back',180)))
    assert protected()==before
    (out/'result.json').write_text(json.dumps({'source_sha256':SOURCE_SHA,'handler_sha256':digest(Path(__file__)),
        'protected':before,'protected_unchanged':True,'source_unchanged':digest(SOURCE)==SOURCE_SHA,'changes':changes,
        'native_sha256':digest(out/'character-dressed.blend') if job['operation']=='build' else None},indent=2))

if __name__=='__main__':
    sys.path.insert(0,str(Path(__file__).resolve().parent))
    args=sys.argv[sys.argv.index('--')+1:]
    if len(args)!=1:raise ValueError('One structured job required')
    run(json.loads(Path(args[0]).read_text()))
