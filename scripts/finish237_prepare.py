"""Explicit237 source reconciliation and bounded execution packet generation."""
import json
from pathlib import Path
from movie_factory.production_knowledge import source_snapshot,digest,file_hash,task_packet,packet_markdown
ROOT=Path(__file__).resolve().parents[1]
PILOT=ROOT/'docs/knowledge/pilot'
def main():
    if (PILOT/'tasks/finish237-motion.json').exists():raise ValueError('237 reconciliation already recorded; review later changes explicitly, do not re-freeze')
    catalog=json.loads((PILOT/'catalog.json').read_text())
    pins=json.loads((PILOT/'source-pins.json').read_text())
    fresh=source_snapshot(ROOT,catalog)
    # Only the reviewed237 current strategy section was added to this source.
    for key in fresh:
        if key!='unit' and fresh[key]!=pins['sources'][key]:raise ValueError('Unreviewed source change: '+key)
    record=next(r for r in catalog['records'] if r['id']=='narrative')
    record['action'] += '237 authorizes225 timing extension and corrected Kirk-direction narration preview, not final voice acceptance; music is Director-operated Suno and excluded from agent production.'
    record['decision_exceptions'].append(dict(task_id='finish237-audio',operation='audio',authority_source='docs/planning/SERIES_01_PASHTUN_FINISHED_UNIT_PLAN.md'))
    (PILOT/'catalog.json').write_text(json.dumps(catalog,indent=2)+'\n')
    pins['sources']['unit']=fresh['unit'];pins['catalog_sha256']=digest(catalog)
    (PILOT/'source-pins.json').write_text(json.dumps(pins,indent=2)+'\n')
    for kind,operation,entities in [('motion','motion',['pashtun','shot','horse','shawl','sword','renderer']),('audio','audio',['officer'])]:
        paths=['docs/planning/SERIES_01_PASHTUN_FINISHED_UNIT_PLAN.md',
            '.runtime/art-direction/series01-facebuilder-trial-01/entrance218-opening12/scene.blend',
            '.runtime/art-direction/series01-facebuilder-trial-01/entrance218-route13/scene.blend']
        task=dict(id='finish237-'+kind,operation=operation,entities=entities,query='native timing camera recognition full speed motion voice quotation sound learning',
            intent='Execute237 music-independent21-second preview under current strategy; no final acceptance or release.',phase='execution',
            inputs={p:file_hash(ROOT/p) for p in paths},open_decisions=[],execution_authority=dict(source=paths[0],scope='Director237 authorizes native timing extension, voice/book/effects; existing AUDIO-220 cap only.'),
            hypotheses_to_test=['Additional screen time must not slow gait or break motion/contact/camera continuity.','Quote and voice must not obscure action or lose natural timing.'],
            execution_prerequisites=['Read237 strategy and reconcile dependencies manually.','Preserve original sources; full visual/audio review before ready claim.'])
        path=PILOT/'tasks'/('finish237-'+kind+'.json');path.write_text(json.dumps(task,indent=2)+'\n')
        packet=task_packet(ROOT,task);out=ROOT/'.runtime/art-direction/series01-finish237';out.mkdir(parents=True,exist_ok=True)
        (out/(kind+'-packet.json')).write_text(json.dumps(packet,indent=2)+'\n');(out/(kind+'-packet.md')).write_text(packet_markdown(packet))
        print(kind,packet['dispatch_ready'],packet['blockers'])
        if not packet['dispatch_ready']:raise SystemExit(2)
if __name__=='__main__':main()
