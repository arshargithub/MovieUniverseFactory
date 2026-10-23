"""Explicit same-task source reconciliation; no authority or counter reset."""
from pathlib import Path
from movie_factory.production_workflow import Controller
from movie_factory.task_router import DATABASE
r=Path(__file__).resolve().parents[1];c=Controller(r,DATABASE)
task='sikh335-continuous-performance';s=c.state(task)
assert s['cycle']==24 and s['max_corrections']==31
d=s['direction']
s=c.reground(task,d['context_sources'],d['knowledge_task'],d['knowledge_digest'],
    'Reviewed361 look/support handler integration changed shared source before late24 body-view review registration. Preserve24 actual evidence and all prior failures; no stale review is qualified. Reground original task for integrated89 parent and fresh same-camera/continuous review under unchanged authority and limits. See results/sikh361/MOTION24_REVIEW.md.',
    'sikh361-motion24-shared-source-reconciliation')
print(s['cycle'],s['stage'],s['max_corrections'])
