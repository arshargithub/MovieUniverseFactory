"""Deterministic authored tail and contact-driven local dust for the fixed demo."""
import math,random
import bpy
from mathutils import Vector

def tail(scene,horse,helper,mf,motion):
    for modifier in bpy.data.objects['horse'].modifiers:
        if modifier.type=='PARTICLE_SYSTEM' and modifier.particle_system.name=='horse.tail':modifier.show_render=modifier.show_viewport=False
    data=bpy.data.curves.new('flowing tail groom','CURVE');data.dimensions='3D';data.bevel_depth=.0015;data.bevel_resolution=1;data.resolution_u=3
    obj=bpy.data.objects.new('flowing tail groom',data);scene.collection.objects.link(obj)
    material=helper._material('tail dark chestnut',(.065,.020,.009),.72);data.materials.append(material)
    rng=random.Random(31415);base=[];parameters=[]
    for strand in range(700):
        angle=rng.random()*math.tau;r=math.sqrt(rng.random());length=.90+.13*rng.random();phase=rng.random()*math.tau
        spline=data.splines.new('NURBS');spline.points.add(7);spline.order_u=4;spline.use_endpoint_u=True;spline.resolution_u=3
        for i,point in enumerate(spline.points):
            u=i/7;spread=.022+.068*math.sin(math.pi*u)**.65
            x=math.cos(angle)*r*spread+.006*math.sin(phase+u*3)*u
            y=length*.88*u
            z=-length*(.12*u+.57*u*u)+math.sin(angle)*r*spread*.7
            point.co=(x,y,z,1);point.radius=(.45+.55*math.sin(math.pi*u))*(1-u)**.6+.025
            base.append(Vector((x,y,z)));parameters.append(u)
    obj.shape_key_add(name='Basis')
    for name,quadrature in (('flow sine',False),('flow cosine',True)):
        key=obj.shape_key_add(name=name);key.slider_min=-1;key.slider_max=1
        for i,(p,u) in enumerate(zip(base,parameters)):
            lag=2.1*u;wave=-math.sin(lag) if quadrature else math.cos(lag)
            key.data[i].co=p+Vector((.13*u**1.7*wave,.025*u*u*wave,.10*u**1.7*(-math.sin(lag+.8) if quadrature else math.cos(lag+.8))))
        for frame in range(61):
            theta=math.tau*motion.FREQUENCY*frame/24
            key.value=math.cos(theta) if quadrature else math.sin(theta);key.keyframe_insert('value',frame=frame)
    anchor=bpy.data.objects.new('tail root anchor',None);scene.collection.objects.link(anchor);obj.parent=anchor
    for frame in range(61):
        helper._refresh(scene,mf,frame);anchor.location=horse.matrix_world@horse.pose.bones['DEF-tail.001'].head;anchor.keyframe_insert('location',frame=frame)
    return {'object':obj.name,'strands':700,'shape_keys':2,'root_bone':'DEF-tail.001','seed':31415,'policy':'Authored smooth correlated strand flow, bounded tips; original groom disabled only in disposable copy. Not physical hair simulation.'}

def dust_material():
    m=bpy.data.materials.new('contact dust volume');m.use_nodes=True;n=m.node_tree.nodes;n.clear();links=m.node_tree.links
    out=n.new('ShaderNodeOutputMaterial');volume=n.new('ShaderNodeVolumePrincipled');volume.inputs['Color'].default_value=(.39,.26,.14,1);volume.inputs['Anisotropy'].default_value=.2;links.new(volume.outputs['Volume'],out.inputs['Volume'])
    coord=n.new('ShaderNodeTexCoord');objinfo=n.new('ShaderNodeObjectInfo');noise=n.new('ShaderNodeTexNoise');noise.noise_dimensions='4D';noise.inputs['Scale'].default_value=4;noise.inputs['Detail'].default_value=2
    links.new(coord.outputs['Generated'],noise.inputs['Vector']);links.new(objinfo.outputs['Random'],noise.inputs['W'])
    distance=n.new('ShaderNodeVectorMath');distance.operation='DISTANCE';distance.inputs[1].default_value=(.5,.5,.5);links.new(coord.outputs['Generated'],distance.inputs[0])
    radial=n.new('ShaderNodeMath');radial.operation='MULTIPLY_ADD';radial.inputs[1].default_value=-2;radial.inputs[2].default_value=1;radial.use_clamp=True;links.new(distance.outputs['Value'],radial.inputs[0])
    power=n.new('ShaderNodeMath');power.operation='POWER';power.inputs[1].default_value=1.4;links.new(radial.outputs[0],power.inputs[0])
    erosion=n.new('ShaderNodeMath');erosion.operation='MULTIPLY_ADD';erosion.inputs[1].default_value=3;erosion.inputs[2].default_value=-.9;erosion.use_clamp=True;links.new(noise.outputs['Fac'],erosion.inputs[0])
    multiply=n.new('ShaderNodeMath');multiply.operation='MULTIPLY';links.new(power.outputs[0],multiply.inputs[0]);links.new(erosion.outputs[0],multiply.inputs[1])
    fade=n.new('ShaderNodeMath');fade.operation='MULTIPLY';links.new(multiply.outputs[0],fade.inputs[0]);links.new(objinfo.outputs['Alpha'],fade.inputs[1])
    density=n.new('ShaderNodeMath');density.operation='MULTIPLY';density.inputs[1].default_value=5;links.new(fade.outputs[0],density.inputs[0]);links.new(density.outputs[0],volume.inputs['Density'])
    return m

def dust(scene,motion,helper):
    material=dust_material();earth=helper._material('scattered dry soil',(.14,.065,.027),.95);objects=[];events=[];rng=random.Random(2718)
    for cycle in range(-4,7):
        for leg,phase in motion.TOUCHDOWN.items():
            t=(cycle+phase)*motion.PERIOD
            if t < -1.35 or t>2.5:continue
            p,_=motion.target(t+1e-8,leg);events.append({'time':t,'leg':leg,'anchor':[p[0],p[1],0]})
    for index,event in enumerate(events):
        t=event['time'];p=Vector(event['anchor']);lifetime=1.2+rng.random()*.15
        bpy.ops.mesh.primitive_cube_add(size=2,location=p);obj=bpy.context.object;obj.name=f'impact dust {index:02d}';obj.data.materials.append(material);obj.rotation_euler.z=rng.uniform(-.5,.5);objects.append(obj)
        for frame in range(61):
            age=frame/24-t
            if 0<age<lifetime:
                obj.location=p+Vector((.12*age,.7*age,.045+.18*age));obj.scale=(.10+.35*age,.15+.68*age,.07+.26*age)
                obj.color=(1,1,1,min(age/.08,1)*(1-age/lifetime)**1.5)
            else:obj.location=p;obj.scale=(.001,.001,.001);obj.color=(1,1,1,0)
            for prop in ('location','scale','color'):obj.keyframe_insert(prop,frame=frame)
        if t<-.4:continue
        for particle in range(5):
            bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=1,location=p);chip=bpy.context.object;chip.name=f'dirt {index:02d} {particle}';chip.data.materials.append(earth);objects.append(chip)
            velocity=Vector((rng.uniform(-.7,.7),rng.uniform(.8,2.5),rng.uniform(.8,1.9)));size=rng.uniform(.005,.012);flight=2*velocity.z/9.81
            for frame in range(61):
                age=frame/24-t
                if 0<age<flight:
                    chip.location=p+velocity*age+Vector((0,0,.012-4.905*age*age));chip.scale=(size,size*.65,size*.45)
                else:chip.location=p;chip.scale=(0,0,0)
                chip.keyframe_insert('location',frame=frame);chip.keyframe_insert('scale',frame=frame)
    return objects,{'events':events,'seed':2718,'policy':'Ground-fixed analytic impact anchors, noisy expanding local volumes and ballistic dirt. Authored effects; not fluid/soil simulation. Pre-roll describes continuous incoming travel.'}
