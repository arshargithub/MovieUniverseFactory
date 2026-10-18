"""Independent authored response profiles; not a physical simulation."""
import math
from movie_factory.sikh305_motion import FRAMES, RATE, FPS

def curve(t, keys):
    if t <= keys[0][0]: return keys[0][1]
    for (a,x),(b,y) in zip(keys,keys[1:]):
        if t <= b:
            u=(t-a)/(b-a);u=u*u*(3-2*u)
            return x+(y-x)*u
    return keys[-1][1]

def pose(t, side='L'):
    # Body comes up before knees finish folding; feet reach before chest lands.
    off=.10 if side=='R' else 0
    q=t-off
    rise=curve(t,[(0,0),(14.72,0),(14.89,.06),(15.13,.83),(15.30,1),
                  (15.48,.99),(15.67,.83),(15.90,.25),(16.02,0),(29,0)])
    paw=curve(q,[(0,0),(15.16,0),(15.36,1),(15.53,-.55),(15.76,0),(29,0)])
    fold=curve(q,[(0,0),(14.84,0),(15.11,.72),(15.27,1),(15.56,.90),
                  (15.72,.55),(15.93,.04),(16.02,0),(29,0)])
    return dict(rise=rise,fold=fold,paw=paw,
        shoulder=-.27*fold+.12*paw,
        elbow=-1.32*fold-.22*paw,
        wrist=2.5*fold+.12*paw,
        toe=.4*fold,
        neck=curve(t,[(0,0),(14.15,0),(14.65,.52),(14.85,.32),(15.15,.20),
                      (15.46,.34),(15.73,.15),(16.02,.18),(16.16,.38),(16.55,0),(29,0)]),
        head=curve(t,[(0,0),(14.2,0),(14.62,.58),(14.92,.15),(15.24,.30),
                      (15.5,.44),(15.80,.17),(16.03,.25),(16.19,.37),(16.6,0),(29,0)]))

def validate(job):
    if type(job) is not dict or set(job)!={'operation','version'}:
        raise ValueError('Exact operation/version required')
    if job['operation'] not in ('build','proof','movie','reopen','limbcontrol','hoofcontrol','audit','auditverify'):
        raise ValueError('Unadmitted operation')
    if type(job['version']) is not int or not 1<=job['version']<=7:
        raise ValueError('Unadmitted version')
    return job
