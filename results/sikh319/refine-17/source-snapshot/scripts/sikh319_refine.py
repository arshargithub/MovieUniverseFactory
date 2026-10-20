"""Local hair attachment/fall correction on the verified319 cast derivative."""
import math
import random
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from sikh319_cast import anatomical_head, strands, hide

def refine():
    bpy.context.scene.frame_set(283)
    mesh=anatomical_head()
    surface=BVHTree.FromPolygons([v.co for v in mesh.vertices],[tuple(p.vertices) for p in mesh.polygons])
    roots=[bpy.data.objects['mounted leader']]+sorted(
        [o for o in bpy.data.objects if o.name.startswith('FOOT WARRIOR ')],key=lambda o:o.name)
    report=[]
    for index,root in enumerate(roots):
        leader=index==0
        frame=next(o for o in root.children if o.name.startswith('secondary facial and crown frame292'))
        old=[o for o in frame.children if o.name.startswith('319 tapered beard fibers')]
        assert len(old)==3
        # Retain the previous bounded follow action and root-near pivot.
        actions=[o.animation_data.action if o.animation_data else None for o in old]
        for o in list(frame.children):
            if o.name.startswith(('319 tapered beard fibers','319 moustache overlapping lip','319 rooted sideburns')):hide(o)
        mats=[bpy.data.materials[n+str(index)] for n in ('319 beard dark ','319 beard mid ','319 beard light ')]
        rng=random.Random(319170+index);buckets=[[],[],[]]
        length=.18 if leader else .12+.018*(index%4)
        # Allocate density to the actual supporting-shot scale, not a principal
        # close-up. This remains a visible comparison, not a count-based pass.
        for i in range(3000 if leader else 900):
            a=rng.uniform(-1.43,1.43);side=abs(math.sin(a))
            root_z=-.055+.065*side;phase=round(a*8)*.77+rng.uniform(-.35,.35)
            end=rng.uniform(.80,1.08);start=rng.uniform(0,.025)
            anchor_x=.073*math.sin(a)
            anchor=surface.ray_cast(Vector((anchor_x,-.4,-.072)),Vector((0,1,0)))[0]
            jaw_y=anchor.y if anchor else -.13
            pts=[]
            for j in range(18):
                t=start+(end-start)*j/17
                z=root_z-length*t
                x=.073*math.sin(a)*(1-.30*t)
                x+=.004*math.sin(t*8+phase)*math.sin(math.pi*min(1,t))
                y=jaw_y-.004-.018*math.sin(t*math.pi*.5)
                hit=surface.ray_cast(Vector((x,-.4,z)),Vector((0,1,0)))[0] if z>-.10 else None
                if hit:
                    w=max(0,min(1,(z+.10)/.03));w=w*w*(3-2*w)
                    y=y*(1-w)+(hit.y-.0025)*w
                y-=rng.uniform(.0002,.0015)
                y+=.003*math.sin(t*10+phase)*math.sin(math.pi*min(1,t))
                pts.append((x,y,z))
            bucket=2 if rng.random()<(0.24 if leader else .045*(index%3)) else i%2
            buckets[bucket].append(pts)
        for k,paths in enumerate(buckets):
            ob=strands('319 refined skin-rooted beard',paths,.0006 if leader else .00085,mats[k],frame)
            if actions[k]:
                ob.animation_data_create();ob.animation_data.action=actions[k]
                ob.animation_data.action_slot=old[k].animation_data.action_slot
        paths=[]
        for side in (-1,1):
            for i in range(500):
                z0=rng.uniform(-.009,.006);phase=rng.uniform(0,math.tau)
                end=rng.uniform(.76,1.12);pts=[]
                for j in range(12):
                    t=end*j/11;x=side*(rng.uniform(.0005,.002)+.059*t)
                    z=-.026+z0-.036*t*t+.0015*math.sin(t*8+phase)
                    hit=surface.ray_cast(Vector((x,-.4,z)),Vector((0,1,0)))[0]
                    y=(hit.y-.003 if hit else -.158)+.0015*math.sin(t*5+phase)
                    pts.append((x,y,z))
                paths.append(pts)
        strands('319 refined surface moustache',paths,.00065,mats[1],frame)
        paths=[]
        for side in (-1,1):
            for i in range(150):
                yy=rng.uniform(-.071,-.045);zz=rng.uniform(.025,.068)
                length0=rng.uniform(.014,.037);pts=[]
                for k in range(6):
                    t=k/5;y=yy-.009*t;z=zz-length0*t
                    hit=surface.ray_cast(Vector((side*.25,y,z)),Vector((-side,0,0)))[0]
                    if hit:pts.append((hit.x+side*.0008,y,z))
                if len(pts)>1:paths.append(pts)
        strands('319 refined feathered sideburns',paths,.0005,mats[0],frame)
        report.append({'actor':root.name,'change':'skin-following cheek to jaw, gravity fall, attached moustache, feathered sideburns',
                       'old_action_reused':all(a is not None for a in actions),
                       'geometry_animation_controls_unchanged':True})
    bpy.context.scene.frame_set(283)
    return report
