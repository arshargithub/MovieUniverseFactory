"""Fixed free-headfall construction screen for authorized cloth rescue.

The headfall has a free lower hem. An exterior draped course overlaps it;
there is no full-width bottom seam that closes it into a rear pouch.
"""
import math


def smooth(x):
    x=max(0.,min(1.,x)); return x*x*(3-2*x)


def head_point(u,v):
    sections=((0.,-.08,1.17,1.28,1.25),(.22,.50,1.26,1.34,1.27),
              (.45,1.18,.45,1.36,1.10),(.70,1.32,-1.55,1.38,.25),
              (1.,1.10,-3.55,1.25,-.10))
    k=next((k for k in range(4) if u<=sections[k+1][0]),3)
    a,b=sections[k:k+2];t=smooth((u-a[0])/(b[0]-a[0]))
    y,z,width,drop=[a[i]*(1-t)+b[i]*t for i in range(1,5)]
    angle=(2*v-1)*math.pi/2; lateral=smooth((u-.32)/.40)
    y=y*(1-lateral*math.sin(angle)**2)+.05*lateral*math.sin(angle)**2
    # Uneven longitudinal slack, fading to the crown support. It supplies
    # a dressed rest shape for physics, not animated wind or painted folds.
    slack=.045*smooth((u-.25)/.30)*(math.sin(v*19+.7*u)+.35*math.sin(v*31-2*u))
    return (width*math.sin(angle), y+.10*math.sin(angle)**2+slack,
            z-drop*(1-math.cos(angle))+.06*math.sin(2.8*angle)*smooth((u-.6)/.4))


def construction(profile=1):
    import bpy
    import numpy as np
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    from wardrobe_refinement import tree_for
    import wardrobe_motion178 as foundation
    rows,cols=33,25
    hood,hf=foundation.sheet_grid(rows,cols,head_point)
    if profile==2:
        for i in range(rows):
            u=i/(rows-1)
            for j in range(cols):
                k=i*cols+j;x,y,z=hood[k];side=abs(2*j/(cols-1)-1)
                edge=(1-smooth(u/.25))*side**3
                hood[k]=(x,y-.35*edge,z-.60*edge)
    groom=tree_for(bpy.data.objects['MF_173_static_groom_clearance'])
    # Pre-dressing clearance against the actual retained groom.
    origin=Vector((0,.25,-.2))
    for i,point in enumerate(hood):
        p=Vector(point);direction=(p-origin).normalized();extent=(p-origin).length
        start=origin.copy();travel=0.
        for _ in range(16):
            hit,_,_,distance=groom.ray_cast(start,direction,6-travel)
            if hit is None:break
            travel+=distance;extent=max(extent,travel+.035)
            travel+=1e-5;start=hit+direction*1e-5
        hood[i]=tuple(origin+direction*extent)
    if profile==2:
        # Below support, gravity drape spans concavities; it does not shrink
        # back towards the nape and create a bag under the hair volume.
        for j in range(cols):
            maximum=-10.
            for i in range(10,rows):
                k=i*cols+j;x,y,z=hood[k]
                maximum=max(maximum,y)
                hood[k]=(x,maximum,z)
    hood_tree=BVHTree.FromPolygons([Vector(p) for p in hood],hf)
    trees=[tree_for(bpy.data.objects[n]) for n in (
        'MF_studio_adult_body','MF_fit_tunic_173_visible',
        'MF_171_fitted_sleeve_L_173_visible','MF_171_fitted_sleeve_R_173_visible',
        'MF_173_tension_harness_-1','MF_173_tension_harness_1')]+[groom,hood_tree]
    r,c=81,17
    wrap=[]
    for i in range(r):
        u=i/(r-1); theta=-.32+(2*math.pi+.64)*u
        front=max(0.,-math.cos(theta));back=max(0.,math.cos(theta))
        top=-1.78-.67*front-.58*back+.32*math.sin(theta)*front
        width=.60+.51*front+.14*back
        # Rear tails overlap at different heights; no exposed hard shoulder end.
        top-=.20*smooth((u-.84)/.16)
        for j in range(c):
            v=j/(c-1);z=top-width*v
            direction=Vector((math.sin(theta),math.cos(theta),0))
            origin=Vector((0,.14,z));extent=0.
            for tree in trees:
                start=origin.copy();travel=0.
                for _ in range(16):
                    hit,_,_,distance=tree.ray_cast(start,direction,4.-travel)
                    if hit is None:break
                    travel+=distance;extent=max(extent,travel)
                    travel+=1e-5;start=hit+direction*1e-5
            if extent<=0:raise ValueError('Missing actual drape support')
            # Fold depth follows the hanging course and fades at the shoulders.
            fold=(.065+.04*front)*math.sin(math.pi*v)*(.55+.45*math.sin(5.5*math.pi*v+theta*.5))
            radius=extent+(.12 if profile==2 else .055)+fold+.055*smooth((u-.88)/.12)
            wrap.append(tuple(origin+direction*radius))
    if profile==2:
        # Drape spans narrow leather/tunic recesses. Keep the smoothed
        # support envelope outside every original sampled contact.
        grid=np.array(wrap).reshape(r,c,3)
        radius=np.linalg.norm(grid[:,:,:2]-np.array([0,.14]),axis=2)
        for _ in range(3):
            padded=np.pad(radius,((1,1),(1,1)),mode='edge')
            average=(padded[:-2,1:-1]+padded[2:,1:-1]+padded[1:-1,:-2]+padded[1:-1,2:])/4
            radius=np.maximum(radius,average)
        for i in range(r):
            theta=-.32+(2*math.pi+.64)*i/(r-1)
            grid[i,:,0]=math.sin(theta)*radius[i]
            grid[i,:,1]=.14+math.cos(theta)*radius[i]
        wrap=grid.reshape(-1,3).tolist()
    _,wf=foundation.sheet_grid(r,c,lambda u,v:(0,0,0))
    offset=len(hood);faces=hf+[tuple(offset+k for k in f) for f in wf]
    p=np.array(hood+wrap)
    # Crown attachment and real shoulder support only. Lower rear curtain is free.
    pins={}
    for i in range(3,10):
        for j in range(9,16):
            idx=i*cols+j;h,n,_,d=groom.find_nearest(Vector(p[idx]))
            if h is not None and d<.10 and n.z>.25:pins[idx]=1.
    for i in range(r):
        theta=-.32+(2*math.pi+.64)*i/(r-1)
        if abs(math.sin(theta))>.99:
            for j in range(4):pins[offset+i*c+j]=1. if j<2 else .5
    return p,np.array(faces),pins,{'hood_vertices':offset,'wrap_vertices':len(wrap),'free_rear_hem':True,
        'logical_construction':'Free headfall and overlapping outer shoulder course; attachment development pending',
        'vertices':len(p),'profile':profile,'crown_pins':sum(i<offset for i in pins),'support_pins':len(pins)}
