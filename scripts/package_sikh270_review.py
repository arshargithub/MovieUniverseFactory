"""Bind manually recorded Sikh270 review and local comparison; no inferred PASS."""
import base64
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from movie_factory import production_knowledge as pk

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    out=ROOT/'results/sikh270';native=ROOT/'.runtime/art-direction/series01-sikh270/candidate-17'
    notes=json.loads((out/'observations.json').read_text())
    files=[p for p in native.iterdir() if p.is_file()]
    files.extend(ROOT/'.runtime/art-direction/series01-sikh270/candidate-12'/f for f in ('cloth.json','cloth-motion.npz','groom-compression.json'))
    manifest={str(p.relative_to(ROOT)):{'sha256':digest(p),'bytes':p.stat().st_size} for p in sorted(files)}
    (out/'file-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    task=json.loads((ROOT/'.runtime/knowledge-pilot213/sikh270-crown17-reopen.json').read_text())['task']
    task['id']='sikh270-native-design-review'
    task['intent']=notes['scope']
    task['inputs']={p:digest(ROOT/p) for p in task['inputs']}
    for p in ('results/sikh270/observations.json','results/sikh270/file-manifest.json','scripts/package_sikh270_review.py'):
        task['inputs'][p]=digest(ROOT/p)
    packet=pk.task_packet(ROOT,task)
    (out/'packet.json').write_text(json.dumps(packet,indent=2)+'\n');(out/'packet.md').write_text(pk.packet_markdown(packet))
    checks=[]
    for ob in packet['obligations']:
        entry=notes['checks'][ob['id']]
        paths=['results/sikh270/observations.json','docs/planning/SERIES_01_SIKH_ASSET_STRATEGY_262.md']+entry['files']
        checks.append(dict(id=ob['id'],kind=ob['check_kind'],status=entry['status'],action_taken=entry['action'],observation=entry['observation'],evidence=[dict(path=p,sha256=digest(ROOT/p)) for p in paths]))
    review=dict(packet_digest=packet['packet_digest'],scope=notes['scope'],checks=checks,hypotheses=notes['hypotheses'],adjacent_regressions=notes['adjacent_regressions'],stopping_reason=notes['stopping_reason'])
    (out/'review.json').write_text(json.dumps(review,indent=2)+'\n');(out/'gate.json').write_text(json.dumps(pk.check_review(ROOT,packet,review),indent=2)+'\n')
    entries=[('Front','front'),('Approved illustration','reference'),('Left three-quarter','three-quarter'),('Right three-quarter','opposite'),('Profile','profile'),('Back','rear'),('Crown','crown'),('Face covered','covered-front'),('Covered oblique','covered-quarter'),('Loose end','released-quarter')]
    slides=[];media=ROOT/'.runtime/art-direction/series01-sikh270/review-media';media.mkdir(exist_ok=True)
    for label,name in entries:
        source=ROOT/notes['accepted_reference'] if name=='reference' else native/(name+'.png')
        target=media/(name+'.jpg')
        subprocess.run(['sips','-s','format','jpeg','-s','formatOptions','68','--resampleHeightWidthMax','720',str(source),'--out',str(target)],check=True,stdout=subprocess.DEVNULL)
        caption='Approved directional illustration v03' if name=='reference' else 'Native17 · '+label+' · identity review, not animation approval'
        if name in {'covered-front','covered-quarter','released-quarter'}:caption='Fixed-body cloth control · '+label+' · actual uncovering NOT_RUN'
        slides.append(dict(label=label,caption=caption,src='data:image/jpeg;base64,'+base64.b64encode(target.read_bytes()).decode()))
    template=ROOT/'.runtime/art-direction/series01-sikh270/review-template.html'
    html=template.read_text().replace('__SLIDES__',json.dumps(slides))
    assert '__SLIDES__' not in html and len(html.encode())<1_000_000
    target=Path('/Users/adisharma/.codex/visualizations/2026/09/09/01a0878c-e7a2-75e0-873c-c31d97f879a1/sikh-guided-character.html')
    target.write_text(html)
    print(target,len(html.encode()))

if __name__=='__main__':main()
