"""292 shot-authored travel and contact FX; not a general dynamics solver."""
import math
from movie_factory.sikh291_motion import ease, RATE, FPS, FRAMES, yaw, launch_amount
STOP=-3.6
def travel(t):
    if t<18.5:
        from movie_factory.sikh291_motion import travel as old
        return old(t)+6
    if t<20:return STOP-(4.925/2.25)*(t-18.5)**2
    if t<21.5:return STOP-4.925-(9.85/1.5)*(t-20)
    u=t-21.5;v=9.85/1.5
    if u<1.5:return STOP-14.775-v*u-4*u*u
    return STOP-14.775-v*1.5-9-(v+12)*(u-1.5)
def wheel_angle(t,rear=False):
    d=travel(t)-travel(0)
    if rear:
        if 6.15<t<7.5:d=travel(6.15)-travel(0)
        elif t>=7.5:d+=travel(6.15)-travel(7.5)
        d-=4.4*ease((t-21.4)/.75)
    return d/.34
def bike_position(t):return (-.77*math.sin(yaw(t)),travel(t),0.)
def slip(t):
    return (6.15<=t<=7.5) or (21.4<=t<=22.15)
def debris_position(origin, velocity, age):
    # Screen seconds. Low ballistic arc; settle on the road, not through it.
    x,y,z=origin;vx,vy,vz=velocity
    if age<0:return (x,y,z)
    landing=(vz+math.sqrt(vz*vz+2*9.81*max(0,z-.012)))/9.81
    a=min(age,landing);drag=(1-math.exp(-1.7*a))/1.7
    return (x+vx*drag,y+vy*drag,max(.012,z+vz*a-4.905*a*a))
def validate_job(job):
    if type(job)is not dict or set(job)!={'operation','version'}:raise ValueError('Exact job fields required')
    if job['operation'] not in ('controls','movie','reopen'):raise ValueError('Unknown operation')
    if type(job['version'])is not int or not 1<=job['version']<=20:raise ValueError('Bad version')
    return job
