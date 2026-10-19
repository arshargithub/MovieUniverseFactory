"""Shot-specific response and stepping. Not a general dynamics/retarget solver."""
import math
import numpy as np
from movie_factory.sikh315_motion import *

def smooth_response(values, radius=5):
    """Zero-phase offline chassis filter; wheel contact stays separately owned."""
    a=np.asarray(values,dtype=float)
    if radius<1 or a.ndim!=1 or not np.isfinite(a).all():
        raise ValueError('finite scalar trajectory and positive radius required')
    w=np.exp(-.5*(np.arange(-radius,radius+1)/(radius*.46))**2);w/=w.sum()
    return np.convolve(np.pad(a,radius,mode='edge'),w,mode='valid')

def travel_response(t):
    return (1-ease((t-4.7)/.6)) if t<10 else ease((t-19.8)/1.2)

def rear(t):
    # Deliberate preparation; quick drive, short active apex, decisive landing.
    # Landing stays on the established impact clock, not stretched music time.
    return curve(t,((13.5,0),(14.94,0),(15.13,.15),(15.52,.91),
                    (15.73,1),(15.93,1.015),(16.13,.96),(16.46,.77),
                    (16.82,.39),(17.03,.055),(17.10,0),(34,0)))

def gather(t):return bump(t,13.87,14.38,14.65,15.15)
def fore_grip(t,side):
    return bump(t,*((13.90,14.16,14.25,14.62) if side=='L' else (14.19,14.47,14.58,14.92)))

def pose(t,side='L'):
    lag=.055 if side=='R' else 0
    a=rear(t);g=gather(t);land=landing(t)
    fold=bump(t,14.98+lag,15.60+lag,16.27+lag,17.07+lag)
    effort=.10*math.sin((t-15.55)*7+(0.5 if side=='R' else 0))*fold
    return dict(rise=a,shoulder=-.27*fold+.06*effort,
                elbow=-1.18*fold-.20*effort,wrist=1.52*fold+.18*effort,
                toe=-.10*fold,neck=.40*g+.24*a+.10*land,
                head=.48*g+.27*rear(t-.07)+.17*land,
                chest=-.055*g-.045*a+.04*land,hips=.06*g+.035*a-.04*land)

def crowd_step(t,index,foot):
    """Four short step-and-close pairs; no crossing or exaggerated split stance."""
    start=17.62+(0,.13,.31,.06,.24,.43,.18,.37,.48,.29)[index]
    duration=.255+.010*(index%3);gap=.035
    side=-1 if index%2 else 1
    leading=0 if side<0 else 1
    schedule=(0,2,4,6) if foot==leading else (1,3,5,7)
    distance=0.;lift=0.;active=0.
    for k in schedule:
        u=(t-start-k*(duration+gap))/duration
        distance+=.425*ease(u)
        if 0<u<1:
            lift=.060*math.sin(math.pi*u)**1.5;active=math.sin(math.pi*u)
    return distance,lift,active,start
