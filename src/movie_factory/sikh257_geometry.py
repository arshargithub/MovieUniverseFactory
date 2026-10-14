"""Fixed construction controls, metres; proposals, not qualified garments."""
import math

def cloth_strip():
    """One indexed strip: secured crown winding continues into loose face span.

    Longitudinal material coordinate is measured arc length; width is explicit.
    This dressed shape is an initial condition, not simulated evidence.
    """
    centers=[];crown_parameters=[]
    crown=241
    for i in range(crown):
        u=i/(crown-1);theta=2*math.pi*4.75*u;latitude=1.50-1.45*u
        crown_parameters.append((u,theta,latitude))
        centers.append(((.108+.008*u)*math.cos(latitude)*math.sin(theta),-.010-(.165+.010*u)*math.cos(latitude)*math.cos(theta),1.610+.130*math.sin(latitude)+.015*abs(math.sin(theta))))
    # Last crown point is on -X. Continue behind ear, across face, to +X tuck.
    for i in range(1,65):
        u=i/64;theta=-math.pi/2+math.pi*u
        centers.append((.117*math.sin(theta),-.010-.175*math.cos(theta),centers[crown-1][2]-.030*u-.130*math.sin(math.pi*u)))
    verts=[];rest=[];uv=[];length=0.;cols=11
    for i,c in enumerate(centers):
        if i:length+=math.dist(c,centers[i-1])
        width=.070 if i<crown else .120
        for j in range(cols):
            v=j/(cols-1)-.5
            if i<crown:
                u,theta,latitude=crown_parameters[i]
                lat=latitude+v*width/.130
                verts.append(((.108+.008*u)*math.cos(lat)*math.sin(theta),-.010-(.165+.010*u)*math.cos(lat)*math.cos(theta),1.610+.130*math.sin(lat)+.015*abs(math.sin(theta))))
            else:verts.append((c[0],c[1],c[2]+width*v))
            rest.append((length,width*v,0.))
            uv.append((length,v+.5))
    faces=[(i*cols+j,(i+1)*cols+j,(i+1)*cols+j+1,i*cols+j+1) for i in range(len(centers)-1) for j in range(cols-1)]
    return {'verts':verts,'rest':rest,'uv':uv,'faces':faces,'cols':cols,'crown_rows':crown,'rows':len(centers),'length':length}

def ease(t):
    t=max(0.,min(1.,t));return t*t*(3-2*t)

def end_translation(frame):
    # Clear cheek first, then lower; final endpoint stands for a proposed tuck.
    reach=ease((frame-30)/24);lower=ease((frame-54)/42)
    return (-.04*reach,-.135*reach,-.24*lower)

def joint_between(a,b,l1,l2,pole):
    """Fixed-length two-bone control. Reject unreachable targets, do not stretch."""
    delta=[b[i]-a[i] for i in range(3)];d=math.sqrt(sum(v*v for v in delta))
    if not abs(l1-l2)+1e-6<d<l1+l2-1e-6:raise ValueError('Unreachable limb target')
    axis=[v/d for v in delta];dot=sum(axis[i]*pole[i] for i in range(3));p=[pole[i]-dot*axis[i] for i in range(3)]
    norm=math.sqrt(sum(v*v for v in p))
    if norm<1e-8:raise ValueError('Collinear pole')
    along=(l1*l1-l2*l2+d*d)/(2*d);height=math.sqrt(max(0,l1*l1-along*along))
    return tuple(a[i]+along*axis[i]+height*p[i]/norm for i in range(3))
