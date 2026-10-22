"""Record only the measured final verification interval; do not infer earlier time."""
import argparse
import json
from datetime import datetime,timezone
from pathlib import Path
from movie_factory.experiment_ledger import Ledger,timestamp

root=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('action',choices=['start','end'])
args=parser.parse_args()
ledger=Ledger(root/'.runtime/experiment-ops.sqlite3')
kind='work_started' if args.action=='start' else 'work_ended'
ident='workflow350-verify-'+args.action
existing=next((e for e in ledger.events() if e['event_id']==ident),None)
if existing is None:
    ledger.append(dict(event_id=ident,experiment_id='workflow350',episode_id='offline-implementation',
        event_type=kind,phase='verification-documentation',activity_id='workflow350-final-verification',
        utc=datetime.now(timezone.utc).isoformat(),note='Partial measured interval only; earlier source recovery and implementation not timed. No production campaign opened.'))
if args.action=='end':
    pair=[e for e in ledger.events() if e['event_id'] in {'workflow350-verify-start','workflow350-verify-end'}]
    result=dict(events=pair,elapsed_seconds=timestamp(pair[1]['utc'])-timestamp(pair[0]['utc']),
        verified_director_wait_seconds=0,gaps=['Source recovery and implementation before recorded start','Final Git and response overhead after end'],
        scope='Verification and documentation elapsed interval, overlapping test time included once. Not total work, model time, production time or efficiency improvement.')
    path=root/'results/workflow350/operating-interval.json'
    if not path.exists():path.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(elapsed_seconds=result['elapsed_seconds'])))
else:print(ident)
