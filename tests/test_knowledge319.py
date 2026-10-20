import json
from pathlib import Path
import pytest
from movie_factory import production_knowledge as pk
ROOT=Path(__file__).resolve().parents[1]

def packet(entity,operation):
    return pk.task_packet(ROOT,{'id':'319-routing-fixture','operation':operation,
        'entities':[entity],'query':'synthetic applicability check','intent':'fixture',
        'phase':'planning','inputs':{pk.CATALOG:pk.file_hash(ROOT/pk.CATALOG)},'open_decisions':[]})

@pytest.mark.parametrize('entity,op',[
    ('nihang_leader','motion'),('nihang_crowd','motion'),('sikh_beard','modeling'),
    ('sikh_hand','modeling'),('pashtun','modeling')])
def test_construction_lesson_routes(entity,op):
    p=packet(entity,op)
    assert p['dispatch_ready'],p['blockers']
    assert 'construction_interfaces' in {r['id'] for r in p['obligations']}

def test_unrelated_audio_is_not_loaded_with_construction_lesson():
    p=packet('music_reference','audio_analysis')
    assert 'construction_interfaces' not in {r['id'] for r in p['obligations']}

def test_all_thirteen_previous_source_snapshots_are_unchanged():
    old=json.loads((ROOT/'results/sikh319/knowledge/source-pins-before.json').read_text())
    current=json.loads((ROOT/pk.PINS).read_text())
    assert len(old['sources'])==13 and len(current['sources'])==14
    assert all(current['sources'][k]==v for k,v in old['sources'].items())
