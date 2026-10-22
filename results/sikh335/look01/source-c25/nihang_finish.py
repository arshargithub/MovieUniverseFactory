"""Coordinated supporting costume interfaces and material candidate, fixed scope."""
import math
import numpy as np
import importlib.util
from pathlib import Path
_spec=importlib.util.spec_from_file_location('mf_finish_transfer',Path(__file__).with_name('nihang_transfer.py'))
transfer=importlib.util.module_from_spec(_spec);_spec.loader.exec_module(transfer)


def mesh(bpy,name,points,faces,parent,material,source=None):
    data=bpy.data.meshes.new(name);data.from_pydata(points,[],faces);data.update()
    for p in data.polygons:p.use_smooth=True
    ob=bpy.data.objects.new(name,data);bpy.context.scene.collection.objects.link(ob)
    ob.parent=parent
    if source:ob.matrix_parent_inverse=source.matrix_parent_inverse.copy();ob.matrix_basis=source.matrix_basis.copy()
    data.materials.append(material);return ob


def bind_overlay(bpy,ob,shirt,reference):
    """Bind a coherent ribbon to source triangles, preserving stand-off vectors."""
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    garment=transfer.module('nihang_garment')
    shirt.data.calc_loop_triangles();tri=np.array([tuple(t.vertices) for t in shirt.data.loop_triangles])
    tree=BVHTree.FromPolygons(reference,tri,all_triangles=True)
    indices=[];weights=[];offsets=[];normals=[]
    for vertex in ob.data.vertices:
        p=np.array(vertex.co);hit,n,i,d=tree.find_nearest(Vector(p))
        if hit is None or d>.16:raise ValueError('FINISH_OVERLAY_SUPPORT')
        indices.append(tri[i]);weights.append(garment.barycentric(np.array(hit),*reference[tri[i]]))
        offsets.append(p-np.array(hit));normals.append(np.array(n))
    ids=np.array(indices);w=np.array(weights);off=np.array(offsets);norm=np.array(normals)
    original=shirt.data.shape_keys
    if not original:return
    ob.shape_key_add(name='Basis');times=[]
    keys=[k for k in original.key_blocks if k.name.startswith('bound')]
    for key in keys:times.append(int(key.name[5:]))
    for i,(f,key) in enumerate(zip(times,keys)):
        pts=np.array([p.co[:] for p in key.data]);t=pts[ids]
        newn=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);newn/=np.maximum(1e-12,np.linalg.norm(newn,axis=1))[:,None]
        cross=np.cross(norm,newn);cos=(norm*newn).sum(1)
        if cos.min()<-.99:raise ValueError('FINISH_OVERLAY_FRAME_FLIP')
        offset=off+np.cross(cross,off)+np.cross(cross,np.cross(cross,off))/(1+cos)[:,None]
        moved=(t*w[:,:,None]).sum(1)+offset
        k=ob.shape_key_add(name=key.name);k.data.foreach_set('co',moved.astype('f4').ravel())
        for ff,value in ((times[i-1] if i else 0,0),(f,1),(times[i+1] if i+1<len(times) else 697,0)):
            k.value=value;k.keyframe_insert('value',frame=ff)
    for layer in ob.data.shape_keys.animation_data.action.layers:
        for strip in layer.strips:
            for bag in strip.channelbags:
                for fc in bag.fcurves:
                    for key in fc.keyframe_points:key.interpolation='LINEAR'


def sash(bpy,root,shirt):
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    old=next(o for o in root.children_recursive if o.name.startswith('297 woven diagonal sash'))
    keys=shirt.data.shape_keys
    ref=np.array([v.co[:] for v in (keys.key_blocks['bound0283'].data if keys else shirt.data.vertices)])
    faces=[tuple(p.vertices) for p in shirt.data.polygons]
    tree=BVHTree.FromPolygons(ref,faces)
    leader=root.name=='mounted leader';offset=0 if leader else .82;facing=-1 if leader else 1
    rows=61;cols=9;panels=[];missing=0
    for side in (facing,-facing):
        points=[];limits=[]
        for j in range(rows):
            t=j/(rows-1);x=.135*(1-t)-.155*t;z=.035*(1-t)+.49*t+offset
            row=[];surface=[]
            for k in range(cols):
                u=(k/(cols-1)-.5)*.085;xx=x+u*.843;zz=z+u*.538
                hit=tree.ray_cast(Vector((xx,side*.8,zz)),Vector((0,-side,0)))[0]
                row.append([xx,float(hit.y) if hit else float('nan'),zz])
                if hit:surface.append(float(hit.y))
                else:missing+=1
            limits.append((min(surface) if side<0 else max(surface)) if surface else np.nan)
            points.append(row)
        points=np.array(points);limits=np.array(limits);valid=np.flatnonzero(np.isfinite(limits))
        if len(valid)<rows*.65:raise ValueError('FINISH_SASH_SUPPORT_MISSING')
        limits=np.interp(np.arange(rows),valid,limits[valid])+side*.012
        # A tensioned ribbon bridges small folds instead of imprinting every
        # low-resolution cloth recess. It cannot cross any sampled outer peak.
        y=limits.copy()
        for _ in range(10):
            smooth=y.copy();smooth[1:-1]=(y[:-2]+2*y[1:-1]+y[2:])/4
            y=np.minimum(smooth,limits) if side<0 else np.maximum(smooth,limits)
        points[:,:,1]=y[:,None]
        panels.append(points)
    front,back=panels;bridge=[]
    for j in range(1,9):
        t=j/9;row=front[-1]*(1-t)+back[-1]*t;row[:,2]+=.008*math.sin(math.pi*t);bridge.append(row)
    points=np.concatenate((front,np.array(bridge),back[::-1]),axis=0);nr=len(points)
    quads=[(j*cols+k,j*cols+k+1,(j+1)*cols+k+1,(j+1)*cols+k) for j in range(nr-1) for k in range(cols-1)]
    mat=old.data.materials[0].copy();mat.name='MF Nihang continuous worn sash'
    ob=mesh(bpy,'MF Nihang continuous shoulder sash '+root.name,points.reshape(-1,3),quads,shirt.parent,mat,shirt)
    bind_overlay(bpy,ob,shirt,ref)
    solid=ob.modifiers.new('Turned woven sash thickness','SOLIDIFY');solid.thickness=.002
    sub=ob.modifiers.new('Soft supported ribbon','SUBSURF');sub.levels=1;sub.render_levels=1
    old.hide_render=True;old.hide_viewport=True
    return {'object':ob.name,'vertices':len(ob.data.vertices),'missing_edge_samples':missing,'scope':'Continuous shoulder wrap with source-bound pose cache; visual contact remains required.'}


def face_material(bpy,root,frame):
    head=next(o for o in root.children_recursive if o.name.startswith('secondary adult head'))
    mat=head.data.materials[0].copy();mat.name='MF Nihang varied warm skin '+root.name
    nodes=mat.node_tree.nodes;links=mat.node_tree.links;bs=nodes.get('Principled BSDF')
    for n in nodes:
        if n.bl_idname=='ShaderNodeTexNoise':n.inputs['Scale'].default_value=36;n.inputs['Detail'].default_value=3
    bs.inputs['Roughness'].default_value=.68;bs.inputs['Specular IOR Level'].default_value=.24
    bs.inputs['Subsurface Weight'].default_value=.055
    tc=nodes.new('ShaderNodeTexCoord');noise=nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=390
    links.new(tc.outputs['Object'],noise.inputs['Vector']);bump=nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value=.19;bump.inputs['Distance'].default_value=.00015
    links.new(noise.outputs['Fac'],bump.inputs['Height']);links.new(bump.outputs['Normal'],bs.inputs['Normal'])
    head.data.materials[0]=mat
    for ob in head.children:
        if ob.name.startswith('319 torso to head neck bridge'):ob.data.materials[0]=mat
    for ob in frame.children:
        if ob.name.startswith('secondary brown iris'):
            m=ob.data.materials[0].copy();m.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.065,.028,.009,1);ob.data.materials[0]=m
        if ob.name.startswith('319 pupil'):ob.scale.x*=.85;ob.scale.z*=.85
        if ob.name.startswith('319 surface fitted eyebrows') and ob.type=='CURVE':
            ob.data=ob.data.copy();ob.data.bevel_depth*=1.2
    return mat.name


def run(bpy,out):
    look=transfer.module('nihang_look');root=bpy.data.objects['mounted leader']
    if not bpy.data.objects.get('MF Nihang neutral-derived chola mounted leader'):raise ValueError('FINISH_TRANSFER_REQUIRED')
    scene=next(s for s in bpy.data.scenes if root.name in s.objects);bpy.context.window.scene=scene
    scene.frame_set(283);bpy.context.view_layer.update()
    report=[]
    for name in ('mounted leader',):
        root=bpy.data.objects[name];shirt=bpy.data.objects['MF Nihang neutral-derived chola '+name]
        upper=shirt.parent;frame=next(o for o in upper.children if o.name.startswith('secondary facial and crown'))
        old=next(o for o in frame.children if o.name.startswith('319 supported dumalla'))
        crown=look.wrapped_crown(bpy,frame,old.data.materials[0],True)
        for ob in frame.children:
            if ob.name.startswith('MF Nihang ') and ob.type=='MESH':
                for p in ob.data.vertices:p.co.z=.045+(p.co.z-.045)*.92
        beard=look.beard_volume(frame)
        for ob in frame.children:
            if not ob.name.startswith('319 tapered beard fibers'):continue
            blocks=[k.data for k in ob.data.shape_keys.key_blocks] if ob.data.shape_keys else [sp.points for sp in ob.data.splines]
            for block in blocks:
                for p in block:
                    w=max(0,min(1,(-p.co.z-.10)/.12));p.co.z+=.026*w*(1-min(1,abs(p.co.x)/.09));p.co.x*=1+.08*w
        report.append({'actor':name,'sash':sash(bpy,root,shirt),'crown':crown,'beard':beard,'skin':face_material(bpy,root,frame)})
    coat=look.horse_finish(bpy);pad=look.saddle_pad(bpy)
    scene.frame_set(283);bpy.context.view_layer.update()
    return {'actors':report,'coat':coat,'pad':pad,'limits':'Coordinated appearance candidate; original motion and camera unchanged. Must inspect stance, reverse, crest and original film floor.'}
