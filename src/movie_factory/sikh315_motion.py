"""Shot-authored coordinated trajectories, not a general dynamics simulator."""
import math
from movie_factory import sikh305_motion as old
from movie_factory.sikh314_motion import curve
from movie_factory.sikh291_motion import FPS,RATE,ease
FRAMES=696
bump=old.bump
old_travel=old.old_travel
ground_height=old.ground_height
# Source seconds. Continuous velocity integrates into position; throttle spin
# and translation deliberately have different owners until grip returns.
SPEED=((20.0,6.5666666667),(21.3,2.4),(22.25,2.4),(22.65,3.0),(23.4,6.3),(25.6,14.8),(27.0,17.0))
def integral(t,knots=SPEED):
    result=0.
    for (a,va),(b,vb) in zip(knots,knots[1:]):
        if t<=a:break
        u=min(1,(t-a)/(b-a));result+=(b-a)*(va*u+(vb-va)*(u**3-.5*u**4))
    if t>knots[-1][0]:result+=(t-knots[-1][0])*knots[-1][1]
    return result
def speed(t):return curve(t,SPEED) if t>=20 else -(old.travel(t+.001)-old.travel(t-.001))/.002
def travel(t):return old.travel(t) if t<=20 else old.travel(20)-integral(t)
def yaw(t):return old.yaw(t) if t<21.4 else -.36*bump(t,21.4,22.05,22.22,23.15)
def lateral(t):return .60*bump(t,21.4,22.08,22.22,23.15)
def lean(t):return old.lean(t) if t<21.4 else -.065*bump(t,21.4,21.95,22.22,23.1)
def slip(t):return old.slip(t) if t<21.4 else 21.4<=t<22.75
def rear_distance(t):
    d=travel(t)-travel(0)
    for a,b in ((5.55,6.15),(6.70,7.50)):
        if t>a:d-=travel(min(t,b))-travel(a)
    return d-7.0*ease((t-21.4)/1.35)
def rear(t):
    return curve(t,((13.5,0),(14.66,0),(14.82,.10),(15.15,.90),(15.34,1),(15.75,.96),(16.12,1.025),(16.40,.94),(16.62,.88),(16.82,.60),(17.03,.08),(17.10,0),(34,0)))
def gather(t):return bump(t,13.92,14.35,14.57,14.94)
def landing(t):return bump(t,17.02,17.14,17.20,17.48)
def spear_lift(t):return old.spear_lift(t)
def fore_grip(t,side):return bump(t,*((14.02,14.16,14.24,14.38) if side=='L' else (14.23,14.35,14.43,14.56)))
def pose(t,side='L'):
    shift=.075 if side=='R' else 0;a=rear(t);g=gather(t);l=landing(t)
    fold=bump(t,14.74+shift,15.18+shift,16.48+shift,17.05+shift)
    paw=2.2*curve(t-(.18 if side=='R' else 0),((14.8,0),(15.30,.04),(15.62,-.17),(15.94,.20),(16.20,-.10),(16.48,.12),(16.78,0),(17.2,0)))
    return dict(rise=a,shoulder=-.28*fold+.26*paw,elbow=-1.34*fold-.65*paw,wrist=2.48*fold+.45*paw,toe=.42*fold,
                neck=.47*g+.28*a+.14*paw+.10*l,
                head=.67*g+.36*rear(t-.09)-.23*paw+.29*l,
                chest=-.055*g-.045*a+.04*l,hips=.06*g+.035*a-.04*l)
