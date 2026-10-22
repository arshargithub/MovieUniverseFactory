"""Fixed24-second source-centred build; no runtime code inputs."""
from pathlib import Path
import importlib.util

def load(name):
 spec=importlib.util.spec_from_file_location(name,Path(__file__).with_name(name+'.py'));m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def run(mf,out,job,helper):
 if set(job)!={'mode','output_dir','profile'} or job['mode']!='demo_cut_motion' or job['profile']!={}:raise ValueError('Fixed cut motion job required')
 gait=load('demo_source_gallop');warp=load('cut_phase_math');original=gait.source_phase
 def phase(p,leg):
  if leg in ('LF','RF'):
   _,_,_,_,td,stroke=gait.LEGS[leg];p=warp.recovery_phase(p,td,stroke/(gait.SPEED/gait.HZ))
  return original(p,leg)
 gait.FRAMES=576;gait.source_phase=phase
 artifacts=gait.run(mf,out,{'mode':'demo_source_gallop_build','output_dir':job['output_dir'],'profile':{}},helper)
 mf.write_json(Path(out)/'recovery-change.json',{'frames':576,'fps':24,'scope':'front-leg swing only, all four control families','warp_strength':.5,'middle_swing_clock_speed_ratio':1.5,'support_timing_unchanged':True,'visual_acceptance':'NOT_RUN'})
 return artifacts+['recovery-change.json']
