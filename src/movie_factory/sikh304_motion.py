"""Shot-specific bounded traction story; not general vehicle dynamics."""
import math
from movie_factory.sikh300_motion import ground_height
from movie_factory.sikh299_motion import travel as old_travel, hermite
from movie_factory.sikh291_motion import ease, FPS, FRAMES, RATE

def bump(t,a,b,c,d):
    return ease((t-a)/(b-a))*(1-ease((t-c)/(d-c)))

def lean(t):
    return -.125*bump(t,5.3,5.65,5.95,6.30)-.028*bump(t,6.70,6.95,7.15,7.55)-.018*bump(t,21.4,21.65,21.95,22.5)

def yaw(t):
    stop=.43*ease((t-5.45)/.62)+.045*ease((t-6.15)/.48)+(math.radians(42)-.475)*ease((t-6.68)/.82)
    return stop*(1-ease((t-18.5)/1.4))-.105*bump(t,21.4,21.85,22.0,22.7)

def braking_distance(u, duration, edge, initial, final):
    """Distance from a ramped-deceleration profile, not positional overshoot."""
    u=max(0,min(duration,u))
    if u<edge: integral=u**3/(6*edge)
    elif u<=duration-edge: integral=u*u/2-edge*u/2+edge*edge/6
    else: integral=(duration-edge)*u-duration*(duration-edge)/2+(duration-u)**3/(6*edge)
    return initial*u-(initial-final)/(duration-edge)*integral

def travel(t):
    # Start braking before the visible rear lock, retaining the fast approach.
    # Same rest location and timing. Peak screen deceleration <7.4m/s2;
    # the inherited Hermite position curve exceeded20m/s2 and briefly sped up.
    if t<3.6:return 25.3+16*(3.6-t)
    if t<6.15:return 25.3-braking_distance(t-3.6,2.55,.25,16,4)
    if t<6.5:return -.2-4*(t-6.15)
    if t<7.5:return -1.6-braking_distance(t-6.5,1.,.2,4,0)
    if t<21.4:return old_travel(t)
    # Integrate acceleration, rather than adding a positional bump whose
    # second derivative caused 2.9g. Rolling launch: weak initial traction,
    # then a smooth ramp to 3.63m/s2 at the retained screen clock. The old
    # endpoint is deliberately NOT preserved at the expense of physics.
    u=t-21.4;w=(u-.55)/.5
    integral=0 if w<=0 else (.25*w**4-.1*w**5 if w<1 else .15+.5*(w-1)+.5*(w-1)**2)
    return old_travel(21.4)-(9.85/1.5)*u-.3*u*u-.5*integral

def slip(t):return 5.55<=t<6.15 or 6.70<=t<7.50 or 21.4<=t<22.15

def rear_distance(t):
    d=travel(t)-travel(0)
    for a,b in ((5.55,6.15),(6.70,7.50)):
        if t>a:d-=travel(min(t,b))-travel(a)
    return d-1.65*ease((t-21.4)/.75)

def lateral(t):return .23*bump(t,21.4,21.95,22.1,22.8)

def validate(job):
    if type(job)is not dict or set(job)!={'operation','version'}:raise ValueError('Exact job fields required')
    if job['operation'] not in ('inspect','build','finish','proof','movie','reopen'):raise ValueError('Unknown operation')
    if type(job['version'])is not int or not 1<=job['version']<=12:raise ValueError('Invalid version')
    if job['operation']=='finish' and job['version'] not in (5,6,7):raise ValueError('Unknown shadow control')
    return job

def source_name(operation,version):
    if operation=='finish':return 'build-04/sequence.blend'
    return f"{'finish' if version in (5,6,7) else 'build'}-{version:02d}/sequence.blend"
