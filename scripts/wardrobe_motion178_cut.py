"""Fixed angular cut construction for two exterior shawl courses.

No payload paths or expressions. Initial dressing only, never post-solve
projection. The cut is deliberately pre-shaped; it is not a textile pattern
certification or a claim that native physics autonomously ties a shawl.
"""
import math


def route(row, column, shoulder_gather=False, supported_major=False, compact_rear=False, diagonal_rear=False,tucked_ends=False):
    if not 0<=row<192 or not 0<=column<13:raise ValueError('Fixed cut bounds')
    u=row/191;v=(12-column)/12;theta=4*math.pi*u
    transition=max(0.,min(1.,(u-.45)/.1));course=transition**2*(3-2*transition)
    front=max(0.,-math.cos(theta));rear=max(0.,math.cos(theta));side=math.sin(theta)**6
    top=-1.55-.70*front-.32*rear+.32*math.sin(theta)*front*(1-2*course)
    top-=.28*course*front;top+=.05*course*side+.16*course*rear
    width=.90+.70*front+.15*rear
    if supported_major:
        # Narrow support crossing; broad downward chest and rear falls. Rear
        # courses lie below the nape, rather than forming a horizontal collar.
        top=-1.58-.57*front-.90*rear+.20*math.sin(theta)*front*(1-2*course)
        top-=.25*course*front;top+=.13*course*rear
        width=.50+.85*front+.75*rear
        if compact_rear:
            top+=.60*rear+.18*math.sin(theta)*rear*(1-2*course)
            width-=.55*rear
        if diagonal_rear:
            top+=.43*rear+.42*math.sin(theta)*rear*(1-2*course)+.28*course*rear
    z=top-width*v*(1-(.55 if shoulder_gather else .70)*side)
    if tucked_ends:
        end=max(0.,1-min(row,191-row)/8);end=end*end*(3-2*end)
        z=z*(1-end)+(-1.52-.16*v)*end
    return {'theta':theta,'z':z,
            'side_ease':(width*.03*math.sin(3*math.pi*v)**2*side if supported_major else
                         width*.065*math.sin(3*math.pi*v)**2*side if shoulder_gather else width*v*.80*side),
            'course':course,'front':front}


def recut(points,faces,scale,shoulder_gather=False,supported_major=False,compact_rear=False,diagonal_rear=False,tucked_ends=False,layered_ends=False):
    """Monotonic circumference and bounded whole-row contact registration.

    The earlier nearest-skin guide could double back and crowd adjacent rows.
    Here the longitudinal material coordinate remains an ordered angle. The
    actual neutral garment/head surfaces supply radial exclusion before any
    simulation; the pre-shaped cut supplies breadth and shoulder roll.
    """
    import bpy
    import numpy as np
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    from wardrobe_refinement import tree_for
    if compact_rear:
        points=[tuple(p) for p in points]
        for row in range(22,45):
            blend=((row-22)/22)**2
            for col in range(31):
                index=row*31+col;x,y,z=points[index]
                points[index]=(x,y,z+blend*((-2.10 if diagonal_rear else -2.24)-z))
    names=('MF_studio_adult_body','MF_fit_tunic_173_visible',
           'MF_171_fitted_sleeve_L_173_visible','MF_171_fitted_sleeve_R_173_visible',
           'MF_173_tension_harness_-1','MF_173_tension_harness_1',
           'MF_173_static_groom_clearance')
    trees=[tree_for(bpy.data.objects[name]) for name in names]
    trees.append(BVHTree.FromPolygons([Vector(p) for p in points[:1395]],
                                    [f for f in faces if max(f)<1395]))
    radii=np.zeros((192,13));descriptions=[]
    for row in range(192):
        descriptions.append([])
        for column in range(13):
            description=route(row,column,shoulder_gather,supported_major,compact_rear,diagonal_rear,tucked_ends);descriptions[-1].append(description)
            theta=description['theta'];direction=Vector((math.sin(theta),math.cos(theta),0))
            root=Vector((0,.14,description['z']));extent=0.
            # Explicit torso corridor excludes remote forearms as supports.
            limit=2.70 if abs(math.sin(theta))>.75 else 3.20
            for tree in trees:
                origin=root.copy();travel=0.
                for _ in range(10):
                    hit,_,_,distance=tree.ray_cast(origin,direction,limit-travel)
                    if hit is None:break
                    travel+=distance;extent=max(extent,travel)
                    origin=hit+direction*1e-5;travel+=1e-5
                    if travel>=limit:break
            if extent<=0:raise ValueError('Missing angular contact at %s/%s'%(row,column))
            margin=(.008+.008*description['course'])/scale
            if compact_rear:
                # Actual end-under-wrap layering, not exposed center-back
                # terminal strips. Retain clearance from the inner headfall.
                end=max(0.,1-min(row,191-row)/5)
                margin=((1-end)*(.008+.008*description['course'])+end*.003)/scale
                if layered_ends:
                    margin=((1-end)*(.010+.010*description['course'])+end*(.004+.003*description['course']))/scale
            relief=0.
            if supported_major:
                v=(12-column)/12
                # Unequal broad fold ridges, strongest in the drape rather
                # than the superior support. Not shader noise or global waves.
                centers=(.27+.06*math.sin(theta+.8),.66+.04*math.sin(1.5*theta))
                relief=sum(a*math.exp(-((v-c)/w)**2) for a,c,w in zip((.10,.07),centers,(.095,.12)))
                relief*=.35+.65*description['front']
            radii[row,column]=extent+margin+description['side_ease']+relief
    measured=radii.copy()
    for _ in range(3):
        fair=radii.copy();fair[1:-1]=.25*radii[:-2]+.5*radii[1:-1]+.25*radii[2:]
        radii=np.maximum(measured,fair)
    result=[tuple(p) for p in points[:1395]]
    for row in range(192):
        for column in range(13):
            d=descriptions[row][column];theta=d['theta'];radius=radii[row,column]
            result.append((math.sin(theta)*radius,.14+math.cos(theta)*radius,d['z']))
    superior=np.array(result[1395:]).reshape(192,13,3)[:,-1]
    guide=np.linalg.norm(np.diff(superior,axis=0),axis=1)*scale
    if guide.min()<.006 or guide.max()>.045:
        raise ValueError('Angular guide has crowded or discontinuous rows: %s..%s m'%(guide.min(),guide.max()))
    end_gap=float(np.min(np.linalg.norm(np.array(result[1395:1408])-np.array(result[-13:]),axis=1))*scale)
    if layered_ends and end_gap<.002:
        raise ValueError('Concealed terminals must be separate physical layers')
    pins={i:1. for i in range(6,25)}
    for row in range(192):
        # Justified supported superior front/shoulder border. Rear drape and
        # all lower width remain native cloth; concealed ends use rig tacks.
        if result[1395+row*13+12][1]<.55:pins[1395+row*13+12]=1.
    for row in (0,191):
        for column in (4,6,8):pins[1395+row*13+column]=1.
    if supported_major:
        # Explicit hybrid scope: supported major form follows chest; lower
        # free margins and lower headfall receive native cloth dynamics.
        pins={}
        for row in range(45):
            for col in range(31):
                if row<24:pins[row*31+col]=1.
                elif row<29:pins[row*31+col]=max(0.,(29-row)/5)
        for row in range(192):
            for col in range(13):
                if col>=6:pins[1395+row*13+col]=1.
                elif col>=4:pins[1395+row*13+col]=(col-3)/3
                if row<3 or row>188:pins[1395+row*13+col]=1.
        if tucked_ends:
            for row in range(45):
                for col in (0,1,2,28,29,30):
                    index=row*31+col
                    if index not in pins:continue
                    factor=.8 if col in (2,28) else .3 if col in (1,29) else 0.
                    if factor:pins[index]*=factor
                    else:pins.pop(index)
            for row in range(3,189):
                for col in range(1,13):pins[1395+row*13+col]=1. if col>=3 else .8 if col==2 else .3
    return result,pins,{'kind':'ordered_angular_pre_shaped_two_course_cut',
        'shoulder_gather':shoulder_gather,
        'supported_major_form':supported_major,
        'compact_rear_headfall':compact_rear,
        'diagonal_rear_crossing':diagonal_rear,
        'tucked_rear_ends_and_loose_front_opening_edge':tucked_ends,
        'minimum_terminal_layer_spacing_m':end_gap,
        'guide_min_edge_m':float(guide.min()),'guide_max_edge_m':float(guide.max()),
        'initial_radial_contact_source':'Actual neutral body/tunic/sleeves/harness/groom and headfall',
        'sewing_springs':False,'post_solve_projection':False,
        'rest_kind':'Pre-shaped neutral course metric, flat head cut; not automatic dressing'}
