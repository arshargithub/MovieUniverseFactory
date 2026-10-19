import json
from pathlib import Path
import pytest
from movie_factory import production_knowledge as pk
ROOT=Path(__file__).resolve().parents[1]

def packet(entity,op='motion'):
    return pk.task_packet(ROOT,{'id':'317-routing-fixture','operation':op,
       'entities':[entity],'query':'generic words cannot suppress mandatory rules',
       'intent':'synthetic applicability test','phase':'planning',
       'inputs':{pk.CATALOG:pk.file_hash(ROOT/pk.CATALOG)},'open_decisions':[]})

@pytest.mark.parametrize('entity,expected',[
    ('motorcycle','vehicle_response'),('nihang_horse','animal_coordination'),
    ('nihang_crowd','crowd_support'),('punjab_night','drainage_use')])
def test_component_lessons_route(entity,expected):
    p=packet(entity);assert p['dispatch_ready']
    assert {expected,'reuse_envelope','anticipation'}<={r['id'] for r in p['obligations']}

def test_music_does_not_retrieve_vehicle_mechanics():
    ids={r['id'] for r in packet('music_reference','audio_analysis')['obligations']}
    assert not ids&{'vehicle_response','animal_coordination','crowd_support','drainage_use'}

def test_original_source_pins_preserved():
    old=json.loads((ROOT/'results/sikh317/knowledge/source-pins-before.json').read_text())
    current=json.loads((ROOT/pk.PINS).read_text())
    assert len(old['sources'])==12
    assert all(current['sources'][key]==value for key,value in old['sources'].items())
    assert len(current['sources'])==13
