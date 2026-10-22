"""Source-derived illustrated skin transfer; pinned static bust, bounded jobs."""
import hashlib
import json
import math
import statistics
from pathlib import Path
import shutil
import sys

ROOT=Path(__file__).resolve().parents[4]
BASE=ROOT/'.runtime/art-direction/series01-facebuilder-trial-01'
SOURCE=BASE/'posterior-neck-build-16/character-upperbody.blend'
SOURCE_SHA='76b2a6c7f4f1c2288ed746ebb3cf146b4146650058e263c6dd16b6f9225ef080'


def validate(job):
    if not isinstance(job,dict) or set(job)!={'operation','candidate'}:raise ValueError('Exact keys required')
    if job['operation'] not in ('build','emission','verify','portraits') or type(job['candidate']) is not int or job['candidate'] not in (1,2,3,4,5,6,7):raise ValueError('Unsupported job')
    if SOURCE.is_symlink() or hashlib.sha256(SOURCE.read_bytes()).hexdigest()!=SOURCE_SHA:raise ValueError('Pinned source changed')
    out=BASE/f'bust-detail-{job["operation"]}-{job["candidate"]:02}'
    if out.exists() or shutil.disk_usage(BASE).free<5_000_000_000:raise ValueError('Existing output or disk low')
    return out


def smooth(t):
    t=max(0.,min(1.,t));return t*t*(3-2*t)


def original_face_weight(x,y,z):
    ax=abs(x)
    top=1.10-.69*min(ax/.85,1.)**1.7
    bottom=-.86+.32*min(ax/.80,1.)**2
    return smooth((top-z)/.15)*smooth((z-bottom)/.14)*smooth((-.27-y)/.27)*smooth((.81-ax)/.16)


def corrected_face_weight(x,y,z):
    ax=abs(x)
    top=.94-.62*min(ax/.85,1.)**1.7
    bottom=-.86+.32*min(ax/.80,1.)**2
    return smooth((top-z)/.13)*smooth((z-bottom)/.14)*smooth((-.34-y)/.22)*smooth((.79-ax)/.17)


def clean_edge_face_weight(x,y,z):
    ax=abs(x)
    top=.87-.50*min(ax/.85,1.)**1.7
    bottom=-.86+.32*min(ax/.80,1.)**2
    return smooth((top-z)/.19)*smooth((z-bottom)/.14)*smooth((-.36-y)/.25)*smooth((.77-ax)/.17)


def texture_material(candidate):
    import bpy
    ob=bpy.data.objects['MF_continuous_head_neck'];assert ob.data.users==1
    mat=ob.data.materials[0].copy();ob.data.materials[0]=mat;mat.name=f'MF_illustrated_bust_skin_{candidate:02}'
    n,l=mat.node_tree.nodes,mat.node_tree.links;p=n.get('Principled BSDF')
    # Preserve the accepted bilateral facial chain, before old neck-projection/tint repairs.
    original=n['Mix (Legacy).001'].outputs['Color']
    im=bpy.data.images['frontal-v02-individualized.png']
    assert tuple(im.size)==(955,1647) and im.packed_file,'Expected embedded approved portrait'
    attr=ob.data.attributes.new('MF_original_face_detail','FLOAT','POINT')
    face_fn=original_face_weight if candidate==1 else corrected_face_weight if candidate==2 else clean_edge_face_weight
    for v,a in zip(ob.data.vertices,attr.data):a.value=face_fn(*v.co)
    def node(kind):return n.new('ShaderNode'+kind)
    def mathnode(op,a,b=0):
        q=node('Math');q.operation=op
        for i,v in enumerate((a,b)):
            if isinstance(v,(int,float)):q.inputs[i].default_value=v
            else:l.new(v,q.inputs[i])
        return q.outputs[0]
    def vector(op,a,b):
        q=node('VectorMath');q.operation=op
        for i,v in enumerate((a,b)):
            if isinstance(v,tuple):q.inputs[i].default_value=v
            else:l.new(v,q.inputs[i])
        return q.outputs[0]
    def mix(a,b,f):
        q=node('MixRGB')
        if isinstance(f,(float,int)):q.inputs[0].default_value=f
        else:l.new(f,q.inputs[0])
        l.new(a,q.inputs[1]);l.new(b,q.inputs[2]);return q.outputs[0]
    coord=node('TexCoord');warp=node('TexNoise');warp.inputs['Scale'].default_value=2.5;warp.inputs['Detail'].default_value=2
    l.new(coord.outputs['Object'],warp.inputs['Vector'])
    warped=vector('ADD',coord.outputs['Object'],vector('MULTIPLY',vector('SUBTRACT',warp.outputs['Color'],(.5,.5,.5)),(.12,.12,.12)))
    xyz=node('SeparateXYZ');l.new(warped,xyz.inputs[0])
    normal=node('SeparateXYZ');l.new(coord.outputs['Normal'],normal.inputs[0])
    weights=[mathnode('POWER',mathnode('ABSOLUTE',normal.outputs[k]),4) for k in ('X','Y','Z')]
    # Safe cheek rectangle, excluding eyes, lips, hair and sharp silhouette shading.
    rect=(332/955,410/955,1-635/1647,1-545/1647)
    pixel_width,pixel_height=78,90
    if candidate>=3:
        # More even forehead donor avoids the cheek's curved dark mark repeating.
        rect=(425/955,555/955,1-423/1647,1-360/1647)
        pixel_width,pixel_height=130,63
    colors=[]
    fields=None
    if candidate==4:
        field=node('TexNoise');field.inputs['Scale'].default_value=3.5;field.inputs['Detail'].default_value=1
        l.new(vector('ADD',coord.outputs['Object'],(1.37,9.17,4.9)),field.inputs['Vector'])
        fields=node('SeparateColor');l.new(field.outputs['Color'],fields.inputs['Color'])
    planes=((('X','Z'),0),) if candidate==4 else ((('Y','Z'),.37),(('X','Z'),.271 if candidate>=2 else .0),(('X','Y'),.71))
    for axes,offset in planes:
        uv=node('CombineXYZ')
        for k,axis in enumerate(axes):
            # ~250 portrait pixels per model unit: match visible facial mark scale.
            pixels=pixel_width if k==0 else pixel_height
            t=mathnode('PINGPONG',mathnode('ADD',mathnode('MULTIPLY',xyz.outputs[axis],250/pixels),offset+(.36*k if candidate>=2 else 0)),1)
            if fields is not None:t=fields.outputs[k]
            lo,hi=rect[:2] if k==0 else rect[2:]
            l.new(mathnode('ADD',mathnode('MULTIPLY',t,hi-lo),lo),uv.inputs[k])
        def image_at(coords):
            tex=node('TexImage');tex.image=im;tex.interpolation='Linear';tex.extension='EXTEND';l.new(coords,tex.inputs['Vector']);return tex.outputs['Color']
        sampled=image_at(uv.outputs[0])
        if candidate>=2:
            # Native shader neighborhood average removes broad donor illumination,
            # retaining actual angular paint marks instead of substituting noise.
            neighbors=[]
            for angle in range(0,360,45):
                a=math.radians(angle)
                radius=8 if candidate>=3 else 18
                neighbors.append(image_at(vector('ADD',uv.outputs[0],(math.cos(a)*radius/955,math.sin(a)*radius/1647,0))))
            summed=neighbors[0]
            for other in neighbors[1:]:summed=vector('ADD',summed,other)
            blur=vector('MULTIPLY',summed,(.125,.125,.125))
            detail=vector('DIVIDE',sampled,vector('MAXIMUM',blur,(.015,.015,.015)))
            if candidate>=3:
                # Retain donor paint-edge contrast after removing larger tone drift.
                detail=vector('ADD',vector('MULTIPLY',vector('SUBTRACT',detail,(1.,1.,1.)),(1.25,1.25,1.25)),(1.,1.,1.))
            sampled=vector('MULTIPLY',detail,(.68,.30,.16))
        colors.append(sampled)
    sumxy=mathnode('ADD',weights[0],weights[1]);total=mathnode('ADD',sumxy,weights[2])
    transferred=colors[0] if candidate==4 else mix(mix(colors[0],colors[1],mathnode('DIVIDE',weights[1],mathnode('MAXIMUM',sumxy,.00001))),colors[2],mathnode('DIVIDE',weights[2],mathnode('MAXIMUM',total,.00001)))
    if candidate>=5:
        # Overlapping randomly rotated planar patches: continuous at cell edges,
        # without mirrored motifs or curved noise-coordinate distortion.
        from likeness_cleanup import linear_channel
        pixels=list(im.pixels)
        samples=[pixels[4*((1646-y)*955+x):4*((1646-y)*955+x)+3] for x in range(450,514,3) for y in range(355,419,3)]
        median=[linear_channel(statistics.median(v[k] for v in samples)) for k in range(3)]
        normalization=tuple(target/max(c,.02) for target,c in zip((.68,.30,.16),median))
        planar=[]
        for plane_index,axes in enumerate((('Y','Z'),('X','Z'),('X','Y'))):
            ab=[mathnode('MULTIPLY',xyz.outputs[a],1/(.18 if candidate>=6 else .14)) for a in axes]
            cell=[mathnode('FLOOR',a) for a in ab];frac=[mathnode('FRACT',a) for a in ab]
            # Smoothstep blending avoids patch boundaries; rotation is constant per cell.
            ff=[mathnode('MINIMUM',mathnode('MAXIMUM',mathnode('DIVIDE',mathnode('SUBTRACT',a,.35),.30),0),1) for a in frac] if candidate>=6 else frac
            f=[mathnode('MULTIPLY',mathnode('MULTIPLY',a,a),mathnode('SUBTRACT',3,mathnode('MULTIPLY',2,a))) for a in ff]
            taps=[]
            for i,j in ((0,0),(1,0),(0,1),(1,1)):
                seed=mathnode('ADD',mathnode('MULTIPLY',mathnode('ADD',cell[0],i),127.1),mathnode('MULTIPLY',mathnode('ADD',cell[1],j),311.7))
                rnd=mathnode('FRACT',mathnode('MULTIPLY',mathnode('SINE',mathnode('ADD',seed,plane_index*73.)),43758.5453))
                angle=mathnode('MULTIPLY',rnd,math.tau);cs=mathnode('COSINE',angle);sn=mathnode('SINE',angle)
                dx=mathnode('SUBTRACT',frac[0],i);dy=mathnode('SUBTRACT',frac[1],j)
                rx=mathnode('SUBTRACT',mathnode('MULTIPLY',cs,dx),mathnode('MULTIPLY',sn,dy))
                ry=mathnode('ADD',mathnode('MULTIPLY',sn,dx),mathnode('MULTIPLY',cs,dy))
                uv=node('CombineXYZ')
                l.new(mathnode('ADD',mathnode('MULTIPLY',rx,22/955),482/955),uv.inputs[0])
                l.new(mathnode('ADD',mathnode('MULTIPLY',ry,22/1647),1-387/1647),uv.inputs[1])
                taps.append(image_at(uv.outputs[0]))
            planar.append(mix(mix(taps[0],taps[1],f[0]),mix(taps[2],taps[3],f[0]),f[1]))
        sample=mix(mix(planar[0],planar[1],mathnode('DIVIDE',weights[1],mathnode('MAXIMUM',sumxy,.00001))),planar[2],mathnode('DIVIDE',weights[2],mathnode('MAXIMUM',total,.00001)))
        transferred=vector('MULTIPLY',sample,normalization)
        if candidate>=6:
            base=(.68,.30,.16)
            gain=2.6 if candidate==6 else 1.7
            transferred=vector('ADD',vector('MULTIPLY',vector('SUBTRACT',transferred,base),(gain,gain,gain)),base)
        rect=(450/955,514/955,1-419/1647,1-355/1647)
    face=node('Attribute');face.attribute_name='MF_original_face_detail'
    l.new(mix(transferred,original,face.outputs['Fac']),p.inputs['Base Color'])
    # Retain source surface response first, to isolate detail transfer from relighting.
    return {'candidate':candidate,'portrait_image':im.name,'source_patch_uv':rect,
        'detail_source':'Approved portrait skin marks;05-07 use overlapping randomly rotated planar donor patches;06-07 narrow overlap and compensate contrast loss;04 noise coordinates;01-03 mirrored mapping',
        'transfer_contrast_gain':2.6 if candidate==6 else 1.7 if candidate==7 else 1.,
        'face_source':'Accepted bilateral chain before old lower-neck repairs',
        'limitations':'Donor includes painted tone; not recovered de-lit skin. Repetition and transition need visual inspection.',
        'geometry_changed':False}


def run(job):
    out=validate(job)
    import bpy
    from bust_skin_review import protected_state,material_record,render
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE),load_ui=False,use_scripts=False)
    before=protected_state();out.mkdir()
    result={'job':job,'source_sha256':SOURCE_SHA,'handler_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'anatomy_director_accepted':True,'skin_director_accepted':False}
    if job['operation']=='build':
        result['material_edit']=texture_material(job['candidate'])
        assert protected_state()==before,'Protected state changed'
        native=out/'character-upperbody.blend';bpy.ops.wm.save_as_mainfile(filepath=str(native))
        result['native_sha256']=hashlib.sha256(native.read_bytes()).hexdigest()
    else:
        folder=BASE/f'bust-detail-build-{job["candidate"]:02}';native=folder/'character-upperbody.blend'
        record=json.loads((folder/'result.json').read_text())
        if native.is_symlink() or hashlib.sha256(native.read_bytes()).hexdigest()!=record['native_sha256']:raise ValueError('Candidate changed')
        bpy.ops.wm.open_mainfile(filepath=str(native),load_ui=False,use_scripts=False);result['native_sha256']=record['native_sha256']
    result['materials']=[material_record(m) for m in bpy.data.objects['MF_continuous_head_neck'].data.materials]
    if job['operation']!='build':assert json.loads(json.dumps(result['materials']))==record['materials'],'Material recipe changed'
    result['images']=[{'name':im.name,'packed':bool(im.packed_file or im.packed_files)} for im in bpy.data.images if im.source=='FILE']
    assert all(im['packed'] for im in result['images'])
    assert protected_state()==before,'Geometry, UVs, shapes or other objects changed'
    result['protected_state']=before
    if job['operation']=='portraits':
        render_portraits(out)
    elif job['operation']!='verify':render(out,job['operation']=='emission')
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==SOURCE_SHA
    (out/'result.json').write_text(json.dumps(result,indent=2))


def render_portraits(out):
    import bpy
    from mathutils import Vector
    from matched_face_review import rotate_z
    from hijab_donor import review
    from bust_skin_review import VIEWS
    scene=bpy.context.scene
    ob=bpy.data.objects['MF_continuous_head_neck'];ob.hide_set(False)
    for o in scene.objects:
        if o.type in ('MESH','CURVE'):o.hide_render=o!=ob
    # Reuse the checked camera/light setup; retain its low-resolution setup image.
    review(scene,out,(0,-.1,-.55),4.8,(('setup',0),))
    scene.render.resolution_x=960;scene.render.resolution_y=1200;scene.cycles.samples=48
    target=Vector((0,-.1,-.55));cam=scene.camera
    lights=[o for o in scene.objects if o.type=='LIGHT' and not o.hide_render]
    assert len(lights)==2
    for label,angle in VIEWS:
        cam.location=target+Vector(rotate_z((0,-10,0),angle));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
        for light,sign in zip(lights,(-1,1)):
            light.location=target+Vector(rotate_z((sign*3,-4,3),angle));light.rotation_euler=(target-light.location).to_track_quat('-Z','Y').to_euler()
        scene.render.filepath=str(out/(label+'.png'));bpy.ops.render.render(write_still=True)


if __name__=='__main__':
    sys.path.insert(0,str(Path(__file__).resolve().parent))
    args=sys.argv[sys.argv.index('--')+1:]
    if len(args)!=1:raise ValueError('One structured job required')
    run(json.loads(Path(args[0]).read_text()))
