"""Close only this measured work interval, retaining experiment lifecycle."""
import json
from datetime import datetime, timezone
from pathlib import Path
from movie_factory.experiment_ledger import Ledger, timestamp

r = Path(__file__).resolve().parents[1]
ledger = Ledger(r/'.runtime/experiment-ops.sqlite3')
events = ledger.events()
start = next(e for e in events if e['event_id'] == 'sikh347-work-start')
end = next((e for e in events if e['event_id'] == 'sikh347-work-end'), None)
if end is None:
    end = dict(event_id='sikh347-work-end', experiment_id=start['experiment_id'],
        episode_id=start['episode_id'], phase=start['phase'], event_type='work_ended',
        activity_id=start['activity_id'], utc=datetime.now(timezone.utc).isoformat(),
        note='Exhausted five347 corrections; final whole actor FAIL; technical evidence preserved. Experiment not closed.')
    ledger.append(end)
out = r/'results/sikh335/closure347/operating-interval.json'
value = dict(events=[start,end], elapsed_seconds=timestamp(end['utc'])-timestamp(start['utc']),
    verified_director_idle_seconds=0,
    scope='Measured active turn interval including overlapping local jobs; excludes unmeasured startup reading before work-start. No Director-response wait occurred inside this interval. Not model-only compute or total historical effort. Post-interval Git handoff overhead is outside this measurement.',
    lifecycle='OPEN', gaps=['Initial continuation/source retrieval before recorded start', 'Final Git handoff overhead after recorded end'])
text = json.dumps(value,indent=2)+'\n'
if out.exists():
    assert out.read_text() == text
else:
    out.write_text(text)
print(json.dumps(dict(elapsed_seconds=value['elapsed_seconds'], lifecycle='OPEN')))
