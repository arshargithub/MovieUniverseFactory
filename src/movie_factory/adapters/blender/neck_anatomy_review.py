"""Geometry-only neck review on a fixed, approved-face costume candidate.

Exact structured operations, pinned source, no external code/assets/provider.
Native materials/clothing remain unchanged; clay overrides are render-only.
"""
import hashlib
import json
import math
from pathlib import Path
import shutil
import sys

ROOT=Path(__file__).resolve().parents[4]
BASE=ROOT/'.runtime/art-direction/series01-facebuilder-trial-01'
SOURCE=BASE/'upperbody-package-36/character-upperbody.blend'
SOURCE_SHA='983f128f82c51efd7b2ab35e06d8c679bbc3fdd38635eabd0687ccddbda71efa'
TOP=-.86
BOTTOM=-1.89
VIEWS=(('front',0),('left',-90),('right',90),('back',180),('three-quarter',-45))


def validate(job):
    if not isinstance(job,dict) or set(job)!={'operation','candidate'}:
        raise ValueError('Exact structured keys required')
    if job['operation'] not in ('build','verify','profile','template','raking') or type(job['candidate']) is not int or not 1<=job['candidate']<=7:
        raise ValueError('Unsupported operation or candidate')
    if SOURCE.is_symlink() or hashlib.sha256(SOURCE.read_bytes()).hexdigest()!=SOURCE_SHA:
        raise ValueError('Pinned source changed')
    out=BASE/f'neck-anatomy-{job["operation"]}-{job["candidate"]:02}'
    if out.exists() or shutil.disk_usage(BASE).free<5_000_000_000:
        raise ValueError('Existing output or disk low')
    return out


def bridge(a,b,da,db,t,length):
    """Single quintic, exact endpoint slopes and zero endpoint curvature."""
    v0=da*length;v1=db*length;delta=b-a
    c3=10*delta-6*v0-4*v1
    c4=-15*delta+8*v0+7*v1
    c5=6*delta-3*v0-3*v1
    return a+v0*t+c3*t**3+c4*t**4+c5*t**5


def cubic_bridge(a,b,da,db,t,length):
    return (2*t**3-3*t*t+1)*a+(t**3-2*t*t+t)*da*length+(-2*t**3+3*t*t)*b+(t**3-t*t)*db*length


def relief(x,z,angle,candidate):
    """Soft paired SCM approach and clavicle arcs, no central vertical ridge."""
    t=(TOP-z)/(TOP-BOTTOM)
    if not 0<t<1:return 0.
    envelope=math.sin(math.pi*t)**2
    front=max(0.,-math.cos(angle))**(.6 if candidate>=4 else 3)
    # Coordinates are already in the shortened-neck space of candidate 36.
    path=.15+.40*max(0.,min(1.,(z+1.56)/.70))
    scm=(.045 if candidate>=3 else .020)*math.exp(-((abs(x)-path)/.14)**2-((z+1.20)/.42)**2)
    clavicle_z=-1.55+.08*abs(x)
    clavicle=(.09 if candidate>=4 else .055 if candidate>=3 else .028)*math.exp(-((z-clavicle_z)/.13)**2)*(1-math.exp(-(x/.24)**2))
    notch=(.022 if candidate>=3 else .012)*math.exp(-(x/.20)**2-((z+1.48)/.14)**2)
    return (scm+clavicle-notch)*front*envelope


def smoother(t):
    t=max(0.,min(1.,t))
    return t**3*(10-15*t+6*t*t)


def bezier5(values,t):
    return sum(math.comb(5,i)*(1-t)**(5-i)*t**i*v for i,v in enumerate(values))


def spline_value(x,knots,values):
    """Natural cubic interpolant: continuous curvature, not layered rings."""
    # Small fixed tridiagonal solve, no external packages in the worker.
    n=len(knots);h=[b-a for a,b in zip(knots,knots[1:])]
    lower=[0.]*n;diag=[1.]*n;upper=[0.]*n;rhs=[0.]*n
    for i in range(1,n-1):
        lower[i]=h[i-1];diag[i]=2*(h[i-1]+h[i]);upper[i]=h[i]
        rhs[i]=6*((values[i+1]-values[i])/h[i]-(values[i]-values[i-1])/h[i-1])
    for i in range(1,n):
        f=lower[i]/diag[i-1];diag[i]-=f*upper[i-1];rhs[i]-=f*rhs[i-1]
    second=[0.]*n;second[-1]=rhs[-1]/diag[-1]
    for i in range(n-2,-1,-1):second[i]=(rhs[i]-upper[i]*second[i+1])/diag[i]
    i=next((i for i in range(n-1) if x<=knots[i+1]),n-2)
    a=(knots[i+1]-x)/h[i];b=(x-knots[i])/h[i]
    return a*values[i]+b*values[i+1]+((a**3-a)*second[i]+(b**3-b)*second[i+1])*h[i]**2/6


def taper_weight(x,y,z):
    angle=math.atan2(x,y-.1)
    ceiling=TOP+.56*smoother((math.cos(angle)+.8)/1.8)
    weight=smoother((ceiling-z)/.25)*smoother((z-BOTTOM)/.13)
    if z>=TOP:weight*=smoother((.70-math.hypot(x,y-.1))/.08)
    return weight


def taper_point(x,y,z,candidate):
    weight=taper_weight(x,y,z)
    if weight==0:return x,y,z
    angle=math.atan2(x,y-.1);depth=-z
    knots=(.30,.50,.75,1.0,1.15,1.35,1.55,1.75,1.89)
    rx=spline_value(depth,knots,(.585,.550,.525,.535,.585,.720,1.00,1.45,1.735))
    rear=spline_value(depth,(.30,.50,.75,1.,1.2,1.45,1.7,1.89),(.495,.475,.479,.509,.550,.610,.690,.768))
    front=spline_value(max(.86,depth),(.86,1.,1.2,1.45,1.7,1.89),(.695,.635,.628,.650,.727,.768))
    ry=rear+(front-rear)*smoother((1-math.cos(angle))/2)
    radius=1/math.sqrt((math.sin(angle)/rx)**2+(math.cos(angle)/ry)**2)
    xx=radius*math.sin(angle);yy=.1+radius*math.cos(angle)
    yy-=relief(xx,z,angle,4)
    return x+(xx-x)*weight,y+(yy-y)*weight,z


def anatomical_point(x,y,z,candidate):
    """Smooth oval shaft/shoulder fan; avoid propagating chin-ray noise."""
    if not BOTTOM<z<TOP:return x,y,z
    t=(TOP-z)/(TOP-BOTTOM);angle=math.atan2(x,y-.1)
    rx=bridge(.57,1.735,0,1.527,t,TOP-BOTTOM)
    ry=bridge(.65,.768,0,.199,t,TOP-BOTTOM)
    if candidate>=3:
        rx=bezier5((.57,.55,.49,.70,1.42,1.735),t)
        rear=bezier5((.56,.60,.60,.67,.727,.768),t)
        front=bezier5((.695,.62,.60,.67,.727,.768),t)
        ry=rear+(front-rear)*smoother((1-math.cos(angle))/2)
    radius=1/math.sqrt((math.sin(angle)/rx)**2+(math.cos(angle)/ry)**2)
    xx=radius*math.sin(angle);yy=.1+radius*math.cos(angle)
    yy-=relief(xx,z,angle,candidate)
    weight=smoother((TOP-z)/.26)*smoother((z-BOTTOM)/.16)
    return x*(1-weight)+xx*weight,y*(1-weight)+yy*weight,z


def signature(obj):
    from hijab_donor import material_signature
    # Curves and meshes are both protected outside the neck derivative.
    if obj.type=='MESH':
        geo=hashlib.sha256(json.dumps({'vertices':[list(v.co) for v in obj.data.vertices],
            'faces':[list(p.vertices) for p in obj.data.polygons],
            'matrix':[list(r) for r in obj.matrix_world],
            'uv':[[list(p.uv) for p in layer.data] for layer in obj.data.uv_layers],
            'shapes':{k.name:{'value':k.value,'vertices':[list(v.co) for v in k.data]} for k in obj.data.shape_keys.key_blocks} if obj.data.shape_keys else {}},sort_keys=True).encode()).hexdigest()
    else:
        geo=hashlib.sha256(json.dumps({'matrix':[list(r) for r in obj.matrix_world],
            'splines':[[list(p.co) for p in s.points] for s in obj.data.splines]},sort_keys=True).encode()).hexdigest()
    return {'geometry':geo,'materials':[material_signature(m) if m else None for m in obj.data.materials],
            'hide_render':obj.hide_render}


def posterior_weight(x,y,z):
    if not -.45>z>-1.48 or y<=.12 or abs(x)>=.70:return 0.
    return smoother((-.45-z)/.22)*smoother((z+1.48)/.24)*smoother((y-.12)/.18)*smoother((.70-abs(x))/.18)


def protected_vertex(x,y,z,candidate):
    if candidate>=6:return z>=TOP
    if candidate>=5:return taper_weight(x,y,z)==0
    if BOTTOM<z<TOP:return False
    if candidate>=4 and posterior_weight(x,y,z)>0:return False
    return True


def invariants(candidate,indices=None):
    import bpy
    from upperbody_refinement import protected_surface_digest
    from hijab_donor import material_signature
    obj=bpy.data.objects['MF_continuous_head_neck']
    return {'protected_surface':protected_surface_digest(obj) if candidate<4 or candidate>=6 else None,
            'protected_vertices':[(v.index,list(v.co)) for v in obj.data.vertices if (v.index in indices if indices is not None else protected_vertex(*v.co,candidate))],
            'neck_materials':[material_signature(m) for m in obj.data.materials],
            'uv':hashlib.sha256(json.dumps([[list(p.uv) for p in layer.data] for layer in obj.data.uv_layers]).encode()).hexdigest(),
            'other_objects':{o.name:signature(o) for o in bpy.context.scene.objects if o.type in ('MESH','CURVE') and o!=obj}}


def sculpt(candidate):
    import bpy
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    obj=bpy.data.objects['MF_continuous_head_neck'];bpy.context.view_layer.update()
    if candidate>=6:return template_neck_extension(candidate)
    if candidate>=5:
        moved=[]
        for v in obj.data.vertices:
            old=v.co.copy();v.co=taper_point(*old,candidate)
            if (v.co-old).length>0:moved.append((v.co-old).length)
        obj.data.update();bpy.context.view_layer.update()
        return {'edited_vertices':len(moved),'max_displacement':max(moved),
                'method':'curvature-continuous neck taper, angular anatomical boundary; no averaging of inherited bulge'}
    tree=BVHTree.FromObject(obj,bpy.context.evaluated_depsgraph_get())
    def radius(a,z):
        d=Vector((math.sin(a),math.cos(a),0));center=Vector((0,.1,z))
        hit,_,_,_=tree.ray_cast(center+d*4,-d,8)
        if hit is None:raise ValueError('Cross-section ray missed')
        return (hit-center).dot(d)
    count=512;table=[]
    for i in range(count):
        a=2*math.pi*i/count;r0=radius(a,TOP);r1=radius(a,BOTTOM)
        d0=(r0-radius(a,TOP+.04))/.04
        d1=(r1-radius(a,BOTTOM+.04))/.04
        table.append((r0,r1,d0,d1))
    displacement=[]
    for v in obj.data.vertices:
        x,y,z=v.co
        if not BOTTOM<z<TOP:continue
        if candidate>=2:
            new=Vector(anatomical_point(x,y,z,candidate))
            displacement.append((new-v.co).length);v.co=new
            continue
        a=math.atan2(x,y-.1)%(2*math.pi);f=a/(2*math.pi)*count;i=int(f);w=f-i
        support=[table[i][k]*(1-w)+table[(i+1)%count][k]*w for k in range(4)]
        r=bridge(*support,(TOP-z)/(TOP-BOTTOM),TOP-BOTTOM)
        if not .25<r<2.1:raise ValueError('Out-of-bounds radial bridge')
        xx=r*math.sin(a);yy=.1+r*math.cos(a)
        yy-=relief(xx,z,a,candidate)
        new=Vector((xx,yy,z));displacement.append((new-v.co).length);v.co=new
    obj.data.update();bpy.context.view_layer.update()
    if candidate>=4:
        # The inherited posterior band straddles the former horizontal guard.
        # Filter only posterior neck below the ears, never anterior jaw/face.
        tree=BVHTree.FromObject(obj,bpy.context.evaluated_depsgraph_get())
        original=[v.co.copy() for v in obj.data.vertices]
        for v,co in zip(obj.data.vertices,original):
            x,y,z=co;weight=posterior_weight(x,y,z)
            if weight==0:continue
            a=math.atan2(x,y-.1);d=Vector((math.sin(a),math.cos(a),0));center=Vector((0,.1,z))
            radii=[];weights=[]
            for j in range(-10,11):
                zz=z+j*.02;c=Vector((0,.1,zz));hit,_,_,_=tree.ray_cast(c+d*4,-d,8)
                if hit is None:raise ValueError('Posterior neck sampling missed')
                radii.append((hit-c).dot(d));weights.append(math.exp(-(j/6)**2))
            r=sum(r*w for r,w in zip(radii,weights))/sum(weights)
            target=center+d*r;v.co=co*(1-weight)+target*weight
        obj.data.update();bpy.context.view_layer.update()
    return {'edited_vertices':len(displacement),'max_displacement':max(displacement),
            'support':table,'top_z':TOP,'bottom_z':BOTTOM,
            'method':'single quintic radial bridge' if candidate==1 else 'smooth oval neck/shoulder fan with compact C2 boundary blending; subtle front anatomy; z unchanged'}


def template_neck_extension(candidate):
    import bpy
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    dg=bpy.context.evaluated_depsgraph_get();head=bpy.data.objects['FBHead']
    tree=BVHTree.FromObject(head,dg);obj=bpy.data.objects['MF_continuous_head_neck']
    def radius(a,z):
        d=Vector((math.sin(a),math.cos(a),0));c=Vector((0,.1,z))
        hit,_,_,_=tree.ray_cast(c+d*4,-d,8)
        if hit is None or (hit-c).dot(d)<=0:raise ValueError('Template cross-section incomplete')
        return (hit-c).dot(d)
    join=-1.0;bottom=-1.9;count=512;table=[]
    for i in range(count):
        a=2*math.pi*i/count;sa,ca=math.sin(a),math.cos(a)
        rear_depth=.94 if candidate>=7 else .99
        ry=.74+(rear_depth-.74)*smoother((ca+1)/2)
        r1=1/math.sqrt((sa/1.75)**2+(ca/ry)**2)
        depth_slope=.16+(.30-.16)*smoother((ca+1)/2)
        d1=r1**3*(sa**2*1.60/1.75**3+ca**2*depth_slope/ry**3)
        d0=(radius(a,join-.025)-radius(a,join+.025))/.05
        table.append((radius(a,join),r1,d0,d1))
    # Filter only slope noise; preserve the original joining surface exactly.
    slopes=[sum(table[(i+j)%count][2] for j in range(-5,6))/11 for i in range(count)]
    table=[(a,b,slopes[i],d) for i,(a,b,_,d) in enumerate(table)]
    moved=[]
    for v in obj.data.vertices:
        x,y,z=v.co
        if z>=TOP:continue
        a=math.atan2(x,y-.1)%(2*math.pi);sa,ca=math.sin(a),math.cos(a)
        if z>=join:r=radius(a,z)
        else:
            f=a/(2*math.pi)*count;i=int(f);w=f-i
            support=[table[i][k]*(1-w)+table[(i+1)%count][k]*w for k in range(4)]
            interpolator=cubic_bridge if candidate>=7 else bridge
            r=interpolator(*support,(join-z)/(join-bottom),join-bottom)
        if not .30<r<1.80:raise ValueError('Template extension out of bounds')
        xx=r*sa;yy=.1+r*ca
        yy-=(.65 if candidate>=7 else 1)*relief(xx,z,a,4)*smoother((join-z)/.22)
        new=Vector((xx,yy,z));moved.append((new-v.co).length);v.co=new
    obj.data.update();bpy.context.view_layer.update()
    return {'edited_vertices':len(moved),'max_displacement':max(moved),
            'method':'Original fitted neck retained through z=-1.0; continuous original-slope shoulder extension; no posterior neck mask',
            'template_join_z':join,'bottom_rear_radius':rear_depth,'extension_support':table,
            'extension_interpolation':'cubic' if candidate>=7 else 'quintic'}


def clay(out,name='MF_continuous_head_neck',raking=False):
    import bpy
    from hijab_donor import review
    for obj in bpy.context.scene.objects:
        if obj.type in ('MESH','CURVE'):obj.hide_render=obj.name!=name
    obj=bpy.data.objects[name];obj.hide_set(False)
    mat=bpy.data.materials.new('MF_neck_anatomy_clay');mat.use_nodes=True
    shader=mat.node_tree.nodes['Principled BSDF'];shader.inputs['Base Color'].default_value=(.35,.35,.35,1)
    shader.inputs['Roughness'].default_value=.8
    obj.data.materials.clear();obj.data.materials.append(mat)
    if not raking:review(bpy.context.scene,out,(0,-.1,-.55),4.8,VIEWS)
    else:
        from mathutils import Vector
        from matched_face_review import rotate_z
        scene=bpy.context.scene
        for ob in scene.objects:
            if ob.type=='LIGHT':ob.hide_render=True
        data=bpy.data.cameras.new('MF_anatomy_raking_camera');camera=bpy.data.objects.new(data.name,data);scene.collection.objects.link(camera)
        scene.camera=camera;data.type='ORTHO';data.ortho_scale=4.8
        ld=bpy.data.lights.new('MF_anatomy_raking_key','AREA');ld.energy=450;ld.shape='DISK';ld.size=2.5
        light=bpy.data.objects.new(ld.name,ld);scene.collection.objects.link(light)
        scene.world=bpy.data.worlds.new('MF_anatomy_raking_world');scene.world.use_nodes=True
        scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.035,.035,.035,1)
        scene.render.engine='CYCLES';scene.cycles.samples=32;scene.cycles.seed=0
        scene.render.resolution_x=640;scene.render.resolution_y=800;scene.render.resolution_percentage=100
        target=Vector((0,-.1,-.55))
        for name,degrees in (('front',0),('left-three-quarter',-45),('left',-90),('left-rear',-135),('back',180),('right-rear',135),('right',90),('right-three-quarter',45)):
            camera.location=target+Vector(rotate_z((0,-10,0),degrees));camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler()
            light.location=target+Vector(rotate_z((-4,-3,2.5),degrees));light.rotation_euler=(target-light.location).to_track_quat('-Z','Y').to_euler()
            scene.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True)


def profiles(name='MF_continuous_head_neck'):
    import bpy
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    obj=bpy.data.objects[name];bpy.context.view_layer.update()
    tree=BVHTree.FromObject(obj,bpy.context.evaluated_depsgraph_get());rows=[]
    for i in range(91):
        z=-.10-.02*i;values={}
        for degree in (0,30,60,90,120,150,180,210,240,270,300,330):
            angle=math.radians(degree);d=Vector((math.sin(angle),math.cos(angle),0));center=Vector((0,.1,z))
            hit,normal,_,_=tree.ray_cast(center+d*4,-d,8)
            values[str(degree)]={'radius':(hit-center).dot(d),'normal_z':normal.z} if hit is not None else None
        rows.append({'z':z,'directions':values})
    return rows


def run(job):
    out=validate(job)
    import bpy
    sys.path.insert(0,str(Path(__file__).resolve().parent))
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE),load_ui=False,use_scripts=False)
    baseline=invariants(job['candidate']);out.mkdir()
    indices={index for index,_ in baseline['protected_vertices']}
    original_z=[v.co.z for v in bpy.data.objects['MF_continuous_head_neck'].data.vertices]
    result={'job':job,'source_sha256':SOURCE_SHA,'handler_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'director_accepted':False,'scope':'Geometry-only static clay review, not anatomy/rig qualification'}
    if job['operation']=='build':
        result['geometry_edit']=sculpt(job['candidate'])
        assert invariants(job['candidate'],indices)==baseline,'Protected state changed'
        native=out/'character-upperbody.blend'
        bpy.ops.wm.save_as_mainfile(filepath=str(native))
        result['native_sha256']=hashlib.sha256(native.read_bytes()).hexdigest()
    else:
        folder=BASE/f'neck-anatomy-build-{job["candidate"]:02}'
        record=json.loads((folder/'result.json').read_text());native=folder/'character-upperbody.blend'
        result['native_sha256']=hashlib.sha256(native.read_bytes()).hexdigest()
        if result['native_sha256']!=record['native_sha256']:raise ValueError('Saved candidate changed')
        bpy.ops.wm.open_mainfile(filepath=str(native),load_ui=False,use_scripts=False)
        assert invariants(job['candidate'],indices)==baseline,'Protected state changed on reopen'
    result['protected_state_pass']=True;result['protected_surface_digest']=baseline['protected_surface']
    result['max_z_delta']=max(abs(v.co.z-z) for v,z in zip(bpy.data.objects['MF_continuous_head_neck'].data.vertices,original_z))
    assert result['max_z_delta']<1e-6,'Vertical proportion changed'
    result['protected_vertex_digest']=hashlib.sha256(json.dumps(baseline['protected_vertices']).encode()).hexdigest()
    result['protected_vertex_count']=len(baseline['protected_vertices'])
    result['posterior_exception']='Below ears z=-0.45..-1.48, y>0.12, abs(x)<0.70; smooth taper. Earlier full horizontal-plane digest not asserted.' if job['candidate']>=4 else None
    if job['candidate']>=5:result['posterior_exception']='Angular ceiling: z=-0.86 at anterior throat through z=-0.30 at nape; above -0.86 restricted to radial distance <0.70. Fixed source vertex protection set; jaw/ears excluded.'
    if job['candidate']>=6:result['posterior_exception']=None
    result['packed_images']=[{'name':im.name,'packed':bool(im.packed_file or im.packed_files)} for im in bpy.data.images if im.source=='FILE']
    assert all(im['packed'] for im in result['packed_images'])
    if job['operation']=='build':
        result['sections']=profiles()
        clay(out)
    if job['operation']=='template':clay(out,'FBHead')
    if job['operation']=='raking':clay(out,raking=True)
    if job['operation']=='profile':
        result['sections']=profiles()
        result['template_sections']=profiles('FBHead')
        for name in ('FBHead','MF_continuous_head_neck'):
            obj=bpy.data.objects[name];dg=bpy.context.evaluated_depsgraph_get();mesh=obj.evaluated_get(dg).to_mesh()
            result[name+'_bounds']=[[min(v.co[c] for v in mesh.vertices) for c in range(3)],[max(v.co[c] for v in mesh.vertices) for c in range(3)]]
            result[name+'_lower_rows']=[{'z':z,'count':len([v for v in mesh.vertices if abs(v.co.z-z)<.04]),
                'xs':[min([v.co.x for v in mesh.vertices if abs(v.co.z-z)<.04],default=None),max([v.co.x for v in mesh.vertices if abs(v.co.z-z)<.04],default=None)]} for z in (-.5,-.7,-.9,-1.1,-1.3,-1.5,-1.7,-1.9)]
            obj.evaluated_get(dg).to_mesh_clear()
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==SOURCE_SHA
    (out/'result.json').write_text(json.dumps(result,indent=2))


if __name__=='__main__':
    args=sys.argv[sys.argv.index('--')+1:]
    if len(args)!=1:raise ValueError('One structured job required')
    run(json.loads(Path(args[0]).read_text()))
