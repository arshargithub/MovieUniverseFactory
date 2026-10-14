"""Fixed MPFB character assembly controls. No arbitrary file/code parameters.

Rugged facial proportions are authored with upstream feature targets before rig
and hair fitting. These controls are internal candidates, not visual acceptance.
"""
import hashlib
import importlib
import json
import math
import random
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from mpfb264_setup import verify_sources, MODULE, INSTALLED

MORPHS = {
    'head/head-scale-vert-incr': .24,
    'head/head-rectangular': .18,
    'head/head-age-incr': .32,
    'head/head-fat-decr': .16,
    'chin/chin-height-incr': .13,
    'chin/chin-bones-incr': .22,
    'nose/nose-scale-depth-incr': .60,
    'nose/nose-hump-incr': .38,
    'nose/nose-scale-vert-incr': .22,
    'nose/nose-width1-incr': .35,
    'eyebrows/eyebrows-trans-forward': .55,
    'cheek/l-cheek-bones-incr': .30,
    'cheek/r-cheek-bones-incr': .30,
    'eyes/l-eye-height2-incr': .35,
    'eyes/r-eye-height2-incr': .35,
}


def validate(job):
    if (not isinstance(job, dict) or set(job) != {'operation', 'attempt'}
            or job['operation'] not in {'build', 'reopen'}
            or type(job['attempt']) is not int or not 1 <= job['attempt'] <= 20):
        raise ValueError('Fixed build/reopen operations, attempts1..20 only')
    return ROOT / '.runtime/art-direction/series01-sikh265' / f"candidate-{job['attempt']:02d}"


def prepare():
    """Outer Python: bind current reviewed sources to a fresh execution packet."""
    files = ['AGENTS.md', 'docs/planning/SERIES_01_SIKH_ASSET_STRATEGY_262.md',
             'docs/planning/SERIES_01_SIKH_BASELINE_V01.md',
             'scripts/sikh265_character.py', 'scripts/mpfb264_setup.py',
             'scripts/sikh257_native.py', 'scripts/sikh261_character.py',
             'tests/test_sikh265_character.py', 'results/sikh263/file-manifest.json',
             '.runtime/art-direction/series01-sikh257/sikh-uncovered-concept-v03.png',
             '.runtime/assets/series01-sikh261-turban/sikh_turban.glb',
             '.runtime/assets/series01-sikh263-donors/mpfb-2.0.18.zip']
    task = dict(id='sikh265-coherent-character', operation='modeling', entities=['sikh'],
                query='MPFB coherent male face beard turban uncover independent assembly reference fidelity anatomy contact rights',
                intent='Continue Director263 MPFB route and264 no-setup-handoff instruction. Internal coherent male/beard/turban proof against directional v03. No purchase or accepted-master edits. Bike input only blocks actual fit; not a production pass.',
                phase='execution', inputs={p: hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in files},
                open_decisions=[], execution_authority=dict(source=files[1], scope='Authorized independent Sikh character assembly and internal proof; no external calls or new installations.'),
                max_context_characters=42000)
    out=ROOT/'results/sikh265';out.mkdir(parents=True,exist_ok=True)
    (out/'task.json').write_text(json.dumps(task,indent=2)+'\n')


def adapt_beard(obj, eye_z, moustache=False):
    """Preserve fitted card roots; author broad, irregular long-beard ends.

    Connected components are authored donor locks. Avoid mapping a global
    curtain onto the face: each lock retains its actual cheek/jaw attachment.
    """
    from mathutils import Vector
    from sikh261_character import strands, painted
    adjacent=[set() for _ in obj.data.vertices]
    for e in obj.data.edges:
        a,b=e.vertices;adjacent[a].add(b);adjacent[b].add(a)
    remaining=set(range(len(adjacent)));components=[]
    while remaining:
        stack=[remaining.pop()];part=[]
        while stack:
            i=stack.pop();part.append(i)
            for j in adjacent[i]&remaining:remaining.remove(j);stack.append(j)
        components.append(part)
    rng=random.Random(265);fibers=[]
    inv=obj.matrix_world.inverted()
    for ids in components:
        original={i:obj.matrix_world@obj.data.vertices[i].co for i in ids}
        lo=min(p.z for p in original.values());hi=max(p.z for p in original.values())
        roots=[p for p in original.values() if p.z>hi-.003]
        root=sum(roots,Vector())/len(roots)
        if moustache:
            for i,p in original.items():
                p.x*=1.45
                # Lift outboard tips, retaining a broad lip attachment.
                p.z+=.014*max(0,(abs(p.x)-.012)/.048)**1.5
                p.y-=.006
                obj.data.vertices[i].co=inv@p
            continue
        if hi-lo<.004:continue
        length=(eye_z-.235+.060*(abs(root.x)/.08)**3+rng.uniform(-.010,.015))
        tip=Vector((root.x*.90+rng.uniform(-.007,.007),min(root.y-.040,-.188)+rng.uniform(-.014,.014),length))
        for i,p in original.items():
            t=max(0,min(1,(hi-p.z)/(hi-lo)))
            current_center=Vector((root.x,root.y,hi+(lo-hi)*t))
            # Card lateral width is retained; coordinated lock flow and
            # rooted curl prevent parallel straight ribbons.
            offset=p-current_center
            wave=math.sin(math.pi*t)
            q=root.lerp(tip,t)+Vector((.007*wave*math.sin(t*10+root.x*90),-.010*wave,.003*wave*math.sin(t*13)))
            q+=Vector((offset.x,offset.y*.4,0))
            obj.data.vertices[i].co=inv@q
        for _ in range(9):
            shift=Vector((rng.uniform(-.004,.004),rng.uniform(-.004,.004),rng.uniform(-.002,.002)))
            pts=[]
            for j in range(20):
                t=j/19;wave=math.sin(math.pi*t)
                pts.append(root.lerp(tip,t)+shift+Vector((.007*wave*math.sin(t*10+root.x*90),-.010*wave,.003*wave*math.sin(t*13))))
            fibers.append(pts)
    if fibers:
        groom=strands('beard donor-guided fiber detail',fibers,painted('beard brown black fibers',(.013,.007,.004),.4,160),.00030)
        # Same complete-head parent as the beard during the first motion proof.
        groom['attachment']='head; root-retaining donor guide adaptation'


def main(job):
    out=validate(job)
    import bpy
    import addon_utils
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    from sikh257_native import scene_setup, camera_at, sphere
    from sikh261_character import painted, strands, donor_crown
    verify_sources()
    if bpy.app.online_access:
        raise ValueError('Offline process required')
    out.mkdir(parents=True,exist_ok=True)
    native=out/'character.blend'
    if job['operation']=='reopen':
        record=json.loads((out/'build.json').read_text())
        if hashlib.sha256(native.read_bytes()).hexdigest()!=record['native_sha256']:
            raise ValueError('Native changed')
        bpy.ops.wm.open_mainfile(filepath=str(native))
        if sorted(o.name for o in bpy.data.objects)!=record['objects']:
            raise ValueError('Object inventory changed')
        (out/'reopen.json').write_text(json.dumps({'inventory_matches':True,'native_sha256':record['native_sha256']}))
        return
    if native.exists() or (out/'build.json').exists():
        raise ValueError('Preserve prior control')
    scene,cam=scene_setup()
    if not addon_utils.check(MODULE)[1]:
        addon_utils.enable(MODULE,default_set=False)
    services=importlib.import_module(MODULE+'.services')
    macro=services.TargetService.get_default_macro_info_dict()
    macro.update(gender=1., age=.48, muscle=.65, weight=.48, height=.65)
    body=services.HumanService.create_human(macro_detail_dict=macro)
    body.name='Sikh265 coherent MPFB male'
    for name,value in MORPHS.items():
        services.TargetService.load_target(body,str(INSTALLED/'data/targets'/f'{name}.target.gz'),weight=value)
    skin=painted('warm ochre authored skin',(.255,.122,.060),.12,85)
    body.data.materials.clear();body.data.materials.append(skin)
    for p in body.data.polygons:p.use_smooth=True
    sub=body.modifiers.new('anatomy subdivision','SUBSURF');sub.levels=1
    rig=services.HumanService.add_builtin_rig(body,'default')
    bpy.context.view_layer.update()
    info={'bones':{b.name:[list(rig.matrix_world@b.head_local),list(rig.matrix_world@b.tail_local)] for b in rig.data.bones}}
    eye_centers=[rig.matrix_world@rig.data.bones['eye.'+side].head_local for side in ('L','R')]
    eye_z=sum(p.z for p in eye_centers)/2
    skin_surface=BVHTree.FromObject(body,bpy.context.evaluated_depsgraph_get())
    dark=painted('dark brown brows',(.012,.008,.005),.3,110)
    for side,center in zip(('L','R'),eye_centers):
        eye=sphere('eyeball.'+side,center,(.0122,.0122,.0122),painted('warm sclera.'+side,(.52,.44,.31),.05,70))
        iris=sphere('iris.'+side,center+Vector((0,-.0116,0)),(.0053,.0014,.0053),painted('brown iris.'+side,(.075,.033,.009),.45,800))
        pupil=sphere('pupil.'+side,center+Vector((0,-.0129,0)),(.0024,.0008,.0024),dark)
        paths=[]
        for i in range(170):
            t=i/169;x=center.x+(-.025+.050*t)
            z=eye_z+.016+.003*math.sin(math.pi*t)+(i%7-3)*.00045
            loc,normal,_,_=skin_surface.ray_cast(Vector((x,-.5,z)),Vector((0,1,0)),1.)
            if loc is None:continue
            paths.append([loc+Vector((0,-.0015,-.0015)),loc+Vector((.002,-.002,.003)),loc+Vector((.004,-.0015,.005))])
        strands('brow.'+side,paths,dark,.0004)
    for name in ('rehmanpolanski_beard_viking','rehmanpolanski_moustache_viking'):
        path=ROOT/'.runtime/assets/series01-sikh263-donors/bodyparts05/clothes'/name/(name+'.mhclo')
        obj=services.HumanService.add_mhclo_asset(str(path),body,asset_type='Hair',subdiv_levels=0)
        adapt_beard(obj,eye_z,moustache='moustache' in name)
        # Preserve donor card alpha/strand texture; recolour only the pigment.
        for mat in obj.data.materials:
            if not mat or not mat.use_nodes:continue
            for node in mat.node_tree.nodes:
                if node.type=='BSDF_PRINCIPLED':
                    socket=node.inputs['Base Color']
                    for link in list(socket.links):mat.node_tree.links.remove(link)
                    socket.default_value=(.022,.012,.007,1)
                    node.inputs['Roughness'].default_value=.84
                    node.inputs['Specular IOR Level'].default_value=.18
    crown=donor_crown(out)
    # The existing donor's geometry is centered at1.640. Fit to the new
    # coherent anatomy's eye height; retain its authored diagonal folds.
    crown.location.z=eye_z+.045-1.640
    crown.scale=(.95,1.35,1.0)
    # Scaling around global origin shifts z; compensate to retain the center.
    crown.location.y=-.070
    scene.render.engine='CYCLES';scene.cycles.samples=20
    scene.render.resolution_x=640;scene.render.resolution_y=760
    scene.view_settings.view_transform='AgX'
    bpy.data.objects['key'].data.energy=260;bpy.data.objects['fill'].data.energy=110
    cam.data.ortho_scale=.64
    target=Vector((0,0,eye_z-.075))
    info.update({'macro':macro,'morphs':MORPHS,'eye_centers':[list(p) for p in eye_centers],
                 'body_bounds':[list(body.matrix_world@Vector(p)) for p in body.bound_box],
                 'status':'INTERNAL_UNREVIEWED','limitations':['donor crown is not yet a continuous releasable cloth','eye material and beard adaptation preliminary','no body performance or motorcycle fit claim']})
    bpy.ops.file.pack_all()
    for name,pos in [('front',(0,-3,eye_z)),('left',(1.7,-3,eye_z)),('right',(-1.7,-3,eye_z))]:
        camera_at(cam,pos,target);scene.render.filepath=str(out/(name+'.png'))
        bpy.ops.render.render(write_still=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(native))
    info['objects']=sorted(o.name for o in bpy.data.objects)
    info['native_sha256']=hashlib.sha256(native.read_bytes()).hexdigest()
    (out/'build.json').write_text(json.dumps(info,indent=2)+'\n')


if __name__=='__main__':
    if sys.argv[1:]==['prepare']:
        prepare()
    else:
        args=sys.argv[sys.argv.index('--')+1:]
        if len(args)!=1:raise ValueError('One structured job required')
        main(json.loads(args[0]))
