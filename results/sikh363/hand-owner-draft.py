"""Reviewed read-only hand-owner audit, install only after active reviews."""
def hand_owner(bpy,rig):
 from mathutils import Vector
 from collections import Counter
 body=bpy.data.objects['MF coherent Nihang body'];root=bpy.data.objects['mounted leader'];target=rig.matrix_world@rig.pose.bones['finger3-1.R'].head
 close=[]
 for ob in root.children_recursive:
  if ob.type!='MESH' or ob.hide_render:continue
  corners=[ob.matrix_world@Vector(p) for p in ob.bound_box];lo=Vector(tuple(min(p[i] for p in corners) for i in range(3)));hi=Vector(tuple(max(p[i] for p in corners) for i in range(3)))
  distance=sum(max(lo[i]-target[i],target[i]-hi[i],0)**2 for i in range(3))**.5
  if distance>.15:continue
  close.append(dict(name=ob.name,parent=ob.parent.name if ob.parent else None,vertices=len(ob.data.vertices),distance=distance,modifiers=[dict(name=m.name,type=m.type,viewport=m.show_viewport,render=m.show_render,object=getattr(getattr(m,'object',None),'name',None)) for m in ob.modifiers]))
 groups=Counter();sample=[]
 for v in body.data.vertices:
  row=[(body.vertex_groups[g.group].name,g.weight) for g in v.groups]
  if any(n.endswith('.R') and n.startswith(('finger','wrist','metacarpal')) and w>.01 for n,w in row):
   for n,w in row:groups[n]+=w
   if len(sample)<30:sample.append(dict(index=v.index,rest=list(v.co),weights=row))
 return dict(nearby_visible=close,hand_group_weight_totals=dict(groups),sample=sample,shape_keys=[dict(name=k.name,value=k.value) for k in body.data.shape_keys.key_blocks] if body.data.shape_keys else [],bone_deform={n:dict(deform=b.use_deform,parent=b.parent.name if b.parent else None) for n,b in rig.data.bones.items() if n.endswith('.R') and n.startswith(('finger','wrist','metacarpal'))})
