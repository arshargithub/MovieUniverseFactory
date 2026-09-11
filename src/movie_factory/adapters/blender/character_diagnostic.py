"""Fixed, provider-free 3D-03.1 diagnostic. Does not alter production baking.

Compares identical frozen source samples under controlled target assignment
methods. All assets pass the existing hash-checked FBX importer. No executable
content or arbitrary diagnostic method can be supplied in the work package.
"""
import math
from pathlib import Path
import bpy
from mathutils import Matrix


def matrix_error(a,b):
    return max(abs(a[i][j]-b[i][j]) for i in range(4) for j in range(4))


def rms(a,b):
    return math.sqrt(sum((x-y).length_squared for x,y in zip(a,b))/len(a))


def dump_matrices(m):
    return {k:[list(row) for row in value] for k,value in m.items()}


def run(w,out,plan,parent_native=None):
    if plan.get('experiment_id')!='3D-03' or set(plan.get('clips',{}))!={'idle','run','jump'}:
        raise ValueError('Diagnostic accepts only the admitted 3D-03 plan')
    result={'status':'DIAGNOSTIC_ONLY','provider_calls':0,'blender':bpy.app.version_string,'clips':{}}
    preview_channels={}
    for clip in ('idle','run','jump'):
        bpy.ops.wm.read_factory_settings(use_empty=True)
        model,_=w.import_animated_fbx(plan['entity']['source'])
        target=next(o for o in model if o.type=='ARMATURE'); mesh=next(o for o in model if o.type=='MESH')
        names={g.name for g in mesh.vertex_groups}
        objects,actions=w.import_animated_fbx(plan['clips'][clip])
        source=next(o for o in objects if o.type=='ARMATURE')
        action=next(a for a in actions if a.name.lower().endswith('|'+clip))
        w.assign_character_action(source,action)
        scene=bpy.context.scene; first,last=map(lambda x:int(round(x)),action.frame_range)
        frames=list(range(first,last+1))
        def sample_source(order):
            data={}
            for f in order:
                scene.frame_set(f); bpy.context.view_layer.update()
                data[f]={b.name:b.matrix.copy() for b in source.pose.bones}
            return data
        forward=sample_source(frames); reverse=sample_source(list(reversed(frames)))
        source_order_error=max(matrix_error(forward[f][n],reverse[f][n]) for f in frames for n in names)
        source_seam=max(matrix_error(forward[first][n],forward[last][n]) for n in names)
        transform=target.matrix_world.inverted()@source.matrix_world
        frozen={f:{n:transform@m for n,m in poses.items()} for f,poses in forward.items()}
        parent_order=sorted([b for b in target.pose.bones if b.name in names],key=lambda b:len(b.parent_recursive))
        full_order=sorted(target.pose.bones,key=lambda b:len(b.parent_recursive))
        rest={b.name:b.bone.matrix_local.copy() for b in full_order}
        w.write_json(out/(clip+'-source.json'),{'source_sha256':plan['clips'][clip]['sha256'],
            'scene_fps':scene.render.fps,'fps_base':scene.render.fps_base,
            'samples':{str(f):dump_matrices(poses) for f,poses in forward.items()},
            'source_rest':dump_matrices({b.name:b.matrix_local for b in source.data.bones}),
            'target_rest':dump_matrices(rest),'source_world':[list(row) for row in source.matrix_world],
            'target_world':[list(row) for row in target.matrix_world]})
        variants={}; vertices={}
        for method in ('legacy_forward','legacy_reverse','legacy_isolated','parent_update_forward','explicit_forward','explicit_reverse'):
            target.animation_data_clear(); target.location=(0,0,0)
            for b in full_order:
                b.matrix_basis=Matrix.Identity(4); b.rotation_mode='QUATERNION'
            bpy.context.view_layer.update()
            bake=bpy.data.actions.new('diagnostic_'+method)
            w.assign_character_action(target,bake)
            order=list(reversed(frames)) if method.endswith('reverse') else frames
            errors=[]; values={}; intended={}
            for f in order:
                scene.frame_set(f); bpy.context.view_layer.update()
                if method=='legacy_isolated':
                    for b in full_order: b.matrix_basis=Matrix.Identity(4)
                    bpy.context.view_layer.update()
                target.location=(0,0,0)
                desired={}
                for b in parent_order:
                    src=frozen[f][b.name]
                    rot=src.to_quaternion().normalized().to_matrix().to_4x4()
                    if b.parent and b.parent.name in desired:
                        local=rest[b.parent.name].inverted()@rest[b.name]
                        loc=desired[b.parent.name]@local.translation
                    else:
                        src_rest=transform@source.data.bones[b.name].matrix_local
                        loc=b.bone.head_local+(src.translation-src_rest.translation)
                    desired[b.name]=Matrix.Translation(loc)@rot
                intended[f]=desired
                if method.startswith('explicit'):
                    # Pure parent-relative conversion; all parent matrices are
                    # from this frame, never Blender's cached prior frame.
                    solved={}
                    for b in full_order:
                        kw={'parent_matrix':solved[b.parent.name],'parent_matrix_local':rest[b.parent.name]} if b.parent else {}
                        if b.name in desired:
                            basis=b.bone.convert_local_to_pose(desired[b.name],rest[b.name],invert=True,**kw)
                            b.matrix_basis=basis
                            solved[b.name]=desired[b.name]
                        else:
                            b.matrix_basis=Matrix.Identity(4)
                            solved[b.name]=b.bone.convert_local_to_pose(b.matrix_basis,rest[b.name],**kw)
                else:
                    for b in parent_order:
                        b.matrix=desired[b.name]
                        if method.startswith('parent_update'): bpy.context.view_layer.update()
                bpy.context.view_layer.update()
                assign_error=max(matrix_error(b.matrix,desired[b.name]) for b in parent_order)
                worst=max(parent_order,key=lambda b:matrix_error(b.matrix,desired[b.name])).name
                rotations={b.name:b.rotation_quaternion.copy() for b in parent_order}
                for b in parent_order:
                    b.location=(0,0,0); b.scale=(1,1,1); b.rotation_quaternion=rotations[b.name]
                bpy.context.view_layer.update()
                # Angular matrix error ignores root displacement discarded by
                # the normalization. It still exposes hierarchy corruption.
                rotation_error=max(max(abs(b.matrix[i][j]-desired[b.name][i][j]) for i in range(3) for j in range(3)) for b in parent_order)
                low,_=w.evaluated_bounds([mesh]); target.location.z=-low[2]
                bpy.context.view_layer.update()
                values[f]={'rotations':{n:list(q) for n,q in rotations.items()},'root':list(target.location)}
                for b in parent_order: b.keyframe_insert(data_path='rotation_quaternion',frame=f,group=b.name)
                target.keyframe_insert(data_path='location',frame=f,group='grounding')
                errors.append({'frame':f,'assignment_max_matrix_error':assign_error,'worst_bone':worst,
                               'rotation_error_after_normalization':rotation_error})
            for c in w.action_channels(bake):
                for k in c.keyframe_points: k.interpolation='LINEAR'
            played={}; playback_errors=[]
            for f in frames:
                scene.frame_set(f); bpy.context.view_layer.update()
                played[f]=w._evaluated_character_points(mesh)
                playback_errors.append(max(abs(target.pose.bones[n].rotation_quaternion[i]-q[i]) for n,q in values[f]['rotations'].items() for i in range(4)))
            rev_played={}
            for f in reversed(frames):
                scene.frame_set(f); bpy.context.view_layer.update()
                rev_played[f]=w._evaluated_character_points(mesh)
            vertices[method]=played
            variants[method]={'stages':sorted(errors,key=lambda x:x['frame']),
                'max_assignment_error':max(e['assignment_max_matrix_error'] for e in errors),
                'max_playback_channel_error':max(playback_errors),
                'max_playback_order_mesh_rms_source_units':max(rms(played[f],rev_played[f]) for f in frames),
                'max_mesh_step_source_units':max(rms(played[f],played[f-1]) for f in frames[1:]),
                'seam_mesh_rms_source_units':rms(played[first],played[last]),
                'negative_adjacent_quaternion_dots':sum(sum(values[f]['rotations'][n][i]*values[f-1]['rotations'][n][i] for i in range(4))<0 for n in names for f in frames[1:])}
            w.write_json(out/(clip+'-'+method+'-channels.json'),values)
            if method=='explicit_forward': preview_channels[clip]=values
            target.animation_data_clear(); bpy.data.actions.remove(bake)
        comparisons={name:max(rms(vertices['explicit_forward'][f],v[f]) for f in frames) for name,v in vertices.items()}
        result['clips'][clip]={'source_order_max_matrix_error':source_order_error,'source_endpoint_max_matrix_error':source_seam,
            'fps':scene.render.fps,'fps_base':scene.render.fps_base,'range':[first,last],
            'variants':variants,'max_mesh_rms_against_explicit_forward_source_units':comparisons}
        w.write_json(out/'diagnostic.json',result)

    if parent_native is not None:
        native=Path(parent_native)
        if not native.is_absolute() or native.is_symlink() or w.file_sha256(native)!='1fbb2535aedc3a25227c87ff3d778e8b2d77efb9e620d30e4eef7e635f5c16bb':
            raise ValueError('Preview requires the exact sealed 3D-03 native')
        bpy.ops.wm.open_mainfile(filepath=str(native),load_ui=False,use_scripts=False)
        target=bpy.data.objects['character_01_armature']
        # Replace channel values in a disposable copy for visual diagnosis.
        # No synthetic arc, resampling, pose damping, or threshold change.
        for clip,values in preview_channels.items():
            action=bpy.data.actions['character_action_'+clip]
            for curve in w.action_channels(action):
                if curve.data_path=='location':
                    samples={f:v['root'][curve.array_index] for f,v in values.items()}
                else:
                    name=curve.data_path.split('"')[1]
                    samples={f:v['rotations'][name][curve.array_index] for f,v in values.items()}
                for key in curve.keyframe_points:
                    frame=int(round(key.co[0])); key.co[1]=samples[frame]
                    key.handle_left[1]=key.co[1]; key.handle_right[1]=key.co[1]
                    key.interpolation='LINEAR'
                curve.update()
        bpy.context.preferences.filepaths.save_version=0
        bpy.ops.wm.save_as_mainfile(filepath=str(out/'diagnostic-corrected.blend'),check_existing=False)
        temporal=out/'preview'; temporal.mkdir()
        w.character_temporal_evidence(temporal,{'name':'diagnostic_only','width':640,'height':360,'samples':2,'device':'CPU','shots':['shot_B']},303,
            {'schema_version':'1.0','camera_id':'camera_B','clips':{c:{'action':a,'frame_start':f,'frame_end':l} for c,(a,f,l) in w.CHARACTER_MOTION_ACTIONS.items()}})


def run_production_regression(w,out,plan):
    """Exercise the production importer under alternate evaluation orders."""
    if plan.get('experiment_id') not in {'3D-03','3D-03.1'} or set(plan.get('clips',{}))!={'idle','run','jump'}:
        raise ValueError('Production regression accepts only an admitted character plan')
    report={'schema_version':'1.0','experiment_id':'3D-03.1-PRODUCTION-REGRESSION','clips':{},'provider_calls':0}
    for clip in ('idle','run','jump'):
        variants={}
        for order in ('forward','reverse','isolated'):
            bpy.ops.wm.read_factory_settings(use_empty=True)
            model,model_actions=w.import_animated_fbx(plan['entity']['source'])
            if model_actions: raise ValueError('Regression model unexpectedly contains animation')
            target=next(obj for obj in model if obj.type=='ARMATURE'); mesh=next(obj for obj in model if obj.type=='MESH')
            for pose_bone in target.pose.bones:
                for constraint in list(pose_bone.constraints): pose_bone.constraints.remove(constraint)
            action=w.import_character_action(plan['clips'][clip],clip,target,mesh,capture_order=order)
            w.assign_character_action(target,action)
            first,last=(int(round(value)) for value in action.frame_range)
            samples=[float(first)]
            for frame in range(first,last): samples.extend((frame+.5,float(frame+1)))
            def evaluated(sequence):
                result={}
                for frame in sequence:
                    bpy.context.scene.frame_set(int(frame),subframe=frame-int(frame)); bpy.context.view_layer.update()
                    points=w._evaluated_character_points(mesh)
                    if not all(math.isfinite(value) for point in points for value in point):
                        raise ValueError('Production regression produced non-finite geometry')
                    result[frame]=points
                return result
            forward=evaluated(samples); reverse=evaluated(list(reversed(samples)))
            variants[order]={'points':forward,
                             'playback_order_max_rms':max(rms(forward[frame],reverse[frame]) for frame in samples),
                             'fractional_sample_count':sum(not frame.is_integer() for frame in samples),
                             'capture_property':action.get('mf_capture_order')}
        baseline=variants['forward']['points']
        comparisons={order:max(rms(baseline[frame],variant['points'][frame]) for frame in baseline)
                     for order,variant in variants.items()}
        report['clips'][clip]={
            'capture_order_max_mesh_rms':comparisons,
            'playback_order_max_mesh_rms':{order:variant['playback_order_max_rms'] for order,variant in variants.items()},
            'fractional_sample_count':variants['forward']['fractional_sample_count'],
            'capture_properties':{order:variant['capture_property'] for order,variant in variants.items()},
        }
    tolerance=1e-7
    report['tolerance_source_units']=tolerance
    report['passed']=all(value<=tolerance for clip in report['clips'].values()
                         for group in ('capture_order_max_mesh_rms','playback_order_max_mesh_rms')
                         for value in clip[group].values())
    w.write_json(out/'production-regression.json',report)
