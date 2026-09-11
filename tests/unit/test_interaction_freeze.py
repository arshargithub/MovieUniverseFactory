from copy import deepcopy
import pytest
from movie_factory.interaction_controller import _validate_frozen_inputs
from movie_factory.packages import content_id


def test_scored_freeze_rejects_scene_revision_or_profile_substitution():
    scene={'held_position':[0,0,1]};revision={'advance_frames':4};profile={'fps':24,'samples':8}
    campaign={'scored_source_binding':{'scene_sha256':content_id(scene),'revision_sha256':content_id(revision)},'render_profile':profile}
    _validate_frozen_inputs(campaign,scene,revision,profile)
    for index,substitute in enumerate(({'held_position':[0,0,2]},{'advance_frames':8},{'fps':24,'samples':1})):
        inputs=deepcopy([scene,revision,profile]);inputs[index]=substitute
        with pytest.raises(ValueError):_validate_frozen_inputs(campaign,*inputs)
