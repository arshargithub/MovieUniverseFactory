"""Emit sidecars for actual reused sources, preserving historical manifests."""
import json,sys
from pathlib import Path
from movie_factory import production_knowledge as pk
from movie_factory.resource_manifest import validate
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results/sikh317/resources'
def binding(path):return {'path':path,'sha256':pk.file_hash(pk.safe_path(ROOT,path))}
def main():
    v=int(sys.argv[1]);assert 1<=v<=9
    native=f'.runtime/art-direction/series01-sikh317/build-{v:02d}'
    dest=OUT if v==5 else OUT.with_name('resources-'+str(v))
    dest.mkdir(exist_ok=False);results=[]
    for ident,source,provenance,rights,evidence,failures in [
        ('horse-rear-coat','.runtime/assets/demonstrator-01/horse.blend','results/demonstrator-01/stage-a/asset-manifest.json','unresolved',['whole-horse-motion.json','coat.json','finish.json','hoof-ownership.json','coat-reuse.json'],['D316-02','D316-03','D316-04']),
        ('motorcycle-response','.runtime/assets/series01-motorcycle289/royal_enfield.glb','results/sikh289/ATTRIBUTION.md','verified_for_use',['suspension.json'],['D316-01']),
        ('supporting-crowd','.runtime/art-direction/series01-sikh315/finish-11/sequence.blend','results/review316/REVIEW.md','unresolved',['crowd.json']+(['crowd-seams.json'] if v>=6 else []),['D316-06']),
        ('drainage-detail','.runtime/art-direction/series01-sikh315/finish-11/sequence.blend','results/review316/REVIEW.md','verified_for_use',['ditch.json'],['D316-05'])]:
        conditions={'runtime':'Blender5.2.1','sequence':'Sikh317 candidate '+str(v),'scope':'local_internal_review','representation':'inherited315 scene and rig only'}
        record={'schema_version':1,'id':ident,'state':'in_progress','reuse_mode':'adapt',
          'source':[binding(source)],'provenance':[binding(provenance),binding('results/sikh317/STRATEGY.md')],
          'rights':{'status':rights,'scope':'Existing local derivative review only; no new redistribution clearance. Horse upstream CC-BY version and supporting donor reconciliation remain open where stated.','evidence_paths':[provenance]},
          'dependencies':[binding(native+'/sequence.blend'),binding('scripts/sikh317_scene.py'),binding('src/movie_factory/sikh317_motion.py'),binding('scripts/finish317_native.py'),binding('scripts/surface317.py')],
          'tested_conditions':conditions,'evidence':[binding(native+'/'+e) for e in evidence],
          'failures':[{'id':f,'status':'open','reason':'Technical/frame checks and Director AV disposition must be recorded separately; no artistic closure inferred.'} for f in failures],
          'effort':{'active_seconds':None,'evidence_path':None,'note':'Operating ledger tracks jobs; no exact asset-specific net-effort attribution yet.'}}
        if ident=='horse-rear-coat':
            record['dependencies'].append(binding('.runtime/art-direction/series01-entrance-art188/horse-coat-v01.png'))
            record['provenance'].append(binding('.runtime/art-direction/series01-entrance-art188/horse-coat-v01.prompt.txt'))
            record['tested_conditions']['coat_reuse']='authored188 luminance only, UV tiled4; grey pigmentation retained'
        if v>=6:record['dependencies'].append(binding('scripts/crowdfix317.py'))
        if v>=8:
            record['dependencies'].append(binding('scripts/leaderfix317.py'))
            if ident=='horse-rear-coat':record['evidence'].append(binding(native+'/leader-seams.json'))
        (dest/(ident+'.json')).write_text(json.dumps(record,indent=2)+'\n');(dest/(ident+'-use.json')).write_text(json.dumps(conditions,indent=2)+'\n')
        result=validate(ROOT,record,conditions);assert not result['reuse_admissible'];results.append(result)
    (dest/'validation.json').write_text(json.dumps({'records':results,'meaning':'Useful sidecars, explicitly not qualified library entries. Historical manifests unchanged.'},indent=2)+'\n')
if __name__=='__main__':main()
