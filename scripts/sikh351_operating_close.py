"""Close captured active interval without closing the ongoing experiment."""
import json
from datetime import datetime,timezone
from pathlib import Path
from movie_factory.experiment_ledger import Ledger,timestamp
from movie_factory import production_knowledge as pk
r=Path(__file__).resolve().parents[1];ledger=Ledger(r/'.runtime/experiment-ops.sqlite3')
events=ledger.events();start=next(e for e in events if e['event_id']=='sikh351-work-start')
end=next((e for e in events if e['event_id']=='sikh351-work-end'),None)
if end is None:
 end=dict(event_id='sikh351-work-end',experiment_id=start['experiment_id'],episode_id=start['episode_id'],phase=start['phase'],event_type='work_ended',activity_id=start['activity_id'],utc=datetime.now(timezone.utc).isoformat(),note='Five authorized corrections exhausted; actual anatomy candidates rejected; experiment remains open.')
 ledger.append(end)
value=dict(events=[start,end],elapsed_seconds=timestamp(end['utc'])-timestamp(start['utc']),verified_director_idle_seconds=0,
 scope='Captured active-turn interval includes overlapping serial native jobs, not additive to native occupancy. No Director-response wait within recorded interval. Not model-only time or complete historical effort.',
 lifecycle='OPEN',gaps=['Initial bootstrap retrieval before recorded start','Final Git/handoff overhead after recorded end'])
p=r/'results/sikh351/operating-interval.json';assert not p.exists();p.write_text(json.dumps(value,indent=2)+'\n')
gate=r/'.runtime/knowledge-pilot213/sikh351-gate.json'
out=dict(source=str(gate.relative_to(r)),sha256=pk.file_hash(gate),result=json.loads(gate.read_text()),note='Exit2 retained; no media handoff or artistic pass.')
(r/'results/sikh351/knowledge-gate.json').write_text(json.dumps(out,indent=2)+'\n')
print(dict(elapsed_seconds=value['elapsed_seconds'],lifecycle='OPEN'))
