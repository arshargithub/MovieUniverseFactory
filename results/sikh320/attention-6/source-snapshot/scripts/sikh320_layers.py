"""Fit visible cloth layers from the outside of the final torso envelope.

Nearest-surface projection is ambiguous on a thin two-sided garment. Explicit
front-facing rays preserve which side of the cloth the sash belongs on.
"""
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

def fit_layers(upper,shirt,leader):
    bpy.context.scene.frame_set(283);bpy.context.view_layer.update()
    ev=shirt.evaluated_get(bpy.context.evaluated_depsgraph_get())
    tree=BVHTree.FromPolygons([p.co for p in ev.data.vertices],
                             [tuple(p.vertices) for p in ev.data.polygons])
    facing=-1 if leader else 1
    report=[]
    for ob in upper.children:
        sash=ob.name.startswith('297 woven diagonal sash')
        panel=ob.name.startswith('319 overlapping chola chest panel')
        seam=ob.name.startswith('319 chola folded placket')
        if not (sash or panel or seam):continue
        for mod in list(ob.modifiers):
            if mod.name.startswith('320 supported'):ob.modifiers.remove(mod)
        points=ob.data.vertices if ob.type=='MESH' else [p for sp in ob.data.splines for p in sp.points]
        hits=0
        for p in points:
            x,y,z=p.co[:3]
            q=tree.ray_cast(Vector((x,facing*.8,z)),Vector((0,-facing,0)))[0]
            if q is None:continue
            offset=.012 if sash else .0045 if seam else .003
            p.co.y=q.y+facing*offset;hits+=1
        if sash and hits<len(points)*.95:raise ValueError('Incomplete sash cloth support')
        report.append({'object':ob.name,'supported_vertices':hits,'vertices':len(points)})
    return report
