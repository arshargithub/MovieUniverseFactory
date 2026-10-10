"""Single traversable ledge and lower checkpoint road for205."""
import numpy as np
from entrance205_motion import smooth


def fields(xy, route):
    points=np.asarray(xy,float)
    centers=route['position'][::8]
    heading=route['heading'][::8]
    grade=route['grade'][::8]
    forward=np.column_stack((np.sin(heading),-np.cos(heading)))
    centers=np.vstack((centers[0]+np.r_[forward[0]*-25,0],centers,
                       centers[-1]+np.r_[forward[-1]*45,grade[-1]*45]))
    forward=np.vstack((forward[0],forward,forward[-1]))
    grade=np.r_[grade[0],grade,grade[-1]]
    results=[];roads=[]
    for start in range(0,len(points),1024):
        p=points[start:start+1024]
        ids=((p[:,None,:]-centers[None,:,:2])**2).sum(2).argmin(1)
        delta=p-centers[ids,:2]
        along=(delta*forward[ids]).sum(1)
        cross=delta[:,0]*(-forward[ids,1])+delta[:,1]*forward[ids,0]
        z=centers[ids,2]+along*grade[ids]
        distance=abs(cross)
        # Narrow, irregular rock shelf rather than a second built road.
        # The turn has room to gather; the steep escape has ~2m support.
        steep=smooth(grade[ids]/.35)
        width=2.2*(1-steep)+(1.05+.12*np.sin(centers[ids,1]*1.1))*steep
        outside=smooth((cross-width)/(4.5-3.0*steep))
        inside=smooth((-cross-width)/5.)
        terrain=z*(1-outside)+inside*(2.4+.9*np.maximum(-cross-width,0)+.5*np.sin(p[:,1]/5))
        # Broken bedrock relief outside the traversed support envelope. The
        # previous perfectly swept bank read as a built channel, not scree.
        rock=(.55*np.sin(.63*p[:,0]+.31*p[:,1])
              +.32*np.sin(1.71*p[:,0]-.83*p[:,1])
              +.14*np.sin(3.9*p[:,0]+2.73*p[:,1]))
        terrain+=steep*smooth((-cross-width)/2.0)*rock
        terrain+=outside*(.45*np.sin(p[:,1]/8)+.3*np.cos(p[:,0]/6))
        terrain=np.maximum(terrain,-.6)
        main=smooth((abs(p[:,0])-2.8)/3.5)
        terrain*=main
        terrain=np.where(distance<=width,z,terrain)
        terrain*=smooth((12-p[:,1])/12)
        results.extend(terrain);roads.extend(np.minimum(abs(p[:,0]),distance))
    return np.array(results),np.array(roads)
