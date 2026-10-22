"""Height-local collision envelope; never mutate the accepted native groom.

A whole-groom convex hull bridges rear locks at different heights and props
cloth into a hood. Local cross-sections retain the actual crown/nape contour.
This is a construction exclusion surface, not hair dynamics or acceptance.
"""
import math
import numpy as np


def envelope(points,levels=48,segments=64):
    from wardrobe_footbed import footprint,center,radius
    data=np.asarray(points,dtype=float)
    if data.ndim!=2 or data.shape[1]!=3 or len(data)<10 or not np.isfinite(data).all():
        raise ValueError('Finite bounded groom coordinates required')
    if len(data)>2_000_000 or levels<4 or segments<8:raise ValueError('Groom envelope complexity bound')
    low=float(data[:,2].min());high=float(data[:,2].max())
    if high-low<.1:raise ValueError('Degenerate groom height')
    step=(high-low)/(levels-1);vertices=[];faces=[]
    for j,z in enumerate(np.linspace(low+.025,high-.012,levels)):
        sample=data[np.abs(data[:,2]-z)<max(.10,step*.8)]
        if len(sample)<3:raise ValueError('Missing local groom support')
        hull=footprint(sample[:,:2]);origin=center(hull)
        for i in range(segments):
            a=math.tau*i/segments;d=(math.cos(a),math.sin(a));r=radius(hull,origin,d)
            if r is None:raise ValueError('Missing radial groom boundary')
            vertices.append((origin[0]+d[0]*(r+.025),origin[1]+d[1]*(r+.025),float(z)))
        if j:
            for i in range(segments):
                k=(j-1)*segments+i;l=(j-1)*segments+(i+1)%segments
                faces.append((k,l,l+segments,k+segments))
    for j in (0,levels-1):
        ring=vertices[j*segments:(j+1)*segments]
        cap=len(vertices);vertices.append((sum(p[0] for p in ring)/segments,sum(p[1] for p in ring)/segments,low-.01 if j==0 else high+.015))
        for i in range(segments):
            a=j*segments+i;b=j*segments+(i+1)%segments
            faces.append((cap,b,a) if j==0 else (cap,a,b))
    return vertices,faces
