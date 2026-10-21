"""Actual five-image rejection, including the diagnostic camera metadata defect."""
import json
from pathlib import Path
from movie_factory import production_workflow as wf,production_knowledge as pk
from movie_factory.native_admission import Bridge
from movie_factory.task_router import DATABASE
root=Path(__file__).resolve().parents[1];out=root/'results/sikh335/look01'
c=wf.Controller(root,DATABASE);task='sikh335-supporting-appearance'
observations={
 'render':'Both283 and327 inspected. Horse has less polished highlights, but rider cloth still reads as smooth anatomical clothing, headwear remains too mechanically layered and face/beard do not yet share accepted film richness.',
 'leader_front':'Front close-up reveals angular projecting collar, very smooth shirt and sash, strip seam up crown, thin pointed beard and staring insert-like eyes. These were not adequately revealed in shot-size checks.',
 'leader_reverse':'Reverse shows a regular seam/gap through crown courses, very smooth back and unsupported-looking collar flap. Saddle pad upper edge/contact still needs verification through motion.',
 'crowd_front':'The test warrior is visible behind a foreground actor, but the crop is still not a clean complete-body proof. Crown has a vertical seam and cheek/beard junction is abrupt; mannequin surface persists.'}
for step,observation in observations.items():
 run=pk.read_json(root,f'results/sikh335/look01/{step}-run-c3.json')
 v={'verdict':'FAIL','run_digest':pk.digest(run),'evidence':run['artifacts'],
    'observation':observation,'comparison':'Compared with accepted Pashtun supported cloth and integrated face/hair, and the faithful rearing source for mounted contacts. Improvement over c2 does not pass same-film quality.',
    'open_defects':['Whole supporting appearance remains below quality floor','No continuous performance acceptance']}
 if step!='render':
  v['observation']+=' Camera manifest records stale identity before dependency update; images are real but recorded camera transform is not trustworthy.'
  v['open_defects'].append('Diagnostic camera matrix captured before evaluated update')
 Bridge(c).record_review(task,step,v)
 (out/(step+'-review-c3.json')).write_text(json.dumps(v,indent=2)+'\n')
print('Four evidence steps rejected; five images inspected. No artistic pass.')
