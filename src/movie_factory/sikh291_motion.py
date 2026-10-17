"""Authored shot-specific timing and assembly rules, not vehicle dynamics."""
import math
from movie_factory.sikh289_motion import ease, pulse, crowd_step as old_crowd_step
FPS=24
FRAMES=528
RATE=26/22
STOP=-9.6
PARKED={158,278,279,285,736}
FRONT_FIXED={265,266,296,297,606,607,746,747,748,749,750,751}
REAR_FIXED={3,95,96,105,145,146,149,150,164,269,270,685,686,752}

def travel(t):
    if t<4.5:return 86.4-16*t
    if t<7.5:
        u=t-4.5
        return 14.4-16*u+(16/6)*u*u
    if t<18.5:return STOP
    if t<20:return STOP-1.3*(t-18.5)**2
    if t<21.5:return STOP-2.925-3.9*(t-20)
    u=t-21.5
    if u<1.5:return STOP-8.775-3.9*u-4*u*u
    return STOP-8.775-3.9*1.5-4*1.5**2-15.9*(u-1.5)

def launch_amount(t):return pulse(t,21.4,.17,21.85,.43)
def yaw(t):return .40*ease((t-6.15)/1.0)*(1-ease((t-18.5)/1.4))-.19*launch_amount(t)
def bike_position(t):return (-.77*math.sin(yaw(t)),travel(t),0.)
def wheel_angle(t,rear=False):
    d=travel(t)-travel(0)
    if rear:
        if 6.15<t<7.5:d=travel(6.15)-travel(0)
        elif t>=7.5:d+=travel(6.15)-travel(7.5)
        d-=4.4*ease((t-21.4)/.75)
    return d/.34
def rear_amount(t):return pulse(t,14.7,.85,16.0,1.0)
def crowd_step(t,index,foot):return old_crowd_step(t+.6,index,foot)
def uncover_amount(t):return ease((t-9.7)/1.7)
def greeting(t):return pulse(t,11.4,.9,17.3,.6)
def spear_lift(t):
    # Lift, short decisive downstroke while the horse is rearing, planted hold.
    return .65*ease((t-14.5)/.6)*(1-ease((t-15.25)/.22))
def validate_job(job):
    if type(job)is not dict or set(job)!={'operation','version'}:raise ValueError('Exact fields required')
    if job['operation'] not in ('controls','movie','reopen','diagnose'):raise ValueError('Unadmitted operation')
    if type(job['version'])is not int or not 1<=job['version']<=20:raise ValueError('Invalid version')
    return job
