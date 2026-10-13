"""Closed grounded camp dressing and second mounted depth layer for245."""
import math
import numpy as np

def build(scene,kind,camp_layout='original'):
    import bpy
    from mathutils import Vector,Matrix
    from mathutils.bvhtree import BVHTree
    if kind=='opening':return {'scope':'No checkpoint in opening source; route owns fixed geography'}
    land=bpy.data.objects['AS_valley_landform'];land.data.calc_loop_triangles()
    tree=BVHTree.FromPolygons([tuple(land.matrix_world@v.co) for v in land.data.vertices],
        [tuple(t.vertices) for t in land.data.loop_triangles],all_triangles=True)
    def ground(x,y):
        hit=tree.ray_cast(Vector((x,y,1000)),Vector((0,0,-1)),4000)
        if hit[0] is None:raise ValueError('Camp unsupported')
        return hit[0].z
    placements=[]
    # Current218 inherits207-threat10, not206's superseded forward anchors.
    for j,(nx,ny,oldx,oldy) in enumerate(((-29,-610,-32,-335),(34,-665,30,-400))):
        donors=[o for o in list(scene.objects) if o.name.startswith(f'MF206_guard{j}_') and o.type=='MESH']
        if not donors:raise ValueError('Missing accepted mounted silhouette')
        delta=Vector((nx-oldx,ny-oldy,ground(nx,ny)-ground(oldx,oldy)))
        for donor in donors:
            ob=donor.copy();ob.data=donor.data.copy();ob.name=donor.name.replace(f'MF206_guard{j}_',f'MF245_guard{j+2}_')
            scene.collection.objects.link(ob);world=donor.matrix_world.copy();ob.parent=None;ob.animation_data_clear();ob.matrix_world=Matrix.Translation(delta)@world
        placements.append({'pair_member':j,'anchor':[nx,ny,ground(nx,ny)],'objects':len(donors)})
    def material(name,color):
        m=bpy.data.materials.new('MF245 '+name);m.use_nodes=True
        n=m.node_tree.nodes;p=n.get('Principled BSDF');p.inputs['Roughness'].default_value=.91
        tex=n.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=3.5;tex.inputs['Detail'].default_value=2
        ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].position=.18;ramp.color_ramp.elements[1].position=.8
        ramp.color_ramp.elements[0].color=(*[v*.65 for v in color],1);ramp.color_ramp.elements[1].color=(*color,1)
        m.node_tree.links.new(tex.outputs['Fac'],ramp.inputs['Fac']);m.node_tree.links.new(ramp.outputs['Color'],p.inputs['Base Color'])
        return m
    canvas=material('dust worn camp canvas',(.38,.29,.17));seam=material('canvas fold shadows',(.15,.105,.058))
    wood=material('camp poles and crates',(.10,.065,.029));rope=material('hemp guy lines',(.31,.24,.13))
    def mesh(name,v,f,m):
        me=bpy.data.meshes.new(name);me.from_pydata(v,[],f);me.update();ob=bpy.data.objects.new('MF245_'+name,me);scene.collection.objects.link(ob);me.materials.append(m);return ob
    def bar(name,a,b,r,m):
        a,b=Vector(a),Vector(b);bpy.ops.mesh.primitive_cone_add(vertices=8,radius1=r,radius2=r,depth=(b-a).length,location=(a+b)/2)
        o=bpy.context.object;o.name='MF245_'+name;o.rotation_euler=(b-a).to_track_quat('Z','Y').to_euler();o.data.materials.append(m);return o
    camps=[]
    layouts={'original':((-77,-850,24,27,27,-.18),(76,-900,21,25,24,.22)),
             'visible03':((-120,-650,30,32,34,-.25),(130,-720,30,32,34,.25))}
    if camp_layout not in layouts:raise ValueError('Closed camp layout')
    for j,(cx,cy,w,d,h,ang) in enumerate(layouts[camp_layout]):
        z=ground(cx,cy);c,s=math.cos(ang),math.sin(ang)
        def p(x,y,zz):return (cx+c*x-s*y,cy+s*x+c*y,z+zz)
        # A-frame ridge, sagging canvas roof and low side walls. Rounded micro
        # folds are subordinate to a readable large tent silhouette.
        for side in (-1,1):
            v=[];f=[]
            for iy in range(13):
                yy=-d+2*d*iy/12
                for ix in range(9):
                    t=ix/8;x=side*w*t
                    zz=h-(h-5)*t-1.1*math.sin(math.pi*t)+.25*math.sin(iy*1.7+ix*.9)*math.sin(math.pi*t)
                    v.append(p(x,yy,zz))
            for iy in range(12):
                for ix in range(8):a=iy*9+ix;f.append((a,a+1,a+10,a+9))
            mesh(f'camp{j}_roof{side}',v,f,canvas)
            mesh(f'camp{j}_wall{side}',[p(side*w,-d,0),p(side*w,d,0),p(side*w,d,5),p(side*w,-d,5)],[(0,1,2,3)],canvas)
            for yy in (-d,d):
                wx,wy,_=p(side*(w+13),yy+(-8 if yy<0 else 8),0);g=ground(wx,wy)
                bar(f'camp{j}_guy',p(side*w,yy,5),(wx,wy,g+.4),.15,rope)
        # Split doorway flaps leave a dark interior opening, not a solid triangle.
        mesh(f'camp{j}_door_left',[p(-w,-d,0),p(-w,-d,5),p(0,-d,h),p(-4,-d,0)],[(0,1,2,3)],canvas)
        mesh(f'camp{j}_door_right',[p(4,-d,0),p(0,-d,h),p(w,-d,5),p(w,-d,0)],[(0,1,2,3)],canvas)
        mesh(f'camp{j}_rear',[p(-w,d,0),p(-w,d,5),p(0,d,h),p(w,d,5),p(w,d,0)],[(0,1,2,3,4)],canvas)
        for yy in (-d,d):bar(f'camp{j}_ridgepole',p(0,yy,0),p(0,yy,h+1.5),.48,wood)
        bar(f'camp{j}_ridgeseam',p(0,-d,h+.08),p(0,d,h+.08),.2,seam)
        for k in range(3):
            x,y,_=p(w+8+k*5,d-9,0);gz=ground(x,y)
            bpy.ops.mesh.primitive_cube_add(size=1,location=(x,y,gz+2.2));o=bpy.context.object;o.name=f'MF245_camp{j}_supply{k}';o.scale=(5,6,4.4);o.data.materials.append(wood)
        camps.append({'anchor':[cx,cy,z],'width':2*w,'depth':2*d,'height':h})
    return {'additional_mounted':placements,'camps':camps,'grounded_on':'AS_valley_landform','new_hero_assets':False}
