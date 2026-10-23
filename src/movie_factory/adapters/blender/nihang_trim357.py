"""Rebuild sewn trim from the current garment topology and skin weights."""
from collections import Counter,defaultdict
import json,importlib.util
from pathlib import Path

def loops(faces):
    counts=Counter(tuple(sorted((a,b))) for f in faces for a,b in zip(f,(*f[1:],f[0])))
    adj=defaultdict(list)
    for (a,b),n in counts.items():
        if n==1:adj[a].append(b);adj[b].append(a)
    if any(len(v)!=2 for v in adj.values()):raise ValueError('TRIM357_NONMANIFOLD_BOUNDARY')
    unseen=set(adj);out=[]
    while unseen:
        first=min(unseen);row=[first];prev=None;cur=first
        while True:
            nxt=next(v for v in adj[cur] if v!=prev)
            if nxt==first:break
            if nxt in row:raise ValueError('TRIM357_BRANCH')
            row.append(nxt);prev,cur=cur,nxt
        unseen.difference_update(row);out.append(row)
    return out

def run(bpy,out):
    from mathutils import Matrix,Vector
    from mathutils.bvhtree import BVHTree
    def load(name):
        s=importlib.util.spec_from_file_location(name,Path(__file__).with_name('nihang_'+name+'.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
    h=load('tack354');mats=load('whole347');sig=h.action_signature(bpy)
    rig=bpy.data.objects['MF coherent Nihang rig'];coat=bpy.data.objects['MF coherent coat']
    if not rig.get('surface357') or rig.get('trim357'):raise ValueError('TRIM357_PARENT')
    mesh=coat.data;faces=[tuple(p.vertices) for p in mesh.polygons];boundaries=loops(faces)
    incident=defaultdict(list)
    for f in mesh.polygons:
        for i in f.vertices:incident[i].append(f.center.copy())
    pts=[];polys=[];weights=[];selected=[]
    def row(v):return [(coat.vertex_groups[g.group].name,g.weight) for g in v.groups if coat.vertex_groups[g.group].name in rig.data.bones]
    for loop in boundaries:
        meanz=sum(mesh.vertices[i].co.z for i in loop)/len(loop)
        if meanz<1.15:continue
        selected.append(dict(vertices=len(loop),mean_z=meanz));start=len(pts)
        for i in loop:
            v=mesh.vertices[i];normal=v.normal.normalized();inner=sum(incident[i],Vector())/len(incident[i])-v.co
            inner-=normal*inner.dot(normal);inner.normalize()
            for p in (v.co+normal*.003,v.co+inner*.006+normal*.0025):pts.append(p);weights.append(row(v))
        for j in range(len(loop)):
            a=start+2*j;b=start+2*((j+1)%len(loop));polys.append((a,b,b+1,a+1))
    if not selected:raise ValueError('TRIM357_NO_BOUNDARIES')
    tree=BVHTree.FromPolygons([v.co for v in mesh.vertices],faces)
    previous=None;placket=0
    for j in range(32):
        z=1.25+.33*j/31;pair=[]
        for x in (.014,.025):
            hit,n,idx,_=tree.ray_cast(Vector((x,-.7,z)),Vector((0,1,0)))
            if hit is None:break
            pair.append((hit+n*.003,mesh.vertices[min(faces[idx],key=lambda i:(mesh.vertices[i].co-hit).length)]))
        if len(pair)!=2:previous=None;continue
        start=len(pts)
        for p,v in pair:pts.append(p);weights.append(row(v))
        if previous is not None:polys.append((previous,previous+1,start+1,start));placket+=1
        previous=start
    data=bpy.data.meshes.new('357 continuous current-coat trim');data.from_pydata(pts,[],polys);data.update()
    ob=bpy.data.objects.new('MF357 sewn current neckline cuffs placket',data);bpy.context.scene.collection.objects.link(ob)
    ob.parent=rig;ob.matrix_parent_inverse=Matrix.Identity(4);ob.matrix_basis=coat.matrix_basis.copy()
    mat=coat.data.materials[0].copy();mat.name='357 indigo sewn binding';mats.material(bpy,mat,(.010,.019,.039),(.018,.034,.065),650);data.materials.append(mat)
    for i,wr in enumerate(weights):
        total=sum(w for _,w in wr)
        if total<.5:raise ValueError('TRIM357_WEIGHT')
        for name,w in wr:(ob.vertex_groups.get(name) or ob.vertex_groups.new(name=name)).add([i],w/total,'REPLACE')
    arm=ob.modifiers.new('357 actual coat skeleton','ARMATURE');arm.object=rig;arm.use_deform_preserve_volume=True
    sub=ob.modifiers.new('357 continuous stitched binding','SUBSURF');sub.levels=1;sub.render_levels=1
    solid=ob.modifiers.new('357 turned fabric thickness','SOLIDIFY');solid.thickness=.001
    for p in data.polygons:p.use_smooth=True
    old=bpy.data.objects.get('MF347 chola neckline cuff and placket')
    if old:old.hide_render=True;old.hide_viewport=True
    # Material only on preserved draped surfaces; never move cloth to hide gaps.
    changed=[]
    for item in rig.children_recursive:
        if item.type!='MESH' or not item.name.startswith(('MF coherent coat','MF coherent split chola','MF coherent pants','MF coherent shoulder sash','MF coherent waist wrap')):continue
        for i,source in enumerate(item.data.materials):
            mat=source.copy();item.data.materials[i]=mat
            ochre=item.name.startswith(('MF coherent shoulder sash','MF coherent waist wrap'))
            low,high=((.16,.074,.017),(.29,.15,.038)) if ochre else ((.013,.026,.053),(.028,.051,.092))
            mats.material(bpy,mat,low,high,650)
            # Thread structure is anisotropic in object space, restrained enough
            # not to become chainmail or unrelated wallpaper.
            n=mat.node_tree.nodes;l=mat.node_tree.links;bs=next(x for x in n if x.type=='BSDF_PRINCIPLED')
            tex=n.new('ShaderNodeTexCoord');wave=n.new('ShaderNodeTexWave');wave.bands_direction='X';wave.inputs['Scale'].default_value=380;wave.inputs['Distortion'].default_value=2
            l.new(tex.outputs['Object'],wave.inputs['Vector']);bump=n.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.12;bump.inputs['Distance'].default_value=.00015
            l.new(bs.inputs['Normal'].links[0].from_socket,bump.inputs['Normal']);l.new(wave.outputs['Fac'],bump.inputs['Height']);l.new(bump.outputs[0],bs.inputs['Normal'])
        changed.append(item.name)
    rig['trim357']=1;bpy.context.view_layer.update()
    if h.action_signature(bpy)!=sig:raise ValueError('TRIM357_ACTION_DRIFT')
    report=dict(changed=True,source_preserved=True,actions_unchanged=True,action_signature=sig,loops=selected,placket_segments=placket,vertices=len(pts),materials=changed,old_trim_retained_hidden=bool(old),scope='Current coat topology/weights, no obsolete trim projection. Actual posed interfaces remain mandatory.')
    (out/'trim357.json').write_text(json.dumps(report,indent=2)+'\n');return report
