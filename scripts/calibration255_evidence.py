"""Record observed controls, fresh routing and a scoped current task. No providers."""
import json
from pathlib import Path
from movie_factory import production_knowledge as pk

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'.runtime/knowledge-pilot213/calibration255'

def write(name,data):
    (OUT/name).write_text(json.dumps(data,indent=2)+'\n')

def main():
    controls=[
      ('.runtime/art-direction/series01-entrance217/motion-diagnostic/L-sheet-0000.jpg','FAIL',
       'Repeated wide finger separations and extended finger sections outside the palm; rounded brown covering does not establish a convincing closed fist. Rein contact alone insufficient. This familiar historical rejection is not a blind benchmark.'),
      ('.runtime/art-direction/series01-finish248/fit07/L-outside.png','PASS_SCOPED_STATIC',
       'Compact fist silhouette; fingers folded against palm, thumb over index region. Rein routed beneath thumb. No glove. This outside view does not alone prove reverse side, joint pivots or motion; exact final unit253 has separate Director provisional approval.'),
      ('.runtime/art-direction/series01-facebuilder-trial-01/wardrobe175-preview01/upper-rear.png','FAIL',
       'Broad nearly horizontal corrugated rear band, abrupt rectangular ends and jagged shoulder connections. Not credible supported cloth; front-only success or mesh connectivity would miss this.'),
      ('.runtime/art-direction/series01-facebuilder-trial-01/wardrobe185-redressreview02/rear-217.png','PASS_SCOPED_STATIC',
       'Overlapping irregular cloth edges travel across outside of rear headfall and shoulders above harness. No rectangular corrugated band in this view. Under-fold route and motion cannot be certified by this single rear still.'),
      ('.runtime/art-direction/series01-facebuilder-trial-01/body161-fit41/accepted-neck-front.png','REFERENCE_ONLY',
       'Accepted bust clay control has defined central clavicle notch and paired clavicle slopes. This is the comparison authority for that historical integration, not a mandate to reconstruct the current accepted film.'),
      ('.runtime/art-direction/series01-facebuilder-trial-01/body161-fit41/neck-front.png','NOT_RUN_FOR_WHOLE_ANATOMY',
       'Front neck landmarks largely match the displayed accepted control; do not invent a neck failure from historical labels alone. Shoulder transition visible but this front still cannot clear seated deformation, back or side anatomy. A broad body PASS would be unsupported.'),
      ('.runtime/art-direction/series01-finish248/encoded-qc01/controls/clean-06.png','PASS_SCOPED_STATIC',
       'At final framing the compact fist reads without the old long extended fingers. Quote has legible dark type and visibly worn paper edges. Face remains expressive and recognizable. Still image does not establish duration, narration intelligibility or neck absorption.'),
      ('.runtime/art-direction/series01-finish248/encoded-qc01/controls/clean-18.png','PASS_SCOPED_STATIC',
       'Uphill shot retains the character and visible closed grasp. Weathered clothing and blue shawl contrast with light terrain. Neck and hands are partly occluded: not sufficient to certify all contact or motion. Preserve Director253 approval, do not reinterpret accepted native differences as new defects.'),
      ('.runtime/art-direction/series01-facebuilder-trial-01/body160-fit39/neck-front.png','FAIL',
       'Compared with accepted-neck-front control, clavicles form a broad prominent shelf and abrupt ridge across the upper chest; throat transition looks block-like. A matched clay comparison exposes geometry/readability failure without blaming skin or lighting.'),
      ('.runtime/art-direction/series01-facebuilder-trial-01/body158-fit25/seated-side.png','FAIL',
       'Bent elbow is a smooth tubular turn with little credible joint landmark/volume change. The armpit/chest transition is also tightly pinched. Static bent-pose control must fail broad natural articulation admission; no speed-based excuse.'),
      ('.runtime/art-direction/series01-facebuilder-trial-01/entrance198-motion04/frame-0217.png','NOT_RUN_FOR_DRAMATIC_MOTION',
       'A pale trailing cloud is visible but blends into pale ground. This small distant still does not prove the intended dramatic cloud at playback; do not call it invisible solely because historical feedback criticized it. Need consecutive frames, matched view and intended phone scale.'),
      ('.runtime/art-direction/series01-finish248/encoded-qc01/controls/clean-01.png','PASS_SCOPED_STATIC',
       'Trailing plume is readable against textured light terrain at final framing, with broad softened ground behind the horse. Static visibility only; no timing/dynamics claim or new creative approval. Not a matched quantitative before/after against198.'),
      ('.runtime/art-direction/series01-finish248/encoded-qc01/controls/clean-14.png','PASS_SCOPED_STATIC',
       'Mounted guards, barrier and camp are readable beyond rider; alternative rocky route visible on viewer right. Cloth wraps visible above rear headfall. This is a static causal-geography check, not proof of edit pacing.'),
    ]
    write('visual-controls.json',{'method':'Current agent re-inspected thirteen familiar historical images at review size; non-blind, non-independent. No production modifications or fresh global artistic pass.',
        'controls':[{'path':p,'sha256':pk.file_hash(ROOT/p),'judgment':v,'observation':o} for p,v,o in controls],
        'unknowns':['No real-time motion/audio perception measured by these stills.','No general audience-judgment accuracy established.','Exact accepted unit is not reopened because a diagnostic crop lacks full motion evidence.'],
        'review_rule':'Known bad controls must fail; accepted scope must not be inflated or routinely reopened; insufficient evidence for a new claim stays NOT_RUN.'})
    paths=['docs/knowledge/CURRENT_PRODUCTION_STATE.md','docs/knowledge/PASHTUN_PRODUCTION_AUDIT250.md',
           'docs/operations/ACTIVE_S3_BACKUP_POLICY.md','docs/planning/PROTECTION_CALIBRATION_255.md',
           'docs/knowledge/pilot/calibration255-cases.json','src/movie_factory/production_knowledge.py',
           'tests/test_calibration255.py','tools/protect255.py','tools/upload_protect255.py',
           'tools/restore_protect255_remote.py','scripts/protection255_native_check.py',
           'tools/finalize_protect255_delta.py']
    task={'id':'protection-calibration255','operation':'knowledge','entities':['knowledge'],
          'query':'Verify current authority, retrospective retrieval, application blocking, review calibration and recovery prerequisites',
          'intent':'Preserve accepted production; calibrate finite mechanisms and prepare/verify authorized protection, not new production.',
          'phase':'execution','inputs':{p:pk.file_hash(ROOT/p) for p in paths},
          'execution_authority':{'source':'docs/planning/PROTECTION_CALIBRATION_255.md','scope':'Director255 protection and calibration plus subsequent Go ahead for the stated Git range, private S3 snapshot and bounded final delta. No deletion, new production, paid models or release.'},
          'open_decisions':[], 'hypotheses_to_test':['Original regression success does not establish coverage of latest lessons/current approval.','Structural evidence validation cannot prove a visual observation is true.']}
    write('task.json',task)
    packet=pk.task_packet(ROOT,task);write('packet.json',packet)
    (OUT/'packet.md').write_text(pk.packet_markdown(packet))
    report=pk.evaluate(ROOT,'docs/knowledge/pilot/calibration255-cases.json');write('retrieval-after.json',report)
    print(json.dumps({'dispatch_ready':packet['dispatch_ready'],'blockers':packet['blockers'],'obligations':[x['id'] for x in packet['obligations']], 'retrieval_pass':report['passed']}))

if __name__=='__main__': main()
