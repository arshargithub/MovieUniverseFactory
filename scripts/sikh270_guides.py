"""Fixed offline guide-based native study, with immutable source and bounded jobs.

Guide coordinates are authored data, not provider output or executable assets.
The secured crown is a rest surface; it is not a simulated tying process.
"""
import hashlib
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
SOURCE = '.runtime/art-direction/series01-sikh269/candidate-24/character.blend'
SOURCE_SHA = '13353e4e11cc1c31ae45341ede0e38d9dc6d5f8f157d4578dff35f4ccb5b81d7'
EYE = 1.665999174118042
# Ordered transverse guides: back, left rear, left ear, left temple, forehead,
# right forehead, right temple, right ear, right rear, back. Radians on envelope.
STATIONS = [-math.pi, -2.35, -1.57, -.8, .20, .67, 1.12, 1.57, 2.35, math.pi]
FOLDS = [
 ('ear-to-forehead edge',[-.56,-.52,-.53,-.14,.26,.02,-.39,-.51,-.52,-.56]),
 ('lower diagonal',[-.36,-.31,-.34,.04,.43,.25,-.14,-.30,-.33,-.36]),
 ('temple sweep',[-.16,-.12,-.14,.13,.61,.49,.13,-.10,-.12,-.16]),
 ('middle sweep',[.04,.08,.06,.36,.78,.67,.35,.11,.10,.04]),
 ('upper sweep',[.25,.30,.29,.56,.94,.84,.56,.33,.32,.25]),
 ('crown shoulder',[.48,.53,.53,.77,1.10,1.00,.77,.56,.55,.48]),
 ('crown return',[.73,.78,.79,.99,1.25,1.17,.98,.80,.80,.73]),
 ('top fold',[1.00,1.06,1.08,1.23,1.40,1.35,1.22,1.08,1.08,1.00]),
 ('crown closure',[1.32,1.36,1.38,1.44,1.51,1.49,1.44,1.38,1.38,1.32]),
 ('pole',[math.pi/2]*10),
]
# Regional guide paths, relative to the eye plane. Root is projected to skin.
# Descending roots at the lower face avoid a single long curtain from cheeks.
BEARD = [
 ('sideburn',[(.076,-.058,-.015),(.080,-.080,-.045),(.078,-.095,-.080),(.071,-.103,-.122)]),
 ('outer cheek',[(.066,-.105,-.041),(.075,-.116,-.075),(.078,-.116,-.121),(.065,-.118,-.175)]),
 ('mid cheek',[(.048,-.136,-.057),(.060,-.143,-.088),(.068,-.137,-.139),(.057,-.127,-.196)]),
 ('jaw corner',[(.069,-.085,-.089),(.078,-.099,-.120),(.074,-.108,-.166),(.051,-.110,-.210)]),
 ('chin flank',[(.029,-.147,-.099),(.042,-.168,-.127),(.045,-.165,-.176),(.031,-.139,-.219)]),
 ('chin center',[(.007,-.153,-.104),(.012,-.178,-.137),(.017,-.170,-.182),(.012,-.144,-.223)]),
 ('under jaw',[(.049,-.083,-.122),(.054,-.116,-.147),(.045,-.126,-.185),(.024,-.119,-.218)]),
 ('under chin',[(.012,-.111,-.125),(.015,-.142,-.151),(.019,-.146,-.191),(.007,-.126,-.221)]),
 ('lower lip',[(.010,-.158,-.086),(.015,-.169,-.106),(.023,-.176,-.133),(.026,-.169,-.160)]),
]


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def validate(job):
    if not isinstance(job,dict) or set(job)!={'operation','attempt'} or job['operation'] not in {'coarse','detail','look','reopen'} or type(job['attempt']) is not int or not 1<=job['attempt']<=30:
        raise ValueError('Bounded coarse/detail/reopen operation and attempt1..30 only')
    return ROOT/'.runtime/art-direction/series01-sikh270'/f"candidate-{job['attempt']:02d}"


def interpolate(values,theta):
    # Linear authored boundaries cannot overshoot or cross between stations.
    for i in range(len(STATIONS)-1):
        if theta<=STATIONS[i+1]:
            t=(theta-STATIONS[i])/(STATIONS[i+1]-STATIONS[i])
            return values[i]*(1-t)+values[i+1]*t
    return values[-1]


def crown_point(theta,course,f):
    a=interpolate(FOLDS[course][1],theta);b=interpolate(FOLDS[course+1][1],theta)
    p=a+(b-a)*f
    # The fabric lap is a small turned edge, not an inflated tube.
    relief=.0013*math.sin(math.pi*f)**.65
    # Small secondary pleat within selected broad courses; follows the same
    # named boundary rather than random displacement of the entire crown.
    if course in (0,2,4,5):relief+=.0006*math.sin(math.pi*f*2)**2
    r=math.cos(p)
    return ((.112*r+relief)*math.sin(theta)+.009*max(0,math.sin(p))**3,
            -.019-(.139*r+relief)*math.cos(theta),
            EYE+.033+.151*math.sin(p))


def prepare(job):
    from movie_factory import production_knowledge as pk
    files=['AGENTS.md','docs/planning/SERIES_01_SIKH_ASSET_STRATEGY_262.md',
           'docs/planning/SERIES_01_SIKH_BASELINE_V01.md','scripts/sikh270_guides.py',
           'scripts/sikh269_character.py','scripts/sikh257_native.py','scripts/sikh261_character.py','scripts/mpfb264_setup.py',
           'tests/test_sikh270_guides.py',SOURCE,
           '.runtime/art-direction/series01-sikh257/sikh-uncovered-concept-v03.png',
           'results/sikh269/observations.json']
    if sha(ROOT/SOURCE)!=SOURCE_SHA:raise ValueError('Protected foundation changed')
    if job['operation']=='reopen':files.append(str((validate(job)/'character.blend').relative_to(ROOT)))
    task=dict(id=f"sikh270-{job['operation']}-{job['attempt']:02d}",operation='modeling',entities=['sikh'],
        query='explicit crown fold guides beard cheek chin moustache volume eyes cloth ear release contact',
        intent='Director270 guide construction of Sikh face/turban candidate; static feasibility only, preserve accepted work and known motion dependencies.',
        phase='execution',inputs={p:sha(ROOT/p) for p in files},open_decisions=[],
        execution_authority=dict(source=files[1],scope='Director270 guide reconstruction and internal proof; no paid calls or new assets'),max_context_characters=42000)
    packet=pk.task_packet(ROOT,task);p=ROOT/'.runtime/knowledge-pilot213'/task['id']
    p.with_suffix('.json').write_text(json.dumps(packet,indent=2)+'\n');p.with_suffix('.md').write_text(pk.packet_markdown(packet))
    if not packet['dispatch_ready']:raise ValueError(packet['blockers'])
    return packet,p


def launch(job,only_prepare=False):
    out=validate(job);packet,p=prepare(job)
    if only_prepare:print(p.with_suffix('.md'));return
    out.mkdir(parents=True,exist_ok=True)
    log=out/(job['operation']+'.log')
    if log.exists():raise ValueError('Prior dispatch must be preserved')
    (out/(job['operation']+'-source.py')).write_bytes(Path(__file__).read_bytes())
    env={k:os.environ[k] for k in ('PATH','HOME','TMPDIR','LANG','LC_ALL') if k in os.environ}
    env['CYCLES_METAL_DISABLE_BINARY_ARCHIVES']='1';start=time.time()
    with log.open('w') as f:
        proc=subprocess.run(['/Applications/Blender.app/Contents/MacOS/Blender','--background','--offline-mode','--disable-autoexec','--python-exit-code','7','--python',str(Path(__file__).resolve()),'--',json.dumps(job)],env=env,stdout=f,stderr=subprocess.STDOUT)
    (out/(job['operation']+'-receipt.json')).write_text(json.dumps(dict(returncode=proc.returncode,seconds=time.time()-start,packet_digest=packet['packet_digest'],inputs=packet['task']['inputs']),indent=2))
    if proc.returncode:raise RuntimeError(str(log))
    print(out)


def crown(mat):
    from sikh257_native import mesh
    vs=[];fs=[];n=256;steps=12
    for k in range(len(FOLDS)-1):
        for row in range(steps):
            for j in range(n):vs.append(crown_point(-math.pi+math.tau*j/n,k,row/steps))
    rows=(len(FOLDS)-1)*steps
    for row in range(rows-1):
        for j in range(n):
            a=row*n+j;b=row*n+(j+1)%n;fs.append((a,b,b+n,a+n))
    vs.append((.009,-.019,EYE+.184));pole=len(vs)-1
    for j in range(n):fs.append(((rows-1)*n+j,(rows-1)*n+(j+1)%n,pole))
    ob=mesh('Sikh270 ordered diagonal crown guide loft',vs,fs,mat)
    ob.modifiers.new('Cloth smoothing','SUBSURF').levels=1
    ob.modifiers.new('Thin folded cotton','SOLIDIFY').thickness=.0007
    ob['construction']='Named ordered guide loft; secured rest surface, not tying simulation'
    # Dominant front-left fan: a supported overlapping sheet that climbs
    # diagonally into the upper return, not a floating helix around the head.
    vs=[];fs=[];nr=145;nc=57
    for i in range(nr):
        u=i/(nr-1);theta=-1.70+2.35*u
        for j in range(nc):
            v=j/(nc-1)
            phi=-.49+1.40*u+.36*v
            theta2=theta-.20*v*u
            tuck=max(0,(u-.84)/.16)**2+max(0,(.08-u)/.08)**2
            offset=.0013+.0008*math.sin(math.pi*(v*4%1))**.7-.005*tuck
            r=math.cos(phi)
            vs.append(((.112*r+offset)*math.sin(theta2)+.009*max(0,math.sin(phi))**3,
                       -.019-(.139*r+offset)*math.cos(theta2),EYE+.033+.151*math.sin(phi)))
    for i in range(nr-1):
        for j in range(nc-1):
            a=i*nc+j;fs.append((a,a+1,a+nc+1,a+nc))
    fan=mesh('Sikh270 supported diagonal front fan',vs,fs,mat)
    fan.modifiers.new('Fan cotton edge','SOLIDIFY').thickness=.0007
    fan.modifiers.new('Fan smoothing','SUBSURF').levels=1
    return ob


def catmull(points,t):
    from mathutils import Vector
    ps=[Vector(p) for p in points];u=t*(len(ps)-1);i=min(len(ps)-2,int(u));f=u-i
    p0=ps[max(0,i-1)];p1=ps[i];p2=ps[i+1];p3=ps[min(len(ps)-1,i+2)]
    return .5*((2*p1)+(-p0+p2)*f+(2*p0-5*p1+4*p2-p3)*f*f+(-p0+3*p1-3*p2+p3)*f**3)


def hair(body,detail):
    import bpy
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    from sikh261_character import strands,painted
    from sikh257_native import mesh
    surface=BVHTree.FromObject(body,bpy.context.evaluated_depsgraph_get())
    rng=random.Random(270);paths=[[] for _ in range(4)];allguides={}
    colors=[(.009,.006,.004),(.019,.012,.007),(.045,.030,.017),(.080,.055,.030)]
    mats=[painted('Sikh270 beard tone '+str(i),c,.18,100) for i,c in enumerate(colors)]
    for mat in mats:
        shader=mat.node_tree.nodes.get('Principled BSDF')
        shader.inputs['Roughness'].default_value=.43
        shader.inputs['Specular IOR Level'].default_value=.32
        shader.inputs['Sheen Weight'].default_value=.20
    for side in (-1,1):
        guides=[]
        for name,coords in BEARD:
            ps=[Vector((side*x,y,EYE+z)) for x,y,z in coords]
            hit=surface.find_nearest(ps[0])[0]
            if hit is None:raise ValueError('Root has no anatomical surface')
            ps[0]=hit+Vector((0,-.0004,0));guides.append(ps)
            allguides[f'{side}:{name}']=[list(p) for p in ps]
        # Continuous scalp sampling is independent of guide placement. The
        # nearest three guides supply a blended flow, not isolated bundles.
        for child in range(14000 if detail else 7000):
            x=side*rng.uniform(0,.078);ax=abs(x)
            upper=EYE-.077+.062*min(1,ax/.075)**1.45
            lower=EYE-.123+.036*(ax/.078)**3
            z=rng.uniform(lower,upper)
            if ax<.019 and z>EYE-.0805-.002*(1-ax/.019):continue
            if rng.random()>min(1,(upper-z)/.007):continue
            root,normal,_,_=surface.ray_cast(Vector((x,-.5,z)),Vector((0,1,0)),1)
            if root is None or root.y>-.045 or (z<EYE-.091 and root.y>-.085):continue
            root+=normal*.0004
            chosen=sorted(guides,key=lambda g:(g[0]-root).length)[:3]
            weights=[1/((g[0]-root).length+.008)**2 for g in chosen];total=sum(weights);weights=[w/total for w in weights]
            base=[sum((g[j]*w for g,w in zip(chosen,weights)),Vector()) for j in range(4)]
            displacement=root-base[0]
            length=rng.uniform(.68,1.05)
            phase=math.floor(x/.017)*1.71+math.floor((z-EYE)/.021)*.83+rng.uniform(-.65,.65)
            amplitude=rng.uniform(.003,.0065);path=[]
            tip_jitter=Vector((rng.uniform(-.018,.018),rng.uniform(-.015,.015),rng.uniform(-.013,.009)))
            # The central beard crosses the sagittal plane; two mirrored
            # positive-X guides otherwise leave an artificial middle part.
            if ax<.028:tip_jitter.x-=side*.012
            for k in range(25):
                t=k/24;u=min(1,t*length)
                p=catmull(base,u)+displacement*(1-.65*t)+tip_jitter*t
                p+=Vector((amplitude*math.sin(phase+t*10),-.001-amplitude*.6*math.cos(phase+t*12),amplitude*.3*math.sin(phase+t*13)))*math.sin(math.pi*t)
                path.append(tuple(p))
            paths[rng.choices(range(4),[.46,.35,.16,.03])[0]].append(path)
        # A curved volumetric flow field, not a fan from roots to a common
        # endpoint plane. The latter produced blade-like tips in oblique view.
        center=[Vector((side*.001,-.169,EYE-.059)),Vector((side*.025,-.177,EYE-.069)),Vector((side*.046,-.172,EYE-.074)),Vector((side*.060,-.162,EYE-.056))]
        for child in range(2600 if detail else 750):
            x=rng.uniform(.001,.030);z=EYE-.058+rng.uniform(-.005,.003)
            root=surface.ray_cast(Vector((side*x,-.5,z)),Vector((0,1,0)),1)[0]
            if root is None:continue
            start=x/.065;finish=rng.uniform(min(.95,start+.22),1.)
            phase=rng.random()*math.tau;radius=.0065*math.sqrt(rng.random())
            path=[];offset=root+Vector((0,-.0005,0))-catmull(center,start)
            for k in range(24):
                t=k/23;u=start+(finish-start)*t;p=catmull(center,u)+offset*(1-t)**2
                r=radius*math.sin(math.pi*t*.86)*max(.08,(1-u)**.4)
                p+=Vector((0,r*math.cos(phase+t*2),r*math.sin(phase+t*2)))
                path.append(tuple(p))
            paths[rng.choices(range(4),[.5,.32,.16,.02])[0]].append(path)
    for i,p in enumerate(paths):strands('Sikh270 regional beard and moustache '+str(i),p,mats[i],.00015 if detail else .00018)
    return allguides


def skin_finish(body):
    """Preserve face geometry. Break smooth fill with restrained brush-scale
    pigment and actual shallow forehead lines fitted to the anatomical surface.
    No image projection, ethnic preset or baked shadow is introduced.
    """
    import bpy
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    from sikh261_character import strands
    from sikh257_native import material
    mat=body.data.materials[0].copy();body.data.materials[0]=mat
    n=mat.node_tree.nodes;l=mat.node_tree.links
    for node in n:
        if node.bl_idname=='ShaderNodeMixRGB' and node.blend_type=='MIX' and abs(node.inputs[0].default_value-.055)<.001:
            node.inputs[0].default_value=.075
    # Shader-space shallow relief, not dark curves drawn on skin. Object
    # coordinates follow the head; mask isolates forehead from body/eyes.
    tex=n.new('ShaderNodeTexCoord');sep=n.new('ShaderNodeSeparateXYZ');l.new(tex.outputs['Object'],sep.inputs[0])
    def calc(op,a,b=0):
        node=n.new('ShaderNodeMath');node.operation=op
        for i,v in enumerate((a,b)):
            if isinstance(v,(float,int)):node.inputs[i].default_value=v
            else:l.new(v,node.inputs[i])
        return node.outputs[0]
    x=sep.outputs['X'];y=sep.outputs['Y'];z=sep.outputs['Z']
    curve=calc('ADD',z,calc('MULTIPLY',calc('MULTIPLY',x,x),1.25))
    relief=0
    for h,depth in ((.029,1.),(.041,.7),(.051,.45)):
        dist=calc('DIVIDE',calc('SUBTRACT',curve,EYE+h),.0007)
        dip=calc('EXPONENT',calc('MULTIPLY',calc('MULTIPLY',dist,dist),-1.))
        relief=calc('ADD',relief,calc('MULTIPLY',dip,-depth))
    mask=calc('MULTIPLY',calc('LESS_THAN',y,-.105),calc('LESS_THAN',calc('ABSOLUTE',x),.060))
    bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.32;bump.inputs['Distance'].default_value=.0008
    l.new(calc('MULTIPLY',relief,mask),bump.inputs['Height'])
    shader=n.get('Principled BSDF');previous=shader.inputs['Normal'].links[0].from_socket
    l.new(previous,bump.inputs['Normal']);l.new(bump.outputs[0],shader.inputs['Normal'])


def eye_structure(body):
    """Individual mature lid volume, without replacing coherent anatomy."""
    import bpy,addon_utils,importlib
    from mpfb264_setup import verify_sources,MODULE,INSTALLED
    verify_sources();addon_utils.enable(MODULE,default_set=False)
    services=importlib.import_module(MODULE+'.services')
    for side in ('l','r'):
        for target,weight in [('height1-decr',.32),('height2-decr',.12),('bag-incr',.40),('eyefold-concave',.25)]:
            services.TargetService.load_target(body,str(INSTALLED/'data/targets/eyes'/f'{side}-eye-{target}.target.gz'),weight=weight)
    for side in ('L','R'):
        ob=bpy.data.objects['Pupil '+side];ob.scale.x*=.78;ob.scale.z*=.78
    bpy.context.view_layer.update()


def native(job):
    import bpy
    from mathutils import Vector
    from sikh257_native import camera_at,material
    from sikh269_character import cloth_material
    out=validate(job);nativepath=out/'character.blend'
    if bpy.app.online_access:raise ValueError('Offline required')
    if job['operation']=='reopen':
        record=json.loads((out/'build.json').read_text())
        if sha(nativepath)!=record['native_sha256']:raise ValueError('Native changed')
        bpy.ops.wm.open_mainfile(filepath=str(nativepath));bpy.context.scene.render.filepath=str(out/'reopen.png');bpy.ops.render.render(write_still=True)
        (out/'reopen.json').write_text(json.dumps(dict(native_sha256=sha(nativepath),inventory_matches=sorted(o.name for o in bpy.data.objects)==record['objects'])))
        return
    if nativepath.exists():raise ValueError('Preserve candidate')
    if sha(ROOT/SOURCE)!=SOURCE_SHA:raise ValueError('Foundation changed')
    bpy.ops.wm.open_mainfile(filepath=str(ROOT/SOURCE));scene=bpy.context.scene;scene.frame_set(96)
    for ob in list(bpy.data.objects):
        if ob.name.startswith(('Rooted beard','Moustache overlapping','Harsh Sikh turban')):bpy.data.objects.remove(ob,do_unlink=True)
    cover=bpy.data.objects['Turban free end | evaluated gravity control'];cover.hide_render=True
    before=set(bpy.data.objects);body=bpy.data.objects['Sikh269 coherent editable anatomy'];rig=next(m.object for m in body.modifiers if m.type=='ARMATURE')
    detail=job['operation'] in {'detail','look'}
    if detail:eye_structure(body)
    crown(cloth_material() if detail else material('Guide clay',(.21,.24,.28)))
    guides=hair(body,detail)
    if detail:skin_finish(body)
    for ob in set(bpy.data.objects)-before:
        if ob.type in {'CURVE','MESH'}:
            world=ob.matrix_world.copy();ob.parent=rig;ob.parent_type='BONE';ob.parent_bone='head';bpy.context.view_layer.update();ob.matrix_world=world
    scene.cycles.samples=24 if detail else 12;scene.render.resolution_x=640;scene.render.resolution_y=800
    cam=scene.camera;cam.data.ortho_scale=.54;target=Vector((0,-.025,EYE-.017))
    for name,pos in [('front',(0,-3,EYE)),('three-quarter',(1.7,-3,EYE+.03)),('opposite',(-1.7,-3,EYE+.03)),('profile',(3,0,EYE)),('rear',(0,3,EYE+.10)),('crown',(1,-1,EYE+2))]:
        if job['operation']=='look' and name not in {'front','three-quarter'}:continue
        camera_at(cam,pos,target);scene.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True)
    cam.data.ortho_scale=.28;camera_at(cam,(0,-3,EYE),(0,-.10,EYE-.04));scene.render.filepath=str(out/'face-detail.png');bpy.ops.render.render(write_still=True)
    cam.data.ortho_scale=.54
    controls={}
    if job['operation']=='detail':
        cover.hide_render=False;scene.frame_set(16)
        for name,pos in [('covered-front',(0,-3,EYE)),('covered-quarter',(1.7,-3,EYE+.03))]:
            camera_at(cam,pos,target);scene.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True)
        scene.frame_set(96);camera_at(cam,(1.7,-3,EYE+.03),target)
        scene.render.filepath=str(out/'released-quarter.png');bpy.ops.render.render(write_still=True)
        cover.hide_render=True
        # Attachment-only head pose. This is not a coordinated actor bow or
        # a cloth/hand performance; fixed-body cloth is deliberately hidden.
        head=rig.pose.bones['head'];head.rotation_mode='XYZ';head.rotation_euler=(math.radians(12),0,math.radians(-12));bpy.context.view_layer.update()
        scene.render.filepath=str(out/'head-attachment.png');bpy.ops.render.render(write_still=True)
        controls['attachment_pose_degrees']=[12,0,-12]
        head.rotation_euler=(0,0,0);bpy.context.view_layer.update()
    camera_at(cam,(0,-3,EYE),target);scene.render.filepath=str(out/'reopen.png')
    bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(nativepath))
    (out/'guides.json').write_text(json.dumps(dict(stations=STATIONS,folds=FOLDS,beard=guides),indent=2))
    (out/'build.json').write_text(json.dumps(dict(native_sha256=sha(nativepath),source_sha256=SOURCE_SHA,objects=sorted(o.name for o in bpy.data.objects),stage=job['operation'],controls=controls,status='INTERNAL_UNREVIEWED',limits=['Static candidate and attachment control only','Free end uses prior fixed-body cache, not new actor motion','Not identity or animation acceptance']),indent=2))


if __name__=='__main__':
    if '--' in sys.argv:
        args=sys.argv[sys.argv.index('--')+1:]
        if len(args)!=1:raise ValueError('One structured operation')
        job=json.loads(args[0]);validate(job);native(job)
    else:
        if len(sys.argv) not in (3,4) or (len(sys.argv)==4 and sys.argv[3]!='--prepare'):raise ValueError('operation attempt [--prepare]')
        job=dict(operation=sys.argv[1],attempt=int(sys.argv[2]));validate(job)
        if len(sys.argv)==4:launch(job,True)
        else:
            import fcntl
            lockpath=ROOT/'.runtime/art-direction/series01-sikh270/worker.lock'
            lockpath.parent.mkdir(parents=True,exist_ok=True)
            with lockpath.open('a') as lock:
                fcntl.flock(lock,fcntl.LOCK_EX)
                launch(job)
