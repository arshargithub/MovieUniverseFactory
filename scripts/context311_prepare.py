"""Generate exact-preservation route records. Never overwrites existing records."""
import hashlib
import json
from pathlib import Path
from movie_factory import production_knowledge as pk

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'results/context311'
DEST=ROOT/'docs/knowledge/context'

# Manual applicability decisions; cross-topic expectations were recorded first.
TOPICS={
 'workflow': {'rules':[4,6,14,15,16,17,18,19,20,24,31,32], 'requires':[]},
 'knowledge': {'rules':[1,7,8,10], 'requires':[]},
 'context': {'rules':[29], 'requires':['knowledge']},
 'planning': {'rules':[16,29,31,32], 'requires':['knowledge']},
 'architecture': {'rules':[14,30,39], 'requires':['knowledge']},
 'character': {'rules':[5,8,21,24,27], 'requires':['review']},
 'pashtun': {'rules':[13,22,23,25,26,28], 'requires':['character']},
 'wardrobe': {'rules':[27,41], 'requires':['character','motion']},
 'motion': {'rules':[9,21,41], 'requires':['review']},
 'horse': {'rules':[11,27], 'requires':['motion','character']},
 'shot': {'rules':[9], 'requires':['review','motion']},
 'environment': {'rules':[8,9], 'requires':['review']},
 'sound': {'rules':[8,9], 'requires':['review']},
 'review': {'rules':[1,7,8,9,21], 'requires':['knowledge']},
 'model-source': {'rules':[3], 'requires':['knowledge']},
 'trellis': {'rules':[2], 'requires':['model-source','experiment']},
 'engineering': {'rules':[33,34,36,37,38,40], 'requires':['knowledge']},
 'escalation': {'rules':[11,12,40], 'requires':['knowledge']},
 'experiment': {'rules':[35,42], 'requires':['engineering']},
 'operations': {'rules':[7,31,32,34,42], 'requires':['knowledge']},
}
CORE={
 'scope-and-authority':[3,4,6,15,16,17,18,19,20,38],
 'strategy-and-quality':[5,8,9,13,14,21,24,25,27,28,41],
 'knowledge-and-current-state':[1,7,10,29,30],
 'execution-and-records':[11,12,26,31,32,33,34,35,36,37,39,40,42],
}


def sha(data):return hashlib.sha256(data).hexdigest()


def write(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x') as f:json.dump(value,f,indent=2);f.write('\n')


def main():
    source=(BASE/'AGENTS.before.md').read_bytes()
    paragraphs=[x[2:] for x in source.decode().splitlines() if x.startswith('- ')]
    assert len(paragraphs)==42
    records=[]
    for i,text in enumerate(paragraphs,1):
        routes=[k for k,v in TOPICS.items() if i in v['rules']]
        sections=[k for k,v in CORE.items() if i in v]
        assert routes or sections
        note=('Planning reads current state and relevant plan sections, not the entire accumulated history; Director311 explicitly authorizes this retrieval change.'
              if i==29 else 'Original instruction retained verbatim; current Director decisions resolve historical pending states. Core is mandatory; routed specifics remain mandatory when applicable.')
        records.append({'id':f'R{i:02}', 'original_text':text,'sha256':sha(text.encode()),
                        'topics':routes,'core_sections':sections,'reconciliation':note})
    catalog={'schema':1,'original':{'path':'results/context311/AGENTS.before.md','sha256':sha(source)},
        'core':{'path':'AGENTS.md','sha256':sha((BASE/'AGENTS.proposed.md').read_bytes())},
        'topics':{k:{'rules':[f'R{i:02}' for i in v['rules']],'requires':v['requires']} for k,v in TOPICS.items()},
        'rules':records,'limits':'Explicit topic routing, not semantic task classification. Preserve core and reconcile adjacent domains manually.'}
    write(DEST/'rules.json',catalog)
    write(BASE/'coverage.json',{'original_paragraphs':42,'preserved_verbatim':42,'mapping':[
        {k:r[k] for k in ['id','topics','core_sections','reconciliation']} for r in records],
        'limits':'Exact text preservation is mechanically checked; applicability/core paraphrase equivalence is manually reviewed, not proven by hashes.'})
    task={'id':'context311-cleanup','operation':'knowledge','entities':['knowledge'],
          'query':'Context routing current-state recovery instruction preservation bounded tool output',
          'intent':'Local instruction/context cleanup only. Production paused; no providers/cloud/uploads/settings changes.',
          'phase':'execution','open_decisions':[],
          'inputs':{p:pk.file_hash(ROOT/p) for p in ['results/context311/STRATEGY.md','results/context311/AGENTS.before.md','results/context311/routing-expectations.json']},
          'execution_authority':{'source':'results/context311/STRATEGY.md','scope':'Director311 local reversible context cleanup'},
          'max_context_characters':48000}
    packet=pk.task_packet(ROOT,task)
    assert packet['dispatch_ready']
    write(BASE/'task.json',task);write(BASE/'knowledge-packet.json',packet)
    print(json.dumps({'original_rules':42,'routes':len(TOPICS),'knowledge_obligations':len(packet['obligations']),'dispatch_ready':True}))


if __name__=='__main__':main()
