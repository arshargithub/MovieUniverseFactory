"""Continuous shot-authored rear profiles; not a general animal simulator."""
import math
from movie_factory.sikh317_motion import *

def flow(t, keys):
    """Shape-preserving Hermite curve. Interior monotone knots retain velocity."""
    if t<=keys[0][0]:return keys[0][1]
    if t>=keys[-1][0]:return keys[-1][1]
    h=[b[0]-a[0] for a,b in zip(keys,keys[1:])]
    if min(h)<=0:raise ValueError('Increasing times required')
    d=[(b[1]-a[1])/dt for a,b,dt in zip(keys,keys[1:],h)]
    slopes=[0.]
    for i in range(1,len(keys)-1):
        if d[i-1]*d[i]<=0:slopes.append(0.)
        else:
            w1=2*h[i]+h[i-1];w2=h[i]+2*h[i-1]
            slopes.append((w1+w2)/(w1/d[i-1]+w2/d[i]))
    slopes.append(0.)
    for i,(a,b) in enumerate(zip(keys,keys[1:])):
        if t<=b[0]:
            u=(t-a[0])/h[i]
            return (2*u**3-3*u*u+1)*a[1]+(u**3-2*u*u+u)*h[i]*slopes[i]+(-2*u**3+3*u*u)*b[1]+(u**3-u*u)*h[i]*slopes[i+1]

REAR=((13.5,0),(15.42,0),(15.61,.13),(15.93,.70),(16.14,1),
      (16.28,.97),(16.57,.68),(16.92,.12),(17.10,0),(34,0))
def rear(t):return flow(t,REAR)
def gather(t):return flow(t,((13.5,0),(14.0,0),(14.55,.6),(15.12,1),(15.5,.12),(15.8,0),(34,0)))
def fore_grip(t,side):
    shift=.29 if side=='R' else 0
    return flow(t-shift,((13.5,0),(14.05,0),(14.26,.7),(14.40,1),(14.68,.15),(14.79,0),(34,0)))
def pose(t,side='L'):
    lag=.06 if side=='R' else 0;q=t-lag;a=rear(t);g=gather(t);land=landing(t)
    fold=flow(q,((13.5,0),(15.39,0),(15.67,.5),(16.04,1),(16.25,.95),(16.55,.67),(16.85,.18),(17.10,0),(34,0)))
    reach=flow(q,((13.5,0),(16.2,0),(16.57,.6),(16.86,1),(17.10,0),(34,0)))
    return dict(rise=a,shoulder=-.27*fold+.055*reach,
        elbow=-1.18*fold+.08*reach,wrist=2.22*fold-.10*reach,toe=.60*fold,
        neck=.40*g+.22*rear(t-.035)+.10*land,
        head=.43*g+.46*rear(t-.075)+.16*land,
        chest=-.055*g-.045*a+.04*land,hips=.06*g+.035*a-.04*land)
