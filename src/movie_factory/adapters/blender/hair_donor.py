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


def validate_live(job):
    from hair_native_groom import SOURCE,SOURCE_SHA,REFBASE,REFERENCES,digest
    if not isinstance(job,dict) or set(job)!={'operation','candidate'} or type(job['candidate']) is not int or (job['operation'],job['candidate']) not in [('live-inspect',0),('live-inspect',1),('live-preview',1),('live-preview',2),('live-preview',3),('live-verify',3)]:
        raise ValueError('Fixed live donor job required')
    for p,h in [(DEMO,DEMO_SHA),(SOURCE,SOURCE_SHA),*[(REFBASE/n,h) for n,h in REFERENCES.items()]]:
        if p.is_symlink() or digest(p)!=h:raise ValueError('Pinned input changed')
    out=BASE/f'donor23-{job["operation"]}-{job["candidate"]:02}'
    if out.exists() or out.is_symlink() or out.resolve().parent!=BASE.resolve():raise ValueError('Output exists or escapes')
    if job['operation']=='live-verify':
        checkpoint=BASE/'donor23-live-preview-03'
        record=json.loads((checkpoint/'result.json').read_text())
        native=checkpoint/'diagnostic-live-groom.blend'
        if native.is_symlink() or digest(native)!=record['native_sha256']:raise ValueError('Checkpoint changed')
    if shutil.disk_usage(BASE).free<5_000_000_000:raise ValueError('Disk low')
    return out


def live_inspect(job):
    out=validate_live(job)
    import bpy
    out.mkdir();shutil.copyfile(Path(__file__),out/'handler-source.py')
    bpy.ops.wm.open_mainfile(filepath=str(DEMO),load_ui=False,use_scripts=False)
    objects=[]
    for ob in bpy.data.collections['Long hair'].all_objects:
        objects.append({'name':ob.name,'type':ob.type,'parent':ob.parent.name if ob.parent else None,'world':[list(row) for row in ob.matrix_world],'drivers':len(ob.animation_data.drivers) if ob.animation_data else 0})
    graphs={}
    for obname in ('long hair main','long hair strands'):
        ob=bpy.data.objects[obname]
        for m in ob.modifiers:
            if m.type!='NODES':continue
            g=m.node_group
            graphs[obname+'/'+m.name]={'group':g.name,'nodes':[{'name':n.name,'type':n.bl_idname,'group':n.node_tree.name if n.type=='GROUP' else None,'inputs':{s.name:str(s.default_value) for s in n.inputs if hasattr(s,'default_value') and not s.is_linked}} for n in g.nodes]}
    (out/'inspection.json').write_text(json.dumps({'objects':objects,'graphs':graphs},indent=2)+'\n')


def live_shape(point,candidate):
    """Fixed hair-only warp in target coordinates; preserves lower/rear shape."""
    import math
    x,y,z=point
    if candidate==1:return (x,y,z)
    def smooth(t):
        t=max(0.,min(1.,t));return t*t*(3-2*t)
    upper=smooth((z-.25)/.65)
    front=1-smooth((y+.15)/.85)
    # Move the side part toward the approved near-centre position, fading
    # the correction at temples rather than shifting the entire hairstyle.
    shift=.29*math.exp(-((x+.32)/.66)**2)*upper*front
    x+=shift
    # Third diagnostic removes global root lift/rearward motion. It also
    # disables Surface Deform below, so it is not a single-variable study.
    if candidate==3:return (x,y,z)
    lift=.10*math.exp(-(x/.60)**2)*front*smooth((z-.4)/.5)
    z+=lift
    y+=.09*front*upper
    return (x,y,z)


def curve_state(ob):
    import bpy,struct
    bpy.context.view_layer.update()
    data=ob.evaluated_get(bpy.context.evaluated_depsgraph_get()).data
    h=hashlib.sha256()
    for p in data.points:h.update(struct.pack('fff',*p.position))
    return {'curves':len(data.curves),'points':len(data.points),'positions_sha256':h.hexdigest()}


def live_preview(job):
    out=validate_live(job)
    import bpy
    from mathutils import Matrix,Vector
    from hair_native_groom import SOURCE,SOURCE_SHA,REFERENCES,digest
    from illustrated_hair_section import protection
    from hair_anatomy_refinement import is_hair,visibility
    from hijab_donor import review
    out.mkdir();shutil.copyfile(Path(__file__),out/'handler-source.py')
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE),load_ui=False,use_scripts=False)
    protected=protection()
    for ob in bpy.context.scene.objects:
        if is_hair(ob):ob.hide_render=True
    existing=set(bpy.data.objects)
    with bpy.data.libraries.load(str(DEMO),link=False) as (a,b):
        b.objects=['long hair main','long hair strands','long hair growth mesh']
    main,strands,surface=b.objects
    imported=set(bpy.data.objects)-existing
    for ob in imported:
        if ob.name not in bpy.context.scene.objects:bpy.context.scene.collection.objects.link(ob)
        ob.hide_render=True;ob.hide_viewport=False;ob.hide_set(False)
    bpy.context.view_layer.update()
    worlds={ob:ob.matrix_world.copy() for ob in imported}
    root=bpy.data.objects.new('MF_donor23_hair_retarget',None);bpy.context.scene.collection.objects.link(root)
    root.matrix_world=Matrix(((1.17,0,0,-5*1.17),(0,1.15,0,.62),(0,0,1.10,1.36-16.400089263916016*1.10),(0,0,0,1)))
    for ob in imported:
        ob.name='MF_donor23_hair_'+ob.name
        ob.parent=root;ob.matrix_parent_inverse=Matrix.Identity(4);ob.matrix_basis=worlds[ob]
    bpy.context.view_layer.update()
    # Apply the same bounded warp to the growth surface and the live source
    # curves, preserving UV/root islands and the existing interpolation graph.
    for ob in (main,strands,surface):
        matrix=ob.matrix_world.copy();inverse=matrix.inverted()
        if ob.type=='MESH':
            for v in ob.data.vertices:v.co=inverse@Vector(live_shape(matrix@v.co,job['candidate']))
            ob.data.update()
        else:
            for p in ob.data.points:p.position=inverse@Vector(live_shape(matrix@p.position,job['candidate']))
            ob.data.update_tag()
    if job['candidate']==3:
        # A static neutral retarget, not a scalp-deformation binding proof.
        # Disable donor rest-surface deformation after editing neutral guides
        # and surface together. Interpolation/clumping remain fully live.
        for ob in (main,strands):
            for mod in ob.modifiers:
                if mod.name=='Surface Deform':mod.show_viewport=False;mod.show_render=False
    material=bpy.data.materials.new('MF_donor23_hair_material');material.use_nodes=True
    n,l=material.node_tree.nodes,material.node_tree.links;p=n.get('Principled BSDF')
    p.inputs['Roughness'].default_value=.72;p.inputs['Specular IOR Level'].default_value=.13
    info=n.new('ShaderNodeHairInfo');ramp=n.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].color=(.008,.0025,.0012,1);ramp.color_ramp.elements[1].color=(.085,.038,.017,1)
    l.new(info.outputs['Random'],ramp.inputs['Fac']);l.new(ramp.outputs['Color'],p.inputs['Base Color'])
    l.new(ramp.outputs['Color'],p.inputs['Emission Color']);p.inputs['Emission Strength'].default_value=.12
    for ob in (main,strands):
        ob.hide_render=False
        tree=bpy.data.node_groups.new('MF_donor23_hair_finish','GeometryNodeTree')
        tree.interface.new_socket(name='Geometry',in_out='INPUT',socket_type='NodeSocketGeometry');tree.interface.new_socket(name='Geometry',in_out='OUTPUT',socket_type='NodeSocketGeometry')
        n,l=tree.nodes,tree.links;gi=n.new('NodeGroupInput');go=n.new('NodeGroupOutput')
        radius=n.new('GeometryNodeSetCurveRadius');radius.inputs['Radius'].default_value=.0016
        mat=n.new('GeometryNodeSetMaterial');mat.inputs['Material'].default_value=material
        l.new(gi.outputs['Geometry'],radius.inputs['Curve']);l.new(radius.outputs['Curve'],mat.inputs['Geometry']);l.new(mat.outputs['Geometry'],go.inputs['Geometry'])
        ob.modifiers.new('MF live finish','NODES').node_group=tree
    visibility()
    for ob in imported:
        ob.hide_render=ob not in (main,strands)
    baseline=curve_state(main)
    # Live control proof: fixed non-root guide-point displacement must change
    # evaluated children, and an exact rollback must restore their digest.
    probe=main.data.curves[0].points[min(4,len(main.data.curves[0].points)-1)]
    old=probe.position.copy();probe.position=old+Vector((0,-.08,.04));main.data.update_tag()
    changed=curve_state(main)
    probe.position=old;main.data.update_tag();restored=curve_state(main)
    assert baseline==restored and baseline!=changed
    assert protection()==protected
    review(bpy.context.scene,out,(0,0,-.03),3.8,(('front',0),('left',-45),('right',45),('back',180)))
    result={'candidate':job['candidate'],'live_control_changed':baseline!=changed,'rollback_exact':baseline==restored,'baseline':baseline,'changed':changed,'guide_counts':[len(main.data.curves),len(strands.data.curves)],'protected_exact':protection()==protected,'protected_digest':protected,'source_sha256':SOURCE_SHA,'donor_sha256':DEMO_SHA,'handler_sha256':digest(Path(__file__)),'reference_authority':REFERENCES,'review_ready':False,'director_acceptance':'NOT_REQUESTED','native_saved':False,'surface_deform_disabled':job['candidate']==3,'scalp_animation_binding':'NOT_VALIDATED'}
    if job['candidate']==3:
        bpy.context.scene['MF_donor23_diagnostic']='NOT_APPROVED';bpy.ops.file.pack_all()
        bpy.ops.wm.save_as_mainfile(filepath=str(out/'diagnostic-live-groom.blend'),compress=True)
        result['native_saved']=True;result['native_sha256']=digest(out/'diagnostic-live-groom.blend')
    (out/'result.json').write_text(json.dumps(result,indent=2)+'\n')


def integrated_validate(job):
    from hair_native_groom import SOURCE,SOURCE_SHA,REFBASE,REFERENCES,digest
    allowed={('root-audit',0),('surface-package',23),('surface-seal',23),('surface-probe',23),('surface-verify',23),*[('surface-preview',i) for i in range(1,24)]}
    if not isinstance(job,dict) or set(job)!={'operation','candidate'} or type(job.get('candidate')) is not int or (job.get('operation'),job.get('candidate')) not in allowed:
        raise ValueError('Fixed integrated hair operation required')
    for p,h in [(DEMO,DEMO_SHA),(SOURCE,SOURCE_SHA),*[(REFBASE/n,h) for n,h in REFERENCES.items()]]:
        if p.is_symlink() or digest(p)!=h:raise ValueError('Pinned input changed')
    out=BASE/f'integrated24-{job["operation"]}-{job["candidate"]:02}'
    if out.exists() or out.is_symlink() or out.resolve().parent!=BASE.resolve():raise ValueError('Output exists or escapes')
    if job['operation'] in ('surface-package','surface-seal','surface-verify'):
        stage='surface-seal' if job['operation']=='surface-verify' else 'surface-preview'
        folder=BASE/f'integrated24-{stage}-23';record=folder/'result.json'
        if record.is_symlink() or not record.is_file():raise ValueError('Prerequisite result required')
        data=json.loads(record.read_text())
        if not data.get('protected_exact'):raise ValueError('Protected state prerequisite failed')
        if job['operation']=='surface-verify':
            native=folder/'integrated-hair.blend'
            if native.is_symlink() or digest(native)!=data['native_sha256']:raise ValueError('Native checkpoint changed')
    if shutil.disk_usage(BASE).free<5_000_000_000:raise ValueError('Disk low')
    return out


def integrated_load():
    import bpy
    from mathutils import Matrix
    from hair_native_groom import SOURCE
    from illustrated_hair_section import protection
    from hair_anatomy_refinement import is_hair
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE),load_ui=False,use_scripts=False)
    protected=protection()
    for ob in bpy.context.scene.objects:
        if is_hair(ob):ob.hide_render=True
    existing=set(bpy.data.objects)
    with bpy.data.libraries.load(str(DEMO),link=False) as (a,b):
        b.objects=['long hair main','long hair strands','long hair growth mesh']
    main,strands,surface=b.objects;imported=set(bpy.data.objects)-existing
    for ob in imported:
        if ob.name not in bpy.context.scene.objects:bpy.context.scene.collection.objects.link(ob)
        ob.hide_render=True;ob.hide_viewport=False;ob.hide_set(False)
    bpy.context.view_layer.update()
    worlds={ob:ob.matrix_world.copy() for ob in imported}
    root=bpy.data.objects.new('MF_integrated24_hair_retarget',None);bpy.context.scene.collection.objects.link(root)
    root.matrix_world=Matrix(((1.17,0,0,-5*1.17),(0,1.15,0,.62),(0,0,1.10,1.36-16.400089263916016*1.10),(0,0,0,1)))
    for ob in imported:
        ob.name='MF_integrated24_hair_'+ob.name
        ob.parent=root;ob.matrix_parent_inverse=Matrix.Identity(4);ob.matrix_basis=worlds[ob]
    bpy.context.view_layer.update()
    return protected,main,strands,surface,imported


def root_audit(job):
    out=integrated_validate(job)
    import bpy
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    from illustrated_hair_section import protection
    out.mkdir();shutil.copyfile(Path(__file__),out/'handler-source.py')
    protected,main,strands,surface,imported=integrated_load()
    head=bpy.data.objects['MF_continuous_head_neck']
    tree=BVHTree.FromPolygons([head.matrix_world@v.co for v in head.data.vertices],[list(p.vertices) for p in head.data.polygons])
    def stats(points):
        rows=[]
        for q in points:
            if q.z>.45 and q.y<-.20:
                hit,n,_,d=tree.find_nearest(q)
                rows.append({'position':list(q),'signed_nearest':(q-hit).dot(n),'distance':d})
        inside=[r for r in rows if r['signed_nearest']<-.008]
        return {'tested':len(rows),'inside_proxy':len(inside),'worst':sorted(rows,key=lambda r:r['signed_nearest'])[:16]}
    report={'surface_attributes':[(a.name,a.data_type,a.domain) for a in surface.data.attributes], 'stages':[]}
    for stage in ('unmodified','previous-lateral-warp'):
        if stage!='unmodified':
            for ob in (main,strands,surface):
                mat=ob.matrix_world.copy();inv=mat.inverted()
                points=ob.data.vertices if ob.type=='MESH' else ob.data.points
                for p in points:
                    if ob.type=='MESH':p.co=inv@Vector(live_shape(mat@p.co,3))
                    else:p.position=inv@Vector(live_shape(mat@p.position,3))
                if ob.type=='MESH':ob.data.update()
                else:ob.data.update_tag()
            for ob in (main,strands):
                for mod in ob.modifiers:
                    if mod.name=='Surface Deform':mod.show_viewport=False;mod.show_render=False
        bpy.context.view_layer.update()
        evaluated=main.evaluated_get(bpy.context.evaluated_depsgraph_get()).data
        report['stages'].append({'stage':stage,'guide_roots':stats([main.matrix_world@c.points[0].position for c in main.data.curves]),'generated_roots':stats([main.matrix_world@c.points[0].position for c in evaluated.curves]),'generated_count':len(evaluated.curves)})
    report['protected_exact']=protection()==protected
    assert report['protected_exact']
    (out/'audit.json').write_text(json.dumps(report,indent=2)+'\n')


def surface_preview(job):
    out=integrated_validate(job)
    import bpy
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    from illustrated_hair_section import protection
    from hair_native_groom import digest,REFERENCES,SOURCE_SHA
    from hair_anatomy_refinement import visibility
    from hijab_donor import review
    out.mkdir();shutil.copyfile(Path(__file__),out/'handler-source.py')
    protected,main,strands,surface,imported=integrated_load()
    head=bpy.data.objects['MF_continuous_head_neck']
    tree=BVHTree.FromPolygons([head.matrix_world@v.co for v in head.data.vertices],[list(p.vertices) for p in head.data.polygons])
    corrected=0
    def transport(point):
        nonlocal corrected
        q=Vector(live_shape(point,3))
        if (q-point).length>=.00001:
            # Preserve distance above the curved accepted scalp rather than
            # translating roots into its wider central cross-section.
            old,n,_,d=tree.find_nearest(point)
            clearance=max(.012,(point-old).dot(n))
            new,nn,_,_=tree.find_nearest(q)
            corrected+=1
            q=new+nn*clearance
        elif job['candidate']<3:return point
        if job['candidate']>=2:
            import math
            # Reference temple flow goes behind the ear, not straight down
            # the cheek. The broad correction fades at crown and lower ends.
            side=max(0.,min(1.,(abs(q.x)-.48)/.35))
            front=max(0.,min(1.,(.25-q.y)/.75))
            q.y+=(.55 if job['candidate']>=7 else .25)*side*front*math.exp(-((q.z-.20)/.48)**2)
            if job['candidate']>=7 and q.z>.1:
                hit,n,_,_=tree.find_nearest(q)
                if (q-hit).dot(n)<.014:q=hit+n*.014
            if job['candidate']>=3 and q.z<-.25:
                lower=max(0.,min(1.,(-q.z-.25)/.8))
                q.x*=1-.10*lower
                q.z-=.25*lower
        return q
    for ob in (main,strands,surface):
        mat=ob.matrix_world.copy();inv=mat.inverted()
        points=ob.data.vertices if ob.type=='MESH' else ob.data.points
        for p in points:
            if ob.type=='MESH':p.co=inv@transport(mat@p.co)
            else:p.position=inv@transport(mat@p.position)
        if ob.type=='MESH':ob.data.update()
        else:ob.data.update_tag()
    if job['candidate']>=8:
        import math
        for ob in (main,strands):
            matrix=ob.matrix_world.copy();inverse=matrix.inverted()
            for curve in ob.data.curves:
                root=matrix@curve.points[0].position
                weight=math.exp(-((root.z-1.1)/.50)**2)*max(0,min(1,(.5-root.y)/.8))
                for k,p in enumerate(curve.points):
                    t=k/max(1,len(curve.points)-1)
                    lift=weight*(.19 if root.x<0 else .14)*math.sin(math.pi*min(1,t/.48))**1.2
                    co=matrix@p.position
                    outward=Vector((co.x*.65,co.y*.5,max(.25,co.z-.3))).normalized()
                    p.position=inverse@(co+outward*lift)
            ob.data.update_tag()
    for ob in (main,strands):
        for mod in ob.modifiers:
            if mod.name=='Surface Deform':mod.show_viewport=False;mod.show_render=False
    if job['candidate']>=2:
        # Reduce procedural flyaway noise, retaining the authored shapes.
        g=next(m.node_group for m in main.modifiers if m.type=='NODES' and m.name=='Long hair')
        for node in g.nodes:
            if node.type=='GROUP' and 'Noise' in node.node_tree.name and 'Factor' in node.inputs and not node.inputs['Factor'].is_linked:
                node.inputs['Factor'].default_value=.18
        if job['candidate']>=6:
            for node in g.nodes:
                if node.type=='GROUP' and 'Noise' in node.node_tree.name and 'Distance' in node.inputs:
                    node.inputs['Distance'].default_value=.012
            info=g.nodes.get('Object Info')
            if info:
                for link in list(info.outputs['Geometry'].links):g.links.remove(link)
    material=bpy.data.materials.new('MF_integrated24_hair_material');material.use_nodes=True
    n,l=material.node_tree.nodes,material.node_tree.links;p=n.get('Principled BSDF')
    p.inputs['Roughness'].default_value=.72;p.inputs['Specular IOR Level'].default_value=.13
    info=n.new('ShaderNodeHairInfo');ramp=n.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].color=(.008,.0025,.0012,1);ramp.color_ramp.elements[1].color=(.085,.038,.017,1)
    if job['candidate']>=2:
        ramp.color_ramp.elements[0].color=(.005,.002,.001,1);ramp.color_ramp.elements[1].color=(.018,.007,.003,1)
    l.new(info.outputs['Random'],ramp.inputs['Fac']);l.new(ramp.outputs['Color'],p.inputs['Base Color'])
    l.new(ramp.outputs['Color'],p.inputs['Emission Color']);p.inputs['Emission Strength'].default_value=.12
    for ob in (main,strands):
        ob.hide_render=False
        g=bpy.data.node_groups.new('MF_integrated24_hair_finish','GeometryNodeTree')
        g.interface.new_socket(name='Geometry',in_out='INPUT',socket_type='NodeSocketGeometry');g.interface.new_socket(name='Geometry',in_out='OUTPUT',socket_type='NodeSocketGeometry')
        n,l=g.nodes,g.links;gi=n.new('NodeGroupInput');go=n.new('NodeGroupOutput')
        radius=n.new('GeometryNodeSetCurveRadius');radius.inputs['Radius'].default_value=.0016
        mat=n.new('GeometryNodeSetMaterial');mat.inputs['Material'].default_value=material
        l.new(gi.outputs['Geometry'],radius.inputs['Curve']);l.new(radius.outputs['Curve'],mat.inputs['Geometry']);l.new(mat.outputs['Geometry'],go.inputs['Geometry'])
        ob.modifiers.new('MF integrated finish','NODES').node_group=g
    visibility()
    for ob in imported:ob.hide_render=ob not in (main,strands)
    if job['candidate'] in (2,3):
        authored_locks(main,job['candidate'])
    elif job['candidate'] in (4,5):
        clustered_locks(main,job['candidate'])
    if job['candidate']>=3:strands.hide_render=True
    if job['candidate']==5 or job['candidate']>=11:
        # Closed clumps over the continuous fitted growth cap replace the
        # competing fine-fiber layer. Cap is only the dark coverage foundation.
        main.hide_render=True;surface.hide_render=False
        cap=bpy.data.materials.new('MF_integrated24_hair_dark_foundation');cap.use_nodes=True
        p=cap.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(.009,.0035,.0018,1);p.inputs['Roughness'].default_value=.9
        if job['candidate']>=12:
            # Rear-only foundation: do not expose a dark cap rim on forehead.
            n,l=cap.node_tree.nodes,cap.node_tree.links
            geo=n.new('ShaderNodeNewGeometry');xyz=n.new('ShaderNodeSeparateXYZ');test=n.new('ShaderNodeMath');test.operation='LESS_THAN';test.inputs[1].default_value=.15
            transparent=n.new('ShaderNodeBsdfTransparent');mix=n.new('ShaderNodeMixShader')
            l.new(geo.outputs['Position'],xyz.inputs[0]);l.new(xyz.outputs['Y'],test.inputs[0]);l.new(test.outputs[0],mix.inputs[0]);l.new(p.outputs[0],mix.inputs[1]);l.new(transparent.outputs[0],mix.inputs[2]);l.new(mix.outputs[0],n.get('Material Output').inputs['Surface'])
        surface.data.materials.clear();surface.data.materials.append(cap)
    if job['candidate']>=6:
        painted_curves(main,job['candidate'])
    bpy.context.view_layer.update()
    evaluated=main.evaluated_get(bpy.context.evaluated_depsgraph_get()).data
    inside=0;tested=0
    for c in evaluated.curves:
        q=main.matrix_world@c.points[0].position
        if q.z>.45 and q.y<-.2:
            hit,n,_,_=tree.find_nearest(q);tested+=1;inside+=int((q-hit).dot(n)<-.008)
    if job['operation']!='surface-probe':review(bpy.context.scene,out,(0,0,-.20) if job['candidate']>=5 else (0,0,-.03),4.2 if job['candidate']>=5 else 3.8,(('front',0),('left',-45),('right',45),('back',180)))
    assert protection()==protected
    result={'candidate':job['candidate'],'corrected_points':corrected,'front_upper_generated_roots':tested,'roots_inside_proxy':inside,'protected_exact':True,'protected_digest':protected,'source_sha256':SOURCE_SHA,'reference_authority':REFERENCES,'handler_sha256':digest(Path(__file__)),'review_ready':False}
    result['root_probe_scope']='Hidden live main output, not the transformed rendered derivative; not a collision-free guarantee'
    if job['operation']=='surface-probe':
        result['control']=integrated_control(main,job['candidate'],protected,out)
    if job['operation'] in ('surface-package','surface-seal'):
        painted=bpy.data.objects['MF_integrated24_hair_painted']
        result['rendered_baseline']=painted_state(painted)
        result['control']=integrated_control(main,job['candidate'],protected,out)
        result['derived_binding']='Explicit deterministic rebuild from retained live source guides; not automatic deformation binding'
        result['motion']='NOT_RUN';result['scalp_animation_binding']='NOT_VALIDATED'
        result['director_acceptance']='PENDING';result['review_ready']=True
        bpy.context.scene['MF_integrated24_status']='DIRECTOR_REVIEW_PENDING_NOT_PRODUCTION_APPROVED'
        bpy.ops.file.pack_all()
        result['unpacked_file_images']=[im.name for im in bpy.data.images if im.source=='FILE' and not im.packed_file and not im.packed_files]
        if result['unpacked_file_images']:raise ValueError('Native image dependency not packed')
        native=out/'integrated-hair.blend';bpy.ops.wm.save_as_mainfile(filepath=str(native),compress=True)
        result['native_sha256']=digest(native)
    (out/'result.json').write_text(json.dumps(result,indent=2)+'\n')


def painted_state(ob):
    import struct
    state=curve_state(ob);h=hashlib.sha256()
    for p in ob.data.attributes['MF_paint'].data:h.update(struct.pack('ffff',*p.color))
    state['color_sha256']=h.hexdigest()
    return state


def rebuild_painted(main,candidate):
    import bpy
    previous=bpy.data.objects['MF_integrated24_hair_painted'];data=previous.data
    bpy.data.objects.remove(previous,do_unlink=True);bpy.data.hair_curves.remove(data)
    painted_curves(main,candidate)
    return bpy.data.objects['MF_integrated24_hair_painted']


def integrated_control(main,candidate,protected,evidence_dir=None):
    import bpy
    from mathutils import Vector
    from illustrated_hair_section import protection
    baseline=painted_state(bpy.data.objects['MF_integrated24_hair_painted'])
    ci=next(i for i,c in enumerate(main.data.curves) if (main.matrix_world@c.points[0].position).x<-.25 and (main.matrix_world@c.points[0].position).y<0 and (main.matrix_world@c.points[0].position).z>.65)
    pi=min(4,len(main.data.curves[ci].points)-1);probe=main.data.curves[ci].points[pi];old=probe.position.copy()
    before=curve_state(main);probe.position=old+Vector((0,-.08,.04));main.data.update_tag()
    source_changed=curve_state(main)
    changed=painted_state(rebuild_painted(main,candidate))
    main.data.curves[ci].points[pi].position=old;main.data.update_tag();restored=painted_state(rebuild_painted(main,candidate))
    diagnostic={'baseline':baseline,'changed':changed,'restored':restored,'source_before':before,'source_changed':source_changed,'source_after':curve_state(main),'probe':[ci,pi]}
    if evidence_dir:(evidence_dir/'control-diagnostic.json').write_text(json.dumps(diagnostic,indent=2)+'\n')
    assert before!=source_changed and baseline!=changed and restored==baseline
    assert protection()==protected
    return {'guide_index':ci,'point_index':pi,'local_delta':[0,-.08,.04],'source_changed':before!=source_changed,'rendered_changed':baseline!=changed,'rollback_exact':restored==baseline,'baseline':baseline,'changed':changed,'protected_exact':True,'scope':'One static left-front non-root guide probe with explicit derivative rebuild; not motion, every-guide coverage or edit-locality qualification'}


def integrated_verify(job):
    out=integrated_validate(job)
    import bpy
    from hair_native_groom import digest
    from illustrated_hair_section import protection
    from hijab_donor import review
    folder=BASE/'integrated24-surface-seal-23';record=json.loads((folder/'result.json').read_text());native=folder/'integrated-hair.blend'
    out.mkdir();shutil.copyfile(Path(__file__),out/'handler-source.py')
    bpy.ops.wm.open_mainfile(filepath=str(native),load_ui=False,use_scripts=False)
    assert protection()==record['protected_digest']
    assert painted_state(bpy.data.objects['MF_integrated24_hair_painted'])==record['rendered_baseline']
    main=bpy.data.objects['MF_integrated24_hair_long hair main']
    control=integrated_control(main,23,record['protected_digest'])
    assert control==record['control']
    review(bpy.context.scene,out,(0,0,-.20),4.2,(('front',0),))
    assert digest(native)==record['native_sha256']
    (out/'verification.json').write_text(json.dumps({'fresh_reopen_exact':True,'repeatable_control_and_rollback':True,'protected_exact':True,'native_unchanged':True,'native_sha256':record['native_sha256'],'handler_sha256':digest(Path(__file__)),'motion':'NOT_RUN','director_acceptance':'PENDING'},indent=2)+'\n')


def cluster_paths(paths,count=36):
    """Deterministic whole-trajectory clustering, not a root-only assignment."""
    import numpy as np
    from hair_volume_sculpt import spline
    rows=np.array([[spline(p,i/47) for i in range(48)] for p in paths])
    features=rows[:,[0,8,20,35,47]].reshape(len(rows),-1)
    centers=[features[0]]
    for _ in range(min(count,len(paths))-1):
        distances=np.min(np.sum((features[:,None,:]-np.array(centers)[None,:,:])**2,axis=2),axis=1)
        centers.append(features[int(np.argmax(distances))])
    centers=np.array(centers)
    for _ in range(12):
        labels=np.argmin(np.sum((features[:,None,:]-centers[None,:,:])**2,axis=2),axis=1)
        for k in range(len(centers)):
            if np.any(labels==k):centers[k]=features[labels==k].mean(axis=0)
    return [(rows[labels==k].mean(axis=0).tolist(),rows[labels==k].tolist()) for k in range(len(centers)) if np.any(labels==k)]


def painted_curves(main,candidate):
    """Coherent color blocks on continuous generated hair, not thick overlays."""
    import bpy,math
    import numpy as np
    from mathutils import Vector
    groups=cluster_paths([[tuple(main.matrix_world@p.position) for p in c.points] for c in main.data.curves],count=48)
    centers=np.array([mean for mean,members in groups])
    bpy.context.view_layer.update();data=main.evaluated_get(bpy.context.evaluated_depsgraph_get()).data
    rows=[[tuple(main.matrix_world@p.position) for p in c.points] for c in data.curves]
    if candidate>=12:
        # Reuse the donor's coherent swept half, not its incompatible heavy
        # side curtain. The retained live guides still drive this derivative.
        rows=[r for r in rows if r[0][0]<0 and r[min(len(r)-1,3)][0]<0]
        if candidate>=13:
            from mathutils.bvhtree import BVHTree
            head=bpy.data.objects['MF_continuous_head_neck']
            scalp=BVHTree.FromPolygons([head.matrix_world@v.co for v in head.data.vertices],[list(p.vertices) for p in head.data.polygons])
            transported=[]
            for row in rows:
                target=[]
                for co in row:
                    old=Vector(co);q=old.copy()
                    weight=max(0,min(1,(q.z-.45)/.40))*max(0,min(1,(.60-q.y)/.80))
                    q.x=-max(.008,abs(q.x)-.29*weight*math.exp(-(q.x/.70)**2))
                    hit,normal,_,_=scalp.find_nearest(old);clearance=max(.012,(old-hit).dot(normal))
                    hit,normal,_,_=scalp.find_nearest(q)
                    if (q-hit).dot(normal)<clearance:q=hit+normal*clearance
                    target.append(tuple(q))
                transported.append(target)
            rows=transported
        mirrored=[]
        for row in rows:
            r=[]
            for k,(x,y,z) in enumerate(row):
                t=k/max(1,len(row)-1)
                # Unequal shoulder length/root volume avoids a mirror hairstyle.
                lift=.035*math.sin(math.pi*min(1,t/.48))*max(0,min(1,(z-.2)/.7))
                r.append((-x,y+.035*math.sin(math.pi*t),z+lift-.035*t*t))
            mirrored.append(r)
        rows+=mirrored
        if candidate>=14:
            # Reference forehead is tapered, not a horizontal slicked-back
            # opening. Compose the lifted sweep and lower outer corners
            # together, preserving root-to-scalp clearance on the same head.
            adjusted=[]
            for row in rows:
                points=[]
                for k,co in enumerate(row):
                    old=Vector(co);q=old.copy()
                    front=max(0,min(1,(.40-q.y)/.85))
                    upper=math.exp(-((q.z-.98)/.50)**4)
                    side=min(1,abs(q.x)/.73)
                    lift,drop=(.07,.50) if candidate>=15 else (.21,.30)
                    q.z+=front*upper*(lift*math.sin(math.pi*side)-drop*side**2)
                    if candidate>=16:
                        continued=max(0,min(1,(old.z+.45)/1.05))
                        q.z-=front*max(0,continued-upper)*drop*side**2
                        q.x*=1-.09*front*math.exp(-((q.z-.35)/.45)**2)
                    q.y-=front*upper*.055*side
                    q.x+=.010*math.sin(q.z*19+q.y*3)*math.exp(-(q.x/.18)**2)*front
                    if candidate>=21:
                        edge=math.exp(-((abs(q.x)-.55)/.23)**2)*math.exp(-((q.z-.72)/.42)**2)*max(0,min(1,(-q.y-.22)/.38))
                        q.z-=.18*edge
                        q.y-=.035*edge
                    hit,n,_,_=scalp.find_nearest(old);clearance=max(.012,(old-hit).dot(n))
                    hit,n,_,_=scalp.find_nearest(q)
                    if (q-hit).dot(n)<clearance:q=hit+n*clearance
                    if candidate==22:
                        hit,n,_,_=scalp.find_nearest(q);distance=max(0,(q-hit).dot(n))
                        temple=math.exp(-((q.z-.50)/.55)**4)*max(0,min(1,(abs(q.x)-.58)/.28))*max(0,min(1,(.30-q.y)/.70))
                        fraction=(.46 if q.x>0 else .36)*temple
                        q-=n*max(0,distance-.035)*fraction
                    if candidate>=15 and q.z<-.35:
                        q.z-=.30*min(1,(-q.z-.35)/.65)
                    points.append(tuple(q))
                adjusted.append(points)
            rows=adjusted
    if candidate>=11:
        from hair_volume_sculpt import spline
        smooth_rows=[]
        for row in rows:
            points=np.array([spline(row,i/63) for i in range(64)])
            for _ in range(5):points[1:-1]=(points[:-2]+points[1:-1]*2+points[2:])/4
            if candidate>=23:
                anchor=points[50].copy();tangent=(points[50]-points[45])/5
                for k in range(51,64):
                    t=(k-50)/13;weight=.85*t*t
                    points[k]=points[k]*(1-weight)+(anchor+tangent*(k-50)*.85)*weight
            smooth_rows.append(points.tolist())
        rows=smooth_rows
    roots=np.array([r[0] for r in rows]);labels=np.argmin(np.sum((roots[:,None,:]-centers[None,:,0,:])**2,axis=2),axis=1)
    painted=bpy.data.hair_curves.new('MF_integrated24_hair_painted');painted.add_curves([len(r) for r in rows])
    if candidate>=7 and candidate<12:
        for name in ('curve_type','resolution','cyclic','nurbs_order'):
            source=data.attributes.get(name)
            if source is not None and source.domain=='CURVE':
                target=painted.attributes.get(name) or painted.attributes.new(name,source.data_type,source.domain)
                for a,b in zip(target.data,source.data):a.value=b.value
    if candidate>=11:
        curve_type=painted.attributes.get('curve_type') or painted.attributes.new('curve_type','INT8','CURVE')
        curve_type.data.foreach_set('value',[0]*len(rows))
    radius=painted.attributes.new('radius','FLOAT','POINT');colors=painted.attributes.new('MF_paint','FLOAT_COLOR','POINT')
    positions=[];radii=[];rgba=[]
    tones=[(.012,.0048,.0026),(.024,.010,.005),(.042,.019,.010),(.072,.034,.019),(.10,.050,.030)]
    if candidate>=10:
        from hair_native_groom import REFBASE
        from hair_volume_sculpt import spline
        source_image=bpy.data.images.load(str(REFBASE/'frontal-v02-individualized.png'),check_existing=True)
        pixels=np.asarray(source_image.pixels[:]).reshape(source_image.size[1],source_image.size[0],4)
        # Sample a curved hair-only swath along the approved painted flow.
        # This is a material coordinate, not a front-camera projection.
        painted_path=[(490,270,0),(448,246,0),(371,278,0),(301,351,0),(246,424,0),(224,510,0),(236,687,0),(260,800,0)]
        def swatch(t,offset,group):
            t=min(.99,max(.01,t*.88+.025*(group%5)))
            q=np.array(spline(painted_path,t))[:2]
            tangent=np.array(spline(painted_path,min(1,t+.003)))[:2]-np.array(spline(painted_path,max(0,t-.003)))[:2]
            across=np.array([-tangent[1],tangent[0]])/max(1e-8,np.linalg.norm(tangent))
            q+=across*offset
            x=int(max(0,min(source_image.size[0]-1,q[0])));y=int(max(0,min(source_image.size[1]-1,q[1])))
            rgb=pixels[source_image.size[1]-1-y,x,:3]
            # Reject scarf blue and skin contamination; no source edits.
            if rgb[2]>rgb[0]*.82 or rgb[0]>.58:return (.012,.0047,.0022)
            return tuple(float(v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4) for v in rgb)
    for ci,row in enumerate(rows):
        group=int(labels[ci]);base=tones[(group*13+7)%len(tones)]
        if candidate>=7:
            mean=centers[group];delta=roots[ci]-mean[0]
            outward=np.array((mean[0,0],mean[0,1],max(.2,mean[0,2]-.2)))
            tangent=mean[3]-mean[0];across=np.cross(tangent,outward);across/=max(1e-8,np.linalg.norm(across))
            stripe=float(delta@across)*95+group*1.7
            accent=max(0,math.sin(stripe)+.35*math.sin(stripe*2.3)-.6)
        for k,co in enumerate(row):
            t=k/max(1,len(row)-1);positions.extend(co)
            radius_value=.0022*(.14+.86*math.sin(math.pi*min(.98,t*.97+.015))**.30)
            if candidate>=9:
                # Full coverage at crown, softly converging ends rather than
                # the donor's long, uniformly thick silhouette whiskers.
                radius_value=.0030*max(.012,(1-t)**.55)
            if candidate>=20:radius_value*=.15+.85*min(1,t/.035)
            if candidate>=23:radius_value*=min(1,max(.015,(1-t)/.20))
            radii.append(radius_value)
            wave=math.sin(t*19+group*1.37)+.25*math.sin(t*57+group*.9)
            fac=.75 if wave<-.4 else 1 if wave<.6 else 1.4
            if candidate>=7:
                envelope=max(0,math.sin(math.pi*min(1,t/.80)))**1.5
                strength=min(1,accent*envelope*(.7 if wave<0 else 1.0)*(2.8 if candidate>=9 else 1.0))
                dark=(.007,.0027,.0013);light=(.085,.038,.018)
                if candidate>=9:dark=(.009,.0037,.0019);light=(.24,.125,.071)
                color=[a*(1-strength)+b*strength for a,b in zip(dark,light)]
                if candidate>=10:color=swatch(t,float(delta@across)*310,group)
                if candidate>=13:
                    fade=min(1,t/.10)
                    color=[a*(1-fade)+b*fade for a,b in zip((.007,.0026,.0012),color)]
                rgba.extend((*color,1))
            else:rgba.extend((*[v*fac for v in base],1))
    painted.attributes['position'].data.foreach_set('vector',positions);radius.data.foreach_set('value',radii);colors.data.foreach_set('color',rgba)
    ob=bpy.data.objects.new(painted.name,painted);bpy.context.scene.collection.objects.link(ob)
    material=bpy.data.materials.new('MF_integrated24_hair_coherent_paint');material.use_nodes=True
    n,l=material.node_tree.nodes,material.node_tree.links;p=n.get('Principled BSDF');attr=n.new('ShaderNodeAttribute');attr.attribute_name='MF_paint'
    l.new(attr.outputs['Color'],p.inputs['Base Color']);l.new(attr.outputs['Color'],p.inputs['Emission Color'])
    p.inputs['Roughness'].default_value=.9;p.inputs['Specular IOR Level'].default_value=0;p.inputs['Emission Strength'].default_value=.8
    if candidate>=7:p.inputs['Emission Strength'].default_value=.3
    if candidate>=9:p.inputs['Emission Strength'].default_value=.75
    if candidate>=10:p.inputs['Emission Strength'].default_value=1.0
    if candidate>=15:p.inputs['Emission Strength'].default_value=.55
    painted.materials.append(material);main.hide_render=True
    ob['dependency']='Color-derived native curves; live source guides retained, regenerate after edits'
    if 16<=candidate<=18:implicit_surface(ob,rows,rgba,material,candidate)
    if candidate>=19:reference_curve_material(material,candidate)


def reference_curve_material(material,candidate):
    """Continuous crown coordinates over real curves; no beauty-image edits."""
    import bpy
    from hair_native_groom import REFBASE
    n,l=material.node_tree.nodes,material.node_tree.links;p=n.get('Principled BSDF')
    def mathnode(op,a,b=None):
        node=n.new('ShaderNodeMath');node.operation=op
        for i,value in enumerate((a,b)):
            if value is None:continue
            if isinstance(value,(float,int)):node.inputs[i].default_value=value
            else:l.new(value,node.inputs[i])
        return node.outputs[0]
    geo=n.new('ShaderNodeNewGeometry');xyz=n.new('ShaderNodeSeparateXYZ');l.new(geo.outputs['Position'],xyz.inputs[0])
    angle=mathnode('ARCTAN2',xyz.outputs['X'],mathnode('MAXIMUM',mathnode('ABSOLUTE',xyz.outputs['Y']),.22))
    u=mathnode('DIVIDE',mathnode('ADD',mathnode('MULTIPLY',angle,175),491),955)
    v=mathnode('SUBTRACT',1,mathnode('DIVIDE',mathnode('SUBTRACT',542,mathnode('MULTIPLY',xyz.outputs['Z'],230)),1647))
    vector=n.new('ShaderNodeCombineXYZ');l.new(u,vector.inputs[0]);l.new(v,vector.inputs[1])
    tex=n.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(REFBASE/'frontal-v02-individualized.png'),check_existing=True);l.new(vector.outputs[0],tex.inputs[0])
    rgb=n.new('ShaderNodeSeparateColor');l.new(tex.outputs[0],rgb.inputs[0])
    valid=mathnode('MULTIPLY',mathnode('LESS_THAN',rgb.outputs['Red'],.42),mathnode('LESS_THAN',rgb.outputs['Blue'],rgb.outputs['Red']))
    if candidate>=20:valid=mathnode('MULTIPLY',valid,mathnode('GREATER_THAN',rgb.outputs['Red'],mathnode('MULTIPLY',rgb.outputs['Green'],1.18)))
    clean=n.new('ShaderNodeMixRGB');clean.inputs[1].default_value=(.008,.003,.0015,1)
    l.new(valid,clean.inputs[0]);l.new(tex.outputs[0],clean.inputs[2])
    attr=n.new('ShaderNodeAttribute');attr.attribute_name='MF_paint'
    dark=n.new('ShaderNodeMixRGB');dark.blend_type='MULTIPLY';dark.inputs[0].default_value=1;dark.inputs[2].default_value=(.50,.50,.50,1);l.new(attr.outputs[0],dark.inputs[1])
    if candidate>=20:
        dark.inputs[2].default_value=(.72,.72,.72,1)
        l.new(dark.outputs[0],clean.inputs[1])
    mix=n.new('ShaderNodeMixRGB');height=mathnode('MINIMUM',1,mathnode('MAXIMUM',0,mathnode('DIVIDE',mathnode('SUBTRACT',xyz.outputs['Z'],.30),.38)))
    if candidate>=20:
        front=mathnode('MINIMUM',1,mathnode('MAXIMUM',0,mathnode('DIVIDE',mathnode('SUBTRACT',-.08,xyz.outputs['Y']),.5)))
        height=mathnode('MULTIPLY',height,front)
    l.new(height,mix.inputs[0]);l.new(dark.outputs[0],mix.inputs[1]);l.new(clean.outputs[0],mix.inputs[2])
    l.new(mix.outputs[0],p.inputs['Base Color']);l.new(mix.outputs[0],p.inputs['Emission Color']);p.inputs['Emission Strength'].default_value=.4


def implicit_surface(curve_object,rows,rgba,material,candidate):
    """Union a dense donor-derived groom, not independently lofted patches."""
    import bpy,math
    from mathutils import Vector
    from mathutils.kdtree import KDTree
    vertices=[];faces=[];samples=[];sample_colors=[]
    stride=4
    for ci in range(0,len(rows),stride):
        row=rows[ci];base=len(vertices);n=len(row)
        for k,co in enumerate(row):
            center=Vector(co);t=k/max(1,n-1)
            tangent=(Vector(row[min(n-1,k+1)])-Vector(row[max(0,k-1)])).normalized()
            axis=tangent.cross(Vector((0,0,1)))
            if axis.length<.01:axis=tangent.cross(Vector((0,1,0)))
            axis.normalize();other=tangent.cross(axis).normalized()
            radius=.019*max(.08,(1-t)**.5)
            for j in range(4):
                angle=math.pi*j/2
                vertices.append(tuple(center+radius*(axis*math.cos(angle)+other*math.sin(angle))))
            samples.append(center);sample_colors.append(rgba[(ci*n+k)*4:(ci*n+k+1)*4])
        for k in range(n-1):
            for j in range(4):faces.append((base+k*4+j,base+k*4+(j+1)%4,base+(k+1)*4+(j+1)%4,base+(k+1)*4+j))
        faces.append(tuple(base+j for j in reversed(range(4))))
        faces.append(tuple(base+(n-1)*4+j for j in range(4)))
    mesh=bpy.data.meshes.new('MF_integrated24_hair_volume');mesh.from_pydata(vertices,[],faces);mesh.update()
    ob=bpy.data.objects.new(mesh.name,mesh);bpy.context.scene.collection.objects.link(ob)
    for other in bpy.context.selected_objects:other.select_set(False)
    ob.select_set(True);bpy.context.view_layer.objects.active=ob
    mesh.remesh_voxel_size=.014
    bpy.ops.object.voxel_remesh()
    mesh=ob.data
    if len(mesh.vertices)>2_000_000:raise ValueError('Hair surface vertex ceiling')
    tree=KDTree(len(samples))
    for i,p in enumerate(samples):tree.insert(p,i)
    tree.balance();colors=mesh.color_attributes.new(name='MF_paint',type='FLOAT_COLOR',domain='POINT')
    for v,c in zip(mesh.vertices,colors.data):
        _,index,_=tree.find(v.co);c.color=sample_colors[index]
    mesh.materials.append(material)
    for p in mesh.polygons:p.use_smooth=True
    smooth=ob.modifiers.new('Hair surface relaxation','SMOOTH');smooth.factor=.65;smooth.iterations=3
    curve_object.hide_render=True
    ob['dependency']='Rebuild fixed implicit surface after live guide edits; not live-bound'
    if candidate>=17:
        from hair_native_groom import REFBASE
        from hair_volume_sculpt import spline
        groups=cluster_paths(rows[::20],count=48)
        flow=KDTree(sum(len(mean) for mean,_ in groups));records=[]
        for group,(mean,_) in enumerate(groups):
            for k,p in enumerate(mean):
                flow.insert(Vector(p),len(records));records.append((group,k))
        flow.balance()
        path=[(490,270,0),(448,246,0),(371,278,0),(301,351,0),(246,424,0),(224,510,0),(236,687,0),(260,800,0)]
        uv=mesh.uv_layers.new(name='Reference_flow')
        for polygon in mesh.polygons:
            _,index,_=flow.find(polygon.center);group,k=records[index];mean=groups[group][0]
            center=Vector(mean[k]);tangent=(Vector(mean[min(47,k+1)])-Vector(mean[max(0,k-1)])).normalized()
            outward=Vector((center.x,center.y,max(.2,center.z-.2)));across=tangent.cross(outward).normalized()
            for li in polygon.loop_indices:
                point=mesh.vertices[mesh.loops[li].vertex_index].co
                t=max(.01,min(.99,k/47+(point-center).dot(tangent)/3.0))
                offset=max(-22,min(22,(point-center).dot(across)*120))
                q=Vector(spline(path,t));d=Vector(spline(path,min(1,t+.003)))-Vector(spline(path,max(0,t-.003)))
                side=Vector((-d.y,d.x,0)).normalized();q+=side*offset
                uv.data[li].uv=(q.x/955,1-q.y/1647)
        if candidate>=18:
            # Continuous material coordinates are a control for the failed
            # nearest-flow atlas seams. This does not alter source images.
            for loop in mesh.loops:
                q=mesh.vertices[loop.vertex_index].co
                angle=math.atan2(q.x,max(.22,abs(q.y)))
                uv.data[loop.index].uv=((491+angle*175)/955,1-(542-q.z*230)/1647)
        mat=material.copy();mat.name='MF_integrated24_hair_reference_flow_surface'
        n,l=mat.node_tree.nodes,mat.node_tree.links;p=n.get('Principled BSDF')
        tex=n.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(REFBASE/'frontal-v02-individualized.png'),check_existing=True)
        mapping=n.new('ShaderNodeUVMap');mapping.uv_map=uv.name;l.new(mapping.outputs[0],tex.inputs[0])
        l.new(tex.outputs['Color'],p.inputs['Base Color']);l.new(tex.outputs['Color'],p.inputs['Emission Color'])
        p.inputs['Emission Strength'].default_value=.45
        if candidate>=18:
            rgb=n.new('ShaderNodeSeparateColor');l.new(tex.outputs['Color'],rgb.inputs[0])
            red=n.new('ShaderNodeMath');red.operation='LESS_THAN';red.inputs[1].default_value=.42;l.new(rgb.outputs['Red'],red.inputs[0])
            blue=n.new('ShaderNodeMath');blue.operation='LESS_THAN';l.new(rgb.outputs['Blue'],blue.inputs[0]);l.new(rgb.outputs['Red'],blue.inputs[1])
            valid=n.new('ShaderNodeMath');valid.operation='MULTIPLY';l.new(red.outputs[0],valid.inputs[0]);l.new(blue.outputs[0],valid.inputs[1])
            mix=n.new('ShaderNodeMixRGB');mix.inputs[1].default_value=(.008,.003,.0015,1)
            l.new(valid.outputs[0],mix.inputs[0]);l.new(tex.outputs['Color'],mix.inputs[2]);l.new(mix.outputs[0],p.inputs['Base Color']);l.new(mix.outputs[0],p.inputs['Emission Color'])
        mesh.materials.clear();mesh.materials.append(mat)


def clustered_locks(main,candidate):
    import bpy,math
    import numpy as np
    from mathutils import Vector
    from hair_volume_sculpt import spline
    paths=[[tuple(main.matrix_world@p.position) for p in c.points] for c in main.data.curves]
    groups=cluster_paths(paths,count=72 if candidate>=5 else 36)
    from mathutils.bvhtree import BVHTree
    head=bpy.data.objects['MF_continuous_head_neck']
    scalp=BVHTree.FromPolygons([head.matrix_world@v.co for v in head.data.vertices],[list(p.vertices) for p in head.data.polygons])
    material=bpy.data.materials.new('MF_integrated24_hair_cluster_paint');material.use_nodes=True
    n,l=material.node_tree.nodes,material.node_tree.links;p=n.get('Principled BSDF')
    p.inputs['Roughness'].default_value=.85;p.inputs['Specular IOR Level'].default_value=.08
    uv=n.new('ShaderNodeTexCoord');scale=n.new('ShaderNodeVectorMath');scale.operation='MULTIPLY';scale.inputs[1].default_value=(5,105,1)
    if candidate>=5:scale.inputs[1].default_value=(5,28,1)
    noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=1;noise.inputs['Detail'].default_value=2;noise.inputs['Roughness'].default_value=.65
    ramp=n.new('ShaderNodeValToRGB');r=ramp.color_ramp;r.interpolation='CONSTANT'
    palette=[(.0,(.004,.0015,.0008,1)),(.36,(.014,.0055,.0025,1)),(.46,(.033,.014,.006,1)),(.55,(.067,.030,.015,1)),(.63,(.12,.060,.033,1)),(.72,(.18,.10,.06,1))]
    for i,(pos,col) in enumerate(palette):
        e=r.elements[i] if i<2 else r.elements.new(pos);e.position=pos;e.color=col
    l.new(uv.outputs['UV'],scale.inputs[0]);l.new(scale.outputs[0],noise.inputs['Vector']);l.new(noise.outputs['Fac'],ramp.inputs['Fac'])
    l.new(ramp.outputs[0],p.inputs['Base Color']);l.new(ramp.outputs[0],p.inputs['Emission Color']);p.inputs['Emission Strength'].default_value=.30
    verts=[];faces=[];uvs=[];nr=12;ns=64
    for idx,(mean,members) in enumerate(groups):
        points=[Vector(p) for p in mean]
        for _ in range(14):points=[points[0]]+[(points[i-1]+points[i]*2+points[i+1])/4 for i in range(1,len(points)-1)]+[points[-1]]
        points=[tuple(p) for p in points];base=len(verts)
        if candidate>=5:
            start=Vector(points[0]);hit,normal,_,_=scalp.find_nearest(start);delta=hit+normal*.014-start
            points=[tuple(Vector(p)+delta*max(0,1-i/12)**2) for i,p in enumerate(points)]
        for i in range(ns):
            t=i/(ns-1);center=Vector(spline(points,t));tangent=(Vector(spline(points,min(1,t+.005)))-Vector(spline(points,max(0,t-.005)))).normalized()
            outward=Vector((center.x,center.y+.04,max(.18,center.z-.15)));outward=(outward-tangent*outward.dot(tangent)).normalized();across=tangent.cross(outward).normalized()
            sample=np.array([p[min(47,int(t*47))] for p in members]);spread=float(np.std((sample-np.array(center))@np.array(across)))
            width=min(.15,max(.04,.028+spread*1.4));depth=width*.32;taper=max(.001,math.sin(math.pi*t)**.44)
            if candidate>=5:width=min(.18,max(.065,.035+spread*1.7));depth=width*.24
            for j in range(nr):
                a=2*math.pi*j/nr;verts.append(tuple(center+across*(width*math.cos(a)*taper)+outward*(depth*math.sin(a)*taper)))
                uvs.append((t+idx*.379,j/nr))
        for i in range(ns-1):
            for j in range(nr):faces.append((base+i*nr+j,base+i*nr+(j+1)%nr,base+(i+1)*nr+(j+1)%nr,base+(i+1)*nr+j))
        faces.append(tuple(base+j for j in reversed(range(nr))));faces.append(tuple(base+(ns-1)*nr+j for j in range(nr)))
    mesh=bpy.data.meshes.new('MF_integrated24_hair_clustered_locks');mesh.from_pydata(verts,[],faces);mesh.update();mesh.materials.append(material)
    layer=mesh.uv_layers.new(name='clump_flow')
    for poly in mesh.polygons:
        poly.use_smooth=True
        for li in poly.loop_indices:layer.data[li].uv=uvs[mesh.loops[li].vertex_index]
    ob=bpy.data.objects.new(mesh.name,mesh);bpy.context.scene.collection.objects.link(ob)
    ob['dependency']='Derived from36 donor trajectory clusters; native guide edits require regeneration'


def authored_locks(main,candidate):
    """Closed illustrated clumps follow the artist-authored 3D guide flow."""
    import bpy,math,random
    from mathutils import Vector
    from hair_volume_sculpt import spline
    rng=random.Random(2402)
    mats=[]
    for i in range(6):
        m=bpy.data.materials.new('MF_integrated24_hair_lock_'+str(i));m.use_nodes=True
        p=m.node_tree.nodes.get('Principled BSDF');shade=.010+i*.004
        p.inputs['Base Color'].default_value=(shade,shade*.43,shade*.23,1)
        p.inputs['Roughness'].default_value=.78;p.inputs['Specular IOR Level'].default_value=.10
        p.inputs['Emission Color'].default_value=(shade,shade*.43,shade*.23,1);p.inputs['Emission Strength'].default_value=.3
        mats.append(m)
    accent=bpy.data.materials.new('MF_integrated24_hair_painted_accent');accent.use_nodes=True
    p=accent.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(.09,.045,.023,1);p.inputs['Roughness'].default_value=.9
    p.inputs['Emission Color'].default_value=(.09,.045,.023,1);p.inputs['Emission Strength'].default_value=.2
    verts=[];faces=[];mi=[]
    for idx,c in enumerate(main.data.curves):
        points=[tuple(main.matrix_world@p.position) for p in c.points]
        if candidate>=3:
            # Regularize the sparse artist control polygon, preserving roots
            # and endpoints, before deriving a broad visible clump surface.
            points=[Vector(spline(points,i/63)) for i in range(64)]
            for _ in range(12):
                points=[points[0]]+[(points[i-1]+points[i]*2+points[i+1])/4 for i in range(1,len(points)-1)]+[points[-1]]
            points=[tuple(p) for p in points]
        width=rng.uniform(.022,.050);depth=width*.27;material=rng.randrange(6)
        ns,nr=48,8;base=len(verts)
        for i in range(ns):
            t=i/(ns-1);center=Vector(spline(points,t))
            tangent=(Vector(spline(points,min(1,t+.005)))-Vector(spline(points,max(0,t-.005)))).normalized()
            outward=Vector((center.x,(center.y+.04),max(.18,center.z-.15)))
            outward=(outward-tangent*outward.dot(tangent)).normalized()
            across=tangent.cross(outward).normalized()
            taper=.10+.90*math.sin(math.pi*t)**.5 if candidate<3 else max(.001,math.sin(math.pi*t)**.65)
            for j in range(nr):
                a=2*math.pi*j/nr
                verts.append(tuple(center+across*(width*math.cos(a)*taper)+outward*(depth*math.sin(a)*taper)))
        for i in range(ns-1):
            for j in range(nr):
                faces.append((base+i*nr+j,base+i*nr+(j+1)%nr,base+(i+1)*nr+(j+1)%nr,base+(i+1)*nr+j));mi.append(material)
        faces.append(tuple(base+j for j in reversed(range(nr))));mi.append(material)
        faces.append(tuple(base+(ns-1)*nr+j for j in range(nr)));mi.append(material)
        # Short, unequal surface accents rather than one highlight per fiber.
        for stroke in range(2):
            begin=rng.uniform(.10,.28);end=rng.uniform(.48,.78);offset=rng.uniform(-.48,.48)
            b=len(verts);n=22
            for i in range(n):
                u=i/(n-1);t=begin+(end-begin)*u;center=Vector(spline(points,t))
                tangent=(Vector(spline(points,min(1,t+.005)))-Vector(spline(points,max(0,t-.005)))).normalized()
                outward=Vector((center.x,center.y+.04,max(.18,center.z-.15)));outward=(outward-tangent*outward.dot(tangent)).normalized()
                across=tangent.cross(outward).normalized();taper=.10+.90*math.sin(math.pi*t)**.5 if candidate<3 else max(.001,math.sin(math.pi*t)**.65)
                half=width*(.075 if candidate<3 else .20)*math.sin(math.pi*u)**.65
                for side in (-1,1):
                    v=offset+side*half/width
                    verts.append(tuple(center+across*(width*v*taper)+outward*(depth*math.sqrt(max(0,1-v*v))*taper+.001)))
            for i in range(n-1):faces.append((b+i*2,b+i*2+1,b+i*2+3,b+i*2+2));mi.append(6)
    mesh=bpy.data.meshes.new('MF_integrated24_hair_authored_locks');mesh.from_pydata(verts,[],faces);mesh.update()
    ob=bpy.data.objects.new(mesh.name,mesh);bpy.context.scene.collection.objects.link(ob)
    for m in mats+[accent]:mesh.materials.append(m)
    for p,index in zip(mesh.polygons,mi):p.material_index=index;p.use_smooth=True
    ob['dependency']='Artist-authored donor guides; generated clump skin is not live-bound yet'


def live_verify(job):
    out=validate_live(job)
    import bpy
    from mathutils import Vector
    from hair_native_groom import digest
    from illustrated_hair_section import protection
    checkpoint=BASE/'donor23-live-preview-03'
    record=json.loads((checkpoint/'result.json').read_text())
    native=checkpoint/'diagnostic-live-groom.blend'
    out.mkdir();shutil.copyfile(Path(__file__),out/'handler-source.py')
    bpy.ops.wm.open_mainfile(filepath=str(native),load_ui=False,use_scripts=False)
    main=bpy.data.objects['MF_donor23_hair_long hair main']
    baseline=curve_state(main)
    assert baseline==record['baseline']
    assert protection()==record['protected_digest']
    probe=main.data.curves[0].points[min(4,len(main.data.curves[0].points)-1)]
    old=probe.position.copy();probe.position=old+Vector((0,-.08,.04));main.data.update_tag()
    changed=curve_state(main)
    assert changed==record['changed'] and changed!=baseline
    probe.position=old;main.data.update_tag()
    assert curve_state(main)==baseline and protection()==record['protected_digest']
    assert digest(native)==record['native_sha256']
    (out/'verification.json').write_text(json.dumps({'fresh_reopen_exact':True,'controlled_revision_exact':True,'rollback_exact':True,'protected_exact':True,'checkpoint_unchanged':True,'native_sha256':record['native_sha256'],'review_ready':False,'motion':'NOT_RUN'},indent=2)+'\n')


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
    if isinstance(job,dict) and job.get('operation')=='live-inspect':live_inspect(job)
    elif isinstance(job,dict) and job.get('operation')=='root-audit':root_audit(job)
    elif isinstance(job,dict) and job.get('operation') in ('surface-preview','surface-package','surface-seal','surface-probe'):surface_preview(job)
    elif isinstance(job,dict) and job.get('operation')=='surface-verify':integrated_verify(job)
    elif isinstance(job,dict) and job.get('operation')=='live-preview':live_preview(job)
    elif isinstance(job,dict) and job.get('operation')=='live-verify':live_verify(job)
    elif isinstance(job,dict) and job.get('operation')=='inspect-demo':inspect_demo(job)
    elif isinstance(job,dict) and job.get('operation')=='fit-demo':fit_demo(job)
    elif isinstance(job,dict) and job.get('operation')=='authored-fit':authored_fit(job)
    else:run(job)
