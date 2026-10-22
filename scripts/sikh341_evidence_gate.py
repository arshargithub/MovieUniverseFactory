"""Record the actual failed garment prerequisite without inherited pass labels."""
import json,subprocess,hashlib
from pathlib import Path
from movie_factory import production_knowledge as pk
r=Path(__file__).resolve().parents[1];out=r/'results/sikh335/look01'
p=pk.read_json(r,'.runtime/knowledge-pilot213/sikh341-current.json')
paths=['results/sikh335/look01/exhaustion-c19.json','results/sikh335/REASSESSMENT_341.md']
evidence=[{'path':x,'sha256':pk.file_hash(r/x)} for x in paths]
checks=[]
for ob in p['obligations']:
 checks.append({'id':ob['id'],'kind':ob['check_kind'],
  'status':'FAIL' if ob['id'] in ('construction_interfaces','visual_gate','look','cache_safety') else 'NOT_RUN',
  'action_taken':'Actual neutral drape performed and inspected; rejected visible neckline and strict reopen dependency failures. Bend blocked, allowance19 exhausted without reset.',
  'observation':'Two actual neutral saves/four images are prerequisite evidence only.19 fabric improves but neckline fails. Full character/AV and controlled bend remain unqualified. Original complete production obligations are not narrowed to this shirt.',
  'evidence':evidence})
review={'packet_digest':p['packet_digest'],'checks':checks,
 'hypotheses':[{'prediction':'Actual neutral donor support and continuous shoulder topology can avoid the posed rectangular-armhole failures.',
  'observation':'Both neutral simulations save within90mm guard.19 front/back/side show coherent shoulders and fabric, but the front neckline remains visibly wrong.',
  'response':'Keep neutral review as a hard dependency. Next allowance would address actual neckline topology/evaluated clearance and reopen before bending.',
  'result':'unresolved'}],
 'adjacent_regressions':'No source overwrite or production motion edit.19 original-scene selected states match after actual evaluation; orphan-library inventory remains a strict failure. No reinterpretation as successful receipt.',
 'stopping_reason':'Appearance19/max19 exhausted. Bend NOT_RUN because neutral form fails. Genuine authority boundary, not completion or production review queue.'}
(out/'knowledge-review341.json').write_text(json.dumps(review,indent=2)+'\n')
# Reconstruct every executed handler byte from changed-file snapshots plus the
# recorded Git parent. This replaces duplicated copies of97 unchanged files.
provenance=[]
for cycle in (18,19):
 manifest=pk.read_json(r,f'results/sikh335/look01/source-manifest-c{cycle}.json')
 for path,digest in manifest.items():
  saved=out/f'source-c{cycle}'/Path(path).name
  data=saved.read_bytes() if saved.is_file() else subprocess.check_output(['git','show','7d079d6:'+path],cwd=r)
  assert hashlib.sha256(data).hexdigest()==digest,(cycle,path)
 provenance.append({'cycle':cycle,'handlers':len(manifest),'git_parent':'7d079d6',
                    'changed_blobs':str((out/f'source-c{cycle}').relative_to(r)),'all_bytes_verified':True})
(out/'source-reconstruction341.json').write_text(json.dumps(provenance,indent=2)+'\n')
print('Failed review and exact executed handler reconstruction recorded')
