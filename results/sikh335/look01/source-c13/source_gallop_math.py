"""Single physical clock and monotone source event maps."""
FPS=24;FRAMES=144;SPEED=12.;HZ=2.2;PERIOD=FPS/HZ
LEGS={'LH':('hind_foot_ik.L','DEF-r_hoof.L',9.125,12.46875,0.,.64579),'RH':('hind_foot_ik.R','DEF-r_hoof.R',1.34375,3.375,.14,.97284),'LF':('forefoot_ik.L','DEF-f_hoof.L',2.4375,5.46875,.32,.75438),'RF':('forefoot_ik.R','DEF-f_hoof.R',3.5,7.3125,.48,.81897)}
def hermite(a,b,m,u,span):return (2*u**3-3*u*u+1)*a+(u**3-2*u*u+u)*span*m+(-2*u**3+3*u*u)*b+(u**3-u*u)*span*m

def source_phase(phase,leg):
 _,_,a,b,td,stroke=LEGS[leg];d=stroke/(SPEED/HZ);p=(phase-td)%1;v=(b-a)/d;w=(10-b+a)/(1-d);slope=2*v*w/(v+w)
 return (hermite(a,b,slope,p/d,d) if p<=d else hermite(b,a+10,slope,(p-d)/(1-d),1-d))%10

def leg_for(name):
 for leg,(ctrl,_,_,_,_,_) in LEGS.items():
  side=ctrl[-2:];front=leg.startswith('L') if False else leg.endswith('F')
  if name.endswith(side) and ((front and name.startswith(('forefoot_','f_hoof','f_toe_'))) or (not front and name.startswith(('hind_foot_','r_hoof','r_toe_')))):return leg
 return None

