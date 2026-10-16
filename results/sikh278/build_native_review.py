"""Evidence assembly for completed static evaluation, blocked actor admission."""
import hashlib
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
p=json.loads((ROOT/'.runtime/knowledge-pilot213/sikh278-native-final.json').read_text())
paths=['results/sikh278/NATIVE_ASSESSMENT.md','results/sikh278/native-inspection.json',
       'results/sikh278/native-reopen.json']
paths += ['.runtime/art-direction/series01-sikh278/native-inspection02/'+name+'.png'
          for name in ('front','left-quarter','right-quarter','profile','rear','crown')]
evidence=[{'path':f,'sha256':hashlib.sha256((ROOT/f).read_bytes()).hexdigest()} for f in paths]
passed={'authority','strategy','anticipation','stopping','versioning','economics','rights','current_state','sikh_scope'}
failed={'visual_gate','representation','anatomy'}
checks=[]
for r in p['obligations']:
    status='PASS' if r['id'] in passed else 'FAIL' if r['id'] in failed else 'NOT_RUN'
    checks.append({'id':r['id'],'kind':r['check_kind'],'status':status,
        'action_taken':'Applied generic static scope and geometry-first falsification; preserved raw source and rejected history; withheld actor admission.',
        'observation':('Scoped evaluation process completed with six inspected views and exact native geometry reopen; see explicit findings.' if status=='PASS' else
                       'Fused eyes/beard/cloth and missing animation anatomy prevent production use; generic study is not the approved hero.' if status=='FAIL' else
                       'Not exercised by this static geometry evaluation; no performance, surface-treatment or production staging qualification.'),
        'evidence':evidence})
review={'packet_digest':p['packet_digest'],'checks':checks,
 'hypotheses':[
  {'prediction':'Surface detail may conceal absent independent performance anatomy.',
   'observation':'No textures in GLB; one connected surface with fused eyes/beard/cloth and no rig.',
   'response':'Do not admit as actor; conversion proof recommended before purchase or hero exposure.','result':'unresolved'},
  {'prediction':'Rear/crown may lose major wrap structure.',
   'observation':'Native rear and crown retain diagonal fold geometry but regularize hidden folds.',
   'response':'Retain as static sculpt reference only, not a verified tying route.','result':'resolved'},
  {'prediction':'Camera/lighting may misrepresent anatomy.',
   'observation':'Initial overlit torso-front replaced with subdued face-aligned diagnostic views without vertex edits.',
   'response':'Preserved initial evidence and selected02 for review.','result':'resolved'}],
 'adjacent_regressions':'Raw mesh coordinate/connectivity hashes unchanged; no accepted character edits. Native02 fresh reopen exact. Generic source not accepted identity.',
 'stopping_reason':'Bounded static evaluation complete. Known structural deficits and unrun performance keep actor gate blocked; no blind extra generation or paid upgrade.'}
(ROOT/'results/sikh278/native-review.json').write_text(json.dumps(review,indent=2)+'\n')
