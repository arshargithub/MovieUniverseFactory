"""Fixed, local Sikh construction study. Reviewed code, not runtime code generation.

MPFB supplies the coherent editable anatomy. This handler authors individual
features, rooted facial hair and an original wrapped cloth construction. The
construction is an artistic rest state, not a textile tying simulation.
"""
import hashlib
import importlib
import json
import math
import os
from pathlib import Path
import random
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'scripts'))
sys.path.insert(0, str(ROOT/'src'))
from mpfb264_setup import verify_sources, MODULE, INSTALLED
CROWN_METHOD = 'donor_control'
CLOTH_SOURCE = 14
ASSEMBLY_CLOTH = 21

MORPHS = {
    'head/head-scale-vert-incr': .50,
    'head/head-rectangular': .22,
    'head/head-age-incr': .38,
    'head/head-fat-decr': .58,
    'chin/chin-height-incr': .16,
    'chin/chin-bones-incr': .27,
    'nose/nose-scale-depth-incr': .82,
    'nose/nose-hump-incr': .44,
    'nose/nose-scale-vert-incr': .24,
    'nose/nose-width1-incr': .38,
    'nose/nose-width3-incr': .40,
    'nose/nose-point-down': .10,
    'eyebrows/eyebrows-trans-forward': .72,
    'eyebrows/eyebrows-trans-down': .18,
    'cheek/l-cheek-bones-incr': .48,
    'cheek/r-cheek-bones-incr': .44,
    'eyes/l-eye-height2-incr': .08,
    'eyes/r-eye-height2-incr': .08,
    'eyes/l-eye-eyefold-up': .22,
    'eyes/r-eye-eyefold-up': .22,
    'eyes/l-eye-epicanthus-out': .30,
    'eyes/r-eye-epicanthus-out': .30,
}


def validate(job):
    if (not isinstance(job, dict) or set(job) != {'operation', 'attempt'}
            or job['operation'] not in {'build', 'reopen', 'inspect', 'cloth', 'assemble'}
            or type(job['attempt']) is not int or not 1 <= job['attempt'] <= 30):
        raise ValueError('Fixed build/reopen and integer attempt1..30 required')
    return ROOT/'.runtime/art-direction/series01-sikh269'/f"candidate-{job['attempt']:02d}"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def packet(job):
    from movie_factory import production_knowledge as pk
    files = ['AGENTS.md','docs/planning/SERIES_01_SIKH_ASSET_STRATEGY_262.md',
             'docs/planning/SERIES_01_SIKH_BASELINE_V01.md','scripts/sikh269_character.py',
             'scripts/mpfb264_setup.py','scripts/sikh257_native.py','scripts/sikh261_character.py',
             'tests/test_sikh269_character.py','results/sikh263/file-manifest.json',
             '.runtime/art-direction/series01-sikh257/sikh-uncovered-concept-v03.png',
             '.runtime/assets/series01-sikh261-turban/sikh_turban.glb',
             '.runtime/assets/series01-sikh263-donors/mpfb-2.0.18.zip']
    if job['operation']!='build':
        source=validate(dict(operation='build',attempt=CLOTH_SOURCE)) if job['operation'] in {'cloth','assemble'} else validate(job)
        files.append(str((source/'character.blend').relative_to(ROOT)))
    if job['operation']=='assemble' or (job['operation']=='reopen' and job['attempt']>=22):
        source=validate(dict(operation='cloth',attempt=ASSEMBLY_CLOTH))
        files.extend(str((source/p).relative_to(ROOT)) for p in ('cloth.json','cloth-motion.npz'))
    task = dict(id=f"sikh269-{job['operation']}-{job['attempt']:02d}",operation='modeling',entities=['sikh'],
        query='individual face eyelid beard original Sikh tied crown rear cloth route release hand contact',
        intent='Director269 sustained native construction; independent face and crown feasibility. No accepted master edits, paid calls, new installs or production qualification.',
        phase='execution', inputs={p:sha(ROOT/p) for p in files},open_decisions=[],
        execution_authority=dict(source=files[1],scope='Director269 native face and turban construction and internal proof'),max_context_characters=42000)
    result=pk.task_packet(ROOT,task)
    out=ROOT/'.runtime/knowledge-pilot213'/task['id'];out.parent.mkdir(parents=True,exist_ok=True)
    out.with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n')
    out.with_suffix('.md').write_text(pk.packet_markdown(result))
    if not result['dispatch_ready']:raise ValueError(result['blockers'])
    return result,out


def launch(job, prepare=False):
    out=validate(job);proof,pp=packet(job)
    if prepare:
        print(pp.with_suffix('.md'));return
    out.mkdir(parents=True,exist_ok=True)
    receipt=out/(job['operation']+'-receipt.json')
    if receipt.exists() or (out/(job['operation']+'.log')).exists():raise ValueError('Preserve prior dispatch')
    # Full executed sources retained before dispatch; no .env is read or inherited.
    (out/(job['operation']+'-source.py')).write_bytes(Path(__file__).read_bytes())
    env={k:os.environ[k] for k in ('PATH','HOME','TMPDIR','LANG','LC_ALL') if k in os.environ}
    env['CYCLES_METAL_DISABLE_BINARY_ARCHIVES']='1'
    start=time.time()
    with (out/(job['operation']+'.log')).open('w') as log:
        p=subprocess.run(['/Applications/Blender.app/Contents/MacOS/Blender','--background',
            '--offline-mode','--disable-autoexec','--python-exit-code','7','--python',str(Path(__file__).resolve()),
            '--',json.dumps(job)],env=env,stdout=log,stderr=subprocess.STDOUT)
    receipt.write_text(json.dumps(dict(returncode=p.returncode,seconds=time.time()-start,
        packet_digest=proof['packet_digest'],inputs=proof['task']['inputs']),indent=2)+'\n')
    if p.returncode or not (out/(job['operation']+'.json')).exists():raise RuntimeError(f'Native failure: {out}')
    print(out)


def wrap_point(theta, course, across, eye_z):
    """Original diagonal crown strip on a padded anatomical envelope.

    Course grows continuously around the head; rear crossover reverses the
    slope between inner/outer family. Rest construction, not solved draping.
    """
    blend=max(0,min(1,(course-2.75)/.5));blend=blend*blend*(3-2*blend)
    slope = .40*(1-2*blend)
    latitude=-.16+.160*course+.18*math.cos(theta)+slope*math.sin(theta)+.36*across
    latitude=max(-1.15,min(1.48,latitude))
    scale=math.cos(latitude)
    r=.0015*course + .0007*math.cos(math.pi*across)**2 + .00015*math.sin(13*theta+2*across)*math.sin(math.pi*(across+.5))
    z=.043+(.130+r)*math.sin(latitude)
    return ((.105+r)*scale*math.sin(theta),
            -.024-(.125+r)*scale*math.cos(theta),eye_z+z)


def cloth_material():
    import bpy
    from sikh261_character import painted
    mat=painted('Indigo cotton | authored tonal weave',(.007,.014,.049),.24,75)
    n=mat.node_tree.nodes;l=mat.node_tree.links;b=n.get('Principled BSDF')
    b.inputs['Roughness'].default_value=.88
    b.inputs['Specular IOR Level'].default_value=.22
    b.inputs['Sheen Weight'].default_value=.22
    coord=n.new('ShaderNodeTexCoord');noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=1350
    l.new(coord.outputs['Generated'],noise.inputs['Vector'])
    bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.15;bump.inputs['Distance'].default_value=.00022
    l.new(noise.outputs['Fac'],bump.inputs['Height']);l.new(bump.outputs['Normal'],b.inputs['Normal'])
    return mat


def skin_material():
    """Authored dry painted surface, not a photographic identity projection."""
    import bpy
    from sikh261_character import painted
    mat=painted('Ochre skin | layered painted planes',(.31,.144,.063),.10,65)
    n=mat.node_tree.nodes;l=mat.node_tree.links;b=n.get('Principled BSDF')
    b.inputs['Roughness'].default_value=.83;b.inputs['Specular IOR Level'].default_value=.20
    coord=n.new('ShaderNodeTexCoord');cells=n.new('ShaderNodeTexVoronoi');cells.feature='F1'
    cells.inputs['Scale'].default_value=250;l.new(coord.outputs['Object'],cells.inputs['Vector'])
    ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.interpolation='CONSTANT'
    colors=[(.21,.087,.035,1),(.27,.122,.048,1),(.34,.169,.077,1),(.40,.211,.108,1)]
    ramp.color_ramp.elements.remove(ramp.color_ramp.elements[1])
    ramp.color_ramp.elements[0].position=0;ramp.color_ramp.elements[0].color=colors[0]
    for position,color in zip((.34,.48,.64),colors[1:]):ramp.color_ramp.elements.new(position).color=color
    l.new(cells.outputs['Color'],ramp.inputs[0])
    prior=b.inputs['Base Color'].links[0].from_socket
    mix=n.new('ShaderNodeMixRGB');mix.inputs[0].default_value=.055
    l.new(prior,mix.inputs[1]);l.new(ramp.outputs[0],mix.inputs[2]);l.new(mix.outputs[0],b.inputs['Base Color'])
    attr=n.new('ShaderNodeVertexColor');attr.layer_name='Anatomical pigment'
    region=n.new('ShaderNodeMixRGB');region.blend_type='MULTIPLY';region.inputs[0].default_value=1
    l.new(mix.outputs[0],region.inputs[1]);l.new(attr.outputs['Color'],region.inputs[2]);l.new(region.outputs[0],b.inputs['Base Color'])
    micro=n.new('ShaderNodeTexNoise');micro.inputs['Scale'].default_value=1800;micro.inputs['Detail'].default_value=2
    l.new(coord.outputs['Object'],micro.inputs['Vector'])
    bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.23;bump.inputs['Distance'].default_value=.00032
    l.new(micro.outputs['Fac'],bump.inputs['Height']);l.new(bump.outputs[0],b.inputs['Normal'])
    return mat


def skin_regions(body,eye_z):
    from mathutils import Vector
    attr=body.data.color_attributes.new(name='Anatomical pigment',type='FLOAT_COLOR',domain='POINT')
    keys=body.data.shape_keys.key_blocks;basis=keys[0]
    for i,v in enumerate(body.data.vertices):
        p=basis.data[i].co.copy()
        for key in list(keys)[1:]:
            if abs(key.value)>.00001:p+=(key.data[i].co-basis.data[i].co)*key.value
        x,y,z=p;front=max(0,min(1,(-y-.07)/.045));dz=z-eye_z
        eye=math.exp(-((abs(x)-.031)/.023)**4-((dz+.010)/.012)**2)*front
        lip=math.exp(-(x/.027)**6-((dz+.075)/.009)**4)*front
        cheek=math.exp(-((abs(x)-.052)/.025)**4-((dz+.036)/.030)**2)*front
        a=1-.22*eye+.035*cheek
        attr.data[i].color=(a*(1-.08*lip),a*(1-.27*lip),a*(1-.18*lip),1)


def crown(eye_z):
    import bpy
    from sikh257_native import mesh
    # Continuous visible rest shell: no intersecting offset ribbons. Fold
    # courses are part of the surface; this is NOT a solved tying simulation.
    mat=cloth_material();verts=[];faces=[];nr=201;nc=192
    for i in range(nr):
        u=i/nr
        for j in range(nc):
            t=2*math.pi*j/nc
            bottom=-.52+(.72*(1-abs(math.sin(t))) if math.cos(t)>0 else .10*abs(math.cos(t)))
            p=bottom+(math.pi/2-bottom)*u+.53*math.sin(t)*math.sin(math.pi*u)
            phase=u*10+.09*math.sin(t*2)*math.sin(math.pi*u)
            f=phase%1
            fold=.0027*math.sin(math.pi*f)**.20
            fold+=.00035*math.sin(19*t+phase*4)*math.sin(math.pi*f)
            fold+=.00045*math.sin(phase*math.tau*2.5+1.3*math.sin(t*3))*math.sin(math.pi*f)
            r=math.cos(p)
            verts.append(((.111*r+fold)*math.sin(t)+.011*u*u,
                          -.024-(.127*r+fold)*math.cos(t),
                          eye_z+.035+.135*math.sin(p)+.004*math.sin(t)*u))
    for i in range(nr-1):
        for j in range(nc):
            a=i*nc+j;b=i*nc+(j+1)%nc;faces.append((a,a+nc,b+nc,b))
    pole=len(verts);verts.append((.011,-.024,eye_z+.170))
    for j in range(nc):faces.append(((nr-1)*nc+j,pole,(nr-1)*nc+(j+1)%nc))
    ob=mesh('Turban authored folded exterior | secured rest shell',verts,faces,mat)
    ob.modifiers.new('cotton thickness','SOLIDIFY').thickness=.001
    ob['representation']='Secured wrapped exterior; not a planar cloth tying simulation'
    return [ob]


def adapted_crown(out,eye_z):
    import bpy
    from sikh261_character import donor_crown
    from movie_factory.sikh257_contract import HERO_SOURCES
    for path,digest in HERO_SOURCES.items():
        if sha(ROOT/path)!=digest:raise ValueError('Crown source changed')
    ob=donor_crown(out)
    for v in ob.data.vertices:
        v.co.x*=.94;v.co.y=v.co.y*1.30-.030
        v.co.z=(v.co.z-1.640)*1.08+eye_z+.050
    smooth=ob.modifiers.new('Relax hard donor tessellation','SMOOTH');smooth.factor=.7;smooth.iterations=3
    sub=ob.modifiers.new('Retain authored fold silhouette','SUBSURF');sub.levels=2
    bpy.context.view_layer.update()
    refined=bpy.data.meshes.new_from_object(ob.evaluated_get(bpy.context.evaluated_depsgraph_get()))
    ob.modifiers.clear();ob.data=refined
    # Local fold relief follows the donor's large cloth panels. It is not
    # global random displacement and does not replace its major wrap route.
    original_normals=[v.normal.copy() for v in ob.data.vertices]
    for v,normal in zip(ob.data.vertices,original_normals):
        x,y,z=v.co;h=z-eye_z
        front=max(0,min(1,(-y-.01)/.05));left=max(0,min(1,(.02-x)/.04))
        mask=front*left*max(0,min(1,(h+.04)/.025))
        phase=(h-.90*x)/.018+.10*math.sin(y*44)
        f=phase%1
        relief=.0018*(1-f)**.45*min(1,f/.12)-.0003
        relief+=.00015*math.sin(phase*math.tau*2.2)
        v.co+=normal*relief*mask
        # Crown gets a modest asymmetric rise, not a flat geometric lid.
        v.co.z+=.014*max(0,min(1,(h-.05)/.08))*(.7+.3*math.sin(x*18))
    ob.data.materials.clear();ob.data.materials.append(cloth_material())
    return [ob]


def cover_control(eye_z):
    """Same garment's slack end: declared tucked root and two wearing poses.

    This is an attachment/clearance study, not a simulated hand release. The
    secured donor exterior and free span are separate control domains.
    """
    from mathutils import Vector
    from sikh257_native import mesh
    def sample(points,count):
        points=[Vector(p) for p in points];dense=[]
        for i in range(len(points)-1):
            p0=points[max(0,i-1)];p1=points[i];p2=points[i+1];p3=points[min(len(points)-1,i+2)]
            for j in range(40):
                t=j/40
                dense.append(.5*((2*p1)+(-p0+p2)*t+(2*p0-5*p1+4*p2-p3)*t*t+(-p0+3*p1-3*p2+p3)*t**3))
        dense.append(points[-1]);lengths=[0.]
        for a,b in zip(dense,dense[1:]):lengths.append(lengths[-1]+(b-a).length)
        result=[];index=0
        for i in range(count):
            d=lengths[-1]*i/(count-1)
            while index<len(dense)-2 and lengths[index+1]<d:index+=1
            f=(d-lengths[index])/max(1e-9,lengths[index+1]-lengths[index])
            result.append(dense[index].lerp(dense[index+1],f))
        return result,lengths[-1]
    covered,L=sample([(-.088,.032,eye_z-.012),(-.100,-.050,eye_z-.045),(-.080,-.125,eye_z-.065),(0,-.218,eye_z-.070),(.078,-.133,eye_z-.055),(.090,-.061,eye_z-.018)],101)
    released,D=sample([(-.088,.032,eye_z-.012),(-.105,.018,eye_z-.085),(-.145,-.025,eye_z-.185),(-.180,-.085,eye_z-.280),(-.160,-.145,eye_z-.390),(-.145,-.160,eye_z-.480)],101)
    root=released[0];released=[root+(p-root)*(L/D) for p in released]
    vs=[];loose=[];faces=[];cols=21
    for i,(a,b) in enumerate(zip(covered,released)):
        u=i/100;w=.035+.070*math.sin(math.pi*u)**.6
        for j in range(cols):
            q=j/(cols-1)-.5
            wrinkle=.0020*math.sin(q*math.pi*6+u*3)*math.sin(math.pi*u)
            relief=.020+.020*math.exp(-((q-.5)/.12)**2)-.007*math.exp(-((q-.25)/.12)**2)
            vs.append(a+Vector((0,-wrinkle+relief*math.sin(math.pi*u),q*w)))
            # Transverse direction rotates from vertical at the root into
            # the loose end's natural hanging cross-section.
            turn=min(1,u/.16)*math.pi/2
            loose.append(b+Vector((q*w*math.sin(turn),-wrinkle,q*w*math.cos(turn))))
    for i in range(100):
        for j in range(cols-1):
            a=i*cols+j;faces.append((a,a+cols,a+cols+1,a+1))
    ob=mesh('Turban own free end | attachment clearance study',vs,faces,cloth_material())
    ob.shape_key_add(name='Covered wearing state')
    key=ob.shape_key_add(name='Released drape study')
    for v,p in zip(key.data,loose):v.co=p
    key.value=1
    ob.modifiers.new('Soft fold edges','SUBSURF').levels=1
    ob.modifiers.new('Cotton thickness','SOLIDIFY').thickness=.0008
    ob['root_route']='Under secured crown behind anatomical right ear; free end tucked above left ear'
    ob['qualification']='Two wearing states only; no release/contact/dynamics qualification'
    return ob,dict(covered_centerline_length=L,released_centerline_length=L,root=list(root),scope='authored rest-state clearance only')


def cloth_study(out,eye_z):
    """Fixed supported free-end simulation; no real hand or bike claims."""
    import bpy
    from mathutils import Vector
    from sikh257_native import sphere,material,camera_at
    scene=bpy.context.scene;body=bpy.data.objects['Sikh269 coherent editable anatomy']
    old=bpy.data.objects.get('Turban own free end | attachment clearance study')
    if old:bpy.data.objects.remove(old,do_unlink=True)
    ob,info=cover_control(eye_z);ob.name='Free end cloth simulation control'
    ob.data.shape_keys.key_blocks['Released drape study'].value=0
    for m in list(ob.modifiers):ob.modifiers.remove(m)
    basis=ob.data.shape_keys.key_blocks[0]
    centers=[basis.data[i*21+10].co.copy() for i in range(101)]
    info['contact_fitted_centerline_length']=sum((b-a).length for a,b in zip(centers,centers[1:]))
    rest=ob.shape_key_add(name='Free span material rest',from_mix=False);rest.value=0
    length=info['covered_centerline_length'];cols=21
    for i,v in enumerate(rest.data):
        row=i//cols;q=(i%cols)/(cols-1)-.5;u=row/100
        v.co=(u*length,0,q*(.035+.070*math.sin(math.pi*u)**.6))
    hold=ob.shape_key_add(name='Hand target only | diagnostic',from_mix=False);hold.value=0
    for i,v in enumerate(hold.data):
        if i//cols>=99:v.co+=Vector((.025,-.130,-.030))
    lower=ob.shape_key_add(name='Hand lower only | diagnostic',from_mix=False);lower.value=0
    for i,v in enumerate(lower.data):
        if i//cols>=99:v.co+=Vector((-.180,0,-.200))
    for f,value in [(1,0),(16,0),(34,1),(96,1)]:hold.value=value;hold.keyframe_insert('value',frame=f)
    for f,value in [(1,0),(34,0),(54,1),(96,1)]:lower.value=value;lower.keyframe_insert('value',frame=f)
    pins=ob.vertex_groups.new(name='Root and hand supports');pins.add(list(range(cols*2)),1,'REPLACE')
    hand=ob.vertex_groups.new(name='Hand supports');hand.add(list(range(cols*99,cols*101)),1,'REPLACE')
    mix=ob.modifiers.new('Release hand support','VERTEX_WEIGHT_MIX');mix.vertex_group_a=pins.name;mix.vertex_group_b=hand.name;mix.mix_mode='ADD';mix.mix_set='ALL'
    mix.default_weight_a=0;mix.default_weight_b=0
    for f,value in [(1,1),(54,1),(58,0),(96,0)]:mix.mask_constant=value;mix.keyframe_insert('mask_constant',frame=f)
    body.modifiers.new('Character cloth contact','COLLISION');body.collision.thickness_outer=.0025
    # Collision must bound the rendered groom, not a convenient ellipsoid
    # that misses the cheek locks. This remains a rigid neutral-pose envelope.
    import bmesh
    hull=bmesh.new()
    for hair in bpy.context.scene.objects:
        if hair.type=='CURVE' and (hair.name.startswith('Rooted beard') or hair.name.startswith('Swept moustache')):
            for spline in hair.data.splines:
                for p in spline.points:hull.verts.new(hair.matrix_world@Vector(p.co[:3]))
    bmesh.ops.convex_hull(hull,input=list(hull.verts),use_existing_faces=False)
    bmesh.ops.delete(hull,geom=[v for v in hull.verts if not v.link_faces],context='VERTS')
    bmesh.ops.recalc_face_normals(hull,faces=list(hull.faces))
    data=bpy.data.meshes.new('Actual groom hull');hull.to_mesh(data);hull.free()
    proxy=bpy.data.objects.new('Actual groom contact envelope only',data);scene.collection.objects.link(proxy)
    proxy.hide_render=True;proxy.modifiers.new('Beard contact','COLLISION');proxy.collision.thickness_outer=.002
    # Retain the established257 evaluated-mesh path. All new keys explicitly
    # start at zero: relying on creation defaults caused the14-17 failures.
    weld=ob.modifiers.new('Dressed initial evaluation','WELD');weld.merge_threshold=.000001
    sim=ob.modifiers.new('Free end gravity and collision','CLOTH');st=sim.settings
    st.quality=12;st.mass=.015;st.tension_stiffness=40;st.compression_stiffness=40;st.shear_stiffness=20;st.bending_stiffness=.025;st.air_damping=3
    st.shrink_min=.025;st.shrink_max=.025
    st.vertex_group_mass=pins.name;st.pin_stiffness=1;st.rest_shape_key=None
    # Use the dressed metric with low bend resistance. The flat key remains
    # diagnostic; no claim of independently validated planar rest topology.
    sim.collision_settings.use_collision=True;sim.collision_settings.distance_min=.002
    sim.collision_settings.use_self_collision=True;sim.collision_settings.self_distance_min=.001
    sim.point_cache.frame_start=1;sim.point_cache.frame_end=96
    ob.modifiers.new('Cloth display smoothing','SUBSURF').levels=1
    ob.modifiers.new('Cloth thin surface','SOLIDIFY').thickness=.0008
    scene.frame_start=1;scene.frame_end=96;scene.cycles.samples=16
    scene.frame_set(1);bpy.context.view_layer.update()
    print('INITIAL_KEYS',[(k.name,k.value,list(k.data[0].co),k.relative_key.name) for k in ob.data.shape_keys.key_blocks],flush=True)
    print('INITIAL_OBJECT',list(ob.location),[list(r) for r in ob.matrix_world],ob.show_only_shape_key,ob.active_shape_key_index,flush=True)
    camera_at(scene.camera,(1.7,-3,eye_z+.03),(0,-.025,eye_z-.04))
    samples={};snapshots={};frame_points=[];polygons=None
    for f in range(1,97):
        scene.frame_set(f);bpy.context.view_layer.update()
        evaluated=ob.evaluated_get(bpy.context.evaluated_depsgraph_get())
        # Force the solver evaluation even at non-rendered frames.
        points=[ob.matrix_world@v.co for v in evaluated.data.vertices]
        if not all(all(math.isfinite(c) for c in p) for p in points):raise ValueError('Nonfinite cloth')
        if f==1 and min(p.z for p in points)<eye_z-.20:raise ValueError('Rest state replaced dressed state')
        if min(p.z for p in points)<eye_z-1. or max(p.z for p in points)>eye_z+.5:raise ValueError('Cloth escaped actor bounds')
        frame_points.append([list(p) for p in points])
        if polygons is None:polygons=[list(p.vertices) for p in evaluated.data.polygons]
        if f in (1,16,34,54,72,96):
            scene.render.filepath=str(out/f'cloth-{f:03d}.png');bpy.ops.render.render(write_still=True)
            samples[str(f)]=dict(bounds=[[min(p[a] for p in points) for a in range(3)],[max(p[a] for p in points) for a in range(3)]])
            print('CLOTH_FRAME',f,flush=True)
        if f in (16,96):snapshots[str(f)]=[list(v.co) for v in evaluated.data.vertices]
    # Native contains the solver/configuration; images are evaluated evidence.
    # Cache portability and full-motion visual acceptance remain unclaimed.
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'cloth-study.blend'))
    import numpy as np
    np.savez_compressed(out/'cloth-motion.npz',vertices=np.asarray(frame_points,dtype=np.float32))
    info.update(samples=samples,snapshots=snapshots,polygons=polygons,status='INTERNAL_UNREVIEWED',limits=['No real hand contact','No bike or body acting','Cache replay not qualified'])
    (out/'cloth.json').write_text(json.dumps(info,indent=2)+'\n')


def layered_crown(eye_z):
    from sikh257_native import mesh,sphere
    mat=cloth_material();verts=[];faces=[];cols=19;rows=1009
    for i in range(rows):
        u=7*(1-i/(rows-1));theta=-math.pi/2+math.tau*u
        for j in range(cols):verts.append(wrap_point(theta,u,j/(cols-1)-.5,eye_z))
    for i in range(rows-1):
        for j in range(cols-1):
            a=i*cols+j;faces.append((a,a+cols,a+cols+1,a+1))
    ob=mesh('Turban seven ordered cloth courses',verts,faces,mat)
    ob.modifiers.new('Soft fold subdivision','SUBSURF').levels=1
    ob.modifiers.new('Cotton thickness','SOLIDIFY').thickness=.0007
    # Concealed secured interior supports the original authored outer winding.
    cap=sphere('Secured cloth interior support',(0,-.024,eye_z+.043),(.103,.123,.129),mat)
    # Only the crown portion is needed; remove the lower hemisphere so it
    # cannot become a helmet covering the forehead or ears.
    import bmesh
    bm=bmesh.new();bm.from_mesh(cap.data)
    bmesh.ops.delete(bm,geom=[v for v in bm.verts if (cap.matrix_world@v.co).z<eye_z+.055],context='VERTS')
    bm.to_mesh(cap.data);bm.free()
    return [ob,cap]


def face_hair(body,eye_z):
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    import bpy
    from sikh261_character import painted,strands
    surface=BVHTree.FromObject(body,bpy.context.evaluated_depsgraph_get())
    rng=random.Random(269);groups=[[] for _ in range(4)]
    def hit(x,z):
        p,n,_,_=surface.ray_cast(Vector((x,-.5,z)),Vector((0,1,0)),1)
        return p,n
    # Roots across the actual cheeks/jaw, with dispersed irregular top edges.
    for i in range(11500):
        x=rng.uniform(-.076,.076);ax=abs(x)
        upper=eye_z-.073+.057*min(1,ax/.072)**1.6
        lower=eye_z-.108+.032*(ax/.076)**3
        z=rng.uniform(lower,upper)
        if ax<.017 and z>eye_z-.087:continue
        if rng.random()>min(1,(upper-z)/.009):continue
        p,n=hit(x,z)
        if p is None or p.y>-.045:continue
        start=p+n*.0007
        gx=round(x/.012)*.012;gz=round((z-eye_z)/.014)*.014+eye_z
        guide_phase=round(x/.012)*1.71+round((z-eye_z)/.014)*.73
        length=(.112+.023*math.sin(guide_phase*2.3))*(1-.15*ax/.076)
        # Individual root heights produce overlapping locks instead of a
        # common straight hem. Broad bottom; no centre-pointed goatee.
        end_z=max(eye_z-.224+.040*(ax/.076)**3,gz-length)+rng.uniform(-.012,.012)
        tip=Vector(((.75*x+.25*gx)*.93+.003*math.sin(guide_phase)+rng.uniform(-.008,.008),p.y-.026+.005*math.sin(guide_phase)+rng.uniform(-.014,.014),end_z))
        phase=guide_phase+rng.uniform(-.9,.9);pts=[]
        for j in range(17):
            t=j/16;w=math.sin(math.pi*t)
            pts.append(start.lerp(tip,t)+Vector((.006*w*math.sin(t*13+phase),-.015*w+.005*w*math.sin(t*13+phase),.003*w*math.sin(t*13+phase))))
        groups[rng.choices(range(4),weights=[.55,.27,.15,.03])[0]].append(pts)
    result=[]
    for k,(paths,color) in enumerate(zip(groups,[(.010,.006,.004),(.019,.010,.006),(.030,.016,.008),(.074,.046,.025)])):
        result.append(strands(f'Rooted beard fibers {k}',paths,painted(f'Beard pigment{k}',color,.22,110),.00022))
    # Moustache fibres flow out from the philtrum into lifted tips, not a
    # rectangular donor patch. Several root elevations overlap naturally.
    paths=[]
    for sign in (-1,1):
        for i in range(1150):
            x=sign*rng.uniform(.002,.027);z=eye_z-.059+rng.uniform(-.006,.003)
            p,n=hit(x,z)
            if p is None:continue
            extent=max(abs(x)+.010,rng.uniform(.029,.057))
            endz=eye_z-.079+.012*(extent/.057)**4+rng.uniform(-.006,.005)
            endpoint,normal=hit(sign*extent,endz)
            end=Vector((sign*extent,(endpoint.y if endpoint else p.y)-rng.uniform(.002,.006),endz))
            pts=[]
            for j in range(21):
                t=j/20;pt=(p+n*.001).lerp(end,t)
                pt.y-=.007*math.sin(math.pi*t)
                pt.z-=.003*math.sin(math.pi*t);pt.z+=.005*t**5
                pts.append(pt)
            paths.append(pts)
    result.append(strands('Swept moustache with lifted ends',paths,painted('Moustache black brown',(.014,.008,.004),.2,160),.00020))
    for sign in (-1,1):
        paths=[]
        for i in range(600):
            t=rng.random();x=sign*(.011+.045*t)
            z=eye_z+.009+.007*math.sin(math.pi*t)-.002*t+rng.uniform(-.004,.0035)
            p,n=hit(x,z)
            if p is None:continue
            paths.append([p+n*.0006,p+n*.0016+Vector((sign*.002,0,.002)),p+n*.0008+Vector((sign*.004,0,.003))])
        result.append(strands('Natural brow '+str(sign),paths,painted('Brow pigment'+str(sign),(.012,.006,.003),.2,120),.00030))
    return result


def assemble(out,source):
    """Package actual solved geometry, not a claim of actor/contact completion."""
    import bpy
    import numpy as np
    from mathutils import Vector
    from sikh257_native import mesh,camera_at
    scene=bpy.context.scene;cam=scene.camera
    record=json.loads((source/'build.json').read_text());eye_z=record['eye_z']
    # Rebuild the moustache as short overlapping growth following the actual
    # lip/cheek surface. The earlier straight root-to-tip fans read as patches.
    from mathutils.bvhtree import BVHTree
    from sikh261_character import strands,painted
    body=bpy.data.objects['Sikh269 coherent editable anatomy']
    surface=BVHTree.FromObject(body,bpy.context.evaluated_depsgraph_get())
    oldhair=bpy.data.objects.get('Swept moustache with lifted ends')
    if oldhair:bpy.data.objects.remove(oldhair,do_unlink=True)
    rng=random.Random(26923);paths=[]
    for side in (-1,1):
        for i in range(2400):
            startx=rng.uniform(.001,.032);endx=min(.062,startx+rng.uniform(.006,.035))
            startz=eye_z-.057-rng.uniform(0,.010)
            drop=rng.uniform(.006,.021)
            path=[];phase=rng.random()*math.tau
            for j in range(25):
                t=j/24;x=side*(startx+(endx-startx)*t)
                z=startz-drop*math.sin(math.pi*t*.65)+.010*(abs(x)/.060)**5
                z+=.0012*math.sin(t*8+phase)*math.sin(math.pi*t)
                p,n,_,_=surface.ray_cast(Vector((x,-.5,z)),Vector((0,1,0)),1.)
                if p is None:break
                p+=n*(.0006+.0025*math.sin(math.pi*t)+.0015*(i%7)/7)
                path.append(p)
            if len(path)==25:paths.append(path)
    moustache=strands('Moustache overlapping surface-following growth',paths,
        painted('Natural moustache pigment',(.012,.007,.003),.24,130),.00010)
    rig=body.parent
    if rig and rig.type=='ARMATURE':
        world=moustache.matrix_world.copy();moustache.parent=rig;moustache.parent_type='BONE';moustache.parent_bone='head'
        bpy.context.view_layer.update();moustache.matrix_world=world
    clothdir=validate(dict(operation='cloth',attempt=ASSEMBLY_CLOTH))
    cloth=json.loads((clothdir/'cloth.json').read_text())
    points=np.load(clothdir/'cloth-motion.npz')['vertices']
    if points.shape[0]!=96 or not np.isfinite(points).all():raise ValueError('Invalid solved trajectory')
    old=bpy.data.objects.get('Turban own free end | attachment clearance study')
    if old:bpy.data.objects.remove(old,do_unlink=True)
    ob=mesh('Turban free end | evaluated gravity control',points[0].tolist(),cloth['polygons'],cloth_material())
    ob.shape_key_add(name='Solved frame 001')
    for frame,coords in enumerate(points[1:],2):
        key=ob.shape_key_add(name=f'Solved frame {frame:03d}',from_mix=False);key.value=0
        key.data.foreach_set('co',coords.reshape(-1))
        for f,value in ((1,0),(frame-1,0),(frame,1),(frame+1,0)):
            key.value=value;key.keyframe_insert('value',frame=f)
        key.value=0
    action=ob.data.shape_keys.animation_data.action
    for layer in action.layers:
        for strip in layer.strips:
            for bag in strip.channelbags:
                for curve in bag.fcurves:
                    for key in curve.keyframe_points:key.interpolation='LINEAR'
    ob['qualification']='Measured fixed-body cloth control; invisible hand target; not actor uncover performance'
    # Dark living eyes: preserve anatomical placement; reduce the pale iris
    # and chalky sclera read from the rough generic diagnostic material.
    for side in ('L','R'):
        iris=bpy.data.objects['Brown iris '+side];pupil=bpy.data.objects['Pupil '+side]
        for v in iris.data.vertices:v.co.x*=1.12;v.co.z*=1.12
        for v in pupil.data.vertices:v.co.x*=1.18;v.co.z*=1.18
        for name,color,rough in [('Warm sclera '+side,(.22,.18,.145,1),.25),('Umber iris '+side,(.025,.010,.003,1),.28),('Pupil black '+side,(.0005,.0003,.0002,1),.18)]:
            mat=bpy.data.materials[name];bs=mat.node_tree.nodes.get('Principled BSDF')
            for link in list(bs.inputs['Base Color'].links):mat.node_tree.links.remove(link)
            bs.inputs['Base Color'].default_value=color;bs.inputs['Roughness'].default_value=rough
    scene.frame_start=1;scene.frame_end=96;scene.frame_set(96)
    scene.cycles.samples=32;scene.render.resolution_x=720;scene.render.resolution_y=900
    cam.data.ortho_scale=.52;target=Vector((0,-.025,eye_z-.005))
    for name,pos in [('front',(0,-3,eye_z)),('three-quarter',(1.7,-3,eye_z+.03)),('opposite',(-1.7,-3,eye_z+.03)),('profile',(3,0,eye_z)),('rear',(0,3,eye_z+.10)),('crown',(1,-1,eye_z+2))]:
        camera_at(cam,pos,target);scene.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True)
    scene.frame_set(16)
    for name,pos in [('covered-front',(0,-3,eye_z)),('covered-quarter',(1.7,-3,eye_z+.03))]:
        camera_at(cam,pos,target);scene.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True)
    scene.frame_set(96);camera_at(cam,(0,-3,eye_z),target);scene.render.filepath=str(out/'reopen.png')
    bpy.ops.file.pack_all();native=out/'character.blend';bpy.ops.wm.save_as_mainfile(filepath=str(native))
    record.update(native_sha256=sha(native),objects=sorted(o.name for o in bpy.data.objects),
        status='INTERNAL_UNREVIEWED',source_native_sha256=sha(source/'character.blend'),
        cloth_source_sha256=sha(clothdir/'cloth-motion.npz'),
        limits=['Unaccepted native appearance; illustrated visual finish not matched',
                'Secured crown and free end separate control domains; physical continuous textile not qualified',
                'Cloth fixed-body diagnostic, not actual crossing-hand reveal or motorcycle motion',
                'No facial performance or production acceptance'])
    (out/'build.json').write_text(json.dumps(record,indent=2)+'\n')
    (out/'assemble.json').write_text(json.dumps(record,indent=2)+'\n')


def build(job):
    out=validate(job)
    import bpy
    import addon_utils
    from mathutils import Vector
    from sikh257_native import scene_setup,camera_at,sphere
    from sikh261_character import painted
    verify_sources()
    if bpy.app.online_access:raise ValueError('Offline required')
    native=out/'character.blend'
    if job['operation']=='assemble':
        if native.exists():raise ValueError('Preserve previous candidate')
        source=validate(dict(operation='build',attempt=CLOTH_SOURCE))
        record=json.loads((source/'build.json').read_text())
        if sha(source/'character.blend')!=record['native_sha256']:raise ValueError('Native changed')
        bpy.ops.wm.open_mainfile(filepath=str(source/'character.blend'));assemble(out,source);return
    if job['operation']=='cloth':
        source=validate(dict(operation='build',attempt=CLOTH_SOURCE));native=source/'character.blend'
        record=json.loads((source/'build.json').read_text())
        if sha(native)!=record['native_sha256']:raise ValueError('Native changed')
        bpy.ops.wm.open_mainfile(filepath=str(native));cloth_study(out,record['eye_z']);return
    if job['operation']=='inspect':
        bpy.ops.wm.open_mainfile(filepath=str(native))
        body=bpy.data.objects['Sikh269 coherent editable anatomy']
        from mathutils.bvhtree import BVHTree
        surface=BVHTree.FromObject(body,bpy.context.evaluated_depsgraph_get())
        info=json.loads((out/'build.json').read_text());ez=info['eye_z']
        rays=[]
        for x in (0,.015,.025,.032,.040,.050,.065,.075):
            for dz in (-.12,-.10,-.08,-.06,-.04,-.02,-.01,0,.01,.02,.04,.08):
                p,n,idx,dist=surface.ray_cast(Vector((x,-.5,ez+dz)),Vector((0,1,0)),1.)
                rays.append(dict(x=x,dz=dz,hit=list(p) if p else None))
        (out/'inspect.json').write_text(json.dumps(dict(rays=rays,
            keys={k.name:k.value for k in body.data.shape_keys.key_blocks},
            groups=[v.name for v in body.vertex_groups if any(s in v.name for s in ('eye','lip','head','face'))]),indent=2))
        return
    if job['operation']=='reopen':
        record=json.loads((out/'build.json').read_text())
        if sha(native)!=record['native_sha256']:raise ValueError('Native changed')
        bpy.ops.wm.open_mainfile(filepath=str(native))
        if sorted(o.name for o in bpy.data.objects)!=record['objects']:raise ValueError('Inventory changed')
        maximum_error=None
        if 'cloth_source_sha256' in record:
            import numpy as np
            cache=validate(dict(operation='cloth',attempt=ASSEMBLY_CLOTH))/'cloth-motion.npz'
            if sha(cache)!=record['cloth_source_sha256']:raise ValueError('Cloth evidence changed')
            points=np.load(cache)['vertices'];ob=bpy.data.objects['Turban free end | evaluated gravity control']
            maximum_error=0
            for frame in (1,16,34,54,72,96):
                bpy.context.scene.frame_set(frame);bpy.context.view_layer.update()
                ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get())
                actual=np.asarray([list(v.co) for v in ev.data.vertices])
                error=float(np.max(np.abs(actual-points[frame-1])))
                maximum_error=max(maximum_error,error)
                if error>1e-6:raise ValueError(f'Embedded cloth differs at {frame}: {error}')
            bpy.context.scene.frame_set(16)
            bpy.context.scene.render.filepath=str(out/'reopen-covered.png');bpy.ops.render.render(write_still=True)
            bpy.context.scene.frame_set(96)
        bpy.context.scene.render.filepath=str(out/'reopen.png');bpy.ops.render.render(write_still=True)
        (out/'reopen.json').write_text(json.dumps({'native_sha256':sha(native),'inventory_matches':True,'embedded_cloth_max_error_m':maximum_error,'limits':'Geometry replay is not actor/contact or visual acceptance'}))
        return
    if native.exists():raise ValueError('Preserve previous candidate')
    scene,cam=scene_setup()
    addon_utils.enable(MODULE,default_set=False)
    services=importlib.import_module(MODULE+'.services')
    macro=services.TargetService.get_default_macro_info_dict()
    macro.update(gender=1.,age=.65,muscle=.62,weight=.43,height=.55)
    # Upstream labels are blend-basis names, not a claim about this individual
    # or an ethnic anatomical prescription. Shape chosen against the portrait.
    macro['race']={'caucasian':.90,'asian':.07,'african':.03}
    body=services.HumanService.create_human(macro_detail_dict=macro);body.name='Sikh269 coherent editable anatomy'
    for name,value in MORPHS.items():services.TargetService.load_target(body,str(INSTALLED/'data/targets'/f'{name}.target.gz'),weight=value)
    skin=skin_material()
    body.data.materials.clear();body.data.materials.append(skin)
    for poly in body.data.polygons:poly.use_smooth=True
    sub=body.modifiers.new('anatomical surface subdivision','SUBSURF');sub.levels=2
    rig=services.HumanService.add_builtin_rig(body,'default');bpy.context.view_layer.update()
    eyes=[rig.matrix_world@rig.data.bones['eye.'+s].head_local for s in ('L','R')]
    eye_z=sum(p.z for p in eyes)/2
    skin_regions(body,eye_z)
    for side,center in zip(('L','R'),eyes):
        center=center+Vector((0,-.005,.001))
        sphere('Eye sclera '+side,center,(.0121,.0121,.0121),painted('Warm sclera '+side,(.32,.27,.21),.02,70))
        sphere('Brown iris '+side,center+Vector((0,-.0115,0)),(.0051,.0012,.0051),painted('Umber iris '+side,(.063,.027,.008),.3,850))
        sphere('Pupil '+side,center+Vector((0,-.01255,0)),(.00225,.00065,.00225),painted('Pupil black '+side,(.001,.0007,.0005),0,10))
    face_hair(body,eye_z)
    if CROWN_METHOD=='donor_control':adapted_crown(out,eye_z)
    elif CROWN_METHOD=='layered_winding':layered_crown(eye_z)
    else:crown(eye_z)
    cover,cover_info=cover_control(eye_z)
    # Preserve actual world-space registration while attaching display
    # surfaces to the same head as the coherent body's rig.
    for ob in list(bpy.context.scene.objects):
        if ob!=body and ob.type in {'MESH','CURVE'}:
            world=ob.matrix_world.copy();ob.parent=rig;ob.parent_type='BONE';ob.parent_bone='head'
            bpy.context.view_layer.update();ob.matrix_world=world
    scene.cycles.samples=24;scene.render.resolution_x=640;scene.render.resolution_y=760
    scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast'
    bpy.data.objects['key'].data.energy=300;bpy.data.objects['key'].data.size=1.7
    bpy.data.objects['fill'].data.energy=65;bpy.data.objects['rim'].data.energy=95
    cam.data.ortho_scale=.59;target=Vector((0,-.025,eye_z-.04))
    record=dict(macro=macro,morphs=MORPHS,crown_method=CROWN_METHOD,cover=cover_info,eye_z=eye_z,eyes=[list(p) for p in eyes],
        limits=['Original crown rest construction, not tied cloth physics or continuous face end yet',
                'No facial performance, motorcycle fit, Director or production acceptance'],status='INTERNAL_UNREVIEWED')
    for name,pos in [('front',(0,-3,eye_z)),('three-quarter',(1.7,-3,eye_z+.03)),('opposite',(-1.7,-3,eye_z+.03)),('profile',(3,0,eye_z)),('rear',(0,3,eye_z+.10)),('crown',(1,-1,eye_z+2))]:
        camera_at(cam,pos,target);scene.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True)
    cover.data.shape_keys.key_blocks['Released drape study'].value=0
    for name,pos in [('covered-front',(0,-3,eye_z)),('covered-quarter',(1.7,-3,eye_z+.03))]:
        camera_at(cam,pos,target);scene.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True)
    cover.data.shape_keys.key_blocks['Released drape study'].value=1
    head=rig.pose.bones['head'];head.rotation_mode='XYZ';head.rotation_euler=(math.radians(12),0,math.radians(-12))
    camera_at(cam,(1.7,-3,eye_z+.03),target);scene.render.filepath=str(out/'bow-control.png');bpy.ops.render.render(write_still=True)
    head.rotation_euler=(0,0,0);bpy.context.view_layer.update()
    camera_at(cam,(0,-3,eye_z),target);scene.render.filepath=str(out/'front.png')
    bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(native))
    record.update(native_sha256=sha(native),objects=sorted(o.name for o in bpy.data.objects))
    (out/'build.json').write_text(json.dumps(record,indent=2)+'\n')


if __name__=='__main__':
    if '--' in sys.argv:
        args=sys.argv[sys.argv.index('--')+1:]
        if len(args)!=1:raise ValueError('One structured operation only')
        build(json.loads(args[0]))
    else:
        if len(sys.argv) not in (3,4):raise ValueError('operation attempt [--prepare]')
        if len(sys.argv)==4 and sys.argv[3]!='--prepare':raise ValueError('Invalid mode')
        launch({'operation':sys.argv[1],'attempt':int(sys.argv[2])},len(sys.argv)==4)
