"""Shot-scoped drainage morphology; protected running lane and occupied crossing."""
import json, math, shutil
import bpy
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from sikh315_scene import noise
from movie_factory.sikh315_motion import ease
from sikh257_native import mesh
from sikh292_assets import surface


def shape(x, y, old):
    a = abs(x)
    w = ease((a-1.65)/.45) * (1-ease((a-4.1)/.65))
    # The crowd steps across this occupied, protected farm access, not a trench.
    w *= ease((abs(y+18)-7)/5)
    if 1.6 < x < 24 and -46 < y < -12 and old > .18:
        w = 0
    side = 7 if x < 0 else 19
    center = 2.9 + .25*noise(side,y,.14) + .12*noise(side,y,.63)
    width = (.70 if a<center else .95) + .15*noise(side+2,y,.21)
    depth = .26 + .10*noise(side+4,y,.18)
    d = (a-center)/width
    bed = -depth*math.exp(-d*d*1.4)
    shoulder = .10*math.exp(-((a-center-.9)/.34)**2)*(1+.7*noise(x,y,.8))
    crumble = (.025*noise(x,y,3)+.013*noise(x,y,8))*math.exp(-d*d*.6)
    new = .045*noise(x,y,.45)+bed+shoulder+crumble
    return old+(new-old)*w, center, w


def refine(out, source):
    for p in source.glob('*.json'):
        if p.name not in ('job.json','bindings.json'):shutil.copy2(p,out/p.name)
    road=bpy.data.objects['irregular packed farm track']
    old=BVHTree.FromPolygons([v.co.copy() for v in road.data.vertices],[list(p.vertices) for p in road.data.polygons])
    changed=0;maxlane=0
    sediment=road.data.color_attributes['315 sediment']
    for v,c in zip(road.data.vertices,sediment.data):
        x,y,z=v.co
        nz,center,w=shape(x,y,z)
        if abs(x)<=1.65:maxlane=max(maxlane,abs(nz-z))
        if w:
            v.co.z=nz;changed+=1
            wet=math.exp(-((abs(x)-center)/.34)**2)*(.4+.3*noise(x,y,.5))
            shade=1-.48*wet;c.color=(shade,shade*.97,shade*.90,1)
    assert maxlane==0
    road.data.update()
    new=BVHTree.FromPolygons([v.co.copy() for v in road.data.vertices],[list(p.vertices) for p in road.data.polygons])
    # Reground existing natural detail; no actor, camera, wheel or FX reauthoring.
    prefixes=('304 rooted ditch','305 settled ditch','314 clustered drainage vegetation',
              '304 intermittent silt','315 collapsed clay bank clods',
              '315 embedded granular soil','315 fallen crop litter')
    for ob in list(bpy.data.objects):
        if ob.type!='MESH' or not ob.name.startswith(prefixes):continue
        inv=ob.matrix_world.inverted()
        for v in ob.data.vertices:
            p=ob.matrix_world@v.co
            if not 1.65<abs(p.x)<4.75:continue
            hit=old.ray_cast(Vector((p.x,p.y,9)),Vector((0,0,-1)))[0]
            if hit:
                nz,_,w=shape(p.x,p.y,hit.z)
                if w:p.z+=nz-hit.z;v.co=inv@p
        ob.data.update()
    # Extend buried pole ends without moving lights/baskets or introducing floats.
    poles=0
    for ob in bpy.data.objects:
        if not ob.name.startswith('297 torch planted pole'):continue
        x,y=ob.location.x,ob.location.y
        hit=new.ray_cast(Vector((x,y,9)),Vector((0,0,-1)))[0]
        if hit is None:continue
        top=ob.location.z+ob.scale.z;bottom=min(ob.location.z-ob.scale.z,hit.z-.10)
        ob.location.z=(top+bottom)/2;ob.scale.z=(top-bottom)/2;poles+=1
    # Break the bare machined edge with rooted patches, not a continuous green strip.
    rng=np.random.default_rng(31510);vs=[];fs=[];mi=[]
    for i in range(1800):
        side=-1 if i%2 else 1;y=float(rng.uniform(-180,80))
        if -30<y<-6 or noise(side*11,y,.22)<.04:continue
        center=shape(side*3,y,0)[1]
        x=side*(center+float(rng.choice([-.62,.67]))+float(rng.uniform(-.16,.16)))
        hit=new.ray_cast(Vector((x,y,9)),Vector((0,0,-1)))[0]
        if hit is None or hit.z>.22:continue
        for j in range(int(rng.integers(10,22))):
            a=float(rng.uniform(0,math.tau));r=float(rng.uniform(0,.13))
            xx=x+r*math.cos(a);yy=y+r*math.sin(a)
            p=new.ray_cast(Vector((xx,yy,9)),Vector((0,0,-1)))[0]
            if p is None:continue
            h=float(rng.uniform(.045,.18));width=float(rng.uniform(.003,.008))
            bend=Vector((math.cos(a)*h*.6,math.sin(a)*h*.6,0));q=len(vs)
            cross=Vector((-math.sin(a)*width,math.cos(a)*width,0))
            mid=p+Vector((0,0,h*.6))+bend*.3;tip=p+Vector((0,0,h))+bend
            vs.extend([tuple(p-cross),tuple(p+cross),tuple(mid+cross*.6),tuple(mid-cross*.6),tuple(tip)])
            fs.extend([(q,q+1,q+2,q+3),(q+3,q+2,q+4)]);mi.extend([i%3,i%3])
    mats=[surface('315 drainage tuft '+str(i),[a,b],21,rough=.96,bump=.00015) for i,(a,b) in enumerate([
        ((.045,.055,.018),(.12,.13,.038)),((.10,.085,.028),(.22,.19,.075)),((.045,.033,.015),(.14,.10,.034))])]
    ob=mesh('315 rooted broken drainage tussocks',vs,fs,mats[0])
    for mat in mats[1:]:ob.data.materials.append(mat)
    for p,index in zip(ob.data.polygons,mi):p.material_index=index
    bs=road.data.materials[0].node_tree.nodes['Principled BSDF']
    if bs.inputs['Normal'].links:
        bump=bs.inputs['Normal'].links[0].from_node
        if bump.type=='BUMP':bump.inputs['Strength'].default_value=.13
    (out/'drainage-morphology.json').write_text(json.dumps({
        'reason':'Full opening chronology still showed bare uniform trench and overly legible crack mosaic; reject before complete export',
        'reference':'J. Carl Ganter / Circle of Blue Punjab Parchh irrigation photograph; observation only, no pixels used in production',
        'changed_vertices':changed,'protected_lane_delta':maxlane,'grounded_tuft_faces':len(fs),
        'pole_bases_checked':poles,'preserved':'Bike running lane, occupied crossing, horse supports, all motion/camera/audio',
        'limits':'Small rooted verge detail is static; existing field wind retained. No new realism or production acceptance claim.'},indent=2))
