from pathlib import Path

from movie_factory.character_export import _reproducibility_text
from movie_factory.character_motion import _write_review_html


def test_corrected_convenience_player_preserves_reviewed_file(tmp_path):
    reviewed=tmp_path/"review.html"
    reviewed.write_text("original reviewed artifact")
    config={"request":{"clips":{"idle":{"frame_start":1,"frame_end":3}}},
            "playback_fps":24,"playback_fps_by_clip":{}}

    _write_review_html(tmp_path,config,{"decision":"GREEN"},
                       filename="review-corrected-loop.html",notice="Packaging convenience player")

    corrected=(tmp_path/"review-corrected-loop.html").read_text()
    assert reviewed.read_text()=="original reviewed artifact"
    assert "Packaging convenience player" in corrected
    assert 'data-loop="true"' in corrected
    assert 'max="2"' in corrected
    assert "autoCount=loop?frames.length-1:frames.length" in corrected


def test_reproduction_guide_maps_bundled_assets_to_native_test_path():
    player=Path("runs/3d031-motion/frozen/review-corrected-loop.html")
    guide=_reproducibility_text(player)

    assert "assets/admitted-staging/. source/.runtime/assets/3d-03/staged-v1/" in guide
    assert "source/.runtime/assets/3d-03/staged-v1/staged-manifest.json" in guide
    assert player.as_posix() in guide
    assert "original Director-reviewed playback" in guide
