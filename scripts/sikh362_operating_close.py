"""End recorded active work without inventing complete timing coverage."""
import json
from pathlib import Path
from datetime import datetime,timezone
from movie_factory.experiment_ledger import Ledger,timestamp
from movie_factory import production_knowledge as pk
r=Path(__file__).resolve().parents[1];o=r/'results/sikh362';l=Ledger(r/'.runtime/experiment-ops.sqlite3')
events=l.events();start=next(e for e in events if e['event_id']=='sikh362-work-start')
end=next((e for e in events if e['event_id']=='sikh362-work-end'),None)
if end is None:
 end=dict(event_id='sikh362-work-end',experiment_id='sikh335',episode_id='leader362',phase='construction',event_type='work_ended',activity_id='sikh362-work',utc=datetime.now(timezone.utc).isoformat(),note='Exact isolated leader/horse proof and scoped agent checks complete; human AV pending, remaining cycles retained.')
 l.append(end)
report=dict(events=[start,end],elapsed_seconds=timestamp(end['utc'])-timestamp(start['utc']),verified_director_idle_seconds=0,lifecycle='OPEN',scope='Recorded active interval includes rendering waits and errors; do not add native process seconds. No verified Director waiting inside this interval.',gaps=['Bootstrap before work-start','Final record/gate/commit/handoff operations after work-end','Per-job start/end timestamps were not prospectively recorded in the ledger; native elapsed receipts are separate and do not establish complete interval coverage'],tokens=None,engineering_cost_usd=None)
p=o/'operating-interval.json';p.write_text(json.dumps(report,indent=2)+'\n')
export=r/'.runtime/operating-sikh362-export';export.mkdir(exist_ok=True);p=export/'events.json';p.write_text(json.dumps([e for e in l.events() if e['experiment_id']=='sikh335'],indent=2)+'\n')
(o/'operating-export.json').write_text(json.dumps(dict(path=str(p.relative_to(r)),sha256=pk.file_hash(p),scope='Experiment remains OPEN; current export is not a verified backup/archive.'),indent=2)+'\n')
print('Recorded active seconds:',round(report['elapsed_seconds'],2),'full-turn net UNKNOWN')
