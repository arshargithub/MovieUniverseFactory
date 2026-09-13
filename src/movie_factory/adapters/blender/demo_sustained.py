"""Reviewed fixed operations for the authorized six-second integrated preview."""
from pathlib import Path
import json,importlib.util,bpy
BASE=Path('/Users/adisharma/projects/MovieUniverseFactory/runs/demonstrator-01')
SHA='37594a7ef2d59e5dcc9af42c332f28ab41e86e78f78a60e6bd5ff9e2a7ca961e'
def validate(job,out):
    if set(job)!={'mode','output_dir','profile'} or job['mode'] not in ('demo_sustained_audit',) or job['profile']!={}:raise ValueError('Fixed sustained operation required')
    if BASE.resolve() not in Path(out).resolve().parents:raise ValueError('Invalid output')
def run(mf,out,job,helper):
    validate(job,out);out=Path(out);helper._file(BASE/'realism-motion/scene.blend',SHA);bpy.ops.wm.open_mainfile(filepath=str(BASE/'realism-motion/scene.blend'),load_ui=False,use_scripts=False)
    h=bpy.data.objects['horse.rig'];action=bpy.data.actions['horse.gallop'];channels=[{'path':f.data_path,'index':f.array_index,'keys':[(k.co.x,k.co.y) for k in f.keyframe_points]} for f in mf.action_channels(action)]
    bones={p.name:{'parent':p.parent.name if p.parent else None,'rotation_mode':p.rotation_mode,'bbone_segments':p.bone.bbone_segments,'constraints':[{'type':c.type,'subtarget':getattr(c,'subtarget',None),'target':getattr(getattr(c,'target',None),'name',None),'influence':c.influence} for c in p.constraints]} for p in h.pose.bones}
    mf.write_json(out/'source-controls.json',{'channels':channels,'bones':bones,'nla':[{'name':t.name,'mute':t.mute,'strips':[{'action':s.action.name,'repeat':s.repeat,'scale':s.scale} for s in t.strips]} for t in h.animation_data.nla_tracks]})
    return ['source-controls.json']
