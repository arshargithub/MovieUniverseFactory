"""Fixed supporting costume fold/readability refinement on current topology."""
import json,math,importlib.util
from pathlib import Path
import numpy as np

def fold_amount(axial,radial,front,boundary_distance):
    support=math.exp(-(axial/.055)**2)*max(0,min(1,(.10-radial)/.03))
    edge=max(0,min(1,(boundary_distance-.018)/.025))
    compression=max(0,min(1,(front+.25)/1.0))
    return .0055*support*edge*compression*(.5+.5*math.sin(axial*190+front*2))

def run(bpy,out):
    from mathutils import Vector
    from mathutils.kdtree import KDTree
    def load(name):
        s=importlib.util.spec_from_file_location(name,Path(__file__).with_name('nihang_'+name+'.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
    h=load('tack354');trim=load('trim357');finish=load('whole347');sig=h.action_signature(bpy)
    rig=bpy.data.objects['MF coherent Nihang rig'];coat=bpy.data.objects['MF coherent coat']
    if not rig.get('trim357') or rig.get('fabric357'):raise ValueError('FABRIC357_PARENT')
    data=coat.data.copy();coat.data=data;faces=[tuple(p.vertices) for p in data.polygons];ids=set(i for loop in trim.loops(faces) for i in loop)
    kd=KDTree(len(ids))
    for j,i in enumerate(sorted(ids)):kd.insert(data.vertices[i].co,j)
    kd.balance();deltas=[]
    for v in data.vertices:
        amount=0
        for side in ('L','R'):
            elbow=rig.data.bones['lowerarm01.'+side].head_local;wrist=rig.data.bones['wrist.'+side].head_local
            axis=(wrist-elbow).normalized();q=v.co-elbow;axial=q.dot(axis);rv=q-axis*axial;radial=rv.length
            front=rv.normalized().dot(Vector((0,-1,0))) if radial else 0
            amount=max(amount,fold_amount(axial,radial,front,kd.find(v.co)[2]))
        v.co+=v.normal*amount;deltas.append(amount)
    data.update();changed=[]
    for ob in rig.children_recursive:
        if ob.type!='MESH' or not ob.name.startswith(('MF Nihang wrapped crown','MF Nihang overlapped cloth','MF Nihang gathered crown','MF coherent coat','MF coherent split chola','MF coherent pants')):continue
        for i,source in enumerate(ob.data.materials):
            mat=source.copy();ob.data.materials[i]=mat;mat.name='357 rich indigo '+ob.name
            finish.material(bpy,mat,(.006,.019,.065),(.017,.045,.135),650)
        changed.append(ob.name)
    rig['fabric357']=1;bpy.context.view_layer.update()
    if h.action_signature(bpy)!=sig:raise ValueError('FABRIC357_ACTION_DRIFT')
    report=dict(changed=True,source_preserved=True,actions_unchanged=True,action_signature=sig,max_fold=max(deltas),moved_vertices=sum(x>.0001 for x in deltas),boundary_fixed=max(deltas[i] for i in ids),materials=changed,scope='Small elbow compression folds and richer existing indigo palette, not cloth simulation; pose/contact review required.')
    (out/'fabric357.json').write_text(json.dumps(report,indent=2)+'\n');return report
