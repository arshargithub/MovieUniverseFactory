"""Record exact mixed production continuation before construction."""
import json
from pathlib import Path
from movie_factory import production_knowledge as pk
r=Path(__file__).resolve().parents[1];out=r/'results/sikh363'
authority=dict(path='results/sikh363/REQUEST.md',sha256=pk.file_hash(out/'REQUEST.md'))
for label in ['appearance','motion']:
 v=dict(text=(out/'REQUEST.md').read_text(),operations=['native_inspect','asset','motion','edit','render','code','test','document'],continuation=True,authority=authority,rationale='Explicit363 revision of the original isolated leader/horse task, adding ten to each existing maximum without discarding unused corrections or history. Appearance chest/hand/flag form and motion phased speed/signal/cloth/gaze jointly require asset and performance work. No crowd/principal/Pashtun/provider/spend/cloud authority.')
 (out/(label+'-entry.json')).write_text(json.dumps(v,indent=2)+'\n')
v=dict(text='Reconcile current source bindings and apply the explicit363 rejection/allowances on original tasks before native construction.',operations=['code','document'],authority=authority,rationale='Administrative source/authority continuation repair after appearance entry blocked on a changed362 learning document. Review the actual changes, preserve stale evidence, reground original task without resetting limits; no native execution in this administrative route.')
(out/'reconcile-entry.json').write_text(json.dumps(v,indent=2)+'\n')
