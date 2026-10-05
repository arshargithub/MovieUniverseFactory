"""Reviewed fixed causal cloth probes for the authorized Astra rescue.

JSON accepts an operation enum only. Protected source and input cut are hashed;
all outputs are new. This module never loads credentials or evaluated code.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import wardrobe_motion178 as foundation
from wardrobe_shawl179_weld import WELD_INPUT, WELD_SHA

OPERATIONS = ('masscontrol01', 'legacycontrol01', 'construction01', 'construction02', 'inspectdynamics01', 'inspectdynamics02')
OPERATIONS += ('xpbdflat01','xpbdcut01')
OPERATIONS += ('inspectdynamics03',)
OPERATIONS += ('xpbdunit01','groomaudit01','xpbdflat02')
OPERATIONS += ('xpbdunit02',)
OPERATIONS += ('xpbdflat03','xpbdcut02')
OPERATIONS += ('xpbdflat04',)
OPERATIONS += ('inspectdynamics04',)
OPERATIONS += ('xpbdflat05',)
OPERATIONS += ('contactisolate01',)
OPERATIONS += ('xpbdflat06','xpbdcut03')
OPERATIONS += ('xpbdweld01',)
OPERATIONS += ('xpbdhead07',)
OPERATIONS += ('assembly01',)
OPERATIONS += ('assembly02',)
OPERATIONS += ('assembly03',)
OPERATIONS += ('assembly04',)
OPERATIONS += ('xpbdhead08','assembly05')
OPERATIONS += ('cacheunit01',)
OPERATIONS += ('cacheunit02',)
OPERATIONS += ('assembly06',)


def validate(job):
    if not isinstance(job, dict) or set(job) != {'operation'} or job['operation'] not in OPERATIONS:
        raise ValueError('Fixed diagnostic operation only')
    for path, expected in ((foundation.SOURCE, foundation.SOURCE_SHA), (WELD_INPUT, WELD_SHA)):
        if path.is_symlink() or foundation.digest(path) != expected:
            raise ValueError('Pinned source changed')
    out = foundation.BASE / ('wardrobe180-' + job['operation'])
    if out.exists() or out.is_symlink():
        raise ValueError('Preserve previous evidence')
    return out


def measures(points, faces, frames, scale):
    import numpy as np
    p = np.asarray(points); f = np.asarray(faces)
    edges = np.array(sorted({tuple(sorted((int(a), int(b)))) for q in f for a, b in zip(q, np.roll(q, -1))}))
    length = np.linalg.norm(p[edges[:, 0]] - p[edges[:, 1]], axis=1)
    area = sum(np.linalg.norm(np.cross(p[f[:, k]]-p[f[:, 0]], p[f[:, k+1]]-p[f[:, 0]]), axis=1).sum()/2 for k in (1, 2))*scale**2
    if min(length) <= 0 or not 0 < area < 10:
        raise ValueError('Invalid source metric')
    ratios = {}
    for frame, coords in frames.items():
        ratio = np.linalg.norm(coords[edges[:, 0]]-coords[edges[:, 1]], axis=1)/length
        ratios[str(frame)] = dict(zip(('min', 'median', 'p90', 'p99', 'max'), np.quantile(ratio, [0,.5,.9,.99,1]).tolist()))
    return {'dressed_area_m2': float(area), 'edge_stretch': ratios}


def main():
    import bpy
    import numpy as np
    import wardrobe_studio as studio
    import wardrobe_motion178_controls as controls
    from wardrobe_motion178_proof import dress_actor
    from wardrobe_underarm179_repair import repair
    from wardrobe_shawl179_collision import supports as make_supports
    from wardrobe_refinement import neutral
    from wardrobe_shawl179 import screens
    job = json.loads(Path(sys.argv[sys.argv.index('--')+1]).read_text())
    out = validate(job); out.mkdir()
    for name in ('wardrobe_shawl180.py','wardrobe_shawl180_dynamics.py','wardrobe_shawl180_cut.py'):
        (out/name).write_bytes((ROOT/'scripts'/name).read_bytes())
    if job['operation'].startswith('cacheunit'):
        from wardrobe_shawl180_cache import unit
        (out/'wardrobe_shawl180_cache.py').write_bytes((ROOT/'scripts/wardrobe_shawl180_cache.py').read_bytes())
        unit(out)
        return
    if job['operation'].startswith('xpbdunit'):
        from wardrobe_shawl180_dynamics import unit_probe
        unit_probe(out,quality=job['operation']=='xpbdunit02')
        return
    if job['operation'].startswith('inspectdynamics'):
        path=Path('/Applications/Blender.app/Contents/Resources/5.2/datafiles/assets/nodes/geometry_nodes_dynamics_assets.blend')
        with bpy.data.libraries.load(str(path),link=False) as (src,dst):
            names=list(src.node_groups);dst.node_groups=[n for n in names if 'Cloth' in n or n in ('Collider','Custom Force')]
        groups=[]
        for group in bpy.data.node_groups:
            groups.append({'name':group.name,'interface':[{'name':i.name,'item_type':i.item_type,
                'in_out':getattr(i,'in_out',None),'identifier':getattr(i,'identifier',None),
                'socket_type':getattr(i,'socket_type',None),'default':str(getattr(i,'default_value',None))}
                for i in group.interface.items_tree],
                'nodes':[{'name':n.name,'type':n.bl_idname,'group':n.node_tree.name if n.type=='GROUP' else None,
                    'inputs':[{'name':s.name,'id':s.identifier,'value':str(getattr(s,'default_value',None))} for s in n.inputs],
                    'operation':getattr(n,'operation',None)} for n in group.nodes],
                'links':[(l.from_node.name,l.from_socket.identifier,l.to_node.name,l.to_socket.identifier) for l in group.links]})
        (out/'result.json').write_text(json.dumps({'available_names':names,'groups':groups,'shipped_asset_sha256':foundation.digest(path)},indent=2)+'\n')
        if job['operation']=='inspectdynamics04':
            node=next(n for g in bpy.data.node_groups for n in g.nodes if n.bl_idname=='NodeCombineBundle')
            print('COMBINE PROPS',[(p.identifier,p.type) for p in node.bl_rna.properties],flush=True)
            for prop in node.bl_rna.properties:
                if prop.type=='COLLECTION' and prop.identifier not in ('inputs','outputs'):
                    collection=getattr(node,prop.identifier)
                    print(prop.identifier,[(f.identifier,[(p.identifier,p.type,[e.identifier for e in p.enum_items] if p.type=='ENUM' else '') for p in f.parameters]) for f in collection.bl_rna.functions],flush=True)
        return
    for name in ('wardrobe_shawl180.py', 'wardrobe_shawl179_motion.py', 'wardrobe_shawl179_collision.py',
                 'wardrobe_motion178_controls.py', 'wardrobe_motion178.py', 'wardrobe_underarm179_repair.py'):
        (out/name).write_bytes((ROOT/'scripts'/name).read_bytes())
    bpy.ops.wm.open_mainfile(filepath=str(foundation.SOURCE), load_ui=False, use_scripts=False)
    foundation.check_protected()
    rig, mats, _ = foundation.clean_foundation()
    if job['operation'].startswith('assembly'):
        from wardrobe_shawl180_assembly import run
        (out/'wardrobe_shawl180_assembly.py').write_bytes((ROOT/'scripts/wardrobe_shawl180_assembly.py').read_bytes())
        run(out,rig,mats)
        return
    if job['operation']=='contactisolate01':
        from wardrobe_shawl180_dynamics import contact_probe
        contact_probe(out)
        return
    if job['operation']=='groomaudit01':
        from wardrobe_shawl180_dynamics import groom_audit
        groom_audit(out,mats)
        return
    if job['operation'].startswith('xpbd'):
        from wardrobe_shawl180_dynamics import probe
        for name in ('wardrobe_shawl180_dynamics.py','wardrobe_shawl180_cut.py'):
            (out/name).write_bytes((ROOT/'scripts'/name).read_bytes())
        probe(out,mats,job['operation'][4:])
        return
    if job['operation'].startswith('construction'):
        from wardrobe_shawl180_cut import construction
        p,f,pins,report=construction(int(job['operation'][-2:]))
        np.savez_compressed(out/'constructed-layout.npz',points=p,faces=f,pin_indices=np.array(sorted(pins)),
                            pin_weights=np.array([pins[i] for i in sorted(pins)]))
        studio.panel('MF180_open_headfall',p.tolist(),f.tolist(),mats['scarf'],.012,1)
        screens(out,(1,))
        foundation.check_protected()
        report.update({'protected_exact':True,'visual_gate':'NOT_RUN','motion_gate':'NOT_RUN'})
        (out/'result.json').write_text(json.dumps(report,indent=2)+'\n')
        (out/'wardrobe_shawl180_cut.py').write_bytes((ROOT/'scripts/wardrobe_shawl180_cut.py').read_bytes())
        return
    scale = bpy.context.scene.unit_settings.scale_length
    sample = controls.body_weight_sampler()
    dress_actor(rig); repair(rig, 'repair04'); controls.animate(rig, neutral_entry=True)
    canonical = controls.canonical_rig(rig, scale)
    actions = [o.animation_data.action for o in (rig, canonical)]
    for o in (rig, canonical): o.animation_data.action = None; neutral(o)
    bpy.context.view_layer.update()
    supports, _ = make_supports(canonical, scale, sample)
    for o, action in zip((rig, canonical), actions): o.animation_data.action = action
    with np.load(WELD_INPUT, allow_pickle=False) as record:
        points = record['points'].copy(); faces = record['faces'].copy()
        pins = dict(zip(record['pin_indices'].tolist(), record['pin_weights'].tolist()))
    mesh = bpy.data.meshes.new('MF180_metric_cut'); mesh.from_pydata((points*scale).tolist(), [], faces.tolist()); mesh.update()
    cloth = bpy.data.objects.new('MF178_live_solver180', mesh); bpy.context.scene.collection.objects.link(cloth); cloth.hide_render = True
    controls.bind(cloth, canonical, scale=scale, chest_only=True)
    pin = cloth.vertex_groups.new(name='Identical179_supports')
    for i, w in pins.items(): pin.add([i], w, 'REPLACE')
    mod = cloth.modifiers.new('Causal mass comparison', 'CLOTH'); s = mod.settings
    s.quality=16; s.mass=.0001 if job['operation']=='masscontrol01' else .04
    s.tension_stiffness=25; s.compression_stiffness=25; s.shear_stiffness=12; s.bending_stiffness=.015
    s.tension_damping=6; s.compression_damping=6; s.shear_damping=6; s.air_damping=1
    s.vertex_group_mass=pin.name; s.use_sewing_springs=False; s.sewing_force_max=1.; s.use_dynamic_mesh=False
    domain=bpy.data.collections.new('MF180_exclusive_metric_contacts'); bpy.context.scene.collection.children.link(domain)
    for support in supports: domain.objects.link(support)
    c=mod.collision_settings; c.collection=domain; c.use_collision=True; c.distance_min=.003
    c.use_self_collision=True; c.self_distance_min=.0015
    mod.point_cache.frame_start=1; mod.point_cache.frame_end=97
    controls.wind(gain=.04)
    scene=bpy.context.scene; scene.gravity=(0,0,-9.81); scene.render.fps=24
    data={}
    with controls.render_geometry_paused():
        for frame in range(1,98):
            scene.frame_set(frame); bpy.context.view_layer.update()
            ev=cloth.evaluated_get(bpy.context.evaluated_depsgraph_get()); m=ev.to_mesh()
            coords=np.array([v.co[:] for v in m.vertices])/scale; ev.to_mesh_clear()
            if not np.isfinite(coords).all() or abs(coords).max()>100: raise ValueError('Escaped cloth')
            if frame in (1,24,48,72,97): data[frame]=coords
            if frame%24==0: print('180 causal sample',frame,flush=True)
    np.savez_compressed(out/'samples.npz', points=points, faces=faces, **{str(k):v for k,v in data.items()})
    studio.panel('MF180_mass_probe',data[97].tolist(),faces.tolist(),mats['scarf'],.014,1)
    screens(out,(97,))
    foundation.check_protected()
    report=measures(points,faces,data,scale)
    report.update({'operation':job['operation'],'effective_vertex_mass':s.mass,'effective_total_mass':s.mass*len(points),
        'mass_rna_min':s.bl_rna.properties['mass'].hard_min,'protected_exact':True,'visual_gate':'NOT_RUN',
        'source_sha256':foundation.SOURCE_SHA,'initial_sha256':WELD_SHA,'handler_sha256':foundation.digest(Path(__file__))})
    (out/'result.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report),flush=True)


if __name__=='__main__': main()
