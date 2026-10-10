"""Scoped fixed mane-guide clearance around moving hand proxies.

This is a blocking/contact aid, not a finished free-mane dynamics system.
Measure the full existing trajectory first, then apply one time-stable guide
offset. Never project different hair points against each hand every frame.
"""
import numpy as np
def offsets(centers,hands):
 """Input F x G x S x3 centers and F x2x3 hand centers, same actor frame."""
 if centers.ndim!=4 or centers.shape[2:]!=(12,3) or hands.shape!=(len(centers),2,3) or not np.isfinite(centers).all() or not np.isfinite(hands).all():raise ValueError('Unexpected fixed guide/hand domain')
 shift=np.zeros(centers.shape[1:3]);before=0
 for i,q in enumerate(centers):
  for h in hands[i]:
   side=1 if h[0]>0 else -1
   yz=((q[:,:,1]-h[1])/1.05)**2+((q[:,:,2]-h[2])/.9)**2
   half=.8*np.sqrt(np.maximum(0,1-yz));inside=(yz<1)&(abs(q[:,:,0]-h[0])<half)
   before+=int(inside.sum());want=(h[0]+side*half-q[:,:,0])*inside
   shift=np.where(abs(want)>abs(shift),want,shift)
 shift[:,0]=0
 # Expand and fair along each strand; roots stay fixed, no framewise chatter.
 for _ in range(3):
  adjacent=(np.roll(shift,1,axis=1)+shift+np.roll(shift,-1,axis=1))/3
  adjacent[:,0]=0;adjacent[:,-1]=shift[:,-1]
  shift=np.where(abs(adjacent)>abs(shift),adjacent,shift)
 if abs(shift).max()>2.5:raise ValueError('Contact correction too large for blocking')
 after=0
 for i,q in enumerate(centers):
  for h in hands[i]:
   yz=((q[:,:,1]-h[1])/1.05)**2+((q[:,:,2]-h[2])/.9)**2
   half=.8*np.sqrt(np.maximum(0,1-yz));after+=int(((yz<1)&(abs(q[:,:,0]+shift-h[0])<half-1e-5)).sum())
 return shift,{'hand_proxy_intersections_before':before,'hand_proxy_intersections_after':after,'max_lateral_offset_native':float(abs(shift).max()),'affected_guides':int(np.any(shift!=0,axis=1).sum())}

def apply(scene,out,start,count):
 import bpy
 from entrance189_groom import read_mdd,write_mdd,attach_cache
 from wardrobe_motion178_controls import render_geometry_paused
 ob=bpy.data.objects['MF188_flowing_mane'];rig=bpy.data.objects['MF_body156_fit_rig'];m=next(m for m in ob.modifiers if m.type=='MESH_CACHE');a=read_mdd(bpy.path.abspath(m.filepath));hands=[]
 if len(a)!=count or a.shape[1]!=226152:raise ValueError('Pinned mane topology/clock differs')
 with render_geometry_paused():
  for f in range(start,start+count):
   scene.frame_set(f);bpy.context.view_layer.update();world=ob.parent.matrix_world@ob.matrix_parent_inverse@ob.matrix_basis if ob.parent else ob.matrix_world;inv=world.inverted();row=[]
   for side in ('L','R'):
    bone=rig.pose.bones['hand.'+side];mat=inv@rig.matrix_world@bone.matrix;row.append(np.array(mat.translation)+np.array(mat.col[1][:3])*.45)
   hands.append(row)
 centers=np.asarray(a).reshape(count,6282,12,3,3).mean(3);shift,report=offsets(centers,np.array(hands));del centers
 def rows():
  for row in a:
   q=np.array(row,copy=True).reshape(6282,12,3,3);q[:,:,:,0]+=shift[:,:,None];yield q.reshape(-1,3)
 path=out/'mane-contact.mdd';write_mdd(path,count,226152,rows());attach_cache(ob,path,start)
 report['method']='One fixed lateral guide correction measured across full motion; conservative hand proxy, not exact skin collision or final mane animation'
 return report
