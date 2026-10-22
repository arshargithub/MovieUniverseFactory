from types import SimpleNamespace as NS
import pytest
from movie_factory.adapters.blender.nihang_support import select_production_scene

NAMES = ('horse.rig', 'HORSE hind support pivot', 'mounted leader',
         '320 articulated upper body mounted leader')

@pytest.mark.parametrize('neutral_active', [True, False])
def test_scene_ownership_not_saved_ui(neutral_active):
    prod = NS(objects=dict.fromkeys(NAMES)); neutral = NS(objects={})
    window = NS(scene=neutral if neutral_active else prod)
    calls=[]
    ctx=NS(scene=window.scene, window=window,
           view_layer=NS(update=lambda: calls.append('updated')))
    bpy=NS(context=ctx, data=NS(scenes=[neutral, prod]))
    assert select_production_scene(bpy) is prod
    assert window.scene is prod and calls==['updated']

@pytest.mark.parametrize('count', [0, 2])
def test_ambiguous_or_absent_owner_fails(count):
    bpy=NS(data=NS(scenes=[NS(objects=dict.fromkeys(NAMES)) for _ in range(count)]))
    with pytest.raises(ValueError, match='OWNERSHIP'): select_production_scene(bpy)

def test_no_window_does_not_sample_wrong_scene():
    prod=NS(objects=dict.fromkeys(NAMES))
    bpy=NS(data=NS(scenes=[prod]),context=NS(scene=None,window=None))
    with pytest.raises(ValueError, match='SWITCH_UNAVAILABLE'):select_production_scene(bpy)
