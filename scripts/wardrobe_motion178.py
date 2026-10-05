"""Reviewed moving-wardrobe operations on pinned protected foundation.

Jobs carry an enum only. No external code, paths, assets or credentials.
Inspection and failed previews are not selected production assets.
"""
import hashlib
import json
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src/movie_factory/adapters/blender'))
sys.path.insert(0, str(ROOT / 'scripts'))
BASE = ROOT / '.runtime/art-direction/series01-facebuilder-trial-01'
SOURCE = BASE / 'wardrobe174-seal01/dressed-fit.blend'
SOURCE_SHA = '65d19c99bc7232b62146df0fb866412e2431f2e8e12deb29caaa17f7e14331cd'
OPERATIONS = ('inspect01', 'settle01', 'settle02', 'settle03', 'settle04', 'settle05', 'settle06', 'move01', 'move02', 'attach01', 'attach02', 'attach03', 'attach04', 'attach05', 'attach06', 'attach07', 'attach08', 'move03', 'move04', 'settle07', 'head08', 'head09', 'move05', 'move06', 'move07', 'move08', 'move09', 'move10', 'move11', 'move12', 'move13', 'move14', 'move15', 'move16')
OPERATIONS += ('move17','move18','move19','move20','move21','move22','move23','move24','move25','move26','inspect24','inspect25')
OPERATIONS += ('move27','move28','move29','move30','move31','move32','move33','move34','move35','move36','move37')
OPERATIONS += ('move38','move39')
OPERATIONS += ('move44','move45','move47')
RIBBON_OPERATIONS=tuple('move%02d'%i for i in range(7,40))
RAISED_OPERATIONS=tuple('move%02d'%i for i in range(14,40))
RIBBON_OPERATIONS+=('move44','move45','move47')
RAISED_OPERATIONS+=('move44','move45','move47')
HYBRID_LAYOUT=BASE/'wardrobe178-hybrid44/constructed-layout.npz'
HYBRID_LAYOUT_SHA='4968da1d8bcea75a56d06bfc96d79a5869e37a1191fc09057710643cca260349'
TUCKED_LAYOUT=BASE/'wardrobe178-hybrid47/constructed-layout.npz'
TUCKED_LAYOUT_SHA='dede2257d6c15c14e17c043820f812ce1cbc627b5e46e0ed882824d6f804bd25'
GATHERED_LAYOUT=BASE/'wardrobe178-initial38b/constructed-layout.npz'
GATHERED_LAYOUT_SHA='754f50d297704e95dfd88928f0a0a2d8a00a20128cf4297b3ec59e7370c22c86'
PRE_SHAPED_LAYOUT=BASE/'wardrobe178-move36/constructed-layout.npz'
PRE_SHAPED_LAYOUT_SHA='abb7b8a203aec864dd778d2c587c5a3871360b7635ce0aa48fcdc67f4533fadf'
DOWNWARD_LAYOUT=BASE/'wardrobe178-move33/constructed-layout.npz'
DOWNWARD_LAYOUT_SHA='017b34a249bf3a8061b33fda6f8b61fbe082bef75a6a1d10025c2374c3f51b6f'
CONTINUOUS_LAYOUT=BASE/'wardrobe178-move30/constructed-layout.npz'
CONTINUOUS_LAYOUT_SHA='e8df2bfd0157e5b1e70474d044b8b904693f903552ba149403a1bd960b9f2dca'
CONTROL_LAYOUT=BASE/'wardrobe178-move18/constructed-layout.npz'
CONTROL_LAYOUT_SHA='a2df28b6537f808a71b3fc51bf45137fd654877890e059f373646d0a22fc39fd'
STAGED_HEAD = BASE / 'wardrobe178-settle03/settled-points.npz'
STAGED_HEAD_SHA = 'fda473691e5fbc5dd3734af15431199ea70f30cd0495f670a604a347725ee5e0'
MOVING_START = BASE/'wardrobe178-settle06/settled-points.npz'
MOVING_START_SHA = '73ef3a14a44ee0bf0cb91c8c5917a9db14911bad3490c31eb3fff0ef41bf56ad'
CURVED_HEAD = BASE/'wardrobe178-head09/settled-points.npz'
CURVED_HEAD_SHA = '19d8adc470c55c6cc56efe089dec5749cedc94cdd6efd87a1a49e14588a00e40'


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def validate(job):
    if not isinstance(job, dict) or set(job) != {'operation'} or job['operation'] not in OPERATIONS:
        raise ValueError('Fixed enum operation only')
    if SOURCE.is_symlink() or not SOURCE.is_file() or digest(SOURCE) != SOURCE_SHA:
        raise ValueError('Pinned source mismatch')
    if job['operation'] in ('settle04','settle05','settle06') and (STAGED_HEAD.is_symlink() or digest(STAGED_HEAD) != STAGED_HEAD_SHA):
        raise ValueError('Pinned staging input mismatch')
    if ((job['operation'].startswith('move') and job['operation'] not in RIBBON_OPERATIONS) or job['operation']=='settle07') and (MOVING_START.is_symlink() or digest(MOVING_START)!=MOVING_START_SHA):
        raise ValueError('Pinned moving start mismatch')
    if job['operation'] in ('move05','move06')+RIBBON_OPERATIONS and (CURVED_HEAD.is_symlink() or digest(CURVED_HEAD)!=CURVED_HEAD_SHA):
        raise ValueError('Pinned curved head start mismatch')
    if job['operation'] in ('move20','move21','move22','move23','move24','move25','move26','move27','move28','move29','move30','move31','move32','move33','move34','move35','move36','move37','inspect24','inspect25') and (CONTROL_LAYOUT.is_symlink() or digest(CONTROL_LAYOUT)!=CONTROL_LAYOUT_SHA):
        raise ValueError('Pinned controlled initial layout mismatch')
    if job['operation'] in ('move31','move32','move33','move34','move35','move36','move37') and (CONTINUOUS_LAYOUT.is_symlink() or digest(CONTINUOUS_LAYOUT)!=CONTINUOUS_LAYOUT_SHA):
        raise ValueError('Pinned continuous initial layout mismatch')
    if job['operation'] in ('move34','move35','move36','move37') and (DOWNWARD_LAYOUT.is_symlink() or digest(DOWNWARD_LAYOUT)!=DOWNWARD_LAYOUT_SHA):
        raise ValueError('Pinned downward initial layout mismatch')
    if job['operation']=='move37' and (PRE_SHAPED_LAYOUT.is_symlink() or digest(PRE_SHAPED_LAYOUT)!=PRE_SHAPED_LAYOUT_SHA):
        raise ValueError('Pinned pre-shaped initial layout mismatch')
    if job['operation'] in ('move38','move39','move44','move45','move47') and (GATHERED_LAYOUT.is_symlink() or digest(GATHERED_LAYOUT)!=GATHERED_LAYOUT_SHA):
        raise ValueError('Pinned gathered initial layout mismatch')
    if job['operation'] in ('move44','move45') and (HYBRID_LAYOUT.is_symlink() or digest(HYBRID_LAYOUT)!=HYBRID_LAYOUT_SHA):
        raise ValueError('Pinned hybrid initial layout mismatch')
    if job['operation']=='move47' and (TUCKED_LAYOUT.is_symlink() or digest(TUCKED_LAYOUT)!=TUCKED_LAYOUT_SHA):
        raise ValueError('Pinned tucked initial layout mismatch')
    out = BASE / ('wardrobe178-' + job['operation'])
    if out.exists() or out.is_symlink():
        raise ValueError('Never overwrite retained evidence')
    return out


def check_protected():
    import bpy
    from wardrobe_riding_fit import accepted_signature
    from body_studio_fit import coordinates_digest
    record = json.loads((SOURCE.parent / 'result.json').read_text())
    assert accepted_signature(record['protected_signatures']) == record['protected_signatures']
    body = bpy.data.objects['MF_studio_adult_body']
    assert coordinates_digest(tuple(v.co for v in body.data.vertices)) == record['body_basis_digest']


def inspect(out):
    import bpy
    from wardrobe_refinement import neutral
    from mathutils import Vector
    rig = bpy.data.objects['MF_body156_fit_rig']
    neutral(rig)
    rows = []
    for ob in bpy.context.scene.objects:
        if ob.hide_render and ob.name not in ('MF_173_static_groom_clearance', 'MF_continuous_head_neck'):
            continue
        if ob.type not in ('MESH', 'CURVE', 'CURVES'):
            continue
        if ob.name.startswith(('MF_fit_horse', 'MF_fit_Full', 'MF_fit_Torus')):
            continue
        bound = [ob.matrix_world @ Vector(p) for p in ob.bound_box]
        row = {'name': ob.name, 'type': ob.type, 'bounds':
               [[min(p[k] for p in bound) for k in range(3)],
                [max(p[k] for p in bound) for k in range(3)]],
               'parent': ob.parent.name if ob.parent else None,
               'matrix': [list(r) for r in ob.matrix_world],
               'modifiers': [(m.name, m.type) for m in ob.modifiers]}
        if ob.type == 'MESH':
            row['vertices'] = len(ob.data.vertices)
            row['attributes'] = [(a.name, a.data_type) for a in ob.data.attributes]
        rows.append(row)
    result = {'source': SOURCE_SHA, 'objects': rows,
              'bones': {b.name: {'head': list(b.head_local), 'tail': list(b.tail_local)}
                        for b in rig.data.bones},
              'unit_scale': bpy.context.scene.unit_settings.scale_length,
              'gravity': list(bpy.context.scene.gravity),
              'protected_exact': True, 'visual_gate': 'NOT_RUN',
              'handler_sha256': digest(Path(__file__))}
    (out / 'inventory.json').write_text(json.dumps(result, indent=2) + '\n')


def sheet_grid(rows, columns, point):
    points = [point(i / (rows - 1), j / (columns - 1))
              for i in range(rows) for j in range(columns)]
    faces = [(i * columns + j, i * columns + j + 1,
              (i + 1) * columns + j + 1, (i + 1) * columns + j)
             for i in range(rows - 1) for j in range(columns - 1)]
    return points, faces


def loop_path(t, course):
    """Separated initial layout; physics, not projection, supplies final folds."""
    from mathutils import Vector
    anchors = [(0, 2.05 + .14 * course, -1.8 - .22 * course),
               (1.50, 1.05, -1.75 - .22 * course),
               (1.91 + .06 * course, .08, -1.77 - .08 * course),
               (1.12, -1.48 - .10 * course, -2.30 - .55 * course),
               (-.05, -1.64 - .12 * course, -2.63 - .48 * course),
               (-1.20, -1.20 - .09 * course, -2.13 - .16 * course),
               (-1.91 - .06 * course, .14, -1.76 - .10 * course),
               (-1.30, 1.12, -1.82 - .32 * course),
               (0, 2.06 + .14 * course, -2.03 - .26 * course)]
    s = max(0, min(1, t)) * (len(anchors) - 1)
    i = min(len(anchors) - 2, int(s)); u = s - i
    a, b, c, d = [Vector(anchors[max(0, min(len(anchors) - 1, k))])
                  for k in (i - 1, i, i + 1, i + 2)]
    return .5 * ((2 * b) + (-a + c) * u + (2*a-5*b+4*c-d)*u*u + (-a+3*b-3*c+d)*u*u*u)


def shoulder_loop(t, course):
    """Periodic sewn course: no overlapping fully pinned rear tabs.

    Two courses preserve the screen intent. These are assembled garment
    panels, not a claim that this is a manufacturable unseamed rectangle.
    """
    from mathutils import Vector
    anchors = [(0,2.02+.09*course,-1.78-.20*course),
               (1.20,1.12,-1.82-.18*course),
               (1.53,.12,-1.93-.10*course),
               (1.05,-1.15,-2.65-.45*course),
               (0,-1.40,-2.95-.44*course),
               (-1.05,-1.10,-2.53-.38*course),
               (-1.53,.18,-1.87-.12*course),
               (-1.18,1.14,-1.91-.22*course)]
    s=(t%1)*len(anchors);i=int(s);u=s-i
    a,b,c,d=[Vector(anchors[k%len(anchors)]) for k in (i-1,i,i+1,i+2)]
    return .5*((2*b)+(-a+c)*u+(2*a-5*b+4*c-d)*u*u+(-a+3*b-3*c+d)*u*u*u)


def periodic_grid(rows, columns, point):
    points=[point(i/rows,j/(columns-1)) for i in range(rows) for j in range(columns)]
    faces=[(i*columns+j,i*columns+j+1,((i+1)%rows)*columns+j+1,
            ((i+1)%rows)*columns+j) for i in range(rows) for j in range(columns-1)]
    return points,faces


def clean_patterns(periodic=False, broad_head=False):
    from mathutils import Vector
    points, faces = sheet_grid(45, 31, lambda u, v: (
        (v-.5)*(6.0 if broad_head else 3.18),
        -.18+(5.2 if broad_head else 4.45)*u+(.65*(2*v-1)**2*(1-u) if broad_head else 0),
        1.38))
    pins = {}
    # Two small actual crown-contact supports. No broad flat pin patch.
    for j in (12, 18):
        pins[7*31+j] = 1.
    components = [len(points)]
    for course in (0, 1):
        offset = len(points)
        def sample(u, v):
            path=shoulder_loop if periodic else loop_path
            p = path(u, course)
            tangent = (path(u+.002,course)-path(u-.002,course)) if periodic else path(min(1,u+.002),course)-path(max(0,u-.002),course)
            side = min(1., (abs(p.x)/1.90)**5)
            n = Vector((p.x*.15, p.y-.14, 0)).normalized().lerp(Vector((0,0,1)), side).normalized()
            across = tangent.cross(n).normalized()
            width = (.97-.20*side) if periodic else (1.48-.38*side)
            return tuple(p+across*((v-.5)*width))
        pp, ff = periodic_grid(96,13,sample) if periodic else sheet_grid(97, 13, sample)
        points.extend(pp); faces.extend(tuple(offset+k for k in f) for f in ff)
        for i in range(96 if periodic else 97):
            for j in range(13):
                # Concealed rear anchoring has breadth; no point-cinched end.
                if periodic:
                    # Small concealed rear attachment; leave edges free.
                    if i in (0,1,95) and j in (5,6,7):pins[offset+i*13+j]=1.
                    # Soft garment contact support at inner shoulder edge.
                    if i in (23,24,25,71,72,73) and j in (5,6,7):pins[offset+i*13+j]=.6
                elif i in (0, 1, 95, 96):pins[offset+i*13+j] = 1.
        components.append(len(pp))
    assert len(points) < 5000 and all(math.isfinite(c) for p in points for c in p)
    return points, faces, pins, components


def supported_head_pattern():
    """Cut panel with a curved supported opening and narrower rear hem.

    Only the opening arc is supported; all sides/rear are free cloth. This is
    initial cutting/dressing, not a post-solve projection or rigid crown patch.
    """
    from wardrobe_motion178_controls import smooth
    points,faces=sheet_grid(45,31,lambda u,v:(
        (v-.5)*(4.6-1.2*smooth((u-.65)/.35)),
        .03+4.7*u+.70*(2*v-1)**2*(1-u),1.38))
    pins={j:1. for j in range(8,23)}
    return points,faces,pins,[len(points)]


def dressed_head_pattern():
    """A pre-dressed curved strip, not a flat sheet dropped on the crown.

    Arc length supplies side fabric without placing unsupported corners above
    the head. Simulation remains responsible for free-side/rear settling.
    """
    def point(u,v):
        angle=(2*v-1)*1.70
        return (1.49*math.sin(angle),.03+4.7*u+.40*math.sin(angle)**2*(1-u),
                1.24*math.cos(angle)+.025)
    points,faces=sheet_grid(45,31,point)
    return points,faces,{j:1. for j in range(6,25)},[len(points)]


def ribbon_path(t,raised_shoulders=False):
    """One two-turn route with distinct diagonal crossings and rear ends."""
    anchors=((0,2.15,-2.55),(1.15,1.2,-2.22),(1.60,.15,-2.0),
             (1.10,-1.40,-2.50),(0,-1.65,-2.95),(-1.10,-1.3,-3.15),
             (-1.65,.25,-2.15),(-1.0,1.3,-1.75),(0,2.4,-1.9),
             (1.15,1.4,-2.1),(1.65,.15,-2.45),(1.05,-1.60,-3.55),
             (0,-1.70,-3.30),(-1.10,-1.40,-2.85),(-1.65,.1,-2.10),
             (-1.15,1.3,-2.65),(0,2.4,-2.90))
    if raised_shoulders:
        anchors=list(anchors)
        for i in (2,6,10,14):
            p=anchors[i];anchors[i]=(math.copysign(1.60,p[0]),.15,-1.62 if i<8 else -1.52)
    s=max(0,min(1,t))*(len(anchors)-1);i=min(len(anchors)-2,int(s));u=s-i
    a,b,c,d=[anchors[max(0,min(len(anchors)-1,k))] for k in (i-1,i,i+1,i+2)]
    return tuple(.5*(2*b[k]+(-a[k]+c[k])*u+(2*a[k]-5*b[k]+4*c[k]-d[k])*u*u+
                          (-a[k]+3*b[k]-3*c[k]+d[k])*u*u*u) for k in range(3))


def twice_wrapped_patterns(raised_shoulders=False):
    """Broad continuous ribbon, not two periodic necklaces.

    Cutting/dressing only. Actual free folds and movement still require the
    native solver and all-angle visual gate.
    """
    def unit(v):
        length=math.sqrt(sum(c*c for c in v))
        if length<1e-8:raise ValueError('Degenerate ribbon frame')
        return tuple(c/length for c in v)
    def point(u,v):
        p=ribbon_path(u,raised_shoulders);a=ribbon_path(u-.001,raised_shoulders);b=ribbon_path(u+.001,raised_shoulders)
        tangent=unit(tuple(b[k]-a[k] for k in range(3)))
        side=min(1.,(abs(p[0])/1.65)**4)
        horizontal=unit((p[0]*.35,p[1]-.14,0.))
        n=unit((horizontal[0]*(1-side),horizontal[1]*(1-side),side))
        across=unit((tangent[1]*n[2]-tangent[2]*n[1],
                     tangent[2]*n[0]-tangent[0]*n[2],tangent[0]*n[1]-tangent[1]*n[0]))
        width=1.48-.65*side
        return tuple(p[k]+across[k]*(v-.5)*width for k in range(3))
    points,faces,pins,components=dressed_head_pattern()
    offset=len(points);pp,ff=sheet_grid(192,13,point)
    points.extend(pp);faces.extend(tuple(offset+i for i in f) for f in ff)
    for row in (23,24,25,71,72,73,118,119,120,166,167,168):
        pins[offset+row*13+6]=.35
    return points,faces,pins,[1395,2496]


def clean_foundation():
    import bpy
    import wardrobe_studio as studio
    import wardrobe_construction174 as prior
    from wardrobe_refinement import neutral
    from wardrobe_outer175 import tunic_support_cloud
    import wardrobe_tension
    rig = bpy.data.objects['MF_body156_fit_rig'];neutral(rig)
    mats = studio.make_materials()
    # Regenerate fitted garments only, never call the abandoned shawl fitter.
    prior.sculpt(mats)
    # The inherited short-sleeve recession went below skin at the armpit.
    # Tight fitted garment coverage is different from loose shawl mechanics.
    # Repair that neutral garment interface only; accepted skin is read-only.
    from wardrobe_refinement import tree_for
    skin=tree_for(bpy.data.objects['MF_studio_adult_body'])
    tunic=bpy.data.objects['MF_fit_tunic_173_visible']
    rest=tunic.data.attributes['MF_173_material_coords'].data
    for vertex in tunic.data.vertices:
        rp=rest[vertex.index].vector
        if not (-3.25<rp.z<-1.35 and abs(rp.x)>1.35):continue
        p=tunic.matrix_world@vertex.co
        hit,normal,_,distance=skin.find_nearest(p)
        if hit is not None and distance<.35 and (p-hit).dot(normal)<.032:
            vertex.co=tunic.matrix_world.inverted()@(hit+normal*.032)
    tunic.data.update()
    wardrobe_tension.support_cloud = tunic_support_cloud
    prior.leather(studio.torso_matrix(-2.7), mats)
    proxy = studio.groom_support()
    for ob in bpy.context.scene.objects:
        if ob.name.startswith(('MF_173_open_scarf', 'MF_173_diagonal_scarf_fall',
                               'MF_172_', 'MF_fit_horse', 'MF_fit_saddle', 'MF_fit_bridle',
                               'MF_fit_bit', 'MF_fit_Torus', 'MF_fit_Full', 'MF_fit_rein_',
                               'MF_fit_stirrup_leather_', 'MF_170_tail_')):
            ob.hide_render = True
    underarm_gusset(mats['cloth'])
    return rig, mats, proxy


def inspect_pin_contacts(out):
    """Measure actual18 supported border contact, not centre-line proxies."""
    import bpy
    import numpy as np
    from mathutils import Vector
    from wardrobe_refinement import tree_for
    clean_foundation()
    names=('MF_studio_adult_body','MF_fit_tunic_173_visible','MF_173_tension_harness_-1',
           'MF_173_tension_harness_1','MF_171_fitted_sleeve_L_173_visible','MF_171_fitted_sleeve_R_173_visible')
    trees=[tree_for(bpy.data.objects[n]) for n in names]
    rows=[];scale=bpy.context.scene.unit_settings.scale_length
    with np.load(CONTROL_LAYOUT,allow_pickle=False) as data:
        points=data['points'];pins=data['pin_indices']
    for i in pins:
        if i<1395:continue
        p=Vector(points[i])
        if out.name.endswith('inspect24') and not (.65<abs(p.x)<2.25 and abs(p.y)<.65):continue
        nearest=[(tree.find_nearest(p),name) for tree,name in zip(trees,names)]
        nearest=[(r,name) for r,name in nearest if r[0] is not None]
        nr,name=min(nearest,key=lambda item:item[0][3])
        contact={'nearest_support':name,'nearest_distance_m':nr[3]*scale,
                 'nearest_signed_m':(p-nr[0]).dot(nr[1])*scale,
                 'skin_signed_m':(p-nearest[0][0][0]).dot(nearest[0][0][1])*scale}
        candidates=[tree.ray_cast(Vector((p.x,p.y,-.8)),Vector((0,0,-1)),3.) for tree in trees]
        candidates=[r for r in candidates if r[0] is not None]
        if not candidates:
            rows.append({'index':int(i),'point':list(p),'surface':'NOT_FOUND',**contact});continue
        hit,normal,_,_=max(candidates,key=lambda r:r[0].z)
        layer=int(i>=1395+1248);desired=.005+.007*layer
        gap=(p.z-hit.z)*scale
        rows.append({'index':int(i),'row':int((i-1395)//13),'point':list(p),**contact,
                     'surface_point':list(hit),'vertical_gap_m':gap,
                     'desired_layer_gap_m':desired,'gap_error_m':gap-desired})
    check_protected()
    (out/'result.json').write_text(json.dumps({'purpose':'Actual pinned upper-border shoulder contact audit',
        'layout_sha256':CONTROL_LAYOUT_SHA,'protected_exact':True,'visual_gate':'NOT_RUN',
        'rows':rows},indent=2)+'\n')


def underarm_gusset(material):
    """Fitted mobility panel covers the inherited sleeve/tunic topology gap.

    This is garment construction, not a body correction or loose-cloth fitter.
    Duplicate skinning/correctives read-only so the panel follows the accepted
    anatomy rather than hiding a deformation defect. Above-clavicle skin and
    neck remain outside its mask. Panel borders overlap existing cloth.
    """
    import bpy
    body=bpy.data.objects['MF_studio_adult_body']
    ob=body.copy();ob.data=body.data.copy();ob.name='MF178_render_underarm_gusset'
    bpy.context.scene.collection.objects.link(ob);ob.hide_render=False;ob.hide_viewport=False
    ob.data.materials.clear();ob.data.materials.append(material)
    for polygon in ob.data.polygons:polygon.material_index=0
    group=ob.vertex_groups.new(name='MF178 underarm garment coverage')
    coords=ob.data.attributes.new('MF_173_material_coords','FLOAT_VECTOR','POINT')
    for vertex,item in zip(ob.data.vertices,coords.data):
        p=vertex.co.copy();item.vector=p
        if .85<abs(p.x)<2.75 and -4.20<p.z<-2.45:
            group.add([vertex.index],1.,'REPLACE')
    offset=ob.modifiers.new('Garment ease above accepted skin','DISPLACE')
    offset.direction='NORMAL';offset.strength=.042;offset.mid_level=0
    mask=ob.modifiers.new('Mobility panel only, not full-body clothing','MASK')
    mask.vertex_group=group.name
    # Do not subdivide the entire copied body before discarding 90% of it.
    # Mask after skinning/correctives but before subdivision; garment borders
    # remain overlapped under the existing fitted sleeves/tunic.
    subsurf=next((m for m in ob.modifiers if m.type=='SUBSURF'),None)
    if subsurf:
        bpy.context.view_layer.objects.active=ob
        while list(ob.modifiers).index(mask)>list(ob.modifiers).index(subsurf):
            bpy.ops.object.modifier_move_up(modifier=mask.name)
    shell=ob.modifiers.new('Gusset cloth thickness','SOLIDIFY');shell.thickness=.014
    ob.data.update()
    return ob


def solver_support(source, scale, faces_limit=4500):
    import bpy
    from mathutils import Matrix
    if faces_limit not in (4500,12000):raise ValueError('Fixed reviewed collision resolution only')
    # Body/groom have no shell; cloth has one. Evaluate a collision-only
    # outer surface generically, restoring every source modifier afterward.
    states = [(m, m.show_viewport) for m in source.modifiers if m.type == 'SUBSURF']
    try:
        for mod, _ in states:mod.show_viewport = False
        bpy.context.view_layer.update()
        ev = source.evaluated_get(bpy.context.evaluated_depsgraph_get())
        data = bpy.data.meshes.new_from_object(ev, depsgraph=bpy.context.evaluated_depsgraph_get())
    finally:
        for mod, state in states:mod.show_viewport = state
        bpy.context.view_layer.update()
    for vertex in data.vertices:vertex.co = scale*(source.matrix_world@vertex.co)
    data.update()
    ob = bpy.data.objects.new('MF178_support_'+source.name, data)
    bpy.context.scene.collection.objects.link(ob);ob.hide_render = True
    # Collision quality must not depend on the render-resolution body/groom.
    if len(data.polygons) > faces_limit:
        decimate = ob.modifiers.new('Collision-only simplification', 'DECIMATE')
        decimate.ratio = min(1, faces_limit/len(data.polygons))
    ob.modifiers.new('Solver collision', 'COLLISION')
    ob.collision.thickness_outer = .0025
    ob.collision.cloth_friction = 8
    return ob


def separated_initial_layout(points, faces, components, supports, scale, curved=False):
    """Stage the physically settled headfall, then lay courses OUTSIDE it.

    This adjusts the starting assembly only. No projection runs after solving.
    Retained headfall is a component diagnostic, not an accepted design target.
    """
    import bpy
    import numpy as np
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    from wardrobe_refinement import tree_for
    with np.load(CURVED_HEAD if curved else STAGED_HEAD, allow_pickle=False) as record:
        head = record['settled'][:components[0]]
    if head.shape != (components[0],3) or not np.isfinite(head).all():
        raise ValueError('Invalid staged head surface')
    points[:components[0]] = [tuple(p) for p in head]
    trees = [tree_for(ob) for ob in supports]
    head_tree = BVHTree.FromPolygons([Vector(p)*scale for p in points[:components[0]]],
        [f for f in faces if max(f)<components[0]])
    trees.append(head_tree)
    shifts = []
    for i in range(components[0],len(points)):
        course = int((i-components[0]) >= 1248)
        p = Vector(points[i])*scale
        root = Vector((0,.14*scale,p.z));d=p-root
        length=d.length
        if length < .05:raise ValueError('Invalid outer-course radial layout')
        d.normalize();limit=length
        for tree in trees:
            origin=root.copy()
            for _ in range(6):
                hit,_,_,_=tree.ray_cast(origin,d,1.)
                if hit is None:break
                limit=max(limit,(hit-root).dot(d)+(.065+(.075 if curved else .16)*course)*scale)
                origin=hit+d*(.004*scale)
        shifted=root+d*limit
        shifts.append((shifted-p).length/scale)
        points[i] = tuple(shifted/scale)
    return {'head_stage_sha256':CURVED_HEAD_SHA if curved else STAGED_HEAD_SHA,'maximum_initial_clearance_shift_native':max(shifts),
            'mean_initial_clearance_shift_native':sum(shifts)/len(shifts),
            'post_solve_projection':False}


def chest_bridge(supports, scale, upper_z=-1.52, upper_band=.23):
    """Smooth collision-only support bridges narrow harness contact gaps.

    Measured height-local torso sections, not a whole-character balloon or
    final cloth projection. Actual hair and shoulders retain separate support.
    """
    import bpy
    import numpy as np
    import bmesh
    from wardrobe_footbed import footprint,center,radius
    cloud=[]
    for ob in supports:
        if not any(k in ob.name for k in ('tunic','harness','adult_body')):continue
        ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=ev.to_mesh()
        cloud.extend(tuple(v.co/scale) for v in mesh.vertices
                     if -4.5<v.co.z/scale<-1.40 and abs(v.co.x/scale)<2.1)
        ev.to_mesh_clear()
    cloud=np.array(cloud);points=[];faces=[]
    if upper_z not in (-1.52,-2.35):raise ValueError('Fixed reviewed bridge extent only')
    if upper_band not in (.23,.055):raise ValueError('Fixed reviewed support section only')
    for row,z in enumerate(np.linspace(-4.4,upper_z,25)):
        # Thick sections borrow the broader lower shoulder/upper-arm outline
        # at a height where that surface does not exist. Keep lower chest
        # support unchanged and sample the actual upper level more closely.
        sample=cloud[np.abs(cloud[:,2]-z)<(upper_band if z>-2.6 else .23)]
        if len(sample)<4:raise ValueError('Missing chest support section')
        hull=footprint(sample[:,:2]);origin=center(hull)
        for column in range(64):
            angle=math.tau*column/64;d=(math.cos(angle),math.sin(angle))
            r=radius(hull,origin,d)
            if r is None:raise ValueError('Invalid chest support ring')
            points.append(((origin[0]+d[0]*(r+.045))*scale,
                           (origin[1]+d[1]*(r+.045))*scale,z*scale))
        if row:
            for column in range(64):
                a=(row-1)*64+column;b=(row-1)*64+(column+1)%64
                faces.append((a,b,b+64,a+64))
    for row in (0,24):
        ring=points[row*64:(row+1)*64];i=len(points)
        points.append(tuple(sum(p[k] for p in ring)/64 for k in range(3)))
        for column in range(64):
            a=row*64+column;b=row*64+(column+1)%64
            faces.append((i,b,a) if row==0 else (i,a,b))
    data=bpy.data.meshes.new('MF178 chest contact bridge');data.from_pydata(points,[],faces);data.update()
    bm=bmesh.new();bm.from_mesh(data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(data);bm.free()
    ob=bpy.data.objects.new('MF178_support_chest_bridge',data)
    bpy.context.scene.collection.objects.link(ob);ob.hide_render=True
    ob.modifiers.new('Broad collision support','COLLISION');ob.collision.thickness_outer=.0025
    return ob


def settle(out):
    import bpy
    import numpy as np
    import wardrobe_studio as studio
    from wardrobe_riding_fit import fit_render
    rig, mats, groom = clean_foundation()
    broad=out.name.endswith('settle07')
    points, faces, pins, components = clean_patterns(periodic=out.name.endswith(('settle06','settle07')), broad_head=broad)
    if out.name.endswith('head08'):
        points,faces,pins,components=supported_head_pattern()
    if out.name.endswith('head09'):
        points,faces,pins,components=dressed_head_pattern()
    if broad:
        import wardrobe_motion178_controls as controls
        with np.load(MOVING_START,allow_pickle=False) as source:
            pp=source['settled']
            if pp.shape!=(len(points),3):raise ValueError('Initial course topology mismatch')
            points[components[0]:]=[tuple(p) for p in pp[components[0]:]]
        for offset in (components[0],components[0]+components[1]):
            for row in (0,1,95):
                for col in (5,6,7):pins.pop(offset+row*13+col,None)
        for index in range(components[0]+components[1],len(points)):
            p=list(points[index]);p[2]+=.25*controls.smooth((-p[1]-.2)/1.2);points[index]=tuple(p)
    scale = bpy.context.scene.unit_settings.scale_length
    if not .10 < scale < .15:raise ValueError('Unexpected assembly scale')
    # Solve in metres; preserve the native render assembly and local data.
    supports = []
    for name in ('MF_studio_adult_body', 'MF_fit_tunic_173_visible',
                 'MF_171_fitted_sleeve_L_173_visible','MF_171_fitted_sleeve_R_173_visible',
                 'MF_173_tension_harness_-1','MF_173_tension_harness_1'):
        supports.append(solver_support(bpy.data.objects[name], scale))
    supports.append(solver_support(groom, scale))
    if out.name.endswith(('settle05','settle06','settle07')):
        supports.append(chest_bridge(supports,scale))
    staging = None
    if out.name.endswith(('settle04','settle05','settle06')):
        staging = separated_initial_layout(points,faces,components,supports,scale)
    # Initial layout only: register the tiny supported points to actual hair,
    # then let the unpinned cloth solve. Never project the final drape.
    from wardrobe_refinement import tree_for
    from mathutils import Vector
    tree = tree_for(groom)
    if out.name.endswith('head09'):
        # Initial dressing only. Use the actual groom's nearest supported
        # opening arc rather than a vertical projection flattening every pin
        # to the same crown height. No post-solve surface fitting.
        for i in pins:
            hit,normal,_,_=tree.find_nearest(Vector(points[i]))
            if hit is None:raise ValueError('Missing actual groom opening')
            points[i]=tuple(hit+normal*.055)
    for i in list(pins):
        if out.name.endswith('head09'):break
        if i >= components[0]:continue
        p = Vector(points[i])
        hit, _, _, _ = tree.ray_cast(Vector((p.x,p.y,3)), Vector((0,0,-1)), 7)
        if hit is None:raise ValueError('Missing actual crown support')
        points[i] = tuple(hit+Vector((0,0,.05)))
    data = bpy.data.meshes.new('MF178_clean_cloth')
    data.from_pydata([tuple(scale*c for c in p) for p in points], [], faces);data.update()
    cloth = bpy.data.objects.new('MF178_solver', data)
    bpy.context.scene.collection.objects.link(cloth);cloth.hide_render = True
    pin = cloth.vertex_groups.new(name='Supported crown and rear overlap')
    for i, weight in pins.items():pin.add([i], weight, 'REPLACE')
    mod = cloth.modifiers.new('Continuous native cloth, not a frozen settle', 'CLOTH')
    settings = mod.settings; settings.quality = 8; settings.mass = .22
    settings.tension_stiffness = 25;settings.compression_stiffness = 25
    settings.shear_stiffness = 12;settings.bending_stiffness = .035
    settings.tension_damping = 6;settings.compression_damping = 6;settings.shear_damping = 6
    settings.air_damping = 3; settings.vertex_group_mass = pin.name
    mod.collision_settings.use_collision = True;mod.collision_settings.distance_min = .003
    mod.collision_settings.use_self_collision = True;mod.collision_settings.self_distance_min = .003
    mod.point_cache.frame_start = 1;mod.point_cache.frame_end = 73
    scene = bpy.context.scene;scene.gravity = (0,0,-9.81);scene.render.fps = 24
    scene.cycles.samples = 12
    display = studio.panel('MF178_visible_shawl', points, faces, mats['scarf'], .014, 1)
    for frame in range(1,74):
        scene.frame_set(frame);bpy.context.view_layer.update()
        ev = cloth.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh = ev.to_mesh()
        coordinates = np.array([v.co[:] for v in mesh.vertices], dtype=float)/scale
        ev.to_mesh_clear()
        if not np.isfinite(coordinates).all() or np.max(np.abs(coordinates)) > 100:
            raise ValueError('Nonfinite or escaped cloth; internal FAIL')
        if frame%12 == 0:print('178 clean cloth settle', frame, flush=True)
    display.data.vertices.foreach_set('co', coordinates.flatten());display.data.update()
    bpy.context.view_layer.update()
    for label, angle in (('front',0),('rear',180),('profile',90)):
        fit_render(out, label, angle, (0,.15,-1.7), 7.5, (600,660))
    np.savez_compressed(out/'settled-points.npz', initial=np.array(points), settled=coordinates)
    check_protected()
    (out/'result.json').write_text(json.dumps({'visual_gate':'NOT_RUN',
        'protected_exact':True,'source_sha256':SOURCE_SHA,'handler_sha256':digest(Path(__file__)),
        'components':components,'pins':len(pins),'metres_per_native_unit':scale,'staging':staging,
        'native_cloth_modifier_retained':True,'motion_gate':'NOT_RUN'}, indent=2)+'\n')


def main():
    import bpy
    job = json.loads(Path(sys.argv[sys.argv.index('--') + 1]).read_text())
    out = validate(job)
    out.mkdir()
    for name in ('wardrobe_motion178.py','wardrobe_motion178_controls.py','wardrobe_motion178_playback.py','wardrobe_motion178_review.py','wardrobe_motion178_cut.py'):
        (out/name).write_bytes((ROOT/'scripts'/name).read_bytes())
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE), load_ui=False, use_scripts=False)
    check_protected()
    if job['operation'] == 'inspect01':inspect(out)
    elif job['operation'] in ('inspect24','inspect25'):inspect_pin_contacts(out)
    elif job['operation'].startswith('attach'):
        import bpy
        import numpy as np
        import wardrobe_motion178_controls as controls
        from wardrobe_riding_fit import fit_render
        rig,_,_=clean_foundation();sample=controls.body_weight_sampler()
        rows={}
        for name in ('MF_fit_tunic_173_visible','MF_171_fitted_sleeve_L_173_visible',
                     'MF_171_fitted_sleeve_R_173_visible','MF_173_tension_harness_-1',
                     'MF_173_tension_harness_1'):
            ob=bpy.data.objects[name];controls.bind(ob,rig,sample)
            totals={g.name:0. for g in ob.vertex_groups}
            for v in ob.data.vertices:
                for g in v.groups:totals[ob.vertex_groups[g.group].name]+=g.weight
            rows[name]={'bone_weight_totals':totals,'modifiers':[(m.name,m.type,getattr(m,'use_vertex_groups',None)) for m in ob.modifiers]}
        if job['operation']=='attach04':
            target=controls.render_surface_target()
            for name in ('MF_fit_tunic_173_visible','MF_171_fitted_sleeve_L_173_visible',
                         'MF_171_fitted_sleeve_R_173_visible'):
                controls.bind_render_surface(bpy.data.objects[name],target)
        controls.animate(rig);bpy.context.scene.frame_set(145);bpy.context.view_layer.update()
        patch=bpy.data.objects['MF178_render_underarm_gusset']
        ev=patch.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=ev.to_mesh()
        rows['mobility_panel']={'evaluated_vertices':len(mesh.vertices),'evaluated_faces':len(mesh.polygons),
                               'hide_render':patch.hide_render,'hide_viewport':patch.hide_viewport,
                               'group_support':len([v for v in patch.data.vertices if any(g.group==patch.vertex_groups['MF178 underarm garment coverage'].index for g in v.groups)])}
        ev.to_mesh_clear()
        for ob in bpy.context.scene.objects:
            if '_seam_' in ob.name or 'harness_welt' in ob.name:ob.hide_render=True
        bpy.context.scene.cycles.samples=8
        for label,angle in (('front',0),('profile',90)):
            fit_render(out,label,angle,(0,-1.3,-2.2),8.,(540,600))
        check_protected()
        (out/'result.json').write_text(json.dumps({'protected_exact':True,'visual_gate':'NOT_RUN',
                    'binding':rows,'purpose':'Attachment-only diagnostic before next cloth solve'},indent=2)+'\n')
    elif job['operation'].startswith('move'):
        import numpy as np
        import wardrobe_motion178_playback as playback
        if job['operation'] in RIBBON_OPERATIONS:initial=np.array(twice_wrapped_patterns(raised_shoulders=job['operation'] in RAISED_OPERATIONS)[0])
        else:
            with np.load(MOVING_START,allow_pickle=False) as record:initial=record['settled'].copy()
        playback.move(out,sys.modules[__name__],initial)
    else:settle(out)
    check_protected()


if __name__ == '__main__':
    main()
