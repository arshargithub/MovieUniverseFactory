"""Geographically placed distant threat; no new hero characters or uniforms."""
import json,math
import numpy as np
import wardrobe_motion178 as base
CHECKPOINT_Y=-900.

def build(scene):
 import bpy
 from mathutils import Vector
 from mathutils.bvhtree import BVHTree
 for ob in list(scene.objects):
  if ob.name.startswith(('MF204_guard','MF190_provisional_timber_barrier')):bpy.data.objects.remove(ob,do_unlink=True)
 land=bpy.data.objects['AS_valley_landform'];land.data.calc_loop_triangles()
 tree=BVHTree.FromPolygons([tuple(land.matrix_world@v.co) for v in land.data.vertices],[tuple(t.vertices) for t in land.data.loop_triangles],all_triangles=True)
 def ground(x,y):
  hit=tree.ray_cast(Vector((x,y,1000)),Vector((0,0,-1)),4000)
  if hit[0] is None:raise ValueError('Checkpoint outside grounded scenery')
  return hit[0].z
 def mat(name,color):
  m=bpy.data.materials.new(name);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Roughness'].default_value=.86;return m
 wood=mat('206 weathered checkpoint dark timber',(.075,.051,.028));stone=mat('206 ochre checkpoint masonry',(.29,.23,.145));coat=mat('206 anonymous mounted coat',(.065,.082,.067));leather=mat('206 checkpoint leather',(.035,.022,.013));skin=mat('206 distant face',(.25,.13,.064));horse_m=mat('206 guard bay coat',(.125,.058,.025))
 def ell(name,p,s,m):
  bpy.ops.mesh.primitive_uv_sphere_add(segments=12,ring_count=8,location=p);o=bpy.context.object;o.name='MF206_'+name;o.scale=s;o.data.materials.append(m);return o
 def bar(name,a,b,r,m,r2=None):
  a,b=Vector(a),Vector(b);bpy.ops.mesh.primitive_cone_add(vertices=10,radius1=r,radius2=r if r2 is None else r2,depth=(b-a).length,location=(a+b)/2);o=bpy.context.object;o.name='MF206_'+name;o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler();o.data.materials.append(m);return o
 z=ground(0,CHECKPOINT_Y)
 for x in (-27,27):
  bar('checkpoint_post',(x,CHECKPOINT_Y,z),(x,CHECKPOINT_Y,z+19),1.15,wood)
  bar('checkpoint_brace',(x,CHECKPOINT_Y+11,z),(x,CHECKPOINT_Y,z+14),.7,wood)
 for h in (6,13):bar('checkpoint_rail',(-28,CHECKPOINT_Y,z+h),(28,CHECKPOINT_Y,z+h),.8,wood)
 rng=np.random.default_rng(206)
 for side in (-1,1):
  for layer in range(3):
   for j in range(5):
    x=side*(31+5*j);y=CHECKPOINT_Y+rng.uniform(-1,1);g=ground(x,y)
    ell('checkpoint_stone',(x,y,g+1.4+layer*2.4),(3.1,3.6,1.6),stone)
 src=base.BASE/'entrance206-guard04';r=json.loads((src/'result.json').read_text())
 if base.digest(src/'horse.npz')!=r['geometry_sha256']:raise ValueError('Guard source changed')
 geometry=np.load(src/'horse.npz');placements=[]
 for j,(x,y,angle) in enumerate(((-24,CHECKPOINT_Y+24,math.pi-.32),(23,CHECKPOINT_Y+29,math.pi+.25))):
  z=ground(x,y);R=np.array([[math.cos(angle),-math.sin(angle),0],[math.sin(angle),math.cos(angle),0],[0,0,1]])
  def p(v):return np.array([x,y,z])+8.3*(R@np.asarray(v))
  for k,item in enumerate(r['objects']):
   if item['name']=='Full Bushy Flowing Horse Tail':continue
   v=(geometry[f'v{k}']-[0,2.52,-.00167655])@R.T*8.3+[x,y,z]
   me=bpy.data.meshes.new('206 standing guard '+item['name']);me.from_pydata(v.tolist(),[],geometry[f'f{k}'].tolist());me.update()
   o=bpy.data.objects.new(f'MF206_guard{j}_{item["name"]}',me);scene.collection.objects.link(o);me.materials.append(horse_m if item['name']=='horse' else leather)
   for poly in me.polygons:poly.use_smooth=True
  def e(name,v,s,m):
   o=ell(f'guard{j}_{name}',p(v),np.array(s)*8.3,m);o.rotation_euler.z=angle;return o
  def b(name,a,c,r,m):return bar(f'guard{j}_{name}',p(a),p(c),r*8.3,m,r*.85*8.3)
  e('coat',(0,0,1.99),(.22,.16,.39),coat);e('head',(0,-.03,2.51),(.105,.10,.145),skin);e('cap',(0,-.02,2.64),(.12,.115,.06),coat)
  for s in (-1,1):
   b('thigh',(s*.16,.03,1.68),(s*.36,-.34,1.35),.095,coat);b('boot',(s*.36,-.34,1.35),(s*.39,-.19,.91),.069,leather)
   b('upperarm',(s*.19,0,2.19),(s*.27,-.15,1.96),.067,coat);b('forearm',(s*.27,-.15,1.96),(s*.12,-.35,1.9),.055,coat)
   e('hand',(s*.12,-.35,1.9),(.05,.045,.065),skin);b('rein',(s*.12,-.35,1.9),(s*.11,-1.0,1.7),.009,leather)
  b('slung_equipment',(.24,.16,1.7),(.25,.10,2.72),.025,wood)
  # Distant mane and hanging tail follow the actual rest horse, not its gallop cache.
  for k in range(12):
   a=k/11;b('mane',(0,-.45-.55*a,1.57+.37*a),(.025,-.42-.55*a,1.40+.35*a),.027,leather)
  b('tail',(0,.88,1.53),(0,1.13,.48),.07,leather)
  placements.append(dict(x=x,y=y,ground=z,horse_height_m=2.087,rider_head_m=2.79))
 return dict(checkpoint=[0,CHECKPOINT_Y,z],distance_from_route_start_m=abs(CHECKPOINT_Y-.2)/8.3,mounted_guards=placements,source=r['source_sha256'],scope='Anonymous distant threat silhouettes; not hero rigs or established faction costume')

def camera(scene):
 import bpy
 from mathutils import Vector
 from wardrobe_motion178_controls import render_geometry_paused
 from entrance205_motion import sample
 rig=bpy.data.objects['MF_body156_fit_rig'];cam=scene.camera
 cam.animation_data.action=cam.animation_data.action.copy();cam.data.animation_data.action=cam.data.animation_data.action.copy();rows=[]
 with render_geometry_paused():
  for f in range(361,391):
   scene.frame_set(f);bpy.context.view_layer.update();head=np.array((rig.matrix_world@rig.pose.bones['MF185_head'].matrix).translation)
   y=sample((f-361)/24)['heading'];forward=np.array([np.sin(y),-np.cos(y),0]);out=np.array([np.cos(y),np.sin(y),0])
   from entrance205_scene import FLOOR
   escape=FLOOR+8.3*sample(4.)['position'];threat=np.array([0.,CHECKPOINT_Y,-10.])
   a=np.arctan2(escape[0]-head[0],-(escape[1]-head[1]));b=np.arctan2(threat[0]-head[0],-(threat[1]-head[1]));mid=(a+b)*.5
   # Fit the two real directions, not two nominal points at the same depth.
   # Slightly elevated shoulder coverage leaves the threat above her head.
   offset=-10*np.tan(mid+np.arctan(.4*20.25/20.))
   loc=head-forward*10+np.array([offset,0,4.5]);target=head+np.array([np.sin(mid)*500,-np.cos(mid)*500,-115.])
   cam.location=Vector(loc);cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=20
   cam.keyframe_insert('location',frame=f);cam.keyframe_insert('rotation_euler',frame=f);cam.data.keyframe_insert('lens',frame=f)
   rows.append(dict(frame=f,location=loc.tolist(),target=target.tolist(),lens=20))
  # Establish the farther checkpoint below before the admitted face-first
  # arc. A changed world target cannot inherit the old66m background framing.
  from entrance205_face_arc import face_camera
  from entrance205_scene import FLOOR
  from entrance205_motion import smooth
  for f in range(472,518):
   scene.frame_set(f);bpy.context.view_layer.update();head=np.array((rig.matrix_world@rig.pose.bones['MF185_head'].matrix).translation);t=(f-361)/24
   loc,target,lens=face_camera(t,(head-FLOOR)/8.3);loc=FLOOR+loc*8.3;target=FLOOR+target*8.3
   loc+=np.array([4.5,4.,1.5])*(1-float(smooth((t-5.05)/1.45)))
   cam.location=Vector(loc);cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.lens=lens
   cam.keyframe_insert('location',frame=f);cam.keyframe_insert('rotation_euler',frame=f);cam.data.keyframe_insert('lens',frame=f)
   rows.append(dict(frame=f,location=loc.tolist(),target=target.tolist(),lens=lens,reason='Farther checkpoint establishment then retained face arc'))
 return rows
