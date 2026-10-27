"""Explicit static diagnostic profile; never changes a production source file."""
import json

def validate(e):
    if e!={'kind':'mounted_anatomy387_static_control','target':'horse'}:raise ValueError('STATIC387_CONTROL_FIELDS')
    return e

def freeze(scene):
    if not hasattr(scene.render,'use_motion_blur'):raise ValueError('STATIC387_MOTION_BLUR_PROPERTY_UNAVAILABLE')
    source=scene.render.use_motion_blur
    if type(source) is not bool:raise ValueError('STATIC387_MOTION_BLUR_TYPE')
    scene.render.use_motion_blur=False
    if scene.render.use_motion_blur is not False:raise ValueError('STATIC387_MOTION_BLUR_NOT_DISABLED')
    return dict(source_use_motion_blur=source,diagnostic_use_motion_blur=False,scope='Static shape diagnostic only; do not adopt this renderprofile as productionstyle. Originalsourcefile unchanged.')

def control(bpy,out,helpers):
    before=helpers('nihang_prep367').frozen(bpy);actions=helpers('nihang_padsolve370').actions(bpy)
    profile=freeze(bpy.context.scene)
    if before!=helpers('nihang_prep367').frozen(bpy) or actions!=helpers('nihang_padsolve370').actions(bpy):raise ValueError('STATIC387_CONTROL_SOURCE_DRIFT')
    result=dict(profile=profile,geometry_actions_unchanged=True,scope='Negative/source control only; no anatomical or temporal approval.')
    (out/'anatomy387-static-control.json').write_text(json.dumps(result,indent=2)+'\n');return result
