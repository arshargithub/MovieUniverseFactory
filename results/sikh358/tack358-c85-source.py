"""Fixed anatomical bridle on measured horse surface, not control-tail offsets."""
import math,json,importlib.util
from pathlib import Path

def smooth_path(anchors,steps=12):
    """Catmull-Rom interpolation, endpoints retained; local authored strap guides."""
    out=[]
    for i in range(len(anchors)-1):
        a,b,c,d=anchors[max(0,i-1)],anchors[i],anchors[i+1],anchors[min(len(anchors)-1,i+2)]
        for j in range(steps):
            t=j/steps
            out.append(tuple(.5*((2*b[k])+(-a[k]+c[k])*t+(2*a[k]-5*b[k]+4*c[k]-d[k])*t*t+(-a[k]+3*b[k]-3*c[k]+d[k])*t*t*t) for k in range(3)))
    return out+[tuple(anchors[-1])]

def run(bpy,out):
    from mathutils import Vector,Matrix
    from mathutils.bvhtree import BVHTree
    spec=importlib.util.spec_from_file_location('tack354',Path(__file__).with_name('nihang_tack354.py'));prior=importlib.util.module_from_spec(spec);spec.loader.exec_module(prior)
    sig=prior.action_signature(bpy);rig=bpy.data.objects['horse.rig'];horse=bpy.data.objects['horse'];leader=bpy.data.objects['MF coherent Nihang rig']
    if not leader.get('coat357') or rig.get('tack358'):raise ValueError('TACK358_PARENT')
    mat=rig.matrix_world.inverted()@horse.matrix_world
    verts=[mat@v.co for v in horse.data.vertices]
    # Restrict to external skin, excluding eye and mouth material surfaces.
    polys=[tuple(p.vertices) for p in horse.data.polygons if p.material_index==0 and all(verts[i].y<-1.22 and verts[i].z>1.68 for i in p.vertices)]
    tree=BVHTree.FromPolygons(verts,polys)
    if len(polys)<300:raise ValueError('TACK358_HEAD_SURFACE')
    def project(probe):
        hit,n,_,dist=tree.find_nearest(Vector(probe))
        if hit is None or dist>.11:raise ValueError('TACK358_UNSUPPORTED:'+str((probe,dist)))
        return hit+n*.005,n
    leather=bpy.data.materials.new('358 worn dark umber bridle leather');leather.use_nodes=True
    bs=leather.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.040,.018,.008,1);bs.inputs['Roughness'].default_value=.63
    noise=leather.node_tree.nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=165
    bump=leather.node_tree.nodes.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.12;bump.inputs['Distance'].default_value=.0003
    leather.node_tree.links.new(noise.outputs['Fac'],bump.inputs['Height']);leather.node_tree.links.new(bump.outputs[0],bs.inputs['Normal'])
    metal=bpy.data.materials.new('358 aged steel bit rings');metal.diffuse_color=(.13,.14,.14,1);metal.use_nodes=True
    bs=metal.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.13,.14,.14,1);bs.inputs['Metallic'].default_value=.82;bs.inputs['Roughness'].default_value=.38
    records=[]
    def mesh(name,points,faces,material):
        data=bpy.data.meshes.new(name);data.from_pydata(points,[],faces);data.update();obj=bpy.data.objects.new(name,data);bpy.context.scene.collection.objects.link(obj)
        obj.parent=rig;obj.matrix_parent_inverse=Matrix.Identity(4);obj.matrix_basis=Matrix.Identity(4)
        data.materials.append(material);group=obj.vertex_groups.new(name='DEF-head');group.add(list(range(len(points))),1,'REPLACE')
        mod=obj.modifiers.new('358 head surface owner','ARMATURE');mod.object=rig
        for p in data.polygons:p.use_smooth=True
        return obj
    def strap(name,probes,width,closed=False):
        routes=[project(p) for p in probes];points=[]
        for i,(p,n) in enumerate(routes):
            before=routes[(i-1)%len(routes)][0] if closed or i else p
            after=routes[(i+1)%len(routes)][0] if closed or i<len(routes)-1 else p
            cross=(after-before).normalized().cross(n).normalized()
            for side in (-1,1):points.append(p+cross*(width*.5*side))
        faces=[(2*i,2*i+1,2*((i+1)%len(routes))+1,2*((i+1)%len(routes))) for i in range(len(routes) if closed else len(routes)-1)]
        obj=mesh(name,points,faces,leather);sol=obj.modifiers.new('358 leather thickness','SOLIDIFY');sol.thickness=.0025;sol.offset=0
        bev=obj.modifiers.new('358 softened leather edge','BEVEL');bev.width=.001;bev.segments=2
        records.append(dict(name=name,centerline=[list(p) for p,n in routes],width=width));return obj
    # Measurements from83: eye center(y=-1.503,z=2.122); nose(-1.786,1.915),
    # jaw001 reaches(-1.743,1.814). Mouth ring is below/behind nostril,
    # not the head-control tail(-1.563,2.120).
    anchors={}
    for sign,label in ((-1,'R'),(1,'L')):
        cheek=[(sign*.105,-1.33,2.12),(sign*.125,-1.37,2.08),(sign*.110,-1.48,2.025),(sign*.085,-1.61,1.95),(sign*.070,-1.73,1.865)]
        strap('358 cheek leather '+label,smooth_path(cheek),.019)
        p,n=project((sign*.075,-1.73,1.865));center=p+n*.011;anchors[label]=list(center)
        points=[];faces=[]
        for i in range(40):
            a=math.tau*i/40
            radial=Vector((0,math.cos(a),math.sin(a)))
            for j in range(8):
                b=math.tau*j/8;points.append(center+radial*(.021+.0023*math.cos(b))+Vector((.0023*math.sin(b),0,0)))
        for i in range(40):
            for j in range(8):faces.append((i*8+j,((i+1)%40)*8+j,((i+1)%40)*8+(j+1)%8,i*8+(j+1)%8))
        mesh('358 bit ring '+label,points,faces,metal)
    # A centerline nearest-point query landed on an ear in84. Cast from above
    # at the deliberately behind-ear y section, preserving transverse order.
    crown=[]
    for x,y,z in smooth_path([(-.105,-1.33,2.12),(-.10,-1.28,2.14),(-.065,-1.24,2.16),(0,-1.24,2.16),(.065,-1.24,2.16),(.10,-1.28,2.14),(.105,-1.33,2.12)]):
        hit,n,_,_=tree.ray_cast(Vector((x,y,2.5)),Vector((0,0,-1)),.8)
        if hit is None:raise ValueError('TACK358_CROWN_SECTION')
        crown.append(hit+n*.005)
    # Endpoints share the cheek root, not independently guessed brow anchors.
    crown[0]=Vector((-.105,-1.33,2.12));crown[-1]=Vector((.105,-1.33,2.12))
    strap('358 crown behind ears',crown,.024)
    strap('358 brow above eyes',smooth_path([(-.105,-1.33,2.12),(-.12,-1.40,2.16),(-.08,-1.47,2.18),(0,-1.48,2.20),(.08,-1.47,2.18),(.12,-1.40,2.16),(.105,-1.33,2.12)]),.017)
    center=Vector((0,-1.67,1.96));axis=Vector((0,-.84,-.54));up=Vector((0,-.54,.84));probes=[]
    for i in range(80):
        a=math.tau*i/80;radial=Vector((math.sin(a),0,0))+up*math.cos(a)
        hit,n,_,distance=tree.ray_cast(center+radial*.35,-radial,.7)
        if hit is None:raise ValueError('TACK358_NOSEBAND_SECTION')
        probes.append(hit+n*.005)
    strap('358 supported noseband',probes,.022,True)
    hidden=[]
    for obj in bpy.data.objects:
        if obj.name.startswith(('horse cheek strap292','horse nose band292')):
            obj.hide_render=True;obj.hide_viewport=True;hidden.append(obj.name)
    rig['tack358']=1;rig['tack358_anchors']=json.dumps(anchors)
    bpy.context.view_layer.update()
    if prior.action_signature(bpy)!=sig:raise ValueError('TACK358_ACTION_DRIFT')
    report=dict(changed=True,source_preserved=True,action_signature=sig,actions_unchanged=True,anchors=anchors,head_skin_polygons=len(polys),straps=records,hidden_legacy=hidden,scope='Actual mesh-supported head-owned bridle; original reins intentionally await motion consumer. Static and dynamic visual checks required.')
    (out/'tack358.json').write_text(json.dumps(report,indent=2)+'\n');return report
