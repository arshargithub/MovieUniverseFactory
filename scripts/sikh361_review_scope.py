"""Append explicit bookkeeping corrections; never waive a creative failure."""
import json,sqlite3
from pathlib import Path
from movie_factory.production_workflow import Controller
from movie_factory.task_router import DATABASE
r=Path(__file__).resolve().parents[1];c=Controller(r,DATABASE)
items=[('motion','24','horse_head'),('motion','24','horse_head_reverse'),('appearance','88','leader_face')]
for label,cycle,step in items:
    task='sikh335-'+('continuous-performance' if label=='motion' else 'supporting-appearance')
    event=f'sikh361-{label}-c{cycle}-{step}-outcome'
    with sqlite3.connect(r/DATABASE) as con:
        record=json.loads(con.execute('SELECT record FROM retrospective_events WHERE task=? AND event_id=?',(task,event)).fetchone()[0])
    data=record['data'];data['supersedes']=event
    for row in data['observations']:
        assert row['status']=='UNKNOWN' and not row.get('foundation')
        row['status']='NOT_TESTED'
        row['observation']+=' Bookkeeping correction: this component render did not test the whole requirement; UNKNOWN was the wrong status. All actual creative failures remain unchanged.'
    c.retrospective(task,'outcome',data,event+'-scope-correction')
    print(task,step,'whole requirement NOT_TESTED; component native review retained')
