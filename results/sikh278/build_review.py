"""Produce a blocked disposition record, never native/visual admission."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
p = json.loads((ROOT / '.runtime/knowledge-pilot213/sikh278-disposition.json').read_text())
evidence = []
for name in ('results/sikh278/ASSESSMENT.md', 'results/sikh278/input-review.json',
             '.runtime/art-direction/series01-sikh278/meshy-result.jpg'):
    evidence.append({'path': name, 'sha256': hashlib.sha256((ROOT/name).read_bytes()).hexdigest()})
review = {
    'packet_digest': p['packet_digest'],
    'checks': [{'id': r['id'], 'kind': r['check_kind'], 'status': 'NOT_RUN',
                'action_taken': 'Preserved generic generation and export failure; withheld native/production admission.',
                'observation': 'No locally retrieved mesh. This is a blocker report, not a completed asset handoff; see scoped assessment.',
                'evidence': evidence} for r in p['obligations']],
    'hypotheses': [{'prediction': 'Fine beard detail may become fused sculpture rather than hair.',
                    'observation': 'Web preview supports this concern; downloaded geometry is unavailable.',
                    'response': 'Require neutral all-angle native inspection after retrieving existing GLB.',
                    'result': 'unresolved'}],
    'adjacent_regressions': 'No native or protected-source edits. Approved production artwork was not supplied to Meshy.',
    'stopping_reason': 'Two export allowances consumed without returned local file. Manual existing-file download required; no further blind retries.'
}
(ROOT/'results/sikh278/review.json').write_text(json.dumps(review, indent=2)+'\n')
