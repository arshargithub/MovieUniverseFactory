"""Reconcile only the explicitly reviewed237 result section, not arbitrary drift."""
import json
from pathlib import Path
from movie_factory import production_knowledge as pk
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'docs/knowledge/pilot'
OUT=ROOT/'.runtime/art-direction/series01-finish237'
OLD='fb5a3211a6367b125ba20b79e48baac8f519135ce20e6f136caeefa0f65ba5f3'
NEW='3f0f9ce2b81c2a7bfa3e91045aaa543474db1be5b3428b0131342b8f393531df'
def main():
    pins=json.loads((P/'source-pins.json').read_text())
    catalog=json.loads((P/'catalog.json').read_text());fresh=pk.source_snapshot(ROOT,catalog)
    if pins['sources']['unit']['sha256']!=OLD or fresh['unit']['sha256']!=NEW:
        raise ValueError('Not the reviewed unit-result delta')
    for key in fresh:
        if key!='unit' and fresh[key]!=pins['sources'][key]:raise ValueError('Unreviewed source '+key)
    pins['sources']['unit']=fresh['unit']
    (P/'source-pins.json').write_text(json.dumps(pins,indent=2)+'\n')
    for kind in ('motion','audio'):
        path=P/'tasks'/f'finish237-{kind}.json';task=json.loads(path.read_text())
        key='docs/planning/SERIES_01_PASHTUN_FINISHED_UNIT_PLAN.md'
        if task['inputs'][key]!=OLD:raise ValueError('Unexpected prior task binding')
        task['inputs'][key]=NEW;path.write_text(json.dumps(task,indent=2)+'\n')
        packet=pk.task_packet(ROOT,task)
        for ext,text in [('json',json.dumps(packet,indent=2)+'\n'),('md',pk.packet_markdown(packet))]:
            dest=OUT/f'{kind}-packet-final.{ext}'
            if dest.exists():raise ValueError('Preserve prior packet')
            dest.write_text(text)
        assert packet['dispatch_ready'],packet['blockers']
    result=pk.evaluate(ROOT);(OUT/'retrieval-final.json').write_text(json.dumps(result,indent=2)+'\n')
    print('Finite retrieval regression:',result['passed'])
    assert result['passed']
if __name__=='__main__':main()
