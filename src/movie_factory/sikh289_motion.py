"""Deterministic staging clock. Authored kinematics, not physics qualification."""
import math

FPS = 12
FRAMES = 312

def ease(x):
    x = max(0., min(1., x))
    return x*x*(3-2*x)

def pulse(t, start, rise, end, fall):
    return ease((t-start)/rise)*(1-ease((t-end)/fall))

def travel(t):
    # Negative time supplies the opening dust pre-roll at the same speed.
    if t < 8: return 50-7*t
    if t < 10:
        u=t-8
        return -6-7*u+1.75*u*u
    if t < 18.5: return -13.
    if t < 20:
        u=t-18.5
        return -13-.5*u*u
    if t < 22: return -14.125-1.5*(t-20)
    u=t-22
    return -17.125-1.5*u-1.1*u*u

def yaw(t):
    return .40*ease((t-8.5)/1.3)*(1-ease((t-18.5)/1.4))

def bike_position(t):
    a=yaw(t)
    return (-.70*math.sin(a), travel(t), 0.)

def wheel_angle(t, rear=False):
    d=travel(t)-travel(0)
    if rear:
        if 8.7<t<10: d=travel(8.7)-travel(0)
        elif t>=10: d+=travel(8.7)-travel(10)
        d-=.48*ease((t-22)/.45)
    return d/.34

def rear_amount(t):
    return pulse(t,15.7,.9,17.0,1.1)

def crowd_step(t, index, foot):
    """Local lateral foot displacement: alternating planted steps, four steps."""
    start=17.7+(index%3)*.12
    clock=max(0.,min(4.,(t-start)/.48))
    # Each foot moves on alternating half cycles. Ends separated along travel.
    k=int(clock);u=clock-k
    if clock>=4: k=3;u=1
    displacement=0.
    lift=0.
    for step in range(4):
        if step%2==foot:
            progress=1 if step<k else ease(u) if step==k else 0
            displacement+=.85*progress
            if step==k:lift=.08*math.sin(math.pi*u)
    return displacement,lift

def validate_job(job):
    if type(job) is not dict or set(job)!={'operation','version'}:
        raise ValueError('Exact structured fields required')
    if job['operation'] not in ('inspect','controls','movie','reopen','diagnose','camera_patch'):
        raise ValueError('Unadmitted operation')
    if type(job['version']) is not int or not 1<=job['version']<=30:
        raise ValueError('Invalid version')
    return job
