"""Preserve incomplete evidence and apply exact authorized correction limits."""
import json
import sys
from pathlib import Path
from movie_factory import production_workflow as wf, production_knowledge as pk
from movie_factory import production_allowance as pa
from movie_factory.native_admission import Bridge
from movie_factory.task_router import DATABASE

root = Path(__file__).resolve().parents[1]
c = wf.Controller(root, DATABASE)
motion = 'sikh335-continuous-performance'
look = 'sikh335-supporting-appearance'
mode = sys.argv[1]
assert mode in {'close-motion', 'extend-motion', 'reground-look'}
with c.connect() as con:
    assert not con.execute('SELECT 1 FROM heavy_job').fetchone()

def persist(path, value):
    target = root / path
    if target.exists():
        raise RuntimeError('Preserve existing receipt: ' + path)
    target.write_text(json.dumps(value, indent=2) + '\n')

if mode == 'close-motion':
    state = c.state(motion)
    assert state['cycle'] == state['max_corrections'] == 6
    completed = {}
    for path in sorted((root / 'results/sikh335/motion01').glob('clip*-run-c6.json')):
        run = json.loads(path.read_text())
        Bridge(c).qualified(run)
        completed[run['step']] = run['artifacts']
    report = {'verdict':'FAIL', 'reason':'Known visible appearance failures; continuous evidence incomplete; manual-only execution step incompatible with native candidate admission.',
              'completed':completed, 'complete_clip':False, 'full_speed_av':'NOT_RUN',
              'preserved_candidate':'results/sikh335/motion01/save-run-c5.json',
              'next':'Use full contiguous evidence on the corrected integrated candidate, and the actual final controller review stage for manual judgment.'}
    persist('results/sikh335/motion01/partial-evidence-review-c6.json', report)
    c.replan(motion, 'STRATEGIZING', report['reason'] + ' See REASSESSMENT_337.md; no partial artistic pass.', 'sikh337-close-incomplete-c6')
elif mode == 'extend-motion':
    path = 'results/sikh335/motion01/allowance-337.json'
    decision = {'path':path, 'sha256':pk.file_hash(root / path)}
    c.route_request('sikh337-motion-extension', {
        'text':'Director337 approves four further corrections to the existing motion task.',
        'operations':['code','test','document'], 'authority':decision,
        'amendment_task':motion,
        'rationale':'Apply exact approved additional allowance, preserving completed attempts and partial evidence. No new spend or artistic approval.'})
    state = pa.extend(c, motion, 'sikh337-motion-extension', decision, 'sikh337-motion-four-approved')
    persist('results/sikh335/motion01/allowance-receipt337.json',
            {k:state[k] for k in ('task','stage','planning_step','cycle','max_corrections')})
else:
    state = c.state(look)
    assert state['cycle'] == 1 and state['max_corrections'] == 4
    d = state['direction']
    c.reground(look, d['context_sources'], d['knowledge_task'], d['knowledge_digest'],
               'Reviewed endpoint fix after first appearance worker rejected float32 fractional-power NaN before save. Preserve failed native run; source authority unchanged. Exact numerical tests and REASSESSMENT_337.md accompany the next plan.',
               'sikh337-look-numeric-repair')
for task in (motion, look):
    state = c.state(task)
    print(json.dumps({k:state[k] for k in ('task','stage','planning_step','cycle','max_corrections')}))
