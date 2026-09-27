"""Pinned, data-only first fit of the acquired hair donor. No external scripts."""
import hashlib
import json
from pathlib import Path
import sys
import shutil

ROOT=Path(__file__).resolve().parents[4]
ASSET=ROOT/'.runtime/assets/series01-dressing-source/o4saken-long01'
BASE=ROOT/'.runtime/art-direction/series01-facebuilder-trial-01'
AUTHORED=ROOT/'.runtime/assets/series01-hair-donor22/lady-hippy'
AUTHORED_PINS={'elvs_ladies_hippyhair1.obj':'9e1ceaa40b62e40237e758611876b90f6323f2c5893acd508910bff2d31e4b28','hairtex1.png':'e6857e7bfbc5eb9f36622b5a734f1c421bf2a26b2105e5db8e2c44b1ad068478','hairnormals.png':'5e1700f59660b964ffbfdfbe9ef83ab62097f42d59bad9d2bbd9fe4638cca59a'}
DEMO=ROOT/'.runtime/assets/series01-hair-donor22/bystedt-hair-demo.blend'
DEMO_SHA='1ad6202095c1793678fee7d69a7e9f8b5fdb6e5c293d300eb1062d2d437e8d48'


def validate_demo(job):
    if job not in ({'operation':'inspect-demo'},{'operation':'fit-demo'}):raise ValueError('Fixed demo operations only')
    if DEMO.is_symlink() or hashlib.sha256(DEMO.read_bytes()).hexdigest()!=DEMO_SHA:raise ValueError('Demo changed')
    out=BASE/('authored-donor22-demo-inspection' if job['operation']=='inspect-demo' else 'authored-donor22-03')
    if out.exists() or out.is_symlink() or out.resolve().parent!=BASE.resolve():raise ValueError('Output exists or escapes')
    if job['operation']=='fit-demo':
        validate_authored({'operation':'authored-fit','candidate':3})
    return out


def inspect_demo(job):
    out=validate_demo(job)
    import bpy
    out.mkdir();shutil.copyfile(Path(__file__),out/'handler-source.py')
    bpy.ops.wm.open_mainfile(filepath=str(DEMO),load_ui=False,use_scripts=False)
    records=[]
    for o in bpy.data.objects:
        r={'name':o.name,'type':o.type,'location':list(o.location),'scale':list(o.scale),'rotation':list(o.rotation_euler),'collections':[c.name for c in o.users_collection],'modifiers':[(m.name,m.type) for m in o.modifiers],'materials':[m.name for m in getattr(o.data,'materials',[]) if m]}
        if o.type=='CURVES':
            r.update(curves=len(o.data.curves),points=len(o.data.points),surface=o.data.surface.name if o.data.surface else None)
        if o.type in ('MESH','CURVES'):
            points=[v.co if o.type=='MESH' else v.position for v in (o.data.vertices if o.type=='MESH' else o.data.points)]
            r['bounds']=[[min(p[i] for p in points) for i in range(3)],[max(p[i] for p in points) for i in range(3)]] if points else None
        records.append(r)
    texts={t.name:t.as_string()[:16000] for t in bpy.data.texts}
    (out/'inspection.json').write_text(json.dumps({'sha256':DEMO_SHA,'objects':records,'texts':texts,'scripts_executed':False,'node_groups':[g.name for g in bpy.data.node_groups]},indent=2)+'\n')


def fit_demo(job):
    """Third bounded fit: preserve authored guide shapes, not donor character."""
    out=validate_demo(job)
    import bpy
    import math
    from mathutils import Vector
    from hair_native_groom import SOURCE,SOURCE_SHA,REFERENCES,digest
    from hair_volume_sculpt import skull_surface
    from hair_anatomy_refinement import is_hair,visibility
    from illustrated_hair_section import protection
    from hijab_donor import review
    out.mkdir();shutil.copyfile(Path(__file__),out/'handler-source.py')
    bpy.ops.wm.open_mainfile(filepath=str(DEMO),load_ui=False,use_scripts=False)
    def enable(layer):
        layer.exclude=False;layer.hide_viewport=False
        for child in layer.children:enable(child)
    enable(bpy.context.view_layer.layer_collection)
    records=[];pieces=[]
    for name in ('long hair main','long hair strands'):
        ob=bpy.data.objects[name];ob.hide_viewport=False;ob.hide_set(False)
        bpy.context.view_layer.update()
        data=ob.evaluated_get(bpy.context.evaluated_depsgraph_get()).data
        if len(data.points)>16_000_000:raise ValueError('Evaluated point ceiling')
        step=max(1,math.ceil(len(data.curves)/24000))
        curves=[]
        for c in list(data.curves)[::step]:
            curves.append([tuple(p.position) for p in c.points])
        guides=[[tuple(p.position) for p in c.points] for c in ob.data.curves]
        records.append({'source_object':name,'authored_guides':len(guides),'evaluated_curves':len(data.curves),'selected_curves':len(curves),'sampling_stride':step})
        pieces.append((curves,guides))
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE),load_ui=False,use_scripts=False)
    before=protection()
    for ob in bpy.context.scene.objects:
        if is_hair(ob):ob.hide_render=True
    skull=skull_surface(bpy.data.objects['MF_reference_crown_hair'])
    material=bpy.data.materials.new('MF_authored_donor_brown');material.use_nodes=True
    n,l=material.node_tree.nodes,material.node_tree.links;p=n.get('Principled BSDF')
    p.inputs['Roughness'].default_value=.72;p.inputs['Specular IOR Level'].default_value=.13
    info=n.new('ShaderNodeHairInfo');ramp=n.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].color=(.008,.0025,.0012,1)
    ramp.color_ramp.elements[1].color=(.085,.038,.017,1)
    l.new(info.outputs['Random'],ramp.inputs['Fac']);l.new(ramp.outputs['Color'],p.inputs['Base Color'])
    l.new(ramp.outputs['Color'],p.inputs['Emission Color']);p.inputs['Emission Strength'].default_value=.12
    pushed=0
    def mapped(point):
        nonlocal pushed
        x,y,z=point
        co=Vector((x*1.17,y*1.15+.62,(z-16.400089263916016)*1.10+1.36))
        # Collision-only guard retains external authored volume; no full wrap.
        if co.z>-.15:
            near,normal,_,_=skull.find_nearest(co)
            if near is not None and (co-near).dot(normal)<.014:
                co=near+normal*.014;pushed+=1
        return co
    for index,(curves,guides) in enumerate(pieces):
        for diagnostic,rows in ((False,curves),(True,guides)):
            data=bpy.data.hair_curves.new(f'MF_donor_bystedt_{index}_{diagnostic}')
            data.add_curves([len(c) for c in rows]);radius=data.attributes.new('radius','FLOAT','POINT')
            positions=[];radii=[]
            for curve in rows:
                for k,point in enumerate(curve):
                    positions.extend(mapped(point));t=k/max(1,len(curve)-1)
                    radii.append(.0019*(1-.85*t)+.0001)
            data.attributes['position'].data.foreach_set('vector',positions)
            radius.data.foreach_set('value',radii)
            ob=bpy.data.objects.new(data.name,data);bpy.context.scene.collection.objects.link(ob)
            data.materials.append(material);ob.hide_render=diagnostic
    visibility()
    # Visibility helper retains CURVES state; original curves stay hidden.
    assert protection()==before
    review(bpy.context.scene,out,(0,0,-.03),3.8,(('front',0),('left',-45),('right',45),('back',180)))
    result={'scope':'Third diagnostic donor fit, not acceptance','candidate':3,'donor':'Daniel Bystedt long hair from official Blender demo','donor_sha256':DEMO_SHA,'license':'CC BY-SA; exact version unresolved, local diagnostic only','records':records,'collision_adjusted_points':pushed,'protected_exact':protection()==before,'source_sha256':SOURCE_SHA,'handler_sha256':digest(Path(__file__)),'reference_authority':REFERENCES,'review_ready':False,'director_acceptance':'NOT_REQUESTED','new_native_saved':False,'motion':'NOT_RUN'}
    (out/'result.json').write_text(json.dumps(result,indent=2)+'\n')


def validate_authored(job):
    from hair_native_groom import SOURCE,SOURCE_SHA,REFBASE,REFERENCES,digest
    if not isinstance(job,dict) or set(job)!={'operation','candidate'} or job['operation']!='authored-fit' or type(job['candidate']) is not int or job['candidate'] not in (1,2,3):
        raise ValueError('Unsupported authored donor job')
    for p,h in [(SOURCE,SOURCE_SHA),*[(REFBASE/n,h) for n,h in REFERENCES.items()],*[(AUTHORED/n,h) for n,h in AUTHORED_PINS.items()]]:
        if p.is_symlink() or digest(p)!=h:raise ValueError('Pinned input changed')
    out=BASE/f'authored-donor22-{job["candidate"]:02}'
    if out.exists() or out.is_symlink() or out.resolve().parent!=BASE.resolve():raise ValueError('Output exists or escapes')
    if shutil.disk_usage(BASE).free<5_000_000_000:raise ValueError('Disk low')
    return out


def authored_fit(job):
    out=validate_authored(job)
    import bpy
    from hair_native_groom import SOURCE,SOURCE_SHA,REFERENCES,digest
    from illustrated_hair_section import protection
    from hair_anatomy_refinement import is_hair,visibility
    from hijab_donor import review
    out.mkdir();shutil.copyfile(Path(__file__),out/'handler-source.py')
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE),load_ui=False,use_scripts=False)
    before=protection()
    for ob in bpy.context.scene.objects:
        if is_hair(ob):ob.hide_render=True
    bpy.ops.wm.obj_import(filepath=str(AUTHORED/'elvs_ladies_hippyhair1.obj'),forward_axis='NEGATIVE_Z',up_axis='Y')
    objects=[o for o in bpy.context.selected_objects if o.type=='MESH']
    assert len(objects)==1
    hair=objects[0];hair.name='MF_authored_donor_hair_Elvaerwyn'
    # Fixed first fit: preserve artist-authored topology/UVs, adjust hair only.
    hair.scale=(.78,.78,.78);hair.location=(.035,0,1.43-8.0392*.78)
    bpy.context.view_layer.objects.active=hair
    bpy.ops.object.transform_apply(location=True,rotation=True,scale=True)
    material=bpy.data.materials.new('MF_Elvaerwyn_hair_reconstructed');material.use_nodes=True
    n,l=material.node_tree.nodes,material.node_tree.links;p=n.get('Principled BSDF')
    tex=n.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(AUTHORED/'hairtex1.png'));tex.image.pack()
    l.new(tex.outputs['Color'],p.inputs['Base Color']);l.new(tex.outputs['Alpha'],p.inputs['Alpha'])
    p.inputs['Roughness'].default_value=.8;p.inputs['Specular IOR Level'].default_value=.1
    hair.data.materials.clear();hair.data.materials.append(material)
    for face in hair.data.polygons:face.use_smooth=True
    # Inspect connected components before any sculpt/deformation proposal.
    parent=list(range(len(hair.data.vertices)))
    def find(i):
        while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
        return i
    for e in hair.data.edges:
        a,b=map(find,e.vertices);parent[a]=b
    components={}
    for v in hair.data.vertices:components.setdefault(find(v.index),[]).append(v)
    inventory=[]
    for vertices in components.values():
        inventory.append({'vertices':len(vertices),'min':[min(v.co[i] for v in vertices) for i in range(3)],'max':[max(v.co[i] for v in vertices) for i in range(3)]})
    if job['candidate']>=2:
        # Retarget the actual authored fringe components; do not reconstruct
        # them from repeated procedural guides or alter the protected head.
        for vertices in components.values():
            lo=[min(v.co[i] for v in vertices) for i in range(3)]
            hi=[max(v.co[i] for v in vertices) for i in range(3)]
            fringe=lo[2]>-1.05 and hi[1]<.15
            side=-1 if (lo[0]+hi[0])/2<.27 else 1
            for v in vertices:
                x,y,z=v.co
                upper=max(0,min(1,(z+.7)/1.5))
                y=y*1.30+.10*upper
                x-=.22*upper
                if fringe:
                    t=max(0,min(1,(hi[2]-z)/max(.3,hi[2]-lo[2])))
                    t=t*t*(3-2*t)
                    x+=side*.26*t
                    y+=.43*t
                    z+=.72*t
                v.co=(x,y,z)
        hair.data.update()
        ramp=n.new('ShaderNodeValToRGB')
        ramp.color_ramp.elements.remove(ramp.color_ramp.elements[1])
        for position,value in [(0,(.0015,.0006,.0003,1)),(.4,(.013,.0045,.0018,1)),(.7,(.065,.027,.011,1)),(1,(.18,.095,.044,1))]:
            e=ramp.color_ramp.elements[0] if position==0 else ramp.color_ramp.elements.new(position)
            e.position=position;e.color=value
        l.new(tex.outputs['Color'],ramp.inputs['Fac']);l.new(ramp.outputs['Color'],p.inputs['Base Color']);l.new(ramp.outputs['Color'],p.inputs['Emission Color'])
        p.inputs['Emission Strength'].default_value=.3
    visibility();bpy.context.scene.cycles.transparent_max_bounces=32
    assert protection()==before
    review(bpy.context.scene,out,(0,0,-.03),3.8,(('front',0),('left',-45),('right',45),('back',180)))
    result={'scope':'Authored donor suitability and first fit; not creative acceptance','candidate':job['candidate'],'protected_exact':protection()==before,'source_sha256':SOURCE_SHA,'handler_sha256':digest(Path(__file__)),'reference_authority':REFERENCES,'asset_pins':AUTHORED_PINS,'vertices':len(hair.data.vertices),'faces':len(hair.data.polygons),'uv_layers':len(hair.data.uv_layers),'components':inventory,'review_ready':False,'director_acceptance':'NOT_REQUESTED','new_native_saved':False,'license':'CC_by in source; exact version unresolved, not release-cleared'}
    (out/'result.json').write_text(json.dumps(result,indent=2)+'\n')


def validate(job):
    if job!={'operation':'hair_fit','output_name':'hair-donor-01'}: raise ValueError('Unsupported job')
    out=BASE/'hair-donor-01'
    if out.exists():raise ValueError('No overwrite')
    for path,digest in [(ASSET/'o4saken_long01.obj','3b58e92dae179dd6d0d9b0be07d5996827d8a8dd4158579d6bcc2e48ebd60c17'),
                        (BASE/'cleanup-portable-01/head-baked.blend','51e2a3d4c9df966e44f6a217d3535115bf19eef8e7ef9561cf6da75dc0ebd9b4')]:
        if path.is_symlink() or hashlib.sha256(path.read_bytes()).hexdigest()!=digest:raise ValueError('Changed input')
    records=json.loads((ASSET/'acquisition.json').read_text())['files']
    for name in ['o4saken_long01.png','o4saken_long01_nrm.png']:
        record=next(r for r in records if r['local']==name)
        if hashlib.sha256((ASSET/name).read_bytes()).hexdigest()!=record['sha256']:raise ValueError('Changed texture')
    return out


def run(job):
    out=validate(job)
    import bpy
    sys.path.insert(0,str(Path(__file__).resolve().parent))
    from likeness_cleanup import geometry_digest,render_views
    out.mkdir()
    bpy.ops.wm.open_mainfile(filepath=str(BASE/'cleanup-portable-01/head-baked.blend'),load_ui=False,use_scripts=False)
    head=bpy.data.objects['FBHead']; before=geometry_digest(head)
    bpy.ops.wm.obj_import(filepath=str(ASSET/'o4saken_long01.obj'),forward_axis='NEGATIVE_Z',up_axis='Y')
    hair=[o for o in bpy.context.selected_objects if o.type=='MESH']
    if len(hair)!=1:raise ValueError('Expected one hair mesh')
    hair=hair[0]; hair.name='MF_hair_donor_04saken'
    # Importer maps source Y-up into Blender Z-up. Uniform first-fit only.
    hair.scale=(.67,.67,.67); hair.location=(0,0,1.40-8.3173*.67)
    mat=bpy.data.materials.new('MF_donor_hair');mat.use_nodes=True
    nodes,links=mat.node_tree.nodes,mat.node_tree.links
    bsdf=nodes.get('Principled BSDF');bsdf.inputs['Roughness'].default_value=.8
    tex=nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(ASSET/'o4saken_long01.png'));tex.image.pack()
    links.new(tex.outputs['Color'],bsdf.inputs['Base Color']);links.new(tex.outputs['Alpha'],bsdf.inputs['Alpha'])
    hair.data.materials.clear();hair.data.materials.append(mat)
    for p in hair.data.polygons:p.use_smooth=True
    scene=bpy.context.scene;scene.camera.data.ortho_scale=4
    render_views(scene,scene.camera,out,'hair-fit')
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'head-hair-fit.blend'))
    assert geometry_digest(head)==before
    (out/'result.json').write_text(json.dumps({'head_preserved':True,'hair_vertices':len(hair.data.vertices),
        'hair_faces':len(hair.data.polygons),'license':'Embedded CC BY 4.0, author 04saken; catalog CC0 discrepancy retained',
        'scope':'Uniform first fit, not final hairstyle or rig'},indent=2))


if __name__=='__main__':
    sys.path.insert(0,str(Path(__file__).resolve().parent))
    args=sys.argv[sys.argv.index('--')+1:]
    if len(args)!=1:raise ValueError('One JSON job required')
    job=json.loads(Path(args[0]).read_text())
    if isinstance(job,dict) and job.get('operation')=='inspect-demo':inspect_demo(job)
    elif isinstance(job,dict) and job.get('operation')=='fit-demo':fit_demo(job)
    elif isinstance(job,dict) and job.get('operation')=='authored-fit':authored_fit(job)
    else:run(job)
