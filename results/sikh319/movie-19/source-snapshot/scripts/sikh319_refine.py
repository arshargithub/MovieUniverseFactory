"""Local beard fall correction on the verified319 cast derivative."""
import math
import bpy
from mathutils import Vector
from sikh319_cast import strands, hide

def refine():
    bpy.context.scene.frame_set(283)
    roots=[bpy.data.objects['mounted leader']]+sorted(
        [o for o in bpy.data.objects if o.name.startswith('FOOT WARRIOR ')],key=lambda o:o.name)
    report=[]
    for index,root in enumerate(roots):
        frame=next(o for o in root.children if o.name.startswith('secondary facial and crown frame292'))
        old=[o for o in frame.children if o.name.startswith('319 tapered beard fibers')]
        assert len(old)==3
        actions=[o.animation_data.action if o.animation_data else None for o in old]
        for o in list(frame.children):
            if o.name.startswith(('319 tapered beard fibers','319 moustache overlapping lip',
                                  '319 rooted sideburns','319 refined')):hide(o)
        mats=[bpy.data.materials[n+str(index)] for n in ('319 beard dark ','319 beard mid ','319 beard light ')]
        # Preserve16's coherent lock design and root placement. The attempted
        # projection/Bezier rebuilds changed its whole mass and are rejected.
        # Correct only excess forward throw, smoothly and with fixed roots.
        for k,original in enumerate(old):
            paths=[]
            for number,sp in enumerate(original.data.splines):
                if number%2:continue
                pts=[]
                for j,p in enumerate(sp.points):
                    q=Vector(p.co[:3]);t=j/(len(sp.points)-1)
                    q.y+=.042*math.sin(t*math.pi*.55)
                    pts.append(tuple(q))
                paths.append(pts)
            ob=strands('319 refined skin-rooted beard',paths,
                       original.data.bevel_depth*1.25,mats[k],frame)
            if actions[k]:
                ob.animation_data_create();ob.animation_data.action=actions[k]
                ob.animation_data.action_slot=original.animation_data.action_slot
        for original in list(frame.children):
            if original.name.startswith(('319 moustache overlapping lip','319 rooted sideburns')):
                original.hide_render=False;original.hide_viewport=False
        report.append({'actor':root.name,'change':'preserve16 locks, fixed roots, reduce forward throw smoothly by up to42mm',
                       'old_action_reused':all(a is not None for a in actions),
                       'body_animation_controls_unchanged':True,
                       'beard_density':'every second original guide, radius1.25; shot-tier proof required'})
    bpy.context.scene.frame_set(283)
    return report
