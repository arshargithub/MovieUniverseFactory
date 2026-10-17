"""Sikh290 authored staging clock; travel in source seconds, not simulation."""
import math
from movie_factory.sikh289_motion import ease,pulse,rear_amount,crowd_step

FPS=24
FRAMES=528
RATE=26/22

def travel(t):
    if t<8:return 86-11*t
    if t<10:
        u=t-8
        return -2-11*u+2.75*u*u
    if t<18.5:return -13.
    if t<20:return -13-.8*(t-18.5)**2
    if t<21.5:return -14.8-2.4*(t-20)
    u=t-21.5
    if u<1.6:return -18.4-2.4*u-3.8*u*u
    return -18.4-2.4*1.6-3.8*1.6**2-(2.4+7.6*1.6)*(u-1.6)

def launch_amount(t):return pulse(t,21.4,.17,21.85,.43)

def yaw(t):
    return .40*ease((t-8.5)/1.3)*(1-ease((t-18.5)/1.4))-.19*launch_amount(t)

def bike_position(t):return (-.77*math.sin(yaw(t)),travel(t),0.)

def wheel_angle(t,rear=False):
    d=travel(t)-travel(0)
    if rear:
        if 8.7<t<10:d=travel(8.7)-travel(0)
        elif t>=10:d+=travel(8.7)-travel(10)
        # Two extra rear revolutions before traction catches: bounded slip.
        d-=4.4*ease((t-21.4)/.75)
    return d/.34

def validate_job(job):
    if type(job)is not dict or set(job)!={'operation','version'}:raise ValueError('Exact structured fields required')
    if job['operation'] not in ('controls','movie','reopen','camera_patch'):raise ValueError('Unadmitted operation')
    if type(job['version'])is not int or not 1<=job['version']<=20:raise ValueError('Invalid version')
    return job
