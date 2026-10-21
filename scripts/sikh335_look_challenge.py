"""Record the actual pre-native reference-role failure without bypassing limits."""
import json
from pathlib import Path
from movie_factory import production_workflow as wf, production_knowledge as pk, planning_pipeline as pp
from movie_factory.task_router import DATABASE
root=Path(__file__).resolve().parents[1];c=wf.Controller(root,DATABASE);task='sikh335-supporting-appearance'
p=c.packet(task)
checks={k:{'status':'PASS','observation':'Existing335 local supporting-appearance scope and actual cast findings are bound.',
    'comparison':'No motion retry, new spend, replacement principal or appearance pass is authorized by this plan.',
    'source_ids':['direction','cast_findings']} for k in pp.FACETS}
checks['reference_roles']={'status':'FAIL','observation':'Accepted Pashtun PNG inherited faithful_motion role,14–19s interval and rear-specific authority from copied reference.',
    'comparison':'The source is an accepted appearance-quality still, not a faithful-motion authority. Correct binding bytes alone do not correct its role.',
    'source_ids':['film_language','references']}
checks['method']={'status':'NOT_RUN','observation':'No appearance native job launched; handler tests pass but shape hypothesis remains untested.',
    'comparison':'Do not admit construction with wrong source-role authority. Preserve initial method and evaluate only after grounded repair.',
    'source_ids':['controls','cast_findings']}
verdict={'input_digest':p['planning_input_digest'],'outcome':'revise','checks':checks,
    'strongest_counterexample':'Copying a structurally valid reference contract can preserve all required fields while changing its semantic meaning. Source type and actual Director role must be checked before admission.',
    'issues':[{'id':'incorrect-still-role','target':'GROUNDING','reason':'Accepted quality still mislabeled as faithful motion.',
        'counterexample':'A PNG cannot contain a14–19second performance interval; the text also claims the wrong Director instruction.',
        'repair':'Construct an explicit accepted_quality reference from the original same-film authority; remove temporal fields, retain original rearing contract separately, regenerate affected downstream artifacts without resetting history or allowances.'}]}
c.submit(task,p['actor'],p['ticket'],verdict,'sikh335-look-reference-rejected')
(root/'results/sikh335/look01/challenge-verdict.json').write_text(json.dumps(verdict,indent=2)+'\n')
print(c.state(task)['stage'])
