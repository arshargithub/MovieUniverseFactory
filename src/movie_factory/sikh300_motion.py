"""Director300 shot curves, units radians and source seconds."""
import math
from movie_factory.sikh299_motion import travel, hermite
from movie_factory.sikh291_motion import ease, FPS, FRAMES, RATE, launch_amount

def yaw(t):
    a=.44*ease((t-5.45)/.7)+.07*ease((t-6.15)/.40)+(math.radians(42)-.51)*ease((t-6.55)/.70)
    return a*(1-ease((t-18.5)/1.4))-.19*launch_amount(t)

def lean(t):
    return -.155*ease((t-5.3)/.4)+.150*ease((t-6.08)/.40)-.095*ease((t-6.55)/.20)+.100*ease((t-7.05)/.55)

def slip(t):return 5.55<=t<6.15 or 6.55<=t<7.5 or 21.4<=t<=22.15

def rear_distance(t):
    d=travel(t)-travel(0)
    for a,b in ((5.55,6.15),(6.55,7.5)):
        if t>a:d-=travel(min(t,b))-travel(a)
    return d-4.4*ease((t-21.4)/.75)

def ground_height(x,y):
    """One continuous compacted crown, shallow swale and cultivated berm."""
    a=abs(x);edge=2.05+.09*math.sin(y*.14)+.035*math.sin(y*.61)
    rut=-.018*sum(math.exp(-((x-c-.035*math.sin(y*.23))/.22)**2) for c in (-.7,.7))
    crown=.022*math.exp(-(a/1.7)**4)+rut
    ditch=-.18*math.exp(-((a-edge-.63)/.37)**2)
    berm=.075*math.exp(-((a-edge-1.32)/.38)**2)
    field=.025*ease((a-3.6)/.7)
    return crown+ditch+berm+field

def validate(j):
    if type(j)is not dict or set(j)!={'operation','version'}:raise ValueError('Exact operation/version fields required')
    if j['operation'] not in ('inspect','controls','motion','movie','reopen'):raise ValueError('Unknown operation')
    if type(j['version'])is not int or not 1<=j['version']<=30:raise ValueError('Bad version')
    return j
