"""Fixed isolated crown-lap control. No generated code or external asset execution."""
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import time
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'));sys.path.insert(0,str(ROOT/'src'))
from sikh270_guides import EYE,FOLDS,STATIONS,sha
BASE=ROOT/'.runtime/art-direction/series01-sikh270'
SOURCE=BASE/'candidate-13'
OUT=BASE/'candidate-17'

def validate(job):
    if not isinstance(job,dict) or set(job)!={'operation'} or job['operation'] not in {'build','reopen'}:raise ValueError('Fixed crown build/reopen only')

def smooth_guide(values,theta):
    i=next((j for j in range(len(STATIONS)-1) if theta<=STATIONS[j+1]),len(STATIONS)-2)
    def slope(j):
        if j==0 or j==len(STATIONS)-1:
            return (values[1]-values[-2])/(STATIONS[1]+math.tau-STATIONS[-2])
        return (values[j+1]-values[j-1])/(STATIONS[j+1]-STATIONS[j-1])
    width=STATIONS[i+1]-STATIONS[i];t=(theta-STATIONS[i])/width
    return (2*t**3-3*t*t+1)*values[i]+(t**3-2*t*t+t)*width*slope(i)+(-2*t**3+3*t*t)*values[i+1]+(t**3-t*t)*width*slope(i+1)

def point(theta,k,f):
    a=smooth_guide(FOLDS[k][1],theta);b=smooth_guide(FOLDS[k+1][1],theta)
    p=a+(b-a)*f
    # Rear courses slope into a return, rather than making horizontal rings.
    rear=max(0,-math.cos(theta))
    p+=.11*math.sin(theta)*rear*math.sin(math.pi*(k+f)/9)
    # A turned lap has a distinct lower edge and a supported flat middle.
    # Independent strips overlap; no broad sinusoidal inflated tubes.
    offset=.0005+.0014*math.exp(-(f/.20)**2)+.0007*math.sin(math.pi*f)**2
    r=math.cos(p)
    return ((.112*r+offset)*math.sin(theta)+.009*max(0,math.sin(p))**3,
            -.019-(.139*r+offset)*math.cos(theta),EYE+.033+.151*math.sin(p))

def packet(job):
    from movie_factory import production_knowledge as pk
    task=json.loads((ROOT/'.runtime/knowledge-pilot213/sikh270-cloth12-assemble.json').read_text())['task']
    task['id']='sikh270-crown17-'+job['operation']
    task['intent']='Isolated secured-crown lap correction; fixed face/groom/cloth. Static identity decision only; actual hand/motorcycle passage remains unqualified.'
    files=list(task['inputs'])+['scripts/sikh270_crown.py',str((SOURCE/'character.blend').relative_to(ROOT)),str((SOURCE/'build.json').relative_to(ROOT))]
    if job['operation']=='reopen':files.append(str((OUT/'character.blend').relative_to(ROOT)))
    task['inputs']={f:sha(ROOT/f) for f in files};p=pk.task_packet(ROOT,task)
    dest=ROOT/'.runtime/knowledge-pilot213'/task['id'];dest.with_suffix('.json').write_text(json.dumps(p,indent=2));dest.with_suffix('.md').write_text(pk.packet_markdown(p))
    if not p['dispatch_ready']:raise ValueError(p['blockers'])
    return p,dest

def native(job):
    import bpy
    from mathutils import Vector
    from sikh257_native import mesh,camera_at
    record=json.loads((SOURCE/'build.json').read_text())
    if bpy.app.online_access or sha(SOURCE/'character.blend')!=record['native_sha256']:raise ValueError('Source/offline mismatch')
    if job['operation']=='reopen':
        import numpy as np
        r=json.loads((OUT/'build.json').read_text())
        if sha(OUT/'character.blend')!=r['native_sha256']:raise ValueError('Native changed')
        bpy.ops.wm.open_mainfile(filepath=str(OUT/'character.blend'));scene=bpy.context.scene
        cloth=bpy.data.objects['Sikh270 own free end | embedded gravity control'];cache=np.load(BASE/'candidate-12/cloth-motion.npz')['vertices'];errors={}
        for f in (1,16,34,54,72,96):
            scene.frame_set(f);bpy.context.view_layer.update();ev=cloth.evaluated_get(bpy.context.evaluated_depsgraph_get())
            errors[str(f)]=float(np.max(np.abs(np.array([list(v.co) for v in ev.data.vertices])-cache[f-1])))
            if errors[str(f)]>1e-6:raise ValueError('Cache mismatch')
        cloth.hide_render=False;scene.frame_set(16);scene.render.filepath=str(OUT/'reopen-covered.png');bpy.ops.render.render(write_still=True)
        cloth.hide_render=True;scene.frame_set(96);scene.render.filepath=str(OUT/'reopen.png');bpy.ops.render.render(write_still=True)
        (OUT/'reopen.json').write_text(json.dumps(dict(native_sha256=sha(OUT/'character.blend'),inventory_matches=sorted(o.name for o in bpy.data.objects)==r['objects'],embedded_cloth_errors_m=errors,limits='Geometry replay; not new solver or actual acting'),indent=2));return
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE/'character.blend'));scene=bpy.context.scene
    old=bpy.data.objects['Sikh270 ordered diagonal crown guide loft'];mat=old.data.materials[0];rig=old.parent
    shader=mat.node_tree.nodes.get('Principled BSDF')
    shader.inputs['Sheen Weight'].default_value=.06
    shader.inputs['Specular IOR Level'].default_value=.10
    bpy.data.objects.remove(old,do_unlink=True)
    for k in range(9):
        vs=[];fs=[];n=256;rows=19
        for row in range(rows):
            f=-.025+1.05*row/(rows-1)
            for j in range(n):vs.append(point(-math.pi+math.tau*j/n,k,f))
        for row in range(rows-1):
            for j in range(n):
                a=row*n+j;b=row*n+(j+1)%n;fs.append((a,b,b+n,a+n))
        ob=mesh('Sikh270 supported cloth lap '+str(k),vs,fs,mat)
        ob.modifiers.new('Thin turned cotton edge','SOLIDIFY').thickness=.00065
        ob.modifiers.new('Supported lap smoothing','SUBSURF').levels=1
        world=ob.matrix_world.copy();ob.parent=rig;ob.parent_type='BONE';ob.parent_bone='head';bpy.context.view_layer.update();ob.matrix_world=world
    # One cross-crown finishing span hides the concentric polar termination.
    # Its long folds cross the head; all four boundaries return under the
    # supported winding surface. It is a dressed rest surface, not a tie sim.
    vs=[];fs=[];nr=145;nc=113;angle=.60
    for i in range(nr):
        u=-1.12+2.24*i/(nr-1)
        for j in range(nc):
            v=-.64+1.28*j/(nc-1)
            a=math.sin(u)*math.cos(v);b=math.sin(v);z=math.cos(u)*math.cos(v)
            x=a*math.cos(angle)-b*math.sin(angle);y=a*math.sin(angle)+b*math.cos(angle)
            fold=(v+.64)/1.28*7+.15*math.sin(u*2)
            fraction=fold%1
            relief=.0008+.00055*(math.exp(-(fraction/.13)**2)+math.exp(-((1-fraction)/.13)**2))
            tuck=.010*(max(0,(abs(u)-.91)/.21)**2+max(0,(abs(v)-.49)/.15)**2)
            offset=relief-tuck
            vs.append(((.112+offset)*x+.009*z**3,-.019+(.139+offset)*y,EYE+.033+(.151+offset)*z))
    for i in range(nr-1):
        for j in range(nc-1):
            a=i*nc+j;fs.append((a,a+1,a+nc+1,a+nc))
    ob=mesh('Sikh270 cross crown finishing span',vs,fs,mat)
    ob.modifiers.new('Finishing cotton edge','SOLIDIFY').thickness=.0006
    ob.modifiers.new('Finishing span smoothing','SUBSURF').levels=1
    world=ob.matrix_world.copy();ob.parent=rig;ob.parent_type='BONE';ob.parent_bone='head';bpy.context.view_layer.update();ob.matrix_world=world
    cam=scene.camera;target=Vector((0,-.025,EYE-.017));cloth=bpy.data.objects['Sikh270 own free end | embedded gravity control'];cloth.hide_render=True;scene.frame_set(96)
    for name,pos in [('crown',(1,-1,EYE+2)),('rear',(0,3,EYE+.10)),('front',(0,-3,EYE)),('three-quarter',(1.7,-3,EYE+.03)),('opposite',(-1.7,-3,EYE+.03)),('profile',(3,0,EYE))]:
        camera_at(cam,pos,target);scene.render.filepath=str(OUT/(name+'.png'));bpy.ops.render.render(write_still=True)
    cloth.hide_render=False;scene.frame_set(16)
    for name,pos in [('covered-front',(0,-3,EYE)),('covered-quarter',(1.7,-3,EYE+.03))]:
        camera_at(cam,pos,target);scene.render.filepath=str(OUT/(name+'.png'));bpy.ops.render.render(write_still=True)
    scene.frame_set(96);scene.render.filepath=str(OUT/'released-quarter.png');bpy.ops.render.render(write_still=True)
    cloth.hide_render=True;head=rig.pose.bones['head'];head.rotation_mode='XYZ';head.rotation_euler=(.20944,0,-.20944);bpy.context.view_layer.update();scene.render.filepath=str(OUT/'head-attachment.png');bpy.ops.render.render(write_still=True)
    head.rotation_euler=(0,0,0);bpy.context.view_layer.update();camera_at(cam,(0,-3,EYE),target)
    bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'character.blend'))
    (OUT/'build.json').write_text(json.dumps(dict(native_sha256=sha(OUT/'character.blend'),source_native_sha256=record['native_sha256'],objects=sorted(o.name for o in bpy.data.objects),status='INTERNAL_UNREVIEWED',limits=['Static identity candidate, not tied-cloth manufacture proof','Fixed body cloth cache; actual hand and bike NOT_RUN']),indent=2))

if __name__=='__main__':
    if '--' in sys.argv:
        args=sys.argv[sys.argv.index('--')+1:]
        if len(args)!=1:raise ValueError('One structured operation')
        job=json.loads(args[0]);validate(job);native(job)
    else:
        if len(sys.argv) not in (2,3) or (len(sys.argv)==3 and sys.argv[2]!='--prepare'):raise ValueError('operation [--prepare]')
        job={'operation':sys.argv[1]};validate(job);p,d=packet(job)
        if len(sys.argv)==3:print(d.with_suffix('.md'));sys.exit(0)
        import fcntl
        with (BASE/'worker.lock').open('a') as lock:
            fcntl.flock(lock,fcntl.LOCK_EX);OUT.mkdir(exist_ok=True);log=OUT/(job['operation']+'.log')
            if log.exists():raise ValueError('Preserve previous attempt')
            (OUT/(job['operation']+'-source.py')).write_bytes(Path(__file__).read_bytes())
            env={k:os.environ[k] for k in ('PATH','HOME','TMPDIR','LANG','LC_ALL') if k in os.environ};env['CYCLES_METAL_DISABLE_BINARY_ARCHIVES']='1';start=time.time()
            with log.open('w') as f:proc=subprocess.run(['/Applications/Blender.app/Contents/MacOS/Blender','--background','--offline-mode','--disable-autoexec','--python-exit-code','7','--python',str(Path(__file__).resolve()),'--',json.dumps(job)],env=env,stdout=f,stderr=subprocess.STDOUT)
            (OUT/(job['operation']+'-receipt.json')).write_text(json.dumps(dict(returncode=proc.returncode,seconds=time.time()-start,packet_digest=p['packet_digest'],inputs=p['task']['inputs']),indent=2))
            if proc.returncode:raise RuntimeError(str(log))
            print(OUT)
