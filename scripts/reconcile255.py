"""One explicit reviewed source reconciliation; never a generic staleness bypass."""
import json
from pathlib import Path
from movie_factory import production_knowledge as pk

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'.runtime/knowledge-pilot213/calibration255'

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    if (OUT/'pins-before.json').exists():raise RuntimeError('Already reconciled; inspect rather than rerun')
    catalog,pins=pk.load(ROOT) # Existing nine-source corpus must still be reviewed/fresh.
    (OUT/'pins-before.json').write_text(json.dumps(pins,indent=2)+'\n')
    (OUT/'catalog-before.json').write_text(json.dumps(catalog,indent=2)+'\n')
    lessons=[
      ('au_reference',['modeling','identity'],'AU01-AU05/AU08: preserve approved identity/native differences; images are art-direction references, not literal reconstruction mandates. Inspect candidate license, editable topology and whole-character fit before commitment. Test genuinely different visual languages, not filters; interpret unseen views explicitly.'),
      ('au_deformation',['anatomy','cloth'],'AU06/AU09-AU10: separate geometry/texture/light and pivot/weight/corrective hypotheses using matched controls. Test full and partial bends, landmark volumes and neighboring regions. Trace both shawl edges over shoulders/rear above harness with supports in actual motion; do not hide anatomy with clothes or polish a failing representation.'),
      ('au_performance',['motion','secondary'],'AU07/AU11-AU12: stable gaze is not a rigid torso/neck. Brief coordinated absorption, intent phases, support/forcing/lag/recovery and actual screen visibility. Inspect real motion where available; still samples cannot certify speed, acting or temporal naturalness. New camera/action invalidates affected checks.'),
      ('au_contact',['contact','prop'],'AU13: touching reins does not prove a fist. First inspect bare joint origins and closed silhouette, then thumb/rein/sleeve/mane integration and partial motion. Include known-bad controls and preserve tolerated-defect reopening triggers; no false pass from constraint distance or relative improvement.'),
      ('au_surface',['visual','look'],'AU06/AU11: preserve approved surface texture at multiple scales and matched lighting. Terrain, dust contrast, skin, costume and background form one look; light/palette changes reopen dependent visibility. Rich illustrated detail is not flat simplification or photorealistic noise.'),
      ('au_staging',['camera'],'AU04/AU12: establish danger and escape route before decisive action; screen-side coordinates, occlusion and camera proximity must support thought process and signature beat. Protect opening hook and final determined continuation; camera work is narrative, not only beautiful framing.'),
      ('au_audio',['audio','narration','delivery'],'AU14-AU15: Director discovery governs music taste; no Gemini taste gate. Test voice/music/effects together with real listening, key-word intelligibility and phone context. Preserve music arc across trailer, exact cue mapping, editable stems/graphics and unchanged picture for mix-only revisions. Signal levels are not hearing.'),
      ('au_reuse',['knowledge','render','delivery'],'AU16: package exact accepted versions, dependencies, rights, editable recipe and tested-use limits; verify remote restore and portable dependency closure. Separate foundation from adaptation, native jobs from work/waits and unknown cost; capture issue/review IDs before next sequence. No prediction from145h divided by20s.'),
      ('au_review',['knowledge'],'AU13/251: distinguish requirement, retrieval, method, evidence and judgment failures. Compare known rejected AND accepted controls, record specific observations and uncertainty, and test omitted/failed evidence blocking. Earlier falsification and fewer repeat escapes matter more than fewer messages. Calibration is familiar non-independent evidence, not universal judgment.'),
    ]
    catalog['sources']['audit250']={'path':'docs/knowledge/PASHTUN_PRODUCTION_AUDIT250.md','records':[x[0] for x in lessons],'reason':'Reviewed AU01-AU16, fixed-cutoff metrics, source limitations and251 deductions; routed actions preserve original statuses and evidence limits.'}
    catalog['sources']['current255']={'path':'docs/knowledge/CURRENT_PRODUCTION_STATE.md','records':['current_state','narrative','render_profile'],'reason':'Reconciled Director253 exact provisional approval and254/255 prerequisites with delivery SHA and recorded replay exception; not final release approval.'}
    catalog['records'].append(dict(id='current_state',status='adopted',kind='constraint',tags=['*'],sources=['current255'],check_kind='process',action='Read CURRENT_PRODUCTION_STATE.md before acting on historical pending wording.253 provisionally accepts exact finish24820s unit, including corrected fist and selected B/Kirk sound. Final pass only at full-trailer release approval; no routine reopening. Strict248 pixel replay FAIL and rights/recovery limits persist.255 authorizes protection/calibration, not new character production, paid calls or public release. Resolve conflicting/current authority rather than accepting top search hit.'))
    for id,tags,action in lessons:
        catalog['records'].append(dict(id=id,status='adopted',kind='workflow',tags=tags,sources=['audit250'],check_kind='review',action=action))
    for r in catalog['records']:
        if r['id']=='narrative':
            r.pop('unresolved_decision',None);r.pop('decision_exceptions',None)
            r['action']+=' Director253 provisionally approves this performed voice within the exact20s unit. New narration/script/provider calls still require their own authority; historic select_performed_voice blocker is superseded for this unit.'
            r['sources'].append('current255')
        if r['id']=='render_profile':
            r['action']+=' Current248 strict repeat exception remains FAIL despite253 creative approval: two red-channel values2/255 in one control; no general profile promotion.'
            r['sources'].append('current255')
    for e in ('hand','rein','shot','officer','film','music_reference'):
        catalog['entities'][e]['version']='finish248-20s-director253-provisional-not-release'
    catalog['entities']['renderer']['version']='248-strict-replay-fail-separate-from253-creative'
    catalog['version']='255-reviewed-current-state-and-audit-actions'
    (ROOT/pk.CATALOG).write_text(json.dumps(catalog,indent=2)+'\n')
    try:pk.load(ROOT)
    except pk.KnowledgeError as e:
        (OUT/'staleness-before-reconciliation.json').write_text(json.dumps({'blocked':True,'reason':str(e)},indent=2)+'\n')
    else:raise AssertionError('Changed source interpretation did not block')
    newpins=pk.freeze(ROOT)
    assert all(newpins['sources'][k]==v for k,v in pins['sources'].items())
    newpins['method']='255 explicit reconciliation: nine prior source snapshots unchanged; two manually reviewed current/audit sources and ten actions added. Initial misses and old pins retained.'
    (ROOT/pk.PINS).write_text(json.dumps(newpins,indent=2)+'\n')
    report=pk.evaluate(ROOT,'docs/knowledge/pilot/calibration255-cases.json')
    (OUT/'retrieval-after.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'passed':report['passed'],'missing':{c['id']:c['missing_critical'] for c in report['cases']},'extra_counts':{c['id']:len(c['extra_context']) for c in report['cases']}}))

if __name__=='__main__':main()
