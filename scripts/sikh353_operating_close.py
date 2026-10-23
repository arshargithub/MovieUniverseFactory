"""Close353 work interval without closing production or claiming backup."""
import json
from datetime import datetime, timezone
from pathlib import Path
from movie_factory.experiment_ledger import Ledger, timestamp
from movie_factory import production_knowledge as pk

r = Path(__file__).resolve().parents[1]
ledger = Ledger(r / '.runtime/experiment-ops.sqlite3')
events = ledger.events()
start = next(e for e in events if e['event_id'] == 'sikh353-work-start')
end = next((e for e in events if e['event_id'] == 'sikh353-work-end'), None)
if end is None:
    end = dict(event_id='sikh353-work-end', experiment_id=start['experiment_id'],
               episode_id=start['episode_id'], phase=start['phase'], event_type='work_ended',
               activity_id=start['activity_id'], utc=datetime.now(timezone.utc).isoformat(),
               note='Ten corrections exhausted; component repairs retained, whole leader appearance/performance unqualified. Crowd deferred; experiment open.')
    ledger.append(end)
value = dict(events=[start, end], elapsed_seconds=timestamp(end['utc']) - timestamp(start['utc']),
             verified_director_idle_seconds=0, lifecycle='OPEN',
             scope='Active-turn interval includes overlapping serial native jobs; not additive, not model-only time. No Director-response wait during recorded interval.',
             gaps=['Bootstrap before recorded start', 'Final Git and handoff overhead after recorded end'])
p = r / 'results/sikh353/operating-interval.json'
assert not p.exists()
p.write_text(json.dumps(value, indent=2) + '\n')
for prefix in ('appearance', 'motion'):
    gate = r / f'.runtime/knowledge-pilot213/sikh353-{prefix}-gate.json'
    result = dict(source=str(gate.relative_to(r)), sha256=pk.file_hash(gate),
                  result=json.loads(gate.read_text()), note='Exit2 retained; no production-media handoff.')
    (r / f'results/sikh353/{prefix}-knowledge-gate.json').write_text(json.dumps(result, indent=2) + '\n')
log = r / '.runtime/context-hygiene/runs/sikh353-tests-final/stdout.log'
assert '110 passed' in log.read_text()
(r / 'results/sikh353/verification.json').write_text(json.dumps(dict(
    tests=110, path=str(log.relative_to(r)), sha256=pk.file_hash(log),
    scope='Focused software regression checks, not visual or audiovisual qualification.'), indent=2) + '\n')
print(dict(elapsed_seconds=value['elapsed_seconds'], lifecycle='OPEN'))
