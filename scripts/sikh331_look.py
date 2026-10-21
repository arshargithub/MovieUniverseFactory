"""One supporting actor form proof before crowd propagation; immutable input coords."""
import math,json
import bpy
import numpy as np
from mathutils import Vector
from sikh257_native import mesh
from sikh319_cast import strands
def actor(root):
    upper=next(o for o in root.children if o.name.startswith('320 articulated upper body'))
    shirt=next(o for o in upper.children if o.name.startswith('319 anatomically'))
    blocks=shirt.data.shape_keys.key_blocks if shirt.data.shape_keys else []
    # Increase fabric ease primarily across trunk, with waist-supported folds.
    for block in ([k.data for k in blocks] if blocks else [shirt.data.vertices]):
        pts=np.array([v.co[:] for v in block],dtype=np.float32)
        z=pts[:,2];x=pts[:,0];y=pts[:,1]
        u=np.clip((z-.05)/.40,0,1)
        trunk=np.clip((.23-np.abs(x))/.07,0,1)*np.maximum(0,np.sin(np.pi*u))**.6
        wave=np.zeros_like(z)
        for origin,slope,width in ((-.14,.32,.012),(-.06,.16,.010),(.05,-.22,.014),(.14,-.36,.013)):
            d=x-(origin+slope*(z-.06))
            wave+=.008*np.exp(-(d/width)**2)-.003*np.exp(-((d-width*1.5)/width)**2)
        # Material is cloth around the body rather than a bare-anatomy skin.
        pts[:,1]+=np.sign(y)*trunk*(.017+wave)
        pts[:,0]+=np.sign(x)*trunk*.014
        if not np.isfinite(pts).all():raise ValueError('Nonfinite garment coordinates')
        block.foreach_set('co',pts.ravel())
    for ob in upper.children_recursive:
        if ob.type=='MESH':
            for p in ob.data.polygons:p.use_smooth=True
        if ob.type=='CURVE' and not ob.hide_render and ob.name.startswith('319 refined skin-rooted beard'):
            for sp in ob.data.splines:
                pts=[p.co.copy() for p in sp.points]
                if not pts:continue
                end=pts[-1];target=-.237+.012*math.sin(end.x*127+end.y*43)
                for i,(p,base) in enumerate(zip(sp.points,pts)):
                    t=i/max(1,len(pts)-1);p.co.z=base.z+(target-end.z)*t*t
                    p.co.x=base.x*(1+.24*t*t)
        if ob.type=='MESH' and ob.name.startswith(('319 supported dumalla','319 overlapping tied cloth')):
            for p in ob.data.vertices:
                a=math.atan2(p.co.x,-p.co.y);z=p.co.z
                w=max(0,min(1,(z-.06)/.12))
                p.co.x*=1+.035*w*math.sin(a*3+.9)
                p.co.z+=.006*w*math.sin(a*2+.4)+.003*w*math.sin(a*5+z*18)
    # Renew foreground sash support against changed torso; existing exterior
    # modifiers remain present, so they see the new evaluated cloth surface.
    from sikh320_layers import fit_layers
    layers=fit_layers(upper,shirt,True)
    return {'actor':root.name,'method':'trunk ease and tension folds; broader beard with preserved roots; irregular tied course geometry','layers':layers,'status':'UNREVIEWED'}
def saddle():
    s=bpy.context.scene;s.frame_set(283);bpy.context.view_layer.update()
    old=bpy.data.objects['fitted saddle blanket292'];parent=old.parent
    mat=old.data.materials[0].copy();mat.name='331 layered saddle wool'
    bs=mat.node_tree.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.92
    # Use the existing attachment frame, but a broad rounded drape instead
    # of a straight projecting quadrilateral. Thickness and hem are visible.
    offset=Vector((0,.646173,.00076556));vs=[];rows=21;cols=33
    for j in range(rows):
        u=j/(rows-1);y=-.36+u*.80
        for i in range(cols):
            a=-1.42+2.84*i/(cols-1)
            x=.37*math.sin(a);z=1.51-.50*(1-math.cos(a))
            edge=abs(math.sin(a))**5
            x+=math.copysign(.008*edge*math.sin(u*math.tau*3+.4),x)
            z+=.013*edge*math.sin(u*math.tau*2.5+.3)
            yy=y+.035*edge*math.sin(math.pi*u)
            vs.append(Vector((x,yy,z))-offset)
    fs=[(j*cols+i,j*cols+i+1,(j+1)*cols+i+1,(j+1)*cols+i) for j in range(rows-1) for i in range(cols-1)]
    ob=mesh('331 rounded draped saddle pad',vs,fs,mat);ob.parent=parent
    sol=ob.modifiers.new('Wool pad thickness','SOLIDIFY');sol.thickness=.012
    sub=ob.modifiers.new('Supported folded wool','SUBSURF');sub.levels=1;sub.render_levels=1
    for p in ob.data.polygons:p.use_smooth=True
    old.hide_render=True;old.hide_viewport=True
    paths=[[vs[j*cols+i] for j in range(rows)] for i in (0,cols-1)]
    paths += [[vs[j*cols+i] for i in range(cols)] for j in (0,rows-1)]
    strands('331 bound saddle wool edges',paths,.006,mat,parent,False)
def build(out):
    report=actor(bpy.data.objects['mounted leader']);saddle()
    (out/'appearance-proof.json').write_text(json.dumps(report,indent=2))
