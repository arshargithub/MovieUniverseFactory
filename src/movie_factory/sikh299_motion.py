"""Shot-authored two-stage brake; no claim of general motorcycle dynamics."""
import math
from movie_factory.sikh291_motion import ease, FPS, FRAMES, RATE, launch_amount
from movie_factory.sikh292_motion import travel as original_travel

def hermite(t, a, b, p, q, v, w):
    u=(t-a)/(b-a);d=b-a
    return (2*u**3-3*u*u+1)*p+(u**3-2*u*u+u)*d*v+(-2*u**3+3*u*u)*q+(u**3-u*u)*d*w

def travel(t):
    knots=((4.5,20.4,-16),(5.4,6.,-12),(6.15,-.2,-4),(6.5,-1.65,-4),(7.5,-3.6,0))
    if t<4.5 or t>=7.5:return original_travel(t)
    for a,b in zip(knots,knots[1:]):
        if a[0]<=t<b[0]:return hermite(t,a[0],b[0],a[1],b[1],a[2],b[2])

def yaw(t):
    angle=.56*ease((t-5.45)/.7)+.10*ease((t-6.15)/.35)+.27*ease((t-6.5)/.75)
    return angle*(1-ease((t-18.5)/1.4))-.19*launch_amount(t)

def lean(t):
    return -.29*ease((t-5.3)/.4)+.12*ease((t-6.1)/.35)-.055*ease((t-6.5)/.2)+.225*ease((t-7.05)/.55)

def slip(t):return 5.55<=t<6.15 or 6.5<=t<7.5 or 21.4<=t<=22.15

def rear_distance(t):
    d=travel(t)-travel(0)
    for a,b in ((5.55,6.15),(6.5,7.5)):
        if t>a:d-=travel(min(t,b))-travel(a)
    return d-4.4*ease((t-21.4)/.75)

def validate(job):
    if type(job)is not dict or set(job)!={'operation','version'}:raise ValueError('Exact fields required')
    if job['operation'] not in ('inspect','controls','motion','movie','reopen'):raise ValueError('Unknown operation')
    if type(job['version'])is not int or not 1<=job['version']<=20:raise ValueError('Bad version')
    return job
