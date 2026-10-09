"""198 retains a closed material-only operation, no caller paths/code."""
import sys
from pathlib import Path
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import entrance198_terrain as terrain

@pytest.mark.parametrize('job',[{}, {'operation':'anything'}, {'operation':'build02','code':'bad'}, {'operation':'build02','source':'other'}])
def test_closed_build(job):
    with pytest.raises(ValueError):terrain.validate(job)

def test_material_allowlist_excludes_people_and_matte():
    assert len(terrain.MATERIALS)==11
    assert not any(x in ' '.join(terrain.MATERIALS).lower() for x in ('skin','hair','cloth','horse','mountain','shawl'))

def test_render_clock_and_prior_failure_coverage():
    from entrance198_render import OPERATIONS,validate
    assert OPERATIONS['motion04']==tuple(range(217,361))
    assert set((217,223,228,295,325,360)).issubset(OPERATIONS['controls03'])
    with pytest.raises(ValueError):validate({'operation':'controls03','source':'other'})

def test_source_and_generated_input_are_pinned():
    assert len(terrain.SOURCE_HASH)==64
    assert len(terrain.TEXTURE_SHA)==64
    assert terrain.SOURCE_HASH!=terrain.TEXTURE_SHA
