"""Construct a local four-boundary anatomical graft and harmonic skin binding.

Inert numeric inputs only. No Blender/provider launch and no artistic PASS.
"""
from pathlib import Path
from collections import defaultdict,Counter
import json
import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.linalg import factorized
from scipy.sparse.csgraph import dijkstra
from scipy.optimize import minimize
from itertools import combinations
from movie_factory.adapters.blender.anatomy_domain386 import main_skin
from movie_factory.adapters.blender.anatomy_bind386 import crossing_pairs
from anatomy386_structural387 import arap


def polygon_edges(polys):
    return [(int(a),int(b)) for p in polys for a,b in zip(p,np.roll(p,-1))]


def recover_polygons(tris,edges):
    """Recover original polygon boundaries from triangulation and true edges."""
    true={tuple(sorted(map(int,e))) for e in edges};owner={};parent=np.arange(len(tris))
    def find(i):
        while parent[i]!=i:parent[i]=parent[parent[i]];i=int(parent[i])
        return i
    for i,t in enumerate(tris):
        for a,b in zip(t,np.roll(t,-1)):
            e=tuple(sorted((int(a),int(b))))
            if e in true:continue
            if e in owner:parent[find(i)]=find(owner[e])
            else:owner[e]=i
    groups=defaultdict(list)
    for i in range(len(tris)):groups[find(i)].append(i)
    polygons=[];members=[]
    for ids in groups.values():
        c=Counter(tuple(sorted(e)) for e in polygon_edges(tris[ids]));boundary=[e for e in polygon_edges(tris[ids]) if c[tuple(sorted(e))]==1]
        nxt={a:b for a,b in boundary}
        if len(nxt)!=len(boundary):raise ValueError('GRAFT390_POLYGON_BOUNDARY')
        start=boundary[0][0];p=[start]
        while nxt[p[-1]]!=start:
            p.append(nxt[p[-1]])
            if len(p)>len(boundary):raise ValueError('GRAFT390_POLYGON_CYCLE')
        if len(p)!=len(boundary) or len(p) not in (3,4):raise ValueError('GRAFT390_POLYGON_SIZE')
        polygons.append(np.array(p,dtype=np.int32));members.append(ids)
    return polygons,members


def largest_face_component(polys,selected):
    owners=defaultdict(list)
    for i in np.flatnonzero(selected):
        for e in polygon_edges([polys[i]]):owners[tuple(sorted(e))].append(int(i))
    adj=defaultdict(list)
    for ids in owners.values():
        if len(ids)==2:adj[ids[0]].append(ids[1]);adj[ids[1]].append(ids[0])
    seen=set();components=[]
    for i in np.flatnonzero(selected):
        if i in seen:continue
        todo=[int(i)];comp=[]
        while todo:
            k=todo.pop()
            if k in seen:continue
            seen.add(k);comp.append(k);todo.extend(adj[k])
        components.append(comp)
    if not components:raise ValueError('GRAFT390_EMPTY_PATCH')
    keep=np.zeros(len(polys),bool);keep[max(components,key=len)]=True
    return keep


def boundary_loops(polys):
    c=Counter(tuple(sorted(e)) for e in polygon_edges(polys));boundary=[e for e in polygon_edges(polys) if c[tuple(sorted(e))]==1]
    nxt={a:b for a,b in boundary}
    if len(nxt)!=len(boundary) or len(set(nxt.values()))!=len(boundary):raise ValueError('GRAFT390_NONMANIFOLD_BOUNDARY')
    seen=set();loops=[]
    for start in nxt:
        if start in seen:continue
        p=[];k=start
        while k not in seen:seen.add(k);p.append(k);k=nxt[k]
        if k!=start:raise ValueError('GRAFT390_OPEN_BOUNDARY')
        loops.append(np.array(p,dtype=np.int32))
    return loops


def semantic_loops(v,loops):
    result={}
    for loop in loops:
        center=v[loop].mean(0)
        label=('legL' if center[0]>0 else 'legR') if center[2]<1.05 else ('barrel' if center[1]>-.5 else 'neck')
        if label in result:raise ValueError('GRAFT390_AMBIGUOUS_RING')
        # Stable anatomical start, keeping actual face orientation.
        start=int(np.argmax(v[loop,0]));result[label]=np.roll(loop,-start)
    if set(result)!={'legL','legR','barrel','neck'}:raise ValueError('GRAFT390_RING_COVERAGE')
    return result


def fractions(points):
    d=np.linalg.norm(np.roll(points,-1,axis=0)-points,axis=1)
    if (d<1e-8).any():raise ValueError('GRAFT390_ZERO_RING_EDGE')
    return np.r_[0,np.cumsum(d)[:-1]]/d.sum()


def sample_ring(points,u,geometry=None):
    t=fractions(points if geometry is None else geometry);xp=np.r_[t,1.];a=np.vstack([points,points[0]])
    return np.stack([np.interp(u,xp,a[:,j]) for j in range(points.shape[1])],axis=1)


def harmonic(v,edges,fixed,values):
    n=len(v);a,b=edges.T;deg=np.bincount(edges.ravel(),minlength=n)
    lap=coo_matrix((np.r_[deg,-np.ones(len(a)),-np.ones(len(a))],(np.r_[np.arange(n),a,b],np.r_[np.arange(n),b,a])),shape=(n,n)).tocsr()
    free=np.ones(n,bool);free[fixed]=False;ids=np.flatnonzero(free);out=np.zeros((n,values.shape[1]));out[fixed]=values
    if len(ids):out[ids]=factorized(lap[ids][:,ids].tocsc())(-lap[ids][:,fixed]@values)
    return out


def zipper(s,d,sv,dv):
    a=np.r_[fractions(sv),1.];b=np.r_[fractions(dv),1.];i=j=0;out=[];n=len(s);m=len(d)
    while i<n or j<m:
        if j==m or (i<n and a[i+1]<=b[j+1]):out.append([s[i%n],s[(i+1)%n],d[j%m]]);i+=1
        else:out.append([s[i%n],d[(j+1)%m],d[j%m]]);j+=1
    return np.array(out,dtype=np.int32)


def collar_controls(rest,initial,edges,loops,planes):
    a,b=edges.T;length=np.linalg.norm(rest[a]-rest[b],axis=1);graph=coo_matrix((np.r_[length,length],(np.r_[a,b],np.r_[b,a])),shape=(len(rest),len(rest))).tocsr()
    boundary={int(i) for loop in loops.values() for i in loop};constraints=defaultdict(list)
    for name,loop in loops.items():
        ring=set(map(int,loop));neighbors={int(v) for e in edges if int(e[0]) in ring or int(e[1]) in ring for v in e}-boundary
        distance=dijkstra(graph,directed=False,indices=loop,min_only=True);normal,plane=planes[name]
        for j in neighbors:constraints[j].append((normal,plane-float(distance[j])))
    ids=np.array(sorted(constraints),int);positions=initial[ids].copy()
    for i,j in enumerate(ids):
        for _ in range(12):
            for normal,plane in constraints[int(j)]:
                error=float(positions[i]@normal-plane)
                if error>0:positions[i]-=error*normal
        if any(positions[i]@normal>plane+1e-7 for normal,plane in constraints[int(j)]):raise ValueError('GRAFT390_COLLAR_CONSTRAINT')
    return ids,positions




def separating_axis(a,b):
    """SAT candidates for the small convex contact patches; fail if not proven."""
    candidates=[b.mean(0)-a.mean(0)]
    for points in (a,b):
        candidates += [np.cross(points[j]-points[i],points[k]-points[i]) for i,j,k in combinations(range(len(points)),3)]
    ea=[a[j]-a[i] for i,j in combinations(range(len(a)),2)]
    eb=[b[j]-b[i] for i,j in combinations(range(len(b)),2)]
    candidates += [np.cross(x,y) for x in ea for y in eb]
    best=None
    for axis in candidates:
        length=np.linalg.norm(axis)
        if length<1e-10:continue
        axis=axis/length
        for normal in (axis,-axis):
            gap=float((b@normal).min()-(a@normal).max())
            if best is None or gap>best[0]:best=(gap,normal)
    if best is None or best[0]<=1e-7:raise ValueError('GRAFT390_NO_REFERENCE_SEPARATION')
    return best


def contact_separation(vertices,reference,faces,edges,fixed):
    pairs=crossing_pairs(vertices,faces,np.ones(len(faces),bool))
    if not pairs:return vertices.copy(),dict(contact_pairs=0,max_delta=0.)
    # Group actually intersecting faces by shared vertices, not arbitrary radius.
    face_ids=sorted({int(x) for pair in pairs for x in pair});groups=[]
    for i in face_ids:
        vertices_i=set(map(int,faces[i]));touch=[k for k,g in enumerate(groups) if vertices_i & g]
        if not touch:groups.append(vertices_i)
        else:
            merged=vertices_i|set().union(*(groups[k] for k in touch));groups=[g for k,g in enumerate(groups) if k not in touch]+[merged]
    if len(groups)!=2:raise ValueError('GRAFT390_CONTACT_COMPONENTS:'+str(len(groups)))
    a,b=[np.array(sorted(g),int) for g in groups];gap,normal=separating_axis(reference[a],reference[b])
    project=vertices@normal;plane=.5*(float(project[a].max())+float(project[b].min()));margin=.0005
    low=np.full(len(vertices),-.03);high=np.full(len(vertices),.03)
    high[a]=np.minimum(high[a],plane-margin-project[a]);low[b]=np.maximum(low[b],plane+margin-project[b]);low[fixed]=0;high[fixed]=0
    if (low>high).any():raise ValueError('GRAFT390_CONTACT_BOUNDS_INFEASIBLE')
    ea,eb=edges.T
    def objective(d):
        edge=d[ea]-d[eb];energy=.5*float(edge@edge)+.05*float(d@d);grad=.1*d.copy();np.add.at(grad,ea,edge);np.add.at(grad,eb,-edge);return energy,grad
    initial=np.clip(np.zeros(len(vertices)),low,high)
    result=minimize(objective,initial,jac=True,bounds=list(zip(low,high)),method='L-BFGS-B',options={'maxiter':500,'ftol':1e-14,'gtol':1e-9})
    if not result.success:raise ValueError('GRAFT390_CONTACT_QP:'+result.message)
    target=vertices+result.x[:,None]*normal
    if abs(result.x).max()>.030001 or abs(result.x[fixed]).max()>1e-10:raise ValueError('GRAFT390_CONTACT_SCOPE')
    if (target[a]@normal).max()>plane-margin+1e-7 or (target[b]@normal).min()<plane+margin-1e-7:raise ValueError('GRAFT390_CONTACT_CONSTRAINT')
    return target,dict(contact_pairs=len(pairs),groups=[len(a),len(b)],reference_separation=gap,normal=normal.tolist(),plane=plane,margin=margin,max_delta=float(abs(result.x).max()),iterations=int(result.nit),scope='Static new-mesh contact separation only; no simulated-motion claim.')


def build(root):
    q=np.load(root/'.runtime/factory-native/sikh386-appearance-c193-source/anatomy386-source.npz',allow_pickle=False)
    old=np.load(root/'.runtime/factory-native/sikh374-appearance-c124-inspect/horse-form374.npz',allow_pickle=False)
    guide=np.load(root/'.runtime/art-direction/anatomy386-references/lyndon-body-reference.npz',allow_pickle=False)
    rigdata=np.load(root/'.runtime/factory-native/sikh375-appearance-c129-inspect/horse-deform375.npz',allow_pickle=False)
    deform_by_name=dict(zip(map(str,rigdata['names']),map(bool,rigdata['deform'])));deform=np.array([deform_by_name.get(str(n),False) for n in q['group_names']]);assert deform.sum()==80
    v=q['rest'].astype(float);tris=old['triangles'];skin=main_skin(q['edges'],len(v));polys,members=recover_polygons(tris,q['edges'])
    centers=np.array([v[p].mean(0) for p in polys]);all_skin=np.array([skin[p].all() for p in polys]);source_axis=np.array([0.,-.6,.8]);source_cut=(centers-np.array([0.,-.85,1.82]))@source_axis
    headcols=[list(q['group_names']).index(n) for n in ('DEF-head','DEF-eye.L','DEF-eye.R','DEF-jaw','DEF-jaw.001')];head=(q['weights'][:,headcols].sum(1)>.05);headface=np.array([head[p].any() for p in polys])
    selected=all_skin&~headface&(centers[:,1]<-.28)&(centers[:,2]>.82)&(source_cut<0)
    selected=largest_face_component(polys,selected);removed=[p for p,s in zip(polys,selected) if s];sloops=semantic_loops(v,boundary_loops(removed))
    gv=guide['vertices'].astype(float);gf=guide['faces'].copy();volume=lambda x,f:float(np.sum(np.einsum('ij,ij->i',x[f[:,0]],np.cross(x[f[:,1]],x[f[:,2]])))/6)
    if volume(v,tris[np.all(skin[tris],axis=1)])*volume(gv,gf)<0:gf=gf[:,::-1]
    center=gv[gf].mean(1);guide_cut=(center-np.array([0.,-1.,1.78]))@source_axis;gs=(center[:,1]<-.28)&(center[:,2]>.82)&(guide_cut<0);gs=largest_face_component(list(gf),gs)
    used=np.unique(gf[gs]);index=np.full(len(gv),-1);index[used]=np.arange(len(used));patch_v=gv[used];patch_f=index[gf[gs]];dloops=semantic_loops(patch_v,boundary_loops(list(patch_f)))
    edges=np.unique(np.sort(np.concatenate([patch_f[:,[0,1]],patch_f[:,[1,2]],patch_f[:,[2,0]]]),axis=1),axis=0)
    fixed=[];targets=[];weights=[];ring_data={};planes={};offsets={'neck':np.array([0,0,-.05]),'barrel':np.array([0,-.05,0]),'legL':np.array([0,0,.05]),'legR':np.array([0,0,.05])}
    for label,sloop in sloops.items():
        dloop=dloops[label];u=fractions(patch_v[dloop]);target=sample_ring(v[sloop],u)
        # Place each inner ring beyond the whole jagged outer boundary, not
        # a constant shift that can remain inside its extreme vertices.
        normal=source_axis if label=='neck' else (np.array([0.,1.,0.]) if label=='barrel' else np.array([0.,0.,-1.]))
        plane=float((v[sloop]@normal).min())-.06;planes[label]=(normal,plane)
        target-=((target@normal)-plane)[:,None]*normal
        fixed.extend(dloop);targets.extend(target);weights.extend(sample_ring(q['weights'][sloop],u,geometry=v[sloop]));ring_data[label]=dict(source_vertices=len(sloop),patch_vertices=len(dloop),target_center=target.mean(0).tolist())
    fixed=np.array(fixed);targets=np.array(targets);boundaryweights=np.array(weights)
    labels=['neck','barrel','legL','legR'];source_centers=np.array([patch_v[dloops[k]].mean(0) for k in labels]);target_by_vertex={int(i):a for i,a in zip(fixed,targets)};target_centers=np.array([np.array([target_by_vertex[int(i)] for i in dloops[k]]).mean(0) for k in labels]);affine=np.linalg.solve(np.c_[source_centers,np.ones(4)],target_centers);affine_det=float(np.linalg.det(affine[:3]));affine_sv=np.linalg.svd(affine[:3])[1]
    if affine_det<=0 or affine_sv.min()<.3 or affine_sv.max()>3:raise ValueError('GRAFT390_AFFINE_FRAME')
    patch_v=np.c_[patch_v,np.ones(len(patch_v))]@affine
    # Move boundary through a sequence of small proper deformations, rather
    # than initialize the nonlinear solve from a folded full-displacement warp.
    free=np.ones(len(patch_v),bool);free[fixed]=False
    fitted=patch_v.copy();last_clean=fitted.copy();path_audit=[];history=[];base=patch_v[fixed].copy()
    for step in range(1,25):
        goal=base+(targets-base)*(step/24.)
        proposal=fitted+harmonic(patch_v,edges,fixed,goal-fitted[fixed])
        fitted,changes=arap(patch_v,proposal,edges,free,iterations=36)
        history.extend(changes)
        count=len(crossing_pairs(fitted,patch_f,np.ones(len(patch_f),bool)))
        path_audit.append(dict(step=step,patch_intersections=count))
        if count==0:last_clean=fitted.copy()
    relaxed=fitted.copy()
    fitted,contact_repair=contact_separation(fitted,last_clean,patch_f,edges,fixed)
    extra_ids=np.array([],int)
    if abs(fitted[fixed]-targets).max()>1e-9:raise ValueError('GRAFT390_BOUNDARY_DRIFT')
    # Dirichlet skin binding: exact source boundary values plus tissue anchors.
    names=list(q['group_names']);anchors={};binding_targets=[('sternum',(0,-.83,1.26),{'DEF-spine.003':.5,'DEF-spine.004':.5})]
    for side,sign in [('L',1),('R',-1)]:
        binding_targets += [(f'shoulder{side}',(sign*.29,-.77,1.43),{'DEF-spine.004':.7,f'DEF-upper_arm.{side}':.3}),(f'upperleg{side}',(sign*.20,-.65,1.16),{f'DEF-upper_arm.{side}.001':.65,f'DEF-forearm.{side}':.35})]
    taken=set(fixed.tolist());ai=[];aw=[]
    for label,position,blend in binding_targets:
        order=np.argsort(np.linalg.norm(fitted-np.array(position),axis=1));chosen=next(int(i) for i in order if int(i) not in taken);taken.add(chosen);row=np.zeros(len(names))
        for name,value in blend.items():row[names.index(name)]=value
        ai.append(chosen);aw.append(row);anchors[label]=dict(vertex=chosen,position=fitted[chosen].tolist(),weights=blend)
    raw_boundary=np.vstack([boundaryweights,aw]);totals=raw_boundary[:,deform].sum(1)
    if (totals<1e-8).any():raise ValueError('GRAFT390_ZERO_DEFORM_BOUNDARY')
    raw_boundary[:,deform]/=totals[:,None]
    w=harmonic(fitted,edges,np.r_[fixed,ai],raw_boundary);minimum=float(w.min());sums=w[:,deform].sum(1)
    if minimum < -1e-7 or abs(sums-1).max()>2e-5:raise ValueError('GRAFT390_WEIGHT_SOLVE')
    w=np.maximum(w,0);w[:,deform]/=w[:,deform].sum(1)[:,None]
    n=len(v);stitches=[]
    for label,sloop in sloops.items():
        dloop=dloops[label];stitches.append(zipper(sloop,dloop+n,v[sloop],patch_v[dloop]))
    append_faces=np.vstack([patch_f+n]+stitches);removed_ids={i for j,s in enumerate(selected) if s for i in members[j]};keep=np.array([i not in removed_ids for i in range(len(tris))]);allfaces=np.vstack([tris[keep],append_faces]);allv=np.vstack([v,fitted]);new_main=np.vstack([tris[keep&np.all(skin[tris],axis=1)],append_faces])
    ec=Counter(tuple(sorted(e)) for e in polygon_edges(new_main));nonmanifold=sum(c!=2 for c in ec.values());euler=len(np.unique(new_main))-len(ec)+len(new_main)
    dc=Counter(polygon_edges(new_main));orientation_errors=sum(dc.get((a,b),0)!=1 or dc.get((b,a),0)!=1 for a,b in ec)
    area=np.linalg.norm(np.cross(allv[append_faces[:,1]]-allv[append_faces[:,0]],allv[append_faces[:,2]]-allv[append_faces[:,0]]),axis=1)
    if nonmanifold or orientation_errors or euler!=2 or (area<1e-10).any():raise ValueError('GRAFT390_TOPOLOGY:'+str((nonmanifold,euler,float(area.min()))))
    relevant=np.any(new_main>=n,axis=1);cross=crossing_pairs(allv,new_main,relevant);relaxed_cross=crossing_pairs(np.vstack([v,relaxed]),new_main,relevant)
    remove_data=np.full((len(removed),4),-1,np.int32)
    for i,p in enumerate(removed):remove_data[i,:len(p)]=p
    out=root/'.runtime/art-direction/anatomy390-targets';out.mkdir(exist_ok=True)
    np.savez_compressed(out/'graft261.npz',source_rest=q['rest'],source_weights=q['weights'],group_names=q['group_names'],deform_mask=deform,remove_polygons=remove_data,vertices=fitted.astype(np.float32),faces=append_faces,weights=w.astype(np.float32),source_boundary=np.unique(np.concatenate(list(sloops.values()))).astype(np.int32))
    report=dict(source_vertices=n,removed_polygons=len(removed),added_vertices=len(fitted),added_triangles=len(append_faces),rings=ring_data,anchors=anchors,main_skin_nonmanifold_edges=nonmanifold,main_skin_euler=euler,orientation_errors=orientation_errors,minimum_twice_triangle_area=float(area.min()),new_region_intersections=len(cross),arap_control_intersections=len(relaxed_cross),chosen_registration='proper_affine_incremental_arap_reference_contact_qp',registration_path=path_audit,contact_repair=contact_repair,collar_control_vertices=len(extra_ids),proper_affine_determinant=affine_det,proper_affine_singular_values=affine_sv.tolist(),maximum_residual_boundary_delta=float(np.linalg.norm(targets-patch_v[fixed],axis=1).max()),minimum_harmonic_weight=minimum,deforming_columns=int(deform.sum()),maximum_weight_sum_error=float(abs(sums-1).max()),arap_iterations=len(history),arap_final_change=history[-1],guide_patch_displacement_max=float(np.linalg.norm(fitted-patch_v,axis=1).max()),scope='New local topology and proposed binding, numeric rest construction only. No native anatomy/pose/coat/motion pass. Exterior original geometry retained exactly.')
    (root/'results/sikh390/numeric261.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)
    if cross:raise ValueError('GRAFT390_REST_INTERSECTIONS:'+str(len(cross)))

if __name__=='__main__':build(Path(__file__).resolve().parents[1])
