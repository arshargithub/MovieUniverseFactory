"""Shot-scoped207 response functions; deterministic, bounded and testable."""
import numpy as np
from entrance205_motion import smooth
from entrance206_performance import expression as old_expression

def flexion(chest):
 """Distributed absorption driven by existing chest pitch, not an independent clock."""
 chest=np.asarray(chest,float)
 if chest.ndim!=1 or len(chest)<20 or not np.isfinite(chest).all():raise ValueError('Finite gait series required')
 mean=np.convolve(np.pad(chest,(12,12),mode='edge'),np.ones(25)/25,mode='valid')
 drive=chest-mean;scale=max(np.percentile(abs(drive),90),np.deg2rad(.5))
 drive=np.clip(drive/scale,-1,1);lag=np.r_[drive[0],drive[:-1]]
 # Forward lean and six-degree absorption at the cervical base; the skull
 # counterrotates most, not all, of that change to maintain visual attention.
 neck=np.deg2rad(3+6*lag);head=-neck*.76
 return np.column_stack((neck,head))

def expression(f):
 v=old_expression(f);acq=float(smooth((f-321)/5)*(1-smooth((f-333)/8)));resolve=float(smooth((f-333)/12))
 v.update(browInnerUp=.025+.55*acq,browOuterUpLeft=.03+.36*acq,browOuterUpRight=.03+.32*acq,
          browDownLeft=.035+.61*resolve,browDownRight=.03+.54*resolve,
          eyeSquintLeft=.06+.48*resolve,eyeSquintRight=.06+.44*resolve,
          mouthPressLeft=.035+.47*resolve,mouthPressRight=.035+.47*resolve)
 return v

def mane_step(rest,offset,velocity,acceleration,phase,clock):
 """Coherent moving-rest guide response with root pinning and length projections.

 Authored one-way aerodynamic model; not a calibrated fluid/hair solver.
 """
 rest=np.asarray(rest,float);u=np.linspace(0,1,12)[None,:,None];mob=u**1.7;mob[:,:2]=0
 lengths=np.linalg.norm(np.diff(rest,axis=1),axis=2);dt=1/96
 # The short forelock is considerably stiffer than long neck hair. Drive
 # neighboring strands coherently rather than turning fine fibers into frizz.
 gain=np.clip((lengths.sum(1)/4.2)**3,.045,1)[:,None,None]
 for sub in range(4):
  t=clock+sub*dt
  gust=np.stack((np.sin(t*8+phase),np.sin(t*5.7+phase*.7),np.sin(t*9.1+phase*.5)),axis=-1)[:,None,:]
  force=(np.array([0,48,12])[None,None,:]+gust*np.array([14,12,16])-acceleration[:,None,:]*.32)*mob*gain-48*offset
  velocity=(velocity+force*dt)*np.exp(-5.0*dt);offset+=velocity*dt
  p=rest+offset
  for _ in range(12):
   for parity in (0,1):
    a=np.arange(parity,11,2);b=a+1;d=p[:,b]-p[:,a];length=np.maximum(np.linalg.norm(d,axis=2),1e-9)
    wa=mob[:,a,0];wb=mob[:,b,0];den=np.maximum(wa+wb,1e-9)
    correction=d*((length-lengths[:,a])/length)[:,:,None]
    p[:,a]+=correction*(wa/den)[...,None];p[:,b]-=correction*(wb/den)[...,None]
   p[:,:2]=rest[:,:2]
  previous=offset.copy();offset=p-rest;velocity+=(offset-previous)/dt;velocity=np.clip(velocity,-35,35)
 if not np.isfinite(p).all():raise ValueError('Nonfinite mane')
 return offset,velocity

def tail_response(centers,roots,worlds):
 """Root-driven damped centerline with gravity and turn inertia; no rigid tail rotation."""
 from entrance193_motion import frame_basis
 centers=np.asarray(centers,float);roots=np.asarray(roots,float);worlds=np.asarray(worlds,float)
 lengths=np.linalg.norm(np.diff(centers,axis=0),axis=1);n=len(centers)
 if n<3 or lengths.min()<1e-5:raise ValueError('Tail centerline invalid')
 # Relax the old floating rest silhouette toward a weighted trailing curve,
 # retaining actual arc length instead of stretching/dropping mesh vertices.
 rest=centers-centers[0];u=np.linspace(0,1,n);rest[:,2]-=2.1*u**1.4
 for j,L in enumerate(lengths):rest[j+1]=rest[j]+(rest[j+1]-rest[j])*L/np.linalg.norm(rest[j+1]-rest[j])
 worldroots=np.einsum('fij,fj->fi',worlds[:,:3,:3],roots)+worlds[:,:3,3]
 acc=np.gradient(np.gradient(worldroots,axis=0)*24,axis=0)*24
 acc=np.array([np.linalg.solve(m[:3,:3],a) for m,a in zip(worlds,acc)]);acc=np.clip(acc,-120,120)
 p=rest+roots[0];vel=np.zeros_like(p);rows=[];dt=1/192
 for i,root in enumerate(roots):
  for sub in range(8):
   anchor=roots[max(i-1,0)]*(1-(sub+1)/8)+root*((sub+1)/8);target=rest+anchor
   force=28*(target-p)-4.8*vel+np.array([0,12,-30])-acc[i]*.5
   # An unequal distributed air response breaks synchronous rod-like motion.
   t=(i+sub/8)/24;force[:,0]+=6*np.sin(t*5-u*2)*u
   old=p.copy();vel+=force*dt;p+=vel*dt
   for _ in range(28):
    p[0]=anchor
    for j,L in enumerate(lengths):
     d=p[j+1]-p[j];c=d*(1-L/max(np.linalg.norm(d),1e-9))
     if j==0:p[j+1]-=c
     else:p[j]+=.5*c;p[j+1]-=.5*c
   p[0]=anchor;vel=(p-old)/dt
  rows.append(p.copy())
 return np.array(rows)
