"""Closed local topology/skin graft with original mesh archive and live rig.

Only bound inert arrays are accepted. Mode0 qualifies the BMesh roundtrip;
mode1 replaces the declared local faces and binding. Art remains unqualified.
"""
import hashlib,json,zipfile
from collections import Counter
from pathlib import Path
import numpy as np

FIELDS={'source_rest','source_weights','group_names','deform_mask','remove_polygons','vertices','faces','weights','source_boundary'}

def validate(e):
    if not isinstance(e,dict) or set(e)!={'kind','target','mode','data'} or e.get('kind')!='mounted_forequarter390_graft' or e.get('target')!='horse' or type(e.get('mode')) is not int or e['mode'] not in (0,1):raise ValueError('GRAFT390_FIELDS')
    b=e['data']
    if not isinstance(b,dict) or set(b)!={'path','sha256'} or not isinstance(b['path'],str) or not b['path'].startswith('.runtime/art-direction/anatomy390-targets/') or '..' in Path(b['path']).parts or not b['path'].endswith('.npz') or len(b.get('sha256',''))!=64 or any(c not in '0123456789abcdef' for c in b['sha256']):raise ValueError('GRAFT390_BINDING')
    return e


def boundary_vertices(polygons):
    counts=Counter()
    for row in polygons:
        p=[int(x) for x in row if x>=0]
        if len(p) not in (3,4) or len(set(p))!=len(p):raise ValueError('GRAFT390_DELETE_POLYGON')
        for a,b in zip(p,p[1:]+p[:1]):counts[tuple(sorted((a,b)))]+=1
    if any(c>2 for c in counts.values()):raise ValueError('GRAFT390_DELETE_MANIFOLD')
    return {v for edge,c in counts.items() if c==1 for v in edge}


def load(root,b):
    path=(root/b['path']).resolve()
    if not path.is_relative_to(root.resolve()) or path.stat().st_size>32*1024*1024 or hashlib.sha256(path.read_bytes()).hexdigest()!=b['sha256']:raise ValueError('GRAFT390_STALE')
    with zipfile.ZipFile(path) as z:
        if sum(x.file_size for x in z.infolist())>64*1024*1024:raise ValueError('GRAFT390_ARRAY_SIZE')
    with np.load(path,allow_pickle=False) as z:
        if set(z.files)!=FIELDS:raise ValueError('GRAFT390_ARRAY_FIELDS')
        q={k:z[k].copy() for k in z.files}
    n=len(q['vertices']);f=q['faces'];w=q['weights'];remove=q['remove_polygons']
    if q['source_rest'].shape!=(22514,3) or q['source_weights'].shape!=(22514,84) or q['group_names'].shape!=(84,) or q['deform_mask'].shape!=(84,) or not 100<=n<=4000 or q['vertices'].shape!=(n,3) or w.shape!=(n,84):raise ValueError('GRAFT390_ARRAY_SHAPES')
    if f.ndim!=2 or f.shape[1]!=3 or f.dtype.kind not in 'iu' or len(f)>16000 or f.min()<0 or f.max()>=22514+n or remove.ndim!=2 or remove.shape[1]!=4 or remove.dtype.kind not in 'iu' or not 500<=len(remove)<=5000:raise ValueError('GRAFT390_TOPOLOGY_ARRAYS')
    for k in ('source_rest','source_weights','vertices','weights'):
        if not np.isfinite(q[k]).all():raise ValueError('GRAFT390_NONFINITE')
    if (w<0).any() or (w>1.000001).any() or abs(w[:,q['deform_mask'].astype(bool)].sum(1)-1).max()>2e-5:raise ValueError('GRAFT390_WEIGHTS')
    boundary=boundary_vertices(remove)
    if boundary!=set(map(int,q['source_boundary'])) or not set(map(int,f[f<22514]))<=boundary:raise ValueError('GRAFT390_BOUNDARY_REFERENCES')
    if len({tuple(sorted(map(int,t))) for t in f})!=len(f) or any(len(set(map(int,t)))!=3 for t in f):raise ValueError('GRAFT390_DUPLICATE_FACE')
    v=q['vertices']
    if abs(v[:,0]).max()>.46 or v[:,1].min()<-1.42 or v[:,1].max()>-.15 or v[:,2].min()<.70 or v[:,2].max()>2.12:raise ValueError('GRAFT390_REGION')
    return q


def run(bpy,out,e,helpers):
    validate(e);root=Path(__file__).resolve().parents[4];q=load(root,e['data']);horse=bpy.data.objects['horse'];rig=bpy.data.objects['horse.rig'];scene=helpers('nihang_support').select_production_scene(bpy)
    if any(horse.get(k) for k in ('cache376','probe389','graft390')) or len(horse.data.vertices)!=22514:raise ValueError('GRAFT390_ORIGINAL_SOURCE')
    old=horse.data;oldkeys=old.shape_keys.key_blocks
    if tuple(k.name for k in oldkeys)!=('Basis','corr.neck','corr.chin','corr.neck.2'):raise ValueError('GRAFT390_KEYS')
    raw=np.array([v.co[:] for v in old.vertices],np.float32);shapes={k.name:np.array([v.co[:] for v in k.data],np.float32) for k in oldkeys}
    if abs(raw-q['source_rest']).max()>2e-6 or abs(shapes['Basis']-q['source_rest']).max()>2e-6:raise ValueError('GRAFT390_REST_SOURCE')
    names,weights=helpers('anatomy_bind386').weights(horse)
    if names!=list(q['group_names']) or not np.array_equal(weights,q['source_weights']):raise ValueError('GRAFT390_WEIGHT_SOURCE')
    actual_deform=np.array([bool(rig.data.bones.get(n) and rig.data.bones[n].use_deform) for n in names])
    if not np.array_equal(actual_deform,q['deform_mask']):raise ValueError('GRAFT390_DEFORM_FLAGS')
    actions=helpers('nihang_padsolve370').actions(bpy);geometry=helpers('nihang_prep367').frozen(bpy);cap=helpers('anatomy_muscle386');bones=[p.name for p in rig.pose.bones]
    before,mb=cap.capture(bpy,horse,rig,bones,helpers)
    oldedges=np.array([a.vertices[:] for a in old.edges]);source_main=helpers('anatomy_domain386').main_skin(oldedges,len(raw))
    old_uv={layer.name:np.array([x.uv[:] for x in layer.data],np.float32) for layer in old.uv_layers}
    old_polys={frozenset(p.vertices[:]):(p.index,p.vertices[:],p.loop_indices[:]) for p in old.polygons}
    delete={frozenset(map(int,row[row>=0])) for row in q['remove_polygons']}
    if len(delete)!=len(q['remove_polygons']) or not delete<=set(old_polys):raise ValueError('GRAFT390_DELETE_SOURCE')
    deleted_indices={old_polys[key][0] for key in delete}
    selected=np.unique(np.concatenate([list(key) for key in delete]));v=raw[selected]
    if not source_main[selected].all() or abs(v[:,0]).max()>.46 or v[:,1].min()<-1.42 or v[:,1].max()>-.15 or v[:,2].min()<.70 or v[:,2].max()>2.12:raise ValueError('GRAFT390_DELETE_REGION')
    headcols=[names.index(n) for n in ('DEF-head','DEF-eye.L','DEF-eye.R','DEF-jaw','DEF-jaw.001')]
    if (weights[selected][:,headcols].sum(1)>.05).any():raise ValueError('GRAFT390_HEAD_OWNERSHIP')
    # Independent data copy retains original keys/drivers and original UV/polys.
    new=old.copy()
    if new.shape_keys is old.shape_keys:raise ValueError('GRAFT390_SHARED_KEYS')
    new.name='390 local forequarter derivative';horse.data=new;old.use_fake_user=True
    import bmesh
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    bm=bmesh.new();bm.from_mesh(new,use_shape_key=True,shape_key_index=0);bm.verts.ensure_lookup_table();bm.faces.ensure_lookup_table();bm.verts.index_update();bm.faces.index_update()
    vi=bm.verts.layers.int.new('source_vertex390');pi=bm.verts.layers.int.new('patch_vertex390');fi=bm.faces.layers.int.new('source_face390')
    for x in bm.verts:x[vi]=x.index;x[pi]=-1
    for x in bm.faces:x[fi]=x.index
    layer_names=list(bm.verts.layers.shape.keys())
    if not set(shapes)<=set(layer_names):raise ValueError('GRAFT390_SHAPE_LAYERS')
    if e['mode']:
        old.calc_loop_triangles();tri=[t for t in old.loop_triangles if t.polygon_index in deleted_indices];indices=[t.vertices[:] for t in tri];bvh=BVHTree.FromPolygons([Vector(v) for v in raw],indices,all_triangles=True)
        uv_tri={name:np.array([values[list(t.loops)] for t in tri]) for name,values in old_uv.items()}
        def correspondence(position):
            result=bvh.find_nearest(Vector(position));nearest,normal,index,distance=result
            if index is None:raise ValueError('GRAFT390_UV_CORRESPONDENCE')
            a,b,c=raw[indices[index]].astype(float);d=np.array(nearest)-a;ab=b-a;ac=c-a;aa=ab@ab;bb=ab@ac;cc=ac@ac;den=aa*cc-bb*bb
            if den<1e-14:raise ValueError('GRAFT390_DEGENERATE_SOURCE')
            u=(cc*(d@ab)-bb*(d@ac))/den;v=(aa*(d@ac)-bb*(d@ab))/den;bc=np.maximum(np.array([1-u-v,u,v]),0);bc/=bc.sum()
            return int(index),bc
        to_delete=[face for face in bm.faces if face[fi] in deleted_indices];candidates={v for f in to_delete for v in f.verts}
        bmesh.ops.delete(bm,geom=to_delete,context='FACES_ONLY');unused=[v for v in candidates if not v.link_faces]
        if unused:bmesh.ops.delete(bm,geom=unused,context='VERTS')
        lookup={v[vi]:v for v in bm.verts};deform_layer=bm.verts.layers.deform.verify()
        for j,co in enumerate(q['vertices']):
            vert=bm.verts.new(co);vert[vi]=-1;vert[pi]=j;lookup[22514+j]=vert;index,bc=correspondence(co);source_ids=np.array(indices[index])
            for name,original in shapes.items():vert[bm.verts.layers.shape[name]]=Vector(co+bc@(original[source_ids]-shapes['Basis'][source_ids]))
            for k,value in enumerate(q['weights'][j]):
                if value>0:vert[deform_layer][k]=float(value)
        main_material=old.polygons[next(iter(deleted_indices))].material_index
        uv_layers={name:bm.loops.layers.uv.get(name) for name in old_uv}
        for row in q['faces']:
            try:face=bm.faces.new([lookup[int(i)] for i in row])
            except (KeyError,ValueError) as error:raise ValueError('GRAFT390_FACE_BUILD') from error
            face[fi]=-1;face.material_index=main_material;face.smooth=True;center=np.mean([x.co[:] for x in face.verts],axis=0)
            for loop in face.loops:
                index,bc=correspondence(np.array(loop.vert.co)*.999+center*.001)
                for name,layer in uv_layers.items():loop[layer].uv=Vector(bc@uv_tri[name][index])
    bm.normal_update();bm.to_mesh(new);bm.free();new.update();horse.update_tag(refresh={'DATA'});bpy.context.view_layer.update()
    srcid=np.array([v.value for v in new.attributes['source_vertex390'].data],int);patchid=np.array([v.value for v in new.attributes['patch_vertex390'].data],int);srcface=np.array([v.value for v in new.attributes['source_face390'].data],int);kept=srcid>=0
    if e['mode'] and sorted(patchid[~kept].tolist())!=list(range(len(q['vertices']))):raise ValueError('GRAFT390_PATCH_MAP')
    expected_faces=set(range(len(old.polygons)))-(deleted_indices if e['mode'] else set())
    if set(map(int,srcface[srcface>=0]))!=expected_faces:raise ValueError('GRAFT390_RETAINED_FACE_SET')
    if len(np.unique(srcid[kept]))!=int(kept.sum()) or len(names)!=len(horse.vertex_groups):raise ValueError('GRAFT390_SOURCE_MAP')
    newshapes={k.name:np.array([v.co[:] for v in k.data],np.float32) for k in new.shape_keys.key_blocks}
    shape_error=max(float(abs(newshapes[n][kept]-a[srcid[kept]]).max()) for n,a in shapes.items())
    _,newweights=helpers('anatomy_bind386').weights(horse);weight_error=float(abs(newweights[kept]-weights[srcid[kept]]).max());uv_error=0.
    for face in new.polygons:
        oldid=srcface[face.index]
        if oldid<0:continue
        original=old.polygons[int(oldid)];by_vertex={v:i for v,i in zip(original.vertices,original.loop_indices)}
        for vertex,loop in zip(face.vertices,face.loop_indices):
            old_vertex=int(srcid[vertex])
            if old_vertex not in by_vertex:raise ValueError('GRAFT390_OLD_FACE_DRIFT')
            for layer in new.uv_layers:uv_error=max(uv_error,float(np.max(np.abs(np.array(layer.data[loop].uv)-old_uv[layer.name][by_vertex[old_vertex]]))))
    after,ma=cap.capture(bpy,horse,rig,bones,helpers);outside=float(abs(after[:,kept]-before[:,srcid[kept]]).max());matrix=float(abs(ma-mb).max());other=helpers('nihang_prep367').frozen(bpy);geometry.pop('horse');other.pop('horse');new_actions=helpers('nihang_padsolve370').actions(bpy)
    preserved=geometry==other and all(new_actions.get(n)==a for n,a in actions.items())
    actual_raw=np.array([v.co[:] for v in new.vertices],np.float32)
    new_rest_error=float(abs(actual_raw[~kept]-q['vertices'][patchid[~kept]]).max()) if e['mode'] else 0.
    new_weight_error=float(abs(newweights[~kept]-q['weights'][patchid[~kept]]).max()) if e['mode'] else 0.
    if max(new_rest_error,new_weight_error)>2e-6:raise ValueError('GRAFT390_PATCH_DATA')
    new.calc_loop_triangles();faces=np.array([t.vertices[:] for t in new.loop_triangles]);on_skin=(srcid<0);on_skin[kept]=source_main[srcid[kept]];faces=faces[np.all(on_skin[faces],axis=1)];relevant=np.any(srcid[faces]<0,axis=1);surface=[]
    if e['mode']:
        for frame in [283,333,339,346]:
            i=cap.FRAMES.index(frame);cross=helpers('anatomy_bind386').crossing_pairs(after[i],faces,relevant);surface.append(dict(frame=frame,new_region_intersections=len(cross)))
    result=dict(mode=e['mode'],original_vertices=len(raw),new_vertices=len(new.vertices),new_surface_vertices=int((srcid<0).sum()),retained_vertices=int(kept.sum()),removed_polygons=len(deleted_indices) if e['mode'] else 0,shape_layers=layer_names,new_rest_error=new_rest_error,new_weight_error=new_weight_error,original_shape_error=shape_error,original_weight_error=weight_error,original_uv_error=uv_error,outside_cage_error=outside,primary_matrix_error=matrix,other_geometry_and_old_actions_preserved=preserved,surface_diagnostics=surface,scope='Local original-horse topology/binding derivative. Actual native anatomy and complete motion/coat/contact remain unqualified; zero mode is transport only.')
    np.savez_compressed(out/'anatomy390-graft.npz',source_id=srcid,patch_id=patchid,source_face_id=srcface,raw=actual_raw,source_pose=before,target_pose=after,rig_before=mb,rig_after=ma,frames=np.array(cap.FRAMES),triangles=faces)
    (out/'anatomy390-graft.json').write_text(json.dumps(result,indent=2)+'\n')
    if max(shape_error,weight_error,uv_error)>2e-6 or outside>2e-5 or matrix>1e-7 or not preserved:raise ValueError('GRAFT390_PRESERVATION')
    if not e['mode'] and (len(new.vertices)!=22514 or (srcid<0).any()):raise ValueError('GRAFT390_ZERO')
    if e['mode']:horse['graft390']=e['data']['sha256']
    result['diagnostic_render_profile']=helpers('anatomy_static387').freeze(scene)
    (out/'anatomy390-graft.json').write_text(json.dumps(result,indent=2)+'\n');return result
