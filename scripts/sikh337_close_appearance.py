"""Record exhausted failed attempt without reclassifying it as an art result."""
import json
from pathlib import Path
from movie_factory import production_workflow as wf
from movie_factory.task_router import DATABASE
root=Path(__file__).resolve().parents[1];c=wf.Controller(root,DATABASE)
task='sikh335-supporting-appearance';state=c.state(task)
assert state['cycle']==state['max_corrections']==4
if state['stage']!='REPLAN_REQUIRED':
    d=state['direction']
    c.reground(task,d['context_sources'],d['knowledge_task'],d['knowledge_digest'],
      'Correction4 failed before simulation: standalone worker cannot use package-relative import. Import helper fixed and standalone-loader regression passes, but no fifth dispatch is authorized. Preserve failed run and c3 visual failures. Cloth method remains untested, not disproved.',
      'sikh337-appearance-exhaustion')
state=c.state(task)
report={k:state[k] for k in ('task','stage','planning_step','cycle','max_corrections')}
report.update({'artistic_pass':False,'last_native_result':'FAILED_BEFORE_SIMULATION',
 'remaining_known_defects':['smooth anatomical garment','mechanical headwear','face/beard integration','collar and underarm interfaces','moving saddle contact'],
 'next_requires':'Explicit appearance correction extension; no counter reset or new task.',
 'repair_ready':'Standalone fixed-path import regression passes; actual cloth simulation has NOT_RUN.'})
(root/'results/sikh335/look01/exhaustion-c4.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))
