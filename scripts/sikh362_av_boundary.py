"""Append-only correction of native availability versus human AV outcome."""
from pathlib import Path
from copy import deepcopy
from movie_factory import production_workflow as wf, retrospective as retro
from movie_factory.task_router import DATABASE
r=Path(__file__).resolve().parents[1];c=wf.Controller(r,DATABASE);task='sikh335-continuous-performance'
with c.connect() as con: history=retro.events(con,task)
ident='native-review:sikh362-motion-c27-tail_context'
prior=next(e for e in history if e['id']==ident)
data=deepcopy(prior['data']);data['supersedes']=ident
found=False
for row in data['observations']:
 if row['requirement']=='director_motion':
  found=True;row['status']='NOT_TESTED';row['observation']='Native frames available and source inspected, but full-speed Director313 judgment has NOT occurred. Availability PASS cannot imply human AV PASS.'
assert found
c.retrospective(task,'outcome',data,'sikh362-native-availability-not-human-av')
print('Native physical/source availability retained; director_motion NOT_TESTED; original history preserved.')
