"""Authored broad gather/turn/climb path in source-horse metres.

One integrated clock owns distance, heading, elevation and gait phase. These
are choreography inputs, not contact or aesthetic qualification.
"""
import numpy as np

FPS=24
DURATION=8.

def smooth(x):
    x=np.clip(x,0.,1.)
    return x*x*(3.-2.*x)

def profile(t):
    t=np.asarray(t,dtype=float)
    gather=smooth(t/2.)
    drive=smooth((t-5.)/2.5)
    speed=12.-5.5*gather+2.*drive
    # Horse forward is -Y, so its right is -X (not Blender world +X).
    heading=-np.deg2rad(55.)*smooth((t-1.5)/4.)
    grade=.12*smooth((t-3.5)/3.)
    hz=2.2-.5*gather+.15*drive
    return speed,heading,grade,hz

def trajectory():
    # 8 samples per output frame; deterministic midpoint integration.
    times=np.arange(round(DURATION*FPS*8)+1)/(FPS*8)
    speed,heading,grade,hz=profile(times)
    mid=(times[:-1]+times[1:])*.5
    v,y,g,h=profile(mid);dt=1/(FPS*8)
    horizontal=v/np.sqrt(1+g*g)
    xyz=np.zeros((len(times),3))
    xyz[1:]=np.cumsum(np.column_stack((horizontal*np.sin(y),-horizontal*np.cos(y),horizontal*g))*dt,axis=0)
    source_frames=np.r_[144.,144.+np.cumsum(h/2.2*FPS*dt)]
    angular=np.gradient(heading,times)
    # Restrained dynamically motivated banking; actual rig/contacts gate it.
    bank=np.arctan(speed*angular/9.81)
    return {'time':times,'position':xyz,'speed':speed,'heading':heading,
        'grade':grade,'frequency':hz,'bank':bank,'source_frame':source_frames,
        'stride_ratio':speed/12./(hz/2.2)}

def sample(t):
    if not 0<=t<=DURATION:raise ValueError('Outside scoped maneuver')
    data=trajectory()
    return {k:np.array([np.interp(t,data['time'],a[:,j]) for j in range(a.shape[1])]) if a.ndim==2 else float(np.interp(t,data['time'],a)) for k,a in data.items() if k!='time'}
