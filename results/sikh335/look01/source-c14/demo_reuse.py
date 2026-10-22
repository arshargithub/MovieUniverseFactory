"""Bounded camera-only reuse of the hash-admitted Courier world."""
from pathlib import Path
import hashlib
import json
import math
import shutil
import time

ROOT = Path(__file__).resolve().parents[4]
BASE = ROOT/'runs/demonstrator-01/cut-world-v4/scene.blend'
BASE_SHA = '7248f9dfecef3e9ece309c08055ab53ee6d802abe0a0e01307c7f9d8b93fd73e'
OUTPUT = ROOT/'runs/demonstrator-01/reuse-01'

def sha(path):
    with Path(path).open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()

def validate(job):
    if not isinstance(job, dict) or set(job) != {'mode','output_dir','profile'}:
        raise ValueError('Invalid job keys')
    if job['mode'] != 'demo_reuse': raise ValueError('Invalid mode')
    out = Path(job['output_dir']).resolve()
    if out.parent != OUTPUT.resolve() or out.name not in {'smoke','smoke-retry','smoke-diagnostic','smoke-fixed','smoke-timing','shot','revision','replay'}:
        raise ValueError('Unapproved output path')
    p = job['profile']
    keys = {'source_sha256','start','duration_frames','offset_start','offset_end','target_offset','lens_mm','operation'}
    if not isinstance(p,dict) or not keys.issubset(p) or set(p)-keys-{'camera_path','path_interpolation'}: raise ValueError('Invalid profile keys')
    if p.get('path_interpolation','smoothstep') not in {'smoothstep','continuous'}:raise ValueError('Invalid path interpolation')
    if p['source_sha256'] != BASE_SHA: raise ValueError('Unadmitted source')
    if type(p['start']) is not int or type(p['duration_frames']) is not int:
        raise ValueError('Integer timeline required')
    if not 72 <= p['duration_frames'] <= 120 or not 0 <= p['start'] <= 576-p['duration_frames']:
        raise ValueError('Only 3–5 seconds within existing timeline')
    if p['operation'] not in {'smoke','clip','replay'}: raise ValueError('Invalid operation')
    def number(x,lo,hi):return type(x) in (float,int) and math.isfinite(x) and lo <= x <= hi
    for key in ('offset_start','offset_end','target_offset'):
        v=p[key]
        if not isinstance(v,list) or len(v)!=3:raise ValueError('Three coordinates required')
        bounds = [(-3,3),(-6,6),(-2,3)] if key=='target_offset' else [(-25,25),(-30,30),(0,20)]
        if not all(number(x,*b) for x,b in zip(v,bounds)):raise ValueError('Camera coordinates outside bounds')
    if not number(p['lens_mm'],24,70):raise ValueError('Lens outside 24–70mm')
    path=p.get('camera_path',[{'at':0,'offset':p['offset_start']},{'at':1,'offset':p['offset_end']}])
    if not isinstance(path,list) or not 2<=len(path)<=6:raise ValueError('Camera path needs2–6 knots')
    previous=-1
    for knot in path:
        if not isinstance(knot,dict) or set(knot)!={'at','offset'}:raise ValueError('Invalid camera knot')
        if not number(knot['at'],0,1) or knot['at']<=previous:raise ValueError('Strictly increasing camera times required')
        previous=knot['at'];v=knot['offset']
        if not isinstance(v,list) or len(v)!=3 or not all(number(x,*b) for x,b in zip(v,[(-25,25),(-30,30),(0,20)])):
            raise ValueError('Camera knot outside bounded coordinates')
    if path[0]['at']!=0 or path[-1]['at']!=1:raise ValueError('Camera path must span entire shot')
    if path[0]['offset']!=p['offset_start'] or path[-1]['offset']!=p['offset_end']:raise ValueError('Endpoint mismatch')
    # Exact minimum along each line segment; smoothstep traverses the same segment.
    for a,b in zip(path,path[1:]):
        d=[a['offset'][j]-p['target_offset'][j] for j in range(3)]
        v=[b['offset'][j]-a['offset'][j] for j in range(3)]
        den=sum(x*x for x in v)
        u=max(0,min(1,-sum(x*y for x,y in zip(d,v))/den)) if den else 0
        if sum((x+u*y)**2 for x,y in zip(d,v))<9:raise ValueError('Camera must stay at least3m from aim point')
    if p.get('path_interpolation')=='continuous':
        # Coordinate-wise monotone Hermite stays within endpoint bounds. Reject if
        # the conservative segment box can approach the target within3m.
        for a,b in zip(path,path[1:]):
            gap=[max(min(x,y)-q,0,q-max(x,y)) for x,y,q in zip(a['offset'],b['offset'],p['target_offset'])]
            if sum(x*x for x in gap)<9:raise ValueError('Continuous path clearance is not conservatively established')
    return out,p

def camera_offset(p,t):
    """Piecewise C1 relative travel; repeated offsets produce explicit holds."""
    path=p.get('camera_path',[{'at':0,'offset':p['offset_start']},{'at':1,'offset':p['offset_end']}])
    if p.get('path_interpolation')=='continuous':
        h=[b['at']-a['at'] for a,b in zip(path,path[1:])]
        slopes=[]
        for axis in range(3):
            d=[(b['offset'][axis]-a['offset'][axis])/dt for a,b,dt in zip(path,path[1:],h)]
            m=[0.0]
            for i in range(1,len(path)-1):
                if d[i-1]*d[i]<=0:m.append(0.0)
                else:
                    w1=2*h[i]+h[i-1];w2=h[i]+2*h[i-1]
                    m.append((w1+w2)/(w1/d[i-1]+w2/d[i]))
            m.append(0.0);slopes.append(m)
        for i,(a,b) in enumerate(zip(path,path[1:])):
            if t<=b['at']:
                u=max(0,min(1,(t-a['at'])/h[i]));u2=u*u;u3=u2*u
                return [(2*u3-3*u2+1)*a['offset'][j]+(u3-2*u2+u)*h[i]*slopes[j][i]+(-2*u3+3*u2)*b['offset'][j]+(u3-u2)*h[i]*slopes[j][i+1] for j in range(3)]
        return list(path[-1]['offset'])
    for a,b in zip(path,path[1:]):
        if t<=b['at']:
            u=max(0,min(1,(t-a['at'])/(b['at']-a['at'])));u=u*u*(3-2*u)
            return [x+(y-x)*u for x,y in zip(a['offset'],b['offset'])]
    return list(path[-1]['offset'])

def stable_property(value):
    if value is None or isinstance(value,(str,int,float,bool)):return value
    if hasattr(value,'to_dict'):return stable_property(value.to_dict())
    if hasattr(value,'to_list'):return stable_property(value.to_list())
    if isinstance(value,dict):return tuple((k,stable_property(v)) for k,v in sorted(value.items()))
    if isinstance(value,(list,tuple)):return tuple(stable_property(v) for v in value)
    if hasattr(value,'name'):return (type(value).__name__,value.name)
    raise TypeError('Unsupported property type: '+type(value).__name__)

def run(mf,out,job,helper):
    output,p=validate(job)
    if Path(out).resolve()!=output:raise ValueError('Output mismatch')
    import bpy
    from mathutils import Vector
    if sha(BASE)!=BASE_SHA:raise ValueError('Baseline hash mismatch')
    if (output/'scene.blend').exists():raise ValueError('Never overwrite scene')
    bpy.ops.wm.open_mainfile(filepath=str(BASE),load_ui=False,use_scripts=False)
    scene=bpy.context.scene
    def protected():
        # All original animation channels, mesh coordinates/topology, identities/bindings.
        h=hashlib.sha256()
        parts=[]
        def add(v):
            encoded=repr(v);h.update(encoded.encode());parts.append(hashlib.sha256(encoded.encode()).hexdigest())
        # Keep mismatch evidence so serialization changes are distinguishable from mutations.
        for o in sorted(scene.objects,key=lambda o:o.name):
            if o.type=='CAMERA':continue
            add((o.name,o.type,o.data.name if o.data else None,o.parent.name if o.parent else None,
                 tuple(o.matrix_basis),o.hide_render,[(k,stable_property(v)) for k,v in sorted(o.items())],
                 o.animation_data.action.name if o.animation_data and o.animation_data.action else None))
            if o.type=='MESH':
                add([tuple(v.co) for v in o.data.vertices]);add([tuple(f.vertices) for f in o.data.polygons])
        for a in sorted(bpy.data.actions,key=lambda a:a.name):
            if a.name.startswith('ReuseCamera'):continue
            add(a.name)
            for layer in a.layers:
                for strip in layer.strips:
                    for bag in strip.channelbags:
                        for fc in bag.fcurves:
                            add((fc.data_path,fc.array_index,[(tuple(k.co),tuple(k.handle_left),tuple(k.handle_right),k.interpolation) for k in fc.keyframe_points]))
        (output/f'protected-{len(list(output.glob("protected-*.json")))}.json').write_text(json.dumps(parts,indent=2)+'\n')
        return h.hexdigest()
    helper._refresh(scene,mf,0)
    before=protected()
    horse=bpy.data.objects['horse.rig']
    origin=horse.matrix_world@horse.pose.bones['torso'].head+Vector((0,0,.6))
    data=bpy.data.cameras.new('ReuseCamera');data.lens=p['lens_mm'];data.clip_end=1200
    cam=bpy.data.objects.new('ReuseCamera',data);scene.collection.objects.link(cam)
    cam.rotation_mode='QUATERNION';previous=None
    start=p['start'];end=start+p['duration_frames']
    for frame in range(start,end):
        t=(frame-start)/(p['duration_frames']-1)
        body=origin+Vector((0,-12*frame/24,0))
        cam.location=body+Vector(camera_offset(p,t))
        q=(body+Vector(p['target_offset'])-cam.location).to_track_quat('-Z','Y')
        if previous is not None and q.dot(previous)<0:q.negate()
        cam.rotation_quaternion=q;previous=q.copy()
        cam.keyframe_insert('location',frame=frame);cam.keyframe_insert('rotation_quaternion',frame=frame)
    cam.animation_data.action.name='ReuseCameraAction'
    for layer in cam.animation_data.action.layers:
        for strip in layer.strips:
            for bag in strip.channelbags:
                for fc in bag.fcurves:
                    for k in fc.keyframe_points:k.interpolation='LINEAR'
    for marker in scene.timeline_markers:marker.camera=None
    scene.camera=cam;scene.frame_start=start;scene.frame_end=end-1
    scene.render.engine='BLENDER_EEVEE'
    scene.eevee.taa_render_samples=16
    scene.render.resolution_x=640;scene.render.resolution_y=360;scene.render.resolution_percentage=100
    scene.render.fps=24;scene.render.fps_base=1;scene.render.image_settings.file_format='PNG'
    helper._refresh(scene,mf,0)
    after=protected()
    if before!=after:raise RuntimeError('Protected state changed')
    scene.render.film_transparent=False
    bpy.ops.wm.save_as_mainfile(filepath=str(output/'scene.blend'),compress=True)
    frames=range(start,start+3) if p['operation']=='smoke' else ([start+p['duration_frames']//2] if p['operation']=='replay' else range(start,end))
    if p['operation']=='clip':
        # Early camera-extreme coverage; reuse these frames in the final sequence.
        probes=list(dict.fromkeys([start,start+int(.35*(end-start-1)),start+int(.52*(end-start-1)),end-1]))
        frames=probes+[f for f in frames if f not in probes]
    # Always reopen saved derived scene before rendering, also checking protected binding.
    bpy.ops.wm.open_mainfile(filepath=str(output/'scene.blend'),load_ui=False,use_scripts=False)
    scene=bpy.context.scene;helper._refresh(scene,mf,0)
    if protected()!=before:raise RuntimeError('Protected state changed on reopen')
    records=[]
    for frame in frames:
        if shutil.disk_usage(ROOT).free<5*1024**3:raise RuntimeError('5 GiB reserve reached')
        helper._refresh(scene,mf,frame);scene.camera=bpy.data.objects['ReuseCamera']
        scene.render.filepath=str(output/f'frame_{frame:04d}.png')
        t=time.monotonic();bpy.ops.render.render(write_still=True)
        records.append({'frame':frame,'seconds':time.monotonic()-t})
        (output/'frames.json').write_text(json.dumps(records,indent=2)+'\n')
    (output/'reuse.json').write_text(json.dumps({'profile':p,'source_sha256':BASE_SHA,'scene_sha256':sha(output/'scene.blend'),'protected_before':before,'protected_after':after,'protected_reopen':True,'frames':records,'limitations':'Structured identity, mesh and animation fingerprint; not exhaustive evaluated collision/material equivalence'},indent=2)+'\n')
    return ['scene.blend','reuse.json','frames.json']
