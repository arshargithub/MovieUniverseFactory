"""Authored gait targets in metres/seconds; independent of Blender."""
import math
SPEED=12.0
FREQUENCY=2.4
PERIOD=1/FREQUENCY
DUTY=.16
TOUCHDOWN={'LH':0.,'RH':.14,'LF':.32,'RF':.48}
HOMES={'LH':(.18,3.18),'RH':(-.18,3.18),'LF':(.17,2.05),'RF':(-.17,2.05)}

def hermite(q0,q1,v0,v1,u,dt):
    return (2*u**3-3*u*u+1)*q0+(u**3-2*u*u+u)*dt*v0+(-2*u**3+3*u*u)*q1+(u**3-u*u)*dt*v1

def target(t,leg):
    phase=(t*FREQUENCY-TOUCHDOWN[leg])%1
    half=SPEED*DUTY*PERIOD/2
    if phase<=DUTY:
        y=-half+SPEED*phase*PERIOD;z=0
    else:
        s=(phase-DUTY)/(1-DUTY);duration=PERIOD*(1-DUTY)
        knots=[(0,half,0,SPEED,0),(.16,.55,.52,-2,1.0),(.55,-.05,.62,-6,0),(.86,-.55,.45,0,-2),(1,-half,0,SPEED,0)]
        a,b=next((a,b) for a,b in zip(knots,knots[1:]) if s<=b[0]+1e-10)
        u=(s-a[0])/(b[0]-a[0]);dt=(b[0]-a[0])*duration
        y=hermite(a[1],b[1],a[3],b[3],u,dt);z=hermite(a[2],b[2],a[4],b[4],u,dt)
    x,home=HOMES[leg]
    return (x,home-SPEED*t+y,z),phase<=DUTY

def heave_profile(count=1024):
    dt=PERIOD/count
    loads=[]
    for i in range(count):
        phase=(i+.5)/count
        loads.append(sum(math.sin(math.pi*p/DUTY)**2 for td in TOUCHDOWN.values() if (p:=(phase-td)%1)<DUTY))
    mean=sum(loads)/count;v=0;vel=[]
    for b in loads:v+=(9.81*b/mean-9.81)*dt;vel.append(v)
    meanv=sum(vel)/count;z=0;zs=[]
    for v in vel:z+=(v-meanv)*dt;zs.append(z)
    meanz=sum(zs)/count
    return [z-meanz for z in zs]
HEAVE=heave_profile()
def body_z(t):
    x=(t*FREQUENCY%1)*len(HEAVE);i=int(x);u=x-i
    return HEAVE[i]*(1-u)+HEAVE[(i+1)%len(HEAVE)]*u
