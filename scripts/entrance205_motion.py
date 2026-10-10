"""Exchange205 choreography inputs. Metres, seconds, no editorial slow motion.

These are authored animation targets, not a physical equestrian simulation.
Contact and screen-readability qualification is performed by the native worker.
"""
import numpy as np

FPS = 24
DURATION = 12.0


def smooth(x):
    x = np.clip(x, 0., 1.)
    return x*x*(3.-2.*x)


def profile(t):
    t = np.asarray(t, float)
    gather = smooth((t-.65)/1.0)
    launch = smooth((t-2.15)/1.2)
    speed = 12.-6.8*gather+3.0*launch
    heading = -np.deg2rad(68.)*smooth((t-1.35)/1.85)
    grade = .48*smooth((t-2.65)/1.6)
    hz = 2.2-.45*gather+.25*launch
    return speed, heading, grade, hz


def trajectory():
    times = np.arange(round(DURATION*FPS*8)+1)/(FPS*8)
    speed, heading, grade, hz = profile(times)
    v, y, g, h = profile((times[:-1]+times[1:])*.5)
    dt = 1/(FPS*8)
    horizontal = v/np.sqrt(1+g*g)
    xyz = np.zeros((len(times), 3))
    xyz[1:] = np.cumsum(np.column_stack((horizontal*np.sin(y), -horizontal*np.cos(y), horizontal*g))*dt, axis=0)
    source = np.r_[144., 144.+np.cumsum(h/2.2*FPS*dt)]
    # Lean is authored and bounded for a readable supported turn; source rig
    # contact projection, not this angle alone, determines ground validity.
    bank = np.clip(np.arctan(speed*np.gradient(heading, times)/9.81), -np.deg2rad(27), np.deg2rad(27))
    return dict(time=times, position=xyz, speed=speed, heading=heading, grade=grade,
                frequency=hz, bank=bank, source_frame=source,
                stride_ratio=speed/12./(hz/2.2))


def sample(t):
    if not 0 <= t <= DURATION:
        raise ValueError('Outside205 choreography')
    data = trajectory()
    return {k: np.array([np.interp(t, data['time'], a[:, j]) for j in range(a.shape[1])])
            if a.ndim == 2 else float(np.interp(t, data['time'], a))
            for k, a in data.items() if k != 'time'}
