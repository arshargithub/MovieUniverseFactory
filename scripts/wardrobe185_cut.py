"""Clean headfall and open, overlapping scarf-strip construction.

Patterns describe support, layering and fabric metric, not final animated folds.
"""
import math
import numpy as np
from wardrobe_doublewrap185 import periodic_section,course


def winding_inside(point, triangles):
    """Solid-angle fallback for numerically ambiguous ray parity."""
    a,b,c=np.moveaxis(np.asarray(triangles)-np.asarray(point),1,0)
    na=np.linalg.norm(a,axis=1);nb=np.linalg.norm(b,axis=1);nc=np.linalg.norm(c,axis=1)
    numerator=np.einsum('ij,ij->i',a,np.cross(b,c))
    denominator=na*nb*nc+np.einsum('ij,ij->i',a,b)*nc+np.einsum('ij,ij->i',b,c)*na+np.einsum('ij,ij->i',c,a)*nb
    winding=abs(np.arctan2(numerator,denominator).sum()/(2*math.pi))
    if winding<1e-4:return False
    if abs(winding-1)<1e-4:return True
    raise ValueError('Unresolved solid-angle interior: '+str(winding))


def headfall(source):
    grid=np.asarray(source).reshape(25,49,3)
    result=grid.copy()
    # Retain the useful supported opening/crown. Replace folded-through lower
    # rows with a free rear curtain, then regularize longitudinal sampling.
    for j in range(49):
        v=j/48;angle=(2*v-1)*math.pi/2
        end=np.array([1.40*math.sin(angle),.56+.98*math.cos(angle),-3.70+.05*math.sin(angle)])
        guide=np.concatenate([grid[:17,j],np.array([grid[16,j]*(1-t)+end*t for t in np.linspace(0,1,9)[1:]])])
        length=np.r_[0,np.cumsum(np.linalg.norm(np.diff(guide,axis=0),axis=1))]
        target=np.linspace(0,length[-1],25)
        for axis in range(3):result[:,j,axis]=np.interp(target,length,guide[:,axis])
    return result.reshape(-1,3)


def rectangular_metric(points, rows, cols, typical=False):
    grid=np.asarray(points).reshape(rows,cols,3)
    statistic=np.median if typical else max
    length=statistic([np.linalg.norm(np.diff(grid[:,j],axis=0),axis=1).sum() for j in range(cols)])
    width=statistic([np.linalg.norm(np.diff(grid[i],axis=0),axis=1).sum() for i in range(rows)])
    return np.array([(length*i/(rows-1),width*j/(cols-1),0.) for i in range(rows) for j in range(cols)])


def separate_layers(points, faces, counts, margin=.10, periodic=False):
    """Dress each outer strip beyond preceding layers along radial rays.

    Initial construction only. Exact triangle overlap rejects any unresolved
    crossing; no post-simulation projection or visual-pass claim.
    """
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    p=np.array(points,copy=True);offset=int(counts[0]);records=[]
    for count in counts[1:]:
        lower=faces[faces[:,0]<offset]
        tree=BVHTree.FromPolygons(p.tolist(),lower.tolist())
        displacement=[];directions=[];original=p[offset:offset+count].copy()
        for i in range(offset,offset+count):
            q=Vector(p[i]);origin=Vector((0,.30,q.z));direction=q-origin
            radius=direction.length;direction.normalize();ray=origin.copy();outer=0.
            for _ in range(64):
                h,_,_,_=tree.ray_cast(ray,direction,5.)
                if h is None:break
                outer=max(outer,(h-origin).dot(direction));ray=h+direction*1e-4
            else:raise ValueError('Layer ray did not terminate')
            delta=max(0.,outer+margin-radius)
            displacement.append(delta);directions.append(np.array(direction))
        # Carry a required clearance across neighboring samples at an open
        # headfall edge. Independent rays otherwise introduce a sharp dent
        # exactly where one ray misses that boundary and its neighbor hits.
        rows=int(count)//21
        grid=np.array(displacement).reshape(rows,21)
        padded=np.pad(np.pad(grid,((2,2),(0,0)),mode='wrap' if periodic else 'edge'),((0,0),(2,2)),mode='edge')
        spread=np.maximum.reduce([padded[i:i+rows,j:j+21] for i in range(5) for j in range(5)])
        for _ in range(2):
            pad=np.pad(np.pad(spread,((1,1),(0,0)),mode='wrap' if periodic else 'edge'),((0,0),(1,1)),mode='edge')
            spread=np.maximum(grid,sum(pad[i:i+rows,j:j+21] for i in range(3) for j in range(3))/9)
        p[offset:offset+count]=original+np.array(directions)*spread.reshape(-1,1)
        upper=faces[(faces[:,0]>=offset)&(faces[:,0]<offset+count)]
        upper_tree=BVHTree.FromPolygons(p.tolist(),upper.tolist())
        overlaps=tree.overlap(upper_tree)
        records.append({'maximum_displacement_native':max(displacement),'initial_layer_crossings':len(overlaps),
            'examples':[{'lower':p[lower[x]].tolist(),'upper':p[upper[y]].tolist()} for x,y in overlaps[:8]]})
        offset+=count
    return p,records


def closed_course(layer, tailored=False):
    """Concealed-join course with a constant-width developable rest cylinder.

    Avoids an invalid self-crossing end overlap and the varying circumferences
    of an annular bib. This is a sewn simulation panel, not automatic tying.
    """
    rows,cols=112,21
    p,f=course(layer,rows,cols,revised=3);grid=p.reshape(rows,cols,3)
    for i in range(rows):
        theta=math.tau*i/rows
        tilt=(-.65 if layer else .45) if tailored else (.45+.25*layer)
        grid[i,:,2]+=tilt*math.sin(theta)*max(0.,-math.cos(theta))
        if tailored:
            # Route the outer back course higher around the headfall, rather
            # than duplicating two low collars. Opposing front bias is a
            # construction choice; simulation supplies the folds.
            grid[i,:,2]+=(.15+.65*layer)*max(0.,math.cos(theta))**2
    lengths=np.linalg.norm(np.roll(grid,-1,axis=0)-grid,axis=2).sum(0)
    radius=float(np.median(lengths))/(math.tau)
    width=(.135 if tailored else .175)/.12292759120464325
    rest=np.array([(radius*math.sin(math.tau*i/rows),radius*math.cos(math.tau*i/rows),-width*j/(cols-1)) for i in range(rows) for j in range(cols)])
    pins={}
    for row in (28,84):
        for i in (row-1,row,row+1):
            center=16 if tailored else 5
            for j in (center-1,center,center+1):pins[i*cols+j]=1. if j==center else .6
    if tailored:
        # Concealed joined ends tuck at the rear, not at visible shoulders.
        # Support a short seam region rather than a lone peak-producing pin.
        for i in (110,111,0,1,2):
            for j in range(6,15):pins[i*cols+j]=.85 if 8<=j<=12 else .5
    return p,f,rest,pins


def radial_actor_fit(points, tree, start, scale):
    """Clear outer courses without collapsing their across-width sampling.

    Closest-point projection onto a shoulder mapped multiple cloth rows to
    the same surface location. Radial initial dressing preserves height and
    angular order; the exact actor, edge and self-intersection gates still
    apply afterwards. This is not an animated-frame correction.
    """
    from mathutils import Vector
    result=np.array(points,copy=True);maximum=0.
    for i in range(start,len(result)):
        q=Vector(result[i]*scale);origin=Vector((0,.30*scale,q.z))
        direction=q-origin;radius=direction.length;direction.normalize()
        ray=origin.copy();outer=0.
        for _ in range(64):
            hit,_,_,_=tree.ray_cast(ray,direction,2.)
            if hit is None:break
            outer=max(outer,(hit-origin).dot(direction));ray=hit+direction*1e-5
        else:raise ValueError('Actor radial query did not terminate')
        target=max(radius,outer+.005)
        for _ in range(60):
            candidate=origin+direction*target
            if tree.find_nearest(candidate)[3]>=.005-1e-7:break
            target+=.001
        else:raise ValueError('Radial actor clearance unresolved')
        maximum=max(maximum,target-radius)
        result[i]=np.array(candidate)/scale
    if maximum>.06:raise ValueError('Radial dressing exceeds six-centimetre reconstruction guard')
    return result,maximum


def strips(layer):
    rows,cols=113,21
    source,_=course(layer,rows=192,cols=2,revised=3)
    source=source.reshape(192,2,3)
    points=[];faces=[]
    for i in range(rows):
        u=-.035+1.07*i/(rows-1);theta=math.tau*u
        a=periodic_section(source[:,0],u);b=periodic_section(source[:,1],u)
        tangent=periodic_section(source.mean(1),u+.0001)-periodic_section(source.mean(1),u-.0001)
        normal=np.cross(tangent,b-a);normal/=np.linalg.norm(normal)
        tilt=(.45+.25*layer)*math.sin(theta)*max(0.,-math.cos(theta))
        # Helical overlap keeps the two rear ends at distinct heights and
        # depths. These are concealed tucks, not visible shoulder clips.
        tuck=(i/(rows-1)-.5)*.12
        for j in range(cols):
            v=j/(cols-1)
            q=a*(1-v)+b*v
            q[2]+=tilt+tuck
            q+=normal*(.07*math.sin(math.pi*v)*math.sin(4*math.pi*v+.4*math.sin(theta))+.025*(i/(rows-1)))
            points.append(q)
    for i in range(rows-1):
        for j in range(cols-1):faces.append((i*cols+j,(i+1)*cols+j,(i+1)*cols+j+1,i*cols+j+1))
    points=np.array(points);grid=points.reshape(rows,cols,3)
    # Rectangular fabric metric, unlike a permanently flared annular bib.
    length=max(np.linalg.norm(np.diff(grid[:,j],axis=0),axis=1).sum() for j in range(cols))
    width=max(np.linalg.norm(np.diff(grid[i],axis=0),axis=1).sum() for i in range(rows))*1.10
    rest=np.array([(length*i/(rows-1),width*j/(cols-1),0.) for i in range(rows) for j in range(cols)])
    pins={}
    for shoulder in (.25,.75):
        row=round((shoulder+.035)/1.07*(rows-1))
        for i in (row-1,row,row+1):
            for j in (4,5,6):pins[i*cols+j]=1. if j==5 else .6
    for i in (0,rows-1):
        for j in (4,5,6):pins[i*cols+j]=.8 if j==5 else .4
    return points,np.array(faces),rest,pins
