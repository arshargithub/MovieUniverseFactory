"""Typed distal-forelimb articulation on the frozen upstream rise, no mesh/landing edit."""
import importlib.util,json,math
from pathlib import Path
import numpy as np
FIELDS=('left_curl','right_curl','left_toe','right_toe')

def module(name):
 s=importlib.util.spec_from_file_location('crest372_'+name,Path(__file__).with_name(name+'.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def validate(edit):
 if not isinstance(edit,dict) or edit.get('target')!='mounted leader':raise ValueError('CREST372_TARGET')
 if edit.get('kind')=='mounted_crest372_contact':
  if set(edit)!={'kind','target'}:raise ValueError('CREST372_CONTACT_FIELDS')
  return edit
 if set(edit)!={'kind','target','anchors'} or edit['kind']!='mounted_crest372':raise ValueError('CREST372_FIELDS')
 a=edit['anchors']
 if not isinstance(a,list) or not 4<=len(a)<=12 or a[0].get('frame')!=315 or a[-1].get('frame')!=333:raise ValueError('CREST372_INTERVAL')
 previous=314
 for row in a:
  if set(row)!=set(FIELDS)|{'frame'} or type(row['frame']) is not int or not previous<row['frame']<=333:raise ValueError('CREST372_ANCHOR')
  previous=row['frame']
  for k in FIELDS:
   value=row[k];limit=1.15 if k.endswith('curl') else .3
   if type(value) not in (float,int) or not math.isfinite(value) or not 0<=value<=limit:raise ValueError('CREST372_BOUND:'+k)
 if any(a[0][k]!=0 for k in FIELDS):raise ValueError('CREST372_ENTRY_DELTA')
 return edit

def sample(a,f):
 # Same monotone cubic rule as prep367, generalized to the four distal channels.
 if f<=a[0]['frame']:return dict(a[0])
 if f>=a[-1]['frame']:return dict(a[-1])
 i=next(i for i in range(len(a)-1) if a[i]['frame']<=f<a[i+1]['frame']);xs=[x['frame'] for x in a];h=xs[i+1]-xs[i];t=(f-xs[i])/h;out={'frame':f}
 for k in FIELDS:
  ys=[x[k] for x in a];ds=[(ys[j+1]-ys[j])/(xs[j+1]-xs[j]) for j in range(len(a)-1)]
  def slope(j):
   if j==0:return ds[0]
   if j==len(a)-1:return ds[-1]
   if ds[j-1]*ds[j]<=0:return 0.
   x=xs[j]-xs[j-1];y=xs[j+1]-xs[j];w1=2*y+x;w2=y+2*x
   return (w1+w2)/(w1/ds[j-1]+w2/ds[j])
  out[k]=(2*t**3-3*t*t+1)*ys[i]+(t**3-2*t*t+t)*h*slope(i)+(-2*t**3+3*t*t)*ys[i+1]+(t**3-t*t)*h*slope(i+1)
 return out

def protected(bpy,frames):
 support=module('nihang_support');scene=support.select_production_scene(bpy);hr=bpy.data.objects['horse.rig'];root=bpy.data.objects['mounted leader']
 objects=sorted(set([hr,root,bpy.data.objects['HORSE hind support pivot'],bpy.data.objects['LEADER spear world contact owner']]+list(root.children_recursive)),key=lambda o:o.name)
 names=[n for n in hr.pose.bones.keys() if n in ('torso','hips','chest','neck','head') or n.startswith(('DEF-spine','DEF-neck','thigh_fk.','lower_leg_fk.','hind_foot_fk.','r_hoof.','upper_arm_fk.','forearm_fk.'))]
 result={}
 for f in frames:
  scene.frame_set(f);bpy.context.view_layer.update();v=[]
  for ob in objects:v.extend(q for row in ob.matrix_world for q in row)
  for n in names:v.extend(q for row in hr.pose.bones[n].matrix for q in row)
  result[f]=np.array(v)
 return result

def run(bpy,out,edit):
 validate(edit)
 if edit['kind']=='mounted_crest372_contact':return contact(bpy,out)
 from mathutils import Matrix,Vector,Quaternion
 apex=module('nihang_apex371');prep=module('nihang_prep367');support=module('nihang_support');motion=module('nihang_motion');scene=support.select_production_scene(bpy)
 if not scene.get('apex371') or scene.get('crest372'):raise ValueError('CREST372_SOURCE')
 before=prep.frozen(bpy);prefix=apex.prefix_states(bpy);tracks=apex.prefix_actions(bpy);fixed=protected(bpy,range(315,334));hr=bpy.data.objects['horse.rig']
 scene.frame_set(283);bpy.context.view_layer.update();basis=hr.matrix_world.to_quaternion();axis=basis@Vector((1,0,0));captured={}
 names=[name+'.'+s for s in ('L','R') for name in ('forefoot_fk','f_toe_fk','f_hoof')]
 for f in range(315,334):
  scene.frame_set(f);bpy.context.view_layer.update();captured[f]={n:(hr.matrix_world@hr.pose.bones[n].matrix).copy() for n in names}
 # Preserve original scalar endpoint before authoring; no new314 pose.
 for fc in motion.curves(hr):
  if any(fc.data_path.startswith('pose.bones["'+n+'"]') for n in names):
   k=fc.keyframe_points.insert(314,float(fc.evaluate(314)),options={'FAST'});k.interpolation='LINEAR';fc.update()
 def set_world(name,world,f):
  b=hr.pose.bones[name];b.rotation_mode='QUATERNION';b.matrix=hr.matrix_world.inverted()@world
  for path in ('location','rotation_quaternion','scale'):b.keyframe_insert(path,frame=f)
  bpy.context.view_layer.update()
 rows=[]
 for f in range(315,334):
  scene.frame_set(f);bpy.context.view_layer.update();row=sample(edit['anchors'],f);e=[]
  for side,p in [('L','left'),('R','right')]:
   source=captured[f];cannon=source['forefoot_fk.'+side];wrist=cannon.translation
   q=Quaternion(axis,row[p+'_curl']);rotate=Matrix.Translation(wrist)@q.to_matrix().to_4x4()@Matrix.Translation(-wrist)
   set_world('forefoot_fk.'+side,rotate@cannon,f)
   fetlock=(rotate@source['f_toe_fk.'+side]).translation
   toe_q=Matrix.Translation(fetlock)@Quaternion(axis,row[p+'_toe']).to_matrix().to_4x4()@Matrix.Translation(-fetlock)
   for n in ('f_toe_fk.','f_hoof.'):set_world(n+side,toe_q@rotate@source[n+side],f)
   actual=hr.matrix_world@hr.pose.bones['forefoot_fk.'+side].matrix
   err=(actual.translation-wrist).length
   oldlength=(cannon.to_3x3().col[1]*hr.data.bones['forefoot_fk.'+side].length).length
   newlength=(actual.to_3x3().col[1]*hr.data.bones['forefoot_fk.'+side].length).length
   if err>1e-5 or abs(oldlength-newlength)>1e-5:raise ValueError('CREST372_SEGMENT_CHANGED')
   v=basis.inverted()@actual.to_3x3().col[1].normalized()
   e.append(dict(side=side,wrist=list(wrist),fetlock=list(fetlock),lower_direction=list(v),angle_from_down=math.atan2(v.y,-v.z),wrist_error=err,length_error=abs(newlength-oldlength),visible_hoof=list(hr.matrix_world@hr.pose.bones['DEF-f_hoof.'+side].head)))
  rows.append(dict(frame=f,channels=row,limbs=e))
 for fc in motion.curves(hr):
  if any(fc.data_path.startswith('pose.bones["'+n+'"]') for n in names):
   for k in fc.keyframe_points:
    if 315<=k.co.x<=333:k.interpolation='LINEAR'
   fc.update()
 prefix_after=apex.prefix_states(bpy);fixed_after=protected(bpy,range(315,334));pe=max(float(np.max(np.abs(prefix[f]-prefix_after[f]))) for f in prefix);fe=max(float(np.max(np.abs(fixed[f]-fixed_after[f]))) for f in fixed);te=max(apex.check_prefix_actions(bpy,tracks,raise_on_error=False).values(),default=0.)
 report=dict(frames=rows,accepted_prefix_error=pe,accepted_prefix_track_error=te,frozen_rise_rider_support_error=fe,geometry_unchanged=prep.frozen(bpy)==before,scope='Only315..333distalforelimb authoring, no upperbody/stance/rider/mesh/landing change. Contact/visual/AV validation separate.')
 (out/'crest372.json').write_text(json.dumps(report,indent=2)+'\n')
 if pe>1e-5 or te>1e-6 or fe>1e-5 or not report['geometry_unchanged']:raise ValueError('CREST372_PRESERVATION')
 scene['crest372']=1;scene['crest372_contact_requires_recheck']=True;scene.frame_set(333)
 return dict(report='crest372.json',frames=19,accepted_preparation_preserved=True)

def contact(bpy,out):
 from mathutils.bvhtree import BVHTree
 support=module('nihang_support');prep=module('nihang_prep367');tack=module('nihang_tack354');scene=support.select_production_scene(bpy)
 if not scene.get('crest372'):raise ValueError('CREST372_CONTACT_SOURCE')
 pad=bpy.data.objects['371 apex contact-solved saddle cloth'];horse=bpy.data.objects['horse'];before=prep.frozen(bpy);actions=tack.action_signature(bpy);saved=scene.frame_current
 levels=[(m,m.levels) for m in horse.modifiers if m.type=='SUBSURF'];rows=[]
 try:
  for m,_ in levels:m.levels=m.render_levels
  for f in range(315,334):
   scene.frame_set(f);bpy.context.view_layer.update();dg=bpy.context.evaluated_depsgraph_get();he=horse.evaluated_get(dg);pe=pad.evaluated_get(dg);hm=he.to_mesh();pm=pe.to_mesh()
   try:
    hv=[he.matrix_world@v.co for v in hm.vertices];tree=BVHTree.FromPolygons(hv,[tuple(p.vertices) for p in hm.polygons],all_triangles=False);pv=[pe.matrix_world@v.co for v in pm.vertices];pm.calc_loop_triangles();points=pv+[sum((pv[i] for i in tri.vertices),pv[0]*0)/3 for tri in pm.loop_triangles];gaps=[]
    for point in points:
     q,n,face,distance=tree.find_nearest(point)
     if q is None:raise ValueError('CREST372_NO_CONTACT_SURFACE')
     gaps.append(float((point-q).dot(n)))
    rows.append(dict(frame=f,samples=len(gaps),min_gap=min(gaps),below_2mm=sum(x<.002 for x in gaps)))
    (out/'crest372-contact-progress.json').write_text(json.dumps(rows,indent=2)+'\n')
    if min(gaps)<.002:raise ValueError('CREST372_CONTACT_FAILURE:'+str(f))
   finally:he.to_mesh_clear();pe.to_mesh_clear()
 finally:
  for m,value in levels:m.levels=value
  scene.frame_set(saved);bpy.context.view_layer.update()
 if prep.frozen(bpy)!=before or tack.action_signature(bpy)!=actions:raise ValueError('CREST372_CONTACT_MUTATED')
 scene['crest372_contact_requires_recheck']=False
 (out/'crest372-contact.json').write_text(json.dumps(dict(rows=rows,original_geometry_actions_unchanged=True,scope='All19integerframes, finalthickenedvertices andtrianglecentres; same71cache revalidated, no clothsimulation/subframeclaim.'),indent=2)+'\n')
 return dict(report='crest372-contact.json',frames=19)
