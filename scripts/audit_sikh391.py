"""Read-only evidence inventory for Director391; no production state mutation."""
import hashlib
import json
import re
import sqlite3
from collections import Counter, defaultdict
from pathlib import Path

from movie_factory.production_knowledge import digest

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'results/sikh391'
TASK = 'sikh335-supporting-appearance'
LOW, HIGH = 212, 261


def write(name, value):
    (OUT / name).write_text(json.dumps(value, indent=2) + '\n')


def binding(path):
    p = ROOT / path
    return {'path': str(path), 'sha256': hashlib.sha256(p.read_bytes()).hexdigest()}


def main():
    con = sqlite3.connect('file:' + str(ROOT / '.runtime/factory-entry.sqlite3') + '?mode=ro', uri=True)
    latest = json.loads(con.execute('SELECT state FROM events WHERE task=? ORDER BY seq DESC LIMIT 1', (TASK,)).fetchone()[0])
    before = {k: latest[k] for k in ('cycle', 'max_corrections', 'stage', 'fingerprint')}
    meta = json.loads((OUT / 'CYCLE_METADATA.json').read_text())
    cycles = {row['cycle']: row for row in meta}
    assert sorted(cycles) == list(range(LOW, HIGH + 1))
    plan_cycle = {}
    # Bind exact preserved brief versions, including pre-admission artifacts.
    for folder in ('sikh386', 'sikh387', 'sikh390'):
        for p in (ROOT / 'results' / folder).glob('*.json'):
            match = re.search(r'(?:revised|appearance-c)(\d+)', p.name)
            if not match or not LOW <= int(match[1]) <= HIGH:
                continue
            cy = int(match[1])
            x = json.loads(p.read_text())
            if isinstance(x.get('artifact'), dict):
                x = x['artifact'].get('brief', x)
            if 'work_unit' in x and 'requirements' in x:
                plan_cycle[digest(x)] = cy
    all_native = {}
    for run_id, raw in con.execute('SELECT id,record FROM native_runs WHERE task=?', (TASK,)):
        all_native[run_id] = json.loads(raw)
    native = {k: v for k, v in all_native.items() if LOW <= v['cycle'] <= HIGH}
    reviews = {}
    for run_id, raw in con.execute('SELECT run,record FROM native_reviews'):
        if run_id in native:
            reviews[run_id] = json.loads(raw)
    for cy, row in cycles.items():
        runs = [v for v in native.values() if v['cycle'] == cy]
        rev = [reviews[v['id']] for v in runs if v['id'] in reviews]
        pictures = {}
        for run in runs:
            for b in run.get('artifacts', {}).values():
                if Path(b['path']).suffix.lower() in {'.png', '.jpg', '.jpeg'}:
                    pictures[b['sha256']] = b
        closeouts = []
        for folder in ('sikh386', 'sikh387', 'sikh390'):
            p = ROOT / 'results' / folder / f'CYCLE{cy}_CLOSEOUT.json'
            if p.exists():
                closeouts.append({'binding': binding(p.relative_to(ROOT)), 'record': json.loads(p.read_text())})
        row.update(native_jobs=len(runs), native_failed=sum(r['status'] != 'RETURNED' for r in runs),
                   unique_returned_images=len(pictures), image_bindings=list(pictures.values()),
                   review_dispositions=[v.get('cycle_disposition') for v in rev],
                   reviewed_artistic_images=bool(pictures) and any(v.get('cycle_disposition', {}).get('category') == 'art_rejected' for v in rev),
                   scoped_artistic_pass=any(v.get('cycle_disposition', {}).get('category') == 'scoped_image_proof_pass' for v in rev),
                   closeouts=closeouts)
    retro = []
    event_cycle = {}
    unmapped = []
    all_retro = []
    for seq, eid, raw in con.execute('SELECT seq,event_id,record FROM retrospective_events WHERE task=? ORDER BY seq', (TASK,)):
        x = json.loads(raw)
        d = x['data']
        cy = plan_cycle.get(d.get('plan'))
        if cy is None:
            m = re.search(r'(?:^|[-_])(?:appearance-)?c(\d+)(?:\D|$)', eid)
            if m:
                cy = int(m[1])
        if cy is None:
            a = str(d.get('attempt', ''))
            m = re.match(r'^(\d+):', a)
            if m:
                cy = int(m[1])
        for parent in (d.get('admission_event'), d.get('outcome_event'), d.get('response_event'), d.get('challenge', {}).get('response_event')):
            if cy is None and parent in event_cycle:
                cy = event_cycle[parent]
        if cy is None:
            for prefix in ('native:', 'native-review:'):
                if eid.startswith(prefix) and eid[len(prefix):] in all_native:
                    cy = all_native[eid[len(prefix):]]['cycle']
        event_cycle[eid] = cy
        record = dict(sequence=seq, event_id=eid, kind=x['kind'], cycle=cy, data=d)
        all_retro.append(record)
        if cy is not None and LOW <= cy <= HIGH:
            retro.append(record)
        elif cy is None:
            unmapped.append({'event_id': eid, 'kind': x['kind'], 'plan': d.get('plan')})
    # Every response/admission/evaluation attributed to this window must be traceable.
    counts = Counter(r['kind'] for r in retro)
    effects = Counter(r['data']['result'] for r in retro if r['kind'] == 'evaluate')
    response_cycles = sorted({r['cycle'] for r in retro if r['kind'] == 'response'})
    scope_counts = Counter(r['data'].get('scope_assessment', {}).get('decision', 'unspecified') for r in retro if r['kind'] == 'response')
    semantic_responses = defaultdict(list)
    for r in retro:
        if r['kind'] == 'response':
            d = r['data']
            semantic_responses[r['cycle']].append({k: d.get(k) for k in ('cause', 'uncertainty', 'change_or_retain_rationale', 'test', 'causal_assessment', 'scope_assessment', 'reference_assessment')})
    representative_responses = {}
    for cy, rs in semantic_responses.items():
        unique = {}
        for response in rs:
            unique[digest(response)] = response
        representative_responses[str(cy)] = dict(finding_responses=len(rs), distinct_bodies=len(unique), bodies=list(unique.values()))
    no_image = [cy for cy, r in cycles.items() if not r['reviewed_artistic_images']]
    image_cycles = sorted(set(cycles) - set(no_image))
    summary = dict(window=[LOW, HIGH], correction_slots=HIGH-LOW+1,
                   image_review_cycles=image_cycles, image_review_cycle_count=len(image_cycles),
                   without_artistic_image_review=no_image, without_artistic_image_review_count=len(no_image),
                   scoped_artistic_pass_cycles=[cy for cy, r in cycles.items() if r['scoped_artistic_pass']],
                   native_jobs=len(native), native_returned=sum(r['status']=='RETURNED' for r in native.values()),
                   native_failed=sum(r['status']!='RETURNED' for r in native.values()),
                   retrospective_event_counts=dict(counts), effectiveness_dispositions=dict(effects),
                   cycles_with_retro_responses=response_cycles, scope_response_counts=dict(scope_counts),
                   unmapped_all_history_events=unmapped,
                   first_source_binding_count=cycles[LOW]['source_bindings'], last_source_binding_count=cycles[HIGH]['source_bindings'],
                   first_brief_bytes=cycles[LOW]['brief_bytes'],last_brief_bytes=cycles[HIGH]['brief_bytes'],
                   production_state_before=before,
                   limits=['Image-review cycles are not unique independent anatomical candidates.',
                           'Per-finding retro records are not independent retrospectives or LLM calls.',
                           'This inventory does not establish wall-clock labor, token cost, false-rejection rate or artistic accuracy.',
                           'Media and representative source reasoning require separate manual inspection.'])
    write('CYCLE_LEDGER.json', sorted(cycles.values(), key=lambda x:x['cycle']))
    write('RETROSPECTIVE_WINDOW.json', retro)
    write('REPRESENTATIVE_RESPONSES.json', representative_responses)
    write('AUDIT_METRICS.json', summary)
    con.close()
    print(json.dumps({k: v for k,v in summary.items() if k not in {'unmapped_all_history_events','limits','production_state_before'}}))
    print('Unmapped all-history events:', len(unmapped))


if __name__ == '__main__':
    main()
