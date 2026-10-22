"""Deterministic convex footprint support for a closed static riding-boot last."""

def cross(a,b):return a[0]*b[1]-a[1]*b[0]


def footprint(points):
    points=sorted(set((float(p[0]),float(p[1])) for p in points))
    if len(points)<3:raise ValueError('Footprint needs nondegenerate support')
    lower=[];upper=[]
    def append(chain,p):
        while len(chain)>=2 and cross((chain[-1][0]-chain[-2][0],chain[-1][1]-chain[-2][1]),(p[0]-chain[-1][0],p[1]-chain[-1][1]))<=0:chain.pop()
        chain.append(p)
    for p in points:append(lower,p)
    for p in reversed(points):append(upper,p)
    result=lower[:-1]+upper[:-1]
    if len(result)<3:raise ValueError('Degenerate footprint')
    return result


def center(hull):return tuple(sum(p[i] for p in hull)/len(hull) for i in range(2))


def radius(hull,origin,direction):
    hits=[]
    for i,a in enumerate(hull):
        b=hull[(i+1)%len(hull)];a=(a[0]-origin[0],a[1]-origin[1]);edge=(b[0]-origin[0]-a[0],b[1]-origin[1]-a[1]);denominator=cross(direction,edge)
        if abs(denominator)<1e-10:continue
        distance=cross(a,edge)/denominator;t=cross(a,direction)/denominator
        if distance>=0 and -1e-8<=t<=1+1e-8:hits.append(distance)
    return max(hits) if hits else None
