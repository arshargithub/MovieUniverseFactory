"""Shot-scaled environment and secondary cast. No principal identity admission."""
import math
import bpy
import numpy as np
from mathutils import Vector
from sikh257_native import ROOT, material,mesh,sphere
from sikh257_layout import empty,attach,tube,capsule,loft

def surface(name,colors,scale=5,rough=.88,bump=.015):
    m=material(name,colors[1]);n=m.node_tree.nodes;l=m.node_tree.links;b=n['Principled BSDF'];b.inputs['Roughness'].default_value=rough
    tc=n.new('ShaderNodeTexCoord');noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=scale;noise.inputs['Detail'].default_value=3
    r=n.new('ShaderNodeValToRGB');r.color_ramp.elements[0].position=.24;r.color_ramp.elements[0].color=(*colors[0],1);r.color_ramp.elements[1].position=.76;r.color_ramp.elements[1].color=(*colors[1],1)
    l.new(tc.outputs['Object'],noise.inputs[0]);l.new(noise.outputs['Fac'],r.inputs[0]);l.new(r.outputs[0],b.inputs['Base Color'])
    fine=n.new('ShaderNodeTexNoise');fine.inputs['Scale'].default_value=120;fine.inputs['Detail'].default_value=2
    bu=n.new('ShaderNodeBump');bu.inputs['Strength'].default_value=.23;bu.inputs['Distance'].default_value=bump
    l.new(tc.outputs['Object'],fine.inputs[0]);l.new(fine.outputs['Fac'],bu.inputs['Height']);l.new(bu.outputs[0],b.inputs['Normal'])
    return m

def sky(s):
    # Translated direction-space noise avoids repeated axial holes and bands.
    n=s.world.node_tree.nodes;l=s.world.node_tree.links;n.clear()
    out=n.new('ShaderNodeOutputWorld');bg=n.new('ShaderNodeBackground');bg.inputs[1].default_value=.5;l.new(bg.outputs[0],out.inputs[0])
    tc=n.new('ShaderNodeTexCoord');v=n.new('ShaderNodeVectorMath');v.operation='MULTIPLY_ADD';v.inputs[1].default_value=(2.2,2.2,5.0);v.inputs[2].default_value=(1.73,4.19,-2.13);l.new(tc.outputs['Normal'],v.inputs[0])
    noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=1.4;noise.inputs['Detail'].default_value=3;noise.inputs['Roughness'].default_value=.62;l.new(v.outputs[0],noise.inputs[0])
    ramp=n.new('ShaderNodeValToRGB');r=ramp.color_ramp;r.elements[0].position=.46;r.elements[0].color=(.008,.015,.031,1);r.elements[1].position=.72;r.elements[1].color=(.14,.19,.27,1)
    e=r.elements.new(.55);e.color=(.021,.034,.056,1);l.new(noise.outputs['Fac'],ramp.inputs[0])
    # Small one-sided disc clearance, irregular outer edge. Not a sky-sized halo.
    dot=n.new('ShaderNodeVectorMath');dot.operation='DOT_PRODUCT';dot.inputs[1].default_value=tuple(Vector((15,-110,30)).normalized());l.new(tc.outputs['Normal'],dot.inputs[0])
    clear=n.new('ShaderNodeMapRange');clear.clamp=True;clear.inputs['From Min'].default_value=.994;clear.inputs['From Max'].default_value=.999;clear.inputs['To Min'].default_value=0;clear.inputs['To Max'].default_value=1;l.new(dot.outputs['Value'],clear.inputs[0])
    mix=n.new('ShaderNodeMixRGB');mix.inputs[2].default_value=(.008,.015,.031,1);l.new(clear.outputs[0],mix.inputs[0]);l.new(ramp.outputs[0],mix.inputs[1]);l.new(mix.outputs[0],bg.inputs[0])

def environment():
    rng=np.random.default_rng(292)
    earth=surface('292 packed ochre lane',[(.13,.105,.062),(.38,.31,.20)],3,bump=.008)
    darkearth=surface('292 rut damp selective dark',[(.12,.10,.065),(.28,.23,.145)],14,bump=.004)
    field=surface('292 field ground',[(.027,.055,.025),(.11,.16,.055)],.15)
    leaf=surface('292 leaf masses',[(.012,.031,.019),(.105,.17,.08)],2.8)
    bark=surface('292 broken bark',[(.045,.035,.022),(.15,.13,.077)],7)
    mesh('cultivated plain292',[(-110,-150,-.035),(110,-150,-.035),(110,145,-.035),(-110,145,-.035)],[(0,1,2,3)],field)
    vs=[];fs=[]
    for j in range(296):
        y=-150+j
        for k in range(13):
            x=-2.1+k*.35;edge=abs(x)/2.1
            rut=-.014*sum(math.exp(-((x-c-.035*math.sin(y*.23))/.19)**2) for c in (-.7,.7))
            vs.append((x+edge**4*(.14*math.sin(y*.22)+.08*math.sin(y*.79)),y,-.008*edge**3+rut))
        if j:
            for k in range(12):q=j*13+k;fs.append((q-13,q,q+1,q-12))
    mesh('irregular packed farm track',vs,fs,earth)
    rockmats=[surface('292 gravel '+str(i),[(.08+.02*i,.075+.016*i,.055+.01*i),(.28+.04*i,.25+.035*i,.19+.03*i)],12) for i in range(3)]
    # Batched low stones: all bases on the actual flat lane; never floating.
    for idx,mat in enumerate(rockmats):
        vs=[];fs=[]
        for i in range(1600):
            y=float(rng.uniform(-80,100));x=float(rng.uniform(-2.05,2.05));r=float(rng.uniform(.012,.055));h=r*float(rng.uniform(.25,.65));n=len(vs)
            for level,rad in ((.001,1),(h*.7,.82),(h,.40)):
                for k in range(7):
                    a=k*math.tau/7;rr=r*rad*float(rng.uniform(.83,1.14));vs.append((x+rr*math.cos(a),y+rr*.7*math.sin(a),level))
            for row in range(2):
                for k in range(7):a=n+row*7+k;b=n+row*7+(k+1)%7;fs.append((a,b,b+7,a+7))
            fs.append(tuple(n+14+k for k in range(7)))
        mesh('grounded road aggregate '+str(idx),vs,fs,mat)
    crops=[surface('292 wheat tones '+str(i),[(.04+.01*i,.065+.008*i,.019),(.17+.015*i,.23+.018*i,.075+.008*i)],5) for i in range(4)]
    for side in (-1,1):
        # Plots differ in width/depth with continuous rows and quiet irrigation edges.
        y=-145
        while y<130:
            depth=float(rng.uniform(13,25));width=float(rng.uniform(22,43))
            tube('earth field margin',[(side*2.3,y,.015),(side*width,y+.7,.015)],.055,earth)
            y+=depth
        for mi,mat in enumerate(crops):
            vs=[];fs=[]
            for i in range(11000):
                x=side*(2.38+float(rng.integers(0,85))*.34+float(rng.uniform(-.10,.10)));y=float(rng.uniform(-140,130));h=float(rng.uniform(.28,.60))
                for blade in range(3):
                    a=float(rng.uniform(0,math.tau));lean=float(rng.uniform(.08,.24));hh=h*float(rng.uniform(.65,1.1));w=float(rng.uniform(.009,.019));n=len(vs)
                    for k in range(5):
                        u=k/4;cx=x+math.cos(a)*lean*u*u;cy=y+math.sin(a)*lean*u*u;cz=hh*(u-.12*u*u)
                        width=w*math.sin((u*.96+.02)*math.pi)
                        for sign in (-1,1):vs.append((cx-sign*math.sin(a)*width,cy+sign*math.cos(a)*width,cz))
                    for k in range(4):q=n+k*2;fs.append((q,q+1,q+3,q+2))
            mesh('individual wheat blades292',vs,fs,mat)
        for i in range(23):
            x=side*float(rng.uniform(17,87));y=float(rng.uniform(-125,105));h=float(rng.uniform(4,8))
            if 0<x<27 and -42<y<-20:continue
            capsule('branching tree trunk292',(x,y,0),(x+.2,y,h*.68),.12,bark)
            for j in range(5):
                a=float(rng.uniform(0,math.tau));tip=Vector((x+math.cos(a)*h*.25,y+math.sin(a)*h*.22,h*float(rng.uniform(.65,.90))))
                capsule('tree branch292',(x+.1,y,h*.45),tip,.045,bark)
                for k in range(6):
                    loc=tip+Vector(tuple(rng.uniform(-.65,.65,3)));ob=sphere('broken broadleaf crown292',loc,(h*.14,h*.13,h*.10),leaf)
                    for v in ob.data.vertices:v.co*=float(rng.uniform(.88,1.12))
    # Asymmetric earth bank; central plateau preserves horse/spear contacts.
    vs=[];fs=[];N=91
    for j in range(N):
        for i in range(N):
            x=-8+i*16/(N-1);y=-9+j*18/(N-1);r=math.sqrt((x/5.9)**2+(y/7.2)**2)
            angle=math.atan2(y,x);rr=r/(1+.13*math.sin(3*angle+.4)+.08*math.sin(5*angle))
            u=max(0,min(1,(rr-.38)/.72));z=3.2*(1-u*u*(3-2*u))
            if u>0:z+=.09*math.sin(x*2.4+y*.5)*math.sin(y*1.4)*math.sin(u*math.pi)
            vs.append((7.5+x,-29+y,z-.01))
    for j in range(N-1):
        for i in range(N-1):q=j*N+i;fs.append((q,q+1,q+1+N,q+N))
    mesh('low field bank for leader',vs,fs,earth)
    # Sparse rooted scrub breaks the bare mound silhouette without interfering
    # with its established flat horse/spear support area.
    grassv=[];grassf=[]
    for j in range(1600):
        idx=int(rng.integers(0,len(vs)));x,y,z=vs[idx]
        if z<.03 or z>2.7 or math.sin(x*1.3+y*.4)<-.25:continue
        for k in range(4):
            a=float(rng.uniform(0,math.tau));h=float(rng.uniform(.08,.22));n=len(grassv)
            grassv.extend([(x-.009*math.sin(a),y+.009*math.cos(a),z),(x+.009*math.sin(a),y-.009*math.cos(a),z),
                (x+.04*math.cos(a),y+.04*math.sin(a),z+h*.7),(x+.10*math.cos(a),y+.10*math.sin(a),z+h)])
            grassf.extend([(n,n+1,n+2),(n+1,n+3,n+2)])
    mesh('bank rooted scrub292',grassv,grassf,crops[1])
    # Earthen roadside village silhouettes, not modern infrastructure.
    plaster=surface('292 distant village mud plaster',[(.13,.105,.06),(.27,.22,.14)],4)
    for i in range(8):
        x=float(rng.uniform(-50,-13));y=-91+float(rng.uniform(-12,12));h=float(rng.uniform(2.1,3.1))
        bpy.ops.mesh.primitive_cube_add(size=1,location=(x,y,h/2));o=bpy.context.object;o.name='distant mud courtyard';o.scale=(float(rng.uniform(3,5)),float(rng.uniform(2.5,4)),h);o.data.materials.append(plaster)
        bevel=o.modifiers.new('rounded earthen edges','BEVEL');bevel.width=.05;bevel.segments=2
    return earth

_head_data=None
def donor_head():
    global _head_data
    if _head_data:return _head_data
    source=ROOT/'.runtime/assets/series01-body-blender-studio/human-base-meshes-bundle-v1.4.1/human_base_meshes_bundle.blend'
    with bpy.data.libraries.load(str(source),link=False) as (_,d):d.objects=['GEO-body_male_realistic']
    ob=d.objects[0];bpy.context.scene.collection.objects.link(ob);bpy.context.view_layer.update()
    center=(-2.705880880355835-1.8228728771209717)/2
    pts=[ob.matrix_world@v.co for v in ob.data.vertices];ids=[i for i,p in enumerate(pts) if p.z>1.40];mapping={i:j for j,i in enumerate(ids)}
    vs=[(pts[i].x-center,pts[i].y,pts[i].z-1.55) for i in ids];fs=[tuple(mapping[i] for i in p.vertices) for p in ob.data.polygons if all(i in mapping for i in p.vertices)]
    bpy.data.objects.remove(ob,do_unlink=True);_head_data=(vs,fs);return _head_data

def head(parent,z,seed,blue,skin):
    rng=np.random.default_rng(seed);vs,fs=donor_head();ob=mesh('secondary adult head292',vs,fs,skin);ob.parent=parent;ob.location=(0,0,z)
    hair=surface('292 secondary beard '+str(seed),[(.012,.009,.007),(.085,.066,.045)],22,bump=.003)
    if seed%3==0:hair=surface('292 salt beard '+str(seed),[(.07,.065,.05),(.28,.26,.19)],18,bump=.003)
    h=empty('secondary facial and crown frame292',parent);h.location=(0,0,z)
    for x in (-.032,.032):
        attach(sphere('secondary eye',(x,-.119,.023),(.0115,.0115,.010),material('secondary eye ivory',(.34,.28,.19))),h)
        attach(sphere('secondary brown iris',(x,-.130,.023),(.005,.002,.005),hair),h)
        tube('secondary brow',[(x-.014,-.125,.043),(x,-.131,.049),(x+.014,-.126,.045)],.004,hair,h)
    # Overlapping broad clumps, irregular rounded lower edge, not a conical beard.
    for i in range(19):
        a=-1.3+i*2.6/18;x=.075*math.sin(a);y=-.061-.057*math.cos(a);length=.11+float(rng.uniform(0,.05))
        pts=[(x,y,-.015),(x*.95,y-.006,-.07),(x*.80,y-.01,-length)]
        tube('secondary beard clump',pts,.014+float(rng.uniform(0,.004)),hair,h)
    for sign in (-1,1):tube('secondary moustache',[(0,-.145,-.04),(sign*.025,-.14,-.043),(sign*.055,-.12,-.060)],.008,hair,h)
    attach(sphere('secondary tied crown core',(0,.008,.15),(.104,.115,.15),blue),h)
    for j in range(9):
        pts=[]
        for k in range(65):
            a=k*math.tau/64;z0=.073+j*.020+.026*math.sin(a+j*.08)
            pts.append((.108*math.sin(a),.008-.119*math.cos(a),z0))
        tube('secondary diagonal turban course',pts,.009,blue,h)
    steel=material('292 patinated chakram',(.22,.23,.21));steel.node_tree.nodes['Principled BSDF'].inputs['Metallic'].default_value=.65
    tube('secondary crown steel ring',[(.111*math.sin(a),.008-.122*math.cos(a),.16+.025*math.sin(a)) for a in np.linspace(0,math.tau,65)],.003,steel,h)
    return h

def pleated_robe(name,parent,mat,bottom=.36,top=1.42,waist=.88):
    vs=[];fs=[];rows=22;cols=64
    for j in range(rows):
        z=bottom+(top-bottom)*j/(rows-1)
        if z<waist:rx=.16+.12*((waist-z)/(waist-bottom));ry=.115+.07*((waist-z)/(waist-bottom))
        else:rx=.16+.075*math.sin((z-waist)/(top-waist)*math.pi*.85);ry=.12+.018*math.sin((z-waist)*5)
        for i in range(cols):
            a=i*math.tau/cols;fold=.009*math.sin(a*13+z*2)+.004*math.sin(a*23-z*4)
            vs.append(((rx+fold)*math.cos(a),(ry+fold)*math.sin(a),z+.008*math.sin(a*5)*(1-j/(rows-1))))
    for j in range(rows-1):
        for i in range(cols):q=j*cols+i;r=j*cols+(i+1)%cols;fs.append((q,r,r+cols,q+cols))
    ob=mesh(name,vs,fs,mat);ob.parent=parent;return ob

def enrich_people(crowd):
    for i,(r,side,x,y,legs) in enumerate(crowd):
        for o in list(r.children):
            if any(o.name.startswith(n) for n in ('PROXY face','PROXY tall turban','PROXY robe','PROXY sash')):bpy.data.objects.remove(o,do_unlink=True)
        blue=surface('292 indigo robe '+str(i),[(.012+.002*(i%3),.025,.08),(.048,.078+.005*(i%3),.18)],9,bump=.002)
        skin=surface('292 crowd skin '+str(i),[(.19,.09,.035),(.38,.21,.09)],15,bump=.001)
        pleated_robe('secondary chola292',r,blue)
        frame=head(r,1.56,300+i,blue,skin);frame.rotation_euler.z=math.pi
        for child in r.children:
            if child.name.startswith('secondary adult head'):child.rotation_euler.z=math.pi
        r.scale.z=.96+.018*(i%6)
        saffron=surface('292 worn saffron sash '+str(i),[(.24,.09,.013),(.57,.29,.045)],12,bump=.002)
        tube('secondary shoulder sash',[(-.19,-.04,1.39),(-.19,.14,1.36),(.12,.14,.89),(.16,0,.88)],.026,saffron,r)
        tube('secondary waist sash',[(.177*math.cos(a),.133*math.sin(a),.88+.009*math.sin(a*3)) for a in np.linspace(0,math.tau,65)],.026,saffron,r)
        for side2 in (-1,1):attach(sphere('secondary closed hand',(side2*.26,-.05,.98),(.036,.03,.05),skin),r)
        for o in r.children:
            if o.name.startswith('PROXY arm'):o.data.materials.clear();o.data.materials.append(blue)
        # Small variation, without changing planted foot or collision envelopes.
        r['individual_variant']=i

def enrich_leader(h):
    root,pivot,rig,rider,feet,rest,arms,spear=h
    for o in list(rider.children):
        if o.name in ('leader head','leader tall turban','leader torso'):bpy.data.objects.remove(o,do_unlink=True)
    blue=surface('292 commander indigo cloth',[(.012,.024,.075),(.055,.09,.23)],12,bump=.002)
    skin=surface('292 commander weathered skin',[(.16,.075,.029),(.38,.21,.095)],18,bump=.001)
    pleated_robe('commander fitted chola',rider,blue,bottom=-.16,top=.52,waist=.06)
    head(rider,.65,333,blue,skin)
    gold=surface('292 commander sash',[(.25,.10,.015),(.62,.32,.055)],14,bump=.002)
    tube('commander cross sash',[(-.20,.04,.46),(-.20,-.14,.45),(.13,-.16,.04),(.17,0,.02)],.032,gold,rider)
    tube('commander waist sash',[(.18*math.cos(a),.15*math.sin(a),.06) for a in np.linspace(0,math.tau,65)],.033,gold,rider)
    for side,up,lo,palm in arms:
        for o in (up,lo):o.data.materials.clear();o.data.materials.append(blue)
        palm.data.materials.clear();palm.data.materials.append(skin)
    body=bpy.data.objects['horse'];coat=surface('292 dappled charcoal silver horse',[(.13,.15,.155),(.29,.31,.30)],8.7,rough=.57,bump=.0015)
    body.data.materials.clear();body.data.materials.append(coat)
    body['292_coat']='multi-scale dapple and fine coat roughness; not fur simulation'
    # Equipment and groom use bone-local ownership from actual evaluated mesh.
    bpy.context.view_layer.update()
    bounds=[body.matrix_world@v.co for v in body.data.vertices]
    (ROOT/'results/sikh292/horse-landmarks.json').write_text(__import__('json').dumps({'bounds':[[min(p[k] for p in bounds),max(p[k] for p in bounds)] for k in range(3)],'bones':{b.name:[list(rig.matrix_world@b.head),list(rig.matrix_world@b.tail)] for b in rig.pose.bones if any(s in b.name.lower() for s in ('head','neck','tail','spine'))}},indent=2))
    return body
