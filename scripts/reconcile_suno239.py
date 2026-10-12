"""One reviewed audio-source delta; refuses unrelated or repeated re-freezing."""
import json
from pathlib import Path
from movie_factory import production_knowledge as pk
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'docs/knowledge/pilot';OUT=ROOT/'.runtime/art-direction/series01-finish237'
def main():
    pins=json.loads((P/'source-pins.json').read_text());catalog=json.loads((P/'catalog.json').read_text());fresh=pk.source_snapshot(ROOT,catalog)
    if pins['sources']['audio']['sha256']!='2cd8f6994211f38f9968f14f907d32aa660e98df35db91fcecb8220efbadfca5':raise ValueError('Unexpected prior review')
    if fresh['audio']['sha256']!='253cdf19e65e9712066a0d783072996ee41cdc7fddde93e9df23baf2c8f68339':raise ValueError('Audio source differs from reviewed239 diff')
    for k in fresh:
        if k!='audio' and fresh[k]!=pins['sources'][k]:raise ValueError('Unreviewed source '+k)
    pins['sources']['audio']=fresh['audio'];pins['catalog_sha256']=pk.digest(catalog)
    (P/'source-pins.json').write_text(json.dumps(pins,indent=2)+'\n')
    for kind in ('motion','audio'):
        task=json.loads((P/'tasks'/f'finish237-{kind}.json').read_text());packet=pk.task_packet(ROOT,task)
        for ext,value in [('json',json.dumps(packet,indent=2)+'\n'),('md',pk.packet_markdown(packet))]:
            dest=OUT/f'{kind}-packet239.{ext}'
            if dest.exists():raise ValueError('Preserve packet')
            dest.write_text(value)
        if not packet['dispatch_ready']:raise ValueError(packet['blockers'])
    result=pk.evaluate(ROOT);(OUT/'retrieval239.json').write_text(json.dumps(result,indent=2)+'\n');print('Finite retrieval regression:',result['passed'])
    if not result['passed']:raise SystemExit(2)
if __name__=='__main__':main()
