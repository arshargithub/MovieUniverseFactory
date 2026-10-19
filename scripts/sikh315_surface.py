"""Fixed derivative: earth microstructure, grounded litter, secondary variation."""
import json,math,shutil
import bpy
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from sikh315_scene import noise,dust
from sikh257_native import mesh
from sikh292_assets import surface

def refine(out,source):
    road=bpy.data.objects['irregular packed farm track'];s=bpy.context.scene;s.frame_set(1)
    # Keep the tested support and travel geometry. Fine relief does not replace
    # the already shaped crown, drainage cross-section or irregular mound.
    supports=json.loads((source/'terrain.json').read_text())['supports']
    moved=0
    for v in road.data.vertices:
        x,y,z=v.co
        if abs(x)>25 or not -180<y<80:continue
        w=min(1,max(0,(abs(x)-1.45)/.9))
        delta=.004*noise(x,y,11)+w*(.018*noise(x,y,8)+.009*noise(x,y,19))
        for a,b,c in supports:delta*=min(1,max(0,(math.hypot(x-a,y-b)-.20)/.35))
        v.co.z+=delta;moved+=1
    road.data.update()
    ground=BVHTree.FromPolygons([v.co.copy() for v in road.data.vertices],[list(p.vertices) for p in road.data.polygons])
    mat=road.data.materials[0];n=mat.node_tree.nodes;l=mat.node_tree.links;bs=n['Principled BSDF'];color=bs.inputs['Base Color'].links[0].from_socket
    tc=n.new('ShaderNodeTexCoord');fine=n.new('ShaderNodeTexNoise');fine.inputs['Scale'].default_value=47;fine.inputs['Detail'].default_value=4;l.new(tc.outputs['Object'],fine.inputs[0])
    ramp=n.new('ShaderNodeValToRGB');r=ramp.color_ramp;r.elements[0].position=.27;r.elements[0].color=(.36,.32,.27,1);r.elements[1].position=.73;r.elements[1].color=(1.05,1.02,.97,1);l.new(fine.outputs['Fac'],ramp.inputs[0])
    mix=n.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=.70;l.new(color,mix.inputs[1]);l.new(ramp.outputs[0],mix.inputs[2]);l.new(mix.outputs[0],bs.inputs['Base Color'])
    vor=n.new('ShaderNodeTexVoronoi');vor.feature='DISTANCE_TO_EDGE';vor.inputs['Scale'].default_value=28;l.new(tc.outputs['Object'],vor.inputs['Vector'])
    cracks=n.new('ShaderNodeMapRange');cracks.inputs['From Min'].default_value=.008;cracks.inputs['From Max'].default_value=.045;cracks.inputs['To Min'].default_value=0;cracks.inputs['To Max'].default_value=1;l.new(vor.outputs['Distance'],cracks.inputs[0])
    bumps=n.new('ShaderNodeBump');bumps.inputs['Distance'].default_value=.005;bumps.inputs['Strength'].default_value=.55;l.new(cracks.outputs[0],bumps.inputs['Height']);oldnormal=bs.inputs['Normal'].links[0].from_socket;l.new(oldnormal,bumps.inputs['Normal']);l.new(bumps.outputs[0],bs.inputs['Normal'])
    # Small embedded aggregate and crop litter on banks; large randomly
    # protruding stones are deliberately not the terrain solution.
    rng=np.random.default_rng(3155);vs=[];fs=[];indices=[]
    for i in range(24000):
        y=float(rng.uniform(-160,65));x=float(rng.uniform(-4.1,4.1))
        if i%3==0:x=float(rng.uniform(2,17));y=float(rng.uniform(-43,-16))
        if abs(x)<1.25 and rng.random()<.72:continue
        p=ground.ray_cast(Vector((x,y,10)),Vector((0,0,-1)))[0]
        if p is None:continue
        radius=float(rng.uniform(.008,.036));q=len(vs);a=float(rng.uniform(0,math.tau))
        for j in range(5):
            ang=a+j*math.tau/5;rr=radius*float(rng.uniform(.6,1.2));xx=x+rr*math.cos(ang);yy=y+rr*math.sin(ang);hit=ground.ray_cast(Vector((xx,yy,10)),Vector((0,0,-1)))[0]
            vs.append((xx,yy,(hit.z if hit else p.z)+.001))
        vs.append((x,y,p.z+radius*.18))
        for j in range(5):fs.append((q+j,q+(j+1)%5,q+5));indices.append(i%4)
    mats=[surface('315 embedded soil aggregate '+str(i),[(.10+i*.025,.081+i*.021,.055+i*.017),(.16+i*.026,.132+i*.023,.09+i*.018)],60,rough=.96,bump=.0002) for i in range(4)]
    ob=mesh('315 embedded granular soil',vs,fs,mats[0])
    for mat2 in mats[1:]:ob.data.materials.append(mat2)
    for p,idx in zip(ob.data.polygons,indices):p.material_index=idx
    vs=[];fs=[]
    for i in range(3800):
        y=float(rng.uniform(-150,65));x=float(rng.uniform(2.2,3.8))*(-1 if rng.random()<.5 else 1)
        if noise(x,y,.6)<-.1:continue
        p=ground.ray_cast(Vector((x,y,10)),Vector((0,0,-1)))[0]
        if p is None:continue
        a=float(rng.uniform(0,math.tau));length=float(rng.uniform(.025,.12));q=len(vs)
        for u,w in ((-1,-1),(-1,1),(1,1),(1,-1)):
            xx=x+u*length*.5*math.cos(a)-w*.0015*math.sin(a);yy=y+u*length*.5*math.sin(a)+w*.0015*math.cos(a);hit=ground.ray_cast(Vector((xx,yy,10)),Vector((0,0,-1)))[0];vs.append((xx,yy,(hit.z if hit else p.z)+.0025))
        fs.append((q,q+1,q+2,q+3))
    mesh('315 fallen crop litter in drainage',vs,fs,surface('315 weathered straw',[(.12,.095,.048),(.29,.23,.12)],18,rough=.96,bump=.0001))
    # Existing source materials were excessively mottled for dark woven cloth.
    for mat2 in bpy.data.materials:
        if mat2.name.startswith('315 worn indigo'):
            ramp2=next(n for n in mat2.node_tree.nodes if n.type=='VALTORGB');ramp2.color_ramp.elements[0].color=(.018,.029,.067,1);ramp2.color_ramp.elements[1].color=(.030,.047,.092,1)
    frames=sorted([o for o in bpy.data.objects if o.name.startswith('secondary facial and crown frame292')],key=lambda o:o.name)
    hairmats=[surface('315 secondary beard tone '+str(i),[(.018+i*.012,.012+i*.010,.009+i*.008),(.045+i*.018,.032+i*.015,.022+i*.013)],33,rough=.85,bump=.00025) for i in range(5)]
    for i,frame in enumerate(frames):
        for child in frame.children:
            if child.type in ('MESH','CURVE') and child.name.startswith(('secondary beard','secondary moustache','secondary brow','297 beard')):
                child.data=child.data.copy();child.data.materials.clear();child.data.materials.append(hairmats[i%5])
    for name in ('impact-events.json','launch-phases.json','coordinated-motion.json','terrain.json','debris.json','whole-horse-motion.json','supporting-cast.json','ground-finish.json'):
        if (source/name).exists():shutil.copy2(source/name,out/name)
    dust(out,json.loads((source/'coordinated-motion.json').read_text()))
    (out/'surface-refinement.json').write_text(json.dumps({'changed_ground_vertices':moved,'maximum_added_lane_relief':.004,'embedded_aggregate_faces':len(indices),'secondary_frames':len(frames),'source_surface_claim':'No direct motion or artistic pass'},indent=2))
    (out/'visible-ground-objects.json').write_text(json.dumps([{'name':o.name,'materials':[m.name for m in o.data.materials]} for o in bpy.data.objects if o.type=='MESH' and not o.hide_render and any(w in o.name.lower() for w in ('ground','road','skid','dust','occlusion','wear','lane','track'))],indent=2))
