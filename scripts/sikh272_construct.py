"""Bounded local whole-form controls after Director271 rejection.

Fixed reviewed handler; accepts no paths, code, provider output or asset scripts.
Rest construction only. No garment/performance qualification is implied.
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

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'));sys.path.insert(0,str(ROOT/'src'))
SOURCE='.runtime/art-direction/series01-sikh269/candidate-24/character.blend'
SOURCE_SHA='13353e4e11cc1c31ae45341ede0e38d9dc6d5f8f157d4578dff35f4ccb5b81d7'
EYE=1.665999174118042
REF='.runtime/art-direction/series01-sikh257/sikh-uncovered-concept-v03.png'
ROOT_OUT=ROOT/'.runtime/art-direction/series01-sikh272'

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def validate(j):
    if not isinstance(j,dict) or set(j)!={'operation','attempt'} or j['operation'] not in {'construct','reopen'} or type(j['attempt']) is not int or not 1<=j['attempt']<=30:
        raise ValueError('Fixed construct/reopen and integer attempt1..30 only')
    return ROOT_OUT/f"candidate-{j['attempt']:02d}"

def plan(j):
    from movie_factory import production_knowledge as pk
    files=['AGENTS.md','docs/knowledge/SIKH_FOUNDATION_REJECTION_271.md',
        'docs/planning/SERIES_01_SIKH_ASSET_STRATEGY_262.md','docs/planning/SERIES_01_SIKH_BASELINE_V01.md',
        'docs/planning/SERIES_01_ART_DIRECTION_C.md','scripts/sikh272_construct.py','tests/test_sikh272_construct.py',
        'scripts/sikh257_native.py','scripts/sikh261_character.py','scripts/sikh270_guides.py','scripts/mpfb264_setup.py',
        'src/movie_factory/sikh257_contract.py','.runtime/assets/series01-sikh261-turban/sikh_turban.glb',
        '.runtime/assets/series01-sikh261-turban/acquisition.json',
        '.runtime/art-direction/series01-sikh272/construction-study/form-study.png',
        SOURCE,REF,'.runtime/art-direction/series01-entrances-v04/C-illustrated-landscape.png',
        '.runtime/art-direction/series01-facebuilder-trial-01/natural152-preview-16/front.png',
        '.runtime/art-direction/series01-sikh271-audit/accepted-pashtun-7s5.png','results/sikh271/disposition.json']
    if j['operation']=='reopen':files.append(str((validate(j)/'character.blend').relative_to(ROOT)))
    if sha(ROOT/SOURCE)!=SOURCE_SHA:raise ValueError('Substrate changed')
    task=dict(id=f"sikh272-{j['operation']}-{j['attempt']:02d}",operation='modeling',entities=['sikh'],phase='execution',
        query='whole facial form natural groom tied turban ensemble same-film reference negative control',
        intent='Director272 native reconstruction under271 quality contract. Internal whole-form control, not Director review or production admission.',
        inputs={f:sha(ROOT/f) for f in files},open_decisions=[],max_context_characters=42000,
        execution_authority=dict(source=files[2],scope='Director272 approved native construction, no paid calls or new assets'))
    p=pk.task_packet(ROOT,task);dest=ROOT/'.runtime/knowledge-pilot213'/task['id']
    dest.with_suffix('.json').write_text(json.dumps(p,indent=2));dest.with_suffix('.md').write_text(pk.packet_markdown(p))
    if not p['dispatch_ready']:raise ValueError(p['blockers'])
    return p,dest

def envelope(theta,phi,offset=0):
    """Asymmetric supported rest surface; no claim of simulated tying."""
    r=math.cos(phi);s=math.sin(phi)
    return ((.104+offset)*r*math.sin(theta)+.008*s,
        -.014-(.123+offset)*r*math.cos(theta),EYE+.045+(.129+offset)*s)

def wrap_surface(theta,u,layer,family):
    # Two oblique families; no closed horizontal crown rings or polar caps.
    if family==0:
        phi=-.39+.145*layer+.47*math.sin(theta+.25)+u*(.28+.035*math.cos(theta))
    else:
        phi=.22+.15*layer-.48*math.sin(theta-.25)+u*.30
    # Turned edge and broad compressed secondary folds. Millimetre amplitude.
    off=.0018+.00055*layer+.0014*math.exp(-(u/.13)**2)
    off+=.0008*math.sin(math.pi*u)**2*math.sin(3.1*theta+layer*.9)
    return envelope(theta,phi,off)

def historical_fans(mat):
    from sikh257_native import mesh
    # Hidden cloth support, with an uneven ear/front boundary, not visible shell.
    vs=[];fs=[];nu=160;nv=40
    for j in range(nv):
        f=j/(nv-1)
        for i in range(nu):
            th=-math.pi+math.tau*i/nu
            lower=-.49+.40*max(0,math.cos(th))-.10*math.sin(th)
            vs.append(envelope(th,lower+(math.pi/2-lower)*f,-.002))
    for j in range(nv-1):
        for i in range(nu):a=j*nu+i;b=j*nu+(i+1)%nu;fs.append((a,b,b+nu,a+nu))
    mesh('272 inner cloth support',vs,fs,mat)
    # Visible broad fans: diagonal front courses return obliquely around back.
    for family,count in ((0,6),(1,3)):
        for layer in range(count):
            vs=[];fs=[];nu=180;nv=18
            lo,hi=(-math.pi,math.pi)
            for i in range(nu):
                th=lo+(hi-lo)*i/(nu-1)
                for j in range(nv):
                    f=j/(nv-1)
                    p=wrap_surface(th,f,layer,family)
                    vs.append(p)
            for i in range(nu-1):
                for j in range(nv-1):a=i*nv+j;fs.append((a,a+nv,a+nv+1,a+1))
            ob=mesh(f'272 oblique wrap fan {family}-{layer}',vs,fs,mat)
            ob.modifiers.new('Cotton thickness','SOLIDIFY').thickness=.00045
    # A broad crossing length actually traverses the crown; it is not a
    # latitude cap closing repeated polar rings. Ends tuck under lower courses.
    vs=[];fs=[];nu=120;nv=35;angle=-.50
    for i in range(nu):
        t=-.24+(math.pi+.48)*i/(nu-1)
        for j in range(nv):
            w=(j/(nv-1)-.5)*.80
            q=math.sqrt(max(.001,1-w*w))
            x=math.sin(angle)*math.cos(t)*q+math.cos(angle)*w
            y=-math.cos(angle)*math.cos(t)*q+math.sin(angle)*w
            z=math.sin(t)*q
            off=.001+.0010*math.sin(math.pi*j/(nv-1)*5)**2
            vs.append(((.104+off)*x+.008*z,-.014+(.123+off)*y,EYE+.045+(.129+off)*z))
    for i in range(nu-1):
        for j in range(nv-1):a=i*nv+j;fs.append((a,a+nv,a+nv+1,a+1))
    cross=mesh('272 crossing crown length',vs,fs,mat)
    cross.modifiers.new('Crossing cotton thickness','SOLIDIFY').thickness=.00045
    return {'construction':'supported oblique fan rest study; route joining and free-end motion NOT_RUN'}

def folded_surface(theta,v):
    """Continuous rest sculpture: oblique compression, not intersecting sheets."""
    front=max(0,math.cos(theta))
    low=-.53+.85*front**1.65-.10*math.sin(theta)
    phi=low+(math.pi/2-low)*v
    # Broad diagonal sweeps continue around the back; upper gathering bends
    # them across the crown. Use one field, so no overlapping band end cuts.
    phase=(phi-.57*math.sin(theta+.18)-.08*math.sin(2*theta))/ .145
    phase+=.10*math.sin(theta*3+phi*5)+.035*math.sin(theta*9+phi*11)
    q=phase-math.floor(phase)
    ridge=math.exp(-((q-.12)/.12)**2)
    compression=.0012*math.sin(phase*math.tau*2+.2*math.sin(theta*4))
    fade=max(0,math.cos(phi))**.45
    off=(.0028*ridge+.0012*math.sin(math.pi*q)+compression)*fade
    r=math.cos(phi);s=math.sin(phi)
    return ((.103+off)*r*math.sin(theta)+.005*s,
        -.011-(.119+off)*r*math.cos(theta),EYE+.037+(.117+off)*s)

def continuous_turban(mat):
    from sikh257_native import mesh
    vs=[];fs=[];nu=360;nv=200
    for j in range(nv):
        for i in range(nu):vs.append(folded_surface(-math.pi+math.tau*i/nu,j/nv))
    for j in range(nv-1):
        for i in range(nu):a=j*nu+i;b=j*nu+(i+1)%nu;fs.append((a,b,b+nu,a+nu))
    pole=len(vs);vs.append(folded_surface(0,1))
    for i in range(nu):fs.append(((nv-1)*nu+i,(nv-1)*nu+(i+1)%nu,pole))
    ob=mesh('272 continuous tied cloth form control',vs,fs,mat)
    ob.modifiers.new('Thin cloth interior','SOLIDIFY').thickness=.001
    return {'construction':'continuous sculpted oblique fold rest surface',
        'limits':'Static tied region only. Free-end joining, physical cloth and reveal NOT_RUN.'}

def turban(mat,out):
    import bpy
    from sikh261_character import donor_crown
    from movie_factory.sikh257_contract import HERO_SOURCES
    for f,d in HERO_SOURCES.items():
        if sha(ROOT/f)!=d:raise ValueError('Turban donor hash changed')
    ob=donor_crown(out);ob.name='272 authored donor fold layout control'
    for v in ob.data.vertices:
        v.co.x*=.90;v.co.y=v.co.y*1.28-.025
        v.co.z=(v.co.z-1.640)*1.03+EYE+.041
    smooth=ob.modifiers.new('Relax triangulation','SMOOTH');smooth.factor=.45;smooth.iterations=2
    sub=ob.modifiers.new('Cloth rest detail resolution','SUBSURF');sub.levels=3
    bpy.context.view_layer.update()
    refined=bpy.data.meshes.new_from_object(ob.evaluated_get(bpy.context.evaluated_depsgraph_get()))
    ob.modifiers.clear();ob.data=refined
    normals=[v.normal.copy() for v in ob.data.vertices]
    # The authored major panel joins remain. Secondary compression is modest,
    # broad and broken along each cloth panel, not a set of exterior ribs.
    for v,n in zip(ob.data.vertices,normals):
        x,y,z=v.co;h=z-EYE
        th=math.atan2(x,-(y+.025))
        phase=(h-.80*x+.015*math.sin(th*2))/.025
        front=max(0,min(1,(-y+.015)/.065))
        wave=.0008*math.sin(phase*math.tau)+.00035*math.sin(phase*math.tau*2+.8)
        mask=max(0,min(1,(h+.045)/.035))
        v.co+=n*wave*mask*(.55+.45*front)
        v.co.z+=.006*max(0,min(1,(h-.045)/.07))*(.7+.3*math.sin(x*25))
    ob.data.materials.clear();ob.data.materials.append(mat)
    return {'construction':'existing CC-BY donor major fold layout, fitted and refined in native mesh',
        'limits':'Rest test only; crown/rear authenticity and free-end continuity remain review obligations.'}

def face(body):
    import addon_utils,importlib,bpy
    from mpfb264_setup import MODULE,INSTALLED,verify_sources
    verify_sources();addon_utils.enable(MODULE,default_set=False)
    service=importlib.import_module(MODULE+'.services').TargetService
    changes={'head/head-age-incr':.65,'head/head-fat-decr':.76,'head/head-rectangular':.40,
        'eyebrows/eyebrows-trans-forward':.90,'eyebrows/eyebrows-trans-down':.10,
        'nose/nose-hump-incr':.55,'nose/nose-scale-depth-incr':.73,
        'nose/nose-width1-incr':.15,'nose/nose-width3-incr':.20}
    for side in ('l','r'):
        changes.update({f'cheek/{side}-cheek-bones-incr':.8,f'cheek/{side}-cheek-inner-decr':.32,
            f'eyes/{side}-eye-bag-incr':.3,f'eyes/{side}-eye-eyefold-concave':.38,
            f'eyes/{side}-eye-height1-incr':0.,f'eyes/{side}-eye-height2-incr':0.,
            f'eyes/{side}-eye-height1-decr':.65})
    for name,value in changes.items():
        # TargetService recognizes existing keys; clear exact stem to avoid
        # double application when a target is already present on the substrate.
        stem=name.split('/')[-1]
        found=next((k for k in body.data.shape_keys.key_blocks if k.name==stem),None)
        if found:found.value=value
        else:service.load_target(body,str(INSTALLED/'data/targets'/f'{name}.target.gz'),weight=value)
    bpy.context.view_layer.update()
    return changes

def groom(body):
    import bpy
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    from sikh270_guides import catmull
    from sikh261_character import strands
    from sikh257_native import material
    surf=BVHTree.FromObject(body,bpy.context.evaluated_depsgraph_get())
    rng=random.Random(272);paths=[[] for _ in range(3)]
    colors=[(.009,.006,.004),(.021,.014,.010),(.042,.029,.019)]
    # Coherent major locks, with separate root coverage, not a global vertical
    # extension. Ear/jaw/chin regions sweep differently and overlap in depth.
    for side in (-1,1):
        for region in range(6500):
            x=side*rng.uniform(0,.078);ax=abs(x)
            upper=EYE-.078+.063*(ax/.078)**1.5
            lower=EYE-.124+.035*(ax/.078)**3
            z=rng.uniform(lower,upper)
            if ax<.018 and z>EYE-.083:continue
            if rng.random()>min(1,(upper-z)/.006):continue
            root=surf.ray_cast(Vector((x,-.5,z)),Vector((0,1,0)),1)[0]
            if root is None or root.y>.005:continue
            end=Vector((side*.85*ax+rng.uniform(-.018,.018),-.135-rng.uniform(-.012,.018),EYE-.208+.025*(ax/.078)**1.5+rng.uniform(-.012,.012)))
            spread=.008*min(1,ax/.035)
            ctr=[root,root+Vector((side*spread,-.025,-.023)),(root+end)*.5+Vector((side*spread,-.032,-.017)),end]
            phase=math.floor(x/.014)*1.8+math.floor((z-EYE)/.025)*.6+rng.uniform(-.2,.2)
            for child in range(1):
                rt=root
                path=[];l=rng.uniform(.64,1.04)
                for k in range(24):
                    t=k/23;u=min(1,t*l);p=catmull(ctr,u)+(rt-root)*(1-.55*t)
                    p+=Vector((.010*math.sin(phase+t*8),-.009*math.cos(phase+t*7),.004*math.sin(phase+t*6)))*math.sin(math.pi*t)
                    path.append(tuple(p))
                paths[rng.choices(range(3),[.62,.30,.08])[0]].append(path)
        # Rooted short upper-lip strokes sweep downward into cheek hair,
        # rather than converging into long upward-pointing moustache wings.
        for child in range(1100):
            x=side*rng.uniform(.001,.034);z=EYE-.058-.006*(abs(x)/.034)+rng.uniform(-.003,.003)
            root=surf.ray_cast(Vector((x,-.5,z)),Vector((0,1,0)),1)[0]
            if root is None:continue
            end=root+Vector((side*rng.uniform(.006,.017),-.003,rng.uniform(-.017,-.008)))
            path=[]
            for k in range(14):
                t=k/13;p=root.lerp(end,t)+Vector((side*.002,-.004,0))*math.sin(math.pi*t)
                path.append(tuple(p))
            paths[rng.choices(range(3),[.66,.29,.05])[0]].append(path)
    for i,ps in enumerate(paths):
        m=material('272 groom mass '+str(i),colors[i]);m.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=.49
        strands('272 region clumps '+str(i),ps,m,.00023)
    # Brows are rooted and tapered, with an inner-to-outer flow; the old
    # isolated straight comb strips are not retained as protected identity.
    brows=[]
    for side in (-1,1):
        for i in range(1050):
            x=side*rng.uniform(.010,.058);u=(abs(x)-.010)/.048
            z=EYE+.008+.007*math.sin(u*math.pi)-.002*u+rng.uniform(-.004,.0035)*(1-.45*u)
            root=surf.ray_cast(Vector((x,-.5,z)),Vector((0,1,0)),1)[0]
            if root is None:continue
            end=root+Vector((side*(.002+.002*u),-.0007,.002*(1-u)-.001*u))
            brows.append([tuple(root),tuple(root.lerp(end,.5)+Vector((0,-.0008,0))),tuple(end)])
    strands('272 rooted brows',brows,material('272 brow pigment',(.012,.008,.005)),.00020)

def run(j):
    import bpy
    from sikh257_native import material,camera_at
    out=validate(j)
    if bpy.app.online_access:raise ValueError('Offline Blender required')
    if j['operation']=='reopen':
        r=json.loads((out/'build.json').read_text())
        if sha(out/'character.blend')!=r['native_sha256']:raise ValueError('Saved source mismatch')
        bpy.ops.wm.open_mainfile(filepath=str(out/'character.blend'))
        bpy.context.scene.render.filepath=str(out/'reopen.png');bpy.ops.render.render(write_still=True)
        (out/'reopen.json').write_text(json.dumps({'objects_match':sorted(o.name for o in bpy.data.objects)==r['objects'],'native_sha256':r['native_sha256']}));return
    if sha(ROOT/SOURCE)!=SOURCE_SHA:raise ValueError('Source changed')
    bpy.ops.wm.open_mainfile(filepath=str(ROOT/SOURCE));scene=bpy.context.scene;scene.frame_set(96)
    for ob in list(bpy.data.objects):
        if ob.name.startswith(('Rooted beard','Moustache','Harsh Sikh','Turban free','Natural brow')):bpy.data.objects.remove(ob,do_unlink=True)
    body=bpy.data.objects['Sikh269 coherent editable anatomy'];changes=face(body)
    # Discriminating registration control: the inherited authored spheres
    # were translated 5mm in front of the rig's anatomical eye centers.
    # Remove that unsupported offset rather than narrowing lids around it.
    from mathutils import Vector
    eye_registration={}
    for side in ('L','R'):
        for prefix in ('Eye sclera ','Brown iris ','Pupil '):
            ob=bpy.data.objects[prefix+side];world=ob.matrix_world.copy()
            world.translation+=Vector((0,.004,-.001));ob.matrix_world=world
            eye_registration[ob.name]=list(ob.matrix_world.translation)
    skin=material('272 clay anatomy',(.30,.21,.15));body.data.materials.clear();body.data.materials.append(skin)
    crown=material('272 broad cotton value',(.014,.025,.057));route=turban(crown,out);groom(body)
    # Shape proof uses simple materials and existing eyes; diagnostic light is
    # deliberately directional, with weaker fill so facial planes are visible.
    bpy.data.objects['key'].data.size=2.0;bpy.data.objects['fill'].data.energy=70
    scene.world.node_tree.nodes['Background'].inputs[1].default_value=.28
    scene.cycles.samples=12;scene.render.resolution_x=560;scene.render.resolution_y=700
    cam=scene.camera;cam.data.ortho_scale=.50;target=(0,-.02,EYE-.012)
    views=[('front',(0,-3,EYE)),('three-quarter',(1.7,-3,EYE+.015)),('left-quarter',(-1.7,-3,EYE+.015)),('profile',(3,0,EYE)),('rear',(0,3,EYE+.04)),('crown',(1,-1,EYE+1.6))]
    for name,pos in views:
        camera_at(cam,pos,target);scene.render.filepath=str(out/(name+'.png'));bpy.ops.render.render(write_still=True)
    # Face-only clay diagnostic separates morphology from groom/crown effect.
    for ob in bpy.data.objects:
        if ob.name.startswith('272 region'):ob.hide_render=True
    cam.data.ortho_scale=.27;camera_at(cam,(1.7,-3,EYE+.015),(0,-.10,EYE-.035))
    scene.render.filepath=str(out/'face-clay.png');bpy.ops.render.render(write_still=True)
    for ob in bpy.data.objects:
        if ob.name.startswith('272 region'):ob.hide_render=False
    cam.data.ortho_scale=.50;camera_at(cam,(0,-3,EYE),target)
    bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(out/'character.blend'))
    (out/'build.json').write_text(json.dumps(dict(native_sha256=sha(out/'character.blend'),source_sha256=SOURCE_SHA,
        objects=sorted(o.name for o in bpy.data.objects),morph_changes=changes,
        active_shape_keys={k.name:k.value for k in body.data.shape_keys.key_blocks if k.value},eye_registration=eye_registration,route=route,
        status='INTERNAL_FORM_CONTROL_NOT_ADMITTED',limits=['No full material treatment','No actual cloth release or motion','Not accepted identity']),indent=2))

def launch(j,prepare=False):
    out=validate(j);p,dest=plan(j)
    if prepare:print(dest.with_suffix('.md'));return
    out.mkdir(parents=True,exist_ok=True);log=out/(j['operation']+'.log')
    if log.exists():raise ValueError('Preserve previous attempt')
    (out/(j['operation']+'-source.py')).write_bytes(Path(__file__).read_bytes())
    env={k:os.environ[k] for k in ('PATH','HOME','TMPDIR','LANG','LC_ALL') if k in os.environ};env['CYCLES_METAL_DISABLE_BINARY_ARCHIVES']='1'
    start=time.monotonic()
    with log.open('w') as f:
        r=subprocess.run(['/Applications/Blender.app/Contents/MacOS/Blender','--background','--offline-mode','--disable-autoexec','--python-exit-code','7','--python',str(Path(__file__).resolve()),'--',json.dumps(j)],env=env,stdout=f,stderr=subprocess.STDOUT)
    (out/(j['operation']+'-receipt.json')).write_text(json.dumps(dict(returncode=r.returncode,seconds=time.monotonic()-start,packet_digest=p['packet_digest'],inputs=p['task']['inputs']),indent=2))
    if r.returncode:raise RuntimeError(str(log))
    print(out)

if __name__=='__main__':
    if '--' in sys.argv:
        args=sys.argv[sys.argv.index('--')+1:]
        if len(args)!=1:raise ValueError('One structured operation only')
        j=json.loads(args[0]);validate(j);run(j)
    else:
        if len(sys.argv) not in (3,4) or (len(sys.argv)==4 and sys.argv[3]!='--prepare'):raise ValueError('operation attempt [--prepare]')
        j=dict(operation=sys.argv[1],attempt=int(sys.argv[2]));validate(j);launch(j,len(sys.argv)==4)
