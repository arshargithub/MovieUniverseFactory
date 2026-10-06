"""Fitted trouser seat with fixed anatomical surface correspondence.

The seat is fitted clothing, not free cloth. Bind once on the neutral skin;
follow those same triangles through the existing animation. No per-frame
nearest-point projection, anatomical edit or new performance is introduced.
"""
import json
from pathlib import Path
import numpy as np


def seat_weight(points,extended=False):
    p=np.asarray(points);z=p[:,2];x=abs(p[:,0])
    def smooth(t):
        t=np.clip(t,0,1);return t*t*(3-2*t)
    upper=-5.7 if extended else -6.15
    return smooth((z+8.8)/.8)*smooth((upper-z)/.45)*smooth((1.75-x)/.75)


def fixed_surface(triangles,weights,clearance):
    t=np.asarray(triangles);n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0]);size=np.linalg.norm(n,axis=1)
    if np.any(size<1e-12):raise ValueError('Degenerate fitted-seat support')
    distance=np.asarray(clearance)
    if distance.ndim==1:distance=distance[:,None]
    return np.einsum('njk,nj->nk',t,weights)+n/size[:,None]*distance


def run(out):
    if out.name.endswith(('seatcheck01','seatcheck02','seatcheck03')):return audit(out)
    import bpy
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    from wardrobe_motion178 import BASE,digest,check_protected
    from wardrobe185_lower import fast_geometry
    from wardrobe185_lower_drape import triangle_weights
    from wardrobe185_lower_gap import local_faces
    from wardrobe_shawl180_cache import cache
    from wardrobe_riding_fit import fit_render
    from wardrobe_motion178_controls import render_geometry_paused
    from wardrobe185_lower_cloth import sample
    from wardrobe185_lower import world_points
    source=BASE/'wardrobe185-mountfit03/integration-working.blend'
    expected='7031e73c027d5032d95398c0380bbbcb010631b6fff4d1c2def6840bd08d2cda'
    if digest(source)!=expected:raise ValueError('Unbound fitted-seat source')
    (out/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False)
    scene=bpy.context.scene;scene.frame_set(1);bpy.context.view_layer.update()
    pants=bpy.data.objects['MF_fit_trousers_173_visible'];body=bpy.data.objects['MF_studio_adult_body']
    flags=[(m,m.show_viewport) for m in pants.modifiers if m.type in ('SUBSURF','SOLIDIFY')]
    for m,_ in flags:m.show_viewport=False
    p,pf=fast_geometry(pants);bp,bf=fast_geometry(body)
    if len(p)!=len(pants.data.vertices):raise ValueError('Fitted-seat cache needs base mesh correspondence')
    whole=out.name.endswith('trouserseat03')
    revised=whole or out.name.endswith('trouserseat02')
    weight=seat_weight(p,revised);ids=np.flatnonzero(weight>0);unchanged=np.flatnonzero(weight==0)
    if whole:ids=np.arange(len(p));unchanged=np.array([],dtype=int)
    bf=local_faces(bp,bf,(-3.,-3.,-14.5) if whole else (-2.4,-2.,-9.),(3.,3.,-4.7) if whole else (2.4,2.,-5.5 if revised else -6.))
    tree=BVHTree.FromPolygons(bp.tolist(),bf.tolist(),all_triangles=True)
    indices=[];weights=[];clearances=[]
    for point in p[ids]:
        hit,normal,index,distance=tree.find_nearest(Vector(point))
        if hit is None or distance>.7:raise ValueError('Seat has no nearby neutral anatomical support')
        indices.append(bf[index]);weights.append(triangle_weights(hit,bp[bf[index]]))
        clearances.append(max(.020,float((Vector(point)-hit).dot(normal))))
    indices=np.array(indices);weights=np.array(weights);frames=[];record={};error=0.
    clearance=np.array(clearances)*(1-weight[ids])+.012*weight[ids] if whole else .012
    initial=fixed_surface(bp[indices],weights,clearance)
    maximum=float(np.max(np.linalg.norm(initial-p[ids],axis=1)))
    required={body,pants}
    for _ in range(8):
        prior=len(required)
        for ob in list(required):
            for m in ob.modifiers:
                for key in ('target','object'):
                    target=getattr(m,key,None)
                    if isinstance(target,bpy.types.Object):required.add(target)
        if len(required)==prior:break
    with render_geometry_paused():
        for ob in required:ob.hide_viewport=False
        for frame in range(1,361):
            scene.frame_set(frame);bpy.context.view_layer.update()
            before=world_points(sample(pants),np.array(pants.matrix_world));bp=world_points(sample(body),np.array(body.matrix_world))
            q=before.copy();mapped=fixed_surface(bp[indices],weights,clearance)
            if whole:q[ids]=mapped
            else:q[ids]=before[ids]*(1-weight[ids,None])+mapped*weight[ids,None]
            if len(unchanged):error=max(error,float(np.max(abs(q[unchanged]-before[unchanged]))))
            if not np.isfinite(q).all():raise ValueError('Nonfinite fitted seat')
            frames.append(q.astype(np.float32))
            if frame%48==0:print('Fixed trouser seat',frame,flush=True)
    frames=np.array(frames)
    for m in list(pants.modifiers):
        if m.type=='SURFACE_DEFORM':pants.modifiers.remove(m)
    pants.data=pants.data.copy();inverse=np.linalg.inv(np.array(pants.matrix_world))
    local=frames@inverse[:3,:3].T+inverse[:3,3]
    pants.data.vertices.foreach_set('co',local[0].astype(np.float32).ravel());pants.data.update()
    mod=cache(pants,local,out/'fitted-seat.mdd')
    bpy.context.view_layer.objects.active=pants
    while list(pants.modifiers).index(mod)>0:bpy.ops.object.modifier_move_up(modifier=mod.name)
    for m,state in flags:m.show_viewport=state
    if revised:
        shells=[m for m in pants.modifiers if m.type=='SOLIDIFY']
        if len(shells)!=1 or abs(shells[0].thickness-.018)>1e-6:raise ValueError('Unexpected trouser shell')
        shells[0].thickness=.006
    scene.camera.animation_data_clear();scene.camera.data.type='ORTHO';scene.cycles.device='CPU';scene.cycles.samples=8
    scene.render.use_persistent_data=True
    for frame in (1,169,193,217,223,226,326,360):
        scene.frame_set(frame);bpy.context.view_layer.update();q,f=fast_geometry(pants)
        f=local_faces(q,f,(-2,-3,-9),(2,2,-4.5));tree=BVHTree.FromPolygons(q.tolist(),f.tolist(),all_triangles=True)
        row={}
        for name in ('MF_studio_adult_body','MF185_gait_saddle','MF185_gait_horse'):
            p,g=fast_geometry(bpy.data.objects[name]);g=local_faces(p,g,(-2,-3,-9),(2,2,-4.5))
            row[name]=len(tree.overlap(BVHTree.FromPolygons(p.tolist(),g.tolist(),all_triangles=True)))
        record[frame]=row
        if frame in (1,217,223):
            hidden=[]
            if frame==1:
                for ob in scene.objects:
                    if ob.name.startswith(('MF185_gait_','MF185_rein_','MF185_stirrup_')):
                        hidden.append((ob,ob.hide_render));ob.hide_render=True
            for angle,label in ((90,'left'),(180,'rear')):
                fit_render(out,'seat-'+label+'-'+str(frame),angle,(0,-.2,-6.7),5.6,(640,640))
            for ob,state in hidden:ob.hide_render=state
    check_protected();scene.frame_set(217);bpy.context.view_layer.update()
    bpy.context.preferences.filepaths.save_version=0
    bpy.ops.wm.save_as_mainfile(filepath=str(out/'integration-working.blend'),check_existing=False)
    np.savez_compressed(out/'binding.npz',vertex_indices=ids,body_triangle_indices=indices,
        barycentric_weights=weights,fit_weights=np.ones(len(ids)) if whole else weight[ids],clearance=clearance)
    (out/'result.json').write_text(json.dumps({'source_sha256':expected,'native_sha256':digest(out/'integration-working.blend'),
        'fixed_surface_vertices':len(ids),'maximum_neutral_fit_native':maximum,'unchanged_region_error':None if whole else error,
        'whole_garment_fixed_binding':whole,'ease_scope':'Retain positive rest-normal ease outside seat; minimum2.46mm, seat1.475mm' if whole else None,
        'clearance_native':.012,'extended_upper_transition':revised,'shell_thickness_native':.006 if revised else .018,
        'frames':record,'visual_gate':'NOT_RUN','protected_exact':True,
        'scope':'Fixed skin-attached fitted trouser seat; not free cloth or final garment approval'},indent=2)+'\n')


def audit(out):
    import bpy,struct
    from mathutils.bvhtree import BVHTree
    from wardrobe_motion178 import BASE,digest,check_protected
    from wardrobe185_lower import fast_geometry
    source=BASE/'wardrobe185-trouserseat01/integration-working.blend'
    expected='b3a4e413c9d43e001b4b627769fac07c029643b1bfd9e053352c0f3d5d94be65'
    if out.name.endswith(('seatcheck02','seatcheck03')):
        source=BASE/'wardrobe185-trouserseat03/integration-working.blend'
        expected='3dc4f8f14c88ff8fd4fb0c98ecb58a9348326ca2e1b4e24537d6c31783547626'
    if digest(source)!=expected:raise ValueError('Unbound seat audit source')
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False)
    (out/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
    ob=bpy.data.objects['MF_fit_trousers_173_visible'];scene=bpy.context.scene
    modifiers=[{'type':m.type,'name':m.name,'thickness':getattr(m,'thickness',None),'offset':getattr(m,'offset',None)} for m in ob.modifiers]
    flags=[(m,m.show_viewport) for m in ob.modifiers if m.type in ('SUBSURF','SOLIDIFY')]
    for m,_ in flags:m.show_viewport=False
    path=source.parent/'fitted-seat.mdd'
    with path.open('rb') as stream:nframes,npoints=struct.unpack('>2i',stream.read(8))
    data=np.memmap(path,dtype='>f4',mode='r',offset=8+4*nframes,shape=(nframes,npoints,3))
    fit=np.zeros(npoints)
    with np.load(source.parent/'binding.npz',allow_pickle=False) as d:
        binding={k:d[k] for k in d.files};fit[d['vertex_indices']]=d['fit_weights']
    rows={};error=0.
    for frame in (1,169,193,217,223,226,326,360,217):
        scene.frame_set(frame);bpy.context.view_layer.update();p,f=fast_geometry(ob)
        error=max(error,float(np.max(abs(p-data[frame-1]))))
        claimed=f[np.max(fit[f],axis=1)>.5]
        tree=BVHTree.FromPolygons(p.tolist(),claimed.tolist(),all_triangles=True);row={}
        for name in ('MF_studio_adult_body','MF185_gait_saddle','MF185_gait_horse'):
            if frame==1 and name!='MF_studio_adult_body':continue
            q,g=fast_geometry(bpy.data.objects[name]);tri=q[g]
            if name=='MF_studio_adult_body' and out.name.endswith('seatcheck03'):
                intended=fixed_surface(q[binding['body_triangle_indices']],binding['barycentric_weights'],binding['clearance'])
                delta=np.linalg.norm(p[binding['vertex_indices']]-intended,axis=1)
                row['actual_body_correspondence_error_native']={'quantiles':np.quantile(delta,[0,.5,.99,1]).tolist(),
                    'above_2e5_tolerance':int(np.count_nonzero(delta>2e-5))}
            g=g[np.all(tri.max(1)>p[np.unique(claimed)].min(0)-.05,axis=1)&np.all(tri.min(1)<p[np.unique(claimed)].max(0)+.05,axis=1)]
            ct=BVHTree.FromPolygons(q.tolist(),g.tolist(),all_triangles=True);pairs=tree.overlap(ct)
            record={'midsurface_claimed_region_pairs':len(pairs)}
            if pairs:
                patch=p[np.unique(claimed[np.array(pairs)[:,0]])]
                record['patch_bounds_native']=[patch.min(0).tolist(),patch.max(0).tolist()]
            row[name]=record
        rows[frame]=row
        print('Seat midsurface audit',frame,row,flush=True)
    if error>2e-5:raise ValueError('Seat cache does not reproduce authored coordinates')
    check_protected()
    (out/'result.json').write_text(json.dumps({'source_sha256':expected,'modifiers':modifiers,'cache_max_error_native':error,
        'frames':rows,'scope':'Fitted region midsurface vs actual skin and mount; thickness contacts remain separately recorded',
        'visual_gate':'NOT_RUN','protected_exact':True},indent=2)+'\n')
