"""Fixed native character suitability control; not an accepted production asset.

Adapts the pinned anatomical donor, authors an editable native curve beard and
one indexed wrapped strip. No provider calls, external scripts or asset code.
"""
import math
import random
import json
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from sikh257_native import male_bust, material, mesh, scene_setup, camera_at


def painted(name, color, contrast=.20, scale=110):
    m=material(name,color);n=m.node_tree.nodes;l=m.node_tree.links
    coord=n.new('ShaderNodeTexCoord');noise=n.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value=scale;noise.inputs['Detail'].default_value=2.5
    ramp=n.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].position=.24;ramp.color_ramp.elements[1].position=.76
    for e,mult in zip(ramp.color_ramp.elements,(1-contrast,1+contrast)):
        e.color=(*(min(.95,c*mult) for c in color),1)
    l.new(coord.outputs['Object'],noise.inputs['Vector']);l.new(noise.outputs['Fac'],ramp.inputs[0])
    bs=n.get('Principled BSDF');l.new(ramp.outputs[0],bs.inputs['Base Color'])
    bs.inputs['Roughness'].default_value=.73
    return m


def strands(name, paths, mat, radius):
    c=bpy.data.curves.new(name,'CURVE');c.dimensions='3D';c.resolution_u=1
    c.bevel_depth=radius;c.bevel_resolution=1;c.resolution_u=2
    for points in paths:
        s=c.splines.new('POLY');s.points.add(len(points)-1)
        for i,(p,co) in enumerate(zip(s.points,points)):
            p.co=(*co,1);p.radius=max(.06,(1-i/(len(points)-1))**.45)
    o=bpy.data.objects.new(name,c);bpy.context.scene.collection.objects.link(o);c.materials.append(mat)
    return o


def hero_bust():
    bust,placeholder=male_bust(detailed=True);bpy.data.objects.remove(placeholder,do_unlink=True)
    bust.name='Sikh anatomical donor adaptation'
    # Preserve a continuous neck transition, elongate lower face modestly.
    for v in bust.data.vertices:
        x,y,z=v.co
        face=max(0,min(1,(z-1.38)/.06))*max(0,min(1,(1.71-z)/.06))
        front=max(0,min(1,(-y-.035)/.055))
        nose=math.exp(-(x/.020)**2-((z-1.545)/.033)**2)*front
        brow=math.exp(-((abs(x)-.032)/.035)**2-((z-1.596)/.012)**2)*front
        v.co.y-=.026*nose+.008*brow
        v.co.x+=x*.30*nose
        eye_mask=math.exp(-((abs(x)-.032)/.018)**4-((z-1.573)/.025)**4)*front
        v.co.z-=.25*(z-1.573)*eye_mask
        if z<1.573:v.co.z-=.011*math.exp(-((z-1.475)/.065)**2)*face
        v.co.x*=1-.035*face
    skin=painted('warm ochre painted skin',(.27,.115,.045),.10,95)
    bust.data.materials.clear();bust.data.materials.append(skin)
    dg=bpy.context.evaluated_depsgraph_get();bpy.context.view_layer.update()
    surface=BVHTree.FromObject(bust,dg)
    def front(x,z,optional=False):
        p,_,_,_=surface.ray_cast(Vector((x,-.5,z)),Vector((0,1,0)),1.)
        return p.y-.001 if p else (None if optional else -.10)
    dark=painted('black brown beard',(.014,.010,.008),.5,55)
    highlight=painted('subtle warm beard strands',(.034,.024,.016),.35,60)
    for mat in (dark,highlight):
        b=mat.node_tree.nodes.get('Principled BSDF');b.inputs['Specular IOR Level'].default_value=.12;b.inputs['Roughness'].default_value=.85
    rng=random.Random(261);paths=[];warm=[]
    for i in range(7200):
        x=rng.uniform(-.076,.076)
        high=1.478+.055*(abs(x)/.076)**.85+rng.uniform(-.007,.003)
        z=rng.uniform(1.451,high)
        # Facial hair roots follow actual donor skin, not a floating beard ball.
        y=front(x,z,True)
        if y is None:continue
        root=Vector((x,y,z))
        # Broad rounded, irregular lower edge instead of a central pointed wedge.
        bottom=1.340+.034*(abs(x)/.078)**6+rng.uniform(-.009,.026)
        endz=bottom
        endx=x*.92+rng.uniform(-.008,.008)
        endy=min(y-.018,-.111)-.027*(1-(abs(x)/.09)**2)
        phase=round(x/.008)*.7;wave=rng.uniform(.003,.008)
        points=[]
        for j in range(18):
            t=j/17;w=math.sin(math.pi*t)
            points.append((x+(endx-x)*t-.18*x*w+wave*w*math.sin(t*18+phase),y+(endy-y)*math.sin(t*math.pi/2)-.009*w+wave*w*math.cos(t*15+phase),z+(endz-z)*t))
        (warm if i%13==0 else paths).append(points)
    strands('editable native beard main',paths,dark,.00052)
    strands('editable native beard accents',warm,highlight,.00039)
    # Dense underlying growth prevents a transparent curtain of isolated hairs.
    vs=[];fs=[];nx=45;nz=26
    for i in range(nx):
        x=-.065+.13*i/(nx-1);top=1.469+.055*(abs(x)/.076)**.85;y=front(x,top)
        for j in range(nz):
            t=j/(nz-1);w=math.sin(math.pi*t)
            vs.append((x*(1-.08*t)-.18*x*w,y+(min(y-.018,-.111)-.024*(1-(abs(x)/.09)**2)-y)*math.sin(t*math.pi/2),top+(1.350+.024*(abs(x)/.078)**6-top)*t))
    for i in range(nx-1):
        for j in range(nz-1):
            a=i*nz+j;fs.append((a,a+1,a+nz+1,a+nz))
    base=mesh('dense beard interior',vs,fs,dark)
    solid=base.modifiers.new('dense growth volume','SOLIDIFY');solid.thickness=.012
    # Moustache follows the upper lip and turns slightly at the ends.
    paths=[]
    for side in (-1,1):
        for i in range(260):
            q=rng.random();x=side*rng.uniform(.002,.012);z=1.507+rng.uniform(-.003,.004)
            y=front(x,z)-rng.uniform(.001,.004);points=[]
            for j in range(16):
                t=j/15;xx=x+side*(.041+.009*q)*t
                zz=z-.013*math.sin(math.pi*t*.8)+.005*t*t
                yy=y-.008*math.sin(math.pi*t)+.016*t
                points.append((xx,yy,zz))
            paths.append(points)
    strands('native moustache',paths,dark,.00035)
    paths=[]
    for side in (-1,1):
        for i in range(220):
            x=side*rng.uniform(.010,.061);z=1.593+.006*math.sin((abs(x)-.012)/.049*math.pi)+rng.uniform(-.004,.004)
            y=front(x,z)-.001
            paths.append([(x,y,z),(x+side*.006,y-.001,z+.002),(x+side*.010,y+.0005,z-.002)])
    strands('native brows',paths,dark,.00035)
    from sikh257_native import sphere
    iris=material('dark warm irises',(.040,.021,.008));pupil=material('pupils',(.002,.001,.001))
    for x in (-.032,.032):
        sphere('iris cap',(x,-.130,1.573),(.0065,.0018,.0055),iris)
        sphere('pupil cap',(x,-.1315,1.573),(.0033,.001,.0028),pupil)
    for o in bpy.context.scene.objects:
        if o.name.startswith('eye'):o.scale.z=.8
    return bust


def wrapped_strip():
    # Wrapped support is an authored initial condition. The attached end will
    # be released into cloth simulation in a separate representative control.
    vs=[];fs=[];cols=15;rows=361;centers=[]
    for i in range(rows):
        u=i/(rows-1);theta=math.tau*5.75*u;lat=1.48-1.41*u
        for j in range(cols):
            w=j/(cols-1)-.5;a=lat+w*.065/.145
            r=.004*math.cos(w*math.pi)+.0013*math.sin(w*math.pi*8+theta*.3)
            x=(.116+r)*math.cos(a)*math.sin(theta)
            y=-.003-(.150+r)*math.cos(a)*math.cos(theta)
            z=1.600+.145*math.sin(a)+.065*math.sin(theta)*math.cos(theta/2)*math.cos(a)
            vs.append((x,y,z))
        centers.append(vs[i*cols+cols//2])
    crown_rows=rows
    # Continuous last quarter-turn approaches the ear and then the face.
    for i in range(1,81):
        u=i/80;theta=-math.pi/2+math.pi*u
        cx=.125*math.sin(theta);cy=-.003-.202*math.cos(theta)
        cz=centers[-1][2]+.030*u-.025*math.sin(math.pi*u)
        width=.065+(.165-.065)*math.sin(math.pi*u)**.65
        for j in range(cols):
            w=j/(cols-1)-.5
            vs.append((cx,cy-.003*math.cos(w*math.pi*6)*math.sin(math.pi*u),cz+width*w))
    rows+=80
    for i in range(rows-1):
        for j in range(cols-1):
            a=i*cols+j;fs.append((a,a+cols,a+cols+1,a+1))
    return {'verts':vs,'faces':fs,'cols':cols,'rows':rows,'crown_rows':crown_rows}


def crown():
    d=wrapped_strip();o=mesh('one continuous diagonal turban and face end',d['verts'],d['faces'],painted('deep indigo woven wraps',(.019,.028,.070),.32,180))
    o.shape_key_add(name='Basis')
    # Only for exposed-face suitability stills; not a simulated release claim.
    k=o.shape_key_add(name='static loose-span clearance study')
    for i,v in enumerate(k.data):
        row=i//d['cols'];u=max(0,(row-d['crown_rows']+1)/80)
        if row>=d['crown_rows']:
            v.co.z-=.24*math.sin(math.pi*u)**.6+.12*u
            v.co.y-=.04*math.sin(math.pi*u)
    k.value=1
    sub=o.modifiers.new('woven display subdivision','SUBSURF');sub.levels=1
    solid=o.modifiers.new('fabric thickness','SOLIDIFY');solid.thickness=.0013
    return o


def proof(out):
    s,cam=scene_setup();hero_bust();cloth=donor_crown(out)
    s.render.engine='CYCLES';s.cycles.samples=24
    s.render.resolution_x=720;s.render.resolution_y=840
    cam.data.ortho_scale=.63
    s.view_settings.view_transform='AgX'
    bpy.data.objects['key'].data.energy=230;bpy.data.objects['fill'].data.energy=85
    for name,pos in [('front',(0,-3,1.57)),('three-quarter',(1.7,-3,1.57)),('opposite',(-1.7,-3,1.57))]:
        camera_at(cam,pos,(0,0,1.53));s.render.filepath=str(out/(name+'.png'))
        bpy.ops.render.render(write_still=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'hero-control.blend'))
    (out/'character-control.json').write_text(json.dumps({'status':'UNREVIEWED','reference':'sikh-uncovered-concept-v03.png','method':'evaluated anatomical donor plus native curve groom and free authored crown feasibility','limitations':['new donor crown not yet extended into face-cover strip','identity suitability requires actual visual review','no full-body/contact proof']},indent=2))


def donor_crown(out):
    from movie_factory.sikh257_contract import ROOT,HERO_SOURCES
    before=set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=str(ROOT/next(iter(HERO_SOURCES))))
    obs=[o for o in set(bpy.data.objects)-before if o.type=='MESH']
    bpy.context.view_layer.update()
    points=[o.matrix_world@v.co for o in obs for v in o.data.vertices]
    low=Vector(tuple(min(p[a] for p in points) for a in range(3)));high=Vector(tuple(max(p[a] for p in points) for a in range(3)))
    center=(low+high)/2;scale=.242/(high.x-low.x)
    verts=[];faces=[]
    for o in obs:
        start=len(verts)
        for v in o.data.vertices:
            p=(o.matrix_world@v.co-center)*scale;p.z+=1.640;verts.append(tuple(p))
        faces.extend(tuple(i+start for i in p.vertices) for p in o.data.polygons)
    for o in set(bpy.data.objects)-before:bpy.data.objects.remove(o,do_unlink=True)
    result=mesh('Harsh Sikh turban feasibility donor',verts,faces,painted('deep indigo cloth donor',(.016,.025,.066),.15,120))
    import bmesh
    bm=bmesh.new();bm.from_mesh(result.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=.00001)
    boundaries=[tuple(v.co) for e in bm.edges if e.is_boundary for v in e.verts]
    bm.to_mesh(result.data);bm.free()
    (out/'donor-topology.json').write_text(json.dumps({'source_bounds':[list(low),list(high)],'scale':scale,'vertices':len(result.data.vertices),'faces':len(result.data.polygons),'boundary_points':boundaries},indent=2))
    return result
