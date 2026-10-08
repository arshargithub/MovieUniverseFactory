"""Read-only new-pose containment and fixed cloth-support motion export."""
import json
import sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
import wardrobe_motion178 as base


def world_transform(data,frame,inertial=False):
    from mathutils import Matrix,Vector
    if frame<=361:return Matrix.Identity(4)
    i=(frame-361)*8;p=np.array(data['position'][i],copy=True)
    if inertial:p-=np.array((0,-12*data['time'][i],0))
    floor=Vector((0,.2,-20.931))
    rot=Matrix.Rotation(float(data['heading'][i]),4,'Z')@Matrix.Rotation(-float(np.arctan(data['grade'][i])),4,'X')@Matrix.Rotation(float(data['bank'][i]),4,'Y')
    return Matrix.Translation(floor+Vector(8.3*p))@rot@Matrix.Translation(-floor)


def main():
    import bpy
    from mathutils import Matrix
    from wardrobe185_convex import region_masks,convex_outside,CONTACT_SHA
    from wardrobe_motion178_controls import render_geometry_paused
    job=json.loads(Path(sys.argv[sys.argv.index('--')+1]).read_text())
    if job!={'operation':'contacts10'}:raise ValueError('Fixed contact inspection required')
    folder=base.BASE/'entrance190-rider09';source=folder/'rider.blend';out=base.BASE/'entrance190-contacts10'
    result=json.loads((folder/'result.json').read_text())
    if out.exists() or source.is_symlink() or base.digest(source)!=result['native_sha256']:raise ValueError('Unbound rider source')
    prior=base.BASE/'wardrobe185-convexcontact04/contact.npz'
    if base.digest(prior)!=CONTACT_SHA:raise ValueError('Unbound original envelopes')
    out.mkdir();(out/'handler.py').write_bytes(Path(__file__).read_bytes())
    with np.load(prior,allow_pickle=False) as z:old={k:z[k] for k in z.files}
    with np.load(folder/'route.npz',allow_pickle=False) as z:route={k:z[k] for k in z.files}
    bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False);base.check_protected()
    scene=bpy.context.scene;rig=bpy.data.objects['MF_body156_fit_rig']
    names={'torso':'chest','armL':'upperarm.L','armR':'upperarm.R','head':'MF185_head','groom':'MF185_head'}
    objects=[bpy.data.objects[n] for n in ('MF185_fitted_upper_tunic','MF_173_tension_harness_-1','MF_173_tension_harness_1','MF_studio_adult_body')]
    body=objects[-1];restbody=np.array([v.co[:] for v in body.data.vertices])
    flags=[(m,m.show_viewport) for ob in objects for m in ob.modifiers if m.type=='SUBSURF']
    for m,_ in flags:m.show_viewport=False
    required=set(objects)
    for _ in range(8):
        for ob in list(required):
            for m in ob.modifiers:
                for prop in ('target','object'):
                    target=getattr(m,prop,None)
                    if isinstance(target,bpy.types.Object):required.add(target)
    mats={k:[] for k in names};sources={k:[] for k in names if k!='groom'};rows=[];world=[]
    def delta(name):
        b=rig.pose.bones[name]
        return rig.matrix_world@b.matrix@b.bone.matrix_local.inverted()@rig.matrix_world.inverted()
    with render_geometry_paused():
        for ob in required:ob.hide_viewport=False
        for frame in sorted(set((1,169,193,217,265,360)+tuple(range(361,554,8))+(553,))):
            scene.frame_set(frame);bpy.context.view_layer.update();samples={k:[] for k in sources}
            for ob in objects:
                ev=ob.evaluated_get(bpy.context.evaluated_depsgraph_get());mesh=ev.to_mesh()
                p=np.array([ob.matrix_world@v.co for v in mesh.vertices])
                attr=mesh.attributes.get('MF_173_material_coords')
                rest=np.array([a.vector[:] for a in attr.data]) if ob!=body and attr else restbody
                if len(rest)!=len(p):raise ValueError('Lost stable anatomical coordinates')
                masks=region_masks(rest)
                if ob==body:masks={'torso':(abs(rest[:,0])<1.5)&(rest[:,2]>-3.8)&(rest[:,2]<-1.35),'head':rest[:,2]>-1.5}
                elif ob!=objects[0]:masks={'torso':(rest[:,2]>-4.2)&(rest[:,2]<-1.35)}
                for key,mask in masks.items():samples[key].extend(p[mask].tolist())
                ev.to_mesh_clear()
            for key,p in samples.items():
                inv=np.array(delta(names[key]).inverted());q=np.array(p)@inv[:3,:3].T+inv[:3,3]
                sources[key].append(q)
                outside=convex_outside(q,old[key+'_points'],old[key+'_faces'])
                rows.append({'frame':frame,'part':key,'points':len(q),'outside_old_envelope':int(outside.sum())})
            print('190 contact anatomy',frame,flush=True)
        for ob in required:ob.hide_viewport=True
        for frame in range(1,554):
            scene.frame_set(frame);bpy.context.view_layer.update()
            for key,bone in names.items():mats[key].append(np.array(delta(bone)))
            world.append(np.array(world_transform(route,frame,True)))
    arrays={k+'_matrices':np.array(v) for k,v in mats.items()}
    arrays.update({k+'_source':np.concatenate(v) for k,v in sources.items()})
    arrays.update(world_inertial=np.array(world),frame_ids=np.arange(1,554))
    for key in names:
        arrays[key+'_points']=old[key+'_points'];arrays[key+'_faces']=old[key+'_faces']
    np.savez_compressed(out/'contacts.npz',**arrays)
    (out/'result.json').write_text(json.dumps({'source_sha256':result['native_sha256'],'contacts_sha256':base.digest(out/'contacts.npz'),
        'rows':rows,'old_envelope_reusable':not any(r['outside_old_envelope'] for r in rows),
        'scope':'Actual coarse upper-body/tunic/harness vertex containment; groom envelope retained, whole-groom containment NOT_RUN',
        'visual_gate':'NOT_RUN'},indent=2)+'\n')


if __name__=='__main__':main()
