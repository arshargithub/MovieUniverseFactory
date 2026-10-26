from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
q=np.load('.runtime/factory-native/sikh380-appearance-c146-repair/chest380.npz');g=np.load('.runtime/factory-native/sikh374-appearance-c124-inspect/horse-form374.npz');tri=g['triangles'];rest=g['shape'][0]
def draw(p,az):
 # Orthographic scientific surface diagnostic, not native film appearance.
 c,s=np.cos(az),np.sin(az);R=np.array([[c,s,0],[-s,c,0],[0,0,1.]])
 v=p@R.T;xy=v[:,[0,2]];depth=-v[:,1];norm=np.cross(v[tri[:,1]]-v[tri[:,0]],v[tri[:,2]]-v[tri[:,0]]);norm/=np.maximum(np.linalg.norm(norm,axis=1)[:,None],1e-8)
 pix=(xy-np.array([-.6,.8]))*450;pix[:,1]=500-pix[:,1];im=Image.new('RGB',(550,550),(225,225,225));d=ImageDraw.Draw(im)
 for t in np.argsort(depth[tri].mean(1)):
  ids=tri[t]
  if (rest[ids,2].max()<.83) or (rest[ids,1].min()>.25):continue
  shade=np.clip(.5+.45*np.dot(norm[t],np.array([-.3,-.8,.5])),.08,1);col=tuple(int(x*shade) for x in [190,155,113]);d.polygon([tuple(x) for x in pix[ids]],fill=col)
 return im
out=Image.new('RGB',(1650,1100),'white')
for row,f in enumerate([367,339]):
 for col,az in enumerate([0,np.pi/4,np.pi/2]):out.paste(draw(q['posed_'+str(f)],az),(col*550,row*550))
out.save('results/sikh381/geometry-study.png')
