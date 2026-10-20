"""Explicit319 reviewed-source addition; refuse changes to any prior source pin."""
import json
from movie_factory import production_knowledge as pk
from sikh319 import ROOT
out=ROOT/'results/sikh319/knowledge'
assert not out.exists();out.mkdir()
old=json.loads((ROOT/pk.PINS).read_text())
new=pk.freeze(ROOT)
assert len(old['sources'])==13 and len(new['sources'])==14
assert all(new['sources'][k]==v for k,v in old['sources'].items())
assert set(new['sources'])-set(old['sources'])=={'construction319'}
(out/'source-pins-before.json').write_text(json.dumps(old,indent=2)+'\n')
(ROOT/pk.PINS).write_text(json.dumps(new,indent=2)+'\n')
(out/'reconciliation.json').write_text(json.dumps({
    'source':'docs/knowledge/CONSTRUCTION_INTERFACES_319.md',
    'basis':'Reviewed local failures and verified16/19 contacts; no artistic acceptance',
    'prior_sources_preserved':13,'new_source_count':14,'new_record_count':49,
    'limitations':'Agent-curated finite routing, not independent semantic recall or visual judgment.',
},indent=2)+'\n')
print(out)
