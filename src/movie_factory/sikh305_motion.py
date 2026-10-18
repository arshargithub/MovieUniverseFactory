"""Explicit source clock and response curves for the Director305 correction."""
import math
from movie_factory import sikh304_motion as old
from movie_factory.sikh291_motion import FPS, RATE, ease

FRAMES = 696
old_travel = old.old_travel
ground_height = old.ground_height
bump = old.bump
lean = old.lean

def travel(t):
    if t <= 21.4:
        return old.travel(t)
    u = t - 21.4
    # Smooth low-traction onset, then sustained acceleration. Integral of a
    # smoothstep acceleration ramp, not an arbitrary positional overshoot.
    w = max(0., (u - .20) / .70)
    integral = (.70**2 * (w**4/4-w**5/10) if w < 1 else
                .70**2 * (.15 + .5*(w-1) + .5*(w-1)**2))
    if u < 4.8:
        return old.travel(21.4) - (9.85/1.5)*u - .12*u*u - 3.2*integral
    v = 9.85/1.5 + .24*4.8 + 3.2*(4.8-.55)
    return travel(26.2-1e-8) - v*(u-4.8)

def yaw(t):
    if t < 21.4:
        return old.yaw(t)
    return -.15*bump(t,21.4,21.84,22.0,22.72)

def lateral(t):
    return .34*bump(t,21.4,21.95,22.08,22.85)

def slip(t):
    return 5.55<=t<6.15 or 6.70<=t<7.50 or 21.4<=t<22.22

def rear_distance(t):
    d=travel(t)-travel(0)
    for a,b in ((5.55,6.15),(6.70,7.50)):
        if t>a:d-=travel(min(t,b))-travel(a)
    return d-3.2*ease((t-21.4)/.82)

def rear(t):
    # Fast weight transfer and rise, short living apex, controlled return.
    return bump(t,14.86,15.30,15.48,16.02)

def gather(t):
    return bump(t,14.25,14.65,14.83,15.10)

def landing(t):
    return bump(t,15.94,16.10,16.14,16.52)

def spear_lift(t):
    return .42*bump(t,13.88,14.12,14.16,14.28)

def fore_grip(t,side):
    return bump(t,*( (14.18,14.31,14.33,14.45) if side=='L' else
                     (14.34,14.44,14.45,14.55) ))

def dust_state(age,life=5.8):
    """Cloud support never contracts; optical density fades independently."""
    size=.20+.64*max(0,age)
    # Expansion must dilute the plume, not create ever more opaque mass.
    density=ease(age/.12)*(1-ease((age-1.0)/(life-1.0)))/(1+(max(0,age-.4)/1.25)**2)
    return size,max(0.,density)

def departure_camera(t):
    """One position/aim/lens contract across tracking-to-recession transition."""
    y=travel(t)
    def lerp(a,b,u):return tuple(x+(z-x)*u for x,z in zip(a,b))
    if t<23:
        u=ease((t-22)/1.0)
        return (lerp((-1.05,y+4.9,.85),(-2.7,-22,2),u),lerp((.1,y,1.02),(0,y-.20,1.02),u),30+4*u)
    u=ease((t-23)/4)
    return (lerp((-2.7,-22,2),(-1.5,-25,3.5),u),lerp((0,y-.20,1.02),(0,-145,1.2),u),34+8*u)

def validate(job):
    if type(job) is not dict or set(job)!={'operation','version'}:
        raise ValueError('Exact operation/version required')
    if job['operation'] not in ('inspect','build','refine','finish','proof','movie','reopen'):
        raise ValueError('Unadmitted operation')
    if type(job['version']) is not int or not 1<=job['version']<=16:
        raise ValueError('Unadmitted version')
    if job['operation']=='refine' and job['version'] not in (5,6,8,9,10,11):
        raise ValueError('Only the reviewed build04/05 support refinements are admitted')
    if job['operation']=='finish' and job['version'] not in (7,12,13):
        raise ValueError('Only the reviewed build06 surface/camera finish is admitted')
    return job
