"""Authored recognition and shot timing for the approved complete story proof.

Pure planning math; not physical simulation or an automatic visual gate.
"""
import numpy as np
def smooth(x):
 x=np.clip(x,0.,1.);return x*x*(3-2*x)
def glance(t):
 return float(smooth((t-5.)/.65)*(1-smooth((t-6.35)/.85)))
def source_time(t):
 """Monotone shared retiming, including a gathered interval before drive."""
 if not 0<=t<=10:raise ValueError('Outside story maneuver')
 # Piecewise cubic Hermite: continuous time and velocity, no frame freeze.
 knots=[0,2,5,8,10];values=[0,2,3.5,6,8];rates=[1,1,.55,1,1]
 i=min(int(np.searchsorted(knots,t,side='right'))-1,3);h=knots[i+1]-knots[i];u=(t-knots[i])/h
 return float((2*u**3-3*u**2+1)*values[i]+(u**3-2*u**2+u)*h*rates[i]+(-2*u**3+3*u**2)*values[i+1]+(u**3-u**2)*h*rates[i+1])
def face_values(t,recognition=False):
 r=float(smooth((t-.25)/.85)) if recognition else 1.
 acquire=float(smooth(t/.25)*(1-smooth((t-.35)/.3))) if recognition else 0.
 return {'eyeBlinkLeft':0.,'eyeBlinkRight':0.,'eyeSquintLeft':.07+.28*r-.04*acquire,'eyeSquintRight':.07+.25*r-.04*acquire,
 'browDownLeft':.025+.255*r,'browDownRight':.02+.23*r,'browInnerUp':.025+.10*acquire,
 'mouthPressLeft':.025+.215*r,'mouthPressRight':.025+.215*r,'jawOpen':.09*(1-r)+.008,'cheekSquintLeft':.025+.07*r,'cheekSquintRight':.025+.07*r}

def shot_frame(index):
 """One edit clock, including the forward continuation AFTER the glance."""
 if not isinstance(index,int) or not 0<=index<432:raise ValueError('Outside complete18-second edit')
 if index<144:return 'opening','opening',float(217+index)
 if index<192:return 'recognition','recognition',float(289+index-144)
 t=(index-192)*10/239
 return 'route',('ots' if t<2 else 'wide' if t<7 else 'final'),361+24*source_time(t)
