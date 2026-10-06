"""Coarse flared lower-tunic cut, with two actual side vents.

This is an unstressed authoring surface, not a prescribed animated silhouette.
Its upper band is the only intended body-supported region.
"""
import math
import numpy as np


def pattern():
    around,down=48,20
    points=[];faces=[];lookup={};pins={};rows=[]
    for panel in range(2):
        grid=[]
        for i in range(around+1):
            column=[]
            for j in range(down+1):
                t=j/down;theta=-math.pi/2+panel*math.pi+i*math.pi/around
                key=('side',panel if i==0 else 1-panel,j) if i in (0,around) and j<=4 else (panel,i,j)
                if key not in lookup:
                    # A narrow real opening avoids coincident unsewn edges.
                    theta+=((.012+.020*(t-.2)/.8) if t>.2 else 0.)*(1 if i==0 else -1 if i==around else 0)
                    rx=1.42+.57*t;ry=1.14+.25*t;cy=.085+.025*t
                    lookup[key]=len(points);points.append((rx*math.sin(theta),cy+ry*math.cos(theta),-5.35-2.10*t))
                    if j<=1:pins[lookup[key]]=1. if j==0 else .8
                column.append(lookup[key])
            grid.append(column)
        for i in range(around):
            for j in range(down):faces.append((grid[i][j],grid[i+1][j],grid[i+1][j+1],grid[i][j+1]))
        rows.append(grid)
    return np.array(points),np.array(faces),pins


def lower_region_masks(rest):
    x,y,z=np.asarray(rest).T
    return {'pelvis':z>-7.15,'thighL':(x>0)&(z<-6.60)&(z>-9.75),
        'thighR':(x<0)&(z<-6.60)&(z>-9.75)}
